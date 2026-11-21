"""Punto de entrada de la aplicación."""

from __future__ import annotations

import os
import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Gio", "2.0")
from gi.repository import Gdk, Gio, Gtk  # noqa: E402

from . import __version__, theme  # noqa: E402
from .db import Database  # noqa: E402
from .ui_helpers import boton, etiqueta  # noqa: E402
from .views import (  # noqa: E402
    CalendarioView, ContactosView, MovimientosView, ProyectosView,
    ReportesView, ResumenView,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# La ruta puede sobreescribirse con THC_CONTABILIDAD_DB (útil para pruebas o
# para guardar los datos fuera del clon cuando el repositorio es de solo lectura).
RUTA_DB = os.environ.get("THC_CONTABILIDAD_DB") or os.path.join(
    BASE_DIR, "datos", "contabilidad.db"
)

PAGINA_RESUMEN = 0
PAGINA_MOVIMIENTOS = 1
PAGINA_PROYECTOS = 2
PAGINA_CALENDARIO = 3
PAGINA_CONTACTOS = 4
PAGINA_REPORTES = 5

def cargar_estilos():
    configuracion = Gtk.Settings.get_default()
    if configuracion is not None:
        configuracion.set_property("gtk-application-prefer-dark-theme", True)
    proveedor = Gtk.CssProvider()
    proveedor.load_from_data(theme.CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), proveedor,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )


