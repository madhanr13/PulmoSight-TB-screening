import os
from datetime import datetime

from flask import Flask, jsonify, render_template, request, redirect, session, url_for

from ga_mobilenet import GAMobileNetClassifier
from preprocessing import ImageValidationError, preprocess_upload

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024
app.config["SECRET_KEY"] = os.getenv(
    "PULMOSIGHT_SECRET_KEY", "dev-secret-change-me")
app.config["ADMIN_EMAIL"] = os.getenv(
    "PULMOSIGHT_ADMIN_EMAIL", "admin@pulmosight.ai")
app.config["ADMIN_PASSWORD"] = os.getenv(
    "PULMOSIGHT_ADMIN_PASSWORD", "admin123")
classifier = GAMobileNetClassifier()

USERS = {
    app.config["ADMIN_EMAIL"].lower(): {
        "password": app.config["ADMIN_PASSWORD"],
        "role": "admin",
    }
}
RESULTS = []


def _is_public_route(path):
    public_paths = {
        "/login",
        "/register",
        "/logout",
        "/api/login",
        "/api/register",
        "/api/auth/status",
        "/api/logout",
    }
    return path in public_paths or path.startswith("/static/")


@app.before_request
def enforce_authentication():
    if session.get("user") or session.get("is_admin"):
        return None

    if _is_public_route(request.path):
        return None

    if request.path.startswith("/api/"):
        return jsonify({"ok": False, "error": "Authentication required."}), 401

    return redirect(url_for("login"))


def _authenticate_credentials(email, password):
    normalized_email = (email or "").strip().lower()
    normalized_password = password or ""
    user = USERS.get(normalized_email)
    return bool(user and user["password"] == normalized_password)


def _current_user():
    if session.get("user"):
        return session["user"]
    if session.get("is_admin"):
        return {"email": app.config["ADMIN_EMAIL"], "role": "admin"}
    return None


def _save_result(result_data):
    entry = {
        "id": len(RESULTS) + 1,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        **result_data,
    }
    RESULTS.insert(0, entry)
    return entry


@app.get("/")
def home():
    if not _current_user():
        return redirect(url_for("login"))
    return render_template("home.html", runtime_mode=classifier.runtime_mode, is_admin=True, user=_current_user())


@app.get("/dashboard")
def dashboard():
    total = len(RESULTS)
    positives = sum(1 for item in RESULTS if item.get("status") == "positive")
    negatives = sum(1 for item in RESULTS if item.get("status") == "negative")
    return render_template(
        "dashboard.html",
        runtime_mode=classifier.runtime_mode,
        is_admin=True,
        user=_current_user(),
        results=RESULTS[:5],
        total=total,
        positives=positives,
        negatives=negatives,
        latest=RESULTS[0] if RESULTS else None,
    )


@app.get("/methodology")
def methodology():
    return render_template("methodology.html", runtime_mode=classifier.runtime_mode, is_admin=True, user=_current_user())


@app.get("/about")
def about():
    return render_template("about.html", runtime_mode=classifier.runtime_mode, is_admin=True, user=_current_user())


@app.get("/gallery")
def gallery():
    dataset = [item for item in RESULTS if item.get("filename")]
    return render_template("gallery.html", runtime_mode=classifier.runtime_mode, is_admin=True, user=_current_user(), dataset=dataset)


@app.get("/history")
def history():
    return render_template("history.html", runtime_mode=classifier.runtime_mode, is_admin=True, user=_current_user(), results=RESULTS)


@app.get("/reports")
def reports():
    positives = sum(1 for item in RESULTS if item.get("status") == "positive")
    negatives = sum(1 for item in RESULTS if item.get("status") == "negative")
    return render_template(
        "reports.html",
        runtime_mode=classifier.runtime_mode,
        is_admin=True,
        user=_current_user(),
        total=len(RESULTS),
        positives=positives,
        negatives=negatives,
    )


@app.get("/login")
def login():
    if _current_user():
        return redirect(url_for("home"))
    return render_template("login.html", runtime_mode=classifier.runtime_mode, is_admin=False)


@app.get("/register")
def register():
    if _current_user():
        return redirect(url_for("home"))
    return render_template("register.html", runtime_mode=classifier.runtime_mode, is_admin=False)


@app.get("/api/auth/status")
def auth_status():
    user = _current_user()
    return jsonify({
        "authenticated": bool(user),
        "user": user,
    })


@app.post("/api/register")
def api_register():
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    if not email or not password:
        return jsonify({"ok": False, "error": "Email and password are required."}), 400
    if len(password) < 6:
        return jsonify({"ok": False, "error": "Password must be at least 6 characters."}), 400
    if email in USERS:
        return jsonify({"ok": False, "error": "An account with this email already exists."}), 409
    USERS[email] = {"password": password, "role": "user"}
    session["user"] = {"email": email, "role": "user"}
    return jsonify({"ok": True, "redirect": url_for("home"), "user": session["user"]})


@app.post("/api/login")
def api_login():
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", request.form.get("email", ""))).strip()
    password = str(payload.get("password", request.form.get("password", "")))

    if _authenticate_credentials(email, password):
        user = USERS[email.strip().lower()]
        session["user"] = {"email": email.strip().lower(),
                           "role": user["role"]}
        return jsonify({
            "ok": True,
            "message": "Login successful.",
            "redirect": url_for("home"),
            "user": session["user"],
        })

    return jsonify({
        "ok": False,
        "error": "Invalid admin credentials.",
    }), 401


@app.post("/login")
def login_submit():
    email = request.form.get("email", "")
    password = request.form.get("password", "")
    if _authenticate_credentials(email, password):
        user = USERS[email.strip().lower()]
        session["user"] = {"email": email.strip().lower(),
                           "role": user["role"]}
        return redirect(url_for("dashboard"))
    return render_template("login.html", runtime_mode=classifier.runtime_mode, is_admin=False, error="Invalid admin credentials."), 401


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.post("/api/logout")
def api_logout():
    session.clear()
    return jsonify({"ok": True, "redirect": url_for("login")})


@app.get("/api/export-report")
def export_report():
    payload = {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "runtime_mode": classifier.runtime_mode,
        "total_cases": len(RESULTS),
        "results": RESULTS,
    }
    response = jsonify(payload)
    response.headers["Content-Disposition"] = "attachment; filename=pulmosight_report.json"
    return response


@app.post("/api/predict")
def predict():
    upload = request.files.get("image")
    if upload is None or not upload.filename:
        return jsonify({"error": "Choose a chest radiograph before analyzing."}), 400

    try:
        processed = preprocess_upload(upload)
        result = classifier.predict(processed.tensor)
        result.update({
            "filename": processed.filename,
            "image_size": processed.image_size,
            "mode": classifier.runtime_mode,
        })
        _save_result(result)
        return jsonify(result)
    except ImageValidationError as error:
        return jsonify({"error": str(error)}), 400
    except Exception:
        app.logger.exception("Prediction failed")
        return jsonify({"error": "The image could not be analyzed. Please try another file."}), 500


@app.errorhandler(413)
def payload_too_large(_error):
    return jsonify({"error": "The image is larger than the 12 MB limit."}), 413


if __name__ == "__main__":
    app.run(debug=True, port=5000)
