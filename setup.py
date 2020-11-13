import setuptools

setuptools.setup(
    name="koi-api",
    version="0.1",
    packages=setuptools.find_packages(),
    install_requires=[
        "flask",
        "flask-cors",
        "flask_sqlalchemy",
        "flask_restful",
        "PyMySql",
        "cryptography",
    ],
)
