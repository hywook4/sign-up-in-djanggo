import re
from rest_framework import serializers
from .models import User


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def to_representation(self, instance):
        ret = super(UserSerializer, self).to_representation(instance)

        ret.pop('id')
        ret.pop('password')
        ret.pop('token')

        return ret

    def validate(self, data):
        if not validate_nickname(data['nickname']):
            raise serializers.ValidationError("nickname must consist of alphabets only")

        if not validate_name(data['name']):
            raise serializers.ValidationError("Invalid name pattern")

        if not validate_phone_number(data['phone_number']):
            raise serializers.ValidationError("phone_number must consist of numbers only")

        if not validate_password(data['password']):
            raise serializers.ValidationError(
                "Password must be longer than 8 and consist of at least one letter and one number")

        return data


class ChangePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'phone_number', 'password')

    def validate(self, data):
        if not validate_password(data['password']):
            raise serializers.ValidationError(
                "Password must be longer than 8 and consist of at least one letter and one number")

        return data


class AuthSerializer(serializers.Serializer):
    id_field = serializers.CharField(required=True)
    id_value = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    email = serializers.CharField(required=False)
    nickname = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    jwt_token = serializers.CharField(required=False)

    def update(self, instance, validated_data, jwt_token=jwt_token):
        self.email = getattr(instance, 'email')
        self.nickname = getattr(instance, 'nickname')
        self.name = getattr(instance, 'name')
        self.phone_number = getattr(instance, 'phone_number')
        self.jwt_token = jwt_token

    def to_representation(self, instance):
        ret = super(AuthSerializer, self).to_representation(instance)

        # Remove unused values
        ret.pop('id_field')
        ret.pop('id_value')
        ret.pop('password')

        ret.update({
            'email': self.email,
            'nickname': self.nickname,
            'name': self.name,
            'phone_number': self.phone_number,
            'jwt_token': self.jwt_token
        })
        return ret


# Validators
def validate_nickname(nickname):
    pattern = "^[A-Za-z]+$"
    return False if re.fullmatch(pattern, str(nickname)) is None else True


def validate_name(name):
    pattern = "^[a-zA-Z]+(([',. -][a-zA-Z ])?[a-zA-Z]*)*$"
    return False if re.fullmatch(pattern, str(name)) is None else True


def validate_phone_number(phone_number):
    pattern = "^[0-9]*$"
    return False if re.fullmatch(pattern, str(phone_number)) is None else True


def validate_password(password):
    pattern = "^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d]{8,}$"
    return False if re.fullmatch(pattern, str(password)) is None else True
