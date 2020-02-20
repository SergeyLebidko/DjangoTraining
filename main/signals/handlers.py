from django.apps import apps

from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from django.forms.models import model_to_dict


@receiver(post_delete, sender=apps.get_model('main', 'Order'))
def order_post_delete(sender, instance, **kwargs):
    instance_data = model_to_dict(instance)
    print(f'Удалено: {instance_data}')
