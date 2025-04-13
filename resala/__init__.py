## __init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# إنشاء كائن قاعدة البيانات
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    
    with app.app_context():
        
        from .main.routes import main
        from .auth.routes import auth
        app.register_blueprint(main)
        app.register_blueprint(auth)
    
    return app