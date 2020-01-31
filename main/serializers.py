from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .addition import Person
from .models import Client


def gender_validator(field):
    if field.lower() not in ['мужской', 'женский']:
        raise ValidationError('Неверное значение поля Пол')
    return field


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('title', 'credit_limit', 'vip')


class PersonSerializer(serializers.Serializer):
    name = serializers.CharField()
    gender = serializers.CharField(validators=[gender_validator])
    age = serializers.IntegerField(max_value=120)
    email = serializers.CharField()

    def create(self, validated_data):
        return Person(
            name=validated_data['name'],
            gender=validated_data['gender'],
            age=validated_data['age'],
            email=validated_data['email']
        )

    def update(self, instance, validated_data):
        instance.name = validated_data['name']
        instance.gender = validated_data['gender']
        instance.age = validated_data['age']
        instance.email = validated_data['email']
        return instance


