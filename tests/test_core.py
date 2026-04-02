from flask import Flask
from src.flask_alice import Dialogs


def test_create_app():
    app = Flask(__name__)
    dialogs = Dialogs(app)
