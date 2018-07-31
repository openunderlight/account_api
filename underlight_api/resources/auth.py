from flask_restful import Resource, reqparse
from flask_jwt_extended import (create_access_token, jwt_required, get_jwt_identity, get_raw_jwt)
from underlight_api.database import UnderlightDatabase
import datetime

'''
All resources related to auth go in here, including logging users in, registration, updating account info
and resetting passwords.
'''

class UserLogin(Resource):
    '''Logs the user in and returns the JWT access token.'''
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
    '''Registers a new user and returns a JWT access token.'''
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

class UpdateUser(Resource):
    '''Updates the user.'''
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('password', type=str, help='Must supply a password', required=False, location='json', store_missing=True, default=None)
        self.parser.add_argument('emailAddress', type=str, help='Must supply an email address', required=False, location='json', store_missing=True, default=None)
        self.parser.add_argument('fullName', type=str, help='Must supply your full name', required=False, location='json', store_missing=True, default=None)
    
    @jwt_required
    def post(self):
        data = self.parser.parse_args()        
        db = UnderlightDatabase.get()
        id = get_jwt_identity()
        db.update_account(id, **data)
        return {
            'message': 'Updated account %d' % id
        }
    
class LogoutUser(Resource):
    '''Logs the user out, blacklists the JTI'''
    @jwt_required
    def get(self):
        jti = get_raw_jwt()['jti']
        db = UnderlightDatabase.get()
        db.blacklist_token(jti)
        return {
            'message': 'Successfully logged out'
        }