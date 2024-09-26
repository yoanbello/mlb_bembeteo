from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum

class Equipo(models.Model):
    nombre = models.CharField(max_length=100)
    eliminado = models.BooleanField(default=False)
    logo_equipo = models.URLField(null=True)
    def __str__(self):
        return self.nombre

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    equipo_campeon = models.ForeignKey(Equipo, on_delete=models.CASCADE, null=True, blank=True)    
    puntos = models.IntegerField(default=0)

class InstanciaPlayoff(models.Model):
    nombre = models.CharField(max_length=100)
    puntos_por_acertar = models.IntegerField()
    bono_por_resultado_exacto = models.IntegerField()
    juegos_para_ganar = models.IntegerField()  # Number of games needed to win the series (3, 5, or 7)

    def __str__(self):
        return self.nombre

class Serie(models.Model):
    instancia = models.ForeignKey(InstanciaPlayoff, on_delete=models.CASCADE)
    equipo_a = models.ForeignKey('Equipo', related_name='equipo_a_series', on_delete=models.CASCADE,
                                  limit_choices_to={'eliminado': False})
    equipo_b = models.ForeignKey('Equipo', related_name='equipo_b_series', on_delete=models.CASCADE,
                                  limit_choices_to={'eliminado': False})
    juegos_ganados_equipo_a = models.IntegerField(null=True, blank=True)
    juegos_ganados_equipo_b = models.IntegerField(null=True, blank=True)
    abierta = models.BooleanField(default=False)
    finalizada = models.BooleanField(default=False)

    class Meta:
        unique_together = ['equipo_a', 'equipo_b']

    def __str__(self):
        return f"{self.equipo_a} vs {self.equipo_b} - {self.instancia}"

    def clean(self):
        super().clean()
        if self.equipo_a == self.equipo_b:
            raise ValidationError("Los equipos A y B deben ser diferentes.")

        # Excluir la validación única al editar una instancia existente
        if self.pk is None or not Serie.objects.filter(pk=self.pk).exists():
            if Serie.objects.filter(equipo_a=self.equipo_a, equipo_b=self.equipo_b).exists() or \
                    Serie.objects.filter(equipo_a=self.equipo_b, equipo_b=self.equipo_a).exists():
                raise ValidationError("Ya existe una serie con estos equipos.")

        # Validación al finalizar la serie
        if self.finalizada:
            if self.juegos_ganados_equipo_a is None or self.juegos_ganados_equipo_b is None:
                raise ValidationError("Debe especificar los juegos ganados por cada equipo.")

            # Obtener el número de juegos necesarios para ganar de la instancia de la serie
            juegos_para_ganar = self.instancia.juegos_para_ganar

            # Calcular el máximo total de juegos
            max_total_juegos = (2 * juegos_para_ganar) - 1

            # Validar que ninguno de los equipos tenga más juegos ganados que juegos_para_ganar
            if self.juegos_ganados_equipo_a > juegos_para_ganar:
                raise ValidationError(f"El equipo {self.equipo_a} no puede tener más de {juegos_para_ganar} juegos ganados.")

            if self.juegos_ganados_equipo_b > juegos_para_ganar:
                raise ValidationError(f"El equipo {self.equipo_b}  no puede tener más de {juegos_para_ganar} juegos ganados.")

            # Validar la suma de juegos ganados
            if self.juegos_ganados_equipo_a + self.juegos_ganados_equipo_b > max_total_juegos:
                raise ValidationError(f"La suma de los juegos ganados por ambos equipos no puede ser mayor que {max_total_juegos}.")

            # Validar que al menos uno de los equipos haya ganado el número requerido de juegos
            if self.juegos_ganados_equipo_a < juegos_para_ganar and self.juegos_ganados_equipo_b < juegos_para_ganar:
                raise ValidationError(f"Uno de los equipos debe haber ganado al menos {juegos_para_ganar} juegos para que la serie sea válida.")
        


    def calcular_puntos(self):
        # Obtener los votos para esta serie
        votos = Voto.objects.filter(serie=self)

        # Obtener los puntos por acertar y el bono por resultado exacto de la instancia
        puntos_por_acertar = self.instancia.puntos_por_acertar
        bono_por_resultado_exacto = self.instancia.bono_por_resultado_exacto

        # Iterar sobre los votos y calcular los puntos para cada usuario
        for voto in votos:
            equipo_ganador_voto = 'A' if voto.juegos_equipo_a > voto.juegos_equipo_b else 'B'
            equipo_ganador_serie = 'A' if self.juegos_ganados_equipo_a > self.juegos_ganados_equipo_b else 'B'

            # Inicializar puntos en 0
            puntos = 0

            # Si el equipo elegido por el usuario coincide con el equipo ganador registrado en el backend,
            # asignar los puntos por acertar o el bono por resultado exacto
            if equipo_ganador_voto == equipo_ganador_serie:
                puntos += puntos_por_acertar
                if voto.juegos_equipo_a == self.juegos_ganados_equipo_a and voto.juegos_equipo_b == self.juegos_ganados_equipo_b:
                    puntos += bono_por_resultado_exacto

            # Actualizar los puntos en la tabla PuntosSerie para este usuario y esta serie
            puntos_serie, _ = PuntosSerie.objects.get_or_create(perfil=voto.usuario.perfil, serie=self)
            puntos_serie.puntos = puntos
            puntos_serie.save()

        # Actualizar los puntos totales en el perfil de cada usuario
        for voto in votos:
            perfil_usuario = voto.usuario.perfil
            total_puntos = PuntosSerie.objects.filter(perfil=perfil_usuario).aggregate(Sum('puntos'))['puntos__sum']
            perfil_usuario.puntos = total_puntos or 0  # Si total_puntos es None, asigna 0
            perfil_usuario.save()

    def save(self, *args, **kwargs):
        self.clean()  # Llamar a la validación antes de guardar
        super().save(*args, **kwargs)



