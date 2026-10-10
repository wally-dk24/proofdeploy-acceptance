"""Item catalog API."""
import os
import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)
DB = os.environ.get("DB_PATH", "./app.db")


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)"
    )
    conn.commit()
    conn.close()


@app.route("/health")
def health():
    return jsonify({"status": "ok", "version": 2})


@app.route("/items", methods=["GET"])
def list_items():
    conn = get_db()
    rows = conn.execute("SELECT id, name FROM items ORDER BY name").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/items", methods=["POST"])
def create_item():
    data = request.get_json(force=True)
    name = data.get("name", "")
    conn = get_db()
    cur = conn.execute("INSERT INTO items (name) VALUES (?)", (name,))
    conn.commit()
    item_id = cur.lastrowid
    conn.close()
    return jsonify({"id": item_id, "name": name}), 201


@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    conn = get_db()
    row = conn.execute(
        "SELECT id, name FROM items WHERE id = ?", (item_id,)
    ).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(dict(row))


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
