"""Rutas de datos y recursos, válidas tanto en Linux como en Windows.

En Windows los datos van a ``%APPDATA%\\THC Contabilidad`` para que la
aplicación pueda instalarse en ``Program Files`` sin necesitar permisos de
escritura allí. En Linux se mantiene la ubicación histórica ``datos/`` junto
al código. Las variables de entorno ``THC_CONTABILIDAD_DB`` y
``THC_CONTABILIDAD_CONFIG`` siguen teniendo prioridad.
"""

from __future__ import annotations

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOMBRE_APLICACION = "THC Contabilidad"
VARIABLE_DB = "THC_CONTABILIDAD_DB"
VARIABLE_CONFIG = "THC_CONTABILIDAD_CONFIG"


def es_windows() -> bool:
    """True cuando se ejecuta sobre Windows (nativo, no bajo WSL)."""
    return os.name == "nt"


def directorio_datos() -> str:
    """Carpeta por defecto para la base de datos y las preferencias."""
    if es_windows():
        base = os.environ.get("APPDATA")
        if not base:
            base = os.path.join(os.path.expanduser("~"), "AppData", "Roaming")
        return os.path.join(base, NOMBRE_APLICACION)
    return os.path.join(BASE_DIR, "datos")


def ruta_db() -> str:
    """Ruta de la base de datos SQLite."""
    return os.environ.get(VARIABLE_DB) or os.path.join(
        directorio_datos(), "contabilidad.db"
    )


def ruta_config() -> str:
    """Ruta del JSON de preferencias."""
    return os.environ.get(VARIABLE_CONFIG) or os.path.join(
        directorio_datos(), "config.json"
    )


def directorio_recursos() -> str:
    """Raíz donde están los recursos incluidos en el paquete."""
    return getattr(sys, "_MEIPASS", None) or BASE_DIR


def recurso(*partes: str) -> str:
    """Devuelve la ruta de un recurso empaquetado (iconos, por ejemplo)."""
    return os.path.join(directorio_recursos(), *partes)


def icono_app() -> str:
    """Icono adecuado para la ventana: ICO en Windows, PNG en Linux."""
    preferido = "thc-contabilidad.ico" if es_windows() else "thc-contabilidad.png"
    ruta = recurso(preferido)
    if os.path.exists(ruta):
        return ruta
    return recurso("thc-contabilidad.svg")


def _anteponer_entorno(variable: str, valor: str) -> None:
    actual = os.environ.get(variable)
    os.environ[variable] = valor + (os.pathsep + actual if actual else "")


def preparar_entorno_gtk() -> None:
    """Configura GTK cuando la app se ejecuta desde el paquete de Windows.

    Debe llamarse antes de ``import gi``. En ejecuciones normales desde el
    código fuente no hace nada, para no alterar el entorno del sistema.
    """
    if not getattr(sys, "frozen", False):
        return

    raiz = getattr(sys, "_MEIPASS", None) or os.path.dirname(sys.executable)
    os.environ["GTK_DATA_PREFIX"] = raiz
    os.environ["GSETTINGS_SCHEMA_DIR"] = os.path.join(
        raiz, "share", "glib-2.0", "schemas"
    )
    os.environ["GDK_PIXBUF_MODULE_FILE"] = os.path.join(
        raiz, "lib", "gdk-pixbuf-2.0", "2.10.0", "loaders.cache"
    )
    _anteponer_entorno("GI_TYPELIB_PATH", os.path.join(raiz, "lib", "girepository-1.0"))
    _anteponer_entorno("XDG_DATA_DIRS", os.path.join(raiz, "share"))
    _anteponer_entorno("PATH", raiz)

    fuentes = os.path.join(raiz, "etc", "fonts", "fonts.conf")
    if os.path.exists(fuentes):
        os.environ["FONTCONFIG_FILE"] = fuentes
