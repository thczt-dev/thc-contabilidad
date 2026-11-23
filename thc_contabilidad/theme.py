"""Paletas y estilos GTK de THC Contabilidad.

El tema oscuro con acento azul pastel sigue siendo el predeterminado. Desde
Ajustes se puede cambiar a claro o seguir la configuración del sistema, sin
tocar los datos de la base de datos.
"""

from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk  # noqa: E402

# ------------------------------------------------------------------ paletas

PALETAS = {
    "oscuro": {
        "fondo": "#0f1420",
        "panel": "#171d2b",
        "panel_claro": "#1b2333",
        "borde": "#252d3d",
        "entrada": "#101725",
        "texto": "#e8edf6",
        "texto_suave": "#93a1b8",
        "texto_apagado": "#64748b",
        "acento": "#8ab4ff",
        "acento_hover": "#a6c7ff",
        "acento_tenue": "rgba(138, 180, 255, 0.22)",
        "acento_linea": "rgba(138, 180, 255, 0.45)",
        "ingreso": "#7ee0b8",
        "gasto": "#ff9a9e",
        "advertencia": "#ffcf8b",
        "neutro": "#9aa9c0",
        "cabecera": "#141b29",
        "titulo": "#f1f5fb",
        "boton": "#202a3b",
        "boton_hover": "#283449",
        "boton_activo": "#313f57",
        "tarjeta_hover": "#243049",
        "paquete": "#1e2b45",
        "paquete_hover": "#263658",
        "texto_acento": "#0d1420",
    },
    "claro": {
        "fondo": "#f4f7fb",
        "panel": "#ffffff",
        "panel_claro": "#eef2f8",
        "borde": "#d7e0ec",
        "entrada": "#ffffff",
        "texto": "#1b2637",
        "texto_suave": "#5d6d84",
        "texto_apagado": "#94a3b8",
        "acento": "#3769cc",
        "acento_hover": "#2c5bb5",
        "acento_tenue": "rgba(55, 105, 204, 0.13)",
        "acento_linea": "rgba(55, 105, 204, 0.40)",
        "ingreso": "#12855c",
        "gasto": "#c13a56",
        "advertencia": "#a76a00",
        "neutro": "#64748b",
        "cabecera": "#e9eff8",
        "titulo": "#16243a",
        "boton": "#e6ecf5",
        "boton_hover": "#dbe5f2",
        "boton_activo": "#cddbec",
        "tarjeta_hover": "#e4edfa",
        "paquete": "#e7effc",
        "paquete_hover": "#dce9fb",
        "texto_acento": "#ffffff",
    },
}

ESCALAS = {"pequeno": 0.90, "normal": 1.0, "grande": 1.15}

# Compatibilidad: los módulos que importan constantes siguen funcionando y se
# actualizan al aplicar un tema distinto.
FONDO = PALETAS["oscuro"]["fondo"]
PANEL = PALETAS["oscuro"]["panel"]
PANEL_CLARO = PALETAS["oscuro"]["panel_claro"]
BORDE = PALETAS["oscuro"]["borde"]
ENTRADA = PALETAS["oscuro"]["entrada"]
TEXTO = PALETAS["oscuro"]["texto"]
TEXTO_SUAVE = PALETAS["oscuro"]["texto_suave"]
TEXTO_APAGADO = PALETAS["oscuro"]["texto_apagado"]
ACENTO = PALETAS["oscuro"]["acento"]
ACENTO_HOVER = PALETAS["oscuro"]["acento_hover"]
INGRESO = PALETAS["oscuro"]["ingreso"]
GASTO = PALETAS["oscuro"]["gasto"]
ADVERTENCIA = PALETAS["oscuro"]["advertencia"]
NEUTRO = PALETAS["oscuro"]["neutro"]

_proveedor = None
_tema_activo = "oscuro"


def resolver_tema(nombre: str) -> str:
    """Resuelve «sistema» a claro u oscuro según el escritorio."""
    if nombre not in (*PALETAS, "sistema"):
        nombre = "oscuro"
    if nombre != "sistema":
        return nombre
    ajustes = Gtk.Settings.get_default()
    if ajustes is None:
        return "oscuro"
    nombre_tema = ajustes.get_property("gtk-theme-name") or ""
    if "dark" in nombre_tema.lower():
        return "oscuro"
    if "light" in nombre_tema.lower():
        return "claro"
    return "oscuro" if ajustes.get_property("gtk-application-prefer-dark-theme") else "claro"


