from .views import hobbies_view, index_view


def register_routes(app):
    app.add_url_rule('/', endpoint='index', view_func=index_view)
    app.add_url_rule('/hobbies', endpoint='hobbies', view_func=hobbies_view)
