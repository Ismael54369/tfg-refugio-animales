import os
import django
import random
import requests
from datetime import date, timedelta
from django.core.files.base import ContentFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from refugio.models import Especie, Rasgo, Animal, SolicitudAdopcion, Donacion

def obtener_foto_real(nombre, nombre_especie, indice):
    print(f"    📸 Descargando foto de {nombre_especie} para {nombre}...")
    
    # Traducimos tu especie a etiquetas de búsqueda precisas en inglés
    diccionario_especies = {
        "Perro": "dog,hound",
        "Gato": "cat,kitten",
        "Ave": "bird,parrot",
        "Reptil": "reptile,lizard,iguana",
        "Roedor": "hamster,mouse,guineapig",
        "Exótico": "wildlife,exotic,animal"
    }
    
    terminos_busqueda = diccionario_especies.get(nombre_especie, "pet")
    
    # Usamos el índice del bucle + un número aleatorio alto para garantizar que NUNCA se repitan
    lock_id = indice + random.randint(10000, 99999)
    url = f"https://loremflickr.com/800/800/{terminos_busqueda}?lock={lock_id}"
    
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        return ContentFile(respuesta.content, f"{nombre.lower()}_foto.jpg")
    return None

def sembrar_base_de_datos():
    print("🧹 Limpiando registros antiguos...")
    Donacion.objects.all().delete()
    SolicitudAdopcion.objects.all().delete()
    Animal.objects.all().delete()
    Rasgo.objects.all().delete()
    Especie.objects.all().delete()

    print("🐾 Creando Especies...")
    nombres_especies = ["Perro", "Gato", "Ave", "Reptil", "Roedor", "Exótico"]
    especies = [Especie.objects.create(nombre=n) for n in nombres_especies]

    print("✨ Creando Rasgos...")
    nombres_rasgos = ["Energético", "Tranquilo", "Cariñoso", "Veloz", "Vacunado", "Juguetón"]
    rasgos = [Rasgo.objects.create(nombre=n) for n in nombres_rasgos]

    print("🔴 Capturando 30 animales con fotos inteligentes (Tardará unos 30-40 segundos)...")
    nombres_pokemon = [
        "Bulbasaur", "Charmander", "Squirtle", "Pikachu", "Eevee", "Snorlax", 
        "Gengar", "Arcanine", "Meowth", "Psyduck", "Machop", "Jigglypuff", 
        "Vulpix", "Zubat", "Oddish", "Diglett", "Mankey", "Abra", "Geodude", 
        "Ponyta", "Slowpoke", "Magnemite", "Doduo", "Seel", "Grimer", "Shellder", 
        "Gastly", "Onix", "Drowzee", "Krabby"
    ]
    
    # Usamos enumerate para tener un índice (i) único por cada animal
    for i, nombre in enumerate(nombres_pokemon):
        especie_random = random.choice(especies)
        animal = Animal(
            nombre=nombre,
            especie=especie_random,
            estado=random.choices(['ADOPCION', 'REHAB', 'ADOPTADO'], weights=[60, 20, 20])[0],
            historia=f"Este valiente {especie_random.nombre} llamado {nombre} necesita un buen hogar.",
            fecha_nacimiento=date.today() - timedelta(days=random.randint(100, 1825))
        )
        
        # Le pasamos el nombre, la especie exacta y su número de índice único
        foto_real = obtener_foto_real(nombre, especie_random.nombre, i)
        if foto_real:
            animal.foto.save(f"{nombre}.jpg", foto_real, save=False)
            
        animal.save()
        animal.rasgos.set(random.sample(rasgos, k=random.randint(2, 4)))
        print(f"  -> ✅ {animal.nombre} registrado correctamente.")

    print("🎉 ¡Siembra completada con éxito! Revisa tu Pokédex.")

if __name__ == '__main__':
    sembrar_base_de_datos()