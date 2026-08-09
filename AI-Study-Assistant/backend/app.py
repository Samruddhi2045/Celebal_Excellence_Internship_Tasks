from flask import Flask, jsonify

from config import Config

from extensions import (
    db,
    jwt,
    cors
)


from models.user import User
from models.document import Document
from models.conversation import Conversation
from models.chat_message import ChatMessage

from routes.auth import auth_bp
from routes.documents import documents_bp
from routes.chat import chat_bp
from routes.history import history_bp

def create_app():

    app = Flask(__name__)

    app.config.from_object(
        Config
    )

    db.init_app(
        app
    )

    jwt.init_app(
        app
    )

    cors.init_app(

        app,

        resources={

            r"/api/*": {

                "origins": "*"

            }

        }

    )


    # Authentication
    app.register_blueprint(
        auth_bp
    )


    # Documents
    app.register_blueprint(
        documents_bp
    )

    # Document Chat
    app.register_blueprint(
        chat_bp
    )

    # Conversation History
    app.register_blueprint(
        history_bp
    )

    @app.route(
        "/",
        methods=["GET"]
    )
    def home():

        return jsonify({

            "message":
            "AI Study Assistant API is running.",

            "status":
            "success"

        })

    with app.app_context():

        print(
            "Creating database tables..."
        )


        db.create_all()


        print(
            "Database tables created successfully."
        )


    return app

app = create_app()

if __name__ == "__main__":

    app.run(

        debug=True,

        host="127.0.0.1",

        port=5000

    )