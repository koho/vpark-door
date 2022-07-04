from app import db
from datetime import datetime


class DoorLog(db.Model):
    __tablename__ = 'door_log'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.DateTime, default=datetime.now)
    username = db.Column(db.String(64))
    door_id = db.Column(db.String(50))
    door_name = db.Column(db.String(100))
    code = db.Column(db.Integer)
    msg = db.Column(db.String(200))
