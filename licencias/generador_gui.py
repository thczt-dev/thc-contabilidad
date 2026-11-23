"""Interfaz gráfica simple para gestionar licencias desde el PC del editor.

No se incluye en la app de usuario: se ejecuta con
``python3 licencias/generador_gui.py`` o con ``./licencias/generador-licencias``.
"""

from __future__ import annotations

import os
import sys
import urllib.parse

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk  # noqa: E402

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BASE)
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

try:  # permite ejecutarlo como script o importarlo como módulo del paquete
    from . import generar  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - ejecución directa
    import generar  # type: ignore[no-redef]

SALIDA_PREDETERMINADA = os.path.join(BASE, "salida")


class GeneradorWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Generador de licencias · THC Contabilidad")
        self.set_default_size(760, 640)
        self.set_border_width(18)

        principal = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.add(principal)

        titulo = Gtk.Label(label="<b>Generador de licencias THC</b>", use_markup=True, xalign=0)
        principal.pack_start(titulo, False, False, 0)

        principal.pack_start(self._frame_nueva_clave(), False, False, 0)
        principal.pack_start(self._frame_activar(), False, False, 0)
        principal.pack_start(self._frame_listado(), True, True, 0)

        self.estado = Gtk.Label(label="Listo.", xalign=0)
        self.estado.set_line_wrap(True)
        principal.pack_start(self.estado, False, False, 0)

        self._actualizar_lista()
        if not os.path.exists(generar.PRIVADA):
            self._mensaje("Falta licencias/private_key.pem. Genera las claves antes de emitir licencias.", error=True)

    # ------------------------------------------------------------------ ui

    def _frame_nueva_clave(self) -> Gtk.Frame:
        frame = Gtk.Frame(label="1 · Nueva clave de suscripción")
        caja = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        caja.set_border_width(12)
        frame.add(caja)

        grid = Gtk.Grid(row_spacing=6, column_spacing=10)
        grid.attach(Gtk.Label(label="Días de validez:", xalign=0), 0, 0, 1, 1)
        self.dias = Gtk.SpinButton.new_with_range(1, 3650, 1)
        self.dias.set_value(365)
        grid.attach(self.dias, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label="Máximo de equipos:", xalign=0), 0, 1, 1, 1)
        self.max_equipos = Gtk.SpinButton.new_with_range(1, 10, 1)
        self.max_equipos.set_value(2)
        grid.attach(self.max_equipos, 1, 1, 1, 1)

        grid.attach(Gtk.Label(label="Clave generada:", xalign=0), 0, 2, 1, 1)
        self.clave_generada = Gtk.Entry()
        self.clave_generada.set_editable(False)
        self.clave_generada.set_text("—")
        grid.attach(self.clave_generada, 1, 2, 1, 1)
        caja.pack_start(grid, False, False, 0)

        botones = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        generar_boton = Gtk.Button(label="Generar clave")
        generar_boton.connect("clicked", self._on_nueva_clave)
        copiar_boton = Gtk.Button(label="Copiar clave")
        copiar_boton.connect("clicked", self._on_copiar_clave)
        botones.pack_start(generar_boton, False, False, 0)
        botones.pack_start(copiar_boton, False, False, 0)
        caja.pack_start(botones, False, False, 0)
        return frame

    def _frame_activar(self) -> Gtk.Frame:
        frame = Gtk.Frame(label="2 · Emitir license.json")
        caja = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        caja.set_border_width(12)
        frame.add(caja)

        grid = Gtk.Grid(row_spacing=6, column_spacing=10)
        grid.attach(Gtk.Label(label="Clave:", xalign=0), 0, 0, 1, 1)
        self.clave = Gtk.Entry()
        self.clave.set_placeholder_text("THCW-XXXX-XXXX-XXXX")
        grid.attach(self.clave, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label="Código de máquina:", xalign=0), 0, 1, 1, 1)
        self.codigo = Gtk.Entry()
        self.codigo.set_placeholder_text("THCW1-...")
        self.codigo.set_width_chars(54)
        grid.attach(self.codigo, 1, 1, 1, 1)

        grid.attach(Gtk.Label(label="Carpeta de salida:", xalign=0), 0, 2, 1, 1)
        os.makedirs(SALIDA_PREDETERMINADA, exist_ok=True)
        self.carpeta = Gtk.FileChooserButton(title="Carpeta de salida")
        self.carpeta.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
        self.carpeta.set_current_folder(SALIDA_PREDETERMINADA)
        grid.attach(self.carpeta, 1, 2, 1, 1)
        caja.pack_start(grid, False, False, 0)

        botones = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        emitir = Gtk.Button(label="Emitir licencia")
        emitir.connect("clicked", self._on_emitir)
        abrir = Gtk.Button(label="Abrir carpeta")
        abrir.connect("clicked", self._on_abrir_carpeta)
        botones.pack_start(emitir, False, False, 0)
        botones.pack_start(abrir, False, False, 0)
        caja.pack_start(botones, False, False, 0)
        return frame

    def _frame_listado(self) -> Gtk.Frame:
        frame = Gtk.Frame(label="3 · Claves registradas")
        caja = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        caja.set_border_width(12)
        frame.add(caja)

        self.modelo = Gtk.ListStore(str, str, str)
        vista = Gtk.TreeView(model=self.modelo)
        for indice, titulo in enumerate(("Clave", "Caduca", "Equipos")):
            columna = Gtk.TreeViewColumn(titulo, Gtk.CellRendererText(), text=indice)
            vista.append_column(columna)

        desplazamiento = Gtk.ScrolledWindow()
        desplazamiento.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        desplazamiento.set_min_content_height(140)
        desplazamiento.add(vista)
        caja.pack_start(desplazamiento, True, True, 0)

        actualizar = Gtk.Button(label="Actualizar lista")
        actualizar.connect("clicked", lambda *_: self._actualizar_lista())
        caja.pack_start(actualizar, False, False, 0)
        return frame

    # --------------------------------------------------------------- acciones

    def _mensaje(self, texto: str, error: bool = False):
        self.estado.set_text(("⚠ " if error else "") + texto)

    def _actualizar_lista(self):
        self.modelo.clear()
        registro = generar.leer_registro()
        for clave, datos in registro["claves"].items():
            usadas = len(datos.get("activaciones", []))
            maximo = datos.get("max_equipos", 0)
            self.modelo.append([clave, datos.get("expires", "—"), f"{usadas}/{maximo}"])

    def _on_nueva_clave(self, _boton):
        try:
            clave = generar.nueva_clave(
                int(self.dias.get_value()), int(self.max_equipos.get_value())
            )
        except Exception as exc:
            self._mensaje(f"Error al crear la clave: {exc}", error=True)
            return
        self.clave_generada.set_text(clave)
        self.clave.set_text(clave)
        self._mensaje(f"Clave creada: {clave}")
        self._actualizar_lista()

    def _on_emitir(self, _boton):
        clave = self.clave.get_text().strip().upper()
        codigo = self.codigo.get_text().strip()
        if not clave or not codigo:
            self._mensaje("Escribe la clave y el código de máquina.", error=True)
            return
        carpeta = self.carpeta.get_filename() or SALIDA_PREDETERMINADA
        ruta = os.path.join(carpeta, f"license-{clave}.json")
        try:
            generar.activar(clave, codigo, ruta)
        except SystemExit as exc:
            self._mensaje(str(exc), error=True)
            return
        except Exception as exc:
            self._mensaje(f"No se pudo emitir la licencia: {exc}", error=True)
            return
        self._mensaje(f"Licencia generada: {ruta}")
        self._actualizar_lista()

    def _on_copiar_clave(self, _boton):
        texto = self.clave_generada.get_text()
        if not texto or texto == "—":
            texto = self.clave.get_text()
        if not texto:
            return
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(texto, -1)
        clipboard.store()
        self._mensaje(f"Clave copiada: {texto}")

    def _on_abrir_carpeta(self, _boton):
        carpeta = self.carpeta.get_filename() or SALIDA_PREDETERMINADA
        uri = "file://" + urllib.parse.quote(os.path.abspath(carpeta))
        try:
            Gtk.show_uri_on_window(self, uri, Gdk.CURRENT_TIME)
        except Exception as exc:
            self._mensaje(f"No se pudo abrir la carpeta: {exc}", error=True)


def main():
    ventana = GeneradorWindow()
    ventana.connect("destroy", Gtk.main_quit)
    ventana.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
