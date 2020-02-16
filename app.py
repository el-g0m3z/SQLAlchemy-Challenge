from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import datetime as dt
import numpy as np

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Resources/hawaii.sqlite"
db = SQLAlchemy(app)


class DictMixIn:
    def to_dict(self):
        return {
            column.name: getattr(self, column.name)
            if not isinstance(getattr(self, column.name), dt.datetime)
            else getattr(self, column.name).isoformat()
            for column in self.__table__.columns
        }


class Measurement(db.Model, DictMixIn):
    __tablename__ = "measurement"

    date = db.Column(db.Date(), primary_key=True)
    station = db.Column(db.String())
    prcp = db.Column(db.Integer())
    tobs = db.Column(db.Integer())


class Station(db.Model, DictMixIn):
    __tablename__ = "station"

    station = db.Column(db.String(), primary_key=True)
    name = db.Column(db.String())
    latitude = db.Column(db.Integer())
    longitude = db.Column(db.Integer())
    elevation = db.Column(db.Integer())


meas_cols = ["date", "station", "prcp", "tobs"]
station_cols = ["station", "name", "latitude", "longitude", "elevation"]


@app.route("/")
def home():
    # list of links to other routes
    return render_template("index.html")


@app.route("/api/v1.0/precipitation")
def prcp():
    # Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
    # Return the JSON representation of your dictionary.
    prcp_q = Measurement.query.all()
    prcp_d = [{str(p.date):str(p.prcp)} for p in prcp_q]
    return jsonify(prcp_d)


@app.route("/api/v1.0/stations")
def station():
    # Return a JSON list of stations from the dataset.
    stat = Station.query.all()
    return jsonify([s.to_dict() for s in stat])


@app.route("/api/v1.0/tobs")
def tobs():
    # query for the dates and temperature observations from a year from the last data point.
    # Return a JSON list of Temperature Observations (tobs) for the previous year.
    tobs_q = Measurement.query.all()
    date_l = [row.date for row in tobs_q]
    max_date = max(date_l)
    yr_prev = dt.date(max_date.year - 1, max_date.month, max_date.day)
    tobs_d = [{str(t.date):str(t.tobs)} for t in tobs_q if t.date > yr_prev]
    return jsonify(tobs_d)


@app.route("/api/v1.0/dates")
def api():
    # Displays instructions for using dates in url.
    # Clickable link on home page.
    return (
        "Include start date with optional end date to be included after another slash. Example: 2016-08-24/2016-08-31"
    )


cols = ["TMIN", "TMAX", "TAVG"]

@app.route("/api/v1.0/<start>")
def start(start):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    # When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
    data_q = Measurement.query.filter(Measurement.date >= start).all()
    tobs_l = [row.tobs for row in data_q]
    calc = [min(tobs_l),max(tobs_l),np.mean(tobs_l)]
    return jsonify(dict(zip(cols, calc)))

@app.route("/api/v1.0/<start>/<end>")
def end(start, end):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    # When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
    data_q = Measurement.query.filter(Measurement.date.between(start, end)).all()
    tobs_l = [row.tobs for row in data_q]
    calc = [min(tobs_l),max(tobs_l),np.mean(tobs_l)]
    return jsonify(dict(zip(cols, calc)))


if __name__ == "__main__":
    app.run(debug=True)