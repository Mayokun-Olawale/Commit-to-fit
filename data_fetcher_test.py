#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
#############################################################################
import unittest
from unittest.mock import patch, Mock, call, MagicMock
from datetime import datetime
import json
from google.cloud.bigquery import Row
from google.cloud import exceptions as google_exceptions
from google.api_core import exceptions as google_exceptions
from data_fetcher import get_user_workouts, get_user_sensor_data, get_genai_advice, get_user_posts, get_user_friends, get_user_info, get_user_profile, get_global_calories_list, set_user_password, get_user_password, get_friends_calories_list
from google.cloud import bigquery

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from vertexai.vision_models import Image, ImageGenerationModel

import streamlit as sl

class TestGetUserWorkouts(unittest.TestCase):
    
    def mock_execute_query(self, client, query):
        return [
            ('workout1', 'user1', datetime(2024, 7, 29, 7, 0, 0), datetime(2024, 7, 29, 8, 0, 0), 37.7749, -122.4194, 37.8049, -122.421, 5.0, 8000, 400.0),
            ('workout2', 'user1', datetime(2024, 7, 30, 7, 0, 0), datetime(2024, 7, 30, 8, 0, 0), 38.7749, -123.4194, 38.8049, -123.421, 6.0, 9000, 500.0),
        ]
    @patch('google.cloud.bigquery.Client')
    def test_get_user_workouts_queries_db(self, mock_big_query_client):
        sl.cache_data.clear() # Clear the cache so that the tests can run more than once
        mock_client = Mock()
        mock_big_query_client.return_value = mock_client
        mock_query_job = Mock()
        mock_query_job.result.return_value = self.mock_execute_query(mock_client, mock_query_job)
        mock_client.query.return_value = mock_query_job
        workouts = get_user_workouts('user1')
        self.assertTrue(mock_big_query_client.call_count > 0, 'Database not called!')
    @patch('google.cloud.bigquery.Client')
    def test_get_user_workouts_first_list_correct(self, mock_big_query_client):
        mock_client = Mock()
        mock_big_query_client.return_value = mock_client
        mock_query_job = Mock()
        mock_query_job.result.return_value = self.mock_execute_query(mock_client, mock_query_job)
        mock_client.query.return_value = mock_query_job
        workouts = get_user_workouts('user1')
        self.assertTrue(workouts[0]['workout_id'], 'workout1')
        self.assertTrue(workouts[0]['start_timestamp'], datetime(2024, 7, 29, 7, 0, 0).strftime('%Y-%m-%d %H:%M:%S'))
        self.assertTrue(workouts[0]['start_timestamp'], datetime(2024, 7, 29, 8, 0, 0).strftime('%Y-%m-%d %H:%M:%S'))
        self.assertTrue(workouts[0]['start_lat_lng'], (37.7749, -122.4194))
        self.assertTrue(workouts[0]['end_lat_lng'], (37.8049, -122.421))
        self.assertTrue(workouts[0]['distance'], 5.0)
        self.assertTrue(workouts[0]['steps'], 8000)
        self.assertTrue(workouts[0]['calories_burned'], 400.0)
    @patch('google.cloud.bigquery.Client')
    def test_get_user_workouts_second_list_correct(self, mock_big_query_client):
        mock_client = Mock()
        mock_big_query_client.return_value = mock_client
        mock_query_job = Mock()
        mock_query_job.result.return_value = self.mock_execute_query(mock_client, mock_query_job)
        mock_client.query.return_value = mock_query_job
        workouts = get_user_workouts('user1')
        self.assertTrue(workouts[0]['workout_id'], 'workout2')
        self.assertTrue(workouts[0]['start_timestamp'], datetime(2024, 7, 30, 7, 0, 0).strftime('%Y-%m-%d %H:%M:%S'))
        self.assertTrue(workouts[0]['start_timestamp'], datetime(2024, 7, 30, 8, 0, 0).strftime('%Y-%m-%d %H:%M:%S'))
        self.assertTrue(workouts[0]['start_lat_lng'], (38.7749, -123.4194))
        self.assertTrue(workouts[0]['end_lat_lng'], (38.8049, -123.421))
        self.assertTrue(workouts[0]['distance'], 6.0)
        self.assertTrue(workouts[0]['steps'], 9000)
        self.assertTrue(workouts[0]['calories_burned'], 500.0)

