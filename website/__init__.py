from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
import os
from flask_login import LoginManager


db = SQLAlchemy()
DB_NAME = "rent_agile_DB"

def create_app():
    """create app"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'topsecret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://u9qa2hbw6ktwmdun:PVOm3sa2s114KTWE2FDX@bhkoe56efo2orbc1igit-mysql.services.clever-cloud.com:3306/bhkoe56efo2orbc1igit'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        """load user function"""
        return User.query.get(int(id)) 
        # user.query.get looks for primary key so it knows that id is id
    return app

def create_database(app):
    """creates database if it doesn't exist"""
    if not path.exists('website/' + DB_NAME):
        try:
            with app.app_context():
                db.create_all()
            print('Created DB')
        except Exception as e:
            print(f"Error creating database: {str(e)}")
    else:
        print('Database already exists')