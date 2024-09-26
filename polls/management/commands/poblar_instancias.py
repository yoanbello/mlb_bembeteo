from django.core.management.base import BaseCommand
from polls.models import InstanciaPlayoff, Equipo

class Command(BaseCommand):
    help = 'Poblar la tabla de InstanciaPlayoff y Equipo con datos iniciales'

    def handle(self, *args, **kwargs):
        # Verificar si ya hay instancias existentes
        if not InstanciaPlayoff.objects.exists():    
            # Crear instancias con nombres y campos coincidentes
            InstanciaPlayoff.objects.create(nombre="Serie de Comodines", puntos_por_acertar=3, bono_por_resultado_exacto=2, juegos_para_ganar=2)
            InstanciaPlayoff.objects.create(nombre="Serie Divisional", puntos_por_acertar=5, bono_por_resultado_exacto=3, juegos_para_ganar=3)
            InstanciaPlayoff.objects.create(nombre="Serie de Campeonato", puntos_por_acertar=7, bono_por_resultado_exacto=5, juegos_para_ganar=4)
            InstanciaPlayoff.objects.create(nombre="Serie Mundial", puntos_por_acertar=7, bono_por_resultado_exacto=5, juegos_para_ganar=4)
            self.stdout.write(self.style.SUCCESS('Instancias creadas exitosamente.'))
        else:
            self.stdout.write(self.style.WARNING('Las Instancias ya están pobladas.'))  
            


        if not Equipo.objects.exists():                   

            # Lista de equipos con sus URLs de logos
            equipos = [
                {"nombre": "New York Yankees", "logo_equipo": "https://midfield.mlbstatic.com/v1/team/147/spots/48"},
                {"nombre": "Cleveland Guardians", "logo_equipo": "https://midfield.mlbstatic.com/v1/team/114/spots/48"},
                {"nombre": "Houston Astros", "logo_equipo": "https://midfield.mlbstatic.com/v1/team/117/spots/48"},
                {"nombre": "Baltimore Orioles", "logo_equipo": "https://midfield.mlbstatic.com/v1/team/110/spots/48"},
                {"nombre": "Detroit Tigers", "logo_equipo": "https://midfield.mlbstatic.com/v1/team/116/spots/48"},
                {"nombre": "Kansas City Royals", "logo_equipo": "https://midfield.mlbstatic.com/v1/team/118/spots/48"},
                {"nombre": "Minnesota Twins", "logo_equipo": "https://midfield.mlbstatic.com/v1/team/142/spots/48"},
                {"nombre": "Los Angeles Dodgers", "logo_equipo": "https://midfield.mlbstatic.com/v1/team/119/spots/48"},
                {"nombre": "Philadelphia Phillies", "logo_equipo": "https://midfield.mlbstatic.com/v1/team/143/spots/48"},
                {"nombre": "Milwaukee Brewers", "logo_equipo": "https://midfield.mlbstatic.com/v1/team/158/spots/48"},
                {"nombre": "San Diego Padres", "logo_equipo": "https://midfield.mlbstatic.com/v1/team/135/spots/48"},
                {"nombre": "New York Mets", "logo_equipo": "https://midfield.mlbstatic.com/v1/team/121/spots/48"},
                {"nombre": "Arizona Diamondbacks", "logo_equipo": "https://midfield.mlbstatic.com/v1/team/109/spots/48"},
                {"nombre": "Atlanta Braves", "logo_equipo": "https://midfield.mlbstatic.com/v1/team/144/spots/48"},
            ]
            # Crear equipos
            for equipo in equipos:
                Equipo.objects.create(nombre=equipo['nombre'], logo_equipo=equipo['logo_equipo'])

            self.stdout.write(self.style.SUCCESS('Equipos creados exitosamente.'))   
        else:
            self.stdout.write(self.style.WARNING('Los equipos ya están poblados.'))  
