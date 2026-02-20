from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    data = response.data

    if isinstance(data, dict):
        if "non_field_errors" in data:
            message = data["non_field_errors"][0]
        else:
            # Field error
            field, errors = next(iter(data.items()))
            if isinstance(errors, list):
                message = errors[0]
            else:
                # It's already a string (like PermissionDenied)
                message = errors

        response.data = {"message": message}

    return response
