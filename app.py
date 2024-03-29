from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import desc
import json

DB_URI = os.environ.get('DATABASE_URL')
ROUTE_KEY = os.environ.get('ROUTE_KEY')

app = Flask(__name__)
socketio = SocketIO(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
db = SQLAlchemy(app)


class Leaderboard(db.Model):
    __tablename__ = "leaderboard"
    username = db.Column(db.Text(), primary_key=True)
    score = db.Column(db.Integer)

    def __init__(self, username, score):
        self.username = username
        self.score = score


db.create_all()
db.session.commit()


@app.route("/")
def index():
    leaderboard = Leaderboard.query.order_by(desc(Leaderboard.score))

    return render_template('index.html', leaderboard=leaderboard)


@app.route("/js")
def wsjs():
    leaderboard = Leaderboard.query.order_by(desc(Leaderboard.score))
    leaderboard_json = []

    for user in leaderboard:
        temp = [user.username, user.score]
        leaderboard_json.append(temp)

    return render_template('websocketsjs.html', leaderboard=leaderboard_json)


@app.route("/{}/add".format(ROUTE_KEY), methods=['POST'])
def insert_user():
    request_json = request.get_json()
    if "player" not in request_json.keys() or "score" not in request_json.keys():
        return "Error - missing key."
    else:
        u = Leaderboard(request_json['player'], request_json['score'])
        db.session.add(u)
        db.session.commit()

        leaderboard = Leaderboard.query.order_by(desc(Leaderboard.score))
        leaderboard_json = []

        for user in leaderboard:
            temp = [user.username, user.score]
            leaderboard_json.append(temp)

        socketio.emit('new_player', leaderboard_json)
        return "user inserted successfully"


@app.route("/{}/update".format(ROUTE_KEY), methods=['POST'])
def update_score():
    request_json = request.get_json()
    try:
        player = Leaderboard.query.filter_by(username=request_json['player']).first()
        player.score = request_json['score']
        db.session.commit()
    except Exception as e:
        return "Error: {}".format(e)
    return "Score updated successfully."


@app.route("/{}/removeuser".format(ROUTE_KEY), methods=['POST'])
def delete_user():
    request_json = request.get_json()
    if "player" not in request_json.keys():
        return "Error, missing player key"
    else:
        player = Leaderboard.query.filter_by(username=request_json['player']).first()
        db.session.delete(player)
        db.session.commit()

        return "Player {} deleted from database".format(request_json['player'])


@app.route("/{}/clear".format(ROUTE_KEY), methods=['POST'])
def clear_lb():
    leaderboard = Leaderboard.query.all()
    for player in leaderboard:
        db.session.delete(player)
        db.session.commit()

    return "leaderboard cleared successfully"


@app.route("/{}/get_lb".format(ROUTE_KEY), methods=['GET'])
def return_lb():
    leaderboard = Leaderboard.query.order_by(desc(Leaderboard.score))
    leaderboard_json = []

    for user in leaderboard:
        temp = [user.username, user.score]
        leaderboard_json.append(temp)

    return Response(json.dumps(leaderboard_json),  mimetype='application/json')


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5858)
