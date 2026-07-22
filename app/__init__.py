import os
import re
import time
import datetime
from flask import Flask, request, render_template
from dotenv import load_dotenv
from peewee import *
from playhouse.shortcuts import model_to_dict

from .routes import register_routes

load_dotenv()

if os.getenv("TESTING") == "true":
    print("Running in test mode")
    mydb = SqliteDatabase('file:memory?mode=memory&cache=shared', uri=True)
else:
    mysql_host = os.getenv("MYSQL_HOST")
    mysql_user = os.getenv("MYSQL_USER")
    mysql_password = os.getenv("MYSQL_PASSWORD")
    mysql_database = os.getenv("MYSQL_DATABASE")

    if mysql_host and mysql_user and mysql_password and mysql_database:
        mydb = MySQLDatabase(
            mysql_database,
            user=mysql_user,
            password=mysql_password,
            host=mysql_host,
            port=3306,
        )
    else:
        print("MYSQL_* env vars are missing; using local SQLite database")
        mydb = SqliteDatabase('portfolio.db')

class TimelinePost(Model):
    name = CharField()
    email = CharField()
    content = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)
    class Meta:
        database = mydb

def initialize_database(max_retries=30, delay_seconds=2):
    for attempt in range(1, max_retries + 1):
        try:
            mydb.connect(reuse_if_open=True)
            mydb.create_tables([TimelinePost], safe=True)
            return
        except OperationalError as exc:
            if attempt == max_retries:
                raise
            print(f"Database not ready yet (attempt {attempt}/{max_retries}): {exc}")
            time.sleep(delay_seconds)


initialize_database()

def create_app():
    app = Flask(__name__)

    app.config['URL'] = os.getenv('URL')
    register_routes(app)
    return app


app = create_app()

EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

@app.route('/api/timeline_post', methods=['POST'])
def post_time_line_post():
    name = request.form.get('name')
    email = request.form.get('email')
    content = request.form.get('content')

    if not name:
        return 'Invalid name', 400
    if not content:
        return 'Invalid content', 400
    if not email or not EMAIL_REGEX.match(email):
        return 'Invalid email', 400

    timeline_post = TimelinePost.create(name=name, email=email, content=content)

    return model_to_dict(timeline_post)

@app.route( '/api/timeline_post', methods=['GET'])
def get_time_line_post():
    return {
        'timeline_posts': [
            model_to_dict(p)
            for p in
TimelinePost.select().order_by(TimelinePost.created_at.desc())
        ]
    }

@app.route('/api/timeline_post/<int:post_id>', methods=['DELETE'])
def delete_time_line_post(post_id):
    deleted = TimelinePost.delete().where(TimelinePost.id == post_id).execute()
    if deleted == 0:
        return {'error': f'timeline post {post_id} not found'}, 404
    return {'deleted': post_id}


@app.route("/timeline")
def timeline():
    return render_template('timeline.html', title="Timeline")