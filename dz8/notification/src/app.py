import os
import json

from flask import Flask, request, Response

app = Flask(__name__)

config = {
    'DATABASE_URI': os.environ.get('DATABASE_URI', ''),
}

from sqlalchemy import create_engine
engine = create_engine(config['DATABASE_URI'], echo=True)

@app.route('/notification')
def me():
    if not 'X-UserId' in request.headers:
        return "Not authenticated"
    userId = request.headers['X-UserId']

    rv = []
    with engine.connect() as connection:
        result = connection.execute(
            "select id, message, created from notification "
            "where user_id={} order by created desc".format(userId))
        rv = result.fetchall()

    return Response(json.dumps([(dict(row.items())) for row in rv], ensure_ascii=False, indent=4, sort_keys=True, default=str), mimetype='application/json')

@app.route("/notification", methods=["POST"])
def userNotice():
    if not 'X-UserId' in request.headers:
        return "Not authenticated"
    userId = request.headers['X-UserId']
    request_data = request.get_json()
    message = request_data['message']
    with engine.connect() as connection:
        result = connection.execute(
            """
            insert into notification (user_id, message)
            values ('{}', '{}') returning id;
            """.format(userId, message)).first()
        id_ = result['id']
    data = {}
    data['id'] = id_
    data['message'] = message
    data['status'] = 'OK'

    return data

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80', debug=True)
