from mewpy import db
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from flask_login import UserMixin
import json


class Device(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(80), nullable=False)
    family_name = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner = db.Column(db.String(80), nullable=False)
    serial_number = db.Column(db.String(80), nullable=False)
    article_number = db.Column(db.String(80), nullable=False)
    user_periods = db.relationship('UserPeriod', backref='device')

    @staticmethod
    def get_all_devices():
        return [Device.json(device) for device in Device.query.all()]

    @staticmethod
    def get_device(serial_number):
        return Device.json(Device.query.filter_by(serialnumber=serial_number).first())

    @staticmethod
    def add_device(name, family_name, user, owner, serial_number, article_number):
        new_device = Device(name=name, family_name=family_name, user=user, owner=owner, serial_number=serial_number,
                            article_number=article_number)
        db.session.add(new_device)
        db.session.commit()

    @staticmethod
    def update_device_holder(serial_number, holder):
        device_to_update = Device.query.filter_by(serial_number=serial_number).first()
        device_to_update.holder = holder
        db.session.commit()

    @staticmethod
    def replace_device(name, family_name, holder, owner, serial_number, article_number):
        device_to_replace = Device.query.filter_by(serial_number=serial_number).first()
        device_to_replace.name = name
        device_to_replace.family_name = family_name
        device_to_replace.holder = holder
        device_to_replace.owner = owner
        device_to_replace.serial_number = serial_number
        device_to_replace.article_number = article_number
        db.session.commit()

    @staticmethod
    def delete_device(serial_number):
        is_successful = Device.query.filter_by(serial_number=serial_number).delete()
        db.session.commit()
        return bool(is_successful)

    def json(self):
        return {
            'name': self.name,
            'family_name': self.family_name,
            'user_id': self.user_id,
            'owner': self.owner,
            'serial_number': self.serial_number,
            'article_number': self.article_number
        }

    def __repr__(self):
        device_object = {
            'name': self.name,
            'family_name': self.family_name,
            'user_id': self.user_id,
            'owner': self.owner,
            'serial_number': self.serial_number,
            'article_number': self.article_number
        }
        return json.dumps(device_object)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String)
    role = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True)
    devices = db.relationship('Device', backref='user')
    user_periods = db.relationship('UserPeriod', backref='user')

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_all_users():
        return User.query.all()

    @staticmethod
    def create_user(username, password, role):
        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()

    def __repr__(self):
        return str({
            'username': self.username,
            'password': self.password_hash,
            'role': self.role
        })


class UserPeriod(db.Model):
    __tablename__ = 'user_periods'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, default=None, nullable=True)
