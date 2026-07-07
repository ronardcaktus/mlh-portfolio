import os
import datetime
from flask import Flask
from dotenv import load_dotenv
from peewee import *

from .routes import register_routes

load_dotenv()

mydb = MySQLDatabase(
    os.getenv("MYSQL_DATABASE"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    host=os.getenv("MYSQL_HOST"),
    port=3306
)

class TimelinePost(Model):
    name = CharField()
    email = CharField()
    content = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)
    class Meta:
        database = mydb

mydb.connect()
mydb.create_tables([TimelinePost])



def create_app():
    app = Flask(__name__)

    app.config['URL'] = os.getenv('URL')
    register_routes(app)
    return app


app = create_app()
