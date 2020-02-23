from itertools import product
from random import shuffle
from firebase_admin import firestore
import time
import uuid

ROOM_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

ROOM_ID_KEY = "room_id"
PLAYERS_KEY = "players"
TIME_START_KEY = "time_start"
ROOM_STATUS_KEY = "room_status"
ROOM_TYPE_KEY = "room_type"
MAX_PLAYERS_KEY = "max_players"
QUESTION_LIST_KEY = "all_questions"
ACTIVE_QUESTION_KEY = "active_question"

QUESTION_ID_KEY = "question_id"
QUESTION_OPTIONS_KEY = "options"
QUESTION_RESPONSES_KEY = "responses"
RESPONSE_KEY_ID = "selected"

def get_uuid():
    """
    Description:
    Gets a hex GUID for a player token

    Returns:
    String guid identifier for a player token
    """
    return uuid.uuid4().hex

def valid_room_id(room_id):
    """
    Parameters:
    room_id - Id to check

    Description:
    Checks the room id is a string and that the id's length is 4 characters.
    Each character must be one of the approved ROOM_LETTERS (which are [A-Z]). 
    """
    return type(room_id) == str and len(room_id) == 4 and sum([l.upper() in ROOM_LETTERS for l in room_id]) == 4

def room_id_generator():
    """
    Description:
    Arbitrarily iterates through every possible combination of room letters.
    """
    index_1_numbers = [l for l in ROOM_LETTERS]
    index_2_numbers = [l for l in ROOM_LETTERS]
    index_3_numbers = [l for l in ROOM_LETTERS]
    index_4_numbers = [l for l in ROOM_LETTERS]

    shuffle(index_1_numbers)
    shuffle(index_2_numbers)
    shuffle(index_3_numbers)
    shuffle(index_4_numbers)

    for room_numbers in product(index_1_numbers, index_2_numbers, index_3_numbers, index_4_numbers):
        yield "".join(room_numbers)

