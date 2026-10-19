import datetime
import json
import os
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


WORKOUT_TEMPLATES = {
    "Chest & Triceps": {
        "Gym": {
            "Phase 1 (Strength: 3-5 reps compounds / 8-12 reps isolation)": {
                "compounds": [
                    {"name": "Barbell Bench Press", "sets": 4, "rep_range": "3-5"},
                    {"name": "Incline Dumbbell Press", "sets": 3, "rep_range": "5-8"},
                ],
                "accessories": [
                    {"name": "Machine Chest Fly", "sets": 3, "rep_range": "8-12"},
                    {"name": "Cable Tricep Pushdown", "sets": 3, "rep_range": "8-12"},
                    {"name": "Overhead Dumbbell Tricep Extension", "sets": 3, "rep_range": "8-12"},
                ],
            },
            "Phase 2 (Hypertrophy: 5-8 reps compounds / 12-15 reps isolation)": {
                "compounds": [
                    {"name": "Barbell Bench Press", "sets": 3, "rep_range": "5-8"},
                    {"name": "Incline Dumbbell Press", "sets": 3, "rep_range": "8-10"},
                ],
                "accessories": [
                    {"name": "Machine Chest Fly", "sets": 3, "rep_range": "12-15"},
                    {"name": "Cable Tricep Pushdown", "sets": 3, "rep_range": "12-15"},
                    {"name": "Overhead Cable Tricep Extension", "sets": 3, "rep_range": "12-15"},
                ],
            },
        },
        "Home": {
            "Phase 1 (Strength: 3-5 reps compounds / 8-12 reps isolation)": {
                "compounds": [
                    {"name": "Barbell Floor Press", "sets": 4, "rep_range": "3-5"},
                    {"name": "Resistance Band Push-Up", "sets": 3, "rep_range": "5-8"},
                ],
                "accessories": [
                    {"name": "Resistance Band Chest Fly", "sets": 3, "rep_range": "8-12"},
                    {"name": "Band Tricep Pushdown", "sets": 3, "rep_range": "8-12"},
                    {"name": "Band Overhead Tricep Extension", "sets": 3, "rep_range": "8-12"},
                ],
            },
            "Phase 2 (Hypertrophy: 5-8 reps compounds / 12-15 reps isolation)": {
                "compounds": [
                    {"name": "Barbell Floor Press", "sets": 3, "rep_range": "5-8"},
                    {"name": "Resistance Band Push-Up", "sets": 3, "rep_range": "8-10"},
                ],
                "accessories": [
                    {"name": "Resistance Band Chest Fly", "sets": 3, "rep_range": "12-15"},
                    {"name": "Band Tricep Pushdown", "sets": 3, "rep_range": "12-15"},
                    {"name": "Band Overhead Tricep Extension", "sets": 3, "rep_range": "12-15"},
                ],
            },
        },
    },
    "Back & Biceps": {
        "Gym": {
            "Phase 1 (Strength: 3-5 reps compounds / 8-12 reps isolation)": {
                "compounds": [
                    {"name": "Barbell Deadlift", "sets": 3, "rep_range": "3-5"},
                    {"name": "Weighted Pull-Up", "sets": 3, "rep_range": "5-8"},
                ],
                "accessories": [
                    {"name": "Seated Cable Row", "sets": 3, "rep_range": "8-12"},
                    {"name": "Barbell Bicep Curl", "sets": 3, "rep_range": "8-12"},
                    {"name": "Dumbbell Hammer Curl", "sets": 3, "rep_range": "8-12"},
                ],
            },
            "Phase 2 (Hypertrophy: 5-8 reps compounds / 12-15 reps isolation)": {
                "compounds": [
                    {"name": "Pendlay Barbell Row", "sets": 3, "rep_range": "5-8"},
                    {"name": "V-Grip Lat Pulldown", "sets": 3, "rep_range": "8-10"},
                ],
                "accessories": [
                    {"name": "Single-Arm Cable Row", "sets": 3, "rep_range": "10-12"},
                    {"name": "Incline Dumbbell Bicep Curl", "sets": 3, "rep_range": "12-15"},
                    {"name": "Cable Rope Hammer Curl", "sets": 3, "rep_range": "12-15"},
                ],
            },
        },
        "Home": {
            "Phase 1 (Strength: 3-5 reps compounds / 8-12 reps isolation)": {
                "compounds": [
                    {"name": "Heavy Bent-Over Barbell Row", "sets": 4, "rep_range": "3-5"},
                    {"name": "Band-Assisted Pull-Up", "sets": 3, "rep_range": "5-8"},
                ],
                "accessories": [
                    {"name": "Underhand Band Row", "sets": 3, "rep_range": "8-12"},
                    {"name": "Resistance Band Bicep Curl", "sets": 3, "rep_range": "8-12"},
                    {"name": "Resistance Band Hammer Curl", "sets": 3, "rep_range": "8-12"},
                ],
            },
            "Phase 2 (Hypertrophy: 5-8 reps compounds / 12-15 reps isolation)": {
                "compounds": [
                    {"name": "Bent-Over Barbell Row", "sets": 3, "rep_range": "5-8"},
                    {"name": "Underhand Band Row", "sets": 3, "rep_range": "8-12"},
                ],
                "accessories": [
                    {"name": "Resistance Band Pullover", "sets": 3, "rep_range": "12-15"},
                    {"name": "Resistance Band Bicep Curl", "sets": 3, "rep_range": "12-15"},
                    {"name": "Resistance Band Hammer Curl", "sets": 3, "rep_range": "12-15"},
                ],
            },
        },
    },
    "Legs (Quads, Hamstrings, Glutes)": {
        "Gym": {
            "Phase 1 (Strength: 3-5 reps compounds / 8-12 reps isolation)": {
                "compounds": [
                    {"name": "Barbell Back Squat", "sets": 4, "rep_range": "3-5"},
                    {"name": "Romanian Deadlift (Barbell)", "sets": 3, "rep_range": "5-8"},
                ],
                "accessories": [
                    {"name": "Leg Press", "sets": 3, "rep_range": "8-12"},
                    {"name": "Seated Leg Curl Machine", "sets": 3, "rep_range": "8-12"},
                    {"name": "Standing Calf Raise (Machine)", "sets": 3, "rep_range": "8-12"},
                ],
            },
            "Phase 2 (Hypertrophy: 5-8 reps compounds / 12-15 reps isolation)": {
                "compounds": [
                    {"name": "Barbell Back Squat", "sets": 3, "rep_range": "5-8"},
                    {"name": "Romanian Deadlift (Barbell)", "sets": 3, "rep_range": "8-10"},
                ],
                "accessories": [
                    {"name": "Leg Extension Machine", "sets": 3, "rep_range": "12-15"},
                    {"name": "Lying Leg Curl Machine", "sets": 3, "rep_range": "12-15"},
                    {"name": "Seated Calf Raise (Machine)", "sets": 3, "rep_range": "12-15"},
                ],
            },
        },
        "Home": {
            "Phase 1 (Strength: 3-5 reps compounds / 8-12 reps isolation)": {
                "compounds": [
                    {"name": "Barbell Back Squat", "sets": 4, "rep_range": "3-5"},
                    {"name": "Barbell Romanian Deadlift", "sets": 3, "rep_range": "5-8"},
                ],
                "accessories": [
                    {"name": "Bulgarian Split Squat", "sets": 3, "rep_range": "8-12"},
                    {"name": "Resistance Band Leg Curl", "sets": 3, "rep_range": "8-12"},
                    {"name": "Bodyweight Calf Raise", "sets": 3, "rep_range": "8-12"},
                ],
            },
            "Phase 2 (Hypertrophy: 5-8 reps compounds / 12-15 reps isolation)": {
                "compounds": [
                    {"name": "Barbell Front Squat", "sets": 3, "rep_range": "5-8"},
                    {"name": "Resistance Band Romanian Deadlift", "sets": 3, "rep_range": "10-12"},
                ],
                "accessories": [
                    {"name": "Resistance Band Leg Extension", "sets": 3, "rep_range": "12-15"},
                    {"name": "Resistance Band Leg Curl", "sets": 3, "rep_range": "12-15"},
                    {"name": "Single-Leg Calf Raise", "sets": 3, "rep_range": "15-20"},
                ],
            },
        },
    },
    "Shoulders & Core": {
        "Gym": {
            "Phase 1 (Strength: 3-5 reps compounds / 8-12 reps isolation)": {
                "compounds": [
                    {"name": "Seated Overhead Barbell Press", "sets": 4, "rep_range": "3-5"},
                    {"name": "Dumbbell Arnold Press", "sets": 3, "rep_range": "5-8"},
                ],
                "accessories": [
                    {"name": "Cable Lateral Raise", "sets": 3, "rep_range": "8-12"},
                    {"name": "Cable Face Pull", "sets": 3, "rep_range": "8-12"},
                    {"name": "Heavy Cable Crunch", "sets": 3, "rep_range": "8-12"},
                ],
            },
            "Phase 2 (Hypertrophy: 5-8 reps compounds / 12-15 reps isolation)": {
                "compounds": [
                    {"name": "Seated Overhead Dumbbell Press", "sets": 3, "rep_range": "5-8"},
                    {"name": "Machine Shoulder Press", "sets": 3, "rep_range": "8-10"},
                ],
                "accessories": [
                    {"name": "Dumbbell Lateral Raise", "sets": 3, "rep_range": "12-15"},
                    {"name": "Machine Reverse Pec Deck", "sets": 3, "rep_range": "12-15"},
                    {"name": "Hanging Leg Raise", "sets": 3, "rep_range": "12-15"},
                ],
            },
        },
        "Home": {
            "Phase 1 (Strength: 3-5 reps compounds / 8-12 reps isolation)": {
                "compounds": [
                    {"name": "Standing Overhead Barbell Press", "sets": 4, "rep_range": "3-5"},
                    {"name": "Resistance Band Shoulder Press", "sets": 3, "rep_range": "5-8"},
                ],
                "accessories": [
                    {"name": "Resistance Band Lateral Raise", "sets": 3, "rep_range": "8-12"},
                    {"name": "Resistance Band Face Pull", "sets": 3, "rep_range": "8-12"},
                    {"name": "Lying Leg Raise", "sets": 3, "rep_range": "8-12"},
                ],
            },
            "Phase 2 (Hypertrophy: 5-8 reps compounds / 12-15 reps isolation)": {
                "compounds": [
                    {"name": "Standing Overhead Barbell Press", "sets": 3, "rep_range": "5-8"},
                    {"name": "Resistance Band Upright Row", "sets": 3, "rep_range": "8-10"},
                ],
                "accessories": [
                    {"name": "Resistance Band Lateral Raise", "sets": 3, "rep_range": "12-15"},
                    {"name": "Resistance Band Face Pull", "sets": 3, "rep_range": "12-15"},
                    {"name": "Bicycle Crunches", "sets": 3, "rep_range": "15-20"},
                ],
            },
        },
    },
}

