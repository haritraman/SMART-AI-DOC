from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask import jsonify
from dotenv import load_dotenv
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    load_dotenv()

    from app.config import Config
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    # Provide clear JSON responses for common JWT errors to aid debugging
    @jwt.unauthorized_loader
    def _unauthorized_callback(msg):
        app.logger.warning("JWT unauthorized: %s", msg)
        return jsonify({"message": "Missing Authorization Header or invalid auth format", "error": msg}), 401

    @jwt.invalid_token_loader
    def _invalid_token_callback(msg):
        app.logger.warning("JWT invalid token: %s", msg)
        return jsonify({"message": "Invalid JWT token", "error": msg}), 422

    @jwt.expired_token_loader
    def _expired_token_callback(jwt_header, jwt_payload):
        app.logger.warning("JWT expired for payload: %s", jwt_payload)
        return jsonify({"message": "Token has expired"}), 401

    from app import models  # noqa: F401
    from app.auth_routes import auth_bp
    from app.project_routes import projects_bp
    from app.ai_routes import ai_bp
    from app.feedback_routes import feedback_bp
    from app.export_routes import export_bp
    from app.ui_routes import ui_bp
    app.register_blueprint(ui_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(projects_bp, url_prefix="/api")
    app.register_blueprint(ai_bp, url_prefix="/api")
    app.register_blueprint(feedback_bp, url_prefix="/api")
    app.register_blueprint(export_bp, url_prefix="/api")
    with app.app_context():
        db.create_all()

    return app