class DatabaseManager:
    def _get_new_question_id(self):
        qid = get_uuid()
        while self.question_exists(qid):
            qid = get_uuid()
        return qid

    def set_question_response(self, question_id, user_id, response):
        if not self.question_exists(question_id):
            return None
        db = firestore.client()
        db.collection('questions') \
            .document(question_id) \
            .collection(QUESTION_RESPONSES_KEY) \
            .document(user_id).set({RESPONSE_KEY_ID: response})
        return response

    def get_question_options(self, question_id):
        if not self.question_exists(question_id):
            return None
        question_data = self.get_question(question_id)
        options = question_data[QUESTION_OPTIONS_KEY]
        return options

    def get_question_responses(self, question_id):
        if not self.question_exists(question_id):
            return None
        db = firestore.client()
        response_ids = db.collection('questions').document(question_id).collection(QUESTION_RESPONSES_KEY).get()
        question_doc = {el.id : el.to_dict()[RESPONSE_KEY_ID] for el in response_ids}
        return question_doc
        

    def make_new_question(self, options):
        new_id = self._get_new_question_id()
        empty_question = {
            QUESTION_ID_KEY: new_id,
            QUESTION_OPTIONS_KEY: options,
            TIME_START_KEY: time.time(),
            #QUESTION_RESPONSES_KEY: {}
        }

        if new_id == None:
            return None
        
        db = firestore.client()
        rooms_ref = db.collection('questions')
        rooms_ref.document(new_id).set(empty_question)
        return new_id

    def get_question(self, question_id):
        if not self.question_exists(question_id):
            return None
        db = firestore.client()
        question_doc = db.collection('questions').document(question_id).get()
        question_data = question_doc.to_dict()

        return question_data

    def question_exists(self, question_id):
        db = firestore.client()
        questions_ref = db.collection('questions')
        return questions_ref.document(question_id).get().exists

    def get_active_question(self, room_id):
        if not self.room_exists(room_id):
            return None
        db = firestore.client()
        room_data = self.get_room(room_id)
        return room_data[ACTIVE_QUESTION_KEY]

    def get_question_list(self, room_id):
        if not self.room_exists(room_id):
            return []
        db = firestore.client()
        room_data = self.get_room(room_id)
        return room_data[QUESTION_LIST_KEY]
    
    def room_exists(self, room_id):
        """
        Parameters:
        room_id - id to check for room

        Description:
        Checks if a room with a given id exists

        Returns:
        True if the room exists, false otherwise
        """
        db = firestore.client()
        rooms_ref = db.collection('rooms')
        return rooms_ref.document(room_id).get().exists

    def _get_new_id(self):
        """
        Description:
        Gets a new, available id
        """
        id_generator = room_id_generator()

        for room_id in id_generator:
            if not self.room_exists(room_id):
                return room_id
        return None
    
    def get_room(self, room_id):
        """
        Parameters:
        room_id - Identity of the room

        Description:
        Gets the data associated with the given room.
        
        Returns:
        the room data associated with a room or None if no room exists
        """
        if self.room_exists(room_id):
            db = firestore.client()
            room_doc = db.collection('rooms').document(room_id).get()
            room_data = room_doc.to_dict()

            return room_data
        return None

    def is_player_in_room(self, room_id, player_id):
        """
        Parameters:
        room_id - Identity of the room
        player_id - Identify of the player

        Description:
        Checks if a given player is in a room.

        Returns: 
        True if the player is in the room, false if the player is not in the room.
        This will return None if the room does not exist or if there is another error. 
        """
        if not self.room_exists(room_id):
            return None
        return player_id in self.get_players(room_id)        

    def add_player(self, room_id, player_id):
        """
        Parameters:
        room_id - Identity of the room
        player_id - Identify of the player

        Description:
        Adds a player to a given room. Will check to ensure that that player
        is not already a member of that room. 

        Returns:
        If the player with the given ID
        is already a member of the room or if the room is already at max
        players this will return None. If any other error occurs, this will return None.

        If the player successfully joins the room, this will return the player's name
        """
        if not self.room_exists(room_id):
            return None
        if self.is_player_in_room(room_id, player_id) or self.is_room_full(room_id):
            return None

        current_players = self.get_players(room_id)
        new_players = current_players + [player_id]
        self.update_room(room_id, {PLAYERS_KEY: new_players})
        return player_id

    def _delete_collection(self, coll_ref, batch_size):
        docs = coll_ref.limit(batch_size).stream()
        deleted = 0

        for doc in docs:
            print(u'Deleting doc {} => {}'.format(doc.id, doc.to_dict()))
            doc.reference.delete()
            deleted = deleted + 1

        if deleted >= batch_size:
            return self._delete_collection(coll_ref, batch_size)

    def update_room(self, room_id, update_data):
        """
        Parameters:
        room_id - Identity of the room
        update_data - Data to update in the room object as dictionary

        Description:
        Updates that data associated with a room_id.
        
        Returns:
        the room data associated with a room after the update or None if
        the room id is invalid
        """
        if not self.room_exists(room_id):
            return None
        db = firestore.client()
        db.collection('rooms').document(room_id).update(update_data)
        return self.get_room(room_id)
    
    def delete_room(self, room_id):
        """
        Parameters:
        room_id - Identity of the room

        Description:
        Deletes a room with a given id.
        
        Returns:
        True if the room was successfully deleted, False if the room does not exist or an error ocurred. 
        """
        if self.room_exists(room_id):
            db = firestore.client()
            db.collection('rooms').document(room_id).delete()
            return True
        return False

    def list_rooms(self):
        """
        Description:
        Gets the list of all room ids stored in the database.

        Returns:
        List of all rooms or None if an error ocurred.
        """
        db = firestore.client()
        rooms_ref = db.collection('rooms')
        rooms = [doc.id for doc in rooms_ref.get()]

        return rooms

    def is_room_full(self, room_id):
        """
        Parameters:
        room_id - Id of the room to check

        Description:
        Checks if the number of player in a room is greater than or 
        equal to the max number of players

        Returns:
        True if the room is full, false otherwise. If there is an error
        if the room does not exist, this will return None.
        """
        if not self.room_exists(room_id):
            return None
        room_data = self.get_room(room_id)
        max_players = room_data[MAX_PLAYERS_KEY]
        num_players = self.get_num_player_in_room(room_id)

        return num_players >= max_players

    def get_num_player_in_room(self, room_id):
        """
        Parameters:
        room_id - Id of the room to check

        Description:
        Gets the number of players in a room.

        Returns:
        Number of players in a given room. If the room does not exist or another error
        occurs, this will return none.
        """
        return len(self.get_players(room_id)) if self.room_exists(room_id) else None

    def get_players(self, room_id):
        """
        Parameters:
        room_id - Id of the room to check

        Description:
        Gets all the players in a given room.

        Returns:
        List of all players in a room. Will be an empty list if the room is empty.
        Will return None if something went wrong.
        """
        if not self.room_exists(room_id):
            return None
        return self.get_room(room_id)[PLAYERS_KEY]

    def create_room(self):
        """
        Description:
        Creates a room and returns the id associated with the room.
        
        Returns:
        The id of the newly created room or None if a new room cannot be created.
        """
        new_id = self._get_new_id()
        empty_room = {
            ROOM_ID_KEY: new_id,
            ROOM_STATUS_KEY: "lobby",
            ROOM_TYPE_KEY: "game",
            TIME_START_KEY: time.time(),
            MAX_PLAYERS_KEY: 4,
            PLAYERS_KEY: [],
            QUESTION_LIST_KEY: [],
            ACTIVE_QUESTION_KEY: "",
        }

        if new_id == None:
            return None
        
        db = firestore.client()
        rooms_ref = db.collection('rooms')
        rooms_ref.document(new_id).set(empty_room)
        return new_id

