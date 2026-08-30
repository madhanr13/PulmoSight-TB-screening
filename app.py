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

RESULTS = []


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
    return render_template("home.html", runtime_mode=classifier.runtime_mode, is_admin=session.get("is_admin", False))


@app.get("/dashboard")
def dashboard():
    return render_template("dashboard.html", runtime_mode=classifier.runtime_mode, is_admin=session.get("is_admin", False), results=RESULTS[:5])


@app.get("/methodology")
def methodology():
    return render_template("methodology.html", runtime_mode=classifier.runtime_mode, is_admin=session.get("is_admin", False))


@app.get("/about")
def about():
    return render_template("about.html", runtime_mode=classifier.runtime_mode, is_admin=session.get("is_admin", False))


@app.get("/gallery")
def gallery():
    dataset = [
        {"name": "TB-01", "count": 184, "type": "Positive", "accent": "positive"},
        {"name": "TB-02", "count": 213, "type": "Borderline", "accent": "warning"},
        {"name": "TB-03", "count": 322, "type": "Normal", "accent": "neutral"},
        {"name": "TB-04", "count": 475,
            "type": "High confidence", "accent": "positive"},
    ]
    return render_template("gallery.html", runtime_mode=classifier.runtime_mode, is_admin=session.get("is_admin", False), dataset=dataset)


@app.get("/history")
def history():
    return render_template("history.html", runtime_mode=classifier.runtime_mode, is_admin=session.get("is_admin", False), results=RESULTS)


@app.get("/reports")
def reports():
    positives = sum(1 for item in RESULTS if item.get("status") == "positive")
    negatives = sum(1 for item in RESULTS if item.get("status") == "negative")
    return render_template(
        "reports.html",
        runtime_mode=classifier.runtime_mode,
        is_admin=session.get("is_admin", False),
        total=len(RESULTS),
        positives=positives,
        negatives=negatives,
        summary={
            "avg_score": round(sum(item.get("score", 0) for item in RESULTS) / len(RESULTS), 1) if RESULTS else 0,
            "last_run": RESULTS[0].get("timestamp") if RESULTS else "No runs yet",
        },
    )


@app.get("/login")
def login():
    if session.get("is_admin"):
        return redirect(url_for("dashboard"))
    return render_template("login.html", runtime_mode=classifier.runtime_mode, is_admin=False)


@app.post("/login")
def login_submit():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    if email == app.config["ADMIN_EMAIL"].lower() and password == app.config["ADMIN_PASSWORD"]:
        session["is_admin"] = True
        return redirect(url_for("dashboard"))
    return render_template("login.html", runtime_mode=classifier.runtime_mode, is_admin=False, error="Invalid admin credentials."), 401


@app.get("/logout")
def logout():
    session.pop("is_admin", None)
    return redirect(url_for("home"))


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
