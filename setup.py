"""
setup.py - a module to allow package installation
"""


from setuptools import setup, find_packages

NAME = "slab"
VERSION = "0.1"
DEPENDENCIES = [
    "numpy",
    "scipy"
]
DESCRIPTION = "This package is used for Schuster Lab experiments"
AUTHOR = "David Schuster"
AUTHOR_EMAIL = "david.schuster@uchicago.edu"

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    install_requires=DEPENDENCIES,
    packages=find_packages(include=["*"], exclude=["__pycache__", "*.pyc"]),
    include_package_data=True,
    zip_safe=False,
)
