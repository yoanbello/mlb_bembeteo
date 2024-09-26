from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Serie

@receiver(post_save, sender=Serie)
def calcular_puntos_serie(sender, instance, **kwargs):    
    if instance.finalizada:
        instance.calcular_puntos()
