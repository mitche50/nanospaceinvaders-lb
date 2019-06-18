from flask import Flask, render_template, url_for, request
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
import os
from flask_heroku import Heroku

DB_URI = os.environ.get('DATABASE_URL')
ROUTE_KEY = os.environ.get('ROUTE_KEY')

app = Flask(__name__)
socketio = SocketIO(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
heroku = Heroku(app)
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
    from sqlalchemy import desc

    leaderboard = Leaderboard.query.order_by(desc(Leaderboard.score))

    return render_template('index.html', leaderboard=leaderboard)


@app.route("/js")
def wsjs():
    from sqlalchemy import desc

    leaderboard = Leaderboard.query.order_by(desc(Leaderboard.score))
    leaderboard_json = []
    temp = []

    for user in leaderboard:
        temp.clear()
        temp.append(user.username)
        temp.append(user.score)
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
        socketio.emit('new_player', {'player': request_json['player'],
                                     'score': request_json['score']
                                     })
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


@socketio.on('connect')
def test_connect():
    print("user connected.")
    emit('my response', {'data': 'Connected'})


if __name__ == "__main__":
    socketio.run(app)
