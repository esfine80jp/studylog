import sqlite3

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import get_subjects_by_user, create_subject, delete_subject

subjects_bp = Blueprint("subjects", __name__)

@subjects_bp.route("/subjects")
@login_required
def index():
    subjects = get_subjects_by_user(current_user.id)
    return render_template("subjects.html", subjects=subjects)

@subjects_bp.route("/subjects", methods=["POST"])
@login_required
def create():
    name  = request.form.get("name", "").strip()
    color = request.form.get("color", "#4A90E2")
    if not name:
        flash("科目名を入力してください", "warning")
    else:
        try:
            create_subject(current_user.id, name, color)
            flash("科目を追加しました", "success")
        except sqlite3.IntegrityError:
            flash("同じ名前の科目がすでに登録されています", "warning")
    return redirect(url_for("subjects.index"))

@subjects_bp.route("/subjects/<int:subject_id>/delete", methods=["POST"])
@login_required
def delete(subject_id: int):
    try:
        if delete_subject(subject_id, current_user.id):
            flash("科目を削除しました", "success")
        else:
            flash("科目が見つかりません", "danger")
    except sqlite3.IntegrityError:
        flash("この科目には学習記録または目標が残っているため削除できません", "danger")
    return redirect(url_for("subjects.index"))
