from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Animal, SolicitudAdopcion, Donacion, Especie
from .forms import SolicitudAdopcionForm, DonacionForm
import stripe
from django.conf import settings
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    return render(request, 'refugio/home.html')

def lista_animales(request):
    animales = Animal.objects.all()
    especies_db = Especie.objects.all() # <-- NUEVO: Obtenemos las especies
    
    estado = request.GET.get('estado')
    especie = request.GET.get('especie')
    busqueda = request.GET.get('q') 
    
    if estado:
        animales = animales.filter(estado=estado)
    if especie:
        animales = animales.filter(especie__nombre=especie)
    if busqueda:
        animales = animales.filter(nombre__icontains=busqueda)

    return render(request, 'refugio/lista.html', {
        'animales': animales, 
        'especies': especies_db 
    })

def detalle_animal(request, animal_id):
    animal = get_object_or_404(Animal, pk=animal_id)
    return render(request, 'refugio/detalle.html', {'animal': animal})

@login_required
def adoptar_animal(request, animal_id):
    animal = get_object_or_404(Animal, pk=animal_id)
    
    if animal.estado != 'ADOPCION':
        messages.error(request, 'Este compañero no está disponible para adopción en este momento.')
        return redirect('detalle_animal', animal_id=animal.id)

    solicitud_existente = SolicitudAdopcion.objects.filter(
        usuario=request.user, 
        animal=animal, 
        estado__in=['PENDIENTE', 'APROBADA']
    ).exists()

    if solicitud_existente:
        messages.error(request, f'Ya tienes una solicitud en curso o aprobada para {animal.nombre}.')
        return redirect('mi_perfil')

    if request.method == 'POST':
        form = SolicitudAdopcionForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.usuario = request.user
            solicitud.animal = animal
            solicitud.save()
            messages.success(request, f'¡Has lanzado tu Pokéball! Tu solicitud para adoptar a {animal.nombre} ha sido enviada.')
            return redirect('mi_perfil')
    else:
        form = SolicitudAdopcionForm()

    return render(request, 'refugio/adoptar.html', {'form': form, 'animal': animal})

@login_required
def donar_animal(request, animal_id):
    animal = get_object_or_404(Animal, pk=animal_id)

    if animal.estado != 'REHAB':
        messages.error(request, 'Este animal no necesita donaciones actualmente.')
        return redirect('detalle_animal', animal_id=animal.id)

    if request.method == 'POST':
        form = DonacionForm(request.POST)
        if form.is_valid():
            cantidad = form.cleaned_data['cantidad']
            mensaje = form.cleaned_data['mensaje']

            # 1. Guardamos los datos en la sesión porque Stripe nos sacará de la web
            request.session['donacion_data'] = {
                'animal_id': animal.id,
                'cantidad': float(cantidad),
                'mensaje': mensaje
            }

            # 2. Creamos la sesión de pago seguro en Stripe
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': f'Donación para {animal.nombre}',
                            'description': mensaje if mensaje else 'Ayuda para su rehabilitación',
                        },
                        'unit_amount': int(cantidad * 100), # Stripe cobra en céntimos
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(reverse('pago_exitoso')),
                cancel_url=request.build_absolute_uri(reverse('pago_cancelado')),
            )
            # 3. Redirigimos a la pasarela oficial de Stripe
            return redirect(checkout_session.url, code=303)
    else:
        form = DonacionForm()

    return render(request, 'refugio/donar.html', {'form': form, 'animal': animal})

@login_required
def pago_exitoso(request):
    donacion_data = request.session.get('donacion_data')
    
    if donacion_data:
        animal = get_object_or_404(Animal, pk=donacion_data['animal_id'])
        
        # Guardamos la donación real en la base de datos
        Donacion.objects.create(
            usuario=request.user,
            animal=animal,
            cantidad=donacion_data['cantidad'],
            mensaje=donacion_data['mensaje']
        )
        
        del request.session['donacion_data'] # Limpiamos la sesión por seguridad
        
        messages.success(request, f'¡Pago completado! Muchas gracias por ayudar a {animal.nombre}.')
        return redirect('mi_perfil')
    
    messages.error(request, 'No se encontraron datos de la donación.')
    return redirect('home')

@login_required
def pago_cancelado(request):
    messages.error(request, 'Has cancelado el pago. No se ha realizado ningún cargo.')
    return redirect('lista_animales')

def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Licencia de entrenador creada con éxito! Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'refugio/registro.html', {'form': form})

@login_required
def mi_perfil(request):
    solicitudes = SolicitudAdopcion.objects.filter(usuario=request.user).order_by('-fecha_solicitud')
    donaciones = Donacion.objects.filter(usuario=request.user).order_by('-fecha_donacion')
    return render(request, 'refugio/perfil.html', {'solicitudes': solicitudes, 'donaciones': donaciones})

@login_required
def editar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudAdopcion, pk=solicitud_id, usuario=request.user)
    
    if solicitud.estado != 'PENDIENTE':
        messages.error(request, 'No puedes editar una solicitud que ya está aprobada o rechazada.')
        return redirect('mi_perfil')

    if request.method == 'POST':
        form = SolicitudAdopcionForm(request.POST, instance=solicitud)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Datos actualizados correctamente en la Refugidex!')
            return redirect('mi_perfil')
    else:
        form = SolicitudAdopcionForm(instance=solicitud)

    return render(request, 'refugio/editar_solicitud.html', {'form': form, 'solicitud': solicitud})

@login_required
def cancelar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudAdopcion, pk=solicitud_id, usuario=request.user)
    
    if request.method == 'POST':
        solicitud.delete()
        messages.success(request, 'Has cancelado la solicitud de adopción.')
        return redirect('mi_perfil')

    return render(request, 'refugio/confirmar_cancelacion.html', {'solicitud': solicitud})