#/src/views/UserView

from flask import request, json, Response, Blueprint, g
from ..models.UserModel import UserModel, UserSchema
from ..lib.Authentication import Auth
from ..lib.Response import custom_response

import logging
#logging.basicConfig(filename='debug.log',level=logging.DEBUG) 


user_api = Blueprint('users', __name__)
user_schema = UserSchema()

"""
@user_api.route('/', methods=['OPTIONS'])
def get_options():
  return options_response(200)
  

@user_api.route('/me', methods=['OPTIONS'])
def get_options_me():
  return options_response(200)   
  
@user_api.route('/login', methods=['OPTIONS'])
def get_options_login():
  return options_response(200)     
"""


  
  

@user_api.route('/', methods=['POST'])
def create():
  """
  Create User Function
  """
  req_data = request.get_json(cache=False)
  data, error = user_schema.load(req_data) # loads ????

  if error:
    return custom_response(error, 400)
  
  # check if user already exist in the db
  user_in_db = UserModel.get_user_by_email(data.get('email'))
  if user_in_db:
    message = {'error': 'User already exist, please supply another email address'}
    return custom_response(message, 400)
  
  user = UserModel(data)
  user.save()

  #Do data serialization
  ser_data = user_schema.dump(user).data
  
  #logging.debug(ser_data)
  
  token = Auth.generate_token(ser_data.get('id'))
  return custom_response({'jwt_token': token}, 201)
  

@user_api.route('/', methods=['GET'])
@Auth.auth_required
def get_all():
  """
  Get all users
  """
  users = UserModel.get_all_users()
  ser_users = user_schema.dump(users, many=True).data
  return custom_response(ser_users, 200)
  
  
@user_api.route('/login', methods=['POST'])
def login():
  """
  Login facility
  """
  req_data = request.get_json()

  data, error = user_schema.load(req_data, partial=True)

  if error:
    return custom_response(error, 400)
  
  if not data.get('email'):
    return custom_response({'error': 'invalid email'}, 400)
    
  if not data.get('password'):
    return custom_response({'error': 'invalid password'}, 400)      
  
  user = UserModel.get_user_by_email(data.get('email'))

  if not user:
    return custom_response({'error': 'Couldn\'t find user with specified email'}, 400)
  
  if not user.check_hash(data.get('password')):
    return custom_response({'error': 'User password is incorrect'}, 400)
  
  ser_data = user_schema.dump(user).data
  token = Auth.generate_token(ser_data.get('id'))
  return custom_response({'jwt_token': token}, 200)

####
@user_api.route('/<int:user_id>', methods=['GET'])
#@Auth.auth_required ###Everybody can see any user data
def get_a_user(user_id):
  """
  Get a single user
  """
  user = UserModel.get_one_user(user_id)
  if not user:
    return custom_response({'error': 'user not found'}, 404)
  
  ser_user = user_schema.dump(user).data
  return custom_response(ser_user, 200)
  


@user_api.route('/me', methods=['GET'])
@Auth.auth_required
def get_me():
  """
  Get me
  """
  user = UserModel.get_one_user(g.user.get('id'))
  ser_user = user_schema.dump(user).data
  return custom_response(ser_user, 200)
  
  
@user_api.route('/me', methods=['PUT'])
@Auth.auth_required
def update():
  """
  Update me
  """
  data = request.get_json()#dict - parse json and return dict


  user = UserModel.get_one_user(g.user.get('id'))
  user.update(data)
  ser_user = user_schema.dump(user).data
  return custom_response(ser_user, 200)

  
  

@user_api.route('/me', methods=['DELETE'])
@Auth.auth_required
def delete():
  """
  Delete a user
  """
  user = UserModel.get_one_user(g.user.get('id'))
  if not user:
    return custom_response({'message': 'user not found'}, 404)
  
  user.delete()
  return custom_response({}, 204)

