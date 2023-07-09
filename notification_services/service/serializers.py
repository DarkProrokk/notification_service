from rest_framework import serializers

from .models import Client, Message, Mailing


class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = '__all__'


class MailingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Mailing
        fields = ('__all__')