def construir_css(nombre: str = "oscuro", tamano: str = "normal") -> bytes:
    """Genera la hoja de estilos para el tema y tamaño de texto dados."""
    p = PALETAS[resolver_tema(nombre)]
    escala = ESCALAS.get(tamano, 1.0)

    def px(valor: float) -> str:
        return f"{round(valor * escala)}px"

    return f"""
* {{ background-color: transparent; }}

window, dialog {{
    background-color: {p["fondo"]};
    color: {p["texto"]};
}}

viewport, notebook > frame, notebook > box, .view {{
    background-color: transparent;
}}

label {{ color: {p["texto"]}; }}

.view-title {{ font-size: {px(21)}; font-weight: 700; color: {p["titulo"]}; }}
.muted {{ color: {p["texto_suave"]}; font-size: {px(12)}; }}
.card-title {{
    color: {p["texto_suave"]};
    font-size: {px(12)};
    font-weight: 600;
    letter-spacing: 0.4px;
}}
.card-value {{ font-size: {px(26)}; font-weight: 700; color: {p["titulo"]}; }}
.verde {{ color: {p["ingreso"]}; }}
.rojo {{ color: {p["gasto"]}; }}
.azul {{ color: {p["acento"]}; }}
.panel-title {{ font-weight: 600; font-size: {px(13)}; color: {p["titulo"]}; }}
.field-label {{ font-weight: 600; color: {p["texto_suave"]}; }}
.total-label {{ color: {p["texto_suave"]}; font-size: {px(12)}; }}
.status {{ color: {p["texto_suave"]}; font-size: {px(12)}; }}

frame {{ border: none; }}
.card, .panel {{
    background-color: {p["panel"]};
    border: 1px solid {p["borde"]};
    border-radius: 14px;
}}

headerbar {{
    background-color: {p["cabecera"]};
    border-bottom: 1px solid {p["borde"]};
    padding: 9px 12px;
}}
headerbar label {{ color: {p["titulo"]}; }}
headerbar .subtitle {{ color: {p["texto_suave"]}; font-size: {px(11)}; }}

notebook header, notebook header tabs {{ background-color: {p["cabecera"]}; }}
notebook header tabs tab {{
    background-color: transparent;
    border: none;
    padding: 11px 20px;
    color: {p["texto_suave"]};
    font-weight: 600;
}}
notebook header tabs tab:checked {{
    color: {p["acento"]};
    box-shadow: inset 0 -2px 0 {p["acento"]};
}}
.tab-label {{ font-size: {px(12)}; font-weight: 600; }}

entry {{
    background-color: {p["entrada"]};
    color: {p["texto"]};
    border: 1px solid {p["borde"]};
    border-radius: 8px;
    padding: 7px 10px;
}}
entry:focus {{
    border-color: {p["acento"]};
    box-shadow: inset 0 0 0 1px {p["acento"]};
}}
entry placeholder {{ color: {p["texto_apagado"]}; }}

textview {{
    background-color: {p["entrada"]};
    color: {p["texto"]};
    border: 1px solid {p["borde"]};
    border-radius: 8px;
    padding: 6px;
}}

treeview.view {{
    background-color: {p["panel"]};
    color: {p["texto"]};
}}
treeview.view:selected {{
    background-color: {p["acento_tenue"]};
    color: {p["titulo"]};
}}
treeview.view:hover {{ background-color: {p["acento_tenue"]}; }}
treeview header {{ background-color: {p["panel_claro"]}; }}
treeview header label {{
    color: {p["texto_suave"]};
    font-weight: 600;
    padding: 6px 8px;
}}

scrolledwindow {{ border: none; background-color: transparent; }}

button {{
    background-color: {p["boton"]};
    color: {p["texto"]};
    border: 1px solid {p["borde"]};
    border-radius: 9px;
    padding: 6px 12px;
}}
button:hover {{ background-color: {p["boton_hover"]}; }}
button:active {{ background-color: {p["boton_activo"]}; }}
button.suggested-action {{
    background-color: {p["acento"]};
    color: {p["texto_acento"]};
    border: none;
    font-weight: 700;
}}
button.suggested-action:hover {{ background-color: {p["acento_hover"]}; }}
button.destructive-action {{
    background-color: {p["gasto"]};
    color: {p["texto_acento"]};
    border: none;
    font-weight: 700;
}}

/* Punto de cobro */
.producto-card {{
    background-color: {p["panel_claro"]};
    border: 1px solid {p["borde"]};
    border-radius: 12px;
    padding: 10px;
}}
.producto-card:hover {{ background-color: {p["tarjeta_hover"]}; border-color: {p["acento"]}; }}
.producto-nombre {{ font-size: {px(13)}; font-weight: 700; color: {p["titulo"]}; }}
.producto-precio {{ font-size: {px(12)}; font-weight: 600; color: {p["acento"]}; }}
.producto-tipo {{ font-size: {px(10)}; color: {p["texto_suave"]}; }}
.paquete-card {{
    background-color: {p["paquete"]};
    border: 1px solid {p["acento_linea"]};
}}
.paquete-card:hover {{ background-color: {p["paquete_hover"]}; }}
.paquete-card .producto-tipo {{ color: {p["acento"]}; font-weight: 600; }}
.recomendado-badge {{
    font-size: {px(9)};
    color: {p["acento"]};
    border: 1px solid {p["acento_linea"]};
    border-radius: 6px;
    padding: 1px 5px;
    margin-top: 2px;
}}

/* Calendario */
.mes-titulo {{ font-size: {px(17)}; font-weight: 700; color: {p["titulo"]}; }}
.dia-semana {{ color: {p["texto_suave"]}; font-weight: 600; font-size: {px(11)}; }}
.leyenda {{ color: {p["texto_suave"]}; font-size: {px(11)}; }}
.caldia {{
    background-color: {p["panel"]};
    border: 1px solid {p["borde"]};
    border-radius: 10px;
    padding: 6px;
}}
.caldia:hover {{ background-color: {p["boton_hover"]}; }}
.caldia.seleccionado {{
    background-color: {p["acento_tenue"]};
    border-color: {p["acento"]};
}}
.caldia.otro-mes {{ opacity: 0.45; }}
.caldia .numero {{ font-size: {px(13)}; font-weight: 700; color: {p["texto"]}; }}
.caldia.hoy .numero {{ color: {p["acento"]}; }}

popover, calendar {{ background-color: {p["panel_claro"]}; color: {p["texto"]}; }}
calendar:selected {{ background-color: {p["acento"]}; color: {p["texto_acento"]}; }}
menu {{ background-color: {p["panel_claro"]}; }}
menuitem {{ color: {p["texto"]}; }}
menuitem:hover {{ background-color: {p["acento"]}; color: {p["texto_acento"]}; }}
tooltip {{ background-color: {p["boton"]}; color: {p["texto"]}; }}
separator {{ color: {p["borde"]}; }}

/* Ajustes */
.settings-section {{ font-weight: 700; color: {p["acento"]}; }}
.settings-note {{ color: {p["texto_suave"]}; font-size: {px(11)}; }}
""".encode("utf-8")


