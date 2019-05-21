# src/models/UserModel.py
from marshmallow import fields, Schema
import datetime
from . import db, bcrypt
from .RoomModel import RoomSchema
from .ReservationModel import ReservationSchema

"""
Logging facility
"""
import logging
UM_LOG_FILENAME = 'debug.log'
logging.basicConfig(filename=UM_LOG_FILENAME,level=logging.DEBUG)


class UserModel(db.Model):
  """
  User Model
  """

  # table name
  __tablename__ = 'user'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String(128), nullable=False)
  age = db.Column(db.Integer, default=999)  
  email = db.Column(db.String(128), unique=True, nullable=False)
  password = db.Column(db.String(128), nullable=True)
  created_at = db.Column(db.DateTime)
  modified_at = db.Column(db.DateTime)
  is_room_master = db.Column(db.Integer)
  rooms = db.relationship('RoomModel', cascade="delete", backref='user', lazy=True, order_by="RoomModel.id.desc()")
  reservations = db.relationship('ReservationModel', cascade="delete", backref='user', lazy=True, order_by="ReservationModel.id.desc()")
  
  


  # class constructor
  def __init__(self, data):
    """
    Class constructor
    """
    self.name = data.get('name')
    self.email = data.get('email')
    self.password = self.__generate_hash(data.get('password')) # add this line
    self.created_at = datetime.datetime.utcnow()
    self.modified_at = datetime.datetime.utcnow()

  def save(self):
    db.session.add(self)
    db.session.commit()

  def update(self, data):
    for key, item in data.items():
    
      if key == 'password': # add this new line
        self.password = self.__generate_hash(item) # add this new line
      else:
        setattr(self, key, item)
    self.modified_at = datetime.datetime.utcnow()
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()
    
  # add this new method
  def __generate_hash(self, password):
    return bcrypt.generate_password_hash(password, rounds=10).decode("utf-8")
  
  # add this new method
  def check_hash(self, password):
    return bcrypt.check_password_hash(self.password, password)    

  @staticmethod
  def get_user_by_email(value):
    return UserModel.query.filter_by(email=value).first()
    
  @staticmethod
  def get_all_users():
    return UserModel.query.all()

  @staticmethod
  def get_one_user(id):
    return UserModel.query.get(id)

  
  def __repr__(self):
    #return '<id {}>'.format(self.id)
    return f"I am object of UserModel and have next data: id:{self.id}, name:{self.name}, email: {self.email}, age: {self.age}, created_at: {self.created_at} and ..."
    
    
# add this class
class UserSchema(Schema):
  """
  User Schema
  """
  id = fields.Int(dump_only=True)
  name = fields.Str(required=True)
  age = fields.Int(required=False)
  email = fields.Email(required=True)
  password = fields.Str(required=True)
  created_at = fields.DateTime(dump_only=True)
  modified_at = fields.DateTime(dump_only=True)
  rooms = fields.Nested(RoomSchema, many=True)    
  reservations = fields.Nested(ReservationSchema, many=True)    