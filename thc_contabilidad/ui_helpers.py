"""Widgets y helpers reutilizables para la interfaz GTK."""

from __future__ import annotations

from datetime import datetime

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Pango", "1.0")
from gi.repository import Gtk, Pango  # noqa: E402

from .i18n import tr  # noqa: E402
from .utils import validar_fecha  # noqa: E402


class DateEntry(Gtk.Box):
    """Entrada de fecha AAAA-MM-DD con calendario emergente."""

    def __init__(self, valor: str = ""):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.entry = Gtk.Entry()
        self.entry.set_text(valor or "")
        self.entry.set_placeholder_text("AAAA-MM-DD")
        self.entry.set_width_chars(12)
        self.entry.set_max_width_chars(12)
        self.pack_start(self.entry, True, True, 0)

        boton = Gtk.Button()
        boton.set_image(Gtk.Image.new_from_icon_name("calendar-symbolic", Gtk.IconSize.BUTTON))
        boton.set_tooltip_text(tr("Elegir fecha"))
        boton.connect("clicked", self._abrir)
        self.pack_start(boton, False, False, 0)

        self.popover = Gtk.Popover()
        self.calendario = Gtk.Calendar()
        if valor:
            try:
                fecha = datetime.strptime(valor, "%Y-%m-%d")
                self.calendario.select_month(fecha.month - 1, fecha.year)
                self.calendario.select_day(fecha.day)
            except ValueError:
                pass
        self.calendario.connect("day-selected", self._dia_seleccionado)
        self.popover.add(self.calendario)
        self.popover.set_relative_to(boton)

    def _abrir(self, _boton):
        self.popover.popup()

    def _dia_seleccionado(self, calendario):
        fecha = calendario.get_date()
        self.entry.set_text(fecha.format("%Y-%m-%d"))
        self.popover.popdown()

    def get_text(self) -> str:
        return self.entry.get_text().strip()

    def set_text(self, texto: str):
        self.entry.set_text(texto or "")

    def get_fecha(self, obligatorio: bool = False):
        return validar_fecha(self.get_text(), obligatorio)


def combo(opciones, activo=None, editable=False, valores=None) -> Gtk.ComboBoxText:
    """Crea un ComboBoxText traducido, opcionalmente con texto libre.

    `opciones` son los valores internos (los que se guardan en la BD); se
    muestran traducidos. `valores` permite mostrar etiquetas distintas a los
    valores, por ejemplo los nombres de los idiomas.
    """
    widget = Gtk.ComboBoxText.new_with_entry() if editable else Gtk.ComboBoxText()
    visibles = [tr(str(opcion)) for opcion in opciones]
    for texto in visibles:
        widget.append_text(texto)
    # PyGObject no permite GObject.set_data(): se guardan como atributos Python.
    widget.thc_opciones = tuple(opciones)
    widget.thc_visibles = tuple(visibles)
    widget.thc_valores = tuple(valores) if valores is not None else tuple(opciones)
    if activo:
        if editable:
            texto = (visibles[list(opciones).index(activo)]
                     if activo in opciones else str(activo))
            widget.get_child().set_text(texto)
        elif activo in opciones:
            widget.set_active(list(opciones).index(activo))
    if not activo and not editable and opciones:
        widget.set_active(0)
    return widget


def texto_combo(widget) -> str:
    """Lee el valor interno de un combo (no su texto traducido)."""
    child = widget.get_child()
    texto = (child.get_text().strip() if isinstance(child, Gtk.Entry)
             else (widget.get_active_text() or "").strip())
    visibles = getattr(widget, "thc_visibles", ())
    valores = getattr(widget, "thc_valores", ())
    if texto in visibles and len(visibles) == len(valores):
        return str(valores[visibles.index(texto)])
    return texto


def _celda(_columna, celda, modelo, iterador, datos):
    indice, formato, color = datos
    valor = modelo.get_value(iterador, indice)
    if formato:
        celda.props.text = formato(valor)
    elif valor is None:
        celda.props.text = ""
    else:
        # `str(valor or "")` convertiría el entero 0 en una celda vacía.
        celda.props.text = tr(str(valor))
    if color:
        tono = color(valor)
        if tono:
            celda.props.foreground = tono


