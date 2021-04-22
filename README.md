# rfiv-reader

This code was designed to run on a Raspberry Pi with the [DLP USB RFID reader](https://www.dlpdesign.com/rf/dlp-rfid2-ds-v114.pdf). It connects to the patient MongoDB database and saves timestamp/location datapoints to patient documents if that patient's RFID tag is detect by the reader. 

## Setup

The following steps are needed to setup the Pi and run this code:
1. The [CP210x USB to UART Bridge VCP Driver](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers) needs to be installed, but it may already be installed on the Raspberry Pi.
2. The [FTDI VCP Driver](https://ftdichip.com/drivers/vcp-drivers/) also needs to be installed, but this may also already come installed on the Pi. 
3. Python3 needs to be installed (should already be on the Pi).
4. The files in this repository need to be copied to the Pi.
5. Python packages for [PyRFIDGeek](https://github.com/scriptotek/pyrfidgeek), [PyMongo](https://pymongo.readthedocs.io/en/stable/), and other dependencies need to be installed using these commands in the terminal:
    * `pip3 install pymongo`
    * `pip3 install 'pymongo[srv]'`
    * `pip3 install pyyaml`
    * `pip3 install pyserial`
    * `Note`: The PyRFIDGeek module does not come with the functionality to activate an external antenna, so we had to manually change the source code to allow this. In order to use the updated rfidgeek module, the official module has to be uninstalled (if it was installed) using the command `pip3 uninstall rfidgeek`. The updated module is already provided in this repository.
6. A `config.json` file needs to be included in this directory. The code expects a file with the following structure:
    ```JSON
    {
        "mongodb": "<connection_string>",
        "reader_location": "<location>",
        "com_port_name": "<port_name>",
        "external_antenna": "<boolean>"
    }
    ```
    where `<connection_string>` is the connection string to a MongoDB database, `<location>` is the physical location of the reader, `<port_name>` is the serial port location of the Raspberry Pi where the reader is plugged into, and `<boolean>` is either `true` or `false` depending on if an external antenna is being used with the reader.

    Our connection string is in the form `mongodb+srv://<USERNAME>:<PASSWORD>@cluster0.muah1.mongodb.net/rfivDB?retryWrites=true&w=majority`, where `<USERNAME>` and `<PASSWORD>` are the username and password of a database user, respectively. The reader location can be any string, like "Lobby" or "Waiting Room". The port name should be in the form "/dev/ttyUSBx", where x is some digit (0, 1, 2, ...) that may vary depending on which port the reader is plugged into on the Raspberry Pi.

## Run the Program

Run the program using `python3 reader.py` in the terminal.