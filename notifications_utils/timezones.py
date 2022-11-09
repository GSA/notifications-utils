from datetime import datetime

import pytz
from dateutil import parser

# Making a gradual switch in order to try things out downstream without immediately breaking everything
london = pytz.timezone("Europe/London")
eastern = pytz.timezone("America/New_York")


def utc_string_to_aware_gmt_datetime(date):
    """
    Date can either be a string, naïve UTC datetime or an aware UTC datetime
    Returns an aware London datetime, essentially the time you'd see on your clock
    """
    if not isinstance(date, datetime):
        date = parser.parse(date)

    forced_utc = date.replace(tzinfo=pytz.utc)
    return forced_utc.astimezone(london)


def convert_utc_to_bst(utc_dt):
    """
    Takes a naïve UTC datetime and returns a naïve London datetime
    """
    return pytz.utc.localize(utc_dt).astimezone(london).replace(tzinfo=None)


def convert_bst_to_utc(date):
    """
    Takes a naïve London datetime and returns a naïve UTC datetime
    """
    return london.localize(date).astimezone(pytz.UTC).replace(tzinfo=None)


def convert_utc_to_et(utc_dt):
    """
    Takes a naïve UTC datetime and returns a naïve Eastern datetime
    """
    return pytz.utc.localize(utc_dt).astimezone(eastern).replace(tzinfo=None)


def convert_et_to_utc(date):
    """
    Takes a naïve Eastern datetime and returns a naïve UTC datetime
    """
    return eastern.localize(date).astimezone(pytz.UTC).replace(tzinfo=None)