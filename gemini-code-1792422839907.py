import base64
import datetime
import json
import os
import time
import requests
import streamlit as st

LOG_FILE = "workout_logs.json"

# Curated Equipment Alternatives for Machine Swaps
EXERCISE_ALTERNATIVES = {
    "Barbell Bench Press": [
        "Dumbbell Flat Bench Press",
        "Plate-Loaded Machine Chest Press",
    ],
    "Seated Machine Row": ["Chest-Supported Dumbbell Row", "T-Bar Row"],
    "Standing Overhead Barbell Press": [
        "Seated Dumbbell Overhead Press",
        "Machine Shoulder Press",
    ],
    "Incline Machine Chest Press": [
        "Incline Dumbbell Press",
        "Incline Smith Machine Press",
    ],
    "Plate-Loaded Machine Chest Press": [
        "Barbell Bench Press",
        "Dumbbell Flat Bench Press",
    ],
    "Incline Dumbbell Press": [
        "Incline Machine Chest Press",
        "Incline Smith Machine Press",
    ],
    "Heavy Lat Pulldown": ["Seated Cable Row", "Neutral Grip Pulldown"],
    "Seated DB Overhead Press": [
        "Standing Overhead Barbell Press",
        "Machine Shoulder Press",
    ],
    "Machine Shoulder Press": [
        "Standing Overhead Barbell Press",
        "Seated DB Overhead Press",
    ],
    "Dumbbell Arnold Press": [
        "Seated Dumbbell Shoulder Press",
        "Machine Shoulder Press",
    ],
    "Seated Cable Row": [
        "Single-Arm Machine Row",
        "Chest-Supported Dumbbell Row",
    ],
    "Single-Arm Machine Row": ["Seated Cable Row", "T-Bar Row"],
    "Barbell Back Squat": ["Smith Machine Squat", "Goblet Squat"],
    "Barbell Front Squat": ["Goblet Squat", "Hack Squat Machine"],
    "Romanian Deadlift (Barbell)": [
        "Dumbbell Romanian Deadlift",
        "Single-Leg DB RDL",
    ],
    "Hack Squat Machine": ["Leg Press Machine", "Pendulum Squat"],
    "Barbell Deadlift": ["Trap Bar Deadlift", "Barbell Rack Pull"],
    "Machine Chest Fly (Pec Deck)": ["Cable Chest Fly", "Dumbbell Fly"],
    "Incline Dumbbell Fly": ["Cable Low-to-High Fly", "Machine Chest Fly"],
    "Cable Chest Fly": ["Machine Chest Fly (Pec Deck)", "Dumbbell Fly"],
    "Machine Rear Delt Fly (Reverse Pec Deck)": [
        "Cable Face Pull",
        "High Cable Rear Delt Fly",
    ],
    "Cable Face Pull (Rear Delts)": [
        "Machine Rear Delt Fly",
        "Dumbbell Rear Delt Fly",
    ],
    "Cable Rear Delt Fly": ["Cable Face Pull", "Machine Rear Delt Fly"],
    "Cable Lateral Raise": [
        "Dumbbell Lateral Raise",
        "Machine Lateral Raise",
    ],
    "Dumbbell Lateral Raise": ["Cable Lateral Raise", "Machine Lateral Raise"],
    "Cable Tricep Pushdown": [
        "Rope Tricep Extension",
        "Lying Tricep Extension (Skullcrushers)",
    ],
    "Overhead Cable Tricep Extension": [
        "Overhead Dumbbell Tricep Extension",
        "EZ-Bar Skullcrushers",
    ],
    "Cable Bicep Curl": ["Dumbbell Bicep Curl", "EZ-Bar Preacher Curl"],
    "Incline Dumbbell Bicep Curl": [
        "Cable Bicep Curl",
        "Concentration Curls",
    ],
    "Dumbbell Hammer Curl": [
        "Cable Rope Hammer Curl",
        "Cross-Body Hammer Curl",
    ],
    "Cable Rope Hammer Curl": ["Dumbbell Hammer Curl", "Reverse Grip EZ-Bar Curl"],
    "Hip Abductor Machine": [
        "Standing Cable Hip Abduction",
        "Resistance Band Clamshells",
    ],
    "Hip Adductor Machine": [
        "Cable Adduction",
        "Wide Stance Sumo Squat Hold",
    ],
    "Leg Press Machine": ["Hack Squat Machine", "Goblet Squat"],
    "Leg Extension Machine": [
        "Sissy Squat",
        "Resistance Band Leg Extension",
    ],
    "Seated Leg Curl Machine": [
        "Lying Leg Curl Machine",
        "Swiss Ball Hamstring Curl",
    ],
    "Lying Leg Curl Machine": [
        "Seated Leg Curl Machine",
        "Single-Leg Standing Leg Curl",
    ],
    "Standing Calf Raise (Machine)": [
        "Seated Calf Raise (Machine)",
        "Leg Press Calf Press",
    ],
    "Seated Calf Raise (Machine)": [
        "Standing Calf Raise (Machine)",
        "Leg Press Calf Press",
    ],
    "Heavy Cable Crunch": ["Hanging Leg Raise", "Weighted Decline Crunch"],
    "Hanging Leg Raise": ["Lying Leg Raise", "Captain's Chair Knee Raise"],
}

