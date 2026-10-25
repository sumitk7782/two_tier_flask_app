
import os
import socket
import psycopg2

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# PostgreSQL configuration
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "postgres"),
    "port": int(os.environ.get("DB_PORT", "5432")),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "dbname": os.environ.get("DB_NAME", "devops"),
}


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


_db_ready = False


def init_db():
    global _db_ready

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    message TEXT
                );
            """)
        conn.commit()
    finally:
        conn.close()

    _db_ready = True


def ensure_db():
    global _db_ready

    if not _db_ready:
        init_db()


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/")
def hello():
    ensure_db()

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT message FROM messages ORDER BY id")
            messages = cur.fetchall()
    finally:
        conn.close()

    return render_template(
        "index.html",
        messages=messages,
        hostname=socket.gethostname()
    )


@app.route("/submit", methods=["POST"])
def submit():
    new_message = request.form.get("new_message")

    if not new_message:
        return jsonify({"error": "Message is required"}), 400

    ensure_db()

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO messages (message) VALUES (%s)",
                (new_message,)
            )
        conn.commit()
    finally:
        conn.close()

    return jsonify({"message": new_message})


if __name__ == "__main__":
    init_db()
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=os.environ.get("FLASK_DEBUG") == "1"
    )
