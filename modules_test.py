#############################################################################
# modules_test.py
#
# This file contains tests for modules.py.
#
# You will write these tests in Unit 2.
#############################################################################

import unittest
import streamlit as sl
from streamlit.testing.v1 import AppTest
from modules import display_post, display_activity_summary, display_genai_advice, display_recent_workouts, users
from data_fetcher import get_user_posts, get_user_workouts
from unittest.mock import patch, Mock, call
import pandas as pd


# Write your tests below

#used gemini for assistance: 

# Mock data (replace with your actual data)
users = {
    'user1': {
        'full_name': 'Remi',
        'username': 'remi_the_rems',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user2', 'user3', 'user4'],
    },
    'user2': {
        'full_name': 'Alice',
        'username': 'alice_wonder',
        'profile_image': 'alice.jpg',
        'friends': [],
    },
    'user3': {
        'full_name': 'Bob',
        'username': 'bob_builder',
        'profile_image': 'bob.jpg',
        'friends': [],
    },
    'user4': {
        'full_name': 'Charlie',
        'username': 'charlie_chaplin',
        'profile_image': 'charlie.jpg',
        'friends': [],
    },
}

posts = {
    'user2': [{'content': 'Post from user2', 'timestamp': '2023-10-27 10:00:00', 'image': None}],
    'user3': [{'content': 'Post from user3', 'timestamp': '2023-10-27 11:00:00', 'image': None}],
    'user4': [{'content': 'Post from user4', 'timestamp': '2023-10-27 12:00:00', 'image': None}],
}

def get_user_posts(user_id):
    return posts.get(user_id, [])

def get_user_friends(user_id):
    return users[user_id]['friends']

def get_user_info(user_id):
    if user_id in users:
        return {
            'full_name': users[user_id]['full_name'],
            'username': users[user_id]['username'],
            'profile_image': users[user_id]['profile_image'],
        }
    else:
        return None  # Return None if the user is not found

def display_post(user_id, get_friends_func=get_user_friends, get_info_func=get_user_info, get_posts_func=get_user_posts, streamlit_module=None):
    """
    Displays list of user's friends' posts: includes, pfp, name, username, timestamp, and post.
    """
    friends = get_friends_func(user_id)

    streamlit_module.header("Friends' Posts")

    for friend_id in friends:
        friend_info = get_info_func(friend_id)
        if friend_info:
            posts = get_posts_func(friend_id)

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


class TestDisplayPost(unittest.TestCase):
    """
    Tests the display_post function:
        valid user + valid friend
        checks if friends in user correlates
        invalid friend
    """
    @patch('streamlit.image')
    @patch('streamlit.subheader')
    @patch('streamlit.write')
    @patch('streamlit.markdown')
    def test_valid_user_posts(self, mock_markdown, mock_write, mock_subheader, mock_image):
        #checks if the info is on the page if user and friends are valid
        mock_sl = Mock()
        display_post('user1', get_friends_func=get_user_friends, get_info_func=get_user_info, get_posts_func=get_user_posts, streamlit_module=mock_sl)
        self.assertTrue(mock_sl.subheader.call_count > 0)
        self.assertTrue(mock_sl.write.call_count > 0)
        self.assertTrue(mock_sl.image.call_count > 0)
        self.assertTrue(mock_sl.markdown.call_count > 0)
        unittest.mock.patch.stopall() # unpatch after test

    def test_correct_friends_displayed(self):
        mock_sl = Mock()
        display_post('user1', get_friends_func=get_user_friends, get_info_func=get_user_info, get_posts_func=get_user_posts, streamlit_module=mock_sl)

        # Check if subheader was called for each friend
        expected_friend_names = [
            f"{users['user2']['full_name']} (@{users['user2']['username']})",
            f"{users['user3']['full_name']} (@{users['user3']['username']})",
            f"{users['user4']['full_name']} (@{users['user4']['username']})",
        ]

        actual_calls = [call[0][0] for call in mock_sl.subheader.call_args_list]

        self.assertEqual(actual_calls, expected_friend_names)
        unittest.mock.patch.stopall() # unpatch after test

    def test_invalid_friend(self):
        #checks for error if invalid friend
        mock_sl = Mock()
        original_friends = users['user1']['friends']
        users['user1']['friends'] = ['invalid_friend']  # Add invalid friend

        display_post('user1', get_friends_func=get_user_friends, get_info_func=get_user_info, get_posts_func=get_user_posts, streamlit_module=mock_sl)

        mock_sl.warning.assert_called_once_with("Friend ID 'invalid_friend' not found.")

        users['user1']['friends'] = original_friends #restore friends list.
        unittest.mock.patch.stopall() # unpatch after test

