from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)  # This will enable CORS for all routes

    # Register error handlers blueprint
    from app.errors.handlers import errors_bp

    app.register_blueprint(errors_bp)

    # Register feature blueprints
    from app.posts import posts_bp

    app.register_blueprint(posts_bp)

    return app