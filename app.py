from flask import Flask, render_template, url_for
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
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text())
    score = db.Column(db.Integer)

    def __init__(self, username, score):
        self.username = username
        self.score = score


db.create_all()
db.session.commit()


@app.route("/")
def hello():
    u = Leaderboard("andrew", 1000)
    db.session.add(u)
    db.session.commit()
    return render_template('index.html')


if __name__ == "__main__":
    app.run()
