#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################

import streamlit as sl
from internals import create_component
from data_fetcher import get_friends_steps_list, get_friends_distance_list, get_friends_calories_list, get_all_users, add_friend, insert_user_post, get_user_workouts, get_user_posts, users, get_genai_advice, get_user_friends, get_user_info, get_user_password,get_user_ID_from_username,create_new_user, username_exists,insert_workout, get_global_calories_list, get_friends_calories_list, insert_sensor_data
from PIL import Image
import pandas as pd
from google.cloud import bigquery
from datetime import datetime, date
import bcrypt

# This one has been written for you as an example. You may change it as wanted.
def display_my_custom_component(value):
    """Displays a 'my custom component' which showcases an example of how custom
    components work.

    value: the name you'd like to be called by within the app
    """
    # Define any templated data from your HTML file. The contents of
    # 'value' will be inserted to the templated HTML file wherever '{{NAME}}'
    # occurs. You can add as many variables as you want.
    data = {
        'NAME': value,
    }
    # Register and display the component by providing the data and name
    # of the HTML file. HTML must be placed inside the "custom_components" folder.
    html_file_name = "my_custom_component"
    create_component(data, html_file_name)

#used gemini for assistance: 
def display_post(user_id, query_db=bigquery, streamlit_module=sl):
    """
    Displays list of user's friends' posts: includes, pfp, name, username, timestamp, and post.
    """
    friends = get_user_friends(user_id, query_db=query_db)

    streamlit_module.header("Friends' Posts")

    for friend_id in friends:
        friend_info = get_user_info(friend_id, query_db=query_db)
        if friend_info:
            posts = get_user_posts(friend_id, query_db=query_db)

            streamlit_module.image(friend_info['profile_image'], width=100)
            streamlit_module.subheader(f"{friend_info['full_name']} (@{friend_info['username']})")
            for post in posts:
                streamlit_module.write(f"**{post['content']}**")
                streamlit_module.write(f"Posted on: {post['timestamp']}")
                if post['image']:
                    streamlit_module.image(post['image'], width=200)
                streamlit_module.markdown("---")
        else:
            streamlit_module.warning(f"Friend ID '{friend_id}' not found.")

# display_activity_summary(fetcher=lambda: get_user_workouts(user_id)
def display_activity_summary(workouts_list=None, fetcher=None): # fetcher = dependency injection, this set up allows to pass hardcoded data still
    import streamlit as sl
    import pandas as pd
    
    """
    Description: 
        Displays an activity summary for the user's workouts.
        This function presents an overview of the user's fitness activity by:
            - Allowing the user to select a workout type (currently limited to "Running").
            - Displaying total distance, total steps, and total calories burned.
            - Showing a detailed table of past workouts, including timestamps, distance, steps, and calories burned.
            - Visualizing weekly calorie progress with a progress bar.
    Input:
        workouts_list (list of dict): A list of workout dictionaries, where each workout contains:
            - 'workout_id' (str): A unique identifier for the workout.
            - 'start_timestamp' (str): The start time of the workout.
            - 'end_timestamp' (str): The end time of the workout.
            - 'start_lat_lng' (tuple): Starting latitude and longitude.
            - 'end_lat_lng' (tuple): Ending latitude and longitude.
            - 'distance' (float): Distance covered in miles.
            - 'steps' (int): Number of steps taken.
            - 'calories_burned' (int): Calories burned during the workout.
    Output:
        None
    """

    if fetcher is not None:
        workouts_list = fetcher()

    
    # workout_options = ["Running", "Full Body", "Chest", "Cardio", "Back"] # Using list when workout types are available

    workout_options = ["Running"]

    
    if "selected_workout" not in sl.session_state:
        sl.session_state.selected_workout = workout_options[0]
    
    workout_type = sl.selectbox("Workout (Beta - Only Running has data):", workout_options, key="workout_selector")
    
    # Refresh workouts only when selection changes
    if workout_type != sl.session_state.selected_workout:
        sl.session_state.selected_workout = workout_type
    
    workouts = workouts_list

    # Summary metrics
  
    total_distance = 0
    total_steps = 0
    total_calories = 0

    for workout in workouts:
        total_distance += workout['distance']
        total_steps += workout['steps']
        total_calories += workout['calories_burned']
    
    sl.session_state.total_distance = total_distance
    sl.session_state.total_steps = total_steps
    sl.session_state.total_calories = total_calories

    
    # Displaying summary statistics
    col1, col2, col3 = sl.columns(3)
    col1.metric("Total Distance", f"{total_distance} mi")
    col2.metric("Total Steps", f"{total_steps}")
    col3.metric("Total Calories", f"{total_calories} cals")
    
    # Workout Details Table
    sl.subheader("Workout Details")
    df = pd.DataFrame(workouts)

    df_display = df.copy()

    df_display = df_display.drop(columns=["start_lat_lng", "end_lat_lng"], errors="ignore")

    # Line written by ChatGPT
    df_display = df_display[["distance", "steps", "calories_burned"]].rename(columns={
    "distance": "Distance (mi)",
    "steps": "Steps Taken",
    "calories_burned": "Calories Burned"
    })

    df_display.index = df_display.index + 1

    sl.dataframe(df_display)
    # Line written by ChatGPT
    
    # Weekly Calorie Progress
    sl.subheader("Weekly Calorie Progress")
    week_goal = 2000  # Default weekly goal
    sl.session_state.weekly_calorie_goal = week_goal
    progress_bar_amount = min(((total_calories / week_goal) * 100), 100)
    # Line written by ChatGPT
    sl.session_state.weekly_calorie_progress_amount = progress_bar_amount
    sl.progress(progress_bar_amount / 100)
    sl.write(f"**Weekly Goal: {week_goal} cal | Current: {total_calories} cal**")


