import flask, flask.views
import os
from flask.ext.socketio import SocketIO, emit
from flask import Flask, render_template, session, request
import time
import threading
import random

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.debug = True
socketio = SocketIO(app)

authenticated_tokens = set()
@app.route('/')
def home():
	return render_template('index.html')

@socketio.on('Authenticated')
def auth(token):
	global authenticated_tokens
	authenticated_tokens.add(token)

@app.route('/order_deliver/<token>')
def order_deliver(token):
	if token in authenticated_tokens:
		return render_template("order_deliver.html")
	else:
		return "ERROR, NOT LOGGED IN"


@app.route('/order_deliver/subway/<token>')
def subway(token):
	if token in authenticated_tokens:
		return render_template('subway.html')
	else:
		return "ERROR, NOT LOGGED IN"



def auth(token):
	authenticated_tokens.add(token)


if __name__ == '__main__':
    socketio.run(app)