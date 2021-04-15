# About
As part of the [KOI-System](https://github.com/koi-learning), *koi-api* manages all objects registered in the system.
All other components([koi-core](https://github.com/koi-learning/koi-core), [koi-pwa](https://guthub.com/koi-learning/koi-pwa)) communicate over an REST-API provided by this component.

# What is KOI?
The *KOI-System* is a framework for the lifecycle management of machine learning solutions.
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
## Using Docker
To run a single container hosting *koi-api*, you check out the repository and use the included [Dockerfile](Dockerfile). The docker file will install the needed python packages and waitress.

For a complete setup including all components of the *KOI-System*, please check our project [KOI-Deploy](https://github.com/koi-learning/koi-deploy).


# Copying & Contributing
*koi-api* was originally written by Johannes Richter (GÖPEL electronics, Jena) and Johannes Nau (Technische Universität Ilmenau).
The source code is licensed under the terms of LGPLv3. Please see [COPYING](COPYING) and [COPYING.LESSER](COPYING.LESSER) for details.

If you're working with *KOI* and find any bugs, please report them as an issue in the respective projects.

If you want to contribute to this project, check the open issues and send us your pull requests. 

# Citation
If you are using the *KOI-System* for academic research, please cite our [accompanying publication](http://dx.doi.org/10.1007/978-3-030-68527-0_8) . Here we give an overview of the architecture and discuss some design decisions.

