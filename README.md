# Messenger LoRa

Low-power system for isolated communities based on the LoRa protocol to provide a messaging system through the creation of a user who can send a message only if the destination user is also registered.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

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

### Installing

Now you can download and install the project in your device.


Primero descarga el proyecto y lo extraes en tu máquina

Instala el repositorio en la LoPy.

En la ruta donde se encuentra el proyecto digita:
```
$ python3 -m there push * /flash
```
Ingresa al modo PERL
```
$ python3 -m there -i
```
## Deployment

Una vez el código se encuentra en la LoPy se importa el archivo server
```
import server
```
conectate a la red creada e ingresa la ip
```
192.168.4.1
```
## Authors

* **Angélica Moreno Cárdenas**
* **Miguel Kiyoshi Nakamura Pinto**
* **Pietro Manzoni**

## License

This project is licensed under the GNU GPLv3 - see the [LICENSE.md](license.md) file for details

## Acknowledgments

* **Ermanno Pietrosemoli**
* **Marco Zennaro**
* **Marco Rainone**