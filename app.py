import flask, flask.views
import os
from flask.ext.socketio import SocketIO, emit
from flask import Flask, render_template, session, request
import time
import threading
import random
import stripe
import json
import ast

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.debug = True
socketio = SocketIO(app)
map_cid_amount_chargeid = {}
authenticated_tokens = set()
stripe.api_key = "sk_test_b2utQtXmanzlaZXruj50NJ3i"
@app.route('/')
def home():
	return render_template('index.html')

@socketio.on('Authenticated')
def auth(token):
	global authenticated_tokens
	authenticated_tokens.add(token)

@socketio.on('create_customer')
def authenticate_stripe(temp):
	temp = ast.literal_eval(json.dumps(temp))
	print temp["card_token"]
	print temp["name"]
	print "CAME HERE OH YEA"


	# Get the credit card details submitted by the form

	# Create a Customer
	customer = stripe.Customer.create(
	  source=temp["card_token"],
	  description=temp["name"]
	)

	emit("sending_customer_id", customer.id)

@socketio.on('charge')
def charge(data):
	global map_cid_amount_chargeid
	print 'IN CHARGE'
	data = ast.literal_eval(json.dumps(data))
	c_id = data["c_id"]
	total = data["amount"]
	print 'c_id {} Total {}'.format(c_id, total)
	if total:
		print 'About to charge something'
		total = int(total*100)
		charge = stripe.Charge.create(
					amount=total, # in cents
					currency="usd",
					customer=c_id
				)
		print 'Charge created: {}'.format(charge.id)
		map_cid_amount_chargeid[c_id] = (total, charge.id)


@socketio.on('refund')
def refund(customer_id):
	cust_id = customer_id.encode('ascii', 'ignore')
	amount, charge_id = map_cid_amount_chargeid[cust_id]
	print 'charge id: {}'.format(charge_id)
	re = stripe.Refund.create(charge=charge_id)
	del map_cid_amount_chargeid[cust_id]


@app.route('/order_deliver/<token>')
def order_deliver(token):
	if token in authenticated_tokens:
		return render_template("order_deliver.html")
	else:
		return "ERROR, NOT LOGGED IN"

@app.route('/stripe/<token>')
def stripe_card(token):
	if token in authenticated_tokens:
		return render_template("stripe.html")
	else:
		return "IN STRIPE"

@app.route('/waiting/<token>')
def waiting_screen(token):
	if token in authenticated_tokens:
		return render_template("findDeliverer.html")
	else:
		return "IN waiting"

@app.route('/pending_orders/<token>')
def pending_orders(token):
	if token in authenticated_tokens:
		return render_template("available_jobs.html")
	else:
		return "IN waiting"

@app.route('/in_progress/<token>/<orderer_uid>')
def in_progress(token, orderer_uid):
	if token in authenticated_tokens:
		return render_template("inProgress.html")
	else:
		return "IN Progress"

@app.route('/deliveryOnWay/<token>')
def delivery_on_way(token):
	if token in authenticated_tokens:
		return render_template("deliveryOnWay.html")
	else:
		return "IN delivery on way"

@app.route('/stripe_deliverer/<token>')
def stripe_deliverer(token):
	if token in authenticated_tokens:
		return render_template("stripe_deliverer.html")
	else:
		return "IN STRIPE DELIVERER"

@app.route('/order_complete/<token>')
def order_complete(token):
	if token in authenticated_tokens:
		return render_template("orderComplete.html")
	else:
		return "IN order complete"

@app.route('/delivery_complete/<token>')
def delivery_complete(token):
	if token in authenticated_tokens:
		return render_template("delivery_complete.html")
	else:
		return "IN delivery complete"


@app.route('/menu/<token>')
def menu(token):
	print "======"
	print token
	print "======"
	if token in authenticated_tokens:
		return render_template('SubwayMenu.html')
	else:
		return "ERROR, NOT LOGGED IN"

if __name__ == '__main__':
    socketio.run(app)