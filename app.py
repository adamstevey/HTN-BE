from flask import Flask, request, Response
from db import DB
import json

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
db = DB("hackathon.db")
db.populate_db()

@app.route("/users/")
@app.route("/users/<user_id>", methods=['GET', 'PUT'])
def users(user_id = None):
    if user_id:
        # User Information
        if request.method == 'GET':
            return Response(json.dumps(json.loads(db.get_hacker(user_id)), indent=2), status=200, mimetype='application/json')
        #Update User Information
        elif request.method == 'PUT':
            data = json.loads(request.data)
            res = db.update_hacker(hacker_id=user_id, data=data)
            return Response(json.dumps(json.loads(res)), status=201, mimetype='application/json')

    elif not user_id:
        # List all users
        if request.method == 'GET':
            return Response(json.dumps(json.loads(db.list_hackers()), indent=2), status=200, mimetype='application/json')

@app.route("/skills/")
def skills():
    args = request.args
    min_frequency = args.get('min_frequency')
    max_frequency = args.get('max_frequency')
    res = str(db.list_skill_frequencies(min=min_frequency if min_frequency else 0, max=max_frequency if max_frequency else db.num_hackers()))
    return Response(json.dumps(json.loads(res), indent=2), status=200, mimetype='application/json')

@app.route("/scan/", methods=["POST"])
def scan():
    data = json.loads(request.data)
    try:
        event_id = data['event_id']
        hacker_id = data['hacker_id']
    except:
        return "Invalid Request. See Documentation"
    res = json.dumps(json.loads(db.handle_scan(event_id=event_id, hacker_id=hacker_id)), indent=2)
    return Response(res, status=200, mimetype='application/json')

@app.route("/events/")
@app.route("/events/<event_id>")
def events(event_id=None):
    if event_id:
        # Event Information
        return Response(json.dumps(json.loads(db.get_event(event_id)), indent=2), status=201, mimetype='application/json')
    else:
        # List Events
        res = json.dumps(json.loads(db.list_events()), indent=2)
        return Response(res, status=201, mimetype='application/json')

@app.route("/register/<user_id>", methods=['PUT'])
def register(user_id=None):
    res = json.dumps(json.loads(db.handle_registration(hacker_id=user_id)), indent=2)
    return Response(res, status=201, mimetype='application/json')

if __name__ == '__main__':
    app.run(port=3000, debug=False)
