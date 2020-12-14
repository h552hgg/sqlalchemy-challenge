import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

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

    #Query for Precp data
    #Create a one line query for troubleshooting 
    #prcp_query=session.query(Measurement.prcp,Measurement.date).filter(func.DATE(Measurement.date)>='2017-01-01')

    # Use a dictionary to gather the data and organize it
    sel = [Measurement.date,Measurement.prcp
      ]
    prcp_query = session.query(*sel).\
    filter(func.DATE(Measurement.date)>='2017-01-01').\
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

    #Query data
    sel_data = [Measurement.station,Measurement.date,
       func.max(Measurement.tobs)]
    tobs = session.query(*sel_data).\
    filter(func.DATE(Measurement.date)>='2016-01-01').\
    order_by(Measurement.tobs.desc()).all()

    #Close Session
    session.close()



    return jsonify(tobs)


@app.route("/api/v1.0/<key>/<value>")
def start(key,value):
    print("Server received request for 'Start Search' page...")

    #Create Session
    session=Session(engine)
    #Query
    temp = [Measurement.id, 
       func.min(Measurement.tobs), 
       func.max(Measurement.tobs), 
       func.avg(Measurement.tobs)]
    temp_find = session.query(*temp)

    #Close session
    session.close()

    #for x in temp_find:
        #if x[key] == value:
            #return jsonify(x)

    #return jsonify({"error": f"Character with key '{key}' with value '{value}' not found."}), 404
    return jsonify(temp_find)

@app.route("/api/v1.0/<start>/<end>")
def end():
    print("Server received request for 'About' page...")
    return "Welcome to my 'About' page!"




@app.route("/api/v1.0/trial")
def trial():
    print("Server received request for 'trial' page...")
 #Create Session
    session=Session(engine)
    #Query
    temp = [Measurement.station, 
       func.min(Measurement.tobs), 
       func.max(Measurement.tobs), 
       func.avg(Measurement.tobs)]
    temp_find = session.query(*temp).all()

    #Close session
    session.close()


    return jsonify(temp_find)

if __name__ == "__main__":
    app.run(debug=True)


