import unittest
import os
import json
import datetime
from ..app import get_app, db

#import logging
#UM_LOG_FILENAME = 'debug.log'
#logging.basicConfig(filename=UM_LOG_FILENAME,level=logging.DEBUG)


class ReservationsTest(unittest.TestCase):
  '''
  Reservations Test Case
  '''
  def setUp(self):
    '''
    Test Setup
    '''
    self.app = get_app("testing")
    self.client = self.app.test_client
    self.reservation = {
      'room_id': 0,#will be replaced later
      'book_from': datetime.datetime(2018,12,10,12,0,0).strftime("%Y-%m-%d %H:%M:%S"),
      'book_to': datetime.datetime(2018,12,21,10,0,0).strftime("%Y-%m-%d %H:%M:%S"),
      'notes': 'Gratzie'
    }
    
    self.room = {
      'address': 'Moscow, Arbat 12',
      'description': 'Very comfortable room',
      'body_capacity': 2,
      'allow_smoking': 0,
      'allow_parking': 1,
      'allow_children': 1
    }
    
    self.user = {
      'name': 'Tester Tester 1',
      'email': 'tester@gmail.com',
      'password': 'passw0rd!@#$'
    }

    with self.app.app_context():
      # create all tables
      db.create_all()
      
  def _create_user_and_get_token_and_id(self):
    '''
    Create user and get his id and jwt token
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
    
  def _create_room_and_get_id(self, api_token):
    '''
    Create room for user and get room's id
    '''
    res = self.client().post('/api/v1/rooms/', headers={'Content-Type': 'application/json', 'api-token': api_token}, data=json.dumps(self.room))
    json_data = json.loads(res.data)
    self.assertEqual(res.status_code, 201)
    self.assertTrue(json_data['id'])
    return json_data['id']
    
  
  def test_reservation_create(self):
    '''
    test room creation
    '''
    user_data = self._create_user_and_get_token_and_id()
    room_id = self._create_room_and_get_id(user_data['api_token'])
    
    res = self.client().post('/api/v1/reservations/room/' + str(room_id), headers={'Content-Type': 'application/json', 'api-token': user_data['api_token']}, data=json.dumps(self.reservation))
    json_data = json.loads(res.data)
    
    self.assertEqual(res.status_code, 201)
    
    #[self.assertEqual(json_data.get(key), self.reservation.get(key)) for key in self.reservation.keys() if key != 'room_id']
    self.assertEqual(json_data.get('room_id'), room_id)
    self.assertEqual(json_data.get('book_from'), '2018-12-10T12:00:00+00:00')
    self.assertEqual(json_data.get('book_to'),   '2018-12-21T10:00:00+00:00')
    self.assertEqual(json_data.get('notes'),   self.reservation.get('notes'))
  
  
  def test_integrity_check(self):
    '''
    Create user + room
    Create reservation
    Delete user and check that room and reservation were erased as well
    '''
    user_data = self._create_user_and_get_token_and_id()
    room_id = self._create_room_and_get_id(user_data['api_token'])
    
    res = self.client().post('/api/v1/reservations/room/' + str(room_id), headers={'Content-Type': 'application/json', 'api-token': user_data['api_token']}, data=json.dumps(self.reservation))
    self.assertEqual(res.status_code, 201)
    
    #remove user
    res = self.client().delete('/api/v1/users/me', headers={'Content-Type': 'application/json','api-token': user_data['api_token']})
    self.assertTrue(res.status_code,204)
    
    #check room was removed
    res = self.client().get('/api/v1/rooms/' + str(room_id), headers={'Content-Type': 'application/json'})
    self.assertEqual(res.status_code, 404)
    
    #check reservation was removed
    res = self.client().get('/api/v1/reservations/room/' + str(room_id), headers={'Content-Type': 'application/json'})
    self.assertEqual(res.status_code,200)
    json_reservation_list = json.loads(res.data)
    self.assertEqual(len(json_reservation_list),0)
    
    
  def test_get_all_reservations_for_room(self):
    '''
    Create user and room, add reservation and get it from db for 
    specified room id
    '''
    user_data = self._create_user_and_get_token_and_id()
    room_id = self._create_room_and_get_id(user_data['api_token'])
    
    res = self.client().post('/api/v1/reservations/room/' + str(room_id), headers={'Content-Type': 'application/json', 'api-token': user_data['api_token']}, data=json.dumps(self.reservation))
    self.assertEqual(res.status_code, 201)
    
    
    res = self.client().get('/api/v1/reservations/room/' + str(room_id), headers={'Content-Type': 'application/json'})
    self.assertEqual(res.status_code,200)
    json_reservation_list = json.loads(res.data)
    reservation = json_reservation_list.pop()
    
    self.assertEqual(reservation.get('room_id'),   room_id)
    self.assertEqual(reservation.get('book_from'), '2018-12-10T12:00:00+00:00')
    self.assertEqual(reservation.get('book_to'),   '2018-12-21T10:00:00+00:00')
    self.assertEqual(reservation.get('notes'),     self.reservation.get('notes'))
    
  def test_update_reservation(self):
    '''
    Update a reservation
    '''    
    user_data = self._create_user_and_get_token_and_id()
    room_id = self._create_room_and_get_id(user_data['api_token'])
    
    res = self.client().post('/api/v1/reservations/room/' + str(room_id), headers={'Content-Type': 'application/json', 'api-token': user_data['api_token']}, data=json.dumps(self.reservation))
    self.assertEqual(res.status_code, 201)
    reserv_data = json.loads(res.data)
    self.assertTrue(reserv_data['id'])
    
    new_reserv_data = {
        'book_from': datetime.datetime(2018,2,10,12,0,0).strftime("%Y-%m-%d %H:%M:%S"),
        'book_to': datetime.datetime(2018,2,21,10,0,0).strftime("%Y-%m-%d %H:%M:%S"),
        'notes': 'Note1'
    }
    
    res = self.client().put('/api/v1/reservations/' + str(reserv_data['id']), headers={'Content-Type': 'application/json', 'api-token': user_data['api_token']}, data=json.dumps(new_reserv_data))
    upd_data = json.loads(res.data)
    self.assertEqual(res.status_code,200)
    self.assertEqual(upd_data.get('book_from'), '2018-02-10T12:00:00+00:00')
    self.assertEqual(upd_data.get('book_to'),   '2018-02-21T10:00:00+00:00')
    self.assertEqual(upd_data.get('notes'),     new_reserv_data.get('notes'))
    
  def test_delete_reservation(self):
    '''
    Delete a reservation
    '''    
    user_data = self._create_user_and_get_token_and_id()
    room_id = self._create_room_and_get_id(user_data['api_token'])
    
    res = self.client().post('/api/v1/reservations/room/' + str(room_id), headers={'Content-Type': 'application/json', 'api-token': user_data['api_token']}, data=json.dumps(self.reservation))
    self.assertEqual(res.status_code, 201)
    reserv_data = json.loads(res.data)
    self.assertTrue(reserv_data['id'])
    
    res = self.client().delete('/api/v1/reservations/' + str(reserv_data['id']), headers={'Content-Type': 'application/json', 'api-token': user_data['api_token']})
    self.assertEqual(res.status_code, 204)
    
    
    
  def tearDown(self):
    '''
    Tear Down
    '''
    with self.app.app_context():
      db.session.remove()
      db.drop_all()

if __name__ == "__main__":
  unittest.main() 