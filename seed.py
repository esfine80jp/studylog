import datetime
import random

from werkzeug.security import generate_password_hash

from database import get_db

SUBJECTS = [
    ("Python", "#4A90E2"),
    ("英語",   "#E2884A"),
    ("簿記",   "#4AE29B"),
]
def seed_demo(email: str = "demo@example.com", password: str = "demo1234"):
    db = get_db()
    if db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone():
        return

    db.execute(
        "INSERT INTO users (email, password_hash) VALUES (?, ?)",
        (email, generate_password_hash(password)),
    )
    user_id = db.execute(
        "SELECT id FROM users WHERE email = ?",
        (email,),
    ).fetchone()["id"]

    for name, color in SUBJECTS:
        db.execute(
            "INSERT INTO subjects (user_id, name, color) VALUES (?, ?, ?)",
            (user_id, name, color),
        )
    
    subject_ids = [
        r["id"]
        for r in db.execute(
            "SELECT id FROM subjects WHERE user_id = ?",
            (user_id,),
        ).fetchall()
    ]

    for sid in subject_ids:
        db.execute(
            "INSERT INTO goals (user_id, subject_id, weekly_minutes) VALUES (?, ?, ?)",
            (user_id, sid, 300),
        )
    today = datetime.date.today()
    for i in range(14):
        day = today - datetime.timedelta(days=i)
        db.execute(
            "INSERT INTO study_logs (user_id, subject_id, date, minutes, memo) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                user_id,
                random.choice(subject_ids),
                day.isoformat(),
                random.choice([30, 45, 60, 90]),
                "デモ用の記録",
            ),
        )
    db.commit()        
