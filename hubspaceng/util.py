"""Utility/convenience functions for the Hubspace API"""
import calendar
import datetime

def get_utc_time():
    """Get current UTC time"""
    date = datetime.datetime.utcnow()
    utc_time = calendar.timegm(date.utctimetuple()) * 1000
    return utc_time
