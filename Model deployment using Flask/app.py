from flask import Flask, render_template, request, redirect, url_for, session
import joblib
import numpy as np
from datetime import datetime
from collections import Counter

app = Flask(__name__)
app.secret_key = "ultrasecretkey"

model = joblib.load("model.pkl")

user_history = []
notifications = []
#th
FLAGGED_TERMS = [
    "breaking",
    "shocking",
    "viral",
    "exclusive",
    "exposed",
    "must read",
    "secret",
    "urgent",
    "click here",
    "unbelievable"
]


def analyze_text_metrics(news):
    text = news.strip()
    lowered = text.lower()
    words = [word for word in text.replace("\n", " ").split(" ") if word]
    word_count = len(words)
    sentence_count = max(1, text.count(".") + text.count("!") + text.count("?"))
    flagged_terms = [term for term in FLAGGED_TERMS if term in lowered]
    uppercase_ratio = round(
        sum(1 for char in text if char.isupper()) / max(1, sum(1 for char in text if char.isalpha())),
        2
    )
    reading_time = max(1, round(word_count / 180))

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "flagged_terms": flagged_terms,
        "flagged_count": len(flagged_terms),
        "uppercase_ratio": uppercase_ratio,
        "reading_time": reading_time
    }


def build_dashboard_context():
    total = len(user_history)
    real = sum(1 for h in user_history if h["result"] == "REAL NEWS")
    fake = total - real
    latest = session.get("latest_result")
    recent_history = user_history[::-1][:4]
    avg_confidence = round(
        sum(item["confidence"] for item in user_history) / total,
        2
    ) if total else 0

    common_flags = Counter(
        flag
        for item in user_history
        for flag in item.get("flagged_terms", [])
    ).most_common(4)

    latest_metrics = recent_history[0] if recent_history else None

    return {
        "total": total,
        "real": real,
        "fake": fake,
        "latest": latest,
        "notifications": notifications[-6:],
        "recent_history": recent_history,
        "avg_confidence": avg_confidence,
        "fake_rate": round((fake / total) * 100, 2) if total else 0,
        "common_flags": common_flags,
        "latest_metrics": latest_metrics,
        "username": session.get("user", "admin")
    }


def login_required(func):
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login_page"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@app.route("/")
def login_page():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    if username == "admin" and password == "admin":
        session["user"] = username
        notifications.append("User logged in successfully.")
        return redirect(url_for("dashboard"))
    else:
        return render_template("login.html", error="Invalid Credentials")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", **build_dashboard_context())


@app.route("/predict", methods=["POST"])
@login_required
def predict():
    news = request.form["news"]
    metrics = analyze_text_metrics(news)

    prediction = model.predict([news])[0]
    score = model.decision_function([news])[0]
    confidence = round((1 / (1 + np.exp(-abs(score)))) * 100, 2)

    label = "REAL NEWS" if prediction == 1 else "FAKE NEWS"
    color = "real" if prediction == 1 else "fake"

    session["latest_result"] = {
        "label": label,
        "confidence": confidence,
        "color": color,
        "word_count": metrics["word_count"],
        "flagged_count": metrics["flagged_count"],
        "reading_time": metrics["reading_time"]
    }

    user_history.append({
        "text": news[:80] + "...",
        "result": label,
        "confidence": confidence,
        "time": datetime.now().strftime("%H:%M:%S"),
        "word_count": metrics["word_count"],
        "sentence_count": metrics["sentence_count"],
        "flagged_terms": metrics["flagged_terms"],
        "flagged_count": metrics["flagged_count"],
        "uppercase_ratio": metrics["uppercase_ratio"],
        "reading_time": metrics["reading_time"]
    })

    notifications.append(f"New prediction: {label} at {datetime.now().strftime('%H:%M')}")

    return redirect(url_for("dashboard"))


@app.route("/history")
@login_required
def history():
    selected_result = request.args.get("result", "ALL")
    filtered_history = user_history[::-1]

    if selected_result in {"REAL NEWS", "FAKE NEWS"}:
        filtered_history = [item for item in filtered_history if item["result"] == selected_result]

    return render_template(
        "history.html",
        history=filtered_history,
        username=session.get("user", "admin"),
        selected_result=selected_result
    )


@app.route("/analytics")
@login_required
def analytics():
    context = build_dashboard_context()
    history_data = user_history[::-1]
    confidence_bands = {
        "high": sum(1 for item in history_data if item["confidence"] >= 85),
        "mid": sum(1 for item in history_data if 70 <= item["confidence"] < 85),
        "low": sum(1 for item in history_data if item["confidence"] < 70)
    }

    return render_template(
        "analytics.html",
        history=history_data[:6],
        confidence_bands=confidence_bands,
        **context
    )


@app.route("/workspace")
@login_required
def workspace():
    return render_template(
        "workspace.html",
        username=session.get("user", "admin"),
        notifications=notifications[-4:],
        checklist=[
            "Review article framing and tone.",
            "Check named sources and publication date.",
            "Compare confidence with suspicious phrase count.",
            "Store uncertain items for manual review."
        ]
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


if __name__ == "__main__":
    app.run(debug=True)
