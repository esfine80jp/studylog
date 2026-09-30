import sqlite3
from flask import g
import datetime
import os

DB_PATH = "studylog.db"

def get_db_path() -> str:
    return os.environ.get("STUDYLOG_DB", DB_PATH)

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(get_db_path())
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            email         TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at    TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS subjects (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name       TEXT NOT NULL,
            color      TEXT NOT NULL DEFAULT '#4A90E2',
            UNIQUE (user_id, name)
        );
        CREATE TABLE IF NOT EXISTS study_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            subject_id  INTEGER NOT NULL REFERENCES subjects(id),
            date        TEXT NOT NULL,
            minutes     INTEGER NOT NULL,
            memo        TEXT DEFAULT '',
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS goals (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            subject_id     INTEGER NOT NULL REFERENCES subjects(id),
            weekly_minutes INTEGER NOT NULL,
            UNIQUE (user_id, subject_id)
        );
        CREATE INDEX IF NOT EXISTS idx_study_logs_user_date
            ON study_logs (user_id, date);
        CREATE INDEX IF NOT EXISTS idx_study_logs_subject
            ON study_logs (subject_id);
    """)
    db.commit()

def get_logs_by_user(user_id: int) -> list:
    db = get_db()
    return db.execute(
        "SELECT l.*, s.name AS subject_name FROM study_logs l "
        "JOIN subjects s ON l.subject_id = s.id "
        "WHERE l.user_id = ? ORDER BY l.date DESC",
        (user_id,)
    ).fetchall()

def create_log(user_id: int, subject_id: int, date: str, minutes: int, memo: str):
    db = get_db()
    db.execute(
        "INSERT INTO study_logs (user_id, subject_id, date, minutes, memo) VALUES (?,?,?,?,?)",
        (user_id, subject_id, date, minutes, memo)
    )
    db.commit()

# 029 追加
def get_logs_by_user(user_id: int, subject_id: int | None = None) -> list:
    db     = get_db()
    sql    = (
        "SELECT l.*, s.name AS subject_name, s.color FROM study_logs l "
        "JOIN subjects s ON l.subject_id = s.id "
        "WHERE l.user_id = ?"
    )
    params = [user_id]

    if subject_id:
        sql += " AND l.subject_id = ?"
        params.append(subject_id)

    sql += " ORDER BY l.date DESC"
    return db.execute(sql, params).fetchall()

def get_subjects_by_user(user_id: int) -> list:
    db = get_db()
    return db.execute(
        "SELECT * FROM subjects WHERE user_id = ? ORDER BY name",
        (user_id,)
    ).fetchall()

def get_log_by_id(log_id: int, user_id: int):
    db = get_db()
    return db.execute(
        "SELECT * FROM study_logs WHERE id = ? AND user_id = ?",
        (log_id, user_id)
    ).fetchone()

def update_log(log_id: int, user_id: int, subject_id: int, date: str, minutes: int, memo: str):
    db = get_db()
    db.execute(
        "UPDATE study_logs SET subject_id = ?, date = ?, minutes = ?, memo = ? "
        "WHERE id = ? AND user_id = ?",
        (subject_id, date, minutes, memo, log_id, user_id)
    )
    db.commit()
def delete_log(log_id: int, user_id: int) -> int:
    db  = get_db()
    cur = db.execute(
        "DELETE FROM study_logs WHERE id = ? AND user_id = ?",
        (log_id, user_id)
    )
    db.commit()
    return cur.rowcount

def create_subject(user_id: int, name: str, color: str):
    db = get_db()
    db.execute(
        "INSERT INTO subjects (user_id, name, color) VALUES (?, ?, ?)",
        (user_id, name, color),
    )
    db.commit()

def delete_subject(subject_id: int, user_id: int) -> int:
    db  = get_db()
    cur = db.execute(
        "DELETE FROM subjects WHERE id = ? AND user_id = ?",
        (subject_id, user_id),
    )
    db.commit()
    return cur.rowcount

def get_goals_by_user(user_id: int) -> dict:
    db   = get_db()
    rows = db.execute(
        "SELECT subject_id, weekly_minutes FROM goals WHERE user_id = ?",
        (user_id,),
    ).fetchall()
    return {r["subject_id"]: r["weekly_minutes"] for r in rows}
def save_goal(user_id: int, subject_id: int, weekly_minutes: int):
    db  = get_db()
    row = db.execute(
        "SELECT id FROM goals WHERE user_id = ? AND subject_id = ?",
        (user_id, subject_id),
    ).fetchone()
    if row is None:
        db.execute(
            "INSERT INTO goals (user_id, subject_id, weekly_minutes) VALUES (?, ?, ?)",
            (user_id, subject_id, weekly_minutes),
        )
    else:
        db.execute(
            "UPDATE goals SET weekly_minutes = ? WHERE id = ?",
            (weekly_minutes, row["id"]),
        )
    db.commit()

def get_weekly_summary(user_id: int) -> list:
    today      = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())
    week_end   = week_start + datetime.timedelta(days=6)

    db = get_db()
    rows = db.execute("""
        SELECT s.name, s.color, SUM(l.minutes) AS total_minutes
        FROM study_logs l
        JOIN subjects s ON l.subject_id = s.id
        WHERE l.user_id = ?
          AND l.date BETWEEN ? AND ?
        GROUP BY s.id
    """, (user_id, week_start.isoformat(), week_end.isoformat())).fetchall()
    return [dict(r) for r in rows]

def get_weekly_progress(user_id: int) -> dict:
    summary      = get_weekly_summary(user_id)
    actual_total = sum(r["total_minutes"] for r in summary)

    db = get_db()
    row        = db.execute(
        "SELECT SUM(weekly_minutes) AS total FROM goals WHERE user_id = ?",
        (user_id,)
    ).fetchone()
    goal_total = row["total"] or 0
    rate       = round(actual_total / goal_total * 100) if goal_total else 0

    return {"actual": actual_total, "goal": goal_total, "rate": rate}
