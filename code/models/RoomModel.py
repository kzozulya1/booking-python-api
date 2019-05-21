# src/models/Blogpost.py
from . import db
import datetime
from marshmallow import fields, Schema
from .ReservationModel import ReservationSchema

class RoomModel(db.Model):
  """
  Room Model
  """

  __tablename__ = 'room'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  address = db.Column(db.Text, nullable=True)
  description = db.Column(db.Text, nullable=False)
  body_capacity = db.Column(db.Integer, nullable=False, default=1)
  owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # add this new line
  created_at = db.Column(db.DateTime)
  modified_at = db.Column(db.DateTime)
  
  img_main = db.Column(db.Text, nullable=True)
  img_1 = db.Column(db.Text, nullable=True)
  img_2 = db.Column(db.Text, nullable=True)
  img_3 = db.Column(db.Text, nullable=True)
  
  
  allow_smoking = db.Column(db.Boolean, default=0) 
  allow_parking = db.Column(db.Boolean, default=0) 
  allow_children = db.Column(db.Boolean, default=0) 
  reservations = db.relationship('ReservationModel', cascade="delete", backref='reservation', lazy=True, order_by="ReservationModel.id.desc()")

  def __init__(self, data):
    self.description = data.get('description')
    self.body_capacity = data.get('body_capacity')
    self.address = data.get('address')
    self.owner_id = data.get('owner_id')
    self.allow_smoking = data.get('allow_smoking')
    self.allow_parking = data.get('allow_parking')
    self.allow_children = data.get('allow_children')
    self.created_at = datetime.datetime.utcnow()
    self.modified_at = datetime.datetime.utcnow()
    
    self.img_main = data.get('img_main')
    self.img_1 = data.get('img_1')
    self.img_2 = data.get('img_2')
    self.img_3 = data.get('img_3')
    

  def save(self):
    db.session.add(self)
    db.session.commit()

  def update(self, data):
    for key, item in data.items():
      setattr(self, key, item)
    self.modified_at = datetime.datetime.utcnow()
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()
  
  @staticmethod
  def get_all_rooms():
    #return RoomModel.query.all()
    return RoomModel.query.order_by(RoomModel.id.desc())
  
  @staticmethod
  def get_one_room(id):
    return RoomModel.query.get(id)

  def __repr__(self):
    return f"Id:{self.id}, desc:{self.description}"


class RoomSchema(Schema):
  """
  Room Schema
  """
  id = fields.Int(dump_only=True)
  address = fields.Str(required=False)
  description = fields.Str(required=True)
  body_capacity = fields.Int(required=True)
  owner_id = fields.Int(required=True)
  created_at = fields.DateTime(dump_only=True)
  modified_at = fields.DateTime(dump_only=True)
  
  img_main = fields.Str(required=False)
  img_1 = fields.Str(required=False)
  img_2 = fields.Str(required=False)
  img_3 = fields.Str(required=False)
  
  allow_smoking = fields.Boolean(required=False)
  allow_parking = fields.Boolean(required=False)
  allow_children = fields.Boolean(required=False)
  reservations = fields.Nested(ReservationSchema, many=True)
 
