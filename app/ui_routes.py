from flask import Blueprint, render_template

ui_bp = Blueprint("ui", __name__)

@ui_bp.route("/")
def index():
    return render_template("login.html", title="Login")

@ui_bp.route("/login")
def login_page():
    return render_template("login.html", title="Login")

@ui_bp.route("/register")
def register_page():
    return render_template("register.html", title="Register")

@ui_bp.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html", title="Dashboard")

@ui_bp.route("/projects/<int:project_id>/configure")
def configure_project_page(project_id):
    return render_template("project_config.html", title="Configure Project", project_id=project_id)


@ui_bp.route("/projects/<int:project_id>/edit")
def edit_project_page(project_id):
    return render_template("project_editor.html", title="Editor", project_id=project_id)

@ui_bp.route("/projects/<int:project_id>/comments")
def project_comments_page(project_id):
    return render_template("project_comments.html", project_id=project_id)