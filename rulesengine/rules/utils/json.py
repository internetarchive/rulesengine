from datetime import datetime
import json

from django.http import HttpResponse


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder which returns datetime objects in ISO format strings."""
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super(DateTimeEncoder, self).default(o)


def success(obj):
    """Create an HttpResponse object with a JSON payload indicating success.

    Arguments:
    obj -- A Python dict to be serialized in the response.

    Returns:
    A Django HttpResponse including the JSON with the proper MIME type.
    """
    return HttpResponse(json.dumps({
        'status': 'success',
        'message': 'ok',
        'result': obj,
    }, cls=DateTimeEncoder), content_type='application/json')


def error(message, obj):
    """Create an HttpResponse object with an optional payload indicating
    failure.

    Arguments:
    message -- A (string) error message.
    obj -- A Python dict to be serialized in the response.

    Returns:
    A Django HttpResponse including the JSON with the proper MIME type.
    """
    result = {
        'status': 'error',
        'message': message,
    }
    if obj is not None:
        result['result'] = obj
    return HttpResponse(json.dumps(result, cls=DateTimeEncoder),
                        content_type='application/json')
