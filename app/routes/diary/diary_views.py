from flask import Blueprint, render_template

diary_views_bp = Blueprint("diary_views", __name__)

@diary_views_bp.route("/")
def index():
    return render_template("diary/index.html")