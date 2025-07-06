#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#
# You will re-write these functions in Unit 3, and are welcome to alter the
# data returned in the meantime. We will replace this file with other data when
# testing earlier units.
#############################################################################

import random
from google.cloud import bigquery
from google.api_core import exceptions as google_exceptions
from datetime import datetime
import os
import uuid
import json
IMAGE_FOLDER = "generated_advice_images"
os.makedirs(IMAGE_FOLDER, exist_ok=True)
import streamlit as sl


import types
from unittest.mock import Mock, MagicMock

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from vertexai.vision_models import Image, ImageGenerationModel
from dotenv import load_dotenv
load_dotenv()
vertexai.init(project=os.environ.get("diegoperez16techx25"), location="us-central1")


users = {
    'user1': {
        'full_name': 'Remi',
        'username': 'remi_the_rems',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user2', 'user3', 'user4'],
    },
    'user2': {
        'full_name': 'Blake',
        'username': 'blake',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1'],
    },
    'user3': {
        'full_name': 'Jordan',
        'username': 'jordanjordanjordan',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1', 'user4'],
    },
    'user4': {
        'full_name': 'Gemmy',
        'username': 'gems',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1', 'user3'],
    },
}

@sl.cache_data(
    ttl=60,
    hash_funcs={
        bigquery.Client: lambda _: None,     # or id(_)
        types.FunctionType: lambda _: None,  # ignore function hashing
        types.MethodType: lambda _: None,    # ignore method hashing
    }
)
def get_user_sensor_data(client: bigquery.Client, user_id: str, workout_id: str):
    """Returns a list of timestampped information for a given workout.
    """
    query_prompt = f"""
        SELECT SensorId, Timestamp, SensorValue
        FROM `diegoperez16techx25`.`Committees`.`SensorData`
        WHERE WorkoutID = '{workout_id}'
    """
    sensor_data_dictionaries = []
    try:
        # 1. Check if user_id exists
        user_check_query = f"""
            SELECT 1 FROM `diegoperez16techx25`.`Committees`.`Users`
            WHERE UserId = '{user_id}'
        """
        user_check_result = client.query(user_check_query).result()
        if not list(user_check_result):
            raise ValueError(f"User ID '{user_id}' not found.")

        # 2. Check if workout_id exists and is associated with user_id
        workout_check_query = f"""
            SELECT 1 FROM `diegoperez16techx25`.`Committees`.`Workouts`
            WHERE WorkoutId = '{workout_id}' AND UserId = '{user_id}'
        """
        workout_check_result = client.query(workout_check_query).result()
        if not list(workout_check_result):
            raise ValueError(f"Workout ID '{workout_id}' not found or not associated with user ID '{user_id}'.")

        query = client.query(query_prompt)
        results = query.result()  # Waits for query to finish

        for row in results:
            sensor_data_dictionaries.append({
                'SensorId': row.SensorId,
                'Timestamp': row.Timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'Data': row.SensorValue,
            })
        if sensor_data_dictionaries:
            sensor_ids = [item['SensorId'] for item in sensor_data_dictionaries]
            sensor_types_query = f"""
                SELECT SensorId, Name, Units
                FROM `diegoperez16techx25`.`Committees`.`SensorTypes`
                WHERE SensorId IN UNNEST({sensor_ids})
            """
            sensor_types_results = client.query(sensor_types_query).result()

            # 3. Create a Sensor Type Map
            sensor_types_map = {row.SensorId: {'Sensor_type': row.Name, 'Units': row.Units} for row in sensor_types_results}

            # 4. Combine Data
            for item in sensor_data_dictionaries:
                sensor_id = item['SensorId']
                if sensor_id in sensor_types_map:
                    item.update(sensor_types_map[sensor_id])
                item.pop('SensorId')

        return sensor_data_dictionaries
    except google_exceptions.GoogleAPIError as e:
        raise  # Re-raise the BigQuery API error
    except ValueError as e:
        raise # Re-raise the value errors.
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []  # Return an empty list for other unexpected errors
    

