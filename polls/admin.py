from django.contrib import admin

# Register your models here.
from .models import Equipo, Serie, InstanciaPlayoff

admin.site.register(Equipo)
admin.site.register(Serie)



