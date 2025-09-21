import random
import math
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend for server
import matplotlib.pyplot as plt
import os
from flask import Flask, render_template

# ------------------------
# PARAMETERS
# ------------------------
SAFE_DISTANCE = 500        # meters
REACTION_TIME = 5          # seconds
DECELERATION = 1.0         # m/s²
TIME_STEP = 1              # seconds
MAX_STEPS = 50             # total simulation steps
MIN_SPEED = 20 * 1000 / 3600  # 20 km/h in m/s

# Fix seed for reproducibility
random.seed(42)

# Directory for saving plots
PLOT_DIR = "static/plots"
os.makedirs(PLOT_DIR, exist_ok=True)

# ------------------------
# TRAIN CLASS
# ------------------------
class Train:
    def __init__(self, train_id, position, speed):
        self.id = train_id
        self.position = position
        self.speed = speed
        self.original_speed = speed

# ------------------------
# HELPER FUNCTIONS
# ------------------------
def calculate_safety_gap(speed_mps):
    braking = (speed_mps ** 2) / (2 * DECELERATION)
    reaction = speed_mps * REACTION_TIME
    return braking + reaction + SAFE_DISTANCE

def create_random_trains(num_trains):
    trains = []
    for i in range(num_trains):
        position = random.uniform(0, 5000)
        speed = random.uniform(20, 120) * 1000 / 3600
        trains.append(Train(i + 1, position, speed))
    return trains

def save_train_plot(history, filename_prefix):
    plt.figure(figsize=(9, 5))
    for train_id, positions in history.items():
        plt.plot(range(len(positions)), positions, label=f"Train {train_id}")
    plt.xlabel("Time step")
    plt.ylabel("Position (m)")
    plt.title("Train Simulation")
    plt.legend()
    filepath = os.path.join(PLOT_DIR, f"{filename_prefix}.png")
    plt.savefig(filepath)
    plt.close()
    return filepath

# ------------------------
# SIMULATIONS
# ------------------------
def simulate_without_ai(trains):
    history = {train.id: [] for train in trains}
    collisions = []
    for t in range(MAX_STEPS):
        for train in trains:
            history[train.id].append(train.position)
        trains.sort(key=lambda x: x.position)
        for i in range(len(trains) - 1):
            follower = trains[i]
            lead = trains[i + 1]
            gap = lead.position - follower.position
            safe_gap = calculate_safety_gap(follower.speed)
            if gap < safe_gap:
                collisions.append((t, follower.position))
        for train in trains:
            train.position += train.speed * TIME_STEP
    plot_path = save_train_plot(history, "no_ai")
    return history, collisions, plot_path

def simulate_ai_prediction(trains):
    history = {train.id: [] for train in trains}
    predicted_collisions = []
    for t in range(MAX_STEPS):
        for train in trains:
            history[train.id].append(train.position)
        trains.sort(key=lambda x: x.position)
        for i in range(len(trains) - 1):
            follower = trains[i]
            lead = trains[i + 1]
            gap = lead.position - follower.position
            safe_gap = calculate_safety_gap(follower.speed)
            if gap < safe_gap:
                predicted_collisions.append((t, follower.position))
        for train in trains:
            train.position += train.speed * TIME_STEP
    plot_path = save_train_plot(history, "ai_prediction")
    return history, predicted_collisions, plot_path

def simulate_ai_prevention(trains):
    history = {train.id: [] for train in trains}
    ai_actions = []

    for t in range(MAX_STEPS):
        for train in trains:
            history[train.id].append(train.position)
        trains.sort(key=lambda x: x.position)
        for i in range(len(trains) - 1):
            follower = trains[i]
            lead = trains[i + 1]
            gap = lead.position - follower.position
            safe_gap = calculate_safety_gap(follower.speed)

            if gap < safe_gap:
                gap_diff = gap - SAFE_DISTANCE
                recommended_speed = math.sqrt(2 * DECELERATION * gap_diff) if gap_diff > 0 else MIN_SPEED
                recommended_speed = max(MIN_SPEED, recommended_speed)
                if recommended_speed < follower.speed:
                    ai_actions.append((t, follower.id, follower.speed, recommended_speed, follower.position))
                    follower.speed = recommended_speed

        for train in trains:
            train.position += train.speed * TIME_STEP

    # Summarize actions per train
    summarized_actions = []
    actions_by_train = {}
    for action in ai_actions:
        t_id = action[1]
        if t_id not in actions_by_train:
            actions_by_train[t_id] = []
        actions_by_train[t_id].append(action)

    for t_id, actions in actions_by_train.items():
        total = len(actions)
        if total == 1:
            summarized_actions.append(actions[0])
        elif total > 1:
            summarized_actions.append(actions[0])
            summarized_actions.append(actions[total // 2])
            summarized_actions.append(actions[-1])

    plot_path = save_train_plot(history, "ai_prevention")
    return history, ai_actions, summarized_actions, plot_path

# ------------------------
# FLASK APP
# ------------------------
app = Flask(__name__)

@app.route('/')
def index():
    trains = create_random_trains(5)
    
    # Run simulations
    no_ai_hist, no_ai_coll, no_ai_plot = simulate_without_ai([Train(t.id, t.position, t.speed) for t in trains])
    ai_pred_hist, ai_pred_coll, ai_pred_plot = simulate_ai_prediction([Train(t.id, t.position, t.speed) for t in trains])
    ai_prev_hist, ai_prev_actions, ai_prev_summarized, ai_prev_plot = simulate_ai_prevention([Train(t.id, t.position, t.speed) for t in trains])

    return render_template(
        "simulation.html",
        no_ai_plot=no_ai_plot,
        no_ai_coll=no_ai_coll,
        ai_pred_plot=ai_pred_plot,
        ai_pred_coll=ai_pred_coll,
        ai_prev_plot=ai_prev_plot,
        ai_prev_actions=ai_prev_summarized
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