@sl.cache_data(
    ttl=60, 
    hash_funcs={
        bigquery.Client: lambda _: None,     # or id(_)
        types.FunctionType: lambda _: None,  # ignore function hashing
        types.MethodType: lambda _: None,    # ignore method hashing
    }
)
def get_user_workouts(user_id, query_db=bigquery, execute_query=None):
    """Returns a list of user's workouts from the BigQuery database.
    """
    client = query_db.Client()
    query = f""" SELECT * FROM `diegoperez16techx25.Committees.Workouts` WHERE UserId = '{user_id}' """
    # run this line to authorize queries: gcloud auth application-default login
    if execute_query is None:
        def default_execute_query(client, query):
            query_job = client.query(query)
            return query_job.result()
        execute_query = default_execute_query
    
    results = execute_query(client, query)
    workouts = []
    for row in results:
        workouts.append({
            'workout_id': row[0],
            'start_timestamp': row[2].strftime('%Y-%m-%d %H:%M:%S'),
            'end_timestamp': row[3].strftime('%Y-%m-%d %H:%M:%S'),
            'start_lat_lng': (row[4], row[5]),
            'end_lat_lng': (row[6], row[7]),
            'distance': row[8],
            'steps': row[9],
            'calories_burned': row[10]
        })
    return workouts

#used gemini for assistance:
@sl.cache_data(
    ttl=200,
    hash_funcs={
        bigquery.Client: lambda _: None,     # or id(_)
        types.FunctionType: lambda _: None,  # ignore function hashing
        types.MethodType: lambda _: None,    # ignore method hashing
    }
)
def get_user_profile(user_id, query_db=bigquery, execute_query=None):
    """Returns information about the given user.

    This function currently returns random data. You will re-write it in Unit 3.
    """

    client = query_db.Client()

    # Step 1: Get user info from the Users table
    query = f"""
        SELECT 
            Name,
            Username,
            ImageUrl,
            DateOfBirth
        FROM 
            `diegoperez16techx25.Committees.Users` 
        WHERE 
            UserId = '{user_id}'
    """

    if execute_query is None:
        def default_execute_query(client, query):
            query_job = client.query(query)
            return query_job.result()
        execute_query = default_execute_query

    results = execute_query(client, query)
    if results.total_rows == 0:
        raise ValueError(f"User {user_id} not found.")

    row = list(results)[0]

    # Step 2: Get the user's friends
    friends = get_user_friends(user_id)

    # Step 3: Return nicely structured profile data
    return {
        "full_name": row[0],
        "username": row[1],
        "profile_image": row[2],
        "date_of_birth": row[3].strftime('%Y-%m-%d') if row[3] else None,
        "friends": friends
    }

#used gemini for assistance: 
@sl.cache_data(
    ttl=30, 
    hash_funcs={
        bigquery.Client: lambda _: None,    
        types.FunctionType: lambda _: None,
        types.MethodType: lambda _: None,    
    }
)
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

def insert_user_post(user_id, content, image_url=None, query_db=bigquery, execute_query=None):
    """Inserts a new post into the Posts table in BigQuery for the given user, with custom post ID format like 'post4'."""
    client = query_db.Client()

    get_max_query = """
        SELECT MAX(CAST(SUBSTR(PostId, 5) AS INT64)) as max_id
        FROM `diegoperez16techx25.Committees.Posts`
        WHERE SAFE_CAST(SUBSTR(PostId, 5) AS INT64) IS NOT NULL
    """
    query_job = client.query(get_max_query)
    max_id_row = list(query_job.result())[0]
    max_id = max_id_row[0] or 0
    new_id = f"post{max_id + 1}"

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    content_escaped = content.replace("'", "''") 
    image_url = image_url or ''
    insert_query = f"""
        INSERT INTO `diegoperez16techx25.Committees.Posts`
        (PostId, AuthorId, Timestamp, ImageUrl, Content)
        VALUES (
            '{new_id}',
            '{user_id}',
            '{timestamp}',
            '{image_url}',
            '{content_escaped}'
        )
    """

    if execute_query is None:
        def default_execute_query(client, query):
            query_job = client.query(query)
            return query_job.result()
        execute_query = default_execute_query

    execute_query(client, insert_query)

