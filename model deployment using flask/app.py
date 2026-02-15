from flask import Flask, render_template, request, redirect, url_for, session
import joblib
import numpy as np
from datetime import datetime

app = Flask(__name__)
app.secret_key = "ultrasecretkey"

model = joblib.load("model.pkl")

user_history = []
notifications = []


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
    total = len(user_history)
    real = sum(1 for h in user_history if h["result"] == "REAL NEWS")
    fake = total - real

    latest = session.get("latest_result")

    return render_template(
        "dashboard.html",
        total=total,
        real=real,
        fake=fake,
        notifications=notifications[-5:],
        latest=latest
    )


@app.route("/predict", methods=["POST"])
@login_required
def predict():
    news = request.form["news"]

    prediction = model.predict([news])[0]
    score = model.decision_function([news])[0]
    confidence = round((1 / (1 + np.exp(-abs(score)))) * 100, 2)

    label = "REAL NEWS" if prediction == 1 else "FAKE NEWS"
    color = "real" if prediction == 1 else "fake"

    session["latest_result"] = {
        "label": label,
        "confidence": confidence,
        "color": color
    }

    user_history.append({
        "text": news[:80] + "...",
        "result": label,
        "confidence": confidence,
        "time": datetime.now().strftime("%H:%M:%S")
    })

    notifications.append(f"New prediction: {label}")

    return redirect(url_for("dashboard"))


@app.route("/history")
@login_required
def history():
    return render_template("history.html", history=user_history[::-1])


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


if __name__ == "__main__":
    app.run(debug=True)
