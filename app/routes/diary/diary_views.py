from flask import Blueprint, render_template

diary_bp = Blueprint("diary_views", __name__)

@diary_bp.route("/")
def index():
    return render_template("diary/index.html")

@diary_bp.route("/write")
def write():
    return render_template("diary/write.html")

@diary_bp.route("/detail/<int:diary_id>")
def detail(diary_id):
    return render_template("diary/detail.html", diary_id=diary_id)

