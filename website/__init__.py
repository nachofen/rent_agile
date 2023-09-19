from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
import os
from flask_login import LoginManager


db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    """create app"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'topsecret'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(os.getcwd(), "website", DB_NAME)}'
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