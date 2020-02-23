from itertools import product
from random import shuffle
import time
import uuid

ROOM_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

ROOM_ID_KEY = "room_id"
PLAYERS_KEY = "players"
TIME_START_KEY = "time_start"
ROOM_STATUS_KEY = "room_status"
ROOM_TYPE_KEY = "room_type"
MAX_PLAYERS_KEY = "max_players"

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
        
game_database = DatabaseManager()
