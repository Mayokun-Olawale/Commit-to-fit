import streamlit as sl
from datetime import datetime
from data_fetcher import insert_user_post, insert_workout, get_all_users, get_user_friends, add_friend
from modules import post_creation_box, manual_workout_box
import streamlit as sl

def display_sidebar(user_id):
    sl.sidebar.title("⚡ Quick Actions")

    if "reset_post_form" in sl.session_state and sl.session_state.reset_post_form:
        sl.session_state.qa_post_text = ""
        sl.session_state.qa_post_img = ""
        sl.session_state.reset_post_form = False

    selected_quick_action = sl.sidebar.radio(
        "Choose Action:",
        ["None", "Create Post", "Add Workout", "Add Friend"],
        key="quick_action"
    )

    if selected_quick_action == "Create Post":
        sl.sidebar.markdown("---")
        sl.sidebar.subheader("📝 New Post")

        post_text = sl.sidebar.text_area("Post Content", key="qa_post_text")
        image_url = sl.sidebar.text_input("Image URL (optional)", key="qa_post_img")

        if sl.sidebar.button("Submit Post", key="qa_post_submit"):
            if post_text.strip():
                insert_user_post(user_id, post_text, image_url)
                sl.session_state.reset_post_form = True  # 🔁 Triggers clearing on next run
                sl.rerun()
            else:
                sl.sidebar.warning("Post cannot be empty.")


    elif selected_quick_action == "Add Workout":
        sl.sidebar.markdown("---")

        sl.sidebar.subheader("🏃 New Workout")

        dist = sl.sidebar.number_input("Distance (mi)", min_value=0.0, key="qa_dist")
        steps = sl.sidebar.number_input("Steps", min_value=0, key="qa_steps")
        cal = sl.sidebar.number_input("Calories", min_value=0.0, key="qa_cals")

        if sl.sidebar.button("Log Workout", key="qa_workout_submit"):
            now = datetime.now()
            insert_workout(user_id, start=now, end=now, distance=dist, steps=steps, calories=cal)
            sl.sidebar.success("✅ Workout added!")

    elif selected_quick_action == "Add Friend":
        sl.sidebar.markdown("---")
        sl.sidebar.subheader("👥 Add a Friend")

        all_users = get_all_users()
        current_friends = get_user_friends(user_id)

        # Filter out self and existing friends
        available_users = [
            user for user in all_users
            if user["id"] != user_id and user["id"] not in current_friends
        ]

        if not available_users:
            sl.sidebar.info("You're already friends with everyone!")
        else:
            display_map = {f'{u["name"]} ({u["id"]})': u["id"] for u in available_users}
            selected_label = sl.sidebar.selectbox("Select someone:", display_map.keys(), key="qa_friend_select")
            selected_id = display_map[selected_label]

            if sl.sidebar.button("Add Friend", key="qa_add_friend_btn"):
                add_friend(user_id, selected_id)
                sl.sidebar.success(f"✅ You added {selected_label} as a friend!")
                get_user_friends.clear()
                sl.rerun()