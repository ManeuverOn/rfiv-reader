# rfiv-reader

This code connects to the patient MongoDB database and saves timestamp/location datapoints to patient documents if that patient's RFID tag is detect by the RFID reader. 

`Note`: The username and password for an authorized user of the MongoDB database were left out of this code. The placeholders `<USERNAME>` and `<PASSWORD>` must be replaced by the username and password, respectively.

Run the program using `python reader.py`.