"""Traducción de la interfaz.

Las claves son los textos originales en español. Si una frase todavía no tiene
traducción, se muestra el original: la app nunca se queda sin texto.
"""

from __future__ import annotations

from . import config
from .i18n_data import TRADUCCIONES

IDIOMAS = config.IDIOMAS


def idioma_actual() -> str:
    codigo = config.get("idioma", "es")
    return codigo if codigo in dict(IDIOMAS) else "es"


def tr(texto: str) -> str:
    """Devuelve `texto` en el idioma configurado."""
    if not texto:
        return texto
    return TRADUCCIONES.get(idioma_actual(), {}).get(texto, texto)


def nombre_idioma(codigo: str | None = None) -> str:
    codigo = codigo or idioma_actual()
    return dict(IDIOMAS).get(codigo, codigo)


ETIQUETAS_PRECIO = {
    "Desde": "Desde (precio)",
    "Adicional desde": "Adicional desde (precio)",
    "por producto": "por producto",
}


def tr_etiqueta_precio(valor: str) -> str:
    """Traduce solo la etiqueta comercial, sin tocar el valor guardado."""
    return tr(ETIQUETAS_PRECIO.get(valor, valor))


def trf(plantilla: str, **valores) -> str:
    """Traduce una plantilla sencilla con marcadores `{{nombre}}`."""
    resultado = tr(plantilla)
    for nombre, valor in valores.items():
        resultado = resultado.replace("{" + nombre + "}", str(valor))
    return resultado
