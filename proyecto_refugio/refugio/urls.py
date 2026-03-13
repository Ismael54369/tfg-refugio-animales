from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Rutas públicas
    path('', views.home, name='home'),
    path('pokedex/', views.lista_animales, name='lista_animales'),
    path('animal/<int:animal_id>/', views.detalle_animal, name='detalle_animal'),
    
    # Rutas de Adopción y Donación
    path('animal/<int:animal_id>/adoptar/', views.adoptar_animal, name='adoptar_animal'),
    path('animal/<int:animal_id>/donar/', views.donar_animal, name='donar_animal'), 

    path('donacion/exito/', views.pago_exitoso, name='pago_exitoso'),
    path('donacion/cancelada/', views.pago_cancelado, name='pago_cancelado'),

    # Panel Privado (CRUD)
    path('mi-perfil/', views.mi_perfil, name='mi_perfil'),
    path('solicitud/editar/<int:solicitud_id>/', views.editar_solicitud, name='editar_solicitud'),
    path('solicitud/cancelar/<int:solicitud_id>/', views.cancelar_solicitud, name='cancelar_solicitud'),

    # Rutas de Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='refugio/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('registro/', views.registro, name='registro'),
]