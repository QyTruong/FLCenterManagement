from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary.uploader
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

app.secret_key = "$&vd@($*vsdvs@B$vs$*@$&(*$&@("
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SENDGRID_API_KEY'] = os.getenv('SENDGRID_API_KEY')
app.config['SENDGRID_FROM_EMAIL'] = 'truong4725@outlook.com'

db = SQLAlchemy(app=app)

login = LoginManager(app=app)

cloudinary.config(
    cloud_name = 'dufzeox2u',
    api_key = '981122581416944',
    api_secret = os.getenv('CLOUDINARY_SECRET_KEY')
)