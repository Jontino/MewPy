from flask import request, Response, jsonify
from .. import app
from . import api
from ..models import Device, User
from datetime import datetime
import jwt
import json


def get_token():
    request_data = request.get_json()
    if 'username' in request_data and 'password' in request_data:
        username = str(request_data['username'])
        password = str(request_data['password'])

        user = User.get_by_username(username)
        if user is not None and user.check_password(password):
            expiration_date = datetime.datetime.utcnow() + datetime.timedelta(seconds=100)
            token = jwt.encode({'exp': expiration_date, 'role': user.role}, app.config['SECRET_KEY'], algorithm='HS256')
            return token
        else:
            return Response('', 401, mimetype='application/json')
    else:
        return Response('', 401, mimetype='application/json')


# GET /devices
@api.route('/devices')
def get_devices():
    return jsonify({'devices': Device.get_all_devices()})


@api.route('/devices/<string:serial_number>')
def get_device_by_serial_number(serial_number):
    return_value = Device.get_device(serial_number)
    temp = jsonify(return_value)
    return temp


# POST /devices
@api.route('/devices', methods=['POST'])
def add_device():
    request_data = request.get_json()
    if valid_device_object(request_data):
        Device.add_device(request_data['name'], request_data['family_name'], request_data['user_id'],
                          request_data['owner'], request_data['serial_number'], request_data['article_number'])
        response = Response("", status=201, mimetype='application/json')
        response.headers['Location'] = "/devices/" + str(request_data['serial_number'])
        return response
    else:
        invalid_device_object_error_msg = {
            "error": "Invalid device object passed in request",
            "helpString": "Data should be passed in similar to this {'name': 'X2 pro 7', 'family_name': 'X2 series'," +
                          " 'user_id': 'JNK', 'owner': 'Dept74', 'serial_number': '1234-0123456', 'article_number': '630000205'}"
        }
        response = Response(json.dumps(invalid_device_object_error_msg), status=400, mimetype="application/json")
        return response


@api.route('/devices/<string:serial_number>', methods=['PUT'])
def replace_device(serial_number):
    request_data = request.get_json()
    if not valid_device_object(request_data):
        invalid_device_object_error_msg = {
            "error": "Invalid device object passed in request",
            "helpString": "Data should be passed in similar to this {'name': 'X2 pro 7', 'family_name': 'X2 series'," +
                          " 'user_id': 'JNK', 'owner': 'Dept74', 'serial_number': '1234-0123456', 'article_number': '630000205'}"
        }
        response = Response(json.dumps(invalid_device_object_error_msg), status=400, mimetype='application/json')
        return response

    Device.replace_device(
        request_data['name'], request_data['family_name'], request_data['user_id'], request_data['owner'],
        request_data['serial_number'], request_data['article_number'])
    response = Response("", status=204)
    return response


@api.route('/devices/<string:serial_number>', methods=['PATCH'])
def update_device(serial_number):
    request_data = request.get_json()
    if not valid_patch_request_data(request_data):
        invalid_device_object_error_msg = {
            "error": "Invalid device object passed in request",
            "helpString": "Data should be passed in similar to this {'name': 'X2 pro 7', 'family_name': 'X2 series'," /
                          " 'user_id': 'JNK', 'owner': 'Dept74', 'serial_number': '1234-0123456'," /
                          "'article_number': '630000205'}"
        }
        response = Response(json.dumps(invalid_device_object_error_msg), status=400, mimetype='application/json')
        return response

    if "user_id" in request_data:
        Device.update_device_holder(serial_number, request_data['user_id'])

    response = Response("", status=204)
    response.headers['Location'] = "/api/devices/" + str(serial_number)
    return response


# DELETE
@api.route('/devices/<string:serial_number>', methods=['DELETE'])
def delete_device(serial_number):
    if Device.delete_device(serial_number):
        response = Response("", status=204)
        return response

    invalid_device_object_error_msg = {
        "error": "Device with serial number provided not found, so unable to delete."
    }
    response = Response(json.dumps(invalid_device_object_error_msg), status=404, mimetype="application/json")
    return response


def valid_device_object(device_object):
    if (
            "name" in device_object and "family_name" in device_object and "user_id" in device_object and "owner" in
            device_object and "serial_number" in device_object and "article_number" in device_object):
        return True
    else:
        return False


def valid_patch_request_data(device_object):
    if "user_id" in device_object:
        return True
    else:
        return False


def token_required(f):
    def wrapper(*args, **kwargs):
        token = request.args.get('token')
        try:
            decoded_payload = jwt.decode(token, app.config['SECRET_KEY'])
            print(decoded_payload)
            return f(*args, **kwargs)
        except:
            invalid_token_error_msg = {
                "error": "Need a valid token to view this page"
            }
            return Response(json.dumps(invalid_token_error_msg), 401, mimetype='application/json')

    return wrapper


def token_and_admin_required(f):
    def wrapper(*args, **kwargs):
        token = request.args.get('token')
        try:
            decoded_payload = jwt.decode(token, app.config['SECRET_KEY'])

            if 'role' in decoded_payload and decoded_payload['role'] == 'admin':
                return f(*args, **kwargs)
            else:
                raise ValueError()
        except:
            invalid_token_error_msg = {
                "error": "Need a valid token to view this page"
            }
            return Response(json.dumps(invalid_token_error_msg), 401, mimetype='application/json')

    return wrapper