st.set_page_config(
    page_title="Hypertrophy Tracker", page_icon="🏋️‍♂️", layout="centered"
)

st.title("🏋️‍♂️ ExerciseDB-Integrated Workout Tracker")

st.sidebar.header("Configuration")
mode = st.sidebar.radio("Environment Mode", ["Gym", "Home"])
split_choice = st.sidebar.selectbox(
    "Select Split Day", list(WORKOUT_TEMPLATES.keys())
)

phase_choice = st.sidebar.selectbox(
    "Select Periodization Phase (Cycling)",
    list(WORKOUT_TEMPLATES[split_choice][mode].keys()),
)

logs = load_logs()

st.subheader(f"{split_choice} — {phase_choice}")
workout_data = WORKOUT_TEMPLATES[split_choice][mode][phase_choice]

compounds = workout_data["compounds"]
accessories = workout_data["accessories"]

st.markdown("### 1. Primary Lifts (Heavy)")
session_inputs = {}

for idx, lift in enumerate(compounds):
  st.markdown(
      f"**{lift['name']}** | Target Sets: {lift['sets']} | Rep Range:"
      f" **{lift['rep_range']}**"
  )
  col1, col2 = st.columns(2)
  with col1:
    weight = st.number_input(
        f"Weight (lbs) - {lift['name']}",
        min_value=0.0,
        step=5.0,
        key=f"c_w_{idx}",
    )
  with col2:
    reps = st.text_input(
        f"Reps completed - {lift['name']}", key=f"c_r_{idx}"
    )
  session_inputs[lift["name"]] = {"weight": weight, "reps": reps}

