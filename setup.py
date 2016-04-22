#!/usr/bin/env python3

"""
Pipe informations to lemonboy's bar
"""

from os import path
from setuptools import setup

here = path.abspath(path.dirname(__file__))

setup(
    name="barython",
    version="0.0.1",

    description="Pipe informations to lemonboy's bar",

    url="https://github.com/Anthony25/barython",
    author="Anthony25 <Anthony Ruhier>",
    author_email="anthony.ruhier@gmail.com",

    license="Simplified BSD",

    classifiers=[
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: BSD License",
    ],

    keywords=["bar", "desktop"],
    packages=["barython", ],
    install_requires=["python-mpd2", "xcffib", "xpyb"],
    setup_requires=['pytest-runner', ],
    tests_require=['pytest', 'pytest-cov', "pytest-mock", "pytest-xdist"],
)
