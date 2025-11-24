from datetime import datetime
from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    projects = db.relationship("Project", backref="user", lazy=True)


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    doc_type = db.Column(db.String(10), nullable=False)  # "docx" or "pptx"
    main_topic = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="configured")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    sections = db.relationship("ProjectSection", backref="project", lazy=True)


class ProjectSection(db.Model):
    __tablename__ = "project_sections"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    index = db.Column(db.Integer, nullable=False)  # order of section/slide
    title = db.Column(db.String(255), nullable=False)
    current_content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    revisions = db.relationship("SectionRevision", backref="section", lazy=True)
    feedback = db.relationship("SectionFeedback", backref="section", lazy=True)
    comments = db.relationship("SectionComment", backref="section", lazy=True)


class SectionRevision(db.Model):
    __tablename__ = "section_revisions"

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(
        db.Integer, db.ForeignKey("project_sections.id"), nullable=False
    )
    version = db.Column(db.Integer, nullable=False)
    prompt = db.Column(db.Text, nullable=True)
    old_content = db.Column(db.Text, nullable=True)
    new_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SectionFeedback(db.Model):
    __tablename__ = "section_feedback"

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(
        db.Integer, db.ForeignKey("project_sections.id"), nullable=False
    )
    is_like = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SectionComment(db.Model):
    __tablename__ = "section_comments"

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(
        db.Integer, db.ForeignKey("project_sections.id"), nullable=False
    )
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