st.markdown("### 2. Isolation & Accessory Movements")

for idx, lift in enumerate(accessories):
  st.markdown(
      f"**{lift['name']}** | Target Sets: {lift['sets']} | Rep Range:"
      f" **{lift['rep_range']}**"
  )
  col1, col2 = st.columns(2)
  with col1:
    weight = st.number_input(
        f"Weight/Band Level - {lift['name']}",
        min_value=0.0,
        step=2.5,
        key=f"a_w_{idx}",
    )
  with col2:
    reps = st.text_input(
        f"Reps completed - {lift['name']}", key=f"a_r_{idx}"
    )
  session_inputs[lift["name"]] = {"weight": weight, "reps": reps}

if st.button("💾 Save Session", type="primary"):
  today_str = datetime.date.today().strftime("%Y-%m-%d")
  if today_str not in logs:
    logs[today_str] = {}
  logs[today_str][f"{split_choice} ({phase_choice})"] = session_inputs
  save_logs(logs)
  st.success("Session logged successfully!")

st.markdown("---")
st.subheader("📈 Exercise History")
if logs:
  all_exercise_names = []
  for cat in WORKOUT_TEMPLATES.values():
    for env in cat.values():
      for ph in env.values():
        for l in ph["compounds"] + ph["accessories"]:
          if l["name"] not in all_exercise_names:
            all_exercise_names.append(l["name"])

  selected_lift = st.selectbox(
      "Select exercise to view past records:", all_exercise_names
  )

  history_data = []
  for date, splits in logs.items():
    for split_name, exercises in splits.items():
      if selected_lift in exercises:
        history_data.append({
            "Date": date,
            "Session": split_name,
            "Weight": exercises[selected_lift]["weight"],
            "Reps": exercises[selected_lift]["reps"],
        })

  if history_data:
    st.table(history_data)
  else:
    st.info("No recorded history for this exercise yet.")
else:
  st.info("Log your first workout to view historical progression.")