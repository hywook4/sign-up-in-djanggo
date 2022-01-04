import uuid
import random
import redis

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from .serializers import SmsAuthPostSerializer, SmsAuthGetSerializer
from django.conf import settings


class SmsAuthView(GenericViewSet):

    def get(self, request):
        serializer = SmsAuthGetSerializer(data=request.GET)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Create SMS Auth Code
        sms_auth_code = generate_sms_auth_code(request)
        if not sms_auth_code:
            return Response("Failed to create SMS Auth Code", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(sms_auth_code)

    @action(detail=False, methods=["POST", ])
    def test(self, request):
        serializer = SmsAuthPostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Validate SMS Auth Code
        sms_auth_code = get_sms_auth_code(request)

        if not sms_auth_code:
            return Response("SMS Auth code for given information doesn't exist", status=status.HTTP_404_NOT_FOUND)

        if sms_auth_code != request.data['sms_auth_code']:
            return Response("SMS Auth code mismatch", status=status.HTTP_401_UNAUTHORIZED)

        delete_sms_auth_code(request)

        # Create Verified Token
        verified_token = generate_verified_token(request)

        if not verified_token:
            return Response("Failed to create Verified Token", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer.set_verified_token(verified_token)
        return Response(serializer.data)


# Utils
redis_client = redis.StrictRedis(host=settings.REDIS['host'], port=settings.REDIS['port'])


def get_random_code():
    ret = ''
    for _ in range(6):
        ret += str(random.randint(0, 9))
    return ret


def make_sms_auth_code_key(name, phone_number):
    return f'{name}:{phone_number}:code'.format(name=name, phone_number=phone_number)


SMS_AUTH_CODE_EXPIRE_SECONDS = 300


def generate_sms_auth_code(request):
    sms_auth_code = get_random_code()

    if not redis_client.setex(make_sms_auth_code_key(request.GET['name'], request.GET['phone_number']),
                              SMS_AUTH_CODE_EXPIRE_SECONDS, sms_auth_code):
        return None

    return sms_auth_code


def get_sms_auth_code(request):
    sms_auth_code_key = make_sms_auth_code_key(request.data['name'], request.data['phone_number'])
    sms_auth_code = redis_client.get(sms_auth_code_key)

    if not sms_auth_code:
        return None

    return sms_auth_code.decode('utf-8')


def make_verified_token():
    return str(uuid.uuid4())


def make_verified_token_key(name, phone_number):
    return f'{name}:{phone_number}:token'.format(name=name, phone_number=phone_number)


VERIFIED_TOKEN_EXPIRE_SECONDS = 300


def generate_verified_token(request):
    verified_token = make_verified_token()

    if not redis_client.setex(make_verified_token_key(request.data['name'], request.data['phone_number']),
                              VERIFIED_TOKEN_EXPIRE_SECONDS, verified_token):
        return None

    return verified_token


def delete_sms_auth_code(request):
    redis_client.delete(make_sms_auth_code_key(request.data['name'], request.data['phone_number']))
