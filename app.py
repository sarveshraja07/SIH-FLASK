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
    return render_template("info.html", ai_actions=global_ai_actions)


@app.route("/simulation", methods=["GET", "POST"])
def simulation():
    global global_ai_actions

    if "user" not in session:
        return redirect(url_for("login"))

    # Initialize variables
    initial_trains = None
    history_no_ai = collisions_no_ai = plot_no_ai = None
    history_prediction = predicted_collisions = plot_prediction = None
    history_prevention = ai_actions = summarized_actions = plot_prevention = None

    if request.method == "POST":
        try:
            num_trains = int(request.form.get("num_trains", 5))
        except ValueError:
            num_trains = 5

        # Create initial trains
        initial_trains = create_random_trains(num_trains)

        # Copy trains for each simulation
        trains_no_ai = [Train(t.id, t.position, t.speed) for t in initial_trains]
        trains_pred = [Train(t.id, t.position, t.speed) for t in initial_trains]
        trains_prev = [Train(t.id, t.position, t.speed) for t in initial_trains]

        # Run simulations and unpack correctly
        history_no_ai, collisions_no_ai, plot_no_ai = simulate_without_ai(trains_no_ai)
        history_prediction, predicted_collisions, plot_prediction = simulate_ai_prediction(trains_pred)
        history_prevention, ai_actions, summarized_actions, plot_prevention = simulate_ai_prevention(trains_prev)

        # Store latest AI actions globally
        global_ai_actions = summarized_actions

    return render_template(
        "simulation.html",
        initial_trains=initial_trains,
        history_no_ai=history_no_ai,
        collisions_no_ai=collisions_no_ai,
        plot_no_ai=plot_no_ai,
        history_prediction=history_prediction,
        predicted_collisions=predicted_collisions,
        plot_prediction=plot_prediction,
        history_prevention=history_prevention,
        ai_actions=ai_actions,
        summarized_actions=summarized_actions,
        plot_prevention=plot_prevention,
        logged_in=True
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email == VALID_EMAIL and password == VALID_PASSWORD:
            session["user"] = email
            return redirect(url_for("simulation"))
        else:
            return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
