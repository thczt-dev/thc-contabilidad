"""Punto de entrada de la aplicación."""

from __future__ import annotations

import os
import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gio", "2.0")
from gi.repository import Gio, Gtk  # noqa: E402

from . import __version__, config, theme  # noqa: E402
from .db import Database  # noqa: E402
from .i18n import tr  # noqa: E402
from .ui_helpers import boton, etiqueta  # noqa: E402
from .views import (  # noqa: E402
    AjustesDialog, CalendarioView, CobrosView, ContactosView, MovimientosView,
    ProyectosView, ReportesView, ResumenView,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# La ruta puede sobreescribirse con THC_CONTABILIDAD_DB (útil para pruebas o
# para guardar los datos fuera del clon cuando el repositorio es de solo lectura).
RUTA_DB = os.environ.get("THC_CONTABILIDAD_DB") or os.path.join(
    BASE_DIR, "datos", "contabilidad.db"
)

# Orden real de las pestañas del Notebook. La navegación usa las vistas como
# referencia para que un reordenamiento no rompa los atajos.
PAGINA_RESUMEN = 0
PAGINA_MOVIMIENTOS = 1
PAGINA_PROYECTOS = 2
PAGINA_CALENDARIO = 3
PAGINA_COBROS = 4
PAGINA_CONTACTOS = 5
PAGINA_REPORTES = 6

# Icono symbolic de cada pestaña (todos presentes en los temas de iconos de GTK).
PESTANAS = (
    ("Resumen", "view-grid-symbolic", ResumenView),
    ("Movimientos", "view-list-symbolic", MovimientosView),
    ("Proyectos", "folder-symbolic", ProyectosView),
    ("Calendario", "office-calendar-symbolic", CalendarioView),
    ("Cobros", "accessories-calculator-symbolic", CobrosView),
    ("Contactos", "address-book-new-symbolic", ContactosView),
    ("Reportes", "x-office-spreadsheet-symbolic", ReportesView),
)


def cargar_estilos():
    """Aplica el tema elegido en Ajustes (oscuro, claro o sistema)."""
    theme.aplicar_tema(config.get("tema"), config.get("tamano_texto"))


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
            ("cobro", self._nuevo_cobro),
            ("exportar", self._exportar),
            ("ajustes", self._abrir_ajustes),
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
        self.set_accels_for_action("app.cobro", ["<Control><Shift>v"])
        self.set_accels_for_action("app.exportar", ["<Control>e"])
        self.set_accels_for_action("app.ajustes", ["<Control>comma"])
        self.set_accels_for_action("app.salir", ["<Control>q"])

    def do_activate(self):
        if self.window is None:
            self.db = Database(RUTA_DB)
            self.window = MainWindow(self, self.db)
        self.window.present()

    def _nuevo_movimiento(self, _accion, _parametro):
        if self.window:
            self.window.ir_a(self.window.movimientos)
            self.window.movimientos.abrir_dialogo()

    def _nuevo_proyecto(self, _accion, _parametro):
        if self.window:
            self.window.ir_a(self.window.proyectos)
            self.window.proyectos.abrir_dialogo()

    def _ir_calendario(self, _accion, _parametro):
        if self.window:
            self.window.ir_a(self.window.calendario)

    def _nuevo_cobro(self, _accion, _parametro):
        if self.window:
            self.window.ir_a(self.window.cobros)
            self.window.cobros.sub.set_current_page(0)

    def _exportar(self, _accion, _parametro):
        if self.window:
            self.window.ir_a(self.window.reportes)
            self.window.reportes._exportar("movimientos")

    def _abrir_ajustes(self, _accion=None, _parametro=None):
        if not self.window:
            return
        dialogo = AjustesDialog(self.window)
        respuesta = dialogo.run()
        cambios = dict(dialogo.valores) if respuesta == Gtk.ResponseType.OK else {}
        dialogo.destroy()
        if not cambios:
            return

        cambia_idioma = cambios.get("idioma") != config.get("idioma")
        config.guardar(cambios)
        theme.aplicar_tema(config.get("tema"), config.get("tamano_texto"))
        if cambia_idioma:
            self.recargar_interfaz()
        else:
            self.window.set_status(tr("Preferencias guardadas"))

    def recargar_interfaz(self):
        """Reconstruye la ventana para que el nuevo idioma se vea en todas partes."""
        anterior = self.window
        pagina = anterior.notebook.get_current_page() if anterior else 0
        if anterior is not None:
            anterior.destroy()
        self.window = MainWindow(self, self.db)
        if 0 <= pagina < self.window.notebook.get_n_pages():
            self.window.notebook.set_current_page(pagina)
        self.window.present()
        self.window.set_status(tr("Preferencias guardadas"))

    def _acerca_de(self, _accion, _parametro):
        if not self.window:
            return
        dialogo = Gtk.AboutDialog(transient_for=self.window, modal=True)
        dialogo.set_program_name("THC Contabilidad")
        dialogo.set_version(__version__)
        dialogo.set_comments(
            tr("Gestión sencilla de ingresos, gastos, proyectos, calendario, cobros, contactos y reportes.")
            + "\n" + tr("Datos guardados localmente en SQLite.")
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
        self.aplicacion = aplicacion
        self.db = db
        self.set_default_size(1220, 820)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_name("thc-contabilidad")

        cabecera = Gtk.HeaderBar()
        cabecera.set_show_close_button(True)
        cabecera.props.title = "THC Contabilidad"
        cabecera.props.subtitle = tr("Ingresos, gastos y proyectos en un solo lugar")
        self.set_titlebar(cabecera)

        nuevo_mov = boton("list-add-symbolic", "Movimiento", "Nuevo ingreso o gasto (Ctrl+N)")
        nuevo_mov.get_style_context().add_class("suggested-action")
        nuevo_mov.connect("clicked", lambda *_: self._nuevo_movimiento())
        cabecera.pack_start(nuevo_mov)

        nuevo_proy = boton("document-new-symbolic", "Proyecto", "Nuevo proyecto (Ctrl+P)")
        nuevo_proy.connect("clicked", lambda *_: self._nuevo_proyecto())
        cabecera.pack_start(nuevo_proy)

        cobrar = boton("accessories-calculator-symbolic", "Cobrar", "Nuevo cobro (Ctrl+Shift+V)")
        cobrar.connect("clicked", lambda *_: self._nuevo_cobro())
        cabecera.pack_start(cobrar)

        menu = Gio.Menu()
        menu.append(tr("Nuevo cobro (POS)"), "app.cobro")
        menu.append(tr("Ver calendario"), "app.calendario")
        menu.append(tr("Exportar movimientos a CSV"), "app.exportar")
        menu.append(tr("Ajustes"), "app.ajustes")
        menu.append(tr("Acerca de THC Contabilidad"), "app.acerca-de")
        menu.append(tr("Salir"), "app.salir")
        boton_menu = Gtk.MenuButton()
        boton_menu.set_image(Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.BUTTON))
        boton_menu.set_menu_model(menu)
        boton_menu.set_tooltip_text(tr("Menú"))
        cabecera.pack_end(boton_menu)

        ajustes = Gtk.Button.new_from_icon_name(
            "preferences-system-symbolic", Gtk.IconSize.BUTTON
        )
        ajustes.set_tooltip_text(tr("Ajustes") + " (Ctrl+,)")
        ajustes.connect("clicked", lambda *_: self.aplicacion._abrir_ajustes())
        cabecera.pack_end(ajustes)

        self.status = etiqueta("Listo. Todos los datos se guardan en este equipo.", "status")
        barra_estado = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        barra_estado.set_border_width(6)
        barra_estado.pack_start(self.status, False, False, 0)

        self.notebook = Gtk.Notebook()
        self.notebook.set_tab_pos(Gtk.PositionType.TOP)
        for titulo, icono, clase in PESTANAS:
            vista = clase(self)
            setattr(self, titulo.lower(), vista)
            etiqueta_pestana = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL, spacing=6
            )
            etiqueta_pestana.pack_start(
                Gtk.Image.new_from_icon_name(icono, Gtk.IconSize.MENU), False, False, 0
            )
            etiqueta_pestana.pack_start(etiqueta(titulo, "tab-label"), False, False, 0)
            etiqueta_pestana.show_all()
            self.notebook.append_page(vista, etiqueta_pestana)
        self.notebook.connect("switch-page", self._al_cambiar_pagina)

        contenedor = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        contenedor.pack_start(self.notebook, True, True, 0)
        contenedor.pack_start(barra_estado, False, False, 0)
        self.add(contenedor)
        self.show_all()

    def _al_cambiar_pagina(self, _notebook, pagina, _indice):
        if hasattr(pagina, "recargar"):
            pagina.recargar()

    def ir_a(self, destino):
        """Va a una pestaña por índice o, de forma segura, por vista/widget."""
        indice = (self.notebook.page_num(destino) if isinstance(destino, Gtk.Widget)
                  else destino)
        self.notebook.set_current_page(indice)

    def set_status(self, texto: str):
        self.status.set_label(texto)

    def actualizar_resumen(self):
        """Refresca todas las vistas que dependen de los movimientos."""
        for vista in (self.resumen, self.movimientos, self.calendario, self.reportes):
            vista.recargar()

    def actualizar_combos(self):
        """Los formularios leen los contactos al abrirse; método reservado."""
        return None

    def _nuevo_movimiento(self):
        self.ir_a(self.movimientos)
        self.movimientos.abrir_dialogo()

    def _nuevo_proyecto(self):
        self.ir_a(self.proyectos)
        self.proyectos.abrir_dialogo()

    def _nuevo_cobro(self):
        self.ir_a(self.cobros)
        self.cobros.sub.set_current_page(0)


def main():
    if "--version" in sys.argv[1:]:
        print(f"THC Contabilidad {__version__}")
        return 0
    aplicacion = ThcApplication()
    raise SystemExit(aplicacion.run(sys.argv))


if __name__ == "__main__":
    main()
