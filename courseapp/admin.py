from flask_admin import Admin
from courseapp import app, db
from flask_admin.contrib.sqla import ModelView
from models import Class


admin = Admin(app=app, name='Administration')


admin.add_view(ModelView(Class, db.session))