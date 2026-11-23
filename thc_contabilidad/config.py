"""Preferencias personales de la aplicación (NO datos contables).

Se guardan en un JSON local, separado de la base de datos, para que cambiar el
idioma, el tema o la moneda nunca altere los importes ni el historial.
"""

from __future__ import annotations

import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA = os.environ.get("THC_CONTABILIDAD_CONFIG") or os.path.join(
    BASE_DIR, "datos", "config.json"
)

PREDETERMINADOS = {
    "idioma": "es",
    "tema": "oscuro",
    "tamano_texto": "normal",
    "moneda": "COP",
    "formato_moneda": "simbolo",
    "confirmar_eliminar": True,
}

# Código -> (símbolo, nombre legible en español)
MONEDAS = {
    "COP": ("$", "Peso colombiano"),
    "USD": ("US$", "Dólar estadounidense"),
    "EUR": ("€", "Euro"),
    "GBP": ("£", "Libra esterlina"),
    "MXN": ("MX$", "Peso mexicano"),
    "ARS": ("AR$", "Peso argentino"),
    "BRL": ("R$", "Real brasileño"),
    "CLP": ("CL$", "Peso chileno"),
    "PEN": ("S/", "Sol peruano"),
    "JPY": ("¥", "Yen japonés"),
}

IDIOMAS = (
    ("es", "Español"),
    ("en", "Inglés"),
    ("de", "Alemán"),
    ("ru", "Ruso"),
    ("zh", "Chino"),
    ("ja", "Japonés"),
    ("fr", "Francés"),
    ("pt", "Portugués"),
    ("it", "Italiano"),
    ("ko", "Coreano"),
)

TEMAS = ("oscuro", "claro", "sistema")
TAMANOS_TEXTO = ("pequeno", "normal", "grande")
FORMATOS_MONEDA = ("simbolo", "codigo", "plano")

_cache: dict | None = None


def cargar() -> dict:
    global _cache
    if _cache is None:
        datos = dict(PREDETERMINADOS)
        try:
            with open(RUTA, encoding="utf-8") as archivo:
                guardados = json.load(archivo)
            if isinstance(guardados, dict):
                datos.update({
                    clave: valor for clave, valor in guardados.items()
                    if clave in PREDETERMINADOS
                })
        except (OSError, ValueError):
            pass
        _cache = datos
    return _cache


def get(clave: str, defecto=None):
    return cargar().get(clave, PREDETERMINADOS.get(clave, defecto))


def guardar(cambios: dict) -> None:
    """Actualiza y persiste las preferencias indicadas."""
    datos = cargar()
    for clave, valor in cambios.items():
        if clave in PREDETERMINADOS:
            datos[clave] = valor
    os.makedirs(os.path.dirname(os.path.abspath(RUTA)), exist_ok=True)
    with open(RUTA, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2, sort_keys=True)
        archivo.write("\n")


def restablecer() -> None:
    global _cache
    _cache = dict(PREDETERMINADOS)
    guardar({})


def moneda_actual() -> tuple[str, str, str]:
    """Devuelve (código, símbolo, formato) de la moneda configurada."""
    codigo = get("moneda", "COP")
    if codigo not in MONEDAS:
        codigo = "COP"
    simbolo, _nombre = MONEDAS[codigo]
    formato = get("formato_moneda", "simbolo")
    if formato not in FORMATOS_MONEDA:
        formato = "simbolo"
    return codigo, simbolo, formato


def formatear_texto(texto: str, codigo: str | None = None, formato: str | None = None) -> str:
    """Aplica el prefijo elegido a un número ya formateado.

    Se usa tanto para mostrar los importes como para la vista previa de
    Ajustes, así que la preview y la app siempre coinciden.
    """
    codigo = codigo or get("moneda", "COP")
    if codigo not in MONEDAS:
        codigo = "COP"
    formato = formato or get("formato_moneda", "simbolo")
    if formato not in FORMATOS_MONEDA:
        formato = "simbolo"
    if formato == "codigo":
        return f"{codigo} {texto}"
    if formato == "plano":
        return texto
    return f"{MONEDAS[codigo][0]} {texto}"