class TestPasswords(unittest.TestCase):

    def mock_big_query_client_passwords(self, client, query):
        return "Password"

    @patch('google.cloud.bigquery.Client')
    def test_set_user_password_updates_password(self, mock_big_query_client):
        sl.cache_data.clear() # Clear the cache so that the tests can run more than once
        username = 'jlsampson'
        password = "Password"
        expected_query = f""" UPDATE `diegoperez16techx25.Committees.Users` SET Password = '{password}' WHERE Username = '{username}' """
    
        mock_client = Mock()
        mock_big_query_client.return_value = mock_client
        mock_query_job = Mock()
        mock_client.query.return_value = mock_query_job
        mock_query_job.result.return_value = None  # Simulate successful execution

        set_user_password(username, password)

        mock_big_query_client.assert_called_once()
        mock_client.query.assert_called_once_with(expected_query)
        mock_query_job.result.assert_called_once()

    @patch('google.cloud.bigquery.Client')
    def test_get_user_password_returns_correct_password(self, mock_big_query_client):
        sl.cache_data.clear() # Clear the cache so that the tests can run more than once
        username = 'jlsampson'
        expected_password = 'Password'
        expected_query = f""" SELECT Password FROM `diegoperez16techx25.Committees.Users` where username = '{username}' """
    
        mock_client = Mock()
        mock_big_query_client.return_value = mock_client
        mock_query_job = Mock()
        mock_client.query.return_value = mock_query_job
        mock_query_job.result.return_value = None  # Simulate successful execution
        mock_results = MagicMock()
        mock_query_job.result.return_value = mock_results
        mock_results.total_rows = 1
        mock_results.__iter__.return_value = [("Password",)]  # Simulate a single row with the password

        actual_password = get_user_password(username)

        mock_big_query_client.assert_called_once()
        mock_client.query.assert_called_once_with(expected_query)
        mock_query_job.result.assert_called_once()
        self.assertEqual(expected_password, actual_password)
        
    @patch('google.cloud.bigquery.Client')
    def test_get_user_password_user_not_found(self, mock_bigquery_client):
        # Arrange
        username = "nonexistentuser"
        expected_query = f""" SELECT Password FROM `diegoperez16techx25.Committees.Users` where username = '{username}' """

        # Create mock objects simulating no results
        mock_client = Mock()
        mock_bigquery_client.return_value = mock_client
        mock_query_job = MagicMock()
        mock_client.query.return_value = mock_query_job
        mock_results = MagicMock() 
        mock_query_job.result.return_value = mock_results
        mock_results.total_rows = 0
        mock_results.__iter__.return_value = []

        # Act and Assert
        with self.assertRaises(ValueError) as context:
            get_user_password(username, query_db=bigquery)
        self.assertEqual(str(context.exception), f"User {username} not found.")


#used gemini for assistance:        
class TestGetUserFriends(unittest.TestCase):

    def mock_execute_query_friends(self, client, query):
        if "Friends" in query:
            return [("friend1",), ("friend2",), ("friend3",)]
        else:
            return []  # Return empty if it's not the Friends query

    @patch('google.cloud.bigquery.Client')
    def test_get_user_friends_basic(self, mock_big_query_client):
        mock_client = Mock()
        mock_big_query_client.return_value = mock_client
        mock_query_job = Mock()
        mock_client.query.return_value = mock_query_job  # Mock the query call

        # Call get_user_friends with the custom execute_query function
        friends = get_user_friends(
            "user1",
            execute_query=self.mock_execute_query_friends
        )

        expected_friends = ["friend1", "friend2", "friend3"]

        self.assertEqual(friends, expected_friends)

    def mock_execute_query_no_friends(self, client, query):
        return []

    @patch('google.cloud.bigquery.Client')
    def test_get_user_friends_no_friends(self, mock_big_query_client):
        mock_client = Mock()
        mock_big_query_client.return_value = mock_client
        mock_query_job = Mock()
        mock_client.query.return_value = mock_query_job

        friends = get_user_friends(
            "user2",
            execute_query=self.mock_execute_query_no_friends
        )

        expected_friends = []

        self.assertEqual(friends, expected_friends)

