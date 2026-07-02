import sys
from database.conexion import init_db
from database.repositorio import BaseDatos
from dominio.mascota import Mascota


def main():
    init_db()
    repo = BaseDatos()

    mascotas = repo.obtener_todas_mascotas()
    if mascotas:
        modelo = mascotas[0]
        mascota = Mascota.from_model(modelo)
        print(f"Mascota cargada: {mascota.nombre}")
    else:
        nombre = input("Nombre de tu mascota: ")
        mascota_id = repo.guardar_mascota(nombre)
        modelo = repo.obtener_mascota(mascota_id)
        mascota = Mascota.from_model(modelo)
        print(f"Mascota creada: {mascota.nombre}")

    print(f"Hambre: {mascota.hambre}")
    print(f"Felicidad: {mascota.felicidad}")
    print(f"Energía: {mascota.energia}")
    print(f"Higiene: {mascota.higiene}")
    print(f"Estado: {mascota.sprite_estado}")

    repo.actualizar_mascota(modelo.id, hambre=mascota.hambre, felicidad=mascota.felicidad,
                            energia=mascota.energia, higiene=mascota.higiene)
    print("Progreso guardado.")


if __name__ == "__main__":
    main()
