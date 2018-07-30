from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token
from ulaccount.database import UnderlightDatabase
import datetime

class UserLogin(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', type=str, help='Must supply a username', required=True, location='json')
        self.parser.add_argument('password', type=str, help='Must supply a password', required=True, location='json')

    def post(self):
        data = self.parser.parse_args()
        db = UnderlightDatabase.get()
        id = db.retrieve_billing_account_id(data['username'], data['password'])
        if not id:
            return { 'message': 'Invalid credentials' }, 401
        else:
            return {
                'message': 'Logged in as %s, id: %d' % (data['username'], id),
                'access_token': create_access_token(identity=id, fresh=True, expires_delta=datetime.timedelta(hours=24))
            }

class UserRegister(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', type=str, help='Must supply a username', required=True, location='json')
        self.parser.add_argument('password', type=str, help='Must supply a password', required=True, location='json')
        self.parser.add_argument('emailAddress', type=str, help='Must supply an email address', required=True, location='json')
        self.parser.add_argument('fullName', type=str, help='Must supply your full name', required=True, location='json')
        self.parser.add_argument('agreeToTerms', type=bool, help='Must agree to TOS', required=True, location='json')
    
    def post(self):
        data = self.parser.parse_args()
        db = UnderlightDatabase.get()
        exists = db.check_account_exists(data['username'], data['emailAddress'])
        if exists:
            return { 'message': 'An account with that username or email already exists' }, 403
        if not data['agreeToTerms']:
            return { 'message': 'Must agree to TOS' }, 401
        id = db.add_account(data['username'], data['emailAddress'], data['password'], data['fullName'])
        return {
            'message': 'Logged in as %s, id: %d' % (data['username'], id),
            'access_token': create_access_token(identity=id, fresh=True, expires_delta=datetime.timedelta(hours=24))
        }