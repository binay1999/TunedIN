from elasticsearch import Elasticsearch
from flask import Flask
from flask import jsonify, request, session
import json
import logging.config
from logging.handlers import RotatingFileHandler
import redis
import mapping
import settings

logger = logging.getLogger("Rotating Log")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(settings.setting["log_file_name"], maxBytes=500, backupCount=2)

logger.addHandler(handler)

es = Elasticsearch(HOST=settings.setting["HOST"], PORT=settings.setting["PORT"])

es.indices.create(index="tuned_in", ignore=400)
es.indices.put_mapping(index="tuned_in",
                       doc_type="users",
                       body=mapping.map_body,
                       include_type_name=True)
app = Flask(__name__)
app.secret_key = "secretkey"
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')


@app.route('/add', methods=['POST'])
def add_user():
    _json = request.json
    _username = _json["username"]
    _password = _json["password"]
    if request.method == 'POST':
        source_query = {
            "query": {
                "match": {
                    "username": _username
                }
            }

        }
        res = es.search(index="tuned_in", doc_type="users", body=source_query)
        if len(res["hits"]["hits"]) == 0:
            logger.info(f" API endpoint: /add. {_username} added to the database!")
            es.index(index="tuned_in", doc_type="users", body=_json)
            resp = jsonify("User added successfully")
            resp.status_code = 200
            return resp
        else:
            logger.warning(f" {_username} can't be added to the database. Username already exists!")
            resp = jsonify("User already exists")
            resp.status_code = 200
            return resp

    else:
        logger.warning("HTTP method not POST")
        return not_found


@app.route('/login', methods=['POST', 'GET'])
def login():
    _json = request.json
    _username = _json["username"]
    _password = _json["password"]
    source_query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "username": _username
                        }
                    },
                    {
                        "match": {
                            "password": _password
                        }
                    }

                ]
            }
        }
    }
    # check if this present in db
    res = es.search(index="tuned_in", doc_type="users", body=source_query)
    if len(res["hits"]["hits"]) == 1:
        session["username"] = _username
        logger.info(f" API endpoint: /login. {_username} logged in!")
        resp = jsonify("Login Successful")
        resp.status_code = 200
        return resp
    else:
        logger.warning(f" API endpoint: /add. {_username} can't login due to cred mismatch!")
        resp = jsonify("Username and password does not match!")
        resp.status_code = 401
        return resp


@app.route('/user', methods=['GET'])
def user():
    res = es.search(index="tuned_in", doc_type="users", body={"query": {"match_all": {}}})
    user = res["hits"]["hits"]
    resp = json.dumps(user)
    return res


@app.route('/update/<_id>', methods=['PUT'])
def update_user(_id):
    _json = request.json
    if request.method == 'PUT':
        logger.info(f" {_id} updated details: {_json}")
        es.update(index="tuned_in", doc_type="users", id=_id, body={"doc": _json})
        resp = jsonify("User updated successfully")
        return resp
    else:
        return not_found()


@app.route("/logout/<username>")
def logout(username):
    if session.get("username") == username:
        session["username"] = None
        logger.info(f"{username} logged out!")
        resp = jsonify("You are logged out")
        resp.status_code = 200
        return resp
    else:
        logger.info(f"{username} already logged in!")
        resp = jsonify("Already logged out")
        resp.status_code = 200
        return resp


@app.route("/send", methods=['POST'])
def send_request():
    _json = request.json
    if request.method == 'POST':
        if session.get("username") == _json["invitor"]:
            i = _json["invitor"]
            j = _json["invitee"]
            logger.info(f"{i} sent invitation to {j}")
            es.index(index="invitations", doc_type="users", body=_json)
            resp = jsonify("invitation sent")
            resp.status_code = 200
            return resp
        else:
            logger.warning(f"/send : not log in")
            resp = jsonify("not logged in")
            resp.status_code = 400
            return resp


@app.route("/accept", methods=['POST'])
def accept_request():
    _json = request.json
    if request.method == 'POST':
        if session.get("username") == _json["invitee"]:
            i = _json["invitor"]
            j = _json["invitee"]
            logger.info(f"{i} accepted invitation from {j}")
            es.index(index="invitations", doc_type="users", body=_json)
            resp = jsonify("invitation accepted")
            resp.status_code = 200
            return resp
        else:
            logger.warning(f"/accept : not log in")
            resp = jsonify("not logged in")
            resp.status_code = 400
            return resp


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found' + request.url
    }
    resp = jsonify(message)
    return resp



