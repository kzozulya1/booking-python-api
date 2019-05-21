#/src/views/UserView

from flask import request, json, Response, Blueprint, g
from ..models.ReservationModel import ReservationModel, ReservationSchema
from ..lib.Authentication import Auth
from ..lib.Response import custom_response

import logging
#UM_LOG_FILENAME = 'debug-reserv.log'
#logging.basicConfig(filename=UM_LOG_FILENAME,level=logging.DEBUG) 



reservation_api = Blueprint('reservations', __name__)
reservation_schema = ReservationSchema()

"""
@reservation_api.route('/', methods=['OPTIONS'])
def get_options():
  return options_response(200)
"""  

@reservation_api.route('/room/<int:room_id>', methods=['POST'])
@Auth.auth_required
def create(room_id):
  """
  Create Reservation Function
  """
  post_data = request.get_json(cache=False)

  post_data['user_id'] = g.user.get('id')
  post_data['room_id'] = room_id
  
  reservation = ReservationModel(post_data)
  error = reservation.save()
  if error:
    """
    return http code 409 Conflict
    """
    return custom_response({'error': error},409)
  
  

  ser_data = reservation_schema.dump(reservation).data
  return custom_response(ser_data, 201)
  

@reservation_api.route('/room/<int:room_id>', methods=['GET'])
def get_reservations_for_room(room_id):
  """
  Get all reservations for room id
  """
  reservations = ReservationModel.get_reservation_by_room_id(room_id)
  """
  for i, r in enumerate(reservations):
    reservations[i].book_from_formatted = r.book_from.strftime("%d.%m.%Y")
    reservations[i].book_to_formatted = r.book_to.strftime("%d.%m.%Y")
   """
    
  ser_reservations = reservation_schema.dump(reservations, many=True).data
  
  return custom_response(ser_reservations, 200)
  
 
  
  
@reservation_api.route('/<int:reservation_id>', methods=['PUT'])
@Auth.auth_required
def update(reservation_id):
  """
  Update me
  """
  data = request.get_json()#dict - parse json and return dict
  reservation = ReservationModel.get_one_reservation(reservation_id)
  reservation.update(data)
  ser_reservation = reservation_schema.dump(reservation).data
  return custom_response(ser_reservation, 200)
  

@reservation_api.route('/<int:reservation_id>', methods=['DELETE'])
@Auth.auth_required
def delete(reservation_id):
  """
  Delete a reservation
  """
  reservation = ReservationModel.get_one_reservation(reservation_id)
  
  if not reservation:
    return custom_response({'message': 'reservation not found'},404)
  
  ser_reservation = reservation_schema.dump(reservation).data
  if (ser_reservation.get('user_id') != g.user.get('id')):
    return custom_response({'message': 'current user doesnt own reservation'}, 400)
  
  
  reservation.delete()
  return custom_response({}, 204)

