# Import Dependencies
import numpy as np
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Set up database connection 
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Set base
Base = automap_base()
# Reflect the tables
Base.prepare(engine,reflect=True)

# Save reference to the tables
measurement = Base.classes.measurement
station = Base.classes.station
# Create app
app = Flask(__name__)

# 1. List all the available routes starting from the homepage

@app.route("/")
def homepage():
        print("Server received request for 'Home' page...</br>")
        return (f'Welcome to the Climate Homepage!</br>'
            f'Here are the available routes:</br>' 
            f'/api/v1.0/precipitation</br>'
            f'/api/v1.0/stations</br>'
            f'/api/v1.0/tobs</br>'
            f'/api/v1.0/<start></br>'
            f'/api/v1.0/<start>/<end>')

# 2. /api/v1.0/precipitation

# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) 
# ...to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def prcp():
    # Begin Session
    session = Session(engine)
    # determine date 12 months from the most recent datapoint
    twelve_months = dt.date(2017,8,23) - dt.timedelta(weeks=52)

    # Perform a query to retrieve the date and precipitation scores
    data_precp = session.query(measurement.date,measurement.prcp).\
                filter(measurement.date>=twelve_months).all()
    data_precp_list = []
    for x, y in data_precp:
        precp_dict = {}
        precp_dict["Date"] = x
        precp_dict["Precipitation"] = y
        data_precp_list.append(precp_dict) 
         
    return jsonify(data_precp_list)
# 3. /api/v1.0/stations

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Begin Session
    session = Session(engine)
    # determine names of unique stations
    Station_names = session.query(measurement.station).distinct().all()
    # Close Session
    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(Station_names))

    return jsonify(all_names)



# 4. /api/v1.0/tobs

# Query the dates and temperature observations of the most-active station for the previous year of data.

# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    # Begin Session
    session = Session(engine)

    # count back 12 mos
    twelve_months = dt.date(2017,8,23) - dt.timedelta(weeks=52)
    # Determine date and temp of most active station over 12 mos
    station_12_mos = session.query(measurement.date, measurement.tobs).\
                filter(measurement.station == 'USC00519281').\
                filter(measurement.date>=twelve_months).all()

    active_station = []
    for x, y in station_12_mos:
        station_dict = {}
        station_dict["Date"] = x
        station_dict["TOBs"] = y
        active_station.append(station_dict)

    return jsonify(active_station)


# 5./api/v1.0/<start> 
# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.


@app.route("/api/v1.0/<start>")
def start_date(start):
    # Begin Session
    session = Session(engine)

    search_date = (dt.datetime(start))
    
    output = (session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
                filter(measurement.date == str(search_date)).all())
    return jsonify(output)

# 6. /api/v1.0/<start>/<end>
# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.




if __name__ == "__main__":
    app.run(debug=True)