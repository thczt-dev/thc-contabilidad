"""Paleta oscura y estilos GTK de THC Contabilidad.

Todos los colores de la interfaz (incluidos los de tablas y diálogos) se
definen aquí para que el aspecto sea uniforme, sin depender del tema del
sistema.
"""

# Paleta
FONDO = "#0f1420"
PANEL = "#171d2b"
PANEL_CLARO = "#1b2333"
BORDE = "#252d3d"
ENTRADA = "#101725"
TEXTO = "#e8edf6"
TEXTO_SUAVE = "#93a1b8"
TEXTO_APAGADO = "#64748b"
ACENTO = "#8ab4ff"
ACENTO_HOVER = "#a6c7ff"
INGRESO = "#7ee0b8"
GASTO = "#ff9a9e"
ADVERTENCIA = "#ffcf8b"
NEUTRO = "#9aa9c0"

CSS = f"""
/* Fondo neutro para contenedores que GTK pinta con su tema propio. */
* {{ background-color: transparent; }}

window, dialog {{
    background-color: {FONDO};
    color: {TEXTO};
}}

viewport, notebook > frame, notebook > box, .view {{
    background-color: transparent;
}}

label {{ color: {TEXTO}; }}

.view-title {{ font-size: 21px; font-weight: 700; color: #f1f5fb; }}
.muted {{ color: {TEXTO_SUAVE}; font-size: 12px; }}
.card-title {{
    color: {TEXTO_SUAVE};
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.4px;
}}
.card-value {{ font-size: 26px; font-weight: 700; color: #f1f5fb; }}
.verde {{ color: {INGRESO}; }}
.rojo {{ color: {GASTO}; }}
.azul {{ color: {ACENTO}; }}
.panel-title {{ font-weight: 600; font-size: 13px; color: #d7e0ee; }}
.field-label {{ font-weight: 600; color: #b9c6da; }}
.total-label {{ color: #b9c6da; font-size: 12px; font-weight: 600; }}
.status {{ color: {TEXTO_SUAVE}; font-size: 12px; }}

frame {{ border: none; }}
.card, .panel {{
    background-color: {PANEL};
    border: 1px solid {BORDE};
    border-radius: 14px;
}}

headerbar {{
    background-color: #141b29;
    border-bottom: 1px solid {BORDE};
    padding: 9px 12px;
}}
headerbar label {{ color: #f1f5fb; }}
headerbar .subtitle {{ color: {TEXTO_SUAVE}; font-size: 11px; }}

notebook header, notebook header tabs {{ background-color: #141b29; }}
notebook header tabs tab {{
    background-color: transparent;
    border: none;
    padding: 11px 20px;
    color: {TEXTO_SUAVE};
    font-weight: 600;
}}
notebook header tabs tab:checked {{
    color: {ACENTO};
    box-shadow: inset 0 -2px 0 {ACENTO};
}}

entry {{
    background-color: {ENTRADA};
    color: {TEXTO};
    border: 1px solid #2b3649;
    border-radius: 8px;
    padding: 7px 10px;
}}
entry:focus {{
    border-color: {ACENTO};
    box-shadow: inset 0 0 0 1px {ACENTO};
}}
entry placeholder {{ color: {TEXTO_APAGADO}; }}

textview {{
    background-color: {ENTRADA};
    color: {TEXTO};
    border: 1px solid #2b3649;
    border-radius: 8px;
    padding: 6px;
}}

treeview.view {{
    background-color: {PANEL};
    color: {TEXTO};
}}
treeview.view:selected {{
    background-color: rgba(138, 180, 255, 0.22);
    color: #ffffff;
}}
treeview.view:hover {{ background-color: rgba(138, 180, 255, 0.07); }}
treeview header {{ background-color: {PANEL_CLARO}; }}
treeview header label {{
    color: {TEXTO_SUAVE};
    font-weight: 600;
    padding: 6px 8px;
}}

scrolledwindow {{ border: none; background-color: transparent; }}

button {{
    background-color: #202a3b;
    color: {TEXTO};
    border: 1px solid #2f3b50;
    border-radius: 9px;
    padding: 6px 12px;
}}
button:hover {{ background-color: #283449; }}
button:active {{ background-color: #313f57; }}
button.suggested-action {{
    background-color: {ACENTO};
    color: #0d1420;
    border: none;
    font-weight: 700;
}}
button.suggested-action:hover {{ background-color: {ACENTO_HOVER}; }}
button.destructive-action {{
    background-color: {GASTO};
    color: #2a1014;
    border: none;
    font-weight: 700;
}}

/* Punto de cobro */
.producto-card {{
    background-color: {PANEL_CLARO};
    border: 1px solid {BORDE};
    border-radius: 12px;
    padding: 10px;
}}
.producto-card:hover {{ background-color: #243049; border-color: {ACENTO}; }}
.producto-nombre {{ font-size: 13px; font-weight: 700; color: #f1f5fb; }}
.producto-precio {{ font-size: 12px; font-weight: 600; color: {ACENTO}; }}
.producto-tipo {{ font-size: 10px; color: {TEXTO_SUAVE}; }}
.paquete-card {{
    background-color: #1e2b45;
    border: 1px solid rgba(138, 180, 255, 0.55);
}}
.paquete-card:hover {{ background-color: #263658; }}
.paquete-card .producto-tipo {{ color: {ACENTO}; font-weight: 600; }}
.recomendado-badge {{
    font-size: 9px;
    color: {ACENTO};
    border: 1px solid rgba(138, 180, 255, 0.45);
    border-radius: 6px;
    padding: 1px 5px;
    margin-top: 2px;
}}

/* Calendario */
.mes-titulo {{ font-size: 17px; font-weight: 700; color: #f1f5fb; }}
.dia-semana {{ color: {TEXTO_SUAVE}; font-weight: 600; font-size: 11px; }}
.leyenda {{ color: {TEXTO_SUAVE}; font-size: 11px; }}
.caldia {{
    background-color: {PANEL};
    border: 1px solid {BORDE};
    border-radius: 10px;
    padding: 6px;
}}
.caldia:hover {{ background-color: #202a3b; }}
.caldia.seleccionado {{
    background-color: rgba(138, 180, 255, 0.18);
    border-color: {ACENTO};
}}
.caldia.otro-mes {{ opacity: 0.45; }}
.caldia .numero {{ font-size: 13px; font-weight: 700; color: {TEXTO}; }}
.caldia.hoy .numero {{ color: {ACENTO}; }}

popover, calendar {{ background-color: {PANEL_CLARO}; color: {TEXTO}; }}
calendar:selected {{ background-color: {ACENTO}; color: #0d1420; }}
menu {{ background-color: {PANEL_CLARO}; }}
menuitem {{ color: {TEXTO}; }}
menuitem:hover {{ background-color: {ACENTO}; color: #0d1420; }}
tooltip {{ background-color: #202a3b; color: {TEXTO}; }}
separator {{ color: {BORDE}; }}
""".encode("utf-8")