class Voto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    serie = models.ForeignKey(Serie, on_delete=models.CASCADE)
    juegos_equipo_a = models.IntegerField(default=0)
    juegos_equipo_b = models.IntegerField(default=0)

    def clean(self):
        super().clean()
        # Aquí no realizamos la validación que depende de la serie

    def save(self, *args, **kwargs):
        # Realizamos la validación aquí
        self.validate_voto()
        super().save(*args, **kwargs)

    def validate_voto(self):
        # Verifica que la serie esté disponible
        if not self.serie:
            raise ValidationError("La serie no está definida.")

        # Obtener el número de juegos necesarios para ganar de la instancia de la serie
        juegos_para_ganar = self.serie.instancia.juegos_para_ganar
        max_total_juegos = (2 * juegos_para_ganar) - 1  # Máximo total de juegos

        # Validar el total de juegos
        total_juegos = self.juegos_equipo_a + self.juegos_equipo_b
        if total_juegos > max_total_juegos:
            raise ValidationError(f"El total de juegos no puede ser mayor que {max_total_juegos} para esta serie.")

        # Validar que ninguno de los equipos tenga más juegos ganados que juegos_para_ganar
        if self.juegos_equipo_a > juegos_para_ganar:
            raise ValidationError(f"El equipo {self.serie.equipo_a} no puede tener más de {juegos_para_ganar} juegos ganados.")

        if self.juegos_equipo_b > juegos_para_ganar:
            raise ValidationError(f"El equipo {self.serie.equipo_b}  no puede tener más de {juegos_para_ganar} juegos ganados.")

        # Validar que uno de los equipos debe tener el número requerido de juegos ganados
        if self.juegos_equipo_a < juegos_para_ganar and self.juegos_equipo_b < juegos_para_ganar:
            raise ValidationError(f"Uno de los equipos debe tener al menos {juegos_para_ganar} juegos ganados.")



class PuntosSerie(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    serie = models.ForeignKey(Serie, on_delete=models.CASCADE)
    puntos = models.IntegerField(default=0)