#used gemini for assistance: 
@sl.cache_data(
    ttl=300,  # Set a 300-second TTL
    hash_funcs={
        bigquery.Client: lambda _: None,    
        types.FunctionType: lambda _: None,  
        types.MethodType: lambda _: None,   
    }
)
def get_user_friends(user_id, query_db=bigquery, execute_query=None):
    """Returns a list of a user's friends from the BigQuery database."""
    client = query_db.Client()
    query = f"""
        SELECT 
            friend_id 
        FROM 
            `diegoperez16techx25.Committees.Friends` 
        WHERE 
            user_id = '{user_id}'
    """

    if execute_query is None:
        def default_execute_query(client, query):
            query_job = client.query(query)
            return query_job.result()
        execute_query = default_execute_query

    results = execute_query(client, query)
    friends = [row[0] for row in results]
    return friends

@sl.cache_data( 
    hash_funcs={
        bigquery.Client: lambda _: None,  
        types.FunctionType: lambda _: None, 
        types.MethodType: lambda _: None,   
    }
)
def get_user_info(user_id, query_db=bigquery, execute_query=None):
    """Returns a user's profile information from the BigQuery database."""
    client = query_db.Client()
    query = f"""
        SELECT 
            Name,
            Username,
            ImageUrl
        FROM 
            `diegoperez16techx25.Committees.Users` 
        WHERE 
            UserId = '{user_id}'
    """

    if execute_query is None:
        def default_execute_query(client, query):
            query_job = client.query(query)
            return query_job.result()
        execute_query = default_execute_query

    results = execute_query(client, query)
    if results.total_rows > 0:
        row = next(iter(results))
        return {
            'full_name': row[0],
            'username': row[1],
            'profile_image': row[2],
        }
    else:
        return None



