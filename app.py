#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as sl
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts,get_user_friends
from streamlit_option_menu import option_menu
from activity_page import display_activity_page
from community_page import display_community
from auth_page import display_auth, logout
from sidebar import display_sidebar
from modules import post_creation_box, manual_workout_box, add_friend_box
from leaderboard_page import render_leaderboards


def display_app_page():
    """Displays the home page of the app."""

    sl.set_page_config(layout="wide")
    
    if 'userId' not in sl.session_state:
        # sl.session_state.userId = 'user1'
        display_auth()
        sl.markdown('Testers: Log in using username \'alicej\' and password \'AliceR0ckss\'')
        return

    userId = sl.session_state.userId

    user_profile = get_user_profile(userId)
    user_name = user_profile['username']

    friends = get_user_friends(userId)
    friend_profiles = [get_user_profile(fid) for fid in friends]
    friend_names = [p['full_name'] for p in friend_profiles]
    friend_usernames = [p['username'] for p in friend_profiles]

    selected = option_menu(
        menu_title=None,  # Appears at top of sidebar
        options=["Home", "Activities", "Community","LeaderBoards"],
        icons=["house", "bar-chart", "heart","trophy"],  # Choose icons from https://icons.getbootstrap.com/
        default_index=0,
        menu_icon="cast",
        orientation="horizontal",
    )

    if selected == "Home":
        sl.title("🏠 Home Page")
        sl.subheader(f"Welcome {user_profile['full_name']} to Commit To Fit!")

        # Profile Card
        col1, col2 = sl.columns([1, 3])
        with col1:
            if user_profile['profile_image']:
                sl.image(user_profile['profile_image'], width=150)
        with col2:
            sl.markdown(f"**Username:** {user_profile['username']}")
            sl.markdown(f"**Date of Birth:** {user_profile['date_of_birth']}")

        # Friends section
        sl.markdown("---")
        sl.markdown("###  Your Friends")
        if friends:
            with sl.container():
                for i, j in zip(friend_names, friend_usernames):
                    sl.markdown(f"**{i}**  \n`@{j}`")
        else:
            sl.info("You don't have any friends yet!")


    elif selected == "Activities":
        display_activity_page(user_id=userId)

    elif selected == "Community":
        display_community(userId)
    
    
    elif selected == "LeaderBoards":
        render_leaderboards(userId)
    
    selected_action = display_sidebar(userId)

    if selected_action == "Create Post":
        post_creation_box(userId)

    elif selected_action == "Add Workout":
        manual_workout_box()

    elif selected_action == "Add Friend":
        add_friend_box(userId)
    
    sl.markdown("---")
    if sl.button("🚪 Log Out"):
        logout()

        

# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()