def display_recent_workouts(userId, workouts_func=get_user_workouts, streamlit_module=sl):
    """
    Description:
        Displays information about the recent workouts by the user by showing relevant information about each workout
    Input: 
        userId (string):  the ID of the user whose workouts are being displayed, used as an argument to get_user_workouts
        workouts_func (function): the function to be called to get the user's workout data
        streamlit_module (module): the module to be used to create the website
    Output:
        Returns nothing
        Outputs relevant information to website
    """
    #Made with slight debugging help from Gemini: https://g.co/gemini/share/d246196d413a
    # streamlit_module.title('💪Recent Workouts💪')
    workouts_list = workouts_func(userId)
    if len(workouts_list) == 0:
        streamlit_module.subheader("No Workout Data To Display")
        return
    for workout in workouts_list:
        streamlit_module.subheader(workout['workout_id'])
        date = workout['start_timestamp']
        date = date[:date.index(' ')]
        streamlit_module.write(f"📅Date: {date}")
        workout_time = workout['start_timestamp']
        start_time = workout_time[workout_time.index(' ')+1:]
        workout_time = workout['end_timestamp']
        end_time = workout_time[workout_time.index(' ')+1:]
        streamlit_module.write(f"⏱️Time: {start_time} &mdash; {end_time}")
        streamlit_module.write(f"↔️Distance: {workout['distance']} miles")
        streamlit_module.write(f"🚶Steps: {workout['steps']}")
        streamlit_module.write(f"🔥Calories Burned: {workout['calories_burned']} calories")
        streamlit_module.write("---")
    streamlit_module.subheader("Keep up the good work(outs)!")

def display_genai_advice(
    userId,
    advice_func=get_genai_advice,
    streamlit_module=sl
):
    """
    Displays AI-generated fitness advice with a related image.
    
    Args:
        timestamp: When the advice was generated
        content: The advice text content
        image: Path to the generated image
        title: Main title of the section
        subheader: Subheader text
        display_fn: Dependency-injected Streamlit display function
        
    Returns:
        None (renders UI components)
    """
    advice = advice_func(userId)
    timestamp = advice['timestamp']
    content = advice['content']
    image = advice['image']
    title = "AI Fitness Coach🦾"
    subheader = "Personalized advice based on your activities"
    streamlit_module.title(title)
    streamlit_module.subheader(subheader)
    streamlit_module.markdown(content)
    
    if image:  # Only show image if available
        streamlit_module.image(image)
    
    streamlit_module.caption(f"Last updated: {timestamp}")

