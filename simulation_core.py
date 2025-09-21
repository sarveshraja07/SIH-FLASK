import random
import math

# --------------------------------
# PARAMETERS
# --------------------------------
SAFE_DISTANCE = 500        # meters
REACTION_TIME = 5          # seconds
DECELERATION = 1.0         # m/s²
TIME_STEP = 1              # seconds
MAX_STEPS = 50             # total simulation steps
MIN_SPEED = 20 * 1000 / 3600  # 20 km/h in m/s

# Fix seed for reproducibility
random.seed(42)


# TRAIN CLASS

class Train:
    def __init__(self, train_id, position, speed):
        self.id = train_id
        self.position = position
        self.speed = speed
        self.original_speed = speed



# SAFE GAP

def calculate_safety_gap(speed_mps):
    braking = (speed_mps ** 2) / (2 * DECELERATION)
    reaction = speed_mps * REACTION_TIME
    return braking + reaction + SAFE_DISTANCE



# CREATE TRAINS

def create_random_trains(num_trains):
    trains = []
    for i in range(num_trains):
        position = random.uniform(0, 5000)
        speed = random.uniform(20, 120) * 1000 / 3600
        trains.append(Train(i + 1, position, speed))
    return trains



# SIMULATE WITHOUT AI

def simulate_without_ai(trains):
    history = {train.id: [] for train in trains}
    collisions = []
    for time_step in range(MAX_STEPS):
        for train in trains:
            history[train.id].append(train.position)
        trains.sort(key=lambda x: x.position)
        for i in range(len(trains) - 1):
            follower = trains[i]
            lead = trains[i + 1]
            gap = lead.position - follower.position
            safe_gap = calculate_safety_gap(follower.speed)
            if gap < safe_gap:
                collisions.append((time_step, follower.position))
        for train in trains:
            train.position += train.speed * TIME_STEP
    return history, collisions



# SIMULATE AI PREDICTION

def simulate_ai_prediction(trains):
    history = {train.id: [] for train in trains}
    predicted_collisions = []
    for time_step in range(MAX_STEPS):
        for train in trains:
            history[train.id].append(train.position)
        trains.sort(key=lambda x: x.position)
        for i in range(len(trains) - 1):
            follower = trains[i]
            lead = trains[i + 1]
            gap = lead.position - follower.position
            safe_gap = calculate_safety_gap(follower.speed)
            if gap < safe_gap:
                predicted_collisions.append((time_step, follower.position))
        for train in trains:
            train.position += train.speed * TIME_STEP
    return history, predicted_collisions



# SIMULATE AI PREVENTION

def simulate_ai_prevention(trains):
    history = {train.id: [] for train in trains}
    ai_actions = []  # (time, train_id, old_speed, new_speed, position)

    for time_step in range(MAX_STEPS):
        for train in trains:
            history[train.id].append(train.position)

        trains.sort(key=lambda x: x.position)

        for i in range(len(trains) - 1):
            follower = trains[i]
            lead = trains[i + 1]
            gap = lead.position - follower.position
            safe_gap = calculate_safety_gap(follower.speed)

            if gap < safe_gap:  # unsafe gap → trigger AI
                gap_diff = gap - SAFE_DISTANCE
                if gap_diff > 0:
                    recommended_speed = math.sqrt(2 * DECELERATION * gap_diff)
                else:
                    recommended_speed = MIN_SPEED

                recommended_speed = max(MIN_SPEED, recommended_speed)

                # Record follower (only if speed reduces)
                if recommended_speed < follower.speed:
                    ai_actions.append((
                        time_step,
                        follower.id,
                        follower.speed,   # old speed
                        recommended_speed,  # reduced speed
                        follower.position
                    ))
                    follower.speed = recommended_speed  # update

                # Always record lead as "involved" (speed unchanged)
                ai_actions.append((
                    time_step,
                    lead.id,
                    lead.speed,
                    lead.speed,   # no reduction
                    lead.position
                ))

        # Move trains after decisions
        for train in trains:
            train.position += train.speed * TIME_STEP

    #  Summarize (first, middle, last) for labels
    summarized_actions = []
    actions_by_train = {}

    for action in ai_actions:
        t_id = action[1]
        # only include trains where speed was reduced
        if action[2] != action[3]:
            if t_id not in actions_by_train:
                actions_by_train[t_id] = []
            actions_by_train[t_id].append(action)

    for t_id, actions in actions_by_train.items():
        total = len(actions)
        if total == 1:
            summarized_actions.append(actions[0])
        elif total > 1:
            summarized_actions.append(actions[0])         # first
            summarized_actions.append(actions[total // 2]) # middle
            summarized_actions.append(actions[-1])        # last

    return history, ai_actions, summarized_actions
