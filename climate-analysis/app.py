# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt 

from flask import Flask, jsonify
#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
# this is the path that I used in the exploratory analysis
engine = create_engine("sqlite:///../climate-data/hawaii.sqlite") 
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        "<h1>Welcome to Honolulu, Hawaii Climate App!</h1>"
        "<p>Here are the available routes:</p>"
        "<ul>"
        "<li><a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a></li>"
        "<li><a href='/api/v1.0/stations'>/api/v1.0/stations</a></li>"
        "<li><a href='/api/v1.0/tobs'>/api/v1.0/tobs</a></li>"
        "<li>api/v1.0/</li>"
        "<br>Required: Enter start_date as YYYY-MM-DD"
        "<br>e.g., <a href ='/api/v1.0/2017-07-25'>/api/v1.0/2017-07-25</a><br>"
        "<br>Optional: Enter end_date as YYYY-MM-DD"
        "<br>e.g., <a href ='/api/v1.0/2016-09-23/2016-09-24'>/api/v1.0/2016-09-23/2016-10-23</a></li>"
        "</ul>"
    )


# Precipitation Route
@app.route('/api/v1.0/precipitation')
def precipitation():
    # Create the session
    session = Session(engine)

    # Query Setup
    results = session.query(
        Measurement.date,
        Measurement.prcp
    ).filter(
        Measurement.date >= dt.date(2017, 8, 23) - dt.timedelta(days=365)
    ).order_by(Measurement.date).all()

    # Close the session
    session.close()

    # Creating an output list
    output = []

    # Iterating through each record in the results list
    for record in results:
        # Empty dictionary for each record
        # Assigning attributes of each record to the corresponding dictionary key
        prep_dict = {'date': record.date, 'prep': record.prcp}

        # Appending the dictionary information to the output list above
        output.append(prep_dict)

    # Jsonify the output
    return jsonify(output)


# Stations Route
@app.route('/api/v1.0/stations')
def stations():
    # Create the session
    session = Session(engine)

    # Query Setup
    station_list = session.query(Station.station).all()

    # Close the session
    session.close()

    # Creating an output list
    output = []

    # Append each record to the list
    for record in station_list:
        output.append(record.station)

    # Jsonify the output
    return jsonify(output)


# Tobs Route
@app.route('/api/v1.0/tobs')
def tobs():
    # Query to retrieve the most active station
    most_active_station_id = session.query(
        Measurement.station
    ).group_by(
        Measurement.station
    ).order_by(
        func.count(Measurement.station).desc()
    ).first()[0]

    # Query to retrieve the last 12 months of temperature observation data for the most active station
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    temperature_data = session.query(
        Measurement.date, Measurement.tobs
    ).filter(
        Measurement.station == most_active_station_id
    ).filter(Measurement.date >= one_year_ago).all()

    # Convert query results to a list of dictionaries
    temperature_list = [{"Date": date, "Temperature": tobs} for date, tobs in temperature_data]

    # Return the JSON representation of the list of dictionaries
    return jsonify(temperature_list)


# temp_stats_start Route
@app.route('/api/v1.0/<start>')
def temp_stats_start(start):

    # Create the session
    session = Session(engine)

    # Query Setup
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(
        Measurement.date >= start
    ).all()

    # Close the session
    session.close()

    # Create a dictionary
    output = {
        'start_date' : start,
        'TMIN' : results[0][0],
        'TAVG' : results[0][1],
        'TMAX' : results[0][2]
    }

    # Jsonify the output
    return jsonify(output)


# temp_stats_range Route
@app.route('/api/v1.0/<start>/<end>')
def temp_stats_range(start, end):
    session = Session(engine)

    # Query Setup
    results = session.query(
        func.avg(Measurement.tobs),
        func.min(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(
        Measurement.date >= start,
        Measurement.date <= end
    ).all()

    # Close the session
    session.close()

    # Create a dictionary
    output = {
        'start_date': start,
        'end_date': end,
        'TMIN': results[0][0],
        'TAVG': results[0][1],
        'TMAX': results[0][2]
    }

    # Jsonify the output
    return jsonify(output)


if __name__ == "__main__":
    app.run(debug=True)
