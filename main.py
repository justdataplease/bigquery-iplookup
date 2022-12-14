import json

import functions_framework
from iplookup import GeoLocation


@functions_framework.http
def iplookup(request):
    """
    Defines iplookup Google Cloud Function
    :param request:
    :return:
    """
    request_json = request.get_json()
    calls = request_json['calls']
    replies = []
    lookup = GeoLocation()
    for call in calls:
        ip_address = call[0]
        rs = lookup.lookup_ip(ip_address=ip_address)
        # each reply is a STRING (JSON not currently supported)
        replies.append(json.dumps(rs, ensure_ascii=False))

    lookup.close()
    return json.dumps({'replies': replies})