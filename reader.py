# Code for reading nearby RFID tags and saving locations to database
# Adapted from example code by Dan Michael O. Heggø
# From PyRFIDGeek GitHub repository available at:
# https://github.com/scriptotek/pyrfidgeek

from __future__ import print_function
import sys
import yaml
from rfidgeek import PyRFIDGeek, ISO15693
import pymongo
import time
import math
import signal
import json


# load config file
with open("config.json", "r") as f:
    config = json.load(f)

# load configurations
try:
    # physical location for this reader
    location = config["reader_location"]
    # COM port which RFID reader module is plugged into
    COM_PORT_NAME = config["com_port_name"]
    # whether or not to enable external antenna
    external_antenna = config["external_antenna"]
    # database connection string
    connection_string = config["mongodb"]
    print("Loaded configurations.")
except Exception as e:
    print(e)
    print("\nFailed to load configurations. Exiting...")
    sys.exit(0)

# connect to database
try:
    myclient = pymongo.MongoClient(connection_string)
    # database called "rfivDB"
    mydb = myclient["rfivDB"]
    # collection called "patients"
    mycol = mydb["patients"]
    print("Connected to database.")
except Exception as e:
    print(e)
    print("\nFailed to connect to database. Exiting...")
    sys.exit(0)

# connect to reader using pyrfidgeek package
try:
    reader = PyRFIDGeek(serial_port=COM_PORT_NAME, debug=True)
    print("Connected to reader.")
except Exception as e:
    print(e)
    print("\nFailed to connect to reader. Exiting...")
    sys.exit(0)

# use RFID protocol ISO 15693
protocols = [ISO15693]

# handle quitting program with control+C
def sig_int_handler(sig, frame):
    print("\nExiting...")
    reader.close()
    sys.exit(0)
signal.signal(signal.SIGINT, sig_int_handler)

# start reading tags
print("Ready to read tags.")
try:
    while True:
        # time of reading
        timestamp = math.floor(time.time() * 1000)

        # list of tags that are read
        tagIds = []

        # for each protocol, read the nearby tags and save their tag ID
        for protocol in protocols:
            reader.set_protocol(protocol)
            if external_antenna:
                reader.enable_external_antenna()
            for uid in reader.inventory():
                tagIds.append(uid)

        # save locations into patient database entries that are associated with the tag IDs
        for tagId in tagIds:
            # get the patient document that has this tag ID
            # the tag ID is stored as little-endian, so it must be reversed
            # reversing trick is adapted from John La Rooy at https://stackoverflow.com/a/5864372
            reversed_tagId = "".join(map(str.__add__, tagId[-2::-2], tagId[-1::-2]))
            patient = mycol.find_one({
                "tagId": reversed_tagId
            })

            # if the tag is associated with a patient, save to database
            if patient is not None:
                # get the last known location/time if it exists
                if len(patient["locations"]) == 0:
                    lastLocation = [0, ""]
                else:
                    lastLocation = patient["locations"][-1]

                # if the current location is different from the last location, add to the database;
                # or if it's been over 120 seconds regardless of the location, add to the database;
                # otherwise, don't add it.
                # A list [timestamp, location] is pushed onto the patient's location array
                if location != lastLocation[1] or timestamp - lastLocation[0] > 120000:
                    mycol.update_one({
                        "_id": patient["_id"]
                    }, {
                        "$push": {
                            "locations": [timestamp, location]
                        }
                    })
                    print(f"Saved location for {patient['name']} at time {timestamp}")
                else:
                    # tag was read too recently
                    print(f"This tag ({reversed_tagId}) was recently read in this location.")
            else:
                # tag not in database
                print(f"This tag ({reversed_tagId}) is not in the database.")

except Exception as e:
    # error while reading
    print(e)
    print("\nError while reading. Exiting...")
    reader.close()
