import requests

"Health checks powered by https://hchk.io/"

def health_check(_id):
    """
    https://hchk.io/{uuid}
    """
    requests.get("https://hchk.io/%s" % _id)
