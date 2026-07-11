import os
import psycopg
from flask import Flask, jsonify, request

app = Flask(__name__)

def get_conn():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "myapp"),
        user=os.getenv("DB_USER", "appuser"),
        password=os.getenv("DB_PASSWORD"),
    )

def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    isi TEXT NOT NULL
                );
            """)

@app.get("/")
def home():
    return "Hello DevOps!"

@app.route("/notes", methods=["GET", "POST"])
def notes():
    if request.method == "POST":
        data = request.get_json() or {}
        isi = data.get("isi", "").strip()
        if not isi:
            return jsonify({"error": "isi wajib diisi"}), 400

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO notes (isi) VALUES (%s) RETURNING id, isi;",
                    (isi,)
                )
                row = cur.fetchone()

        return jsonify({"id": row[0], "isi": row[1]}), 201

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, isi FROM notes ORDER BY id;")
            rows = cur.fetchall()

    return jsonify([{"id": row[0], "isi": row[1]} for row in rows])

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
