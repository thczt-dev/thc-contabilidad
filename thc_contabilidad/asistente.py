"""Asistente gráfico de preferencias iniciales.

Se abre al terminar la instalación desde GitHub y, si no se ejecutó entonces,
en el primer arranque de la aplicación. Solo escribe `config.json`: nunca toca
la base de datos contable.

Uso directo (por ejemplo, desde `instalar-github.sh`):

    python3 -m thc_contabilidad.asistente
"""

from __future__ import annotations

import os

from . import config, rutas

rutas.preparar_entorno_gtk()

import gi  # noqa: E402

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from .ui_helpers import combo, etiqueta, marco_con_titulo, texto_combo  # noqa: E402

MUESTRA = "1.250.000,50"


def debe_mostrarse() -> bool:
    """True si aún no se han guardado preferencias (primera instalación)."""
    return not os.path.exists(config.RUTA)


class AsistenteDialog(Gtk.Dialog):
    """Selección inicial de idioma, tema, texto, moneda y confirmaciones."""

    def __init__(self, parent=None):
        super().__init__(
            title="Bienvenido a THC Contabilidad",
            transient_for=parent,
            modal=True,
        )
        self.add_buttons(
            "Omitir", Gtk.ResponseType.CANCEL,
            "Guardar y continuar", Gtk.ResponseType.OK,
        )
        self.set_default_size(560, 620)
        self.set_resizable(False)
        self.valores: dict = dict(config.PREDETERMINADOS)

        area = self.get_content_area()
        area.set_spacing(12)
        area.set_margin_start(20)
        area.set_margin_end(20)
        area.set_margin_top(18)
        area.set_margin_bottom(18)

        area.pack_start(etiqueta("Bienvenido a THC Contabilidad", "view-title"), False, False, 0)
        area.pack_start(
            etiqueta(
                "Elige tus preferencias iniciales. Podrás cambiarlas cuando quieras "
                "desde Ajustes.",
                "muted",
            ),
            False, False, 0,
        )

        area.pack_start(self._seccion("Idioma", self._combo_idioma()), False, False, 0)
        area.pack_start(self._seccion("Apariencia", self._combo_apariencia()), False, False, 0)
        area.pack_start(self._seccion("Moneda", self._combo_moneda()), False, False, 0)

        marco, caja = marco_con_titulo("Opciones generales")
        self.confirmar = Gtk.CheckButton(label="Confirmar al eliminar")
        self.confirmar.set_active(bool(config.get("confirmar_eliminar", True)))
        caja.pack_start(self.confirmar, False, False, 0)
        area.pack_start(marco, False, False, 0)

        area.pack_start(
            etiqueta(
                "Los importes se guardan siempre en centavos. Cambiar la moneda "
                "solo cambia cómo se muestran.",
                "settings-note",
            ),
            False, False, 0,
        )

        self.show_all()

    def _seccion(self, titulo: str, contenido: Gtk.Widget) -> Gtk.Frame:
        marco, caja = marco_con_titulo(titulo)
        caja.pack_start(contenido, False, False, 0)
        return marco

    def _combo_idioma(self) -> Gtk.Grid:
        codigos = [codigo for codigo, _nombre in config.IDIOMAS]
        nombres = [nombre for _codigo, nombre in config.IDIOMAS]
        actual = config.get("idioma", "es")
        visible = nombres[codigos.index(actual)] if actual in codigos else None
        self.idioma = combo(nombres, activo=visible, valores=codigos)
        return self._rejilla((("Idioma de la interfaz", self.idioma),))

    def _combo_apariencia(self) -> Gtk.Grid:
        self.tema = self._combo_codigos(
            ["Oscuro", "Claro", "Sistema"], config.TEMAS, config.get("tema", "oscuro")
        )
        self.tamano = self._combo_codigos(
            ["Pequeño", "Normal", "Grande"], config.TAMANOS_TEXTO,
            config.get("tamano_texto", "normal"),
        )
        return self._rejilla((
            ("Tema", self.tema),
            ("Tamaño del texto", self.tamano),
        ))

    def _combo_moneda(self) -> Gtk.Grid:
        codigos = list(config.MONEDAS)
        nombres = [config.MONEDAS[codigo][1] for codigo in codigos]
        actual = config.get("moneda", "COP")
        visible = config.MONEDAS[actual][1] if actual in config.MONEDAS else None
        self.moneda = combo(nombres, activo=visible, valores=codigos)
        self.formato = self._combo_codigos(
            ["Símbolo", "Código", "Sin símbolo"], config.FORMATOS_MONEDA,
            config.get("formato_moneda", "simbolo"),
        )
        self.vista = etiqueta("", "settings-note")
        self.moneda.connect("changed", self._actualizar_vista)
        self.formato.connect("changed", self._actualizar_vista)
        rejilla = self._rejilla((
            ("Moneda", self.moneda),
            ("Formato", self.formato),
            ("Vista previa", self.vista),
        ))
        self._actualizar_vista()
        return rejilla

    @staticmethod
    def _combo_codigos(opciones, codigos, activo) -> Gtk.ComboBoxText:
        visible = opciones[codigos.index(activo)] if activo in codigos else None
        return combo(opciones, activo=visible, valores=codigos)

    @staticmethod
    def _rejilla(campos) -> Gtk.Grid:
        rejilla = Gtk.Grid(row_spacing=8, column_spacing=12)
        for fila, (texto, widget) in enumerate(campos):
            rejilla.attach(etiqueta(texto + ":", "field-label"), 0, fila, 1, 1)
            rejilla.attach(widget, 1, fila, 1, 1)
        return rejilla

    def _actualizar_vista(self, *_argumentos):
        codigo = texto_combo(self.moneda) or "COP"
        formato = texto_combo(self.formato) or "simbolo"
        self.vista.set_label(config.formatear_texto(MUESTRA, codigo, formato))

    def leer_valores(self) -> dict:
        return {
            "idioma": texto_combo(self.idioma) or "es",
            "tema": texto_combo(self.tema) or "oscuro",
            "tamano_texto": texto_combo(self.tamano) or "normal",
            "moneda": texto_combo(self.moneda) or "COP",
            "formato_moneda": texto_combo(self.formato) or "simbolo",
            "confirmar_eliminar": self.confirmar.get_active(),
        }


def mostrar(parent=None) -> bool:
    """Muestra el asistente y guarda las preferencias. Devuelve True si se aceptó."""
    dialogo = AsistenteDialog(parent)
    respuesta = dialogo.run()
    aceptado = respuesta == Gtk.ResponseType.OK
    if aceptado:
        config.guardar(dialogo.leer_valores())
    elif not os.path.exists(config.RUTA):
        # Omitir también marca el primer arranque como completado.
        config.guardar({})
    dialogo.destroy()
    return aceptado


def main() -> None:
    mostrar()


if __name__ == "__main__":
    main()
