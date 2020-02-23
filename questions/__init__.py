from flask import Blueprint, jsonify, request, session
from database import db_container, ACTIVE_QUESTION_KEY, QUESTION_LIST_KEY
from games import ROOM_ID, USERNAME

questions_api = Blueprint('questions_api', __name__)

@questions_api.route("/<roomId>", methods=['GET', 'POST'])
def handleQuestion(roomId):
    if request.method == 'GET':
        return getQuestionList(roomId)
    elif request.method == 'POST':
        return addNewQuestion(roomId)

@questions_api.route("/<roomId>/<questionId>", methods=['GET'])
def getQuestionOptions(roomId, questionId):
    if not db_container.get_database().room_exists(roomId):
        response = jsonify("Room Id not found")
        response.status_code = 404
        return response
    if not db_container.get_database().question_exists(questionId):
        response = jsonify("Question Id not found")
        response.status_code = 404
        return response
    active_id = db_container.get_database().get_active_question(roomId)
    active_options = db_container.get_database().get_question_options(active_id)
    response = jsonify(active_options)
    response.status_code = 200
    return response

@questions_api.route("/<roomId>/active", methods=['DELETE', 'POST'])
def handleActiveQuestion(roomId):
    if request.method == 'DELETE':
        return clearActiveQuestion(roomId)
    
def clearActiveQuestion(roomId):
    if not db_container.get_database().room_exists(roomId):
        response = jsonify("Room Id not found")
        response.status_code = 404
        return response
    
    db_container.get_database().update_room(roomId, {ACTIVE_QUESTION_KEY: ""})
    response = jsonify("")
    response.status_code = 204
    return response

def getQuestionList(roomId):
    if not db_container.get_database().room_exists(roomId):
        response = jsonify("Room Id not found")
        response.status_code = 404
        return response
    question_list = jsonify(db_container.get_database().get_question_list(roomId))
    question_list.status_code = 200
    return question_list

def addNewQuestion(roomId):
    if not db_container.get_database().room_exists(roomId):
        response = jsonify("Room Id not found")
        response.status_code = 404
        return response
    options = request.json
    questionId = db_container.get_database().make_new_question(options)
    db_container.get_database().update_room(roomId, {ACTIVE_QUESTION_KEY: questionId})
    current_questions = db_container.get_database().get_question_list(roomId)
    db_container.get_database().update_room(roomId, {QUESTION_LIST_KEY: [questionId] + current_questions})

    response = jsonify(questionId)
    response.status_code = 200
    return response

