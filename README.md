# About
As part of the [KOI-System](https://github.com/koi-learning) *koi-api* manages all objects registered in the system.
All other components([koi-core](https://github.com/koi-learning/koi-core), [koi-pwa](https://guthub.com/koi-learning/koi-pwa)) communicate over an REST-API provided by this component.
"*KOI*" is an abbreviation of the german name "Kognitive Objekt-orientierte Intelligenz", which translates to "cognitive object-oriented intelligence".

The project is written in Python and uses Flask.
# Setup
## Local Installation
You can install *koi-api* on your system by running:
```
pip install git+https://github.com/koi-learning/koi-api.git
```
To serve the REST-API, you need any Flask compatible WSGI server.
[Here](https://flask.palletsprojects.com/en/1.1.x/deploying/) is a complete guide for this.
For this example we recommend using `waitress`. You can run:
```
pip install waitress
waitress-server --app koi_api:create_app
```
## Using Docker
comming soon...

# Copying & Contributing
*koi-api* was originally written by Johannes Richter (GÖPEL electronics, Jena) and Johannes Nau (Technische Universität Ilmenau).
The source code is licensed under the terms of LGPLv3, please see [COPYING](COPYING) and [COPYING.LESSER](COPYING.LESSER) for details.

If you are working with the KOI-System and find any bugs, please report them as an issue in the respective projects on Github.com.

If you want to contribute to this project, take a look at the open issues and send us your pull-requests. 