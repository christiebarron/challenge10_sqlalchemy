# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.sql import desc
import datetime as dt


#################################################
# Database Setup
#################################################

# Create an engine for the chinook.sqlite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

# reflect the tables
Base = automap_base()
Base.prepare(autoload_with=engine)
#Base.classes.keys()

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return(
    f"This is a Climate App API! <br/>"
    f"Available Routes Include: <br/>"
    f"/api/v1.0/precipitation <br/>"
    f"/v1.0/stations<br/>"
    f"/v1.0/tabs<br/>"
    f"/v1.0/<start><br/>"
    f"/v1.0/<start>/end<br/>")

@app.route("/api/v1.0/precipitation")
def precipitation_json():
    """Convert precipitation analysis query results to dictionary.
    last 12 months. date as key, prcp as value"""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    #query the maximum date
    results = session.query(func.max(measurement.date))

    # Calculate the date one year from the last date in data set.
    most_recent = dt.datetime.strptime(results[0][0], '%Y-%m-%d').date()
    one_year = most_recent - dt.timedelta(weeks = 52.1429)

    # Perform a query to retrieve the data and precipitation scores for the last year
    query = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year).all()
    
    #create dictionary
    preciptation_dict = {}

    #save the first column (date) as key, save second collumn (prcp) as value
    for result in query:
        preciptation_dict[result[0]] = result[1]
    
    session.close()

    #return the query as JSON for flask app
    return(jsonify(preciptation_dict))


@app.route("/v1.0/stations")
def station_json():
    """Return JSON list of stations from the dataset"""
    session = Session(engine)

    #query the station
    results = session.query(station.station, station.name, station.latitude, station.longitude, station.elevation).all()

    #save as dictionary
    output = []

    #save parts of output as dictionary
    for station, name, latitude, longitude, elevation in results:
        station_dict = {}
        station_dict['station'] = station
        station_dict['name'] = name
        station_dict['latitude'] = latitude
        station_dict['longitude'] = longitude
        station_dict['elevation'] = elevation
        output.append(station_dict)


    return (jsonify(output))

@app.route("/v1.0/tabs")
def temp_obs_json():
    #"""
    #query dates and temperature observations for most active station for previous year of data
    #return json list of temp obs for previous year
    #"""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    #create a query
    results = session.query(measurement.station, func.count(measurement.station)).\
        group_by(measurement.station).\
        order_by(desc(func.count(measurement.station))).\
        all()

    #extract the station with highest number of observations
    active_station = results[0][0]

    #select the station
    sel = [measurement.station, measurement.tobs]

    #query the selection, filtering to only include the most active station
    results = session.query(*sel).\
        filter(measurement.station == active_station).\
        all()
    
    #convert results to list of key and values
    tobs_dict = {}
    for result in results:
        tobs_dict[result[0]] = result[1]

    session.close()
    
    #return the dictionary as a json file
    return jsonify(tobs_dict)

    

@app.route("/v1.0/<start>")
def temp_obs_json(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #create a query
    results = session.query(measurement.station, func.count(measurement.station)).\
        group_by(measurement.station).\
        order_by(desc(func.count(measurement.station))).\
        all()

    #extract the station with highest number of observations
    active_station = results[0][0]

    #extract date
    start_date_dt = dt.datetime.strptime(start_date, "%Y-%m-%d")
    #end_date_dt = dt.datetime.strptime(end_date, "%Y-%m-%d")

    results = session.query(measurement.station, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.station == active_station).\
        filter(measurement.date >= start_date_dt)
    
    output = {
    "minimum temperature observation" : results[0][1],
    "average temperature observation" : results[0][2],
    "maximum temperature observation" : results[0][3]
    }

    session.close()
    return (jsonify(output))



#3 sep queries: max, min, average. store in 3 sep vars. list where each of those 3 in list. 


@app.route("/v1.0/<start>/<end>")
def temp_obs_json(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #create a query
    results = session.query(measurement.station, func.count(measurement.station)).\
        group_by(measurement.station).\
        order_by(desc(func.count(measurement.station))).\
        all()

    #extract the station with highest number of observations
    active_station = results[0][0]

    #extract date
    start_date_dt = dt.datetime.strptime(start_date, "%Y-%m-%d")
    end_date_dt = dt.datetime.strptime(end_date, "%Y-%m-%d")

    results = session.query(measurement.station, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.station == active_station).\
        filter(measurement.date >= start_date_dt).\
        filter(measurement.date <= end_date_dt)
    
    output = {
    "minimum temperature observation" : results[0][1],
    "average temperature observation" : results[0][2],
    "maximum temperature observation" : results[0][3]
    }

    session.close()
    return (jsonify(output))


if __name__ == "__main__":
    app.run(debug=True)