import bcrypt  # 🔐 Add this at the top of your file

def login_box():
    def check_password(plain_password, hashed_password):
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

    sl.subheader("🔐 Login")

    username = sl.text_input("Username")
    password = sl.text_input("Password", type="password")

    login_button = sl.button("Log In")

    if login_button:
        if not username or not password:
            sl.warning("Please enter both username and password.")
            return None

        userID = get_user_ID_from_username(username)
        user_info = get_user_info(userID)
        expected_password = get_user_password(username)

        if user_info is None:
            sl.error("User not found.")
            return False

        if not check_password(password, expected_password):
            sl.error("Incorrect password.")
            return False

        sl.success(f"Welcome back, {user_info['full_name']}!")
        sl.session_state.userId = userID
        sl.rerun()
        return True

    return None


def signup_box():
    sl.subheader("📝 Sign Up")

    if "signup_submitted" not in sl.session_state:
        sl.session_state.signup_submitted = False

    if sl.session_state.signup_submitted:
        sl.success("✅ Account created successfully!")
        if sl.button("Go to Login"):
            sl.session_state.auth_mode = 'login'
            sl.session_state.signup_submitted = False
            sl.rerun()
        return

    first_name = sl.text_input("First Name")
    last_name = sl.text_input("Last Name")
    dob = sl.date_input(
        "Date of Birth",
        value=date(2000, 1, 1),
        min_value=date(1900, 1, 1),
        max_value=datetime.today().date()
    )
    username = sl.text_input("Username")
    image_url = sl.text_input("Profile Image URL (optional)")
    password = sl.text_input("Password", type="password")
    confirm_password = sl.text_input("Confirm Password", type="password")

    signup_button = sl.button("Create Account")

    if signup_button:
        if not all([first_name, last_name, dob, username, password, confirm_password]):
            sl.warning("Please fill in all required fields.")
            return None

        if password != confirm_password:
            sl.error("Passwords do not match.")
            return None

        if username_exists(username):
            sl.error("Username already taken.")
            return None


        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

        full_name = f"{first_name} {last_name}"

        create_new_user(
            username=username,
            name=full_name,
            image_url=image_url,
            date_of_birth=str(dob),
            password=hashed_password  
        )

        sl.success("Account created! You can now log in.")
        sl.session_state.signup_submitted = True
        sl.rerun()

    return None

