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
    """List all available api routes."""
    return (
        f"Welcome to my homepage! Please see available listed routes below.<br/><br/> "
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/mm-dd-yyyy<br/>"
        f"/api/v1.0/mm-dd-yyyy/mm-dd-yyyy"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    session = Session(engine)
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago)
    precip = {date: prcp for date, prcp in precipitation}
    session.close()
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    stations_query = session.query(Station.station).all()
    station_list = list(np.ravel(stations_query))
    session.close()
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    most_active_station = session.query(Measurement.station, func.count(Measurement.station).label("station_count")).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).\
    first()
        
    most_active_past_year = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= year_ago).\
    filter(Measurement.station == most_active_station[0]).all()
    
    most_active_temp_list = [(tobs) for date, tobs in most_active_past_year]
    
    session.close()
    return jsonify (most_active_temp_list)
    
if __name__ == "__main__":
    app.run(debug=True)