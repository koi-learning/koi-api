# About
As part of the [KOI-System](https://github.com/koi-learning), *koi-api* manages all objects registered in the system.
All other components([koi-core](https://github.com/koi-learning/koi-core), [koi-pwa](https://guthub.com/koi-learning/koi-pwa)) communicate over an REST-API provided by this component.

# What is KOI?
The *KOI-System* is a framework for the lifecycle management and deployment of machine learning solutions.
As such, it allows the user to create, train, and deploy ML solutions.

The lifecycle management involves:
- Continuous Training of ML-Models
- Collecting new Samples from multiple sources
- Control visibility and access through user account management and roles
- Distributed training using multiple workers  

"*KOI*" is an abbreviation of the German name "Kognitive Objekt-orientierte Intelligenz", which translates to "cognitive object-oriented intelligence".

The system defines three types of objects to simplify the development and deployment of different ML solutions: 
- **Models**
- **Instances**
- **Samples**

Models define how data is processed and how the machine learning application learns.
Samples are an atomic piece of training information used for a specific problem.
Instances are specific implementations of models trained with associated samples to reach a state suitable for inference.

The project is written in Python and uses Flask.
It does not depend on ML-Frameworks and enables the user to choose what is best for their Model.
# Setup
## Local Installation
You can install *koi-api* on your system by running:
```
pip install git+https://github.com/koi-learning/koi-api.git
```
To serve the REST-API, you need any Flask compatible WSGI server.
[Here](https://flask.palletsprojects.com/en/1.1.x/deploying/) is a complete guide for this.
For this example, we recommend using `waitress`. You can run:
```
pip install waitress
waitress-server --app koi_api:create_app
```

Prebuild wheels are available on the projects github page.
## Using Docker
We offer prebuild Docker-images over the github package registry.
To configure the service you could use the exposed environment variables or define a custom config und build your own image using our Dockerfile.
Some usefule enviroment variables are:
```
KOI_SQLALCHEMY_DATABASE_URI="sqlite:////koi.db"  # for a local sqlite database
KOI_SQLALCHEMY_DATABASE_URI="mysql+pymysql://user:password@host/database?charset=utf8mb4"  # for a more complex example using mysql

KOI_FILEPERSISTENCE_BASE_URI="/koi_persist"  # to set the folder used for all data files

KOI_FILEPERSISTENCE_COMPRESS="false"  # to not compress the data files
```

You can also setup additional roles and users this way.
See the config files for reference and simply prefix the settings with ```KOI_```.

For a complete setup using Docker, including all components of the *KOI-System*, please check our project [KOI-Deploy](https://github.com/koi-learning/koi-deploy).

## Development Setup
To install all test and development requirements, checkout the repository and run:
```bash
pip install -e .[develop]
```

# Copying & Contributing
*koi-api* was originally written by Johannes Richter (GÖPEL electronics, Jena) and Johannes Nau (Technische Universität Ilmenau).
The source code is licensed under the terms of LGPLv3. Please see [COPYING](COPYING) and [COPYING.LESSER](COPYING.LESSER) for details.

If you're working with *KOI* and find any bugs, please report them as an issue in the respective projects.

If you want to contribute to this project, check the open issues and send us your pull requests. 

# Citation
If you are using the *KOI-System* for academic research, please cite our [accompanying publication](http://dx.doi.org/10.1007/978-3-030-68527-0_8) . Here we give an overview of the architecture and discuss some design decisions.

