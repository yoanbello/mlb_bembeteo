
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import VotoForm
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Voto
from django.db.models import Q
from django.contrib import messages


from .models import Equipo, Perfil, Serie, Voto, PuntosSerie

def registro(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        equipo_campeon_id = request.POST.get('equipo_campeon')

        if password1 != password2:
            return render(request, 'polls/registro.html', {'error': 'Las contraseñas no coinciden'})

        if not equipo_campeon_id:
            return render(request, 'polls/registro.html', {'error': 'Debes seleccionar un equipo'})

        equipo_campeon = Equipo.objects.get(id=equipo_campeon_id)
        user = User.objects.create_user(username=username, password=password1)
        Perfil.objects.create(user=user, equipo_campeon=equipo_campeon)
        
        # Redirigir al usuario a la página de inicio de sesión
        return render(request, 'polls/login.html')
    
    
    return render(request, 'polls/registro.html')



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # Esta línea debe recibir el usuario autenticado como argumento
            # Redireccionar a alguna página de éxito, por ejemplo:
            return redirect('series_abiertas')
        else:
            # Usuario no válido, mostrar mensaje de error
            return render(request, 'polls/login.html', {'error_message': 'Credenciales inválidas'})
    else:
        return render(request, 'polls/login.html')
    
def logout_view(request):
    logout(request)
    return redirect('home')
    
def home(request):
    perfiles = Perfil.objects.order_by('-puntos')
    # Pasar los perfiles al template
    return render(request, 'polls/home.html', {'perfiles': perfiles})


@login_required
def series_abiertas(request):
    try:
        # Obtener todas las series abiertas
        series_abiertas = Serie.objects.all()        
        return render(request, 'polls/series_abiertas.html', {'series_abiertas': series_abiertas})
    except PermissionDenied:
        # Redirigir al usuario a la página de inicio de sesión si no tiene permiso
        return redirect('login')

from django.contrib import messages
from django.core.exceptions import ValidationError

@login_required
def votar_serie(request, serie_id):
    try:
        serie = get_object_or_404(Serie, id=serie_id)
        if not serie.abierta:
            return HttpResponse("Esta serie está cerrada para votación.")
        
        usuario = request.user
        voto_existente = Voto.objects.filter(usuario=usuario, serie=serie).first()
        
        if request.method == 'POST':
            form = VotoForm(request.POST, instance=voto_existente, initial={'serie': serie})
            perfil_usuario = Perfil.objects.get(user=usuario)
            if form.is_valid():
                form.instance.usuario = usuario
                form.instance.serie = serie
                try:
                    form.save()  # Intenta guardar el voto
                except ValidationError as e:
                    for error in e.messages:  # `e.messages` es una lista
                        messages.error(request, error) 
                      
                else:
                    # Si no hay excepciones, reiniciar puntos o crear uno nuevo
                    try:
                        puntos_serie = PuntosSerie.objects.get(perfil=perfil_usuario, serie=serie)
                        puntos_serie.puntos = 0
                    except PuntosSerie.DoesNotExist:
                        PuntosSerie.objects.create(perfil=perfil_usuario, serie=serie)
                    return redirect('series_abiertas')
        
        else:
            form = VotoForm(instance=voto_existente, initial={'serie': serie})
        
        return render(request, 'polls/votar_serie.html', {'serie': serie, 'form': form})
    
    except PermissionDenied:
        return redirect('login')



def equipos_list(request):
    equipos = Equipo.objects.filter(eliminado=False)
    data = [{'id': equipo.id, 'nombre': equipo.nombre} for equipo in equipos]
    return JsonResponse(data, safe=False)

def info(request):    
    return render(request, 'polls/info.html')  

def votaciones_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    
    # Filtrar las votaciones del usuario y las series abiertas en false
    votos_usuario = Voto.objects.filter(usuario=usuario)
    votos_usuario = votos_usuario.filter(serie__abierta=False)
    
    rondas = set(voto.serie.instancia.nombre for voto in votos_usuario)
    
    votos_por_ronda = {}
    for ronda in rondas:
        votos_por_ronda[ronda] = [voto for voto in votos_usuario if voto.serie.instancia.nombre == ronda]
    
    return render(request, 'polls/votaciones_usuario.html', {'usuario': usuario, 'votos_por_ronda': votos_por_ronda})