@sl.cache_data(
    ttl=120, 
    hash_funcs={
        bigquery.Client: lambda _: None,    
        types.FunctionType: lambda _: None, 
    }
)
def get_genai_advice(
   user_id: str,
   client: bigquery.Client= None,
   text_model: GenerativeModel = None,
   image_model: ImageGenerationModel = None,
   workouts_provider: callable = None,
   timestamp: datetime = None
):
   """
   Generate fitness advice and motivational image based on user's workout history.
  
   Args:
       user_id: The ID of the user
       text_model: GenerativeModel instance (injected for testing)
       image_model: ImageGenerationModel instance (injected for testing)
       workouts_provider: Function to get workouts (injected for testing)
       timestamp: Optional timestamp (for testing)
  
   Returns:
       Dictionary containing advice_id, content, image filename, and timestamp
   """
   if client is None:
       client = bigquery.Client()
   user_check_query = f"""
           SELECT 1 FROM `diegoperez16techx25`.`Committees`.`Users`
           WHERE UserId = '{user_id}'
       """
   user_check_result = client.query(user_check_query).result()
   if not list(user_check_result):
       raise ValueError(f"User ID '{user_id}' not found.")


   if text_model is None:
       text_model = GenerativeModel(
           "gemini-1.5-flash-002",
           system_instruction="You are a qualified fitness coach. You will take input the data from client which is a list of information from different workouts they did and then you will give me a 1-2 sentence advice based on this information."
       )
  
   if image_model is None:
       image_model = ImageGenerationModel.from_pretrained("imagegeneration@006")
  
   if workouts_provider is None:
       workouts_provider = get_user_workouts  # Default to your actual function
  
   if timestamp is None:
       timestamp = datetime.now()
  
   # Get workouts for the user
   try:
       workouts = workouts_provider(user_id)
   except Exception as e:
       print(f"❌ Workout retrieval failed: {e}")
       return None
  
   result = {}
   response_schema = {
       "type": "OBJECT",
       "properties": {
           "adviceid": {"type": "STRING", "description": "Unique identifier for the advice"},
           "advice": {"type": "STRING", "description": "The 1-2 sentence fitness advice"}
       },
       "required": ["adviceid", "advice"]
   }
  
   # Generate advice
   try:
       if workouts:
           advice_prompt = "Generate advice and an adviceid for this user based on this workout summary list: " + str(workouts)
       else:
           advice_prompt = "Give advice and an adviceid for this user, The user has no recorded workouts. Give a motivational message to start training"
       advice_response = text_model.generate_content(
           advice_prompt,
           generation_config=GenerationConfig(
               response_mime_type="application/json",
               response_schema=response_schema
           ),
       )
      
       structured_response = json.loads(advice_response.text)
       advice_id = structured_response.get("adviceid")
       advice_content = structured_response.get("advice")
      
       if not advice_id or not advice_content:
           raise ValueError("Invalid response from text model")
          
       result['advice_id'] = advice_id
       result['content'] = advice_content
   except Exception as e:
       print(f"Error generating advice: {e}")
       return None
  
   # Generate image
   try:
       image_prompt = f"Please generate aesthetic motivating image for this advice: {advice_content}, If humans are featured, they should be clothed"
       image_response = image_model.generate_images(
           prompt=image_prompt,
           number_of_images=1
       )
      
       if image_response and image_response.images:
           image = image_response.images[0]
           filename = f"{IMAGE_FOLDER}/motivation_{uuid.uuid4().hex}.png"
           image.save(filename)
           result['image'] = filename
       else:
           result['image'] = None
   except Exception as e:
       print(f"Error generating image: {e}")
       result['image'] = None
  
   # Add timestamp
   result['timestamp'] = timestamp.strftime("%Y-%m-%d %H:%M:%S")
  
   return result

@sl.cache_data(
    hash_funcs={
        bigquery.Client: lambda _: None,    
        types.FunctionType: lambda _: None, 
    }
)
def get_user_ID_from_username(username, query_db=bigquery, execute_query=None):
    client = query_db.Client()
    query = f""" SELECT UserId FROM `diegoperez16techx25.Committees.Users` where username = '{username}' """
    
    if execute_query is None:
        def default_execute_query(client, query):
            query_job = client.query(query)
            return query_job.result()
        execute_query = default_execute_query
    
    results = execute_query(client, query)
    if results.total_rows == 0:
        raise ValueError(f"User {username} not found.")
        
    row = list(results)[0]
    return row[0]
    

@sl.cache_data( 
    hash_funcs={
        bigquery.Client: lambda _: None,    
        types.FunctionType: lambda _: None, 
    }
)
def get_user_password(username, query_db=bigquery, execute_query=None):
    client = query_db.Client()
    query = f""" SELECT Password FROM `diegoperez16techx25.Committees.Users` where username = '{username}' """
    
    if execute_query is None:
        def default_execute_query(client, query):
            query_job = client.query(query)
            return query_job.result()
        execute_query = default_execute_query
    
    results = execute_query(client, query)
    if results.total_rows == 0:
        raise ValueError(f"User {username} not found.")
        
    row = list(results)[0]
    return row[0]

@sl.cache_data(
    hash_funcs={
        bigquery.Client: lambda _: None,    
        types.FunctionType: lambda _: None, 
    }
)
def set_user_password(username, password, query_db=bigquery, execute_query=None):
    client = query_db.Client()
    query = f""" UPDATE `diegoperez16techx25.Committees.Users` SET Password = '{password}' WHERE Username = '{username}' """
    
    if execute_query is None:
        def default_execute_query(client, query):
            query_job = client.query(query)
            return query_job.result()
        execute_query = default_execute_query
    execute_query(client, query) #no return value, don't need to assign to var


