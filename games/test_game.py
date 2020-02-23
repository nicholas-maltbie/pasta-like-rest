import os
import unittest

from main import app
from database import game_database, valid_room_id
from games import ROOM_ID, USERNAME

class BasicTests(unittest.TestCase):
 
    ############################
    #### setup and teardown ####
    ############################
 
    # executed prior to each test
    def setUp(self):
        app.secret_key = "test-key"
        # app.config['TESTING'] = True
        # app.config['WTF_CSRF_ENABLED'] = False
        # app.config['DEBUG'] = False
        # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
        #     os.path.join(app.config['BASEDIR'], TEST_DB)
        self.app = app.test_client()
        game_database._reset()

        self.assertEqual(app.debug, False)

        result_post_first = self.app.post('/rooms/')
        self.room_id = result_post_first.json
 
    # executed after each test
    def tearDown(self):
        pass

    def test_ping(self):
        result_ping = self.app.get('/games/ping')

        # assert the status code of the response
        self.assertEqual(result_ping.status_code, 401)

    def test_join_empty(self):
        result_join = self.app.post('/games/join')
        self.assertEqual(result_join.status_code, 400)

    def test_join_only_user(self):
        result_join = self.app.post('/games/join', headers={USERNAME: "user"})
        self.assertEqual(result_join.status_code, 400)

    def test_join_only_room(self):
        result_join = self.app.post('/games/join', headers={ROOM_ID: self.room_id})
        self.assertEqual(result_join.status_code, 400)
    
    def test_join_invalid_room(self):
        result_join = self.app.post('/games/join', headers={USERNAME: "user", ROOM_ID: "A"})
        self.assertEqual(result_join.status_code, 400)
        
    def test_join_invalid_name(self):
        result_join = self.app.post('/games/join', headers={USERNAME: "", ROOM_ID: "A"})
        self.assertEqual(result_join.status_code, 400)

    def test_join_no_room(self):
        new_id = game_database._get_new_id()
        result_join = self.app.post('/games/join', headers={USERNAME: "user", ROOM_ID: new_id})
        self.assertEqual(result_join.status_code, 404)

    def test_join_correct(self):
        result_join = self.app.post('/games/join', headers={USERNAME: "user", ROOM_ID: self.room_id})
        self.assertEqual(result_join.status_code, 200)

    def test_join_full(self):
        suffix = 1
        while not game_database.is_room_full(self.room_id):
            test_client = app.test_client()
            result_join = test_client.post('/games/join', headers={USERNAME: "user" + str(suffix), ROOM_ID: self.room_id})
            self.assertEqual(result_join.status_code, 200)
            suffix += 1
        
        result_join = self.app.post('/games/join', headers={USERNAME: "user", ROOM_ID: self.room_id})
        self.assertEqual(result_join.status_code, 401)

    def test_rejoin(self):
        test_client = app.test_client()
        name = "user"
        result_join = test_client.post('/games/join', headers={USERNAME: name, ROOM_ID: self.room_id})
        self.assertEqual(result_join.status_code, 200)

        result_join = test_client.post('/games/join', headers={USERNAME: name, ROOM_ID: self.room_id})
        self.assertEqual(result_join.status_code, 200)

        all_players = game_database.get_players(self.room_id)
        self.assertEqual(all_players, [name])

    def test_name_taken(self):
        test_client1 = app.test_client()
        test_client2 = app.test_client()
        result_join = test_client1.post('/games/join', headers={USERNAME: "user-1", ROOM_ID: self.room_id})
        self.assertEqual(result_join.status_code, 200)
        result_join = test_client2.post('/games/join', headers={USERNAME: "user-1", ROOM_ID: self.room_id})
        self.assertEqual(result_join.status_code, 401)
        self.assertEqual(result_join.json, "Name is taken")


if __name__ == '__main__':
    unittest.main()
