import os
import json

from flask import Flask, request, Response

app = Flask(__name__)

config = {
    'DATABASE_URI': os.environ.get('DATABASE_URI', ''),
}

from sqlalchemy import create_engine
engine = create_engine(config['DATABASE_URI'], echo=True)

def balance(userId):
    res = 0.0
    with engine.connect() as connection:
        result = connection.execute(
            "select SUM(amount) as balance from user_balance_change "
            "where user_id={} group by user_id".format(userId)).first()
        if result != None :
            res = result['balance']
    return float(res)

@app.route('/billing/reject', methods=["POST"])
def reject():
    if not 'X-UserId' in request.headers:
        return "Not authenticated"
    request_data = request.get_json()
    order_id = request_data['order_id']
    with engine.connect() as connection:
        result = connection.execute(
            """
            delete from user_balance_change where order_id = {};
            """.format(order_id))

    data = {}
    data["status"] = "OK"
    return data

@app.route('/billing/change', methods=["POST"])
def change():
    if not 'X-UserId' in request.headers:
        return "Not authenticated"
    userId = request.headers['X-UserId']
    request_data = request.get_json()
    amount = request_data['amount']
    reason = request_data['reason']
    data = {}

    with engine.connect() as connection:
        if amount < 0 :
            cbalance = balance(userId)

            if cbalance < abs(amount):
                data["status"] = "ERROR"
                data["message"] = "balance < amount (" + str(cbalance) + " < " + str(abs(amount)) + ")"
                return data;

        if 'order_id' not in request_data :
            q = """
            insert into user_balance_change (user_id, amount, reason)
            values ({}, {}, '{}') returning id;
            """.format(userId, amount, reason)
        else:
            q = """
            insert into user_balance_change (user_id, amount, reason, order_id)
            values ({}, {}, '{}', {}) returning id;
            """.format(userId, amount, reason, request_data['order_id'])

        result = connection.execute(q).first()
        id_ = result['id']

        data = request_data
        data['id'] = id_
        data['status'] = "OK"
        data["balance"] = balance(userId)
    return data


@app.route("/billing/history")
def history():
    if not 'X-UserId' in request.headers:
        return "Not authenticated"
    userId = request.headers['X-UserId']

    rv = []
    with engine.connect() as connection:
        result = connection.execute(
            "select created, amount, reason from user_balance_change "
            "where user_id={} order by created desc".format(userId))
        rv = result.fetchall()

    return Response(json.dumps([(dict(row.items())) for row in rv], ensure_ascii=False, indent=4, sort_keys=True, default=str), mimetype='application/json')


@app.route("/billing/current")
def current():
    if not 'X-UserId' in request.headers:
        return "Not authenticated"
    userId = request.headers['X-UserId']    
    data = {};
    data["balance"] = balance(userId)
    return data

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80', debug=True)