def get_global_calories_list(client: bigquery.Client= None):
    if client is None:
       client = bigquery.Client()
    query = client.query('''
    SELECT
      Users.Name,
      SUM(Workouts.CaloriesBurned) AS TotalCalories,
      Users.UserId  -- Include UserId in the query
    FROM
      `diegoperez16techx25`.`Committees`.`Users` AS Users
    INNER JOIN
      `diegoperez16techx25`.`Committees`.`Workouts` AS Workouts
    ON
      Users.UserId = Workouts.UserId
    GROUP BY
      1, 3; --  Include UserId in the GROUP BY clause
    ''')
    results = query.result()
    global_calories_list = []
    for row in results:
        name = row.Name
        total_calories = row.TotalCalories
        user_id = row.UserId # Extract UserId from the row
        global_calories_list.append((name, int(total_calories), user_id)) # Append a tuple
    sorted_global_calories_list = sorted(global_calories_list, key=lambda item: item[1], reverse=True)
    if len(sorted_global_calories_list) > 10:
        sorted_global_calories_list = sorted_global_calories_list[:10]
    return sorted_global_calories_list


def get_friends_calories_list(user_id, client: bigquery.Client= None):
    if client is None:
       client = bigquery.Client()
    query = client.query(f'''
    SELECT
    Users.Name,
    SUM(Workouts.CaloriesBurned) AS TotalCalories,
    Users.UserId  -- Include UserId in the query
    FROM
    `diegoperez16techx25`.Committees.Users
    INNER JOIN
    `diegoperez16techx25`.Committees.Workouts ON Users.UserId = Workouts.UserId
    WHERE
    Users.UserId = '{user_id}'  --  Calories for the specified user
    GROUP BY
    1, 3

    UNION ALL

    SELECT
    Users.Name,
    SUM(Workouts.CaloriesBurned) AS TotalCalories,
    Users.UserId  -- Include UserId in the query
    FROM
    `diegoperez16techx25`.`Committees`.`Users` AS Users
    INNER JOIN
    `diegoperez16techx25`.`Committees`.`Friends` AS Friends ON Users.UserId = Friends.friend_id
    INNER JOIN
    `diegoperez16techx25`.`Committees`.`Workouts` AS Workouts ON Users.UserId = Workouts.UserId
    WHERE
    Friends.user_id = '{user_id}'
    GROUP BY
    1, 3;
        ''')
    results = query.result()
    friends_calories_list = []
    for row in results:
        name = row.Name
        total_calories = row.TotalCalories
        user_id = row.UserId
        friends_calories_list.append((name, int(total_calories), user_id))
    sorted_friends_calories_list = sorted(friends_calories_list, key=lambda item: item[1], reverse=True)
    if len(sorted_friends_calories_list) > 10:
        sorted_friends_calories_list = sorted_friends_calories_list[:10]
    return sorted_friends_calories_list

def get_global_distance_list(client: bigquery.Client = None):
    if client is None:
        client = bigquery.Client()
    query = client.query('''
    SELECT
      Users.Name,
      SUM(Workouts.TotalDistance) AS TotalDistance,
      Users.UserId
    FROM
      `diegoperez16techx25`.`Committees`.`Users` AS Users
    INNER JOIN
      `diegoperez16techx25`.`Committees`.`Workouts` AS Workouts
    ON
      Users.UserId = Workouts.UserId
    GROUP BY
      1, 3
    ''')
    results = query.result()
    distance_list = [(row.Name, float(row.TotalDistance), row.UserId) for row in results]
    sorted_list = sorted(distance_list, key=lambda item: item[1], reverse=True)
    return sorted_list[:10]