def manual_workout_box():

    SENSOR_TYPES = {
    "sensor1": {"name": "Heart Rate", "units": "bpm"},
    "sensor2": {"name": "Step Count", "units": "steps"},
    "sensor3": {"name": "Temperature", "units": "Celsius"}
    }

    sl.subheader("🏃 Add Workout Manually")

    if "workout_submitted" not in sl.session_state:
        sl.session_state.workout_submitted = False

    if sl.session_state.workout_submitted:
        sl.success("Workout added successfully!")
        if sl.button("Add Another Workout"):
            sl.session_state.workout_submitted = False
            sl.rerun()
        return

    start_time = sl.time_input("Start Time")
    end_time = sl.time_input("End Time")
    date = sl.date_input("Date")

    distance = sl.number_input("Total Distance (miles)", min_value=0.0, format="%.2f")
    steps = sl.number_input("Total Steps", min_value=0)
    calories = sl.number_input("Calories Burned", min_value=0.0, format="%.2f")

    add_sensor_data = sl.checkbox("➕ Add Sensor Data (optional)")

    sensor_entries = []
    sensor_ids = list(SENSOR_TYPES.keys())

    if add_sensor_data:
        num_rows = sl.number_input("How many sensor readings?", min_value=1, max_value=10, value=1)

        for i in range(num_rows):
            sl.markdown(f"**Sensor Entry {i + 1}**")

            selected_sensor_id = sl.selectbox(f"Sensor Type", sensor_ids, key=f"sensor_id_{i}")
            selected_sensor = SENSOR_TYPES[selected_sensor_id]

            sl.caption(f"{selected_sensor['name']} ({selected_sensor['units']})")

            sensor_time = sl.time_input("Timestamp", key=f"sensor_time_{i}")
            sensor_value = sl.number_input(
                f"Sensor Value ({selected_sensor['units']})",
                key=f"sensor_value_{i}",
                format="%.2f"
            )

        sensor_entries.append({
            "sensor_id": selected_sensor_id,
            "timestamp": sensor_time,
            "value": sensor_value
        })


    if sl.button("Add Workout"):
        if start_time >= end_time:
            sl.error("End time must be after start time.")
            return

        if 'userId' not in sl.session_state:
            sl.error("You're not logged in.")
            return

        start_timestamp = datetime.combine(date, start_time)
        end_timestamp = datetime.combine(date, end_time)

        workout_id = insert_workout(
            user_id=sl.session_state.userId,
            start=start_timestamp,
            end=end_timestamp,
            distance=distance,
            steps=steps,
            calories=calories
        )

        if add_sensor_data:
            for sensor in sensor_entries:
                full_timestamp = datetime.combine(date, sensor["timestamp"])
                insert_sensor_data(
                    workout_id=workout_id,
                    sensor_id=sensor["sensor_id"],
                    timestamp=full_timestamp,
                    value=sensor["value"]
                )

        sl.success("✅ Workout added!")

        get_user_workouts.clear()

        sl.session_state.workout_submitted = True
        sl.rerun()

def display_global_leaderboard(
    metric="calories",
    streamlit_module=sl,
    get_leaderboard_func=None,
    highlight_user_id=None
):
    metric_title = {
        "calories": "🔥 Calories Burned",
        "distance": "↔️ Distance Covered",
        "steps": "🚶 Steps Taken"
    }

    leaderboard_data = get_leaderboard_func() if get_leaderboard_func else []

    if leaderboard_data:
        streamlit_module.subheader(f"{metric_title[metric]} Leaderboard 🌍")

        top_3 = leaderboard_data[:3]
        remaining = leaderboard_data[3:5]

        cols = streamlit_module.columns(3)
        for i, (name, value, user_id) in enumerate(top_3):
            with cols[i]:
                rank_emoji = ["🥇", "🥈", "🥉"][i]
                highlight = user_id == highlight_user_id
                label = f"<b style='color:#0077ff;'>{name}</b>" if highlight else f"<b>{name}</b>"
                streamlit_module.markdown(f"<div style='text-align:center;'>{rank_emoji} {label}</div>", unsafe_allow_html=True)
                streamlit_module.markdown(f"<div style='text-align:center;'>{value} {metric}</div>", unsafe_allow_html=True)
                streamlit_module.markdown(
                    "<div style='text-align:center; background-color:#D3D3D3; height: 10px;'></div>", unsafe_allow_html=True
                )

        if remaining:
            streamlit_module.markdown("---")
            streamlit_module.subheader("Top Performers (4th & 5th)")
            for i, (name, value, user_id) in enumerate(remaining):
                prefix = "🎯 " if user_id == highlight_user_id else ""
                streamlit_module.write(f"**{i + 4}. {prefix}{name}:** {value} {metric}")

        streamlit_module.markdown("---")
        streamlit_module.subheader("All Participants (Top 10)")
        for name, value, user_id in leaderboard_data[:10]:
            prefix = "⭐ " if user_id == highlight_user_id else ""
            label = f"<b style='color:#0077ff;'>{prefix}{name}</b>" if user_id == highlight_user_id else f"{name}"
            streamlit_module.markdown(f"**{label}:** {value} {metric}", unsafe_allow_html=True)
    else:
        streamlit_module.info(f"No {metric} data available to display the leaderboard.")



