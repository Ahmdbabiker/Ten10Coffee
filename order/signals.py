from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver

from .utils import unique_stamp_code_generator
from .models import Stamp


@receiver(pre_save, sender=Stamp)
def pre_save_stamp_code(sender, instance, *args, **kwargs):
    if not instance.code:
        instance.code = unique_stamp_code_generator(instance)
