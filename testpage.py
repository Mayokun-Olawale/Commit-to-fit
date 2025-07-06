import streamlit as sl
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts
from streamlit_option_menu import option_menu
from activity_page import display
from community_page import display_community



def display_app_page():
    """Displays the home page of the app."""
    userId = 'user1'
    user_profile = get_user_profile(userId)
    user_name = user_profile['username']

   
    selected = option_menu(
        menu_title=None,  # Appears at top of sidebar
        options=["Home", "Activities", "Community"],
        icons=["house", "bar-chart", "heart"],  # Choose icons from https://icons.getbootstrap.com/
        default_index=0,
        menu_icon="cast",
        orientation="horizontal",
    )

    if selected == "Home":
        sl.title("🏠 Home Page")
        sl.subheader(f"Welcome {user_profile['full_name']} to MyFitness!")

        # Profile Card
        sl.image(user_profile['profile_image'], width=150, caption="Your Profile Picture")

        sl.markdown(f"**Username:** {user_profile['username']}")
        sl.markdown(f"**Date of Birth:** {user_profile['date_of_birth']}")

        # Friends section
        sl.markdown("### 👯 Your Friends")
        if user_profile['friends']:
            for friend_id in user_profile['friends']:
                sl.markdown(f"- {friend_id}")
        else:
            sl.info("You don't have any friends yet!")
        display_genai_advice(userId)

    