import streamlit as sl
from modules import display_global_leaderboard, display_friends_leaderboard
from data_fetcher import  get_friends_calories_list,get_global_calories_list, insert_user_post, get_global_distance_list, get_global_steps_list, get_friends_distance_list, get_friends_steps_list

def render_leaderboards(user_id):
    # sl.markdown("---")
    sl.subheader("🏆 Leaderboards")

    leaderboard_type = sl.radio("Select Leaderboard:", ["Global", "Friends"], horizontal=True)
    metric = sl.radio("Choose Category:", ["calories", "distance", "steps"], horizontal=True)

    # Map metrics to fetch functions
    global_funcs = {
        "calories": get_global_calories_list,
        "distance": get_global_distance_list,
        "steps": get_global_steps_list
    }

    friends_funcs = {
        "calories": get_friends_calories_list,
        "distance": get_friends_distance_list,
        "steps": get_friends_steps_list
    }

    sl.markdown("---")

    if leaderboard_type == "Global":
        display_global_leaderboard(
            metric=metric,
            streamlit_module=sl,
            get_leaderboard_func=global_funcs[metric],
            highlight_user_id=user_id  
        )
    elif leaderboard_type == "Friends":
        display_friends_leaderboard(
            user_id=user_id,
            metric=metric,  # comes from the radio button above
            streamlit_module=sl
        )
