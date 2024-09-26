from django.urls import path

from .views import registro, login_view,logout_view, votar_serie, series_abiertas, equipos_list, info, votaciones_usuario


urlpatterns = [
    path('', series_abiertas, name='series_abiertas'),    
    path('registro/', registro, name='registro'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('votar/<int:serie_id>/', votar_serie, name='votar_serie'),
    path('equipos-list/', equipos_list, name='equipos_list'),
    path('info/', info, name='info'),
    path('votaciones/<int:user_id>/', votaciones_usuario, name='votaciones_usuario'),
    

    # Otra configuración de URL, como la página de inicio, etc.
]
