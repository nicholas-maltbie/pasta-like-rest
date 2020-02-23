from flask import Blueprint, jsonify, request, session
from project.database import game_database, valid_room_id
import re

SESSION_USERNAME = "username"
SESSION_ROOM = "room"

ROOM_ID = "room_id"
USERNAME = "username"

games_api = Blueprint('games_api', __name__)

VALID_NAME_CHARS = "[a-zA-Z0-9-_]"
username_chars = re.compile(VALID_NAME_CHARS)
username_regex = re.compile(VALID_NAME_CHARS + "{3,8}")

def get_filtered_username(name):
    return "".join([l for l in name if username_chars.match(l)])

def valid_username(name):
    return username_regex.match(name) != None

def attempt_join(join_room, join_name):
    if not valid_room_id(join_room):
        response = jsonify("Room Id not valid")
        response.status_code = 400
        return response
    elif not game_database.room_exists(join_room):
        response = jsonify("Room Id not found")
        response.status_code = 404
        return response
    session_name = session[SESSION_USERNAME] if SESSION_USERNAME in session else None
    session_room = session[SESSION_ROOM] if SESSION_ROOM in session else None

    # Fix the user's name so they can't change names
    #  from the same browser. They just rejoined the room so we're good
    if session_room != None and session_room == join_room and session_name != None:
        session[SESSION_USERNAME] = session_name
        session[SESSION_ROOM] = session_room

        response = jsonify("Successfully rejoined room %s as user %s" % (session_room, session_name))
        response.status_code = 200
        return response
    
    # Attempt to join the room
    # Filter out invalid characters in name
    join_name = get_filtered_username(join_name)
    # Check to ensure name is valid
    if not valid_username(join_name):
        response = jsonify("Invalid username")
        response.status_code = 400
        return response

    # Check to ensure the game is not full
    if game_database.is_room_full(join_room):
        response = jsonify("Room is full")
        response.status_code = 401
        return response

    # Check to ensure the game is not full
    if game_database.is_player_in_room(join_room, join_name):
        response = jsonify("Name is taken")
        response.status_code = 401
        return response

    # Make request to join game from database
    join_name = game_database.add_player(join_room, join_name)

    if join_name == None:
        response = jsonify("Error joining room")
        response.status_code = 500
        return response
    
    # Set session token
    session[SESSION_USERNAME] = join_name
    session[SESSION_RO0M] = join_room

    response = jsonify("Successfully joined room %s as user %s" % (join_room, join_name))
    response.status_code = 200
    return response

@games_api.route("/join", methods=['POST'])
def joinGame():
    headers = request.headers
    room_id = headers[ROOM_ID].upper() if ROOM_ID in headers else None
    name = headers[USERNAME] if USERNAME in headers else None

    if room_id == None or name == None:
        response = jsonify("Must provide room_id AND name")
        response.status_code = 400
        return response

    return attempt_join(room_id, name)

@games_api.route("/ping", methods=['GET'])
def pingGame():
    player_name = session[SESSION_USERNAME] if SESSION_USERNAME in session else None
    game_room = session[SESSION_ROOM] if SESSION_ROOM in session else None

    if player_name != None and game_room != None:
        response = jsonify({SESSION_ROOM: game_room, SESSION_USERNAME: player_name})
        response.status_code = 200
        return response
    response = jsonify("You must join a room")
    response.status_code = 401
    return response

