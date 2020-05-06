"""Setup script for rusertracker
"""
import re
from setuptools import setup
from codecs import open
from os import path


NAME = "rusertracker"
DESCRIPTION = "Maintains a list of active members of a set of subreddits."

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as filein:
    long_description = filein.read()

with open(path.join(here, "requirements.txt"), encoding="utf-8") as filein:
    requirements = [line.strip() for line in filein.readlines()]

with open(path.join(here, NAME, "__init__.py"), encoding="utf-8") as filein:
    pattern = r"__version__\W*=\W*\"([^']+)\""
    for line in filein:
        if line.startswith("__version__"):
            match = line
            break
    VERSION = re.findall(pattern, match)[0]


setup(
    name="rusertracker",
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    url="https://github.com/chapotracker/rusertracker",
    author="Nick Mullen's Biggest Simp",
    author_email="ICntBelieveHwSmrtIAm@reddit.com",
    classifiers=["Development Status :: 2 - Pre-Alpha",
                 "Intended Audience :: Developers",
                 "Programming Language :: Python :: 3"],
    packages=["rusertracker"],
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "rusertracker=rusertracker.app:main"
        ]
    }
)
