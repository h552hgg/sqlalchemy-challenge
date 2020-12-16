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
database_path = "/Users/jonathanrocha/Desktop/SQL Alchemy/Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{database_path}")


# # reflect an existing database into a new model
Base = automap_base()
# # reflect the tables
Base.prepare(engine, reflect=True)

# # Save reference to the table
#Hawaii = Base.classes.hawaii 
Measurement=Base.classes.measurement
Station=Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    print("Server request received for 'Home' page")
    return (f"Welcome to the page about Hawaii <br/>"
            f"Available Routes:<br/>"
            f"/api/v1.0/precipitation <br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            )

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'Precipitation' page...")

    #Create Session
    session = Session(engine)

    #Use a key to establish a year timeframe from datetime
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #Query for Precp data
    #Create a one line query for troubleshooting 
    #prcp_query=session.query(Measurement.prcp,Measurement.date).filter(func.DATE(Measurement.date)>='2017-01-01')
    
    # Use a dictionary to gather the data and organize it
    sel = [Measurement.date,Measurement.prcp
      ]
    prcp_query = session.query(*sel).\
    filter(func.DATE(Measurement.date)>=query_date).\
    group_by(Measurement.date)

    #Close session
    session.close()

    #Convert to dictionary
    dates_prcp=[]

    for prcp,date in prcp_query:
        data_values={}
        data_values["prcp"]=prcp
        data_values["date"]=date
        dates_prcp.append(data_values)

    return jsonify(dates_prcp)

@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'stations' page...")

    #Create Session
    session=Session(engine)

    #Query data
    station=session.query(Station.station).all()

    #Close Session
    session.close()

    #Convert to lise
    stations_all=list(np.ravel(station))
    
    return jsonify(stations_all)

@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'tobs' page...")

    #Create Session
    session=Session(engine)

    #Use a key to establish a year timeframe from datetime
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #Query data
    sel_data =[Measurement.station,
        func.count(Measurement.station),
        func.min(Measurement.tobs), 
        func.max(Measurement.tobs), 
        func.avg(Measurement.tobs)]
    tobs = session.query(*sel_data).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.tobs).desc()).first()

    #Close Session
    session.close()



    return jsonify(tobs)


@app.route("/api/v1.0/<start>")
def daily_normals(start):
    print("Server received request for 'Start Date'page")
    session=Session(engine)

    """Daily Normals.
    
    Args:
        date (str): A date string in the format '%m-%d'
        
    Returns:
        A list of tuples containing the daily normals, tmin, tavg, and tmax
    
    """
    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    return jsonify(session.query(*sel).filter(func.strftime( '%Y-%m-%d', Measurement.date) == start).all()
    )  


@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start, end):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    session=Session(engine)
    return jsonify(session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    )


if __name__ == "__main__":
    app.run(debug=True)