class TestDisplayActivitySummary(unittest.TestCase):
    """Tests the display_activity_summary function using Streamlit's AppTest."""
    @patch("data_fetcher.get_user_workouts")
    def setUp(self, mock_fetch):
        """Set up the AppTest environment using from_function()"""
        
        self.test_workouts = [
            {
                'workout_id': 'workout0',
                "start_timestamp": "2024-03-07 08:00:00",
                "end_timestamp": "2024-03-07 08:30:00",
                'start_lat_lng': (),
                'end_lat_lng': (),
                "distance": 3.2,
                "steps": 4500,
                "calories_burned": 320
            },
            {
                'workout_id': 'workout1',
                "start_timestamp": "2024-03-06 07:30:00",
                "end_timestamp": "2024-03-06 08:00:00",
                'start_lat_lng': (),
                'end_lat_lng': (),
                "distance": 2.5,
                "steps": 3800,
                "calories_burned": 270
            }
        ]

        mock_fetch.return_value = self.test_workouts

        fetcher = lambda: mock_fetch("user1")

        # Asked LLM help on how to pass kwargs
        #self.app = AppTest.from_function(display_activity_summary, kwargs={"workouts_list": self.test_workouts})
        # Line written by ChatGPT

        self.app = AppTest.from_function(display_activity_summary, kwargs={"fetcher": fetcher})

        self.app.run()  # Run the application to apply testing

        self.subheaders = [subh for subh in self.app.subheader]

        # Calculate expected totals
        expected_distance = sum(workout["distance"] for workout in self.test_workouts) # Line written by ChatGPT
        expected_steps = sum(workout["steps"] for workout in self.test_workouts) # Line written by ChatGPT
        expected_calories = sum(workout["calories_burned"] for workout in self.test_workouts) # Line written by ChatGPT

        self.total_distance = expected_distance
        self.total_steps = expected_steps
        self.total_calories = expected_calories

        self.columns = [col for col in self.app.columns]
    
    
    def test_select_box(self):
        select_box_elements = [el.label for el in self.app.selectbox]
        # Check for workout selection dropdown
        # Used help of LLM
        found_dropdown = any("Workout (Beta - Only Running has data):" in label for label in select_box_elements)
        self.assertTrue(found_dropdown, "Workout selection dropdown not found!")
    
    def test_workout_type(self):
        self.assertEqual(self.app.session_state.selected_workout, "Running")
    
    def test_calculated_totals(self):

        metrics = [ el.value for el in self.app.metric]

        # In Total values, Total Distance is always the first element
        self.assertEqual(metrics[0], f"{5.7} mi", 
                         f"Total Distance metric incorrect! Expected {self.total_distance} mi")
        
        self.assertEqual(metrics[1], f"{8300}", f"Total Steps isn't correct! Expected {self.total_steps}")
        self.assertEqual(metrics[2], f"{590} cals", f"Total Calories isn't correct! Expected {self.total_calories}")
    
    def test_columns_init(self):

        self.assertEqual(len(self.columns), 3)

    def test_columns_values(self):

        # Checking for first columns where should be displayed Total Distance
        self.assertIn("Total Distance",self.columns[0].metric[0].label, "Label isn't Total Distance!")
        self.assertEqual(f"{self.total_distance} mi", self.columns[0].metric[0].value)

        # Checking for second columns where should be displayed Total Steps
        self.assertIn("Total Steps",self.columns[1].metric[0].label, "Label isn't Total Steps!")
        self.assertEqual(f"{self.total_steps}", self.columns[1].metric[0].value)

         # Checking for first columns where should be displayed Total Calories
        self.assertIn("Total Calories", self.columns[2].metric[0].label, "Label isn't Total Calories!")
        self.assertEqual(f"{self.total_calories} cals", self.columns[2].metric[0].value)
    
    def test_details_table_init(self):

        # Check for first subheader that should appear (first one created)
        self.assertIn("Workout Details", self.subheaders[0].body)

        # Check if size of dataframe is more than 0 (it's not empty)
        self.assertGreater(len(self.app.dataframe), 0)
    
    def test_details_table_values(self):
        # As for the actual function code, utilized LLM
        # to correctly access dataframe data

        import pandas as pd

        renamed_column_map = {
            "Distance (mi)": "distance",
            "Steps Taken": "steps",
            "Calories Burned": "calories_burned"
        }

        # Get the actual dataframe from the Streamlit test response
        df_element = self.app.dataframe  # This is a Streamlit ElementList
        # Line written by ChatGPT
        df = pd.DataFrame(df_element[0].value._data)  # Convert it back to a Pandas DataFrame
        # Line written by ChatGPT

        self.assertIsInstance(df, pd.DataFrame)  # Ensure it's a DataFrame
        # Line written by ChatGPT

        workout_keys = df.columns.tolist()

        for key in workout_keys:
            self.assertIn(key, df.columns)

            expected_lst = []

            for workout in self.test_workouts:
                og_key = renamed_column_map[key]
                expected_lst.append(workout[og_key])
            
            self.assertListEqual(df[key].tolist(),expected_lst)
    
    def test_progress_bar(self):

        # Check for second subheader that should appear (second one created)
        self.assertIn("Weekly Calorie Progress", self.subheaders[1].body)

        self.assertEqual(self.app.session_state.weekly_calorie_goal, 2000) # Default calorie goal for now (hardcoded)

        test_progress_bar_amount = min(((self.total_calories / 2000) * 100), 100)
        # Line written by ChatGPT

        self.assertEqual(test_progress_bar_amount, self.app.session_state.weekly_calorie_progress_amount)


