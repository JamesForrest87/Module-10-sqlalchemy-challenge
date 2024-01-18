# Import the dependencies.
import numpy as np
import datetime as dt
import pandas as pd
import sqlalchemy

from sqlalchemy.ext.automap import automap_base

from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



# #################################################
# # Database Setup
# #################################################
# # create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# # reflect an existing database into a new model
base = automap_base()
# # reflect the tables
base.prepare(autoload_with=engine) 

# # Save references to each table
measurement = base.classes.measurement
station = base.classes.station

# # Create our session (link) from Python to the DB
session = Session(engine)

# #################################################
# # Flask Setup
# #################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
#Homepage and list of available routes
@app.route("/")
def welcome():
    return (
    f"Available Routes:<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/start<br/>"
    f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    
    #One year beginning date
    recent_date = session.query(func.max(measurement.date)).first()[0]
    #Convert the query results from your precipitation analysis last 12 months of data
    twelve_months = dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    twelve_months_str = twelve_months.strftime("%Y-%m-%d")
    twelve_months = session.query(measurement.date, measurement.prcp).filter(measurement.date >= twelve_months_str).all()
    session.close()

    #Convert to a dictionary using date as the key and prcp as the value.
    prcp_dictionary = []

    for date, prcp in twelve_months:
        date_dict = {}
        date_dict["Date"] = date
        date_dict["Precipitation"] = prcp
        prcp_dictionary.append(date_dict)

    return jsonify(prcp_dictionary)

# Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    
    results = session.query(station.name).all()
    session.close()

    return jsonify(list(np.ravel(results)))

#Query the dates and temperature observations of the most-active station for the previous year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    #Twelve months of data
    
    recent_date = session.query(func.max(measurement.date)).first()[0]
    #print (recent_date)
    twelve_months = dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    twelve_months_str = twelve_months.strftime("%Y-%m-%d")

    #Most active station data
    #most_active_station_USC00519281 = session.query(measurement.tobs).filter(measurement.station == 'USC00519281').all()    #.filter(measurement.date >= twelve_months_str).all()
    twelve_months_tobs = session.query(measurement.date, measurement.tobs).filter(measurement.date >= twelve_months_str).filter(measurement.station == 'USC00519281').all()
    #print (most_active_station_USC00519281)
    #Return a JSON list of temperature observations for the previous year.
    return jsonify(list(np.ravel(twelve_months_tobs)))

#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start(start=None,end=None):
    #For start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date
    
    if not end:
        twelve_months_tobs = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).all()
        session.close()
        return jsonify(list(np.ravel(twelve_months_tobs)))
    twelve_months_tobs = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <=end).all()
    session.close()
    return jsonify(list(np.ravel(twelve_months_tobs)))


if __name__=="__main__":
    app.run()

