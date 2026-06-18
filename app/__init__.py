import os
from flask import Flask
from dotenv import load_dotenv

from .routes import register_routes

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config['URL'] = os.getenv('URL')
    register_routes(app)
    return app


app = create_app()
