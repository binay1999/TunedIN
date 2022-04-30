from flask import Flask
from flask_pymongo import PyMongo
from bson.json_util import dumps
from flask import jsonify, request
from flask import session
from flask_session import Session
import json
#initializing the app and mongodb
app = Flask(__name__)
app.secret_key = "secretkey"
app.config['MONGO_URI'] = "mongodb://localhost:27017/TunedIn"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
mongo = PyMongo(app)
#Route for signup
@app.route('/add',methods=['POST'])
def add_user():
    _json  = request.json
    _username = _json["username"]
    if not mongo.db.Credentials.find_one({'username':_username}):
        _password = _json["password"]
        if request.method == 'POST':
            id1 = mongo.db.Credentials.insert_one({"username":_username,"password":_password})
            del _json["password"]
            id2 = mongo.db.Users.insert_one(_json)
            resp = jsonify("User added successfully")
            resp.status_code = 200
            return resp
        else:
            return not_found()
    else:
        resp = jsonify("Username already exists!")
        resp.status_code = 409
        return resp
#Route for getting data of a user
@app.route('/user/<username>',methods = ['GET'])
def user(username):
    if session.get("username") == username:
        user = mongo.db.Users.find_one({'username':username})
        resp = dumps(user)
        return resp
    else:
        resp = jsonify("Unauthorized Access")
        resp.status_code = 401
        return resp
#Route for login
@app.route('/login',methods=['POST','GET'])
def login():
    _json = request.json
    _username = _json["username"]
    _password = _json["password"]
    #check if this present in db
    var = mongo.db.Credentials.find_one({'username': _username,'password': _password})
    if var:
        session["username"] = _username
        resp = jsonify("Login Successful")
        resp.status_code = 200
        return resp
    else:
        resp = jsonify("Username and password does not match!")
        resp.status_code = 401
        return resp
#Route for updating a user data
@app.route('/update/<username>',methods=['PUT'])
def update_user(username):
    if session.get("username") == username:
        _json = request.json
        if request.method == 'PUT' and _json['username']== username:
            mongo.db.Users.update_one({'username':username},{'$set': _json})
            resp = jsonify("User updated succesfully")
            return resp
        else:
            return not_found()
    else:
        resp = jsonify("Unauthorized Access")
        resp.status_code = 401
        return resp
#Route for logging out
@app.route("/logout/<username>")
def logout(username):
    if session.get("username") == username:
        session["username"] = None
        resp = jsonify("You are logged out")
        resp.status_code = 200
        return resp
    else:
        resp = jsonify("Already logged out")
        resp.status_code  = 200
        return resp
#Route for uploading resume
@app.route("/upload/<username>",methods=['PUT'])
def upload_resume(username):
    if request.method == 'PUT' and  session.get("username") == username:
        if 'input_file' in request.files:
            input_file = request.files['input_file']
            mongo.save_file(input_file.filename,input_file)
            mongo.db.Users.update_one({"username" :username},{'$set' : {'resume':input_file.filename}})
            resp = jsonify("Resume Uploaded !")
            resp.status_code = 200
            return resp
        else:
            resp = jsonify(request.files)
            resp.status_code = 200
            return resp
    else:
         resp = jsonify('login to upload resume')
         resp.status_code = 401
         return resp
#Route for sending a connection request
@app.route("/send",methods = ['POST'])
def send_request():
    if request.method == 'POST':
        _json = request.json
        if session.get("username") == _json["invitor"]:
            _invitee = _json["invitee"] 
            _status = _json["status"]
            _invitor = session.get("username")
            if not (mongo.db.Users.find_one({'username':_invitee}) and mongo.db.Invitations.find_one({"invitee": _invitee, "invitor": _invitor, "status": "accepted" })):
                id = mongo.db.Invitations.insert_one( {"invitee": _invitee, "invitor": _invitor, "status":_status })
                resp = jsonify("invitation sent")
                resp.status_code = 200
                return resp
            else:
                resp = jsonify("no user exist or conncection already accepted")
                resp.status_code = 409
                return resp
        else:
            resp = jsonify("Please Login to send connection request")
            resp.status_code = 401
            return resp
    else:
        return not_found()
#Route for accepting a connection request
@app.route("/accept",methods = ['PUT'])
def accept_request():
    if request.method == 'PUT' :
        _json = request.json
        if session.get("username")== _json["invitee"]:
            _invitee = session.get("username") 
            _invitor = _json["invitor"]
            if not mongo.db.Invitations.find_one({"invitee": _invitee, "invitor": _invitor, "status": "accepted" }):
                id = mongo.db.Invitations.update_one({"invitor" :_invitor},{'$set' :{"invitee": _invitee, "invitor": _invitor, "status":"accepted"}})
                resp = jsonify("invitation accepted")
                resp.status_code = 200
                return resp
            else:
                resp = jsonify("Request already accepted")
                return resp
        else:
            resp = jsonify("Please Login to accept connection request")
            resp.status_code = 401
            return resp
    else:
        return not_found()
#Route for search - with autocomplete feature 
@app.route("/search",methods = ['GET'])
def search():
    if session.get("username"):
        _json = request.json
        key_list = list(_json.keys())
        search_list = []
        found_list = []
        return_list = []
        names_rec = []
        for key in key_list:
            search_dict = {}
            search_dict[key] = _json[key]
            if key == "skills":
               search_dict = {}
               search_dict["skills"] =  { "$in": _json[key]}
            if key == "firstname":
                all_name_details = mongo.db.Users.find({ key: { "$regex": f'^{_json[key]}',"$options":"i" } } )
                for detail in all_name_details:
                    names_rec.append(detail.get("firstname"))
                return_list.append(names_rec)
            search_list.append(search_dict)
        if search_list:
            found_list = list(mongo.db.Users.find({"$and":[{ "$and": search_list }, search_dict] } ))
            if found_list:
                return_list.append(found_list)
        resp = dumps(return_list)
        return resp
    else:
        resp = jsonify("Please Login to search other users")
        resp.status_code = 401
        return resp
#Route for deleting a user
@app.route('/delete/<username>',methods=['DELETE'])
def delete_user(username):
    if session.get("username") == username:
        _json = request.json
        _password = _json["password"]
        if mongo.db.Credentials.find_one({'username':username,'password':_password}):
            mongo.db.Users.delete_one({'username':username})
            mongo.db.Credentials.delete_one({'username':username})
            resp = jsonify("User deleted successfully")
            resp.status_code = 200
            return resp
        else:
            resp = jsonify("Incorrect Password")
            resp.status_code = 401
            return resp

    else:
        resp = jsonify("Unauthorized Access")
        resp.status_code = 401
        return resp

@app.errorhandler(404)
def not_found(error = None):
    message = {
        'status':404,
        'message':'Not Found' + request.url
    }
    resp = jsonify(message)
    return resp

if __name__ == '__main__':
    app.run(debug=True)  #debug=True automatically restarts the application if we make any changes

