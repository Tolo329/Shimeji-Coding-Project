import sys
from PySide6.QtWidgets import QApplication, QInputDialog
from database.conexion import init_db
from database.repositorio import BaseDatos
from dominio.mascota import Mascota
from gui.ventana_principal import VentanaPrincipal


def main():
    init_db()
    repo = BaseDatos()
    app = QApplication(sys.argv)

    mascotas = repo.obtener_todas_mascotas()
    if mascotas:
        modelo = mascotas[0]
        mascota = Mascota.from_model(modelo)
        mascota_id = modelo.id
    else:
        nombre, ok = QInputDialog.getText(None, "Nueva Mascota", "Nombre de tu mascota:")
        if not ok or not nombre.strip():
            nombre = "Mascota"
        mascota_id = repo.guardar_mascota(nombre.strip())
        modelo = repo.obtener_mascota(mascota_id)
        mascota = Mascota.from_model(modelo)

    window = VentanaPrincipal(mascota, repo, mascota_id)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
