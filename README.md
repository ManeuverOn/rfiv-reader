# rfiv-reader

This code was designed to run on a Raspberry Pi with the [DLP USB RFID reader](https://www.dlpdesign.com/rf/dlp-rfid2-ds-v114.pdf). It connects to the patient MongoDB database and saves timestamp/location datapoints to patient documents if that patient's RFID tag is detect by the reader. 

## Setup

The following steps are needed to setup the Pi and run this code:
1. The [CP210x USB to UART Bridge VCP Driver](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers) needs to be installed, but it may already be installed on the Raspberry Pi.
2. The [FTDI VCP Driver](https://ftdichip.com/drivers/vcp-drivers/) also needs to be installed, but this may also already come installed on the Pi. 
3. Python needs to be installed (should already be on the Pi).
4. Python packages for PyRFIDGeek, PyMongo, and other dependencies need to be installed using these commands:
    * pip install rfidgeek
    * pip install pymongo
    * pip install 'pymongo\[srv\]'
    * pip install pyyaml
    * pip install pyserial 
5. The [reader.py](reader.py) code needs to be copied to the Pi.
6. The hardcoded location needs to be set in [reader.py, line 13](reader.py#L13). 
7. The serial port location needs to be set in [reader.py, line 16](reader.py#L16).
8. The database connection string with username and password needs to be set in [reader.py, line 26](reader.py#L26).

## Run the Program

Run the program using `python reader.py`.