#used gemini for assistance:   
def get_user_posts(user_id, query_db=bigquery, execute_query=None):
    """Returns a list of a user's posts from the BigQuery database."""
    client = query_db.Client()
    query = f"""
        SELECT 
            PostId,
            AuthorId,
            Timestamp,
            ImageUrl,
            Content
        FROM 
            `diegoperez16techx25.Committees.Posts` 
        WHERE 
            AuthorId = '{user_id}'
    """

    if execute_query is None:
        def default_execute_query(client, query):
            query_job = client.query(query)
            return query_job.result()
        execute_query = default_execute_query

    results = execute_query(client, query)
    posts = []
    for row in results:
        posts.append({
            'post_id': row[0],
            'user_id': row[1],
            'timestamp': row[2].strftime('%Y-%m-%d %H:%M:%S'),
            'image': row[3],
            'content': row[4],
        })
    return posts

#used gemini for assistance: 
class TestGetUserPosts(unittest.TestCase):

    def mock_execute_query_posts(self, client, query):
        if "Posts" in query:
            return [
                ("post1", "user1", datetime(2023, 11, 15, 12, 30, 0), "image1.jpg", "Hello world!"),
                ("post2", "user1", datetime(2023, 11, 16, 14, 45, 0), "image2.jpg", "Another post."),
            ]
        else:
            return []

    @patch('google.cloud.bigquery.Client')
    def test_get_user_posts_basic(self, mock_big_query_client):
        mock_client = Mock()
        mock_big_query_client.return_value = mock_client
        mock_query_job = Mock()
        mock_client.query.return_value = mock_query_job

        posts = get_user_posts("user1", execute_query=self.mock_execute_query_posts)

        expected_posts = [
            {
                "post_id": "post1",
                "user_id": "user1",
                "timestamp": "2023-11-15 12:30:00",
                "image": "image1.jpg",
                "content": "Hello world!",
            },
            {
                "post_id": "post2",
                "user_id": "user1",
                "timestamp": "2023-11-16 14:45:00",
                "image": "image2.jpg",
                "content": "Another post.",
            },
        ]

        self.assertEqual(posts, expected_posts)

    def mock_execute_query_no_posts(self, client, query):
        return []

    @patch('google.cloud.bigquery.Client')
    def test_get_user_posts_no_posts(self, mock_big_query_client):
        mock_client = Mock()
        mock_big_query_client.return_value = mock_client
        mock_query_job = Mock()
        mock_client.query.return_value = mock_query_job

        posts = get_user_posts("user2", execute_query=self.mock_execute_query_no_posts)

        expected_posts = []

        self.assertEqual(posts, expected_posts)

#used gemini for assistance: 
class TestGetUserFriends(unittest.TestCase):

    def mock_execute_query_friends(self, client, query):
        if "Friends" in query:
            return [("friend1",), ("friend2",), ("friend3",)]
        else:
            return []

    @patch('google.cloud.bigquery.Client')
    def test_get_user_friends_basic(self, mock_big_query_client):
        mock_client = Mock()
        mock_big_query_client.return_value = mock_client
        mock_query_job = Mock()
        mock_client.query.return_value = mock_query_job

        friends = get_user_friends("user1", execute_query=self.mock_execute_query_friends)

        expected_friends = ["friend1", "friend2", "friend3"]

        self.assertEqual(friends, expected_friends)

    def mock_execute_query_no_friends(self, client, query):
        return []

    @patch('google.cloud.bigquery.Client')
    def test_get_user_friends_no_friends(self, mock_big_query_client):
        mock_client = Mock()
        mock_big_query_client.return_value = mock_client
        mock_query_job = Mock()
        mock_client.query.return_value = mock_query_job

        friends = get_user_friends("user2", execute_query=self.mock_execute_query_no_friends)

        expected_friends = []

        self.assertEqual(friends, expected_friends)

