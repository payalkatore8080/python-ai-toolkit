from flask import Flask, render_template, request, jsonify, Response, stream_with_context, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from pathlib import Path
import sys
import json
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai_client import stream_response
from history_store import (
    create_chat,
    load_history,
    add_message,
    delete_chat,
    clear_chat,
    claim_unowned_chats
)
from models import db, User

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "development-secret-key-change-before-deployment"
)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + str(PROJECT_ROOT / "users.db")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith("/api/"):
        return jsonify({"error": "Please login first."}), 401
    return redirect(url_for("login"))


with app.app_context():
    db.create_all()


@app.route("/")
@login_required
def home():
    return render_template("index.html", username=current_user.username)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("Please fill in all fields.")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must contain at least 8 characters.")
            return render_template("register.html")

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash("Username or email already exists.")
            return render_template("register.html")

        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        claim_unowned_chats(user.id)

        login_user(user)
        flash("Registration successful!")
        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("home"))

        flash("Invalid email or password.")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/api/chats", methods=["POST"])
@login_required
def new_chat():
    chat = create_chat(current_user.id)

    return jsonify({
        "id": chat["id"],
        "title": chat["title"]
    })


@app.route("/api/chats", methods=["GET"])
@login_required
def get_chats():
    history = load_history(current_user.id)

    chats = [
        {
            "id": chat["id"],
            "title": chat["title"],
            "created_at": chat["created_at"]
        }
        for chat in reversed(history)
    ]

    return jsonify(chats)


@app.route("/api/chats/<chat_id>/clear", methods=["POST"])
@login_required
def clear_chat_route(chat_id):
    if clear_chat(chat_id, current_user.id):
        return jsonify({"message": "Chat cleared successfully"})

    return jsonify({"error": "Chat not found"}), 404


@app.route("/api/chats/<chat_id>", methods=["GET"])
@login_required
def get_chat(chat_id):
    history = load_history(current_user.id)

    for chat in history:
        if chat["id"] == chat_id:
            return jsonify(chat)

    return jsonify({"error": "Chat not found"}), 404


@app.route("/api/chats/<chat_id>", methods=["DELETE"])
@login_required
def remove_chat(chat_id):
    if delete_chat(chat_id, current_user.id):
        return jsonify({"message": "Chat deleted successfully"})

    return jsonify({"error": "Chat not found"}), 404


@app.route("/api/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json(silent=True) or {}

    user_message = data.get("message", "").strip()
    chat_id = data.get("chat_id", "").strip()

    if not user_message:
        return jsonify({"error": "Please enter a message."}), 400

    history = load_history(current_user.id)

    selected_chat = next(
        (item for item in history if item["id"] == chat_id),
        None
    )

    if selected_chat is None:
        return jsonify({"error": "Chat not found. Please start a new chat."}), 404

    add_message(chat_id, "user", user_message, current_user.id)

    previous_messages = selected_chat["messages"][-11:]

    conversation = []

    for message in previous_messages:
        role = "User" if message["role"] == "user" else "Assistant"
        conversation.append(f"{role}: {message['content']}")

    conversation_history = "\n".join(conversation)

    prompt = f"""
You are a helpful AI assistant.
Continue the conversation naturally.
Use previous messages to understand the user's questions.

Previous conversation:
{conversation_history}

User: {user_message}

Assistant:
"""

    def generate():
        full_response = ""

        try:
            for token in stream_response(prompt):
                full_response += token
                yield json.dumps({"token": token}) + "\n"

            add_message(
                chat_id,
                "assistant",
                full_response,
                current_user.id
            )

            yield json.dumps({"done": True}) + "\n"

        except Exception as error:
            yield json.dumps({"error": str(error)}) + "\n"

    return Response(
        stream_with_context(generate()),
        mimetype="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