REST_RULES = {
    "Phase 1 (Strength: 3-5 reps compounds / 8-12 reps isolation)": {
        "compound_rest": "2.0 min",
        "compound_seconds": 120,
        "isolation_rest": "1.0 min",
        "isolation_seconds": 60,
    },
    "Phase 2 (Hypertrophy: 5-8 reps compounds / 12-15 reps isolation)": {
        "compound_rest": "1.5 min",
        "compound_seconds": 90,
        "isolation_rest": "1.0 min",
        "isolation_seconds": 60,
    },
}

# 16 Total Workouts (4 Split Days x 4 Options Each) — Streamlined 30-Min Routines
WORKOUT_TEMPLATES = {
    "Upper A (Chest / Back / Shoulders / Arms)": {
        "Gym": {
            "Option 1": {
                "compounds": [
                    {"name": "Barbell Bench Press", "sets": 4, "rep_range": "3-5"},
                    {"name": "Seated Machine Row", "sets": 4, "rep_range": "3-5"},
                ],
                "accessories": [
                    {
                        "name": "Machine Chest Fly (Pec Deck)",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Cable Tricep Pushdown",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
            "Option 2": {
                "compounds": [
                    {
                        "name": "Incline Dumbbell Press",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {"name": "Heavy Lat Pulldown", "sets": 4, "rep_range": "3-5"},
                ],
                "accessories": [
                    {
                        "name": "Cable Lateral Raise",
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
            "Option 3": {
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
                ],
                "accessories": [
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
                ],
            },
            "Option 4": {
                "compounds": [
                    {
                        "name": "Incline Machine Chest Press",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {
                        "name": "Seated Cable Row",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                ],
                "accessories": [
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
            "Option 1": {
                "compounds": [
                    {"name": "Barbell Floor Press", "sets": 4, "rep_range": "3-5"},
                    {
                        "name": "Heavy Bent-Over Barbell Row",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                ],
                "accessories": [
                    {
                        "name": "Resistance Band Chest Fly",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Band Tricep Pushdown",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
            "Option 2": {
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
                ],
                "accessories": [
                    {
                        "name": "Resistance Band Lateral Raise",
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
            "Option 3": {
                "compounds": [
                    {"name": "Barbell Floor Press", "sets": 4, "rep_range": "3-5"},
                    {
                        "name": "Heavy Bent-Over Barbell Row",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                ],
                "accessories": [
                    {
                        "name": "Resistance Band Rear Delt Fly",
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
            "Option 4": {
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
                ],
                "accessories": [
                    {
                        "name": "Band Overhead Tricep Extension",
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
    "Lower A (Quads / Hamstrings / Glutes / Calves)": {
        "Gym": {
            "Option 1": {
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
                ],
            },
            "Option 2": {
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
                        "name": "Standing Calf Raise (Machine)",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
            "Option 3": {
                "compounds": [
                    {"name": "Barbell Back Squat", "sets": 4, "rep_range": "3-5"},
                    {
                        "name": "Romanian Deadlift (Barbell)",
                        "sets": 3,
                        "rep_range": "5-8",
                    },
                ],
                "accessories": [
                    {
                        "name": "Seated Leg Curl Machine",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Hip Abductor Machine",
                        "sets": 3,
                        "rep_range": "10-12",
                    },
                ],
            },
            "Option 4": {
                "compounds": [
                    {
                        "name": "Hack Squat Machine",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {"name": "Barbell Deadlift", "sets": 3, "rep_range": "3-5"},
                ],
                "accessories": [
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
            "Option 1": {
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
                        "name": "Bodyweight Calf Raise",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
            "Option 2": {
                "compounds": [
                    {
                        "name": "Barbell Front Squat",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {
                        "name": "Barbell Romanian Deadlift",
                        "sets": 3,
                        "rep_range": "5-8",
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
            "Option 3": {
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
                        "name": "Single-Leg Calf Raise",
                        "sets": 3,
                        "rep_range": "12-15",
                    },
                ],
            },
            "Option 4": {
                "compounds": [
                    {
                        "name": "Barbell Front Squat",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {
                        "name": "Barbell Romanian Deadlift",
                        "sets": 3,
                        "rep_range": "5-8",
                    },
                ],
                "accessories": [
                    {
                        "name": "Resistance Band Leg Extension",
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
        },
    },
    "Upper B (Chest / Back / Shoulders / Arms)": {
        "Gym": {
            "Option 1": {
                "compounds": [
                    {
                        "name": "Standing Overhead Barbell Press",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {
                        "name": "Seated Cable Row",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                ],
                "accessories": [
                    {"name": "Cable Chest Fly", "sets": 3, "rep_range": "8-12"},
                    {
                        "name": "Cable Rear Delt Fly",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
            "Option 2": {
                "compounds": [
                    {
                        "name": "Seated DB Overhead Press",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {"name": "Heavy Lat Pulldown", "sets": 4, "rep_range": "3-5"},
                ],
                "accessories": [
                    {
                        "name": "Dumbbell Lateral Raise",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Cable Rope Hammer Curl",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
            "Option 3": {
                "compounds": [
                    {
                        "name": "Machine Shoulder Press",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {
                        "name": "Single-Arm Machine Row",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                ],
                "accessories": [
                    {
                        "name": "Machine Chest Fly (Pec Deck)",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Overhead Cable Tricep Extension",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
            "Option 4": {
                "compounds": [
                    {
                        "name": "Dumbbell Arnold Press",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {
                        "name": "Seated Cable Row",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                ],
                "accessories": [
                    {"name": "Cable Face Pull", "sets": 3, "rep_range": "8-12"},
                    {
                        "name": "Cable Bicep Curl",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
        },
        "Home": {
            "Option 1": {
                "compounds": [
                    {
                        "name": "Standing Overhead Barbell Press",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {
                        "name": "Underhand Band Row",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                ],
                "accessories": [
                    {
                        "name": "Resistance Band Chest Fly",
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
            "Option 2": {
                "compounds": [
                    {
                        "name": "Standing Overhead Barbell Press",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {
                        "name": "Underhand Band Row",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                ],
                "accessories": [
                    {
                        "name": "Resistance Band Face Pull",
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
            "Option 3": {
                "compounds": [
                    {
                        "name": "Standing Overhead Barbell Press",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {
                        "name": "Underhand Band Row",
                        "sets": 4,
                        "rep_range": "3-5",
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
            "Option 4": {
                "compounds": [
                    {
                        "name": "Standing Overhead Barbell Press",
                        "sets": 4,
                        "rep_range": "3-5",
                    },
                    {
                        "name": "Underhand Band Row",
                        "sets": 4,
                        "rep_range": "3-5",
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
                ],
            },
        },
    },
    "Lower B (Quads / Hamstrings / Glutes / Core)": {
        "Gym": {
            "Option 1": {
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
                        "name": "Heavy Cable Crunch",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
            "Option 2": {
                "compounds": [
                    {
                        "name": "Barbell Front Squat",
                        "sets": 3,
                        "rep_range": "5-8",
                    },
                    {
                        "name": "Romanian Deadlift (Barbell)",
                        "sets": 3,
                        "rep_range": "5-8",
                    },
                ],
                "accessories": [
                    {"name": "Leg Press Machine", "sets": 3, "rep_range": "8-12"},
                    {
                        "name": "Seated Calf Raise (Machine)",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
            "Option 3": {
                "compounds": [
                    {"name": "Barbell Deadlift", "sets": 3, "rep_range": "3-5"},
                    {"name": "Leg Press Machine", "sets": 3, "rep_range": "5-8"},
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
                ],
            },
            "Option 4": {
                "compounds": [
                    {
                        "name": "Barbell Front Squat",
                        "sets": 3,
                        "rep_range": "5-8",
                    },
                    {
                        "name": "Hack Squat Machine",
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
                        "name": "Hanging Leg Raise",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
        },
        "Home": {
            "Option 1": {
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
                        "name": "Lying Leg Raise",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                ],
            },
            "Option 2": {
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
                        "name": "Bodyweight Calf Raise",
                        "sets": 3,
                        "rep_range": "8-12",
                    },
                    {
                        "name": "Bicycle Crunches",
                        "sets": 3,
                        "rep_range": "12-15",
                    },
                ],
            },
            "Option 3": {
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
                        "name": "Resistance Band Leg Extension",
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
            "Option 4": {
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

SPLIT_ORDER = list(WORKOUT_TEMPLATES.keys())


def get_github_file():
  if "GITHUB_TOKEN" in st.secrets and "GITHUB_REPO" in st.secrets:
    url = f"https://api.github.com/repos/{st.secrets['GITHUB_REPO']}/contents/{LOG_FILE}"
    headers = {"Authorization": f"token {st.secrets['GITHUB_TOKEN']}"}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
      content = res.json()["content"]
      decoded_bytes = base64.b64decode(content)
      return json.loads(decoded_bytes.decode("utf-8")), res.json()["sha"]
  return {}, None


def save_logs(logs, sha=None):
  with open(LOG_FILE, "w") as f:
    json.dump(logs, f, indent=4)

  if "GITHUB_TOKEN" in st.secrets and "GITHUB_REPO" in st.secrets:
    url = f"https://api.github.com/repos/{st.secrets['GITHUB_REPO']}/contents/{LOG_FILE}"
    headers = {"Authorization": f"token {st.secrets['GITHUB_TOKEN']}"}
    encoded_content = base64.b64encode(
        json.dumps(logs, indent=4).encode("utf-8")
    ).decode("utf-8")
    payload = {
        "message": f"Auto-update workout logs {datetime.date.today()}",
        "content": encoded_content,
    }
    if sha:
      payload["sha"] = sha
    res = requests.put(url, json=payload, headers=headers)
    if res.status_code in [200, 201]:
      st.sidebar.success("☁️ Synced to GitHub!")


logs, current_sha = get_github_file()
if not logs and os.path.exists(LOG_FILE):
  with open(LOG_FILE, "r") as f:
    logs = json.load(f)

st.set_page_config(
    page_title="Fast 30-Min Workout App", page_icon="⚡", layout="centered"
)

st.title("⚡ 30-Min Workout Tracker")

st.sidebar.header("Configuration")
mode = st.sidebar.radio("Environment Mode", ["Gym", "Home"])

# Automatic Sequence Prompting for Split Day (Upper A -> Lower A -> Upper B -> Lower B)
default_split_idx = 3  # Pre-default to Lower B if no history found
last_logged_split = None
if logs:
  sorted_dates = sorted(logs.keys())
  for date_str in reversed(sorted_dates):
    for session_key in logs[date_str].keys():
      for s_key in SPLIT_ORDER:
        if s_key in session_key:
          last_logged_split = s_key
          break
      if last_logged_split:
        break
    if last_logged_split:
      break

if last_logged_split in SPLIT_ORDER:
  last_idx = SPLIT_ORDER.index(last_logged_split)
  default_split_idx = (last_idx + 1) % len(SPLIT_ORDER)
  st.sidebar.info(
      f"🔄 Sequence Auto-Prompt: Logged {last_logged_split.split(' ')[0]} last"
      " time."
  )
else:
  st.sidebar.info("🔄 Pre-defaulted to Lower B per routine sequence.")

split_choice = st.sidebar.selectbox(
    "Select Split Day", SPLIT_ORDER, index=default_split_idx
)

# Automatic Sequence Prompting for Workout Option (Option 1 -> 2 -> 3 -> 4)
available_options = list(WORKOUT_TEMPLATES[split_choice][mode].keys())
last_logged_option = None
if logs:
  sorted_dates = sorted(logs.keys())
  for date_str in reversed(sorted_dates):
    for session_key in logs[date_str].keys():
      if split_choice in session_key:
        for opt in available_options:
          if f"[{opt}]" in session_key:
            last_logged_option = opt
            break
      if last_logged_option:
        break
    if last_logged_option:
      break

if last_logged_option in available_options:
  curr_opt_idx = available_options.index(last_logged_option)
  next_opt_idx = (curr_opt_idx + 1) % len(available_options)
else:
  next_opt_idx = 0

option_choice = st.sidebar.radio(
    "Workout Option (Auto-Alternates)", available_options, index=next_opt_idx
)
phase_choice = st.sidebar.selectbox(
    "Select Periodization Phase", list(REST_RULES.keys())
)

st.subheader(f"{split_choice} — {option_choice}")
rest_config = REST_RULES[phase_choice]

workout_data = WORKOUT_TEMPLATES[split_choice][mode][option_choice]
compounds = workout_data["compounds"]
accessories = workout_data["accessories"]

# Overview Card
st.markdown("---")
st.markdown("### 📋 Today's 30-Min Routine Overview")
overview_cols = st.columns(len
