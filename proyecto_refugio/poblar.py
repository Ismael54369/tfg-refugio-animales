import os
import django
import random
from datetime import date, timedelta
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile

# 1. Conexión con Django (Asegúrate de que el nombre coincida con tu manage.py)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from refugio.models import Especie, Rasgo, Animal, SolicitudAdopcion, Donacion

def generar_foto_cuadrada(nombre, color_hex):
    """Genera una imagen perfectamente cuadrada (1:1) de 800x800 px"""
    img = Image.new('RGB', (800, 800), color=color_hex)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue(), f"{nombre.lower()}_perfil.png")

def sembrar_base_de_datos():
    print("🧹 Limpiando registros antiguos por seguridad...")
    Donacion.objects.all().delete()
    SolicitudAdopcion.objects.all().delete()
    Animal.objects.all().delete()
    Rasgo.objects.all().delete()
    Especie.objects.all().delete()

    # 2. Crear 6 Especies
    print("🐾 Creando Especies...")
    nombres_especies = ["Perro", "Gato", "Ave", "Reptil", "Roedor", "Exótico"]
    especies = [Especie.objects.create(nombre=n, descripcion=f"Tipo de animal: {n}") for n in nombres_especies]

    # 3. Crear 10 Rasgos
    print("✨ Creando Rasgos...")
    nombres_rasgos = ["Energético", "Tranquilo", "Cariñoso", "Veloz", "Vacunado", 
                      "Tímido", "Glotón", "Juguetón", "Protector", "Dormilón"]
    rasgos = [Rasgo.objects.create(nombre=n) for n in nombres_rasgos]

    # 4. Crear 30 Animales de forma dinámica
    print("🔴 Capturando 30 animales y generando sus fotos 1:1...")
    
    nombres_pokemon = [
        "Bulbasaur", "Charmander", "Squirtle", "Pikachu", "Eevee", "Snorlax", 
        "Gengar", "Arcanine", "Meowth", "Psyduck", "Machop", "Jigglypuff", 
        "Vulpix", "Zubat", "Oddish", "Diglett", "Mankey", "Abra", "Geodude", 
        "Ponyta", "Slowpoke", "Magnemite", "Doduo", "Seel", "Grimer", "Shellder", 
        "Gastly", "Onix", "Drowzee", "Krabby"
    ]
    
    colores_hex = ["#F08030", "#F8D030", "#A8A878", "#C03028", "#A040A0", "#78C850", "#6890F0", "#F85888", "#E0C068", "#A890F0"]
    estados_posibles = ['ADOPCION', 'REHAB', 'ADOPTADO']

    for nombre in nombres_pokemon:
        especie_random = random.choice(especies)
        color_random = random.choice(colores_hex)
        
        # Le damos un 60% de probabilidad de estar en Adopción, 20% Rehab, 20% Adoptado
        estado_random = random.choices(estados_posibles, weights=[60, 20, 20])[0] 
        
        # Fecha de nacimiento aleatoria en los últimos 5 años (1825 días)
        dias_restar = random.randint(100, 1825)
        fecha_nac = date.today() - timedelta(days=dias_restar)

        # Aquí usamos "historia" en lugar de "descripcion"
        animal = Animal(
            nombre=nombre,
            especie=especie_random,
            estado=estado_random,
            historia=f"Este valiente {especie_random.nombre} llamado {nombre} fue encontrado explorando la Ruta 1. Necesita un buen entrenador.",
            fecha_nacimiento=fecha_nac
        )
        
        # Guardar la foto cuadrada automática
        animal.foto.save(f"{nombre}.png", generar_foto_cuadrada(nombre, color_random), save=False)
        animal.save()
        
        # Añadir entre 2 y 4 rasgos aleatorios
        rasgos_random = random.sample(rasgos, k=random.randint(2, 4))
        animal.rasgos.set(rasgos_random)
        
        print(f"  -> {animal.nombre} registrado con éxito.")

    print("✅ ¡Siembra completada al 100%! Tienes 30 animales listos en tu base de datos PostgreSQL.")

if __name__ == '__main__':
    sembrar_base_de_datos()