def agregar_columna(
    tree: Gtk.TreeView, titulo: str, indice: int, ancho: int = 0,
    formato=None, color=None, expandir=False, orden=None,
) -> Gtk.TreeViewColumn:
    renderer = Gtk.CellRendererText()
    renderer.set_property("ellipsize", Pango.EllipsizeMode.END)
    columna = Gtk.TreeViewColumn(tr(titulo), renderer, text=indice)
    if ancho:
        columna.set_min_width(ancho)
    columna.set_expand(expandir)
    columna.set_resizable(True)
    if orden is not None:
        columna.set_sort_column_id(orden)
    columna.set_cell_data_func(renderer, _celda, (indice, formato, color))
    tree.append_column(columna)
    return columna


def crear_tabla(
    columnas: list[dict], tipos_extra: tuple = (),
) -> tuple[Gtk.TreeView, Gtk.ListStore]:
    tipos = [columna.get("tipo", str) for columna in columnas] + list(tipos_extra)
    modelo = Gtk.ListStore(*tipos)
    tree = Gtk.TreeView(model=modelo)
    tree.set_headers_visible(True)
    tree.set_search_column(0)
    for columna in columnas:
        agregar_columna(
            tree,
            columna["titulo"],
            columna["indice"],
            columna.get("ancho", 0),
            columna.get("formato"),
            columna.get("color"),
            columna.get("expandir", False),
            columna.get("orden"),
        )
    return tree, modelo


def boton(icono: str, texto: str, tooltip: str = "") -> Gtk.Button:
    widget = Gtk.Button(label=tr(texto))
    widget.set_image(Gtk.Image.new_from_icon_name(icono, Gtk.IconSize.BUTTON))
    widget.set_always_show_image(True)
    if tooltip:
        widget.set_tooltip_text(tr(tooltip))
    return widget


def etiqueta(texto: str, clase: str | None = None, xalign: float = 0.0) -> Gtk.Label:
    widget = Gtk.Label(label=tr(texto), xalign=xalign)
    if clase:
        widget.get_style_context().add_class(clase)
    return widget


def tarjeta(titulo: str, clase: str = "") -> tuple[Gtk.Frame, Gtk.Label]:
    marco = Gtk.Frame()
    marco.get_style_context().add_class("card")
    caja = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    caja.set_border_width(20)
    titulo_widget = etiqueta(titulo, "card-title")
    valor = etiqueta("—", "card-value " + clase)
    caja.pack_start(titulo_widget, False, False, 0)
    caja.pack_start(valor, False, False, 0)
    marco.add(caja)
    return marco, valor


def marco_con_titulo(titulo: str) -> tuple[Gtk.Frame, Gtk.Box]:
    marco = Gtk.Frame()
    marco.get_style_context().add_class("panel")
    caja = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    caja.set_border_width(16)
    encabezado = etiqueta(titulo, "panel-title")
    caja.pack_start(encabezado, False, False, 0)
    marco.add(caja)
    return marco, caja


def confirmar(parent, titulo: str, mensaje: str) -> bool:
    from . import config  # importación diferida: Ajustes puede desactivar esto

    if not config.get("confirmar_eliminar", True):
        return True
    dialogo = Gtk.MessageDialog(
        parent, Gtk.DialogFlags.MODAL, Gtk.MessageType.QUESTION,
        Gtk.ButtonsType.NONE, tr(titulo),
    )
    dialogo.format_secondary_text(tr(mensaje))
    dialogo.add_button("_" + tr("Cancelar"), Gtk.ResponseType.CANCEL)
    aceptar = dialogo.add_button("_" + tr("Eliminar"), Gtk.ResponseType.YES)
    aceptar.get_style_context().add_class("destructive-action")
    respuesta = dialogo.run()
    dialogo.destroy()
    return respuesta == Gtk.ResponseType.YES


def mostrar_error(parent, mensaje: str, titulo: str = "No se pudo guardar"):
    dialogo = Gtk.MessageDialog(
        parent, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR,
        Gtk.ButtonsType.OK, tr(titulo),
    )
    dialogo.format_secondary_text(tr(mensaje))
    dialogo.run()
    dialogo.destroy()


def mostrar_info(parent, mensaje: str, titulo: str = "Información"):
    dialogo = Gtk.MessageDialog(
        parent, Gtk.DialogFlags.MODAL, Gtk.MessageType.INFO,
        Gtk.ButtonsType.OK, tr(titulo),
    )
    dialogo.format_secondary_text(tr(mensaje))
    dialogo.run()
    dialogo.destroy()
