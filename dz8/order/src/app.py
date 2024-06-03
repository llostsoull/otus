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
def getOrders():
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
    return create_order(request_data, userId)


# ******************* SAGA ********************************
def create_order(order_data, user_id):
    order_id = 0
    try:
        # Шаг 1: Создание заказа
        order_entity = _create_order_in_database(order_data, user_id)
        order_id = int(order_entity["id"])

        # Шаг 2: Резерв на складе
        reserve = _process_reserve(order_id, order_entity)
        
        # Шаг 3: Выполнение платежа
        payment = _process_payment(order_id, order_entity)

        # Шаг 4: Резерв доставки
        delivery = _process_delivery(order_id, order_data) 

        # Шаг 5: Отправка уведомления
        notify = _send_notification(order_id, "Заказ #" + str(order_id) + " Оплечен. ")

        _update_status_order_in_database('Processing', order_id)

        data = order_entity
        data["notification"] = notify
        data["delivery"] = delivery 
        data["payment"] = payment
        data["reserve"] = reserve
        return data
    except Exception as e:
        _handle_saga_failure(order_id)
        data = {}
        data["status"] = "ERROR"
        data["message"] = "Произошла ошибка при оформлении заказа: " + str(e)
        return data

def _update_status_order_in_database(newState, orderId):
    with engine.connect() as connection:
        connection.execute(
            """
            update user_order set
                status = '{}' where id={};
            """.format(newState, orderId))
    return "OK";

def _create_order_in_database(order_data, userId):
    amount = order_data['amount']
    items = order_data['items']
    dt_delivery = order_data['dt_delivery']
    address = order_data['address']
    data = {}
    with engine.connect() as connection:
        transaction = connection.begin()
        result = connection.execute(
            "insert into user_order (user_id, amount, dt_delivery, address)"
            "values ({}, {}, '{}', '{}') returning *;".format(userId, amount, dt_delivery, address)).first()
        orderId = result["id"];
        data = json.loads(json.dumps((dict(result.items())), ensure_ascii=False, indent=4, sort_keys=True, default=str))
        data["items"] = [];

        for obj in items:
            resultItem = connection.execute(
                """
                insert into order_items (key_order, key_item, qty)
                values ({}, {}, {}) returning *;
                """.format(orderId, obj["key_item"], obj["qty"])).first()     
            data["items"].append(json.loads(json.dumps(dict(resultItem.items()), ensure_ascii=False, indent=4, sort_keys=True, default=str)))
        transaction.commit()
    return data

def  _process_reserve(order_id, order_data):
    url = "http://storage.order.svc.cluster.local:9000/storage/change"
    amount = order_data['amount']
    dataPost = []
    for obj in order_data['items']:
        dataPost.append({
            "key_storage_item": obj["key_item"],
            "reason": "По заказу #" + str(order_id),
            "qty": obj["qty"] * -1,
            "order_id": order_id
        })
    resp = requests.post(url, headers=request.headers, json=dataPost)
    data = resp.json()
    
    if data["status"] != "OK" :
        raise Exception(data["message"])
    return data["data"]

def _process_payment(order_id, order_data):
    url = "http://billing.order.svc.cluster.local:9000/billing/change"
    amount = order_data['amount']
    dataPost = {
        "reason": "order payment #" + str(order_id),
        "amount": amount * -1,
        "order_id": order_id
    }
    resp = requests.post(url, headers=request.headers, json=dataPost)
    data = resp.json()
    if data["status"] != "OK" :
        raise Exception(data["message"])
    return data

def _process_delivery(order_id, order_data):
    url = "http://delivery.order.svc.cluster.local:9000/delivery/reserve"
    dataPost = {
        "datetime": order_data['dt_delivery']
    }
    resp = requests.post(url, headers=request.headers, json=dataPost)
    data = resp.json()
    if data["status"] != "OK" :
        raise Exception(data["message"])
    return data["data"]

def _send_notification(order_id, message):
    url = "http://notification.order.svc.cluster.local:9000/notification"
    dataPost = {
        "message": message
    }
    resp = requests.post(url, headers=request.headers, json=dataPost)
    data = resp.json()
    if data["status"] != "OK" :
        raise Exception(data["message"])
    return data    

def _handle_saga_failure(order_id):
    # Вызываем компенсирующие действия для отката предыдущих операций
    _rollback_reserve(order_id)
    _rollback_payment(order_id)
    _rollback_order_creation(order_id)

def _rollback_reserve(order_id):
    url = "http://storage.order.svc.cluster.local:9000/storage/reject"
    dataPost = {
        "order_id": order_id
    }
    resp = requests.post(url, headers=request.headers, json=dataPost)

def _rollback_payment(order_id):
    url = "http://billing.order.svc.cluster.local:9000/billing/reject"
    dataPost = {
        "order_id": order_id
    }
    resp = requests.post(url, headers=request.headers, json=dataPost)

def _rollback_order_creation(order_id):
    # Здесь реализация отмены создания заказа
    _update_status_order_in_database('Failed', order_id)
#****************************************************


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80', debug=True)
