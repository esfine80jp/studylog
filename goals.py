from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import get_subjects_by_user, get_goals_by_user, save_goal

goals_bp = Blueprint("goals", __name__)

@goals_bp.route("/goals")
@login_required
def index():
    subjects = get_subjects_by_user(current_user.id)
    goals    = get_goals_by_user(current_user.id)
    return render_template("goals.html", subjects=subjects, goals=goals)
@goals_bp.route("/goals", methods=["POST"])
@login_required
def save():
    subject_id = request.form.get("subject_id", type=int)
    hours      = request.form.get("hours", type=int)
    if hours is None or hours <= 0:
        flash("目標時間は 1 時間以上を入力してください", "warning")
    else:
        save_goal(current_user.id, subject_id, hours * 60)
        flash("目標を保存しました", "success")
    return redirect(url_for("goals.index"))