class TestGetUserProfile(unittest.TestCase):

    def make_mock_result(self, rows):
        mock_result = MagicMock()
        mock_result.total_rows = len(rows)
        mock_result.__iter__.return_value = iter(rows)  # Makes it iterable like BigQuery results
        return mock_result


    def mock_execute_query_profile(self, client, query):
        if "Users" in query:
            rows = [(
                "Remi",                     # Name
                "remi_the_rems",            # Username
                "https://img.jpg",          # ImageUrl
                datetime(1990, 1, 1)        # DateOfBirth
            )]
            return self.make_mock_result(rows)
        return self.make_mock_result([])


    def mock_execute_query_friends(self, client, query):
        rows = []
        if "Friends" in query:
            rows = [("user2",), ("user3",)]

        mock_result = MagicMock()
        mock_result.total_rows = len(rows)
        mock_result.__iter__.return_value = iter(rows)

        return mock_result


    @patch('google.cloud.bigquery.Client')
    def test_get_user_profile_returns_correct_data(self, mock_big_query_client):
        mock_client = MagicMock()
        mock_big_query_client.return_value = mock_client

        with patch('data_fetcher.get_user_friends', return_value=["user2", "user3"]):
            user_profile = get_user_profile(
                "user1", 
                execute_query=self.mock_execute_query_profile
            )

        expected = {
            "full_name": "Remi",
            "username": "remi_the_rems",
            "profile_image": "https://img.jpg",
            "date_of_birth": "1990-01-01",
            "friends": ["user2", "user3"]
        }

        self.assertEqual(user_profile, expected)

    @patch('google.cloud.bigquery.Client')
    def test_get_user_profile_raises_error_on_user_not_found(self, mock_big_query_client):
        mock_client = MagicMock()
        mock_big_query_client.return_value = mock_client

        with self.assertRaises(ValueError):
            get_user_profile("userX", execute_query=self.mock_execute_query_user_not_found)
    
    def mock_execute_query_user_not_found(self, client, query):
        return self.make_mock_result([])       

class TestGetUserSensorData(unittest.TestCase):

    @patch('google.cloud.bigquery.Client')
    def test_get_user_sensor_data_success(self, MockClient):
        mock_client_instance = Mock()
        mock_client_instance.query.side_effect = [
            Mock(result=Mock(return_value=[1])),  # User exists
            Mock(result=Mock(return_value=[1])),  # Workout exists and is mapped to user
            Mock(result=Mock(return_value=[
                Mock(SensorId='sensor_a', Timestamp=datetime(2025, 4, 3, 19, 15, 0), SensorValue=120.0),
                Mock(SensorId='sensor_b', Timestamp=datetime(2025, 4, 3, 19, 30, 0), SensorValue=3000.0)
            ])),
            Mock(result=Mock(return_value=[
                Mock(SensorId='sensor_a', Name='Heart Rate', Units='bpm'),
                Mock(SensorId='sensor_b', Name='Step Count', Units='steps')
            ]))
        ]
        MockClient.return_value = mock_client_instance
        actual_data = get_user_sensor_data(MockClient(), "test_user", "test_workout")
        expected_data = [
            {'Timestamp': '2025-04-03 19:15:00', 'Data': 120.0, 'Sensor_type': 'Heart Rate', 'Units': 'bpm'},
            {'Timestamp': '2025-04-03 19:30:00', 'Data': 3000.0, 'Sensor_type': 'Step Count', 'Units': 'steps'},
        ]
        self.assertEqual(actual_data, expected_data)

    @patch('google.cloud.bigquery.Client')
    def test_get_user_sensor_data_invalid_user_id(self, MockClient):
        mock_client_instance = Mock()
        mock_client_instance.query.return_value.result.return_value = [] 

        MockClient.return_value = mock_client_instance

        with self.assertRaises(ValueError) as context:
            get_user_sensor_data(MockClient(), "invalid_user", "test_workout")

        self.assertEqual(str(context.exception), "User ID 'invalid_user' not found.")

    @patch('google.cloud.bigquery.Client')
    def test_get_user_sensor_data_invalid_workout_id(self, MockClient):
        mock_client_instance = Mock()
        mock_client_instance.query.side_effect = [
            Mock(result=Mock(return_value=[1])),  # User exists
            Mock(result=Mock(return_value=[])),
        ]
        MockClient.return_value = mock_client_instance

        with self.assertRaises(ValueError) as context:
            get_user_sensor_data(MockClient(), "test_user", "invalid_workout")

        self.assertEqual(str(context.exception), "Workout ID 'invalid_workout' not found or not associated with user ID 'test_user'.")

    @patch('google.cloud.bigquery.Client')
    def test_get_user_sensor_data_success_no_sensor_data(self, MockClient):
        mock_client_instance = Mock()
        mock_client_instance.query.side_effect = [
            Mock(result=Mock(return_value=[1])),  # User exists
            Mock(result=Mock(return_value=[1])),  # Workout exists
            Mock(result=Mock(return_value=[])),  # No sensor data
            Mock(result=Mock(return_value=[]))   # No sensor types (still called)
        ]
        MockClient.return_value = mock_client_instance

        actual_data = get_user_sensor_data(MockClient(), "test_user", "test_workout")
        expected_data = []
        self.assertEqual(actual_data, expected_data)
        
    @patch('google.cloud.bigquery.Client')
    def test_get_user_sensor_data_missing_sensor_types(self, MockClient):
        mock_client_instance = Mock()
        mock_client_instance.query.side_effect = [
            Mock(result=Mock(return_value=[1])),  # User exists
            Mock(result=Mock(return_value=[1])),
            Mock(result=Mock(return_value=[
                Mock(SensorId='sensor_a', Timestamp=datetime(2025, 4, 3, 19, 15, 0), SensorValue=120.0),
            ])),
            Mock(result=Mock(return_value=[]))
        ]
        MockClient.return_value = mock_client_instance

        actual_data = get_user_sensor_data(MockClient(), "test_user", "test_workout")
        expected_data = [{'Timestamp': '2025-04-03 19:15:00', 'Data': 120.0}]
        self.assertEqual(actual_data, expected_data)

    @patch('google.cloud.bigquery.Client')
    def test_get_user_sensor_data_bigquery_error(self, MockClient):
        mock_client_instance = Mock()
        mock_client_instance.query.side_effect = google_exceptions.ServiceUnavailable("BigQuery service unavailable")
        MockClient.return_value = mock_client_instance

        with self.assertRaises(google_exceptions.ServiceUnavailable):
            get_user_sensor_data(MockClient(), "test_user", "test_workout")

    @patch('google.cloud.bigquery.Client')
    def test_get_user_sensor_data_general_error(self, MockClient):
        mock_client_instance = Mock()
        mock_client_instance.query.side_effect = Exception("General Exception")
        MockClient.return_value = mock_client_instance

        actual_data = get_user_sensor_data(MockClient(), "test_user", "test_workout")

        self.assertEqual(actual_data, [])

