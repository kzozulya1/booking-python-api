# -*- coding: utf-8 -*-

#import sys
#sys.path.append('..')

import os

from .config.env import env_config 
from .models import db, bcrypt
from .views.UserView import user_api as user_blueprint 
from .views.RoomView import room_api as room_blueprint
from .views.ReservationView import reservation_api as reservation_blueprint

#import logging
from flask import Flask


#LOG_FILENAME = 'error.log'
#logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
#logging.debug(app_config[os.getenv('FLASK_ENV')])

def get_app(env = os.getenv('FLASK_ENV')):
   application = Flask(__name__)
   application.config.from_object(env_config[env])

   bcrypt.init_app(application)
   db.init_app(application) 
   
   application.register_blueprint(user_blueprint, url_prefix='/api/v1/users')
   application.register_blueprint(room_blueprint, url_prefix='/api/v1/rooms')
   application.register_blueprint(reservation_blueprint, url_prefix='/api/v1/reservations')
   
   """
   Add extra allow headers for react js libs
   """
   @application.after_request
   def apply_caching(response):
      response.headers['Access-Control-Allow-Origin'] = '*'
      response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept, api-token'
      response.headers['Access-Control-Allow-Methods'] = 'HEAD, GET, PUT, POST, OPTIONS, DELETE'
      return response

   return application
