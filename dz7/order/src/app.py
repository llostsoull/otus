import os
import json

from flask import Flask, request, Response
import requests

app = Flask(__name__)

config = {
    'DATABASE_URI': os.environ.get('DATABASE_URI', ''),
}

from sqlalchemy import create_engine
engine = create_engine(config['DATABASE_URI'], echo=True)

@app.route('/order')
def me():
    if not 'X-UserId' in request.headers:
        return "Not authenticated"
    userId = request.headers['X-UserId']

    rv = []
    with engine.connect() as connection:
        result = connection.execute(
            "select * from user_order "
            "where user_id={} order by created desc".format(userId))
        rv = result.fetchall()

    return Response(json.dumps([(dict(row.items())) for row in rv], ensure_ascii=False, indent=4, sort_keys=True, default=str), mimetype='application/json') 

@app.route("/order", methods=["POST"])
def createOrder():
    if not 'X-UserId' in request.headers:
        return "Not authenticated"
    userId = request.headers['X-UserId']
    request_data = request.get_json()
    amount = request_data['amount']
    with engine.connect() as connection:
        result = connection.execute(
            """
            insert into user_order (user_id, amount)
            values ('{}', '{}') returning *;
            """.format(userId, amount)).first()

    return Response(json.dumps((dict(result.items())), ensure_ascii=False, indent=4, sort_keys=True, default=str), mimetype='application/json')

@app.route("/order/<int:order_id>/pay", methods=["PUT"])
def updateMe(order_id):
    if not 'X-UserId' in request.headers:
        return "Not authenticated"

    userId = request.headers['X-UserId']
    data = {}
 
    with engine.connect() as connection:
        result = connection.execute(
            "select amount, status from user_order "
            "where id={} and user_id={}".format(order_id, userId)).first()
        if result is None :
            return buildError("Order not found")

        status = result['status']
        amount = result['amount']
        if status != "Pending":
            return buildError("Order wrong state")

        billing_api_url = "http://billing.order.svc.cluster.local:9000/billing/change"
        dataBulling = {
            "reason": "order payment #" + str(order_id),
            "amount": amount * -1
        }
        billingResponse = requests.post(billing_api_url, headers=request.headers, json=dataBulling)

        billingJson = billingResponse.json()
        newState = ''
        if billingJson["status"] == "OK" :
            print('NICE need update state order')
            newState = 'Processing'
        else:
            print('NICE need update state order')
            newState = 'Failed'

        # update ORDER STATE
        connection.execute(
            """
            update user_order set
                status = '{}' where user_id={} and id={};
            """.format(newState, userId, order_id))

        # SEND Notification
        notification_api_url = "http://notification.order.svc.cluster.local:9000/notification"
        dataNotification = {
            "message": "order #" + str(order_id) + " " + newState
        }
        noticeResponse = requests.post(notification_api_url, headers=request.headers, json=dataNotification)

        data["notification"] = noticeResponse.json()
        data["billing"] = billingResponse.json()

    return data  


def buildError(message):
    data = {}
    data["status"] = "ERROR"
    data["message"] = message
    return data;

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80', debug=True)
