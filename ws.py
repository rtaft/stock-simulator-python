from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@socketio.on('ws')
def handle_message(message):
    print('received message: ' + message)
    socketio.emit(message)

@socketio.on("connect")
def connectServer():
    print("Client connected")
    socketio.emit("connected")

def hello():
    while (True):
        handle_message("hello")
        time.sleep(3)

if __name__ == '__main__':
    t = threading.Timer(3.0, hello)
    t.start()
    socketio.run(app, debug=True)