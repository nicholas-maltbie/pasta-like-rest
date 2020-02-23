from flask import Blueprint, jsonify, request
from database import db_container, ACTIVE_QUESTION_KEY

rooms_api = Blueprint('rooms_api', __name__)

@rooms_api.route("/", methods=['GET', 'POST'])
def handleGetCreate():
    if request.method == 'GET':
        return listRooms()
    elif request.method == 'POST':
        return createRoom()

def listRooms():
    room_list = db_container.get_database().list_rooms()
    resp = jsonify(room_list)
    resp.status_code = 200
    return resp

def createRoom():
    room_id = db_container.get_database().create_room()
    if room_id == None:
        response =  jsonify("Server error creating room")
        response.status_code = 500
        return response
    resp = jsonify(room_id)
    resp.status_code = 201
    return resp

@rooms_api.route("/<roomId>/active", methods=['GET'])
def getActiveQuestion(roomId):
    roomData = db_container.get_database().get_room(roomId)
    # Check to ensure room exists
    if roomData == None:
        response =  jsonify("Room not found")
        response.status_code = 404
        return response
    
    response = jsonify(roomData[ACTIVE_QUESTION_KEY])
    response.status_code = 200
    return response
    

@rooms_api.route("/<roomId>", methods=['GET', 'PATCH', 'DELETE'])
def handleRoom(roomId=None):
    if request.method == 'GET':
        return getRoomData(roomId)
    elif request.method == 'PATCH':
        return updateRoom(roomId)
    elif request.method == 'DELETE':
        return deleteRoom(roomId)

def updateRoom(roomId):
    roomData = db_container.get_database().get_room(roomId)
    # Check to ensure room exists
    if roomData == None:
        response =  jsonify("Room not found")
        response.status_code = 404
        return response

    if not request.headers['Content-Type'] == 'application/json':
        response =  jsonify("Invalid update data, must be json")
        response.status_code = 415
        return response

    # Update room
    updated_room = db_container.get_database().update_room(roomId, request.json)

    if updated_room == None:
        response =  jsonify("Server error updating room")
        response.status_code = 500
        return response

    resp = jsonify(updated_room)
    resp.status_code = 200
    return resp

def deleteRoom(roomId):
    # Check to ensure room exists
    if not db_container.get_database().room_exists(roomId):
        response =  jsonify("Room Id not found")
        response.status_code = 404
        return response

    # Delete room
    response = db_container.get_database().delete_room(roomId)

    if response == True:
        response =  jsonify("Deleted room with id %s successfully" % roomId)
        response.status_code = 204
        return response
    response =  jsonify("Server error deleting room")
    response.status_code = 500
    return response

def getRoomData(roomId):
    roomData = db_container.get_database().get_room(roomId)
    # Check to ensure room exists
    if roomData == None:
        response =  jsonify("Room not found")
        response.status_code = 404
        return response
    
    resp = jsonify(roomData)
    resp.status_code = 200
    return resp
