from datetime import datetime

def datetimeStringTodate(dateString):
    if dateString is None or dateString ==  "":
        return "Present"
    try:
        return datetime.strptime("2023-01-19T18:30:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ").strftime('%d-%m-%Y')
    except:
        return "Present"