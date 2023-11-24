"""
Shared python code for Notify applications
"""
import ast
import re

from setuptools import find_packages, setup

setup(
    name="notifications-utils",
    version="0.2.3",
    url="https://github.com/GSA/notifications-utils",
    license_files=("LICENSE.md",),
    author="General Services Administration",
    description="Shared python code for Notify applications",
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "bleach>=4.1.0",
        "cachetools>=4.1.1",
        "cryptography>=39.0.1",
        "mistune<2.0.0",  # v2 is totally incompatible with unclear benefit
        "requests>=2.25.0",
        "python-json-logger>=2.0.1",
        "Flask>=2.2.2",
        "orderedset>=2.0.3",
        "Jinja2>=2.11.3",
        "Flask-Redis>=0.4.0",
        "pyyaml>=5.3.1",
        "phonenumbers>=8.13.3",
        "pytz>=2020.4",
        "smartypants>=2.0.1",
        "itsdangerous>=1.1.0",
        "govuk-bank-holidays>=0.10",
        "geojson>=2.5.0",
        "Shapely>=1.8.0",
        "boto3>=1.19.4",
    ],
)
