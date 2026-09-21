import os
from pathlib import Path
from flask import Flask, jsonify, request, render_template, send_from_directory
from werkzeug.utils import secure_filename

from backend.database import initialize_database, add_transfer, list_transfers
from backend.security.encryption import encrypt_bytes, encode_bytes
from backend.ai_monitor import analyze_transfer

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

if os.environ.get("VERCEL"):
    STORAGE_DIR = Path("/tmp/secure_data_transfer/encrypted")
else:
    STORAGE_DIR = BASE_DIR / "storage" / "encrypted"

STORAGE_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR / "static"),
    template_folder=str(FRONTEND_DIR / "templates"),
)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024
app.config["SECRET_KEY"] = "development-only-change-me"

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(FRONTEND_DIR / "static", filename)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/login", methods=["POST"])
def login():
    payload = request.get_json(silent=True) or {}
    username = payload.get("username", "")
    password = payload.get("password", "")

    if username == "admin" and password == "admin123":
        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": username,
        })

    return jsonify({
        "success": False,
        "message": "Invalid username or password",
    }), 401


@app.route("/api/transfers", methods=["GET"])
def transfers():
    return jsonify(list_transfers())


@app.route("/api/transfer", methods=["POST"])
def create_transfer():
    uploaded_file = request.files.get("file")
    receiver = request.form.get("receiver", "").strip()
    sender = request.form.get("sender", "Organization A").strip()

    if uploaded_file is None or not uploaded_file.filename:
        return jsonify({"success": False, "message": "Please select a file"}), 400

    if not receiver:
        return jsonify({"success": False, "message": "Receiver is required"}), 400

    original_filename = secure_filename(uploaded_file.filename)
    file_data = uploaded_file.read()

    if not file_data:
        return jsonify({"success": False, "message": "The selected file is empty"}), 400

    nonce, encrypted_data = encrypt_bytes(file_data)

    stored_filename = f"transfer_{len(list(STORAGE_DIR.iterdir())) + 1}.bin"
    stored_path = STORAGE_DIR / stored_filename

    # Store nonce and encrypted content together.
    stored_path.write_bytes(nonce + encrypted_data)

    risk = analyze_transfer(file_size=len(file_data))

    transfer_id = add_transfer(
        original_filename=original_filename,
        stored_filename=stored_filename,
        sender=sender,
        receiver=receiver,
        file_size=len(file_data),
        risk_label=risk["risk_label"],
    )

    return jsonify({
        "success": True,
        "message": "File encrypted and transfer recorded",
        "transfer_id": transfer_id,
        "risk": risk,
        "encrypted_preview": encode_bytes(encrypted_data[:24]),
    }), 201


if __name__ == "__main__":
    initialize_database()
    app.run(host="127.0.0.1", port=5000, debug=True)