class TestDisplayGenAIAdvice(unittest.TestCase):
    """Tests the updated display_genai_advice function with injected advice_func."""


    @patch('streamlit.title')
    @patch('streamlit.subheader')
    @patch('streamlit.markdown')
    @patch('streamlit.image')
    @patch('streamlit.caption')
    def test_display_with_image(self, mock_caption, mock_image, mock_markdown, mock_subheader, mock_title):
        """Test all Streamlit calls when image is provided"""
        test_data_with_image = {
            "content": "Test advice",
            "timestamp": "2024-03-07 12:00:00",
            "image": "mock.png"
        }
        mock_advice_func = Mock(return_value=test_data_with_image)
        
        display_genai_advice(
            userId="test123",
            advice_func=mock_advice_func,
            streamlit_module=sl
        )
        
        mock_title.assert_called_once_with("AI Fitness Coach🦾")
        mock_subheader.assert_called_once_with("Personalized advice based on your activities")
        mock_markdown.assert_called_once_with("Test advice")
        mock_image.assert_called_once_with("mock.png")
        mock_caption.assert_called_once_with(f"Last updated: 2024-03-07 12:00:00")

    @patch('streamlit.title')
    @patch('streamlit.subheader')
    @patch('streamlit.markdown')
    @patch('streamlit.image')
    @patch('streamlit.caption')
    def test_display_with_no_image(self, mock_caption, mock_image, mock_markdown, mock_subheader, mock_title):
        """Test all Streamlit calls when no image is provided"""
        test_data_no_image = {
            "content": "Test advice",
            "timestamp": "2024-03-07 12:00:00",
            "image": None
        }
        mock_advice_func = Mock(return_value=test_data_no_image)
        
        display_genai_advice(
            userId="test123",
            advice_func=mock_advice_func,
            streamlit_module=sl
        )
        
        mock_title.assert_called_once_with("AI Fitness Coach🦾")
        mock_subheader.assert_called_once_with("Personalized advice based on your activities")
        mock_markdown.assert_called_once_with("Test advice")
        mock_image.assert_not_called()
        mock_caption.assert_called_once_with(f"Last updated: 2024-03-07 12:00:00")


