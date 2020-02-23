from itertools import product
from random import shuffle
import time

ROOM_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

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
        if self.room_exists(room_id):
            for elem in update_data:
                self.rooms[room_id][elem] = update_data[elem]
            return self.rooms[room_id]
        return None
            
    
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

    def create_room(self):
        """
        Description:
        Creates a room and returns the id associated with the room.
        
        Returns:
        The id of the newly created room or None if a new room cannot be created.
        """
        new_id = self._get_new_id()
        empty_room = {
            "room_id": new_id,
            "room_status": "lobby",
            "room_type": "game",
            "create_time": str(time.time())
        }

        if new_id == None:
            return None
        
        self.rooms[new_id] = empty_room
        return new_id
        
game_database = DatabaseManager()