def aplicar_tema(nombre: str = "oscuro", tamano: str = "normal") -> None:
    """Aplica el tema en toda la app, reemplazando el proveedor anterior."""
    global _proveedor, _tema_activo
    global FONDO, PANEL, PANEL_CLARO, BORDE, ENTRADA, TEXTO, TEXTO_SUAVE
    global TEXTO_APAGADO, ACENTO, ACENTO_HOVER, INGRESO, GASTO
    global ADVERTENCIA, NEUTRO, CSS

    screen = Gdk.Screen.get_default()
    if screen is not None and _proveedor is not None:
        Gtk.StyleContext.remove_provider_for_screen(screen, _proveedor)

    resuelto = resolver_tema(nombre)
    p = PALETAS[resuelto]
    FONDO, PANEL, PANEL_CLARO, BORDE, ENTRADA = (
        p["fondo"], p["panel"], p["panel_claro"], p["borde"], p["entrada"]
    )
    TEXTO, TEXTO_SUAVE, TEXTO_APAGADO = p["texto"], p["texto_suave"], p["texto_apagado"]
    ACENTO, ACENTO_HOVER = p["acento"], p["acento_hover"]
    INGRESO, GASTO, ADVERTENCIA, NEUTRO = (
        p["ingreso"], p["gasto"], p["advertencia"], p["neutro"]
    )
    CSS = construir_css(nombre, tamano)
    _tema_activo = nombre

    ajustes = Gtk.Settings.get_default()
    if ajustes is not None:
        ajustes.set_property("gtk-application-prefer-dark-theme", resuelto == "oscuro")

    if screen is not None:
        _proveedor = Gtk.CssProvider()
        _proveedor.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            screen, _proveedor, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )


def tema_activo() -> str:
    return _tema_activo


CSS = construir_css()
