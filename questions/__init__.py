from flask import Blueprint, jsonify, request, session
from database import db_container

questions_api = Blueprint('questions_api', __name__)

@questions_api.route("/<roomId>", methods=['GET', 'POST'])
def handleQuestion(roomId):
    if request.method == 'GET':
        return getQuestionList(roomId)
    elif request.method == 'POST':
        return addNewQuestion(roomId)

@questions_api.route("/<roomId>/<questionId>", methods=['GET'])
def getQuestionOptions(roomId, questionId):
    pass

@questions_api.route("/<roomId>/active", methods=['DELETE', 'POST'])
def handleActiveQuestion(roomId):
    if request.method == 'DELETE':
        return clearActiveQuestion(roomId)
    elif request.method == 'POST':
        return setActiveQuestion(roomId)

@questions_api.route("/<roomId>/responses/<questionId>", methods=['GET', 'POST'])
def handlequestionResponse(roomId, questionId):
    if request.method == 'GET':
        return getQuestionResponses(roomId, questionId)
    elif request.method == 'POST':
        return respondToQuestion(roomId, questionId)

def getQuestionResponses(roomId, questionId):
    pass

def respondToQuestion(roomId, questionId):
    pass

def clearActiveQuestion(roomId):
    pass

def setActiveQuestion(roomId):
    pass

def getQuestionList(roomId):
    pass

def addNewQuestion(roomId):
    pass
