import json

import functions_framework
from ip_lookup import GeoLocation


@functions_framework.http
def ip_lookup(request):
    """
    Defines ip_lookup Google Cloud Function
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

    return json.dumps({'replies': replies})