class TestGetGenaiAdvice(unittest.TestCase): 
    @patch('google.auth.default', return_value=("mock-project", None))
    @patch('vertexai.init')
    @patch('google.cloud.bigquery.Client')
    @patch('vertexai.generative_models.GenerativeModel')
    @patch('vertexai.vision_models.ImageGenerationModel.from_pretrained')
    def test_get_genai_advice_success(self, 
                                    mock_image_model,  # Last patch (5)
                                    mock_text_model,            # 4th patch (GenerativeModel)
                                    mock_client,                # 3rd patch (bigquery.Client)
                                    mock_vertexai_init,         # 2nd patch (vertexai.init)
                                    mock_auth_default):         # First patch (google.auth.default)
        IMAGE_FOLDER = "generated_advice_images"
       # Setup mocks (now using correct variable names)
        mock_client_instance = Mock()
        mock_client_instance.query.return_value.result.return_value = [1]
        mock_client.return_value = mock_client_instance
        
        mock_text_instance = Mock()
        mock_text_instance.generate_content.return_value.text = json.dumps({
            "adviceid": "advice123", 
            "advice": "Mix cardio with strength training for better results."
        })
        mock_text_model.return_value = mock_text_instance
        
        mock_image_instance = Mock()
        mock_image = Mock()
        mock_image.save = Mock()  # The save method we want to verify

        mock_image_response = Mock()
        mock_image_response.images = [mock_image]  # Contains our mock image with save method
        mock_image_instance.generate_images.return_value = mock_image_response
        mock_image_model.return_value = mock_image_instance
      
       # Call the function
        result = get_genai_advice(
            user_id="test_user",
            client=mock_client_instance,
            text_model=mock_text_instance,
            image_model=mock_image_instance,
            workouts_provider=Mock(return_value=[...]),
            timestamp=datetime(2025, 4, 5, 12, 0, 0)
        )
      
       # Assertions
        self.assertEqual(result['advice_id'], "advice123")
        self.assertEqual(result['content'], "Mix cardio with strength training for better results.")
        self.assertTrue(result['image'].startswith(IMAGE_FOLDER))  # Just check the prefix
        self.assertTrue(result['image'].endswith(".png"))  # Just check the suffix
        self.assertEqual(result['timestamp'], "2025-04-05 12:00:00")
      
       # Verify the image was saved with the same filename that's returned
        mock_image.save.assert_called_once_with(result['image'])


    @patch('google.cloud.bigquery.Client')
    def test_get_genai_advice_user_not_found(self, mock_client):
       # Setup BigQuery client mock to return empty result (user not found)
       mock_client_instance = Mock()
       mock_client_instance.query.return_value.result.return_value = []
       mock_client.return_value = mock_client_instance
      
       # Call the function and check for exception
       with self.assertRaises(ValueError) as context:
           get_genai_advice(user_id="nonexistent_user", client=mock_client_instance)
          
       self.assertEqual(str(context.exception), "User ID 'nonexistent_user' not found.")


    @patch('google.auth.default', return_value=("mock-project", None))
    @patch('vertexai.init')
    @patch('google.cloud.bigquery.Client')
    @patch('vertexai.generative_models.GenerativeModel')
    @patch('vertexai.vision_models.ImageGenerationModel.from_pretrained')     
    def test_get_genai_advice_no_workouts(self, 
                                    mock_image_model,  # Last patch (5)
                                    mock_text_model,            # 4th patch (GenerativeModel)
                                    mock_client,                # 3rd patch (bigquery.Client)
                                    mock_vertexai_init,         # 2nd patch (vertexai.init)
                                    mock_auth_default):         # First patch (google.auth.default)
       # Setup BigQuery client mock
       mock_client_instance = Mock()
       mock_client_instance.query.return_value.result.return_value = [1]  # User exists
       mock_client.return_value = mock_client_instance
      
      
       # Setup text model mock
       mock_text_instance = Mock()
       mock_response = Mock()
       mock_response.text = json.dumps({"adviceid": "advice123", "advice": "Start with light exercises to build a habit."})
       mock_text_instance.generate_content.return_value = mock_response
       mock_text_model.return_value = mock_text_instance
      
       # Setup image model mock
       mock_image_instance = Mock()
       mock_image = Mock()
       mock_image.save = Mock()
       mock_image_response = Mock()
       mock_image_response.images = [mock_image]
       mock_image_instance.generate_images.return_value = mock_image_response
       mock_image_model.return_value = mock_image_instance
      
       # Call the function
       result = get_genai_advice(
           user_id="test_user",
           client=mock_client_instance,
           text_model=mock_text_instance,
           image_model=mock_image_instance,
           workouts_provider=Mock(return_value=[]),
       )
      
       # Verify the prompt mentions no workouts
       prompt_arg = mock_text_instance.generate_content.call_args[0][0]
       self.assertIn("no recorded workouts", prompt_arg)
      
       # Validate results
       self.assertEqual(result['advice_id'], "advice123")
       self.assertEqual(result['content'], "Start with light exercises to build a habit.")


    @patch('google.auth.default', return_value=("mock-project", None))
    @patch('vertexai.init')
    @patch('google.cloud.bigquery.Client')
    @patch('vertexai.generative_models.GenerativeModel')
    @patch('vertexai.vision_models.ImageGenerationModel.from_pretrained')
    def test_get_genai_advice_text_model_exception(self, 
                                                    mock_image_model,  # Last patch (5)
                                                    mock_text_model,            # 4th patch (GenerativeModel)
                                                    mock_client,                # 3rd patch (bigquery.Client)
                                                    mock_vertexai_init,         # 2nd patch (vertexai.init)
                                                    mock_auth_default):         # First patch (google.auth.default)
       # Setup BigQuery client mock
       mock_client_instance = Mock()
       mock_client_instance.query.return_value.result.return_value = [1]  # User exists
       mock_client.return_value = mock_client_instance
      
      
       # Setup text model to raise exception
       mock_text_instance = Mock()
       mock_text_instance.generate_content.side_effect = Exception("Text model failed")
       mock_text_model.return_value = mock_text_instance
      
       # Call the function
       result = get_genai_advice(
           user_id="test_user",
           client=mock_client_instance,
           text_model=mock_text_instance,
           workouts_provider=Mock(return_value=[])
       )
      
       # Verify function gracefully handles the error
       self.assertIsNone(result)

    @patch('google.auth.default', return_value=("mock-project", None))
    @patch('vertexai.init')
    @patch('google.cloud.bigquery.Client')
    @patch('vertexai.generative_models.GenerativeModel')
    @patch('vertexai.vision_models.ImageGenerationModel.from_pretrained')
    def test_get_genai_advice_image_model_exception(self, 
                                                    mock_image_model,  # Last patch (5)
                                                    mock_text_model,            # 4th patch (GenerativeModel)
                                                    mock_client,                # 3rd patch (bigquery.Client)
                                                    mock_vertexai_init,         # 2nd patch (vertexai.init)
                                                    mock_auth_default):         # First patch (google.auth.default)
       # Setup BigQuery client mock
       mock_client_instance = Mock()
       mock_client_instance.query.return_value.result.return_value = [1]  # User exists
       mock_client.return_value = mock_client_instance
      
       # Setup text model mock
       mock_text_instance = Mock()
       mock_response = Mock()
       mock_response.text = json.dumps({"adviceid": "advice123", "advice": "Run more consistently"})
       mock_text_instance.generate_content.return_value = mock_response
       mock_text_model.return_value = mock_text_instance
      
       # Setup image model to raise exception
       mock_image_instance = Mock()
       mock_image_instance.generate_images.side_effect = Exception("Image generation failed")
       mock_image_model.return_value = mock_image_instance
      
       # Call the function
       result = get_genai_advice(
           user_id="test_user",
           client=mock_client_instance,
           text_model=mock_text_instance,
           image_model=mock_image_instance,
           workouts_provider=Mock(return_value=[])
       )
      
       # Verify advice is still returned but image is None
       self.assertEqual(result['advice_id'], "advice123")
       self.assertEqual(result['content'], "Run more consistently")
       self.assertIsNone(result['image'])


