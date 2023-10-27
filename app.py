# Import the dependencies.
import numpy as np
import datetime as dt
#from relativedelta import relativedelta

import sqlalchemy

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the tables
measurement = Base.classes.measurement
stations = Base.classes.station


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
        f"Available Routes:<br/>"
        f"/api/v1.0/prcp<br/>"
        f"/api/v1.0/names<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date  format MMDDYYYY.</p>"
    )


@app.route("/api/v1.0/prcp")
def prcp():

# Calculate the date 1 year ago from • last date in database
    prev_year = dt.date (2017, 8, 23) - dt.timedelta (days=365)
    # Perform a query to retrieve the data and precipitation scores
    #  for the last year
    precipitation = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= prev_year).all ()

    session.close()

    # Dict with date as the key and prep as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)


@app.route("/api/v1.0/names")
def names():

#"Return a list of stations."'"
    results = session.query (stations.station,stations.name).all ()

    session.close()

    # Dict with name as the key and location as the value
    station_list = {station: name for station, name in results}

    # Unravel• results into a 1D array and convert to a list
    name_list = list(np.ravel(station_list))

    #  return jsonify(list(np.ravel(station_list))
    return jsonify(name_list)

@app.route("/api/v1.0/tobs")
def tobs(): 

#Query the dates and temperature observations of the most-active station for the previous year of data.
    prev_year = dt.date (2017, 8, 23) - dt.timedelta (days=365)
    most_active = session.query(measurement.date,measurement.tobs).filter(measurement.station == 'USC00519281', measurement.date >= prev_year).all()

    session.close()

# Unravel results into a 1D array and convert to a list and return them
    return jsonify(list(np.ravel(most_active)))


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_or_end(start=None, end=None):

    # Get min, max and average temps
    stats_temp = [func.min(measurement,tobs), func.avg(measurement, tobs), func.max(measurement,tobs)]

    if not end:

        start = dt.datetime.strptime(start, "%m%d%Y")
        temp_results = session.query(*stats_temp).\
            filter(measurement.date >= start).all()

        session.close()

        temps_start = list(np.ravel(temp_results))
        return jsonify(temps_start)

    # user enters start and stop fields
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    results_start_stop = session.query(*stats_temp).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()

    session.close()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results_start_stop))
    return jsonify(temps=temps)

# Define main behavior
if __name__ == '__main__':
    app.run(debug=True)


