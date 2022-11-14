import os

import pytz
from dateutil import parser

local_timezone = pytz.timezone(os.getenv("TIMEZONE", "America/New_York"))


def utc_string_to_aware_gmt_datetime(date):
    """
    Date can either be a string, naïve UTC datetime or an aware UTC datetime
    Returns an aware local datetime, essentially the time you'd see on your clock
    """
    date = parser.parse(date)
    forced_utc = date.replace(tzinfo=pytz.utc)
    return forced_utc.astimezone(local_timezone)


def convert_utc_to_est(utc_dt):
    """
    Takes a naïve UTC datetime and returns a naïve local datetime
    """
    return pytz.utc.localize(utc_dt).astimezone(local_timezone).replace(tzinfo=None)


def convert_est_to_utc(date):
    """
    Takes a naïve UTC datetime and returns a naïve local datetime
    """
    return local_timezone.localize(date).astimezone(pytz.UTC).replace(tzinfo=None)


def convert_utc_to_local_timezone(utc_dt, timezone=local_timezone):
    """
    Takes a naïve UTC datetime and timezone and returns a naïve datetime in that timezone
    """
    return pytz.utc.localize(utc_dt).astimezone(timezone).replace(tzinfo=None)


def convert_local_timezone_to_utc(date, timezone=local_timezone):
    """
    Takes a naïve datetime and timezone and returns a naïve UTC datetime
    """
    return timezone.localize(date).astimezone(pytz.UTC).replace(tzinfo=None)
