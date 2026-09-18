import os
from flask import Flask
from models import db, User, seed_database
from routes import main
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'trekking_app_secret_key_12345'
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    app.register_blueprint(main)
    seed_database(app)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
