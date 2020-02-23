from flask import Blueprint, jsonify, request, session
from database import db_container, ACTIVE_QUESTION_KEY
from games import ROOM_ID, USERNAME

responses_api = Blueprint('responses_api', __name__)

@responses_api.route("/<questionId>", methods=['GET', 'POST'])
def handlequestionResponse(questionId):
    if request.method == 'GET':
        return getQuestionResponses(questionId)
    elif request.method == 'POST':
        return respondToQuestion(questionId)

def getQuestionResponses(questionId):
    if not db_container.get_database().question_exists(questionId):
        response = jsonify("Question Id not found")
        response.status_code = 404
        return response
    responses = jsonify(db_container.get_database().get_question_responses(questionId))
    responses.status_code = 200
    return responses

def respondToQuestion(questionId):
    headers = request.headers
    userId = headers[USERNAME]
    answer_data = request.json
    if not db_container.get_database().question_exists(questionId):
        response = jsonify("Question Id not found")
        response.status_code = 404
        return response
    result = db_container.get_database().set_question_response(questionId, userId, answer_data)
    responses = jsonify(result)
    responses.status_code = 200
    return responses