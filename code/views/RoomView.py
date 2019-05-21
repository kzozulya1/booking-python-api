#/src/views/BlogpostView.py
from flask import request, g, Blueprint, json, Response
from ..lib.Authentication import Auth
from ..models.RoomModel import RoomModel, RoomSchema
from ..lib.Response import custom_response
import logging

room_api = Blueprint('rooms', __name__)
room_schema = RoomSchema()

"""
@room_api.route('/', methods=['OPTIONS'])
def get_options():
  return options_response(200)
"""


@room_api.route('/', methods=['POST'])
@Auth.auth_required
def create():
  """
  Create a Room
  """
  req_data = request.get_json()
  req_data['owner_id'] = g.user.get('id')
  data, error = room_schema.load(req_data)
  if error:
    return custom_response(error, 400)
  
  
  
  room = RoomModel(data)
  room.save()
  data = room_schema.dump(room).data
  
  #logging.debug(data)
  
  return custom_response(data, 201)
  
  

@room_api.route('/', methods=['GET'])
def get_all():
  """
  Get All Rooms
  """
  rooms = RoomModel.get_all_rooms()
  data = room_schema.dump(rooms, many=True).data
  return custom_response(data, 200)
  
  

@room_api.route('/<int:room_id>', methods=['GET'])
def get_one(room_id):
  """
  Get a Room
  """
  room = RoomModel.get_one_room(room_id)
  if not room:
    return custom_response({'error': 'room not found'}, 404)
  data = room_schema.dump(room).data
  return custom_response(data, 200)


@room_api.route('/<int:room_id>', methods=['PUT'])
@Auth.auth_required
def update(room_id):
  """
  Update a Room
  """
  #req_data = request.get_json()
  data = request.get_json()
  room = RoomModel.get_one_room(room_id)
  if not room:
    return custom_response({'error': 'room not found'}, 404)
    
  #check room is owned by post customer
  orig_room_data = room_schema.dump(room).data
  if orig_room_data.get('owner_id') != g.user.get('id'):
    return custom_response({'error': 'permission denied - room owner doesnt match current UID'}, 400)
  
  #data, error = room_schema.load(req_data, partial=True)
  #if error:
    #return custom_response(error, 400)

  #logging.debug(data)
    
  room.update(data)
  data = room_schema.dump(room).data
  return custom_response(data, 200)

@room_api.route('/<int:room_id>', methods=['DELETE'])
@Auth.auth_required
def delete(room_id):
  """
  Delete A Room
  """
  room = RoomModel.get_one_room(room_id)
  if not room:
    return custom_response({'error': 'room not found'}, 404)
  
  data = room_schema.dump(room).data
  if data.get('owner_id') != g.user.get('id'):
    return custom_response({'error': 'permission denied'}, 400)

  room.delete()
  return custom_response({'message': 'deleted'}, 204)
 
