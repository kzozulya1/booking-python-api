import unittest
import os
import json
from ..app import get_app, db

#import logging
#UM_LOG_FILENAME = 'debug.log'
#logging.basicConfig(filename=UM_LOG_FILENAME,level=logging.DEBUG)


class UsersTest(unittest.TestCase):
  '''
  Users Test Case
  '''
  def setUp(self):
    '''
    Test Setup
    '''
    self.app = get_app("testing")
    self.client = self.app.test_client
    self.user = {
      'name': 'Olga Steiman',
      'email': 'o.steiman@gmail.com',
      'password': 'passw0rd$%^^!'
    }

    with self.app.app_context():
      # create all tables
      db.create_all()
  
  def test_user_creation(self):
    ''' 
    test user creation with valid credentials 
    '''
    res = self.client().post('/api/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    json_data = json.loads(res.data)
    self.assertTrue(json_data.get('jwt_token'))
    self.assertEqual(res.status_code, 201)

  def test_user_creation_with_existing_email(self):
    ''' 
    test user creation with already existing email
    '''
    res = self.client().post('/api/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    self.assertEqual(res.status_code, 201)
    res = self.client().post('/api/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    json_data = json.loads(res.data)
    self.assertEqual(res.status_code, 400)
    self.assertTrue(json_data.get('error'))    
    
  def test_user_creation_with_no_password(self):    
    '''
    User create with no password
    '''  
    user_no_pwd = {'name': "Kosta", "email": 'terra@gmail.com'}
    res = self.client().post('/api/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(user_no_pwd))
    json_data = json.loads(res.data) # {'password': ['Missing data for required field.']}
    self.assertEqual(res.status_code,400)
    self.assertTrue(json_data.get('password'))
    self.assertEqual(json_data.get('password'),['Missing data for required field.'])
    
  def test_user_creation_with_no_email(self):
    '''
    User create with no email
    ''' 
    user_no_email = {'name': "Kosta", "password": 'password1'}
    res = self.client().post('/api/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(user_no_email))
    json_data = json.loads(res.data)
    self.assertEqual(res.status_code,400)
    self.assertTrue(json_data.get('email'))
    
  def test_user_creation_with_empty_request(self):
    '''
    User create with empty data
    '''
    user = {}
    res = self.client().post('/api/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(user))
    json_data  = json.loads(res.data)
    self.assertEqual(res.status_code,400)
    #loop over 3 keys of error response
    [self.assertTrue(json_data.get(i)) for i in ('name', 'email', 'password')]
    
  def test_user_login(self):
    '''
    User login without email
    '''
    res = self.client().post('/api/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    login_data = {'email': self.user.get('email'), 'password': self.user.get('password') }
    res = self.client().post('/api/v1/users/login', headers={'Content-Type': 'application/json'}, data=json.dumps(login_data))
    json_data = json.loads(res.data)
    
    self.assertEqual(res.status_code,200)
    self.assertTrue(json_data.get('jwt_token'))

  def test_user_login_no_email(self):
    '''
    User login without email
    '''
    res = self.client().post('/api/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    login_data = {'password': self.user.get('password') }
    res = self.client().post('/api/v1/users/login', headers={'Content-Type': 'application/json'}, data=json.dumps(login_data))
    json_data = json.loads(res.data)
    
    self.assertEqual(res.status_code,400)
    self.assertEqual(json_data.get('error'),'invalid email')

  def test_user_login_incorrect_password(self):
    '''
    User login with incorrect password
    '''
    res = self.client().post('/api/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    login_data = {'email': self.user.get('email'), 'password': 'fuck-password:)' }
    res = self.client().post('/api/v1/users/login', headers={'Content-Type': 'application/json'}, data=json.dumps(login_data))
    json_data = json.loads(res.data)
    
    self.assertEqual(res.status_code,400)
    #self.assertEqual(json_data.get('error'),'check user password hash failed')
    
  def test_user_login_fake_email(self):
    '''
    User login with not existing email
    '''
    res = self.client().post('/api/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    login_data = {'email': 'fake-email@gmail.com', 'password': '12345678' }
    res = self.client().post('/api/v1/users/login', headers={'Content-Type': 'application/json'}, data=json.dumps(login_data))
    json_data = json.loads(res.data)
    
    self.assertEqual(res.status_code,400)
    #self.assertEqual(json_data.get('error'), 'no user with specified email' )    
    

  def test_user_get_me(self):
    '''
    Get Me with correct params
    '''
    res = self.client().post('/api/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    json_data = json.loads(res.data)
    api_token = json_data.get('jwt_token')
    
    res = self.client().get('/api/v1/users/me', headers={'Content-Type': 'application/json', 'api-token': api_token})
    json_data = json.loads(res.data)
    self.assertTrue(res.status_code,200)
    self.assertEqual(json_data.get('name'),self.user.get('name'))
    self.assertEqual(json_data.get('email'),self.user.get('email'))
    
  def test_get_user_by_id(self):
    '''
    Get user by ID
    '''
    res = self.client().post('/api/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    json_data = json.loads(res.data);
    self.assertTrue(res.status_code,201)
    api_token = json_data['jwt_token']
    
    res = self.client().get('/api/v1/users/me', headers={'Content-Type': 'application/json', 'api-token': api_token})
    json_data = json.loads(res.data)
    id = json_data['id']
    
    res = self.client().get('/api/v1/users/'+str(id), headers={'Content-Type': 'application/json', 'api-token': api_token})
    self.assertTrue(res.status_code,200)
    json_data = json.loads(res.data)
    
    self.assertEqual(json_data.get('email'), self.user['email'])
    self.assertEqual(json_data['name'], self.user.get('name'))
    
  def test_get_user_get_all(self):
    '''
    Get all users
    '''
    res = self.client().post('/api/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    json_data = json.loads(res.data);
    self.assertTrue(res.status_code,201)
    api_token = json_data['jwt_token']
    
    res = self.client().get('/api/v1/users/', headers={'Content-Type': 'application/json', 'api-token': api_token})
    self.assertTrue(res.status_code,200)
    json_list = json.loads(res.data)

    first_user = json_list.pop()
    self.assertEqual(first_user['email'], self.user.get('email'))
    self.assertEqual(first_user['name'], self.user['name'])
    
    
  def test_user_get_me_failed_jwt_token(self):
    '''
    Get Me with incorrect Jwt Token
    '''
    res = self.client().get('/api/v1/users/me', headers={'Content-Type': 'application/json', 'api-token': 'fake-token!'})
    json_data = json.loads(res.data)
    self.assertTrue(res.status_code,400)
    self.assertEqual(json_data.get('error'),'invalid jwt token')
    
  def test_user_get_me_no_jwt_token(self):
    '''
    Get Me without Jwt Token
    '''
    res = self.client().get('/api/v1/users/me', headers={'Content-Type': 'application/json'})
    json_data = json.loads(res.data)
    self.assertTrue(res.status_code,400)
    self.assertEqual(json_data.get('error'),'no jwt token specified')    
  
  def test_user_update_me(self):
    '''
    Update user
    '''
    res = self.client().post('/api/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    json_data = json.loads(res.data)
    api_token = json_data.get('jwt_token')
    
    update_data = {'name': 'Ivan Petrov'}
    res = self.client().put('/api/v1/users/me', headers={'Content-Type': 'application/json','api-token': api_token}, data=json.dumps(update_data))
    json_data = json.loads(res.data)
    self.assertTrue(res.status_code,200)
    self.assertEqual(json_data.get('name'),update_data.get('name'))
    

  def test_user_delete_me(self):
    '''
    Delete me user
    '''
    res = self.client().post('/api/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    json_data = json.loads(res.data)
    api_token = json_data.get('jwt_token')
    res = self.client().delete('/api/v1/users/me', headers={'Content-Type': 'application/json','api-token': api_token})
    self.assertTrue(res.status_code,204)
    
  def tearDown(self):
    '''
    Tear Down
    '''
    with self.app.app_context():
      db.session.remove()
      db.drop_all()

if __name__ == "__main__":
  unittest.main() 