def get_friends_distance_list(user_id, client: bigquery.Client = None):
    if client is None:
        client = bigquery.Client()
    query = client.query(f'''
    SELECT
    Users.Name,
    SUM(Workouts.TotalDistance) AS TotalDistance,
    Users.UserId
    FROM
    `diegoperez16techx25`.Committees.Users
    INNER JOIN
    `diegoperez16techx25`.Committees.Workouts ON Users.UserId = Workouts.UserId
    WHERE
    Users.UserId = '{user_id}'
    GROUP BY
    1, 3

    UNION ALL

    SELECT
    Users.Name,
    SUM(Workouts.TotalDistance) AS TotalDistance,
    Users.UserId
    FROM
    `diegoperez16techx25`.Committees.Users AS Users
    INNER JOIN
    `diegoperez16techx25`.Committees.Friends AS Friends ON Users.UserId = Friends.friend_id
    INNER JOIN
    `diegoperez16techx25`.Committees.Workouts AS Workouts ON Users.UserId = Workouts.UserId
    WHERE
    Friends.user_id = '{user_id}'
    GROUP BY
    1, 3
    ''')
    results = query.result()
    distance_list = [(row.Name, float(row.TotalDistance), row.UserId) for row in results]
    sorted_list = sorted(distance_list, key=lambda item: item[1], reverse=True)
    return sorted_list[:10]

def get_global_steps_list(client: bigquery.Client = None):
    if client is None:
        client = bigquery.Client()
    query = client.query('''
    SELECT
      Users.Name,
      SUM(Workouts.TotalSteps) AS TotalSteps,
      Users.UserId
    FROM
      `diegoperez16techx25`.`Committees`.`Users` AS Users
    INNER JOIN
      `diegoperez16techx25`.`Committees`.`Workouts` AS Workouts
    ON
      Users.UserId = Workouts.UserId
    GROUP BY
      1, 3
    ''')
    results = query.result()
    steps_list = [(row.Name, int(row.TotalSteps), row.UserId) for row in results]
    sorted_list = sorted(steps_list, key=lambda item: item[1], reverse=True)
    return sorted_list[:10]

def get_friends_steps_list(user_id, client: bigquery.Client = None):
    if client is None:
        client = bigquery.Client()
    query = client.query(f'''
    SELECT
    Users.Name,
    SUM(Workouts.TotalSteps) AS TotalSteps,
    Users.UserId
    FROM
    `diegoperez16techx25`.Committees.Users
    INNER JOIN
    `diegoperez16techx25`.Committees.Workouts ON Users.UserId = Workouts.UserId
    WHERE
    Users.UserId = '{user_id}'
    GROUP BY
    1, 3

    UNION ALL

    SELECT
    Users.Name,
    SUM(Workouts.TotalSteps) AS TotalSteps,
    Users.UserId
    FROM
    `diegoperez16techx25`.Committees.Users AS Users
    INNER JOIN
    `diegoperez16techx25`.Committees.Friends AS Friends ON Users.UserId = Friends.friend_id
    INNER JOIN
    `diegoperez16techx25`.Committees.Workouts AS Workouts ON Users.UserId = Workouts.UserId
    WHERE
    Friends.user_id = '{user_id}'
    GROUP BY
    1, 3
    ''')
    results = query.result()
    steps_list = [(row.Name, int(row.TotalSteps), row.UserId) for row in results]
    sorted_list = sorted(steps_list, key=lambda item: item[1], reverse=True)
    return sorted_list[:10]


def create_new_user(username, name, image_url, date_of_birth, password, query_db=bigquery, execute_query=None):
    client = query_db.Client()
    def get_next_user_id():
        query = f"""
            SELECT MAX(CAST(REGEXP_EXTRACT(UserId, r'user(\\d+)') AS INT64)) AS max_id
            FROM `diegoperez16techx25.Committees.Users`
            WHERE REGEXP_CONTAINS(UserId, r'^user\\d+$')
        """
        result = client.query(query).result()
        row = next(result)
        return f"user{(row.max_id + 1) if row.max_id else 1}"
    
    user_id = get_next_user_id()
    
    escaped_name = name.replace("'", "''") 

    query = f"""
        INSERT INTO `diegoperez16techx25.Committees.Users` (UserId, Name, Username, ImageUrl, DateOfBirth, Password)
        VALUES (
            '{user_id}',
            '{escaped_name}',
            '{username}',
            '{image_url}',
            DATE '{date_of_birth}',
            '{password}'
        )
    """


    client.query(query).result()

