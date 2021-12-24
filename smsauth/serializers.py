from rest_framework import serializers


class SmsAuthGetSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)


class SmsAuthPostSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    sms_auth_code = serializers.CharField(required=True)
    verified_token = serializers.CharField(required=False)

    def set_verified_token(self, verified_token):
        self.verified_token = verified_token

    def to_representation(self, instance):
        ret = super(SmsAuthPostSerializer, self).to_representation(instance)
        ret.pop('sms_auth_code')
        ret.update({'verified_token': self.verified_token})

        return ret
