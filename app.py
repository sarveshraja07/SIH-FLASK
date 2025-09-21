from flask import Flask, render_template, request, redirect, url_for, session
from simulation_core import (
    create_random_trains,
    simulate_without_ai,
    simulate_ai_prediction,
    simulate_ai_prevention,
    Train
)
import os

app = Flask(__name__)
# Use environment variable for secret key if available, otherwise fallback
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")  

# 🔹 Global variable to store last simulation's AI actions
global_ai_actions = []

# 🔹 Hardcoded credentials
VALID_EMAIL = "sarveshraja2007@gmail.com"
VALID_PASSWORD = "sarvesh@07"


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/info")
def info():
    # Pass the last stored AI actions to info.html
    return render_template("info.html", ai_actions=global_ai_actions)


@app.route("/simulation", methods=["GET", "POST"])
def simulation():
    global global_ai_actions

    # Restrict access if not logged in
    if "user" not in session:
        return redirect(url_for("login"))

    initial_trains = None
    history_no_ai = None
    collisions_no_ai = None
    history_prediction = None
    predicted_collisions = None
    history_prevention = None
    ai_actions = None
    summarized_actions = None

    if request.method == "POST":
        num_trains = int(request.form.get("num_trains"))
        initial_trains = create_random_trains(num_trains)

        # Simulate scenarios
        history_no_ai, collisions_no_ai = simulate_without_ai(
            [Train(t.id, t.position, t.speed) for t in initial_trains]
        )
        history_prediction, predicted_collisions = simulate_ai_prediction(
            [Train(t.id, t.position, t.speed) for t in initial_trains]
        )
        history_prevention, ai_actions, summarized_actions = simulate_ai_prevention(
            [Train(t.id, t.position, t.speed) for t in initial_trains]
        )

        # 🔹 Store the latest AI actions globally for info.html
        global_ai_actions = ai_actions

    return render_template(
        "index.html",
        initial_trains=initial_trains,
        history_no_ai=history_no_ai,
        collisions_no_ai=collisions_no_ai,
        history_prediction=history_prediction,
        predicted_collisions=predicted_collisions,
        history_prevention=history_prevention,
        ai_actions=ai_actions,
        summarized_actions=summarized_actions,
        logged_in=True
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email == VALID_EMAIL and password == VALID_PASSWORD:
            session["user"] = email  # store user in session
            return redirect(url_for("simulation"))
        else:
            return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)  # remove user from session
    return redirect(url_for("home"))


if __name__ == "__main__":
    # Use Render's port or default 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