def display_friends_leaderboard(
    user_id,
    metric="calories",
    streamlit_module=sl,
    get_friends_funcs={
        "calories": get_friends_calories_list,
        "distance": get_friends_distance_list,
        "steps": get_friends_steps_list
    }
):
    metric_title = {
        "calories": "🔥 Calories Burned",
        "distance": "↔️ Distance Covered (mi)",
        "steps": "🚶 Steps Taken"
    }

    leaderboard_data = get_friends_funcs[metric](user_id)

    if leaderboard_data:
        streamlit_module.subheader(f"👯 Friends' {metric_title[metric]} Leaderboard")

        top_3 = leaderboard_data[:3]
        remaining = leaderboard_data[3:5]
        cols = streamlit_module.columns(3)

        for i, (name, value, friend_user_id) in enumerate(top_3):
            with cols[i]:
                rank_emoji = ["🥇", "🥈", "🥉"][i]
                is_user = friend_user_id == user_id
                label = f"<b style='color:#0077ff;'>{name}</b>" if is_user else f"<b>{name}</b>"
                streamlit_module.markdown(f"<div style='text-align:center;'>{rank_emoji} {label}</div>", unsafe_allow_html=True)
                streamlit_module.markdown(f"<div style='text-align:center;'>{value} {metric}</div>", unsafe_allow_html=True)
                streamlit_module.markdown(
                    "<div style='text-align:center; background-color:#ADD8E6; height: 10px;'></div>", unsafe_allow_html=True
                )

        if remaining:
            streamlit_module.markdown("---")
            streamlit_module.subheader("Top Friends (4th & 5th)")
            for i, (name, value, friend_user_id) in enumerate(remaining):
                prefix = "🎯 " if friend_user_id == user_id else ""
                streamlit_module.write(f"**{i + 4}. {prefix}{name}:** {value} {metric}")

        streamlit_module.markdown("---")
        streamlit_module.subheader("Friends' Performance (Top 10)")
        for name, value, friend_user_id in leaderboard_data[:10]:
            prefix = "⭐ " if friend_user_id == user_id else ""
            label = f"<b style='color:#0077ff;'>{prefix}{name}</b>" if friend_user_id == user_id else f"{name}"
            streamlit_module.markdown(f"**{label}:** {value} {metric}", unsafe_allow_html=True)
    else:
        streamlit_module.info(f"No {metric} data available to display the leaderboard.")


def post_creation_box(user_id):

    if "reset_post_form" in sl.session_state and sl.session_state.reset_post_form:
        sl.session_state.post_text = ""
        sl.session_state.post_image_url = ""
        sl.session_state.reset_post_form = False

    sl.subheader("🗨️ Create a Post")

    post_text = sl.text_area("What's on your mind?", placeholder="Type your post here...", key="post_text")

    include_image = sl.checkbox("Attach an image (via URL)?", key="include_image")
    image_url = ""
    if include_image:
        image_url = sl.text_input("Image URL (optional)", key="post_image_url")
    

    if sl.button("Post"):
        if not post_text.strip():
            sl.warning("Post content cannot be empty.")
            return

        else:
            insert_user_post(
                user_id=user_id,
                content=post_text,
                image_url=image_url
            )

            sl.success("✅ Post created!")

            sl.session_state.reset_post_form = True  # Flag triggers clearing on next run
            sl.rerun()

def add_friend_box(user_id):
    sl.subheader("👥 Add a Friend")

    all_users = get_all_users()
    current_friends = get_user_friends(user_id)

    # Filter out yourself and people you're already friends with
    available_users = [
        user for user in all_users
        if user["id"] != user_id and user["id"] not in current_friends
    ]

    if not available_users:
        sl.info("You're already friends with everyone!")
        return

    # Build display-friendly names for selection
    user_display_map = {f'{u["name"]} ({u["username"]})': u["id"] for u in available_users}
    selected_display = sl.selectbox("Select someone to add:", user_display_map.keys())
    selected_id = user_display_map[selected_display]

    if sl.button("Add Friend"):
        add_friend(user_id, selected_id)
        sl.success(f"✅ You added {selected_display} as a friend!")
        get_user_friends.clear()
        sl.rerun()