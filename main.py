from flask import Flask, render_template, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, URL
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
Bootstrap(app)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


## Database Table
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    seats = db.Column(db.String(250))
    coffee_price = db.Column(db.String(250))

# db.create_all()

## New Cafe Form
class CafeForm(FlaskForm):
    cafe = StringField('Cafe Name:', validators=[DataRequired()])
    city = StringField("Cafe Location (City):", validators=[DataRequired()])
    location_url = StringField("Google Maps Link (URL):", validators=[DataRequired(), URL()])
    image = StringField("Photo of Cafe (URL):", validators=[DataRequired(), URL()])
    sockets = BooleanField("Power Outlets")
    toilets = BooleanField("Public Bathroom")
    wifi = BooleanField("Free WiFi")
    seating = StringField("Number of Seats:", validators=[DataRequired()])
    price = StringField("Coffee Price:", validators=[DataRequired()])
    submit = SubmitField('Submit')


## Search Form
class SearchForm(FlaskForm):
    city = StringField("Cafe Location (City)")
    sockets = BooleanField("Has Power Outlets")
    toilets = BooleanField("Has Public Bathroom")
    wifi = BooleanField("Free WiFi")
    search = SubmitField('Search')


# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add', methods=["GET", "POST"])
def add_cafe():
    add_form = CafeForm()
    if add_form.validate_on_submit():
        new_cafe = Cafe(
            name=add_form.cafe.data,
            map_url=add_form.location_url.data,
            img_url=add_form.image.data,
            location=add_form.city.data,
            has_sockets=add_form.sockets.data,
            has_toilet=add_form.toilets.data,
            has_wifi=add_form.wifi.data,
            seats=add_form.seating.data,
            coffee_price=add_form.price.data
        )
        db.session.add(new_cafe)
        db.session.commit()
        flash("Cafe Successfully Added!")
        return render_template('add.html', form=add_form)
    return render_template('add.html', form=add_form)


@app.route('/cafes', methods=["GET", "POST"])
def cafes():
    search_form = SearchForm()
    cafe_results = Cafe.query.order_by(Cafe.location).all()
    if search_form.validate_on_submit():
        location = search_form.city.data
        has_wifi = search_form.wifi.data
        has_sockets = search_form.sockets.data
        has_toilet = search_form.toilets.data
        location_exists = Cafe.query.filter_by(location=location).first()
        if location_exists:
            if has_wifi and has_sockets and has_toilet:
                cafe_results = Cafe.query.filter_by(location=location,
                                                    has_wifi=True,
                                                    has_sockets=True,
                                                    has_toilet=True)
            elif has_wifi and has_sockets and not has_toilet:
                cafe_results = Cafe.query.filter_by(location=location,
                                                    has_wifi=True,
                                                    has_sockets=True)
            elif has_wifi and not has_sockets and not has_toilet:
                cafe_results = Cafe.query.filter_by(location=location,
                                                    has_wifi=True)
            elif has_wifi and not has_sockets and has_toilet:
                cafe_results = Cafe.query.filter_by(location=location,
                                                    has_wifi=True,
                                                    has_toilet=True)
            elif not has_wifi and has_sockets and has_toilet:
                cafe_results = Cafe.query.filter_by(location=location,
                                                    has_sockets=True,
                                                    has_toilet=True)
            elif not has_wifi and not has_sockets and not has_toilet:
                cafe_results = Cafe.query.filter_by(location=location)
        elif location == "":
            if has_wifi and has_sockets and has_toilet:
                cafe_results = Cafe.query.filter_by(has_wifi=True,
                                                    has_sockets=True,
                                                    has_toilet=True)
            elif has_wifi and has_sockets and not has_toilet:
                cafe_results = Cafe.query.filter_by(has_wifi=True,
                                                    has_sockets=True)
            elif has_wifi and not has_sockets and has_toilet:
                cafe_results = Cafe.query.filter_by(has_wifi=True,
                                                    has_toilet=True)
            elif has_wifi and not has_sockets and not has_toilet:
                cafe_results = Cafe.query.filter_by(has_wifi=True)
            elif not has_wifi and has_sockets and not has_toilet:
                cafe_results = Cafe.query.filter_by(has_sockets=True)
            elif not has_wifi and not has_sockets and has_toilet:
                cafe_results = Cafe.query.filter_by(has_toilet=True)
        else:
            flash("There are no cafes that meet your criteria. Please try again.")
            cafe_results = Cafe.query.filter_by(location=None)
    return render_template('cafes.html', cafes=cafe_results, form=search_form)


if __name__ == '__main__':
    app.run(debug=True)

