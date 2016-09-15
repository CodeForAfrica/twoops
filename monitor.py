import requests

"Health checks powered by https://hchk.io/"

def health_check(_id):
    """
    https://hchk.io/{uuid}
    """
    resp = requests.get("https://hchk.io/%s" % _id)
    print "HEALTH - %s - %s" % (_id, resp.status_code)
