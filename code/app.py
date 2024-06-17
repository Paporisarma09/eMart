from flask import Flask
import os
from application.database import db
from flask_restful import Api
from flask_cors import CORS

current_dir = os.path.abspath(os.path.dirname(__file__))

app= Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "instance/database.sqlite3")
app.config['CORS_HEADERS'] = 'Content-Type'
db.init_app(app)
api = Api(app)
app.app_context().push()

from application.controllers import *
from application.api import UserAPI, ProductCategoryAPI, ProductAPI, UserCartDetailsAPI
api.add_resource(UserAPI, "/api/user/<username>/<role>", "/api/user")
api.add_resource(ProductCategoryAPI, "/api/productcategory/<productcategoryid>", "/api/productcategory")
api.add_resource(ProductAPI, "/api/product/<productid>", "/api/product")
api.add_resource(UserCartDetailsAPI, "/api/usercartdetails/<id>", "/api/usercartdetails")

if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True)