"""Diálogo con los atajos de teclado disponibles en la aplicación."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from ..i18n import tr  # noqa: E402
from ..ui_helpers import etiqueta  # noqa: E402

ATAJOS = (
    ("Ctrl + N", "Nuevo movimiento"),
    ("Ctrl + P", "Nuevo proyecto"),
    ("Ctrl + Shift + C", "Ver calendario"),
    ("Ctrl + Shift + V", "Nuevo cobro (POS)"),
    ("Ctrl + E", "Exportar movimientos a CSV"),
    ("Ctrl + F", "Buscar en Movimientos"),
    ("Ctrl + 1 … 7", "Ir a Resumen, Movimientos, Proyectos, Calendario, Cobros, Contactos o Reportes"),
    ("Ctrl + ,", "Ajustes"),
    ("Ctrl + F1", "Ver esta ayuda"),
    ("Ctrl + Q", "Salir"),
)


class AtajosDialog(Gtk.Dialog):
    """Muestra los atajos sin modificar ningún dato."""

    def __init__(self, parent=None):
        super().__init__(title=tr("Atajos de teclado"), transient_for=parent, modal=True)
        self.add_buttons("_" + tr("Cerrar"), Gtk.ResponseType.CLOSE)
        self.set_default_size(560, 460)
        self.set_resizable(False)

        area = self.get_content_area()
        area.set_spacing(12)
        area.set_margin_start(22)
        area.set_margin_end(22)
        area.set_margin_top(18)
        area.set_margin_bottom(18)

        area.pack_start(etiqueta(tr("Atajos de teclado"), "view-title"), False, False, 0)
        area.pack_start(
            etiqueta(tr("Acciones rápidas disponibles en toda la aplicación."), "muted"),
            False, False, 0,
        )

        rejilla = Gtk.Grid()
        rejilla.set_column_spacing(18)
        rejilla.set_row_spacing(8)
        for fila, (atajo, descripcion) in enumerate(ATAJOS):
            tecla = etiqueta(atajo, "field-label", xalign=1.0)
            rejilla.attach(tecla, 0, fila, 1, 1)
            texto = etiqueta(tr(descripcion), "muted", xalign=0.0)
            texto.set_line_wrap(True)
            rejilla.attach(texto, 1, fila, 1, 1)
        area.pack_start(rejilla, False, False, 0)
        self.show_all()
