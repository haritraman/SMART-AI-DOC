from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models import Project, ProjectSection, SectionFeedback, SectionComment

feedback_bp = Blueprint("feedback", __name__)


@feedback_bp.route("/sections/<int:section_id>/feedback", methods=["POST"])
@jwt_required()
def add_feedback(section_id):
    user_id = int(get_jwt_identity())

    section = ProjectSection.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found"}), 404

    project = Project.query.filter_by(id=section.project_id, user_id=user_id).first()
    if not project:
        return jsonify({"message": "Not authorized for this section"}), 403

    data = request.get_json() or {}
    is_like = data.get("is_like")

    if is_like is None:
        return jsonify({"message": "is_like (true/false) is required"}), 400

    fb = SectionFeedback(
        section_id=section.id,
        is_like=bool(is_like),
    )
    db.session.add(fb)
    db.session.commit()

    return jsonify({"message": "Feedback recorded"}), 201


@feedback_bp.route("/sections/<int:section_id>/comments", methods=["POST"])
@jwt_required()
def add_comment(section_id):
    user_id = int(get_jwt_identity())

    section = ProjectSection.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found"}), 404

    project = Project.query.filter_by(id=section.project_id, user_id=user_id).first()
    if not project:
        return jsonify({"message": "Not authorized for this section"}), 403

    data = request.get_json() or {}
    comment_text = data.get("comment")

    if not comment_text:
        return jsonify({"message": "comment is required"}), 400

    c = SectionComment(
        section_id=section.id,
        comment=comment_text,
    )
    db.session.add(c)
    db.session.commit()

    return jsonify({"message": "Comment added"}), 201

@feedback_bp.route("/projects/<int:project_id>/comments", methods=["GET"])
@jwt_required()
def get_project_comments(project_id):
    """
    Return all comments for a project, grouped by section.
    """
    user_id = int(get_jwt_identity())

    # Make sure the project belongs to this user
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({"message": "Project not found"}), 404

    sections = (
        ProjectSection.query
        .filter_by(project_id=project.id)
        .order_by(ProjectSection.index)
        .all()
    )

    result = []
    for sec in sections:
        comments = (
            SectionComment.query
            .filter_by(section_id=sec.id)
            .order_by(SectionComment.created_at)
            .all()
        )
        # count likes/dislikes for this section
        likes = (
            SectionFeedback.query.filter_by(section_id=sec.id, is_like=True).count()
        )
        dislikes = (
            SectionFeedback.query.filter_by(section_id=sec.id, is_like=False).count()
        )
        result.append({
            "section_id": sec.id,
            "section_index": sec.index,
            "section_title": sec.title,
            "comments": [
                {
                    "id": c.id,
                    "comment": c.comment,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in comments
            ],
            "likes": likes,
            "dislikes": dislikes,
        })

    return jsonify({
        "project_id": project.id,
        "project_title": project.title,
        "items": result,
    })
