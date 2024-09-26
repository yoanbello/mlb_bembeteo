from django import forms
from .models import Voto

class VotoForm(forms.ModelForm):
    class Meta:
        model = Voto
        fields = ['juegos_equipo_a', 'juegos_equipo_b']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Obtener la serie asociada al formulario
        serie = kwargs.get('initial').get('serie')
        
        # Obtener los nombres de los equipos de la serie
        equipo_a_nombre = serie.equipo_a.nombre
        equipo_b_nombre = serie.equipo_b.nombre
        
        # Actualizar las etiquetas de los campos con los nombres de los equipos
        self.fields['juegos_equipo_a'].label = equipo_a_nombre
        self.fields['juegos_equipo_b'].label = equipo_b_nombre
        
        # Agregar la clase 'input' a los widgets de los campos
        self.fields['juegos_equipo_a'].widget.attrs['class'] = 'input'
        self.fields['juegos_equipo_b'].widget.attrs['class'] = 'input'