class ThcApplication(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="com.thcdev.contabilidad",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.db: Database | None = None
        self.window: MainWindow | None = None

    def do_startup(self):
        Gtk.Application.do_startup(self)
        cargar_estilos()

        acciones = (
            ("nuevo-movimiento", self._nuevo_movimiento),
            ("nuevo-proyecto", self._nuevo_proyecto),
            ("calendario", self._ir_calendario),
            ("exportar", self._exportar),
            ("acerca-de", self._acerca_de),
            ("salir", self._salir),
        )
        for nombre, funcion in acciones:
            accion = Gio.SimpleAction.new(nombre, None)
            accion.connect("activate", funcion)
            self.add_action(accion)

        self.set_accels_for_action("app.nuevo-movimiento", ["<Control>n"])
        self.set_accels_for_action("app.nuevo-proyecto", ["<Control>p"])
        self.set_accels_for_action("app.calendario", ["<Control><Shift>c"])
        self.set_accels_for_action("app.exportar", ["<Control>e"])
        self.set_accels_for_action("app.salir", ["<Control>q"])

    def do_activate(self):
        if self.window is None:
            self.db = Database(RUTA_DB)
            self.window = MainWindow(self, self.db)
        self.window.present()

    def _nuevo_movimiento(self, _accion, _parametro):
        if self.window:
            self.window.ir_a(PAGINA_MOVIMIENTOS)
            self.window.movimientos.abrir_dialogo()

    def _nuevo_proyecto(self, _accion, _parametro):
        if self.window:
            self.window.ir_a(PAGINA_PROYECTOS)
            self.window.proyectos.abrir_dialogo()

    def _ir_calendario(self, _accion, _parametro):
        if self.window:
            self.window.ir_a(PAGINA_CALENDARIO)

    def _exportar(self, _accion, _parametro):
        if self.window:
            self.window.ir_a(PAGINA_REPORTES)
            self.window.reportes._exportar("movimientos")

    def _acerca_de(self, _accion, _parametro):
        if not self.window:
            return
        dialogo = Gtk.AboutDialog(transient_for=self.window, modal=True)
        dialogo.set_program_name("THC Contabilidad")
        dialogo.set_version(__version__)
        dialogo.set_comments(
            "Gestión sencilla de ingresos, gastos, proyectos, calendario, contactos y reportes.\n"
            "Datos guardados localmente en SQLite."
        )
        dialogo.set_authors(["ThcDev"])
        dialogo.set_website_label("ThcDev")
        dialogo.set_logo_icon_name("thc-contabilidad")
        dialogo.run()
        dialogo.destroy()

    def _salir(self, _accion, _parametro):
        self.quit()


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, aplicacion: ThcApplication, db: Database):
        super().__init__(application=aplicacion, title="THC Contabilidad")
        self.db = db
        self.set_default_size(1220, 820)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_name("thc-contabilidad")

        cabecera = Gtk.HeaderBar()
        cabecera.set_show_close_button(True)
        cabecera.props.title = "THC Contabilidad"
        cabecera.props.subtitle = "Ingresos, gastos y proyectos en un solo lugar"
        self.set_titlebar(cabecera)

        nuevo_mov = boton("list-add-symbolic", "Movimiento", "Nuevo ingreso o gasto (Ctrl+N)")
        nuevo_mov.get_style_context().add_class("suggested-action")
        nuevo_mov.connect("clicked", lambda *_: self._nuevo_movimiento())
        cabecera.pack_start(nuevo_mov)

        nuevo_proy = boton("document-new-symbolic", "Proyecto", "Nuevo proyecto (Ctrl+P)")
        nuevo_proy.connect("clicked", lambda *_: self._nuevo_proyecto())
        cabecera.pack_start(nuevo_proy)

        menu = Gio.Menu()
        menu.append("Ver calendario", "app.calendario")
        menu.append("Exportar movimientos a CSV", "app.exportar")
        menu.append("Acerca de THC Contabilidad", "app.acerca-de")
        menu.append("Salir", "app.salir")
        boton_menu = Gtk.MenuButton()
        boton_menu.set_image(Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.BUTTON))
        boton_menu.set_menu_model(menu)
        boton_menu.set_tooltip_text("Menú")
        cabecera.pack_end(boton_menu)

        self.status = etiqueta("Listo. Todos los datos se guardan en este equipo.", "status")
        barra_estado = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        barra_estado.set_border_width(6)
        barra_estado.pack_start(self.status, False, False, 0)

        self.resumen = ResumenView(self)
        self.movimientos = MovimientosView(self)
        self.proyectos = ProyectosView(self)
        self.calendario = CalendarioView(self)
        self.contactos = ContactosView(self)
        self.reportes = ReportesView(self)

        self.notebook = Gtk.Notebook()
        self.notebook.set_tab_pos(Gtk.PositionType.TOP)
        for titulo, vista in (
            ("Resumen", self.resumen),
            ("Movimientos", self.movimientos),
            ("Proyectos", self.proyectos),
            ("Calendario", self.calendario),
            ("Contactos", self.contactos),
            ("Reportes", self.reportes),
        ):
            self.notebook.append_page(vista, etiqueta(titulo))
        self.notebook.connect("switch-page", self._al_cambiar_pagina)

        contenedor = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        contenedor.pack_start(self.notebook, True, True, 0)
        contenedor.pack_start(barra_estado, False, False, 0)
        self.add(contenedor)
        self.show_all()

    def _al_cambiar_pagina(self, _notebook, pagina, _indice):
        if hasattr(pagina, "recargar"):
            pagina.recargar()

    def ir_a(self, indice: int):
        self.notebook.set_current_page(indice)

    def set_status(self, texto: str):
        self.status.set_label(texto)

    def actualizar_resumen(self):
        self.resumen.recargar()

    def actualizar_combos(self):
        """Los formularios leen los contactos al abrirse; método reservado."""
        return None

    def _nuevo_movimiento(self):
        self.ir_a(PAGINA_MOVIMIENTOS)
        self.movimientos.abrir_dialogo()

    def _nuevo_proyecto(self):
        self.ir_a(PAGINA_PROYECTOS)
        self.proyectos.abrir_dialogo()


def main():
    if "--version" in sys.argv[1:]:
        print(f"THC Contabilidad {__version__}")
        return 0
    aplicacion = ThcApplication()
    raise SystemExit(aplicacion.run(sys.argv))


if __name__ == "__main__":
    main()
