import os
import json

from flask import Flask, request, Response

app = Flask(__name__)

config = {
    'DATABASE_URI': os.environ.get('DATABASE_URI', ''),
}

from sqlalchemy import create_engine
engine = create_engine(config['DATABASE_URI'], echo=True)

def qtyItem(key_storage_item):
    res = 0
    with engine.connect() as connection:
        result = connection.execute(
            "select key_storage_item, SUM(qty) as qty from storage_items_qty "
            "where key_storage_item={} group by key_storage_item".format(key_storage_item)).first()
        if result != None :
            res = result['qty']
    return res

@app.route('/storage')
def storage():
    if not 'X-UserId' in request.headers:
        return "Not authenticated"

    rv = []
    with engine.connect() as connection:
        result = connection.execute(
            "select si.id, si.name, qty.qty, qty.last_update from storage_items si left join "
                "(SELECT key_storage_item, SUM(qty) as qty, max(created) as last_update FROM storage_items_qty GROUP BY key_storage_item) qty"
                " ON si.id=qty.key_storage_item ")
        rv = result.fetchall()

    return Response(json.dumps([(dict(row.items())) for row in rv], ensure_ascii=False, indent=4, sort_keys=True, default=str), mimetype='application/json')

@app.route('/storage/reject', methods=["POST"])
def reject():
    if not 'X-UserId' in request.headers:
        return "Not authenticated"
    request_data = request.get_json()
    order_id = request_data['order_id']
    with engine.connect() as connection:
        result = connection.execute(
            """
            delete from storage_items_qty where order_id = {};
            """.format(order_id))

    data = {}
    data["status"] = "OK"
    return data

@app.route("/storage/change", methods=["POST"])
def change():
    if not 'X-UserId' in request.headers:
        return "Not authenticated"
    userId = request.headers['X-UserId']
    request_data = request.get_json()
    

    data = []
    with engine.connect() as connection:
        transaction = connection.begin()
        for obj in request_data:
            key_storage_item = obj['key_storage_item']
            reason = obj['reason']
            qty = obj['qty']
            
     
            if qty < 0 :
                cqty = qtyItem(key_storage_item)

                if cqty < abs(qty):
                    transaction.rollback()
                    return buildError("storage qty < qty (" + str(cqty) + " < " + str(abs(qty)) + ")")

            if 'order_id' not in obj :
                q =  """
                insert into storage_items_qty (key_storage_item, reason, qty)
                values ({}, '{}', {}) returning *;
                """.format(key_storage_item, reason, qty)
            else:
                order_id = obj['order_id']
                q =  """
                insert into storage_items_qty (key_storage_item, reason, qty, order_id)
                values ({}, '{}', {}, {}) returning *;
                """.format(key_storage_item, reason, qty, order_id)

            result = connection.execute(q).first()
            if result is None :
                transaction.rollback()
                return buildError("!storage_items_qty")

            data.append(json.loads(json.dumps(dict(result.items()), ensure_ascii=False, indent=4, sort_keys=True, default=str)))
        transaction.commit()
        dataResp = {}
        dataResp["status"] = "OK"
        dataResp["data"] = data
        return dataResp


def buildError(message):
    data = {}
    data["status"] = "ERROR"
    data["message"] = message
    return data;   

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80', debug=True)
