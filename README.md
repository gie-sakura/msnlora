# Messenger LoRa

Low-power system to connect isolated communities based on the LoRa protocol to provide a messaging system to registered users and a gateway to a telegram user using a raspberry Pi connected to Internet.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes in your lopy and raspberry.

### Prerequisites

####In the lopy device

This is the basic information required to set up a suitable development environment for a Pycom device, in this case the LoPys.

You first need to have Python 3 installed in your computer. Check here for the proper instructions and code:

```
https://www.python.org/download/releases/3.0/
```

Install the software required to connect to the LoPy device

```
$ python3 -m pip install mpy-repl-tool
```

For more information you can check the full [documentation](https://docs.pycom.io/)

####In the raspberry

First you need to install or upgrade python-telegram-bot with:

```
$ pip install python-telegram-bot --upgrade
```
Or you can install from source with:
```
$ git clone https://github.com/python-telegram-bot/python-telegram-bot --recursive
$ cd python-telegram-bot
$ python setup.py install
```

### Installing

Now you can download and install the project in your device.

First download the .ZIP and extract it in your machine.

Installing the repository in the LoPy device.

On the project's location type:
```
$ python3 -m there push * /flash
```
Get access to the REPL prompt:
```
$ python3 -m there -i
```
## Deployment

Once in the REPL promt import the server file
```
import server
```
Connect to the network and type the address
```
192.168.4.1
```
## Authors

* **Angélica Moreno Cárdenas**
* **Miguel Kiyoshy Nakamura Pinto**
* **Pietro Manzoni**

## License

This project is licensed under the GNU GPLv3 - see the [LICENSE.md](license.md) file for details

## Acknowledgments

* **Ermanno Pietrosemoli**
* **Marco Zennaro**
* **Marco Rainone**