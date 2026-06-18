from flask import current_app, render_template
from .usr_data import portfolio_data

# Navbar
pages = [
    {'name': 'Home', 'url': '/'},
    {'name': 'Hobbies', 'url': '/hobbies'},
]

# Views
def template_context():
    data = dict(portfolio_data)
    data['url'] = current_app.config.get('URL')
    return {'data': data, 'pages': pages}


def index_view():
    return render_template('index.html', **template_context())


def hobbies_view():
    return render_template('hobbies.html', **template_context())
