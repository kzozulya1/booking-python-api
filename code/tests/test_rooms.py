import unittest
import os
import json
from ..app import get_app, db

#import logging
#UM_LOG_FILENAME = 'debug.log'
#logging.basicConfig(filename=UM_LOG_FILENAME,level=logging.DEBUG)


class RoomsTest(unittest.TestCase):
  '''
  Rooms Test Case
  '''
  def setUp(self):
    '''
    Test Setup
    '''
    self.app = get_app("testing")
    self.client = self.app.test_client
    self.room = {
      'address': 'Moscow, Arbat 12',
      'description': 'Very comfortable room',
      'owner_id' : 0, # will be replaced later
      'body_capacity': 2,
      'allow_smoking': 0,
      'allow_parking': 1,
      'allow_children': 1,
      'img_main': 'image_main.jpg',
      'img_1': 'image_1.jpg',
      'img_2': 'image_2.jpg',
      'img_3': 'image_3.jpg'
    }
    
    self.user = {
      'name': 'Nikola Lenz',
      'email': 'n.lenz@gmail.com',
      'password': 'p#$%^assw0rd!'
    }

    with self.app.app_context():
      # create all tables
      db.create_all()
      
  def _create_user_and_get_token_and_id(self):
    '''
    Helper routine - create user and get his id and jwt token
    '''
    res = self.client().post('/api/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    json_data = json.loads(res.data)
    self.assertTrue(json_data.get('jwt_token'))
    self.assertEqual(res.status_code, 201)
    api_token = json_data.get('jwt_token')
    
    res = self.client().get('/api/v1/users/me', headers={'Content-Type': 'application/json', 'api-token': api_token})
    json_data = json.loads(res.data)
    self.assertEqual(res.status_code,200)
    self.assertTrue(json_data['id'])
    return {'user_id': json_data['id'], 'api_token': api_token}
    
  
  def test_room_creation(self):
    ''' 
    test room creation
    '''
    user_data = self._create_user_and_get_token_and_id()

    res = self.client().post('/api/v1/rooms/', headers={'Content-Type': 'application/json', 'api-token': user_data['api_token']}, data=json.dumps(self.room))
    json_data = json.loads(res.data)
    self.assertEqual(res.status_code, 201)
    self.assertEqual(json_data['address'], self.room['address'])
    self.assertEqual(json_data['description'], self.room['description'])
    self.assertEqual(json_data['owner_id'], user_data['user_id'])
    self.assertEqual(json_data['body_capacity'], self.room['body_capacity'])
    self.assertEqual(json_data['allow_smoking'], self.room['allow_smoking'])
    self.assertEqual(json_data['allow_parking'], self.room['allow_parking'])
    self.assertEqual(json_data['allow_children'], self.room['allow_children'])
    self.assertEqual(json_data['img_main'], self.room['img_main'])
    self.assertEqual(json_data['img_1'], self.room['img_1'])
    self.assertEqual(json_data['img_2'], self.room['img_2'])
    self.assertEqual(json_data['img_3'], self.room['img_3'])
    
  def test_room_get_all(self):
    ''' 
    test room get all rooms
    '''
    user_data = self._create_user_and_get_token_and_id()

    res = self.client().post('/api/v1/rooms/', headers={'Content-Type': 'application/json', 'api-token': user_data['api_token']}, data=json.dumps(self.room))
    json_data = json.loads(res.data)
    self.assertEqual(res.status_code, 201)
    
    res = self.client().get('/api/v1/rooms/', headers={'Content-Type': 'application/json'})
    json_list = json.loads(res.data)
    self.assertEqual(res.status_code, 200)
    room = json_list.pop()
    
    self.assertEqual(room['address'], self.room['address'])
    self.assertEqual(room['description'], self.room['description'])
    self.assertEqual(room['owner_id'], user_data['user_id'])
    
  def test_room_get_by_id(self):
    ''' 
    test room get all rooms
    '''
    user_data = self._create_user_and_get_token_and_id()

    res = self.client().post('/api/v1/rooms/', headers={'Content-Type': 'application/json', 'api-token': user_data['api_token']}, data=json.dumps(self.room))
    json_data = json.loads(res.data)
    self.assertEqual(res.status_code, 201)
    
    res = self.client().get('/api/v1/rooms/' + str(json_data.get('id')), headers={'Content-Type': 'application/json'})
    json_data = json.loads(res.data)
    self.assertEqual(res.status_code, 200)
    
    self.assertEqual(json_data['address'], self.room['address'])
    self.assertEqual(json_data['description'], self.room['description'])
    self.assertEqual(json_data['owner_id'], user_data['user_id'])    
    
  def test_update_room(self):
    ''' 
    test room update
    '''
    user_data = self._create_user_and_get_token_and_id()

    res = self.client().post('/api/v1/rooms/', headers={'Content-Type': 'application/json', 'api-token': user_data['api_token']}, data=json.dumps(self.room))
    json_data = json.loads(res.data)
    self.assertEqual(res.status_code, 201)
    
    room_id = json_data.get('id')
    new_room = {
        'address': 'Moscow, Arbat 1222',
        'description': 'Very comfortable room 2',
        'body_capacity': 3,
        'allow_smoking': 1,
        'allow_parking': 0,
        'allow_children': 0,
        'img_main': 'img2_main.jpg',
        'img_1': 'img2_1.jpg',
        'img_2': 'img2_2.jpg',
        'img_3': 'img2_3.jpg'
    }
    res = self.client().put('/api/v1/rooms/' + str(room_id), headers={'Content-Type': 'application/json', 'api-token': user_data['api_token']}, data=json.dumps(new_room))
    room_upd = json.loads(res.data)
    self.assertEqual(res.status_code, 200)
    
    [self.assertEqual(room_upd.get(key), new_room.get(key) ) for key in new_room.keys()]
    
    res = self.client().get('/api/v1/rooms/' + str(room_upd.get('id')), headers={'Content-Type': 'application/json'})
    json_data = json.loads(res.data)
    self.assertEqual(res.status_code, 200)
    
    [self.assertEqual(json_data.get(key), new_room.get(key) ) for key in new_room.keys()]
    
  def test_delete_room(self):
    '''
    Delete room
    '''
    user_data = self._create_user_and_get_token_and_id()

    res = self.client().post('/api/v1/rooms/', headers={'Content-Type': 'application/json', 'api-token': user_data['api_token']}, data=json.dumps(self.room))
    json_data = json.loads(res.data)
    self.assertEqual(res.status_code, 201)  
    room_id = json_data.get('id')
    
    res = self.client().delete('/api/v1/rooms/' + str(room_id), headers={'Content-Type': 'application/json', 'api-token': user_data['api_token']})
    self.assertEqual(res.status_code, 204)
    
  def test_delete_room_not_existed_room_id(self):
    '''
    Delete room when room id is fake
    '''
    user_data = self._create_user_and_get_token_and_id()
    
    res = self.client().delete('/api/v1/rooms/333', headers={'Content-Type': 'application/json', 'api-token': user_data['api_token']})
    self.assertEqual(res.status_code, 404)    
  
    
  def tearDown(self):
    '''
    Tear Down
    '''
    with self.app.app_context():
      db.session.remove()
      db.drop_all()

if __name__ == "__main__":
  unittest.main() 