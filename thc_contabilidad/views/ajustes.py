"""Diálogo de preferencias personales (idioma, tema, moneda y opciones básicas)."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from .. import config  # noqa: E402
from ..i18n import idioma_actual, tr  # noqa: E402
from ..ui_helpers import boton, combo, etiqueta, marco_con_titulo, texto_combo  # noqa: E402

MUESTRA = 125_000_050  # 1.250.000,50 en centavos


def _combo(opciones, codigos, activo):
    """Crea un combo cuyas opciones visibles se traducen pero guarda códigos."""
    visible = opciones[codigos.index(activo)] if activo in codigos else None
    return combo(opciones, activo=visible, valores=codigos)


def _seleccionar(widget, codigo):
    valores = list(getattr(widget, "thc_valores", ()))
    if codigo in valores:
        widget.set_active(valores.index(codigo))


def _campo(texto: str) -> Gtk.Label:
    """Etiqueta de campo con los dos puntos fuera de la traducción."""
    return etiqueta(tr(texto) + ":", "field-label")


class AjustesDialog(Gtk.Dialog):
    """Preferencias locales: nunca escriben en la base de datos contable."""

    def __init__(self, parent):
        super().__init__(title=tr("Ajustes"), transient_for=parent, modal=True)
        self.set_default_size(560, 640)
        self.add_buttons(
            "_" + tr("Cancelar"), Gtk.ResponseType.CANCEL,
            "_" + tr("Guardar preferencias"), Gtk.ResponseType.OK,
        )
        self.valores: dict = {}

        area = self.get_content_area()
        area.set_spacing(14)
        area.set_margin_start(22)
        area.set_margin_end(22)
        area.set_margin_top(18)
        area.set_margin_bottom(18)

        area.pack_start(etiqueta("Ajustes", "view-title"), False, False, 0)
        area.pack_start(
            etiqueta("Cambia el aspecto y el idioma sin modificar tus datos.", "muted"),
            False, False, 0,
        )

        area.pack_start(self._seccion_apariencia(), False, False, 0)
        area.pack_start(self._seccion_idioma(), False, False, 0)
        area.pack_start(self._seccion_moneda(), False, False, 0)
        area.pack_start(self._seccion_general(), False, False, 0)
        self.show_all()

        self.connect("response", self._al_responder)

    # ------------------------------------------------------------- secciones

    def _seccion_apariencia(self):
        marco, caja = marco_con_titulo("Apariencia")
        rejilla = Gtk.Grid()
        rejilla.set_row_spacing(10)
        rejilla.set_column_spacing(14)

        self.tema = _combo(
            ["Oscuro", "Claro", "Sistema"], config.TEMAS, config.get("tema")
        )
        self.tamano = _combo(
            ["Pequeño", "Normal", "Grande"], config.TAMANOS_TEXTO,
            config.get("tamano_texto"),
        )
        for fila, (texto, widget) in enumerate((
            ("Tema:", self.tema),
            ("Tamaño del texto:", self.tamano),
        )):
            rejilla.attach(_campo(texto), 0, fila, 1, 1)
            rejilla.attach(widget, 1, fila, 1, 1)
        caja.pack_start(rejilla, False, False, 0)
        caja.pack_start(
            etiqueta("Los cambios se aplican al guardar.", "settings-note"), False, False, 0
        )
        return marco

    def _seccion_idioma(self):
        marco, caja = marco_con_titulo("Idioma")
        self.idioma = _combo(
            [nombre for _codigo, nombre in config.IDIOMAS],
            [codigo for codigo, _nombre in config.IDIOMAS],
            idioma_actual(),
        )
        caja.pack_start(self.idioma, False, False, 0)
        caja.pack_start(
            etiqueta("Los cambios se aplican al guardar.", "settings-note"), False, False, 0
        )
        return marco

    def _seccion_moneda(self):
        marco, caja = marco_con_titulo("Moneda")
        rejilla = Gtk.Grid()
        rejilla.set_row_spacing(10)
        rejilla.set_column_spacing(14)

        self.moneda = _combo(
            [nombre for _codigo, (_simbolo, nombre) in config.MONEDAS.items()],
            list(config.MONEDAS),
            config.get("moneda"),
        )
        self.formato = _combo(
            ["Símbolo", "Código", "Sin símbolo"], config.FORMATOS_MONEDA,
            config.get("formato_moneda"),
        )
        rejilla.attach(_campo("Moneda"), 0, 0, 1, 1)
        rejilla.attach(self.moneda, 1, 0, 1, 1)
        rejilla.attach(_campo("Formato de moneda"), 0, 1, 1, 1)
        rejilla.attach(self.formato, 1, 1, 1, 1)

        self.vista = etiqueta("", "settings-note")
        rejilla.attach(_campo("Vista previa"), 0, 2, 1, 1)
        rejilla.attach(self.vista, 1, 2, 1, 1)

        self.moneda.connect("changed", self._actualizar_vista)
        self.formato.connect("changed", self._actualizar_vista)
        self._actualizar_vista()

        caja.pack_start(rejilla, False, False, 0)
        caja.pack_start(etiqueta(
            "Los importes se guardan siempre en centavos. Cambiar de moneda solo cambia cómo se muestran.",
            "settings-note",
        ), False, False, 0)
        return marco

    def _seccion_general(self):
        marco, caja = marco_con_titulo("Opciones generales")
        self.confirmar = Gtk.CheckButton(label=tr("Confirmar al eliminar"))
        self.confirmar.set_active(bool(config.get("confirmar_eliminar", True)))
        caja.pack_start(self.confirmar, False, False, 0)

        restaurar = boton("view-refresh-symbolic", "Restablecer preferencias")
        restaurar.connect("clicked", self._restablecer)
        caja.pack_start(restaurar, False, False, 0)
        return marco

    # -------------------------------------------------------------- acciones

    def _actualizar_vista(self, *_argumentos):
        codigo = texto_combo(self.moneda) or "COP"
        formato = texto_combo(self.formato) or "simbolo"
        self.vista.set_label(config.formatear_texto("1.250.000,50", codigo, formato))

    def _restablecer(self, _widget):
        datos = config.PREDETERMINADOS
        _seleccionar(self.tema, datos["tema"])
        _seleccionar(self.tamano, datos["tamano_texto"])
        _seleccionar(self.idioma, datos["idioma"])
        _seleccionar(self.moneda, datos["moneda"])
        _seleccionar(self.formato, datos["formato_moneda"])
        self.confirmar.set_active(datos["confirmar_eliminar"])

    def _al_responder(self, _dialogo, respuesta):
        if respuesta != Gtk.ResponseType.OK:
            return
        self.valores = {
            "idioma": texto_combo(self.idioma) or "es",
            "tema": texto_combo(self.tema) or "oscuro",
            "tamano_texto": texto_combo(self.tamano) or "normal",
            "moneda": texto_combo(self.moneda) or "COP",
            "formato_moneda": texto_combo(self.formato) or "simbolo",
            "confirmar_eliminar": self.confirmar.get_active(),
        }
