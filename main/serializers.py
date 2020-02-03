from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .addition import Person
from .models import Client, Product, Order


def gender_validator(field):
    if field.lower() not in ['мужской', 'женский']:
        raise ValidationError('Неверное значение поля Пол')
    return field


class SimpleClientSerializer(serializers.ModelSerializer):

    def validate(self, data):
        if data.get('vip') and data.get('credit_limit') < 100000:
            raise ValidationError('VIP-клиент не модет иметь кредитный лимит меньше 100 000')
        return data

    def validate_credit_limit(self, field):
        if field <= 0:
            raise ValidationError('Слишком маленький кредитный лимит')
        return field

    class Meta:
        model = Client
        fields = ('title', 'credit_limit', 'vip', 'id')


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['title', 'credit_limit', 'vip', 'order_set']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'balance', 'price']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'dt_create', 'client', 'product', 'count', '__str__']


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


