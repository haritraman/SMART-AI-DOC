from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models import (
    Project,
    ProjectSection,
    SectionRevision,
    SectionFeedback,
    SectionComment,
)

projects_bp = Blueprint("projects", __name__)


def project_to_dict(project):
    return {
        "id": project.id,
        "title": project.title,
        "doc_type": project.doc_type,
        "main_topic": project.main_topic,
        "status": project.status,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat() if project.updated_at else None,
    }


@projects_bp.route("/projects", methods=["GET"])
@jwt_required()
def list_projects():
    user_id = int(get_jwt_identity())
    projects = (
        Project.query.filter_by(user_id=user_id)
        .order_by(Project.created_at.desc())
        .all()
    )
    return jsonify([project_to_dict(p) for p in projects])


@projects_bp.route("/projects", methods=["POST"])
@jwt_required()
def create_project():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    title = data.get("title")
    doc_type = data.get("doc_type")  # "docx" or "pptx"
    main_topic = data.get("main_topic")

    if not title or not doc_type or not main_topic:
        return (
            jsonify({"message": "title, doc_type, and main_topic are required"}),
            400,
        )

    if doc_type not in ("docx", "pptx"):
        return jsonify({"message": "doc_type must be 'docx' or 'pptx'"}), 400

    project = Project(
        user_id=user_id,
        title=title,
        doc_type=doc_type,
        main_topic=main_topic,
        status="configured",
    )
    try:
        db.session.add(project)
        db.session.commit()
    except Exception as e:
        from flask import current_app

        current_app.logger.exception("Failed to create project")
        db.session.rollback()
        return jsonify({"message": "Failed to create project", "error": str(e)}), 500

    return jsonify(project_to_dict(project)), 201


@projects_bp.route("/projects/<int:project_id>", methods=["GET"])
@jwt_required()
def get_project(project_id):
    user_id = int(get_jwt_identity())
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({"message": "Project not found"}), 404

    sections = (
        ProjectSection.query.filter_by(project_id=project.id)
        .order_by(ProjectSection.index)
        .all()
    )
    return jsonify(
        {
            "project": project_to_dict(project),
            "sections": [
                {
                    "id": s.id,
                    "index": s.index,
                    "title": s.title,
                    "current_content": s.current_content,
                }
                for s in sections
            ],
        }
    )

@projects_bp.route("/projects/<int:project_id>/sections", methods=["POST"])
@jwt_required()
def configure_sections(project_id):
    """
    Save the outline/sections for a project.

    ✅ If the incoming structure is IDENTICAL to the existing one
       (same indexes & titles), we DO NOT touch existing sections,
       AI content, comments, or feedback.

    ✅ If the structure changed, we:
       - delete revisions / feedback / comments for old sections
       - delete the old sections
       - insert the new sections (fresh, no content, no comments/feedback)
    """
    user_id = int(get_jwt_identity())
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({"message": "Project not found"}), 404

    data = request.get_json() or {}
    sections = data.get("sections") or []

    if not sections:
        return jsonify({"message": "sections array is required"}), 400

    # Validate + normalize incoming sections
    cleaned = []
    for s in sections:
        idx = s.get("index")
        title = (s.get("title") or "").strip()
        if idx is None or not title:
            continue
        try:
            idx_int = int(idx)
        except (TypeError, ValueError):
            return jsonify({"message": "Each section index must be an integer"}), 400
        cleaned.append({"index": idx_int, "title": title})

    if not cleaned:
        return (
            jsonify(
                {
                    "message": "At least one section with a valid index and title is required"
                }
            ),
            400,
        )

    try:
        # Existing sections ordered by index
        existing_sections = (
            ProjectSection.query.filter_by(project_id=project.id)
            .order_by(ProjectSection.index)
            .all()
        )
        existing_normalized = [
            {"index": s.index, "title": (s.title or "").strip()}
            for s in existing_sections
        ]
        new_normalized = sorted(cleaned, key=lambda x: x["index"])

        # Check if structure actually changed
        structure_changed = True
        if len(existing_normalized) == len(new_normalized):
            if all(
                e["index"] == n["index"] and e["title"] == n["title"]
                for e, n in zip(existing_normalized, new_normalized)
            ):
                structure_changed = False

        if not structure_changed:
            # Nothing changed → keep everything (content, comments, feedback, revisions)
            project.status = "configured"
            db.session.commit()
            return jsonify(
                {
                    "message": "Sections unchanged; existing AI content, comments, and feedback are preserved."
                }
            ), 200

        # 🚨 Structure changed → reset sections + ALL associated data
        existing_ids = [s.id for s in existing_sections]

        if existing_ids:
            # 1) Delete child rows for these sections
            SectionRevision.query.filter(
                SectionRevision.section_id.in_(existing_ids)
            ).delete(synchronize_session=False)

            SectionFeedback.query.filter(
                SectionFeedback.section_id.in_(existing_ids)
            ).delete(synchronize_session=False)

            SectionComment.query.filter(
                SectionComment.section_id.in_(existing_ids)
            ).delete(synchronize_session=False)

            # 2) Delete the sections themselves
            ProjectSection.query.filter_by(project_id=project.id).delete(
                synchronize_session=False
            )
            db.session.flush()

        # 3) Insert new sections (fresh, without content/comments/feedback)
        for item in new_normalized:
            sec = ProjectSection(
                project_id=project.id,
                index=item["index"],
                title=item["title"],
                current_content=None,
            )
            db.session.add(sec)

        project.status = "configured"
        db.session.commit()
    except Exception as e:
        import traceback
        from flask import current_app

        tb = traceback.format_exc()
        current_app.logger.error(
            "Failed to configure sections for project %s:\n%s", project.id, tb
        )
        db.session.rollback()
        max_len = 4000
        tb_snip = tb if len(tb) <= max_len else tb[-max_len:]
        return (
            jsonify(
                {
                    "message": "Failed to configure sections",
                    "error": str(e),
                    "traceback": tb_snip,
                }
            ),
            500,
        )

    return jsonify({"message": "Sections configured successfully"}), 200
