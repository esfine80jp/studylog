from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import (
    get_logs_by_user, get_subjects_by_user,
    get_log_by_id, create_log, update_log, delete_log,
)

logs_bp = Blueprint("logs", __name__)

import re

def validate_log_form(date: str, minutes: int) -> list[str]:
    errors = []
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        errors.append("日付は YYYY-MM-DD 形式で入力してください")
    if minutes <= 0:
        errors.append("学習時間は 1 分以上を入力してください")
    if minutes > 1440:
        errors.append("学習時間は 1440 分（24 時間）以内で入力してください")
    return errors

@logs_bp.route("/logs")
@login_required
def index():
    subject_id = request.args.get("subject_id", type=int)
    logs       = get_logs_by_user(current_user.id, subject_id=subject_id)
    subjects   = get_subjects_by_user(current_user.id)
    return render_template(
        "logs/index.html",
        logs=logs,
        subjects=subjects,
        subject_id=subject_id,
    )

@logs_bp.route("/logs/new", methods=["GET", "POST"])
@login_required
def new():
    subjects = get_subjects_by_user(current_user.id)
    if request.method == "POST":
        subject_id    = int(request.form.get("subject_id"))
        date          = request.form.get("date", "")
        hours         = int(request.form.get("hours", 0) or 0)
        input_minutes = int(request.form.get("minutes", 0) or 0)
        minutes       = hours * 60 + input_minutes
        memo          = request.form.get("memo", "").strip()

        errors = validate_log_form(date, minutes)
        if errors:
            for err in errors:
                flash(err, "warning")
        else:
            create_log(current_user.id, subject_id, date, minutes, memo)
            flash("記録しました", "success")
            return redirect(url_for("logs.index"))
    return render_template("logs/new.html", subjects=subjects)

@logs_bp.route("/logs/<int:log_id>/edit", methods=["GET", "POST"])
@login_required
def edit(log_id: int):
    log = get_log_by_id(log_id, current_user.id)
    if log is None:
        flash("記録が見つかりません", "danger")
        return redirect(url_for("logs.index"))

    subjects = get_subjects_by_user(current_user.id)
    if request.method == "POST":
        subject_id = int(request.form.get("subject_id"))
        date       = request.form.get("date", "")
        hours         = int(request.form.get("hours", 0) or 0)
        input_minutes = int(request.form.get("minutes", 0) or 0)
        minutes       = hours * 60 + input_minutes
        memo       = request.form.get("memo", "").strip()
        errors = validate_log_form(date, minutes)
        if errors:
            for err in errors:
                flash(err, "warning")
        else:
            update_log(log_id, current_user.id, subject_id, date, minutes, memo)
            flash("更新しました", "success")
            return redirect(url_for("logs.index"))
    return render_template("logs/edit.html", log=log, subjects=subjects)
@logs_bp.route("/logs/<int:log_id>/delete", methods=["POST"])
@login_required
def delete(log_id: int):
    if delete_log(log_id, current_user.id):
        flash("削除しました", "success")
    else:
        flash("記録が見つかりません", "danger")
    return redirect(url_for("logs.index"))

