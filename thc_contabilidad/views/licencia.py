"""Diálogo de activación de la edición Windows de pago."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk  # noqa: E402

from .. import licencia  # noqa: E402


class LicenciaDialog(Gtk.Dialog):
    """Muestra el estado de la suscripción y permite cargar license.json."""

    def __init__(self, parent=None):
        super().__init__(title="Licencia de THC Contabilidad", transient_for=parent, modal=True)
        self.add_buttons("Cerrar", Gtk.ResponseType.CLOSE)
        self.set_default_size(560, 420)
        self.set_resizable(False)

        area = self.get_content_area()
        area.set_spacing(10)
        area.set_border_width(18)

        self.estado = Gtk.Label()
        self.estado.set_xalign(0)
        self.estado.set_line_wrap(True)
        area.pack_start(self.estado, False, False, 0)

        ayuda = Gtk.Label(
            label=(
                "Tu suscripción se activa con un archivo firmado. Copia el código "
                "de máquina, envíalo junto con tu clave de licencia y guarda el "
                "archivo que recibas."
            )
        )
        ayuda.set_xalign(0)
        ayuda.set_line_wrap(True)
        area.pack_start(ayuda, False, False, 0)

        marco = Gtk.Frame(label="Código de máquina")
        codigo_caja = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        codigo_caja.set_border_width(8)
        self.codigo = Gtk.Label(selectable=True)
        self.codigo.set_line_wrap(True)
        self.codigo.set_max_width_chars(52)
        codigo_caja.pack_start(self.codigo, True, True, 0)

        copiar = Gtk.Button(label="Copiar")
        copiar.set_image(Gtk.Image.new_from_icon_name("edit-copy-symbolic", Gtk.IconSize.BUTTON))
        copiar.connect("clicked", self._copiar)
        codigo_caja.pack_start(copiar, False, False, 0)
        marco.add(codigo_caja)
        area.pack_start(marco, False, False, 0)

        selector = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        selector.pack_start(Gtk.Label(label="Archivo de licencia recibido:", xalign=0), False, False, 0)
        self.archivo = Gtk.FileChooserButton(title="Seleccionar license.json")
        filtro = Gtk.FileFilter()
        filtro.set_name("Archivos de licencia")
        filtro.add_pattern("*.json")
        self.archivo.add_filter(filtro)
        selector.pack_start(self.archivo, False, False, 0)
        area.pack_start(selector, False, False, 0)

        boton_activar = Gtk.Button(label="Activar licencia")
        boton_activar.connect("clicked", self._activar)
        area.pack_start(boton_activar, False, False, 0)

        self.mensaje = Gtk.Label()
        self.mensaje.set_xalign(0)
        self.mensaje.set_line_wrap(True)
        area.pack_start(self.mensaje, False, False, 0)

        self.actualizar()
        self.show_all()

    def actualizar(self):
        resultado = licencia.estado()
        texto = licencia.texto_estado(resultado)
        color = "#15803d" if resultado["activa"] else "#b91c1c"
        self.estado.set_markup(f"<b><span foreground='{color}'>{texto}</span></b>")
        self.codigo.set_text(resultado["codigo"] or "—")
        if resultado["id"]:
            self.estado.set_tooltip_text(f"Licencia {resultado['id']}")

    def _copiar(self, _boton):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(self.codigo.get_text(), -1)
        clipboard.store()
        self.mensaje.set_text("Código copiado al portapapeles.")

    def _activar(self, _boton):
        ruta = self.archivo.get_filename()
        if not ruta:
            self.mensaje.set_text("Selecciona primero el archivo license.json.")
            return
        try:
            licencia.activar_desde_archivo(ruta)
        except (OSError, ValueError) as exc:
            self.mensaje.set_text(f"No se pudo activar: {exc}")
            return
        self.actualizar()
        self.mensaje.set_text("Licencia activada correctamente.")
