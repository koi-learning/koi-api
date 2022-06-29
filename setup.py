import setuptools

setuptools.setup(
    name="koi-api",
    version="0.4.0",
    packages=setuptools.find_packages(),
    install_requires=[
        "sqlalchemy",
        "flask",
        "flask-cors",
        "flask_sqlalchemy",
        "flask_restful",
        "PyMySql",
        "cryptography",
    ],
)
