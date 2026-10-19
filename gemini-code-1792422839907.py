import datetime
import json
import os
import time
import streamlit as st

LOG_FILE = "workout_logs.json"


def load_logs():
  if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r") as f:
      return json.load(f)
  return {}


def save_logs(logs):
  with open(LOG_FILE, "w") as f:
    json.dump(logs, f, indent=4)


# Phase-based rest period rules
REST_RULES = {
    "Phase 1 (Strength: 3-5 reps compounds / 8-12 reps isolation)": {
        "compound_rest": "2.0 - 3.0 min",
        "compound_seconds": 120,
        "isolation_rest": "1.0 - 1.5 min",
        "isolation_seconds": 60,
    },
    "Phase 2 (Hypertrophy: 5-8 reps compounds / 12-15 reps isolation)": {
        "compound_rest": "1.5 - 2.0 min",
        "compound_seconds": 90,
        "isolation_rest": "1.0 min",
        "isolation_seconds": 60,
    },
}

# Workouts with distinct target-swaps per rotation (Chest Fly & Rear Delt present together)
WORKOUT_TEMPLATES = {
    "Upper A (Chest / Back / Shoulders / Arms)": {
        "Gym": {
            "Rotation 1": {
                "compounds": [
                    {"name": "Barbell Bench Press", "sets": 4, "rep_range": "3-5"},
                    {"name": "Seated Machine Row", "sets": 4, "rep_range": "3-5"},
                    {
                        "name": "Seated Overhead Barbell Press",
                        "sets": 3,
                        "rep_range": "5-8",
                    },
                ],
                "accessories": [
                    {
                        "name": "Machine Chest Fly (Pec Deck)",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Machine Rear Delt Fly (Reverse Pec Deck)",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Cable Lateral Raise",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Cable Tricep Pushdown",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Cable Bicep Curl",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
            "Rotation 2": {
                "compounds": [
                    {
                        "name": "Incline Machine Chest Press",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {"name": "Heavy Lat Pulldown", "sets": 4, "rep_range": "3-5"},
                    {
                        "name": "Seated Overhead Dumbbell Press",
                        "sets": 3,
                        "rep_range": "5-8",
                    },
                ],
                "accessories": [
                    {
                        "name": "Incline Dumbbell Fly",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Cable Face Pull (Rear Delts)",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Dumbbell Lateral Raise",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Overhead Cable Tricep Extension",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Incline Dumbbell Bicep Curl",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
        },
        "Home": {
            "Rotation 1": {
                "compounds": [
                    {"name": "Barbell Floor Press", "sets": 4, "rep_range": "3-5"},
                    {
                        "name": "Heavy Bent-Over Barbell Row",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {
                        "name": "Standing Overhead Barbell Press",
                        "sets": 3,
                        "rep_range": "5-8",
                    },
                ],
                "accessories": [
                    {
                        "name": "Resistance Band Chest Fly",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Resistance Band Rear Delt Fly",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Resistance Band Lateral Raise",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Band Tricep Pushdown",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Resistance Band Bicep Curl",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
            "Rotation 2": {
                "compounds": [
                    {
                        "name": "Resistance Band Push-Up",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {
                        "name": "Underhand Band Row",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {
                        "name": "Standing Overhead Barbell Press",
                        "sets": 3,
                        "rep_range": "5-8",
                    },
                ],
                "accessories": [
                    {
                        "name": "Resistance Band Chest Fly",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Resistance Band Face Pull",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Resistance Band Lateral Raise",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Band Overhead Tricep Extension",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Resistance Band Hammer Curl",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
        },
    },
    "Lower A (Quads / Hamstrings / Glutes / Calves)": {
        "Gym": {
            "Rotation 1": {
                "compounds": [
                    {"name": "Barbell Back Squat", "sets": 4, "rep_range": "3-5"},
                    {
                        "name": "Romanian Deadlift (Barbell)",
                        "sets": 3,
                        "rep_range": "5-8",
                    },
                ],
                "accessories": [
                    {"name": "Leg Press Machine", "sets": 3, "rep_range": "8-12"},
                    {
                        "name": "Hip Abductor Machine",
                        "sets": 3,
                        "rep_range": "10-12",
                    },
                    {
                        "name": "Seated Leg Curl Machine",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Standing Calf Raise (Machine)",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
            "Rotation 2": {
                "compounds": [
                    {
                        "name": "Hack Squat Machine",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {
                        "name": "Romanian Deadlift (Barbell)",
                        "sets": 3,
                        "rep_range": "5-8",
                    },
                ],
                "accessories": [
                    {
                        "name": "Leg Extension Machine",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Hip Abductor Machine",
                        "sets": 3,
                        "rep_range": "10-12",
                    },
                    {
                        "name": "Lying Leg Curl Machine",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Seated Calf Raise (Machine)",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
        },
        "Home": {
            "Rotation 1": {
                "compounds": [
                    {"name": "Barbell Back Squat", "sets": 4, "rep_range": "3-5"},
                    {
                        "name": "Barbell Romanian Deadlift",
                        "sets": 3,
                        "rep_range": "5-8",
                    },
                ],
                "accessories": [
                    {
                        "name": "Bulgarian Split Squat",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Resistance Band Leg Curl",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Bodyweight Calf Raise",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
            "Rotation 2": {
                "compounds": [
                    {
                        "name": "Barbell Front Squat",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {
                        "name": "Resistance Band Romanian Deadlift",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
                "accessories": [
                    {
                        "name": "Resistance Band Leg Extension",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Single-Leg Calf Raise",
                        "sets": 3,
                        "rep_range": "12-15",
                    },
                ],
            },
        },
    },
    "Upper B (Chest / Back / Shoulders / Arms)": {
        "Gym": {
            "Rotation 1": {
                "compounds": [
                    {
                        "name": "Plate-Loaded Machine Chest Press",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {
                        "name": "Single-Arm Machine Row",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {
                        "name": "Dumbbell Arnold Press",
                        "sets": 3,
                        "rep_range": "5-8",
                    },
                ],
                "accessories": [
                    {
                        "name": "Machine Chest Fly (Pec Deck)",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Machine Rear Delt Fly (Reverse Pec Deck)",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Dumbbell Hammer Curl",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Overhead Dumbbell Tricep Extension",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
            "Rotation 2": {
                "compounds": [
                    {
                        "name": "Incline Dumbbell Press",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {
                        "name": "Seated Cable Row",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {
                        "name": "Machine Shoulder Press",
                        "sets": 3,
                        "rep_range": "5-8",
                    },
                ],
                "accessories": [
                    {"name": "Cable Chest Fly", "sets": 3, "rep_range": "8-12"},
                    {
                        "name": "Cable Rear Delt Fly",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {"name": "Cable Face Pull", "sets": 3, "rep_range": "8-12"},
                    {
                        "name": "Cable Rope Hammer Curl",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
        },
        "Home": {
            "Rotation 1": {
                "compounds": [
                    {
                        "name": "Resistance Band Push-Up",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {
                        "name": "Band-Assisted Pull-Up",
                        "sets": 3,
                        "rep_range": "5-8",
                    },
                    {
                        "name": "Resistance Band Shoulder Press",
                        "sets": 3,
                        "rep_range": "5-8",
                    },
                ],
                "accessories": [
                    {
                        "name": "Resistance Band Face Pull",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Resistance Band Hammer Curl",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Band Overhead Tricep Extension",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
            "Rotation 2": {
                "compounds": [
                    {"name": "Barbell Floor Press", "sets": 4, "rep_range": "3-5"},
                    {
                        "name": "Underhand Band Row",
                        "sets": 3,
                        "rep_range": "5-8",
                    },
                    {
                        "name": "Resistance Band Upright Row",
                        "sets": 3,
                        "rep_range": "5-8",
                    },
                ],
                "accessories": [
                    {
                        "name": "Resistance Band Chest Fly",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Resistance Band Bicep Curl",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
        },
    },
    "Lower B (Quads / Hamstrings / Glutes / Core)": {
        "Gym": {
            "Rotation 1": {
                "compounds": [
                    {"name": "Barbell Deadlift", "sets": 3, "rep_range": "3-5"},
                    {
                        "name": "Hack Squat Machine",
                        "sets": 3,
                        "rep_range": "5-8",
                    },
                ],
                "accessories": [
                    {
                        "name": "Hip Adductor Machine",
                        "sets": 3,
                        "rep_range": "10-12",
                    },
                    {
                        "name": "Leg Extension Machine",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Standing Calf Raise (Machine)",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Heavy Cable Crunch",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
            "Rotation 2": {
                "compounds": [
                    {"name": "Barbell Deadlift", "sets": 3, "rep_range": "3-5"},
                    {
                        "name": "Leg Press Machine",
                        "sets": 3,
                        "rep_range": "5-8",
                    },
                ],
                "accessories": [
                    {
                        "name": "Hip Adductor Machine",
                        "sets": 3,
                        "rep_range": "10-12",
                    },
                    {
                        "name": "Seated Leg Curl Machine",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Seated Calf Raise (Machine)",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Hanging Leg Raise",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
        },
        "Home": {
            "Rotation 1": {
                "compounds": [
                    {
                        "name": "Heavy Barbell Deadlift",
                        "sets": 3,
                        "rep_range": "3-5",
                    },
                    {"name": "Barbell Front Squat", "sets": 3, "rep_range": "5-8"},
                ],
                "accessories": [
                    {
                        "name": "Resistance Band Romanian Deadlift",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Bodyweight Calf Raise",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Lying Leg Raise",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
            "Rotation 2": {
                "compounds": [
                    {"name": "Barbell Front Squat", "sets": 3, "rep_range": "5-8"},
                    {
                        "name": "Resistance Band Romanian Deadlift",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
                "accessories": [
                    {
                        "name": "Resistance Band Leg Extension",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Single-Leg Calf Raise",
                        "sets": 3,
                        "rep_range": "12-15",
                    },
                    {
                        "name": "Bicycle Crunches",
                        "sets": 3,
                        "rep_range": "12-15",
                    },
                ],
            },
        },
    },
}

st.set_page_config(
    page_title="Upper/Lower Tracker", page_icon="🏋️‍♂️", layout="centered"
)

st.title("🏋️‍♂️ Upper / Lower Workout Tracker")

st.sidebar.header("Configuration")
mode = st.sidebar.radio("Environment Mode", ["Gym", "Home"])
split_choice = st.sidebar.selectbox(
    "Select Split Day", list(WORKOUT_TEMPLATES.keys())
)

logs = load_logs()

# Auto-alternating rotation logic based on past log history
last_logged_rotation = None
if logs:
  sorted_dates = sorted(logs.keys())
  for date_str in reversed(sorted_dates):
    for session_key in logs[date_str].keys():
      if split_choice in session_key:
        if "Rotation 1" in session_key:
          last_logged_rotation = "Rotation 1"
          break
        elif "Rotation 2" in session_key:
          last_logged_rotation = "Rotation 2"
          break
    if last_logged_rotation:
      break

# Auto-select the alternate workout rotation
if last_logged_rotation == "Rotation 1":
  default_rot_index = 1  # Auto-prompt Rotation 2
  st.sidebar.info("🔄 Auto-prompted: You logged Rotation 1 last time.")
elif last_logged_rotation == "Rotation 2":
  default_rot_index = 0  # Auto-prompt Rotation 1
  st.sidebar.info("🔄 Auto-prompted: You logged Rotation 2 last time.")
else:
  default_rot_index = 0  # Default to Rotation 1 for new workouts

rotation_choice = st.sidebar.radio(
    "Session Rotation (Auto-Alternates)",
    ["Rotation 1", "Rotation 2"],
    index=default_rot_index,
)

phase_choice = st.sidebar.selectbox(
    "Select Periodization Phase", list(REST_RULES.keys())
)

st.subheader(f"{split_choice} — {rotation_choice}")
rest_config = REST_RULES[phase_choice]
st.caption(f"Phase: {phase_choice} | Mode: {mode}")

workout_data = WORKOUT_TEMPLATES[split_choice][mode][rotation_choice]
compounds = workout_data["compounds"]
accessories = workout_data["accessories"]

session_inputs = {}


def render_exercise_inputs(
    exercise_list, section_title, start_idx, is_compound=False
):
  st.markdown(f"### {section_title}")
  target_rest_str = (
      rest_config["compound_rest"]
      if is_compound
      else rest_config["isolation_rest"]
  )
  timer_seconds = (
      rest_config["compound_seconds"]
      if is_compound
      else rest_config["isolation_seconds"]
  )

  for idx, lift in enumerate(exercise_list):
    e_idx = start_idx + idx
    st.markdown(
        f"#### **{lift['name']}**  \n*Target: {lift['sets']} Working Sets |"
        f" {lift['rep_range']} Reps | Target Rest: **{target_rest_str}***"
    )

    sets_data = []

    if is_compound:
      st.info("🔥 **Warm-Up Set:** Light weight (~50-60% target), 8-10 reps")
      w_col1, w_col2, w_col3 = st.columns([1, 2, 2])
      with w_col1:
        st.write("**Warm-Up**")
      with w_col2:
        wu_w = st.number_input(
            "Warmup Weight (lbs)",
            min_value=0.0,
            step=5.0,
            key=f"ex_{e_idx}_wu_w",
        )
      with w_col3:
        wu_r = st.number_input(
            "Warmup Reps",
            min_value=0,
            max_value=50,
            step=1,
            key=f"ex_{e_idx}_wu_r",
        )
      sets_data.append({"set": "Warmup", "weight": wu_w, "reps": wu_r})

    for s in range(1, lift["sets"] + 1):
      col_set, col_weight, col_reps = st.columns([1, 2, 2])
      with col_set:
        st.write(f"**Set {s}**")
      with col_weight:
        w = st.number_input(
            "Weight (lbs)",
            min_value=0.0,
            step=2.5,
            key=f"ex_{e_idx}_s{s}_w",
        )
      with col_reps:
        r = st.number_input(
            "Reps",
            min_value=0,
            max_value=100,
            step=1,
            key=f"ex_{e_idx}_s{s}_r",
        )
      sets_data.append({"set": s, "weight": w, "reps": r})

    timer_placeholder = st.empty()
    if st.button(
        f"⏱️ Start {target_rest_str} Rest Timer", key=f"timer_btn_{e_idx}"
    ):
      for remaining in range(timer_seconds, 0, -1):
        mins, secs = divmod(remaining, 60)
        timer_placeholder.warning(
            f"⏳ Rest Timer Active: **{mins:02d}:{secs:02d}** remaining..."
        )
        time.sleep(1)
      timer_placeholder.success("🔔 Rest time up! Start your next set.")

    session_inputs[lift["name"]] = sets_data
    st.markdown("---")


render_exercise_inputs(
    compounds, "1. Primary Lifts (Compounds)", 0, is_compound=True
)
render_exercise_inputs(
    accessories, "2. Isolations & Accessories", 100, is_compound=False
)

if st.button("💾 Save Session Logs", type="primary"):
  today_str = datetime.date.today().strftime("%Y-%m-%d")
  if today_str not in logs:
    logs[today_str] = {}
  logs[today_str][
      f"{split_choice} [{rotation_choice}] ({phase_choice})"
  ] = session_inputs
  save_logs(logs)
  st.success("Session logged successfully! Auto-rotation updated for next week.")

st.markdown("---")
st.subheader("📈 Exercise History")
if logs:
  all_exercise_names = []
  for cat in WORKOUT_TEMPLATES.values():
    for env in cat.values():
      for rot in env.values():
        for l in rot["compounds"] + rot["accessories"]:
          if l["name"] not in all_exercise_names:
            all_exercise_names.append(l["name"])

  selected_lift = st.selectbox(
      "Select exercise to view past records:", sorted(all_exercise_names)
  )

  history_data = []
  for date, splits in logs.items():
    for split_name, exercises in splits.items():
      if selected_lift in exercises:
        ex_entry = exercises[selected_lift]
        if isinstance(ex_entry, list):
          sets_summary = ", ".join([
              f"WU: {s['weight']}×{s['reps']}"
              if s["set"] == "Warmup"
              else f"S{s['set']}: {s['weight']}lbs×{s['reps']}"
              for s in ex_entry
          ])
        else:
          sets_summary = f"{ex_entry.get('weight', 0)}lbs × ({ex_entry.get('reps', '')})"

        history_data.append({
            "Date": date,
            "Session": split_name,
            "Per-Set Performance": sets_summary,
        })

  if history_data:
    st.table(history_data)
  else:
    st.info("No recorded history for this exercise yet.")
else:
  st.info("Log your first workout to view historical progression.")
