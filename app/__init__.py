import os
import datetime
from flask import Flask, request, render_template
from dotenv import load_dotenv
from peewee import *
from playhouse.shortcuts import model_to_dict

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

@app.route('/api/timeline_post', methods=['POST'])
def post_time_line_post():
    name = request.form[ 'name']
    email = request.form['email']
    content = request. form[ 'content' ]
    timeline_post = TimelinePost. create(name=name, email=email, content=content)

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