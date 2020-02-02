from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .addition import Person
from .models import Client, Order


def gender_validator(field):
    if field.lower() not in ['мужской', 'женский']:
        raise ValidationError('Неверное значение поля Пол')
    return field


class SimpleClientSerializer(serializers.ModelSerializer):

    def validate(self, data):
        if data.get('vip') and data.get('credit_limit') < 100000:
            raise ValidationError('VIP-клиент не модет иметь кредитный лимит меньше 100 000')
        return data

    class Meta:
        model = Client
        fields = ('title', 'credit_limit', 'vip')


class FictiveKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        print(self.context)
        return Order.objects.filter(count__gt=5)


class ClientSerializer(serializers.ModelSerializer):
    order_set = FictiveKey(many=True)

    class Meta:
        model = Client
        fields = ['title', 'credit_limit', 'vip', 'order_set']


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