class TestGetGlobalCaloriesList(unittest.TestCase):

    @patch('google.cloud.bigquery.Client')
    def test_get_global_calories_list_success(self, mock_bigquery_client):
        """
        Test that the function correctly processes query results and returns a sorted list of tuples.
        """
        # 1. Arrange
        mock_row1 = Mock(Name="Alice", TotalCalories=1200, UserId="alice123")
        mock_row2 = Mock(Name="Bob", TotalCalories=800, UserId="bob456")
        mock_row3 = Mock(Name="Charlie", TotalCalories=1500, UserId="charlie789")
        mock_results = [mock_row1, mock_row2, mock_row3]

        mock_query_job = Mock()
        mock_query_job.result.return_value = mock_results

        mock_client = mock_bigquery_client.return_value
        mock_client.query.return_value = mock_query_job

        expected_output = [
            ("Charlie", 1500, "charlie789"),
            ("Alice", 1200, "alice123"),
            ("Bob", 800, "bob456"),
        ]

        # 2. Act
        actual_output = get_global_calories_list()

        # 3. Assert
        self.assertEqual(actual_output, expected_output)
        mock_client.query.assert_called_once()

    @patch('google.cloud.bigquery.Client')
    def test_get_global_calories_list_limits_results(self, mock_bigquery_client):
        """
        Test that the function limits the results to the top 10 users.
        """
        # 1. Arrange
        mock_rows = [Mock(Name=f"User{i}", TotalCalories=2000 - i * 100, UserId=f"user{i}") for i in range(15)]

        mock_query_job = Mock()
        mock_query_job.result.return_value = mock_rows

        mock_client = mock_bigquery_client.return_value
        mock_client.query.return_value = mock_query_job

        expected_output = [
            (f"User{i}", 2000 - i * 100, f"user{i}") for i in range(10)
        ]

        # 2. Act
        actual_output = get_global_calories_list()

        # 3. Assert
        self.assertEqual(len(actual_output), 10)
        self.assertEqual(actual_output, expected_output)
        mock_client.query.assert_called_once()

    @patch('google.cloud.bigquery.Client')
    def test_get_global_calories_list_handles_empty_results(self, mock_bigquery_client):
        """
        Test that the function handles the case where the query returns no results.
        """
        # 1. Arrange
        mock_query_job = Mock()
        mock_query_job.result.return_value = []

        mock_client = mock_bigquery_client.return_value
        mock_client.query.return_value = mock_query_job

        expected_output = []

        # 2. Act
        actual_output = get_global_calories_list()

        # 3. Assert
        self.assertEqual(actual_output, expected_output)
        mock_client.query.assert_called_once()

    @patch('google.cloud.bigquery.Client')
    def test_get_global_calories_list_uses_provided_client(self, mock_bigquery_client):
        """
        Test that the function uses the provided BigQuery client if one is given.
        """
        # 1. Arrange
        provided_client = Mock()

        mock_row1 = Mock(Name="David", TotalCalories=950, UserId="david111")
        mock_results = [mock_row1]
        mock_query_job = Mock()
        mock_query_job.result.return_value = mock_results

        provided_client.query.return_value = mock_query_job

        expected_output = [("David", 950, "david111")]

        # 2. Act
        actual_output = get_global_calories_list(client=provided_client)

        # 3. Assert
        self.assertEqual(actual_output, expected_output)
        provided_client.query.assert_called_once()
        mock_bigquery_client.assert_not_called()

