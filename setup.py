import setuptools

setuptools.setup(
    name="koi-api",
    version="0.4.1",
    packages=setuptools.find_packages(),
    install_requires=[
        "sqlalchemy",
        "flask<=2.1.3",
        "flask-cors",
        "flask_sqlalchemy",
        "flask_restful",
        "PyMySql",
        "cryptography",
    ],
)
