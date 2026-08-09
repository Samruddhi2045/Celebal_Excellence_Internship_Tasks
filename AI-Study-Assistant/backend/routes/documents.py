import os
import uuid

from flask import (
    Blueprint,
    request,
    jsonify,
    current_app
)

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from werkzeug.utils import secure_filename

from extensions import db

from models.document import Document

from services.document_processor import extract_text

from services.rag_service import index_document


documents_bp = Blueprint(
    "documents",
    __name__,
    url_prefix="/api/documents"
)


ALLOWED_EXTENSIONS = {
    "pdf",
    "docx",
    "txt"
}


# Maximum file size: 50 MB
MAX_FILE_SIZE = 50 * 1024 * 1024


def allowed_file(filename):

    if "." not in filename:

        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return extension in ALLOWED_EXTENSIONS


@documents_bp.route(
    "/upload",
    methods=["POST"]
)
@jwt_required()
def upload_document():


    user_id = int(
        get_jwt_identity()
    )

    if "file" not in request.files:

        return jsonify({
            "detail": "No file was uploaded."
        }), 400


    file = request.files["file"]


    if not file or not file.filename:

        return jsonify({
            "detail": "Please select a file."
        }), 400


    if not allowed_file(
        file.filename
    ):

        return jsonify({
            "detail":
            "Only PDF, DOCX and TXT files are supported."
        }), 400


    filename = secure_filename(
        file.filename
    )


    extension = filename.rsplit(
        ".",
        1
    )[1].lower()


    unique_name = (
        f"{uuid.uuid4().hex}.{extension}"
    )


    upload_folder = os.path.join(
        current_app.root_path,
        "uploads"
    )


    os.makedirs(
        upload_folder,
        exist_ok=True
    )


    file_path = os.path.join(
        upload_folder,
        unique_name
    )


    try:

        file.save(
            file_path
        )

    except Exception as error:

        return jsonify({
            "detail":
            f"Could not save document: {str(error)}"
        }), 500


    try:

        extracted_text = extract_text(
            file_path,
            extension
        )

    except Exception as error:

        if os.path.exists(file_path):

            os.remove(file_path)


        return jsonify({
            "detail":
            f"Could not process document: {str(error)}"
        }), 400


    if not extracted_text or not extracted_text.strip():

        if os.path.exists(file_path):

            os.remove(file_path)


        return jsonify({
            "detail":
            "No readable text was found in the document."
        }), 400

    document = Document(

        user_id=user_id,

        filename=filename,

        stored_filename=unique_name,

        file_type=extension,

        file_path=file_path,

        extracted_text=extracted_text,

        status="processing"

    )


    db.session.add(
        document
    )

    db.session.commit()


    try:

        rag_result = index_document(

            user_id=user_id,

            document_id=document.id,

            text=extracted_text

        )

        document.status = "ready"

        db.session.commit()


    except Exception as error:


        document.status = "failed"

        db.session.commit()


        print(
            "RAG indexing error:",
            error
        )


        return jsonify({

            "detail":
            "Document uploaded, but AI indexing failed.",

            "error":
            str(error)

        }), 500

    return jsonify({

        "message":
        "Document uploaded and indexed successfully.",

        "document":
        document.to_dict(),

        "rag": {

            "chunks":
            rag_result["chunks"]

        }

    }), 201

@documents_bp.route(
    "",
    methods=["GET"]
)
@jwt_required()
def get_documents():

    user_id = int(
        get_jwt_identity()
    )


    documents = Document.query.filter_by(

        user_id=user_id

    ).order_by(

        Document.uploaded_at.desc()

    ).all()


    return jsonify({

        "documents": [

            document.to_dict()

            for document in documents

        ]

    }), 200


@documents_bp.route(
    "/<int:document_id>",
    methods=["GET"]
)
@jwt_required()
def get_document(
    document_id
):

    user_id = int(
        get_jwt_identity()
    )


    document = Document.query.filter_by(

        id=document_id,

        user_id=user_id

    ).first()


    if not document:

        return jsonify({
            "detail":
            "Document not found."
        }), 404


    return jsonify({

        "document": {

            **document.to_dict(),

            "text_length":
            len(
                document.extracted_text or ""
            )

        }

    }), 200