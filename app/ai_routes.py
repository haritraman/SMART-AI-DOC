from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models import Project, ProjectSection, SectionRevision
# Import AI service functions at runtime inside handlers to avoid import-time
# failures when optional AI libs are missing or misconfigured.

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/projects/<int:project_id>/generate", methods=["POST"])
@jwt_required()
def generate_project_content(project_id):
    """Generate content for all sections of a project."""
    user_id = int(get_jwt_identity())

    # Ensure this project belongs to the logged-in user
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({"message": "Project not found"}), 404

    sections = (
        ProjectSection.query
        .filter_by(project_id=project.id)
        .order_by(ProjectSection.index)
        .all()
    )
    if not sections:
        return jsonify({"message": "No sections configured"}), 400

    for sec in sections:
        old_text = sec.current_content

        try:
            try:
                from app.ai_service import generate_section_content
            except Exception as e:
                print("AI service import failed:", e)
                new_text = old_text or "(AI generation unavailable)"
            else:
                new_text = generate_section_content(project, sec)
        except Exception as e:
            # Do NOT crash the whole request – log and fallback
            print("AI generation error for section", sec.id, ":", e)
            new_text = old_text or "(AI generation failed; please try again.)"

        sec.current_content = new_text

        # Determine next version number
        last_rev = (
            SectionRevision.query
            .filter_by(section_id=sec.id)
            .order_by(SectionRevision.version.desc())
            .first()
        )
        next_version = (last_rev.version + 1) if last_rev else 1

        rev = SectionRevision(
            section_id=sec.id,
            version=next_version,
            prompt="initial generation" if not last_rev else "regenerate",
            old_content=old_text,
            new_content=new_text,
        )
        db.session.add(rev)

    project.status = "generated"
    db.session.commit()

    return jsonify({"message": "Content generated successfully"}), 200


@ai_bp.route("/sections/<int:section_id>/refine", methods=["POST"])
@jwt_required()
def refine_section(section_id):
    """Refine a single section based on a user prompt."""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    user_prompt = data.get("prompt")

    if not user_prompt:
        return jsonify({"message": "prompt is required"}), 400

    section = ProjectSection.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found"}), 404

    project = Project.query.filter_by(id=section.project_id, user_id=user_id).first()
    if not project:
        return jsonify({"message": "Not authorized for this section"}), 403

    # Latest version for this section
    last_rev = (
        SectionRevision.query
        .filter_by(section_id=section.id)
        .order_by(SectionRevision.version.desc())
        .first()
    )
    next_version = (last_rev.version + 1) if last_rev else 1

    old_text = section.current_content or ""

    try:
        try:
            from app.ai_service import refine_section_content
        except Exception as e:
            print("AI service import failed:", e)
            return jsonify({"message": "AI refine unavailable; optional dependency missing or misconfigured."}), 500
        new_text = refine_section_content(project, section, user_prompt)
    except Exception as e:
        print("AI refine error for section", section.id, ":", e)
        return jsonify({"message": "AI refine failed; please try again."}), 500

    section.current_content = new_text

    rev = SectionRevision(
        section_id=section.id,
        version=next_version,
        prompt=user_prompt,
        old_content=old_text,
        new_content=new_text,
    )
    db.session.add(rev)
    db.session.commit()

    return jsonify({
        "section_id": section.id,
        "version": next_version,
        "content": new_text,
    }), 200
