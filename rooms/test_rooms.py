import os
import unittest

from main import app
from database import game_database, valid_room_id

class BasicTests(unittest.TestCase):
 
    ############################
    #### setup and teardown ####
    ############################
 
    # executed prior to each test
    def setUp(self):
        # app.config['TESTING'] = True
        # app.config['WTF_CSRF_ENABLED'] = False
        # app.config['DEBUG'] = False
        # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
        #     os.path.join(app.config['BASEDIR'], TEST_DB)
        self.app = app.test_client()
        game_database._reset()

        self.assertEqual(app.debug, False)
 
    # executed after each test
    def tearDown(self):
        pass

    def test_rooms(self):
        result_get_empty = self.app.get('/rooms/')

        # assert the status code of the response
        self.assertEqual(result_get_empty.status_code, 200) 
        self.assertEqual(result_get_empty.json, [])

        result_post_first = self.app.post('/rooms/')
        self.assertEqual(result_post_first.status_code, 201)
        self.assertTrue(valid_room_id(result_post_first.json))

        result_get_one = self.app.get('/rooms/')
        self.assertEqual(result_get_one.status_code, 200)
        self.assertEqual(len(result_get_one.json), 1)
    
    def test_room_get_id(self):
        rooms_get = self.app.get('/rooms/ASDF')
        self.assertEqual(rooms_get.status_code, 404)

        room_post = self.app.post('/rooms/')
        self.assertEqual(room_post.status_code, 201)
        self.assertTrue(valid_room_id(room_post.json))
        room_id = room_post.json

        rooms_get = self.app.get('/rooms/%s' % room_id)
        self.assertEqual(rooms_get.status_code, 200)
        self.assertEqual(type(rooms_get.json), dict)

    def test_create_many_rooms(self):
        result_get_empty = self.app.get('/rooms/')
        self.assertEqual(result_get_empty.status_code, 200) 
        self.assertEqual(result_get_empty.json, [])

        for rooms_created in range(1, 100):
            room_post = self.app.post('/rooms/')
            self.assertEqual(room_post.status_code, 201)
            self.assertTrue(valid_room_id(room_post.json))

            rooms_get = self.app.get('/rooms/')
            self.assertEqual(rooms_get.status_code, 200)
            self.assertEqual(len(rooms_get.json), rooms_created)
    
    def test_delete_room(self):
        room_post = self.app.post('/rooms/')
        self.assertEqual(room_post.status_code, 201)
        self.assertTrue(valid_room_id(room_post.json))
        room_id = room_post.json

        rooms_get = self.app.get('/rooms/')
        self.assertEqual(rooms_get.status_code, 200)
        self.assertEqual(rooms_get.json[0], room_id)

        rooms_delete = self.app.delete('/rooms/%s' % room_id)
        self.assertEqual(rooms_delete.status_code, 204)

        rooms_get = self.app.get('/rooms/')
        self.assertEqual(rooms_get.status_code, 200)
        self.assertEqual(rooms_get.json, [])
        
        rooms_delete = self.app.delete('/rooms/%s' % room_id)
        self.assertEqual(rooms_delete.status_code, 404)


if __name__ == '__main__':
    unittest.main()