class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function."""
    def mock_get_user_workouts(self, userId):
        #mocks get_user_workouts and returns test data
        return [
            {
                'workout_id': 'workout0',
                "start_timestamp": "2024-03-07 08:00:00",
                "end_timestamp": "2024-03-07 08:30:00",
                'start_lat_lng': (),
                'end_lat_lng': (),
                "distance": 3.2,
                "steps": 4500,
                "calories_burned": 320
            },
            {
                'workout_id': 'workout1',
                "start_timestamp": "2024-03-06 07:30:00",
                "end_timestamp": "2024-03-06 08:00:00",
                'start_lat_lng': (),
                'end_lat_lng': (),
                "distance": 2.5,
                "steps": 3800,
                "calories_burned": 270
            }
        ]

    # @patch('streamlit.title')
    # def test_drw_contains_title(self, mock_title):
    #     "Checks to make sure the title is present"
    #     mock_sl = Mock()
    #     display_recent_workouts('user1', workouts_func=self.mock_get_user_workouts, streamlit_module=mock_sl)
    #     self.assertTrue(mock_sl.title.call_count > 0, "Title \'Recent Workouts\' not found!")
    
    @patch('streamlit.subheader')
    def test_drw_contains_subheader(self, mock_subheader):
        "Checks to make sure the subheader is present"
        mock_sl = Mock()
        display_recent_workouts('user1', workouts_func=self.mock_get_user_workouts, streamlit_module=mock_sl)
        self.assertTrue(mock_sl.subheader.call_count > 0, 'Subheader not found!')
    
    @patch('streamlit.subheader')
    def test_drw_contains_encouragement(self, mock_write):
        "Checks to make sure the final encouragement text is shown"
        mock_sl = Mock()
        display_recent_workouts('user1', workouts_func=self.mock_get_user_workouts, streamlit_module=mock_sl)
        encouragement = "Keep up the good work(outs)!"
        calls = [call[0][0] for call in mock_sl.subheader.call_args_list]
        self.assertTrue(any(encouragement in call for call in calls), f'{encouragement} no found!')

    #rest of tests are Gemini generated, was a bit repetitive
    @patch('streamlit.write')
    def test_drw_contains_correct_date(self, mock_write):
        mock_sl = Mock()
        display_recent_workouts('user1', workouts_func=self.mock_get_user_workouts, streamlit_module=mock_sl)
        
        expected_date_1 = "Date: 2024-03-07"
        expected_date_2 = "Date: 2024-03-06"
        
        calls = [call[0][0] for call in mock_sl.write.call_args_list]
        self.assertTrue(any(expected_date_1 in call for call in calls), f"{expected_date_1} not found!")
        self.assertTrue(any(expected_date_2 in call for call in calls), f"{expected_date_2} not found!")

    @patch('streamlit.write')
    def test_drw_contains_correct_time(self, mock_write):
        mock_sl = Mock()
        display_recent_workouts('user1', workouts_func=self.mock_get_user_workouts, streamlit_module=mock_sl)
        
        expected_time_1 = "Time: 08:00:00 &mdash; 08:30:00"
        expected_time_2 = "Time: 07:30:00 &mdash; 08:00:00"

        calls = [call[0][0] for call in mock_sl.write.call_args_list]
        self.assertTrue(any(expected_time_1 in call for call in calls), f"{expected_time_1} not found!")
        self.assertTrue(any(expected_time_2 in call for call in calls), f"{expected_time_2} not found!")

    @patch('streamlit.write')
    def test_drw_contains_correct_distance(self, mock_write):
        mock_sl = Mock()
        display_recent_workouts('user1', workouts_func=self.mock_get_user_workouts, streamlit_module=mock_sl)
        
        expected_distance_1 = "Distance: 3.2 miles"
        expected_distance_2 = "Distance: 2.5 miles"

        calls = [call[0][0] for call in mock_sl.write.call_args_list]
        self.assertTrue(any(expected_distance_1 in call for call in calls), f"{expected_distance_1} not found!")
        self.assertTrue(any(expected_distance_2 in call for call in calls), f"{expected_distance_2} not found!")

    @patch('streamlit.write')
    def test_drw_contains_correct_steps(self, mock_write):
        mock_sl = Mock()
        display_recent_workouts('user1', workouts_func=self.mock_get_user_workouts, streamlit_module=mock_sl)
        
        expected_steps_1 = "Steps: 4500"
        expected_steps_2 = "Steps: 3800"

        calls = [call[0][0] for call in mock_sl.write.call_args_list]
        self.assertTrue(any(expected_steps_1 in call for call in calls), f"{expected_steps_1} not found!")
        self.assertTrue(any(expected_steps_2 in call for call in calls), f"{expected_steps_2} not found!")

    @patch('streamlit.write')
    def test_drw_contains_correct_calories(self, mock_write):
        mock_sl = Mock()
        display_recent_workouts('user1', workouts_func=self.mock_get_user_workouts, streamlit_module=mock_sl)
        
        expected_calories_1 = "Calories Burned: 320 calories"
        expected_calories_2 = "Calories Burned: 270 calories"

        calls = [call[0][0] for call in mock_sl.write.call_args_list]
        self.assertTrue(any(expected_calories_1 in call for call in calls), f"{expected_calories_1} not found!")
        self.assertTrue(any(expected_calories_2 in call for call in calls), f"{expected_calories_2} not found!")

    @patch('streamlit.subheader')
    @patch('streamlit.write')
    def test_drw_empty_workout_table_contains_subheader(self, mock_write, mock_subheader):
        """Tests that the correct message is displayed for an empty workout list."""
        mock_sl = Mock()
        def empty_workouts(userId):
            return []
        display_recent_workouts('user1', workouts_func=empty_workouts, streamlit_module=mock_sl)
        
        calls = [call[0][0] for call in mock_sl.subheader.call_args_list]
        self.assertTrue(any("No Workout Data To Display" in call for call in calls), "Empty list message not found!")
        self.assertEqual(mock_sl.write.call_count,0)


if __name__ == "__main__":
    unittest.main()
