import flask

from src.rest.images import images

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.register_blueprint(images)


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Hello, from Flask!</h1>'''


if __name__ == '__main__':
    app.run(port=6164)