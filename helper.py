from datetime import datetime

def datetimeStringTodate(dateString):
    if dateString is None or dateString ==  "":
        return "Present"
    try:
        return datetime.strptime(dateString, "%Y-%m-%dT%H:%M:%S.%fZ").strftime('%d-%m-%Y')
    except:
        return "Present"