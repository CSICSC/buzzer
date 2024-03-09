from flask import Flask, render_template, make_response, request
from config import DevConfig
import uuid
from flask_sock import Sock
from redis_client import redis_client

app = Flask(__name__)
sock = Sock(app)

CONTROLLER_COOKIE_KEY = "controllerck"


@app.route('/')
def index():
    if request.method == 'GET':
        return render_template("index.html")
    else:
        return render_template('errors/405.html'), 405


@app.route('/buzzer-controller')
def buzzer_controller():
    if request.method == 'GET':
        user_cookie = request.cookies.get(CONTROLLER_COOKIE_KEY)

        if user_cookie:
            return render_template("buzzer-controller.html", code=user_cookie)

        code = str(uuid.uuid4()).split('-')[0]

        resp = make_response(render_template(
            "buzzer-controller.html", code=code))

        resp.set_cookie(CONTROLLER_COOKIE_KEY, code)

        redis_client.lpush(code, 'end')

        return resp
    else:
        return render_template('errors/405.html'), 405


# finish the POST, which routes redirects to the GET
@app.route('/game-room')
def game_room():
    if request.method == 'GET':
        return render_template('room.html')


@sock.route('/buzzer-lock')
def handle_stream(ws):
    while True:
        received = ws.receive()
        if received is None:
            break

        print(received)


if __name__ == "__main__":
    app.config.from_object(DevConfig)

    app.run()
