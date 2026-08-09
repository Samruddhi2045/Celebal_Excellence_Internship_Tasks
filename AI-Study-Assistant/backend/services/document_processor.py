import os

import pymupdf

from docx import Document as DocxDocument


def extract_pdf_text(file_path):

    text = []

    pdf = pymupdf.open(file_path)

    try:

        for page in pdf:

            page_text = page.get_text()

            if page_text:
                text.append(page_text)

    finally:

        pdf.close()

    return "\n".join(text)


def extract_docx_text(file_path):

    document = DocxDocument(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:

        if paragraph.text.strip():

            paragraphs.append(
                paragraph.text
            )

    return "\n".join(paragraphs)


def extract_txt_text(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:

        return file.read()


def extract_text(file_path, file_type):

    file_type = file_type.lower()

    if file_type == "pdf":

        return extract_pdf_text(file_path)

    if file_type == "docx":

        return extract_docx_text(file_path)

    if file_type == "txt":

        return extract_txt_text(file_path)

    raise ValueError(
        "Unsupported document type."
    )