from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'replace-string-12345-s00p3r-s33kr!!!t####-z0m$()*-g0@'
jwt = JWTManager(app)
api = Api(app)
bcrypt = Bcrypt(app)

import ulaccount.resources as resources
api.add_resource(resources.UserLogin, '/login')
api.add_resource(resources.UserRegister, '/register')