def username_exists(username, query_db=bigquery):
    client = query_db.Client()
    table_id = "diegoperez16techx25.Committees.Users"

    query = f"""
        SELECT COUNT(*) as count
        FROM `{table_id}`
        WHERE Username = @username
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("username", "STRING", username)
        ]
    )

    result = client.query(query, job_config=job_config).result()
    row = next(result)

    return row.count > 0

def insert_workout(user_id, start, end, distance, steps, calories, query_db=bigquery):
    client = query_db.Client()
    table_id = "diegoperez16techx25.Committees.Workouts"

    def get_next_workout_id():
        query = f"""
            SELECT MAX(CAST(REGEXP_EXTRACT(WorkoutId, r'workout(\\d+)') AS INT64)) AS max_id
            FROM `{table_id}`
            WHERE REGEXP_CONTAINS(WorkoutId, r'^workout\\d+$')
        """
        result = client.query(query).result()
        row = next(result)
        return f"workout{(row.max_id + 1) if row.max_id else 1}"

    workout_id = get_next_workout_id()

    # Convert Python datetime to DATETIME string format
    start_str = start.strftime('%Y-%m-%d %H:%M:%S')
    end_str = end.strftime('%Y-%m-%d %H:%M:%S')

    query = f"""
        INSERT INTO `{table_id}` (WorkoutId, UserId, StartTimestamp, EndTimestamp, TotalDistance, TotalSteps, CaloriesBurned)
        VALUES (
            @workout_id,
            @user_id,
            @start,
            @end,
            @distance,
            @steps,
            @calories
        )
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("workout_id", "STRING", workout_id),
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("start", "DATETIME", start_str),
            bigquery.ScalarQueryParameter("end", "DATETIME", end_str),
            bigquery.ScalarQueryParameter("distance", "FLOAT64", distance),
            bigquery.ScalarQueryParameter("steps", "INT64", steps),
            bigquery.ScalarQueryParameter("calories", "FLOAT64", calories),
        ]
    )

    client.query(query, job_config=job_config).result()
    return workout_id

def insert_sensor_data(workout_id, sensor_id, timestamp, value, query_db=bigquery):
    client = query_db.Client()
    table_id = "diegoperez16techx25.Committees.SensorData"

    query = f"""
        INSERT INTO `{table_id}` (SensorId, WorkoutID, Timestamp, SensorValue)
        VALUES (@sensor_id, @workout_id, @timestamp, @value)
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("sensor_id", "STRING", sensor_id),
            bigquery.ScalarQueryParameter("workout_id", "STRING", workout_id),
            bigquery.ScalarQueryParameter("timestamp", "DATETIME", timestamp.strftime('%Y-%m-%d %H:%M:%S')),
            bigquery.ScalarQueryParameter("value", "FLOAT64", value)
        ]
    )

    client.query(query, job_config=job_config).result()

def get_all_users(query_db=bigquery):
    client = query_db.Client()
    query = """
        SELECT UserId, Name, Username
        FROM `diegoperez16techx25.Committees.Users`
    """
    results = client.query(query).result()
    return [{"id": row["UserId"], "name": row["Name"], "username": row["Username"]} for row in results]

def add_friend(user_id, friend_id, query_db=bigquery):
    client = query_db.Client()
    query = f"""
        INSERT INTO `diegoperez16techx25.Committees.Friends` (user_id, friend_id)
        VALUES (@user_id, @friend_id)
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("friend_id", "STRING", friend_id),
        ]
    )
    client.query(query, job_config=job_config).result()



