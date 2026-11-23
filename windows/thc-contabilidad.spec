# -*- mode: python ; coding: utf-8 -*-
"""Especificación de PyInstaller para el paquete Windows de THC Contabilidad.

Se ejecuta desde build-windows.ps1. El prefijo de MSYS2 se toma de
MSYSTEM_PREFIX (o de C:\\msys64\\mingw64 por defecto). Se incluye el runtime
de GTK porque los temas de iconos, typelibs y esquemas no se descubren solos
dentro del ejecutable.
"""

import os

_spec_dir = globals().get("SPECPATH") or os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(_spec_dir)
RAIZ_PROYECTO = os.path.dirname(RAIZ)

MSYS_ROOT = os.environ.get("MSYSTEM_ROOT", r"C:\msys64")
PREFIJO = os.environ.get("MSYSTEM_PREFIX") or os.path.join(MSYS_ROOT, "mingw64")

if not os.path.isdir(PREFIJO):
    raise RuntimeError(
        f"No se encontró el prefijo de MSYS2 en {PREFIJO}. "
        "Define MSYSTEM_PREFIX antes de compilar."
    )


def arbol(origen, destino, aceptar=None):
    """Devuelve entradas (origen, destino) para todo un árbol de archivos."""
    if not os.path.isdir(origen):
        return []
    salida = []
    for raiz, directorios, archivos in os.walk(origen):
        directorios[:] = [d for d in directorios if d != "__pycache__"]
        relativo = os.path.relpath(raiz, origen)
        destino_actual = destino if relativo == "." else os.path.join(destino, relativo)
        for nombre in archivos:
            if aceptar and not aceptar(nombre):
                continue
            salida.append((os.path.join(raiz, nombre), destino_actual))
    return salida


def es_dll(nombre):
    nombre = nombre.lower()
    return nombre.endswith(".dll") and not nombre.startswith("python3")


# Todas las DLL de mingw64/bin. Se copian como binarios para que PyInstaller
# resuelva dependencias, pero se excluyen las del intérprete para no duplicar
# las que ya genera el propio PyInstaller.
binarios = arbol(os.path.join(PREFIJO, "bin"), ".", es_dll)

datos = [
    (os.path.join(RAIZ_PROYECTO, "thc-contabilidad.ico"), "."),
    (os.path.join(RAIZ_PROYECTO, "thc-contabilidad.png"), "."),
]

recursos = (
    (os.path.join("lib", "girepository-1.0"), os.path.join("lib", "girepository-1.0"), None),
    (
        os.path.join("lib", "gdk-pixbuf-2.0", "2.10.0", "loaders"),
        os.path.join("lib", "gdk-pixbuf-2.0", "2.10.0", "loaders"),
        lambda nombre: nombre.lower().endswith(".dll"),
    ),
    (
        os.path.join("share", "glib-2.0", "schemas"),
        os.path.join("share", "glib-2.0", "schemas"),
        lambda nombre: not nombre.endswith(".compiled"),
    ),
    (os.path.join("share", "icons"), os.path.join("share", "icons"), None),
    (os.path.join("share", "themes"), os.path.join("share", "themes"), None),
    (os.path.join("share", "locale"), os.path.join("share", "locale"), None),
    (os.path.join("etc", "gtk-3.0"), os.path.join("etc", "gtk-3.0"), None),
    (os.path.join("etc", "fonts"), os.path.join("etc", "fonts"), None),
)

for origen_rel, destino_rel, filtro in recursos:
    datos += arbol(os.path.join(PREFIJO, origen_rel), destino_rel, filtro)

ocultos = [
    "gi",
    "gi._gi",
    "gi._error",
    "gi._option",
    "gi._enum",
    "gi.repository",
    "cairo",
    "cairo._cairo",
    "cryptography",
    "cryptography.hazmat.primitives.asymmetric.ed25519",
]

excluidos = [
    "tkinter",
    "matplotlib",
    "numpy",
    "pytest",
    "IPython",
]

a = Analysis(
    [os.path.join(RAIZ, "entrypoint.py")],
    pathex=[RAIZ_PROYECTO, RAIZ],
    binaries=binarios,
    datas=datos,
    hiddenimports=ocultos,
    hookspath=[],
    runtime_hooks=[],
    excludes=excluidos,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

# La app normal no abre consola. La versión -diag sí, para --version y
# --smoke-test desde CI (y se excluye del instalador).
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="thc-contabilidad",
    icon=os.path.join(RAIZ_PROYECTO, "thc-contabilidad.ico"),
    console=False,
)

diag = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="thc-contabilidad-diag",
    icon=os.path.join(RAIZ_PROYECTO, "thc-contabilidad.ico"),
    console=True,
)

coll = COLLECT(
    exe,
    diag,
    a.binaries,
    a.zipfiles,
    a.datas,
    name="thc-contabilidad",
)
