import os
import tempfile
from flask import Blueprint, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import Project, ProjectSection

export_bp = Blueprint("export", __name__)


def _get_project_and_sections(project_id, user_id):
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return None, None, ("Project not found", 404)

    sections = (
        ProjectSection.query
        .filter_by(project_id=project.id)
        .order_by(ProjectSection.index)
        .all()
    )
    if not sections:
        return project, None, ("No sections to export", 400)

    return project, sections, None


@export_bp.route("/projects/<int:project_id>/export/docx", methods=["GET"])
@jwt_required()
def export_docx(project_id):
    user_id = int(get_jwt_identity())

    project, sections, error = _get_project_and_sections(project_id, user_id)
    if error:
        msg, code = error
        return jsonify({"message": msg}), code

    tmp_dir = tempfile.gettempdir()
    safe_title = "".join(
        c if c.isalnum() or c in (" ", "-", "_") else "_" for c in project.title
    )
    filename = f"{safe_title or 'document'}.docx"
    path = os.path.join(tmp_dir, filename)

    try:
        from app.docx_service import build_docx
    except Exception as e:
        return jsonify({
            "message": "DOCX export unavailable; optional dependency missing or failed to import.",
            "error": str(e),
        }), 500

    build_docx(project, sections, path)

    return send_file(
        path,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@export_bp.route("/projects/<int:project_id>/export/pptx", methods=["GET"])
@jwt_required()
def export_pptx(project_id):
    user_id = int(get_jwt_identity())

    project, sections, error = _get_project_and_sections(project_id, user_id)
    if error:
        msg, code = error
        return jsonify({"message": msg}), code

    tmp_dir = tempfile.gettempdir()
    safe_title = "".join(
        c if c.isalnum() or c in (" ", "-", "_") else "_" for c in project.title
    )
    filename = f"{safe_title or 'slides'}.pptx"
    path = os.path.join(tmp_dir, filename)

    try:
        from app.pptx_service import build_pptx
    except Exception as e:
        return jsonify({
            "message": "PPTX export unavailable; optional dependency missing or failed to import.",
            "error": str(e),
        }), 500

    build_pptx(project, sections, path)

    return send_file(
        path,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )
