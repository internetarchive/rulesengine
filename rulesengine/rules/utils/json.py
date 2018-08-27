from datetime import datetime
import ujson

from django.http import HttpResponse


def date_renderer(obj):
    if isinstance(obj, datetime):
        return obj.replace(tzinfo=None).isoformat() + 'Z'
    return obj


def success(obj):
    """Create an HttpResponse object with a JSON payload indicating success.

    Arguments:
    obj -- A Python dict to be serialized in the response.

    Returns:
    A Django HttpResponse including the JSON with the proper MIME type.
    """
    return HttpResponse(ujson.dumps({
        'status': 'success',
        'message': 'ok',
        'result': obj,
    }, pre_encode_hook=date_renderer), content_type='application/json')


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
    return HttpResponse(ujson.dumps(result, pre_encode_hook=date_renderer),
                        content_type='application/json',
                        status=400)
