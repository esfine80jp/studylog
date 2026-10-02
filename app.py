import io, base64, os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import japanize_matplotlib
from flask import Flask, render_template
from flask_login import LoginManager, login_required, current_user

from database import init_db, close_db, get_db
from database import get_weekly_summary, get_weekly_progress
from user     import User
from auth     import auth_bp
from logs     import logs_bp
from subjects import subjects_bp
from goals    import goals_bp
from seed import seed_demo

login_manager = LoginManager()
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id: str):
    db  = get_db()
    row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        return None
    return User(row["id"], row["email"])
def make_weekly_graph(summary: list) -> str:
    labels  = [r["name"]          for r in summary]
    minutes = [r["total_minutes"] for r in summary]
    colors  = [r["color"]         for r in summary]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(minutes, labels=labels, colors=colors, autopct="%1.0f%%", startangle=90)
    ax.set_title("今週の科目別学習比率")
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()
def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-fallback-key")

    app.teardown_appcontext(close_db)
    login_manager.init_app(app)

    with app.app_context():
        init_db()
        if os.environ.get("SEED_DEMO") == "1":
            seed_demo()

    app.register_blueprint(auth_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(goals_bp)
    @app.route("/")
    @login_required
    def dashboard():
        summary  = get_weekly_summary(current_user.id)
        progress = get_weekly_progress(current_user.id)
        graph    = make_weekly_graph(summary) if summary else None
        return render_template("dashboard.html", progress=progress, graph=graph)

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    return app

app = create_app()
if __name__ == "__main__":
    app.run(port=5000)
