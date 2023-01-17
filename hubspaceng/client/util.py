
import calendar
import datetime

def getExpansions(expansions):
    if expansions == None or len(expansions) == 0:
        return ""
    return "?expansions=" + ",".join(expansions)

def getUTCTime():
    date = datetime.datetime.utcnow()
    utc_time = calendar.timegm(date.utctimetuple()) * 1000
    return utc_time