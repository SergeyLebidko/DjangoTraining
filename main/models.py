from django.db import models


class Client(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название клиента')
    credit_limit = models.IntegerField(verbose_name='Кредитный лимит')
    vip = models.BooleanField(verbose_name='VIP-клиент', default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['title']


class Product(models.Model):
    title = models.CharField(max_length=100, verbose_name='Товар')
    balance = models.IntegerField(verbose_name='Остаток')
    price = models.IntegerField(verbose_name='Цена')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['title']


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    count = models.IntegerField(verbose_name='Количество')
    dt_create = models.DateField(verbose_name='Дата заказа')

    def __str__(self):
        return f'Заказ клиента: {self.client} от: {self.dt_create} на товар: {self.product} количество: {self.count}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['client', 'product']
