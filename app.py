from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
import sys
import json
from flask_heroku import Heroku

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
heroku = Heroku(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://uckuuqvvpuravr:8ed73c5895c2e4ad35a443da461605e85233994efc09b37f6abc78cbb7287f17@ec2-54-235-104-136.compute-1.amazonaws.com:5432/daad1ji37o07ln'
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
    leaderboard = Leaderboard.query.all()

    return render_template('index.html', leaderboard=leaderboard)


@app.route("/BODBAJSDOFE48UAB30/add", methods=['POST'])
def insert_user():
    request_json = request.get_json()
    if "player" not in request_json.keys() or "score" not in request_json.keys():
        return "Error - missing key."
    else:
        u = Leaderboard(request_json['player'], request_json['score'])
        db.session.add(u)
        db.session.commit()
        return "user inserted successfully"


@app.route("/BODBAJSDOFE48UAB30/update", methods=['POST'])
def update_score():
    request_json = request.get_json()
    try:
        player = Leaderboard.query.filter_by(username=request_json['player'])
        player.score = request_json['score']
        db.session.commit()
    except Exception as e:
        return "Error: {}".format(e)
    return "Score updated successfully."


@app.route("/BODBAJSDOFE48UAB30/clear", methods=['POST'])
def clear_lb():
    leaderboard = Leaderboard.query.all()
    for player in leaderboard:
        db.session.delete(player)
        db.session.commit()

    return "leaderboard cleared successfully"


if __name__ == "__main__":
    app.run()
