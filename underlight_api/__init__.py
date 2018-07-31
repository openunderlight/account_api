from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)
#The JWT secret key. Don't hardcode here - load from file.
app.config['JWT_SECRET_KEY'] = 'replace-string-12345-s00p3r-s33kr!!!t####-z0m$()*-g0@'
#Blacklisted JWTs for logouts.
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = [ 'access', 'refresh' ]
jwt = JWTManager(app)
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    from .database import UnderlightDatabase
    jti = decrypted_token['jti']
    db = UnderlightDatabase.get()
    return db.token_in_blacklist(jti)

api = Api(app)
bcrypt = Bcrypt(app)

from .resources import *
api.add_resource(UserLogin, '/login')
api.add_resource(UserRegister, '/register')
api.add_resource(UpdateUser, '/update_account')
api.add_resource(LogoutUser, '/logout')