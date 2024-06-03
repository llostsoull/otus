import os
import json

from flask import Flask, request, Response
from datetime import date, datetime, time, timedelta

app = Flask(__name__)

config = {
    'DATABASE_URI': os.environ.get('DATABASE_URI', ''),
}

from sqlalchemy import create_engine
engine = create_engine(config['DATABASE_URI'], echo=True)

@app.route('/delivery/person')
def person():
    if not 'X-UserId' in request.headers:
        return "Not authenticated"

    rv = []
    with engine.connect() as connection:
        result = connection.execute(
            "select * from delivery_person ")
        rv = result.fetchall()

    return Response(json.dumps([(dict(row.items())) for row in rv], ensure_ascii=False, indent=4, sort_keys=True, default=str), mimetype='application/json')


@app.route('/delivery/reserve', methods=["POST"])
def reserve():
    if not 'X-UserId' in request.headers:
        return "Not authenticated"

    request_data = request.get_json()
    datetimedelivery = request_data['datetime']

    with engine.connect() as connection:
        result = connection.execute(
            "select * from delivery_person where "
            "    id not in ("
            "            select key_delivery_person from reserve_delivery_person "
            "            where status='OK' and ('{}' BETWEEN datetime_from AND datetime_to)" 
            "            group by key_delivery_person"
            "        ) limit 1".format(datetimedelivery)).first()
        if result is None :
            return buildError("Нет доставщиков")

        dp = result["id"]
        dtFrom = datetime.strptime(datetimedelivery, '%Y-%m-%d %H:%M:%S.%f+00')
        dtTo = dtFrom + timedelta(minutes=30)
        resultTime = connection.execute(
            """
            insert into reserve_delivery_person (key_delivery_person, datetime_from, datetime_to, status)
                values ({}, '{}', '{}', 'OK') returning *;
            """.format(dp, dtFrom, dtTo)).first()
        if resultTime is None :
            return buildError("!reserve_delivery_person")
        
        dataResp = {}
        dataResp["status"] = "OK"
        dataResp["data"] = json.loads(json.dumps(dict(resultTime.items()), ensure_ascii=False, indent=4, sort_keys=True, default=str))
        return dataResp


def buildError(message):
    data = {}
    data["status"] = "ERROR"
    data["message"] = message
    return data;    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80', debug=True)
