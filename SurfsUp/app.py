# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
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
Base.prepare(engine, reflect=True)

# Save references to each table
station = Base.classes.station  
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#1
@app.route("/", methods=['GET'])
def start():
  return(
       f"Home Page<br/>"
       f"Available Routes:<br/>"
       f"/api/v1.0/precipitation<br/>"
       f"/api/v1.0/stations<br/>"
       f"/api/v1.0/tobs<br/>"
       f"/api/v1.0/start<br/>"
       f"/api/v1.0/start/end<br/>"
  )
#2
@app.route("/api/v1.0/precipitation", methods=['GET'])
def precipitation():
    session = Session(engine)
    last_twelve_month = dt.date(2017, 8, 23)- dt.timedelta(days=365)
    prcp_results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= last_twelve_month).all()
    session.close()

    output = []
    for date, prcp in prcp_results: 
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        output.append(prcp_dict)

    return jsonify(output)

#3
@app.route("/api/v1.0/stations", methods=['GET'])
def station_jsn():
    results = session.query(station.station).all()
    session.close()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

#4
@app.route("/api/v1.0/tobs")
def temp():
    session = Session(engine)
    last_twelve_month = dt.date(2017, 8, 23)- dt.timedelta(days=365) 

    temp_df = session.query(measurement.tobs).\
    filter(measurement.station == 'USC00519281').\
    filter(measurement.date >= last_twelve_month).all()
    temp = list(np.ravel(temp_df))
    session.close()
    
    return jsonify(temp)




#5
@app.route("/api/v1.0/<start>", methods=['GET']) 
def s_date(start=None): 
    session = Session(engine)
    start = dt.datetime.strptime(start,'%Y-%d-%m')
    act_station = session.query(func.min(measurement.tobs), func.max(measurement.tobs),
                                 func.avg(measurement.tobs)).\
    filter(measurement.date >= start).all()
    list_st = list(np.ravel(act_station))

    session.close()
    return jsonify(list_st)


@app.route("/api/v1.0/<start>/<end>", methods=['GET'])
def temperature_range(start, end):
    session = Session(engine)
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    session.close()
   
    all_tobs = []
    for min_temp, avg_temp, max_temp in results:
        tobs_dict = {}
        tobs_dict["Minimum Temperature"] = min_temp
        tobs_dict["Average Temperature"] = avg_temp
        tobs_dict["Maximum Temperature"] = max_temp
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


if __name__ == "__main__":
    app.run(debug=True)

#################################################
