from flask import Flask
from flask_bcrypt import Bcrypt
from .server import socketio
from flask_cors import CORS

def create_app(config_obj="website.settings"):
    app = Flask(__name__)
    app.config.from_object(config_obj)

    # cors = CORS(app, supports_credentials=True)

    bcrypt = Bcrypt(app)

    socketio.init_app(app)

    from .views import views, auth, files, update
    app.register_blueprint(views, url_prefix="")
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(files, url_prefix="/files")
    app.register_blueprint(update, url_prefix="/update")

    return app, socketio
