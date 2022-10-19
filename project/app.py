from urllib.parse import parse_qs

from flask import Flask, request

from project.poll import Poll

app = Flask(__name__)


@app.route("/")
def index():
    # Temporary text

    return '<h1>Methods</h1></br>' \
           'POST /poll/create/ [name:str, options:list]<br/>' \
           'POST /poll/vote/ [poll_id:int, option_id:int]<br/>' \
           'GET /poll/stats/ [poll_id:int]'


@app.route("/poll/create/", methods=['POST'])
def create_poll():
    name = request.form.get('name')
    options = request.form.getlist('options')

    if not options:
        return "The options field cannot be empty.", 422

    poll_id = Poll.create_poll(name, options)

    return {'poll_id': poll_id}


@app.route("/poll/vote/", methods=['POST'])
def vote_poll():
    poll_id = request.form.get('poll_id')
    option_id = request.form.get('option_id')
    ip_address = request.remote_addr

    try:
        status = Poll.vote_poll(poll_id, option_id, ip_address)
        message = 'You have successfully voted!'
        if not status:
            message = 'You have already voted.'

    except TypeError:
        return "Poll not found", 404

    return {'status': status, 'message': message}


@app.route('/poll/stats/', methods=['GET'])
def stats_poll():
    query = parse_qs(request.query_string)

    try:
        poll_id = int(query.get(b'poll_id')[0])
    except (TypeError, IndexError):
        return "Invalid field `poll_id`", 422

    try:
        stats = Poll.stats_poll(poll_id)
    except TypeError:
        return "Poll not found", 404

    return stats
