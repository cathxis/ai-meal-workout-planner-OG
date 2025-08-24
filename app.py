import streamlit as st
import pandas as pd
import requests
from io import StringIO
import datetime

# -------------------------
# Load Meals from GitHub CSV
# -------------------------
def load_meals_from_github():
    """Loads meal data from a GitHub CSV file in the repo."""
    github_csv_url = "https://raw.githubusercontent.com/fitmaxxAi/ai-meal-workout-planner/main/meals.csv"

    try:
        # Fetch CSV from GitHub raw link
        response = requests.get(github_csv_url)
        response.raise_for_status()
        meals_df = pd.read_csv(StringIO(response.text))

        # Group meals by goal → meal_type → meal_name
        meal_templates = {}
        for goal in meals_df['goal_type'].unique():
            goal_meals = {}
            goal_df = meals_df[meals_df['goal_type'] == goal]
            for meal_type in goal_df['meal_type'].unique():
                meal_name = goal_df[goal_df['meal_type'] == meal_type]['meal_name'].iloc[0]
                goal_meals[meal_type] = meal_name
            meal_templates[goal] = goal_meals

        return meal_templates

    except Exception as e:
        st.error(f"⚠️ Error loading meals from GitHub: {e}")
        return {}  # Empty if CSV fails


# -------------------------
# Workout Library
# -------------------------
workout_library = {
    "Strength": [
        "Push-ups (3 sets of 12)", 
        "Squats (3 sets of 15)", 
        "Lunges (3 sets of 12 per leg)", 
        "Plank (3 x 45s)",
        "Dumbbell Shoulder Press (3 sets of 12)"
    ],
    "Cardio": [
        "Jump Rope (5 minutes)", 
        "Burpees (3 sets of 10)", 
        "Mountain Climbers (3 x 30s)", 
        "Running (20 minutes)", 
        "High Knees (3 x 40s)"
    ],
    "Flexibility": [
        "Yoga Sun Salutation (5 min)", 
        "Seated Forward Bend (3 x 30s)", 
        "Cat-Cow Stretch (3 x 10)", 
        "Child’s Pose (3 x 40s)", 
        "Shoulder Stretch (3 x 30s)"
    ],
    "Endurance": [
        "Cycling (30 minutes)", 
        "Jogging (25 minutes)", 
        "Rowing (15 minutes)", 
        "Stair Climbing (10 minutes)", 
        "Swimming (20 minutes)"
    ]
}


# -------------------------
# Main Streamlit App
# -------------------------
def main():
    st.set_page_config(page_title="AI Personalized Meal & Workout Planner", layout="wide")
    st.title("🥗 AI Personalized Meal & Workout Planner")

    # Load meals
    meal_templates = load_meals_from_github()

    # Sidebar: user inputs
    st.sidebar.header("⚙️ User Settings")
    gender = st.sidebar.radio("Select Gender", ["Male", "Female", "Other"])
    goal = st.sidebar.selectbox("🎯 Select Your Goal", list(meal_templates.keys()) if meal_templates else ["Weight Loss"])
    age = st.sidebar.number_input("Enter Age", min_value=10, max_value=80, value=18)
    sleep_hours = st.sidebar.slider("🛌 Sleep Hours (last night)", 0, 12, 7)
    completed_workout = st.sidebar.checkbox("✅ Mark Today's Workout Completed")

    # -------------------------
    # Show Meal Plan
    # -------------------------
    st.subheader(f"🍴 Your Meal Plan for {goal}")
    if goal in meal_templates:
        for meal_type, meal_name in meal_templates[goal].items():
            st.write(f"**{meal_type}:** {meal_name}")
    else:
        st.warning("⚠️ No meals found in CSV for this goal.")

    # -------------------------
    # Show Workout Plan
    # -------------------------
    st.subheader("💪 Recommended Workouts")
    for category, workouts in workout_library.items():
        with st.expander(category):
            for w in workouts:
                st.write(f"- {w}")

    # -------------------------
    # Sleep Tracking
    # -------------------------
    st.subheader("🛌 Sleep Tracking")
    if sleep_hours < 6:
        st.warning("⚠️ You slept less than 6 hours. Try to rest more.")
    else:
        st.success("✅ Great! You had enough sleep.")

    # -------------------------
    # Workout Completion Progress
    # -------------------------
    if "progress" not in st.session_state:
        st.session_state.progress = []

    today = str(datetime.date.today())
    if completed_workout and today not in st.session_state.progress:
        st.session_state.progress.append(today)

    st.subheader("📊 Workout Progress")
    if st.session_state.progress:
        progress_df = pd.DataFrame(st.session_state.progress, columns=["Date"])
        progress_df["Count"] = 1
        progress_chart = progress_df.groupby("Date").sum().cumsum()
        st.line_chart(progress_chart)
    else:
        st.info("No workouts logged yet.")


# -------------------------
# Run App
# -------------------------
if __name__ == "__main__":
    main()
