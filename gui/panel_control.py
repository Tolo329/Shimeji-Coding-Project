from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QProgressBar, QLabel
from PySide6.QtCore import Qt


class PanelControl(QFrame):
    """Panel flotante que muestra las estadisticas y botones de accion"""

    def __init__(self, callback_accion=None, parent=None):
        super().__init__(parent)
        self.callback_accion = callback_accion  # funcion que se llama al pulsar un boton

        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.setStyleSheet("""
            PanelControl {
                background: rgba(255, 255, 255, 235);
                border: 1px solid rgba(0, 0, 0, 30);
                border-radius: 16px;
            }
        """)

        self._crear_interfaz()

    def _crear_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(14, 12, 14, 12)

        # Encabezado con nombre y estado
        encabezado = QHBoxLayout()
        self.titulo = QLabel("Mi Mascota")
        self.titulo.setStyleSheet("color: #444; font-size: 14px; font-weight: bold;")
        self.estado_label = QLabel("")
        self.estado_label.setStyleSheet("color: #666; font-size: 11px;")
        encabezado.addWidget(self.titulo)
        encabezado.addStretch()
        encabezado.addWidget(self.estado_label)
        layout.addLayout(encabezado)

        # Barras de progreso para cada atributo
        self.barras = {}
        colores = {
            "hambre": "#FF6464",
            "felicidad": "#FFC832",
            "energia": "#64C8FF",
            "higiene": "#64FF96",
        }
        nombres = {
            "hambre": "Hambre",
            "felicidad": "Felicidad",
            "energia": "Energia",
            "higiene": "Higiene",
        }

        grid = QGridLayout()
        grid.setSpacing(6)

        for i, clave in enumerate(["hambre", "felicidad", "energia", "higiene"]):
            etiqueta = QLabel(nombres[clave])
            etiqueta.setStyleSheet("color: #555; font-size: 11px;")

            barra = QProgressBar()
            barra.setRange(0, 100)
            barra.setValue(50)
            barra.setFixedHeight(14)
            barra.setTextVisible(True)
            barra.setFormat("%v")
            barra.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid #ddd; border-radius: 7px;
                    background: #f0f0f0; height: 14px;
                }}
                QProgressBar::chunk {{
                    border-radius: 7px;
                    background: {colores[clave]};
                }}
            """)
            self.barras[clave] = barra
            grid.addWidget(etiqueta, i, 0)
            grid.addWidget(barra, i, 1)

        layout.addLayout(grid)

        # Linea separadora
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setStyleSheet("border: none; border-top: 1px solid #ddd;")
        layout.addWidget(linea)

        # Botones de accion (solo si hay un callback definido)
        if self.callback_accion:
            botones_layout = QGridLayout()
            botones_layout.setSpacing(6)

            acciones = [
                ("comer", "Comer"),
                ("jugar", "Jugar"),
                ("dormir", "Dormir"),
                ("banar", "Banar"),
            ]
            for idx, (clave, texto) in enumerate(acciones):
                boton = QPushButton(texto)
                boton.setFixedHeight(32)
                boton.setStyleSheet("""
                    QPushButton {
                        border: 1px solid #ccc; border-radius: 8px; padding: 4px 12px;
                        background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #fafafa, stop:1 #eee);
                        color: #333; font-size: 11px;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #e8e8e8, stop:1 #ddd);
                    }
                    QPushButton:pressed { background: #ccc; }
                """)
                boton.clicked.connect(lambda checked, k=clave: self.callback_accion(k))
                botones_layout.addWidget(boton, idx // 2, idx % 2)

            layout.addLayout(botones_layout)

        self.setFixedSize(self.sizeHint())

    def actualizar(self, mascota):
        """Actualiza las barras y el estado con los valores de la mascota"""
        self.barras["hambre"].setValue(100 - mascota.hambre)
        self.barras["felicidad"].setValue(mascota.felicidad)
        self.barras["energia"].setValue(mascota.energia)
        self.barras["higiene"].setValue(mascota.higiene)

        estados = {
            "muy_feliz": "Muy feliz",
            "feliz": "Feliz",
            "neutral": "Normal",
            "triste": "Triste",
            "enfermo": "Enfermo",
        }
        self.estado_label.setText(estados.get(mascota.obtener_estado_general(), ""))

    def mostrar_cerca_de(self, widget_origen):
        """Muestra el panel cerca del widget indicado"""
        punto = widget_origen.mapToGlobal(widget_origen.rect().topLeft())
        x = punto.x() - self.width() // 2 + widget_origen.width() // 2
        y = punto.y() - 170
        self.move(x, y)
        self.show()
        self.activateWindow()
        self.setFocus()

    def focusOutEvent(self, event):
        """Se oculta al perder el foco (click en otro lado)"""
        self.hide()
        super().focusOutEvent(event)
