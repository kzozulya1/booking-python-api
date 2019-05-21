# src/models/ReservationModel.py
from marshmallow import fields, Schema
from sqlalchemy.sql import text
import datetime
from . import db, bcrypt

import logging


class ReservationModel(db.Model):
  """
  Room Reservation Model
  """

  # table name
  __tablename__ = 'reservation'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  
  book_from = db.Column(db.DateTime, nullable=False)
  book_to = db.Column(db.DateTime, nullable=False)
  created_at = db.Column(db.DateTime)
  modified_at = db.Column(db.DateTime)
  notes = db.Column(db.Text, nullable=True)

  # class constructor
  def __init__(self, data):
    """
    Class constructor
    """
    self.room_id = data.get('room_id')
    self.user_id = data.get('user_id')
    self.book_from = data.get('book_from')
    self.book_to = data.get('book_to')
    self.created_at = datetime.datetime.utcnow()
    self.modified_at = datetime.datetime.utcnow()
    self.notes = data.get('notes')
 

  def save(self):
    existedReservationInTargetDates = self.query.\
      filter(ReservationModel.book_from <= self.book_from).\
      filter(ReservationModel.book_to >= self.book_from).\
      filter(ReservationModel.room_id == self.room_id)
    
    if existedReservationInTargetDates.count():
      reservedDates = "Already reserved from " + existedReservationInTargetDates.first().book_from.strftime("%d.%m.%Y") + \
        " to " +  existedReservationInTargetDates.first().book_to.strftime("%d.%m.%Y")
      #logging.debug(reservedDates)
      return reservedDates
    
  
    db.session.add(self)
    db.session.commit()
    return False;

  def update(self, data):
    for key, item in data.items():
      setattr(self, key, item)
      
    self.modified_at = datetime.datetime.utcnow()
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  @staticmethod
  def get_reservation_by_room_id(value):
    #return ReservationModel.query.filter_by(room_id=value).all()
    return ReservationModel.query.filter_by(room_id=value).order_by(ReservationModel.id.desc())
    
    
  '''
  @staticmethod
  def get_all_users():
    return UserModel.query.all()
  '''

  @staticmethod
  def get_one_reservation(id):
    return ReservationModel.query.get(id)

  
  def __repr__(self):
    return f"I am object of ReservationModel and have next data: id:{self.id}, notes:{self.notes}, book_to: {self.book_to} and ..."
    

class ReservationSchema(Schema):
  """
  Reservation Schema
  """
  id = fields.Int(dump_only=True)
  room_id = fields.Int(required=True)
  user_id = fields.Int(required=True)
  book_from = fields.DateTime(required=True)
  book_to = fields.DateTime(required=True)
  created_at = fields.DateTime(dump_only=True)
  modified_at = fields.DateTime(dump_only=True)
  notes = fields.Str(required=False)