class TestDatabaseManager:
    def __init__(self):
        self.rooms = dict()

    def _reset(self):
        self.rooms = dict()

    def room_exists(self, room_id):
        """
        Parameters:
        room_id - id to check for room
        Description:
        Checks if a room with a given id exists
        Returns:
        True if the room exists, false otherwise
        """
        return room_id in self.rooms

    def _get_new_id(self):
        """
        Description:
        Gets a new, available id
        """
        id_generator = room_id_generator()

        for room_id in id_generator:
            if not self.room_exists(room_id):
                return room_id
        return None
    
    def get_room(self, room_id):
        """
        Parameters:
        room_id - Identity of the room
        Description:
        Gets the data associated with the given room.
        
        Returns:
        the room data associated with a room or None if no room exists
        """
        if self.room_exists(room_id):
            return self.rooms[room_id]
        return None

    def is_player_in_room(self, room_id, player_id):
        """
        Parameters:
        room_id - Identity of the room
        player_id - Identify of the player
        Description:
        Checks if a given player is in a room.
        Returns: 
        True if the player is in the room, false if the player is not in the room.
        This will return None if the room does not exist or if there is another error. 
        """
        if not self.room_exists(room_id):
            return None
        current_players = self.get_players(room_id)
        return player_id in current_players        

    def add_player(self, room_id, player_id):
        """
        Parameters:
        room_id - Identity of the room
        player_id - Identify of the player
        Description:
        Adds a player to a given room. Will check to ensure that that player
        is not already a member of that room. 
        Returns:
        If the player with the given ID
        is already a member of the room or if the room is already at max
        players this will return None. If any other error occurs, this will return None.
        If the player successfully joins the room, this will return the player's name
        """
        if not self.room_exists(room_id):
            return None
        if self.is_player_in_room(room_id, player_id) or self.is_room_full(room_id):
            return None

        current_players = self.get_players(room_id)
        new_players = current_players + [player_id]
        self.update_room(room_id, {PLAYERS_KEY: new_players})
        return player_id

    def update_room(self, room_id, update_data):
        """
        Parameters:
        room_id - Identity of the room
        update_data - Data to update in the room object as dictionary
        Description:
        Updates that data associated with a room_id.
        
        Returns:
        the room data associated with a room after the update or None if
        the room id is invalid
        """
        if not self.room_exists(room_id):
            return None
        for elem in update_data:
            self.rooms[room_id][elem] = update_data[elem]
        return self.rooms[room_id]
    
    def delete_room(self, room_id):
        """
        Parameters:
        room_id - Identity of the room
        Description:
        Deletes a room with a given id.
        
        Returns:
        True if the room was successfully deleted, False if the room does not exist or an error ocurred. 
        """
        if self.room_exists(room_id):
            del self.rooms[room_id]
            return True
        return False

    def list_rooms(self):
        """
        Description:
        Gets the list of all room ids stored in the database.
        Returns:
        List of all rooms or None if an error ocurred.
        """
        return list(self.rooms.keys())

    def is_room_full(self, room_id):
        """
        Parameters:
        room_id - Id of the room to check
        Description:
        Checks if the number of player in a room is greater than or 
        equal to the max number of players
        Returns:
        True if the room is full, false otherwise. If there is an error
        if the room does not exist, this will return None.
        """
        if not self.room_exists(room_id):
            return None
        room_data = self.get_room(room_id)
        max_players = room_data[MAX_PLAYERS_KEY]
        num_players = self.get_num_player_in_room(room_id)

        return num_players >= max_players

    def get_num_player_in_room(self, room_id):
        """
        Parameters:
        room_id - Id of the room to check
        Description:
        Gets the number of players in a room.
        Returns:
        Number of players in a given room. If the room does not exist or another error
        occurs, this will return none.
        """
        return len(self.get_players(room_id)) if self.room_exists(room_id) else None


    def get_players(self, room_id):
        """
        Parameters:
        room_id - Id of the room to check
        Description:
        Gets all the players in a given room.
        Returns:
        List of all players in a room. Will be an empty list if the room is empty.
        Will return None if something went wrong.
        """
        if not self.room_exists(room_id):
            return None
        return self.get_room(room_id)[PLAYERS_KEY]

    def create_room(self):
        """
        Description:
        Creates a room and returns the id associated with the room.
        
        Returns:
        The id of the newly created room or None if a new room cannot be created.
        """
        new_id = self._get_new_id()
        empty_room = {
            ROOM_ID_KEY: new_id,
            ROOM_STATUS_KEY: "lobby",
            ROOM_TYPE_KEY: "game",
            TIME_START_KEY: str(time.time()),
            MAX_PLAYERS_KEY: 4,
            PLAYERS_KEY: [],
        }

        if new_id == None:
            return None
        
        self.rooms[new_id] = empty_room
        return new_id

class DatabaseContainer:
    def __init__(self):
        self.database = DatabaseManager()

    def get_database(self):
        return self.database

    def set_test_mode(self):
        self.database = TestDatabaseManager()

db_container = DatabaseContainer()
