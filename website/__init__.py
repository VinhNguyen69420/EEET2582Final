from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

# Initialize SQLAlchemy and set the database name
db = SQLAlchemy()
DB_NAME = "database.db"

# Function to create the Flask app
def create_app():
    # Create the Flask app
    app = Flask(__name__)
    
    # Set a secret key for security
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    
    # Set the URI for the SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
    # Initialize SQLAlchemy with the app
    db.init_app(app)

    # Import views and auth blueprints
    from .views import views
    from .auth import auth

    # Register the blueprints with their respective URL prefixes
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Import User and Note models
    from .models import User
    
    # Create the database tables within the app context
    with app.app_context():
        db.create_all()

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Define a user loader function for Flask-Login
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

# Function to create the database if it doesn't exist
def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
