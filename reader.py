# Code for reading nearby RFID tags and saving locations to database
# Adapted from example code by Dan Michael O. Heggø
# From PyRFIDGeek GitHub repository available at:
# https://github.com/scriptotek/pyrfidgeek

from __future__ import print_function
import yaml
from rfidgeek import PyRFIDGeek, ISO15693
import pymongo
import time
import math

# hardcoded location for this reader
location = "Senior Design Lab"

# COM port which RFID reader module is plugged into
COM_PORT_NAME = "/dev/ttyUSB0"

# connect to reader using pyrfidgeek package
reader = PyRFIDGeek(serial_port=COM_PORT_NAME, debug=True)

# use RFID protocol ISO 15693 (can add more in the list)
protocols = [ISO15693]

# enable external antenna
external_antenna = True

# connect to database
myclient = pymongo.MongoClient(
    "mongodb+srv://<USERNAME>:<PASSWORD>@cluster0.muah1.mongodb.net/rfivDB?retryWrites=true&w=majority")
mydb = myclient["rfivDB"]
mycol = mydb["patients"]

# read tags
try:
    if external_antenna:
        reader.enable_external_antenna()

    while True:
        # time of reading
        timestamp = math.floor(time.time() * 1000)

        # keep track of tags that are read
        tagIds = []

        # for each protocol, read the nearby tags and save their tag ID
        for protocol in protocols:
            reader.set_protocol(protocol)
            for uid in reader.inventory():
                tagIds.append(uid)

        # save locations into patient database entries that are associated with the tag IDs
        for tagId in tagIds:
            # get the patient entry with this tag ID
            # the tag ID is stored as little-endian, so it must be reversed
            # reversing trick is adapted from John La Rooy at https://stackoverflow.com/a/5864372
            patient = mycol.find_one({
                "tagId": "".join(map(str.__add__, tagId[-2::-2], tagId[-1::-2]))
            })

            # if the tag is associated with a patient, save to database
            if patient is not None:
                # get the last location/time if it exists
                if len(patient["locations"]) == 0:
                    lastLocation = [0, ""]
                else:
                    lastLocation = patient["locations"][-1]

                # if the current location is different from the last location, add it to the database
                # or if it's been over 120 seconds regardless of the location, add it to the database
                # otherwise, don't add it to save space in database
                if location != lastLocation[1] or timestamp - lastLocation[0] > 120000:
                    mycol.update_one({
                        "_id": patient["_id"]
                    }, {
                        "$push": {
                            "locations": [timestamp, location]
                        }
                    })
                    print(
                        f"Saved location for {patient['name']} at time {timestamp}")
                else:
                    print(
                        f"This tag ({tagId}) was recently read in this location.")
            else:
                print(f"This tag ({tagId}) is not in the database.")

        # read every half second
        time.sleep(0.5)

finally:
    print("Done")
    reader.close()
