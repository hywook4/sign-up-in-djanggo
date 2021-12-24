import datetime
import redis
import jwt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from uuid import uuid4
from django.conf import settings
from .models import User
from .serializers import UserSerializer, TestSerializer, ChangePasswordSerializer, AuthSerializer


class UserAPIView(APIView):

    def get(self, request):
        queryset = User.objects.all()
        serializer = TestSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Validate Verified Token
        if 'HTTP_X_SMS_VERIFIEDTOKEN' not in request.META:
            return Response('Verified Token required', status=status.HTTP_400_BAD_REQUEST)

        verified_token = get_verified_token(request)
        if not verified_token:
            return Response("Verified token for given information doesn't exist", status=status.HTTP_404_NOT_FOUND)
        elif verified_token != request.META['HTTP_X_SMS_VERIFIEDTOKEN']:
            return Response('Verified token mismatch', status=status.HTTP_401_UNAUTHORIZED)

        # Set User Token
        request.data['token'] = generate_user_token()
        serializer = UserSerializer(data=request.data)

        # Validate
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        delete_verified_token(request)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        # Validate Verified Token
        if 'HTTP_X_SMS_VERIFIEDTOKEN' not in request.META:
            return Response('Verified Token required', status=status.HTTP_400_BAD_REQUEST)

        verified_token = get_verified_token(request)
        if not verified_token:
            return Response("Verified token for given information doesn't exist", status=status.HTTP_404_NOT_FOUND)
        elif verified_token != request.META['HTTP_X_SMS_VERIFIEDTOKEN']:
            return Response('Verified token mismatch', status=status.HTTP_401_UNAUTHORIZED)

        # Get proper user from request body
        user = User.objects.get(name=request.data['name'], phone_number=request.data['phone_number'])
        serializer = ChangePasswordSerializer(user, data=request.data, many=False)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        delete_verified_token(request)

        return Response()


class AuthAPIView(APIView):
    # TODO: Change routing(url path) to proper value -> API is for getting JWT token
    def post(self, request):
        serializer = AuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Check if user of given info exists
        user = get_user_object(request)
        if not user:
            return Response("Please check Id or Password", status=status.HTTP_401_UNAUTHORIZED)

        # Return user info with JWT Token
        jwt_token = generate_jwt_token(getattr(user, 'token'))
        serializer.update(user, serializer.validated_data, jwt_token=jwt_token)
        return Response(serializer.data)

    # TODO: Change routing
    def get(self, request):
        # Validate AUTHORIZATION header
        if 'HTTP_AUTHORIZATION' not in request.META:
            return Response("Access Token required", status=status.HTTP_401_UNAUTHORIZED)

        authorization_header = request.META['HTTP_AUTHORIZATION']
        if authorization_header.split(' ')[0] != 'Bearer':
            return Response('Wrong AUTHORIZATION header type', status=status.HTTP_401_UNAUTHORIZED)

        access_token = authorization_header.split(' ')[1]

        # Validate Access Token (JWT Token)
        try:
            payload = jwt.decode(access_token, settings.JWT_SECRET_KEY, algorithms='HS256')
        except jwt.ExpiredSignatureError:
            return Response('Token expired', status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response('Invalid Token', status=status.HTTP_401_UNAUTHORIZED)

        queryset = User.objects.get(token=payload['token'])
        serializer = UserSerializer(queryset, many=False)
        return Response(serializer.data)


# Utils
redis_client = redis.StrictRedis(host=settings.REDIS['host'], port=settings.REDIS['port'])


def make_verified_token_key(name, phone_number):
    return f'{name}:{phone_number}:token'.format(name=name, phone_number=phone_number)


def get_verified_token(request):
    verified_token_key = make_verified_token_key(request.data['name'], request.data['phone_number'])
    verified_token = redis_client.get(verified_token_key)

    if not verified_token:
        return None

    return verified_token.decode('utf-8')


def delete_verified_token(request):
    redis_client.delete(make_verified_token_key(request.data['name'], request.data['phone_number']))


def generate_user_token():
    return str(uuid4())


def get_user_object(request):
    try:
        if request.data['id_field'] == 'email':
            return User.objects.get(email=request.data['id_value'], password=request.data['password'])
        elif request.data['id_field'] == 'phone_number':
            return User.objects.get(phone_number=request.data['id_value'], password=request.data['password'])
    except Exception:
        return None


def generate_jwt_token(user_token):
    return jwt.encode({
        'token': user_token,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=300)
    }, settings.JWT_SECRET_KEY, algorithm='HS256', )
