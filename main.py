import sys
from PySide6.QtWidgets import QApplication, QInputDialog
from database.conexion import init_db
from database.repositorio import BaseDatos
from dominio.mascota import Mascota
from gui.ventana_principal import VentanaPrincipal


def main():
    # Inicializar base de datos y crear tablas si no existen
    init_db()
    repo = BaseDatos()
    app = QApplication(sys.argv)

    # Buscar si ya hay una mascota guardada
    mascotas = repo.obtener_todas_mascotas()
    if mascotas:
        # Cargar la primera mascota encontrada
        modelo = mascotas[0]
        mascota = Mascota.copiar_desde_modelo(modelo)
        mascota_id = modelo.id
    else:
        # Pedir nombre y crear mascota nueva
        nombre, ok = QInputDialog.getText(None, "Nueva Mascota", "Nombre de tu mascota:")
        if not ok or not nombre.strip():
            nombre = "Mascota"
        mascota_id = repo.guardar_mascota(nombre.strip())
        modelo = repo.obtener_mascota(mascota_id)
        mascota = Mascota.copiar_desde_modelo(modelo)

    # Mostrar la ventana de la mascota
    ventana = VentanaPrincipal(mascota, repo, mascota_id)
    ventana.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