class TestGetFriendsCaloriesList(unittest.TestCase):

    @patch('google.cloud.bigquery.Client')
    def test_get_friends_calories_list_success(self, mock_bigquery_client):
        """
        Test that the function correctly processes query results and returns a sorted list of tuples.
        This test mocks the BigQuery client and query execution to return predefined data.
        """
        # 1. Arrange
        mock_row_user = Mock(Name="User1", TotalCalories=1000, UserId="user1_id")
        mock_row_friend1 = Mock(Name="Friend1", TotalCalories=1200, UserId="friend1_id")
        mock_row_friend2 = Mock(Name="Friend2", TotalCalories=800, UserId="friend2_id")
        mock_results = [mock_row_user, mock_row_friend1, mock_row_friend2]

        mock_query_job = Mock()
        mock_query_job.result.return_value = mock_results

        mock_client = mock_bigquery_client.return_value
        mock_client.query.return_value = mock_query_job

        expected_output = [
            ("Friend1", 1200, "friend1_id"),
            ("User1", 1000, "user1_id"),
            ("Friend2", 800, "friend2_id"),
        ]

        # 2. Act
        actual_output = get_friends_calories_list(user_id='user1')

        # 3. Assert
        self.assertEqual(actual_output, expected_output)
        mock_client.query.assert_called_once()

    @patch('google.cloud.bigquery.Client')
    def test_get_friends_calories_list_limits_results(self, mock_bigquery_client):
        """
        Test that the function limits the results to the top 10 users (including the main user).
        """
        # 1. Arrange
        mock_row_user = Mock(Name="User1", TotalCalories=2000, UserId="user1_id")
        mock_friends_rows = [Mock(Name=f"Friend{i}", TotalCalories=2000 - i * 100, UserId=f"friend{i}_id") for i in range(10)]
        mock_results = [mock_row_user] + mock_friends_rows

        mock_query_job = Mock()
        mock_query_job.result.return_value = mock_results

        mock_client = mock_bigquery_client.return_value
        mock_client.query.return_value = mock_query_job

        expected_output = [ ("User1", 2000, "user1_id"), ] + [(f"Friend{i}", 2000 - i * 100, f"friend{i}_id") for i in range(9)]
        

        # 2. Act
        actual_output = get_friends_calories_list(user_id='user1')

        # 3. Assert
        self.assertEqual(len(actual_output), 10)
        self.assertEqual(actual_output, expected_output)
        mock_client.query.assert_called_once()

    @patch('google.cloud.bigquery.Client')
    def test_get_friends_calories_list_handles_empty_friends(self, mock_bigquery_client):
        """
        Test that the function handles the case where the user has no friends.
        It should still return the user's calories.
        """
        # 1. Arrange
        mock_row_user = Mock(Name="User1", TotalCalories=500, UserId="user1_id")
        mock_results = [mock_row_user]
        mock_query_job = Mock()
        mock_query_job.result.return_value = mock_results

        mock_client = mock_bigquery_client.return_value
        mock_client.query.return_value = mock_query_job

        expected_output = [("User1", 500, "user1_id")]

        # 2. Act
        actual_output = get_friends_calories_list(user_id='user1')

        # 3. Assert
        self.assertEqual(actual_output, expected_output)
        mock_client.query.assert_called_once()

    @patch('google.cloud.bigquery.Client')
    def test_get_friends_calories_list_uses_provided_client(self, mock_bigquery_client):
        """
        Test that the function uses the provided BigQuery client if one is given.
        """
        # 1. Arrange
        provided_client = Mock()

        mock_row_user = Mock(Name="David", TotalCalories=950, UserId="david111")
        mock_results = [mock_row_user]
        mock_query_job = Mock()
        mock_query_job.result.return_value = mock_results

        provided_client.query.return_value = mock_query_job

        expected_output = [("David", 950, "david111")]

        # 2. Act
        actual_output = get_friends_calories_list(user_id='user1', client=provided_client)

        # 3. Assert
        self.assertEqual(actual_output, expected_output)
        provided_client.query.assert_called_once()
        mock_bigquery_client.assert_not_called()

if __name__ == "__main__":
    unittest.main()