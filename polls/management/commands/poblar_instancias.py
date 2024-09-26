from django.core.management.base import BaseCommand
from polls.models import InstanciaPlayoff

class Command(BaseCommand):
    help = 'Poblar la tabla de InstanciaPlayoff con datos iniciales'

    def handle(self, *args, **kwargs):
        # Verificar si ya hay instancias existentes
        if InstanciaPlayoff.objects.exists():
            self.stdout.write(self.style.WARNING('Las instancias ya están pobladas.'))
            return

        # Crear instancias con nombres y campos coincidentes
        InstanciaPlayoff.objects.create(nombre="Serie de Comodines", puntos_por_acertar=3, bono_por_resultado_exacto=2, juegos_para_ganar=2)
        InstanciaPlayoff.objects.create(nombre="Serie Divisional", puntos_por_acertar=5, bono_por_resultado_exacto=3, juegos_para_ganar=3)
        InstanciaPlayoff.objects.create(nombre="Serie de Campeonato", puntos_por_acertar=7, bono_por_resultado_exacto=5, juegos_para_ganar=4)
        InstanciaPlayoff.objects.create(nombre="Serie Mundial", puntos_por_acertar=7, bono_por_resultado_exacto=5, juegos_para_ganar=4)

        self.stdout.write(self.style.SUCCESS('Instancias creadas exitosamente.'))
