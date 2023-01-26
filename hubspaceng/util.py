
import calendar
import datetime

def getUTCTime():
    date = datetime.datetime.utcnow()
    utc_time = calendar.timegm(date.utctimetuple()) * 1000
    return utc_time
