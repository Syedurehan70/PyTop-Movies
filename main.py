from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies-collection.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Bootstrap(app)


class EditForm(FlaskForm):
    rating = StringField('Your rating out of 10 e.g: 7.5', validators=[DataRequired()])
    review = StringField('Your Review')
    submit = SubmitField('Done')


class AddForm(FlaskForm):
    new_movie = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description =  db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(250))
    img_url = db.Column(db.String(250), nullable=False)


db.create_all()
#
# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )

# db.session.add(new_movie)
# db.session.commit()


@app.route("/")
def home():
    # reading all data in database, and sorting them in descending rating order
    all_movies = Movie.query.order_by(Movie.rating.desc()).all()

    # showing the rankings from here
    i = 1
    for movie in all_movies:
        movie.ranking = i
        i += 1
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route('/edit', methods=['POST', 'GET'])
def editing():
    form = EditForm()
    # selecting a movie to update
    movie_id = request.args.get('id')
    movie_selected = Movie.query.get(movie_id)

    if form.validate_on_submit():

        # update record
        movie_selected.rating = float(form.rating.data)
        movie_selected.review = form.review.data
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('edit.html', movie=movie_selected, form=form)


@app.route('/delete')
def delete():
    movie_id = request.args.get('id')

    # Deleting a selected book using ID
    movie_selected = Movie.query.get(movie_id)
    db.session.delete(movie_selected)
    db.session.commit()
    return redirect(url_for('home'))


# API IMPORTANT ELEMENTS
API_URL = "https://api.themoviedb.org/3/search/movie"
API_KEY = os.environ.get("api_key")
request_token = "8e5d085b6955f2f0926200fb8bcabeaf26c3849d"


@app.route('/add', methods=['POST', 'GET'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        title = form.new_movie.data

        parameters = {
            "api_key": API_KEY,
            "query": title,
        }
        response = requests.get(url=API_URL, params=parameters)
        response.raise_for_status()
        data = response.json()['results']

        return render_template('select.html', data=data)
    return render_template('add.html', form=form)


@app.route('/find')
def find_movie():

    # updating movie in database
    movie_id = request.args.get('id')
    if movie_id:
        MOVIE_INFO_URL = f"https://api.themoviedb.org/3/movie/{movie_id}"

        parameters = {
            "api_key": API_KEY,
            "language": "en-US",
        }

        response = requests.get(url=MOVIE_INFO_URL, params=parameters)
        response.raise_for_status()
        data = response.json()

        # adding data in database
        new_movie = Movie(
            title=data['title'],
            year=data['release_date'].split('-')[0],
            description=data['overview'],
            img_url="https://image.tmdb.org/t/p/w500/" + data['poster_path']
        )
        db.session.add(new_movie)
        db.session.commit()

        return redirect(url_for('editing', id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
