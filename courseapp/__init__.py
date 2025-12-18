from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary.uploader

app = Flask(__name__)

app.secret_key = "$&vd@($*vsdvs@B$vs$*@$&(*$&@("
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Admin%40123@localhost/flcenterdb?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app=app)

login = LoginManager(app=app)

cloudinary.config(
    cloud_name = 'dufzeox2u',
    api_key = '981122581416944',
    api_secret = 'xbdkpX5KXY3T0K-bULf5tV37OD0'
)