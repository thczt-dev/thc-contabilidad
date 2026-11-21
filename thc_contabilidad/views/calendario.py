"""Calendario mensual con plazos de proyectos y movimientos por día."""

from __future__ import annotations

import calendar
from datetime import date, timedelta

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from .. import theme  # noqa: E402
from ..ui_helpers import boton, crear_tabla, etiqueta, marco_con_titulo, tarjeta  # noqa: E402
from ..utils import (  # noqa: E402
    MESES_LARGOS, formatear_monto, fecha_legible, primer_dia_mes, sumar_meses,
)

DIAS_SEMANA = ("Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom")
DIAS_LARGOS = (
    "lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo",
)


class CalendarioView(Gtk.Box):
    def __init__(self, ventana):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        self.ventana = ventana
        self.db = ventana.db
        self.set_margin_start(30)
        self.set_margin_end(30)
        self.set_margin_top(26)
        self.set_margin_bottom(24)

        hoy = date.today()
        self.mes_actual = primer_dia_mes(hoy)
        self.dia_seleccionado = hoy
        self.datos_dia: dict[str, dict] = {}
        self.hitos: dict[str, dict] = {}

        cabecera = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        cabecera.pack_start(etiqueta("Calendario", "view-title"), False, False, 0)
        self.pack_start(cabecera, False, False, 0)

        barra = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        anterior = boton("go-previous-symbolic", "")
        anterior.set_tooltip_text("Mes anterior")
        anterior.connect("clicked", lambda *_: self._cambiar_mes(-1))
        barra.pack_start(anterior, False, False, 0)

        self.mes_titulo = etiqueta("", "mes-titulo")
        self.mes_titulo.set_width_chars(20)
        barra.pack_start(self.mes_titulo, False, False, 0)

        siguiente = boton("go-next-symbolic", "")
        siguiente.set_tooltip_text("Mes siguiente")
        siguiente.connect("clicked", lambda *_: self._cambiar_mes(1))
        barra.pack_start(siguiente, False, False, 0)

        hoy_boton = Gtk.Button(label="Hoy")
        hoy_boton.connect("clicked", lambda *_: self._ir_hoy())
        barra.pack_start(hoy_boton, False, False, 0)

        leyenda = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        for texto, color in (
            ("Ingresos", theme.INGRESO),
            ("Gastos", theme.GASTO),
            ("Entregas", theme.ACENTO),
            ("Inicios", theme.ADVERTENCIA),
        ):
            marcador = Gtk.Label()
            marcador.set_markup(f'<span foreground="{color}">●</span> '
                                f'<span foreground="{theme.TEXTO_SUAVE}">{texto}</span>')
            marcador.get_style_context().add_class("leyenda")
            leyenda.pack_start(marcador, False, False, 0)
        barra.pack_end(leyenda, False, False, 0)
        self.pack_start(barra, False, False, 0)

        principal = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)

        marco_cal, caja_cal = marco_con_titulo("Vista mensual")
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(6)
        self.grid.set_column_spacing(6)
        self.grid.set_row_homogeneous(True)
        self.grid.set_column_homogeneous(True)
        self.celdas: list[tuple[Gtk.Button, Gtk.Label, Gtk.Label]] = []
        self._crear_celdas()
        caja_cal.pack_start(self.grid, True, True, 0)
        principal.pack_start(marco_cal, True, True, 0)

        marco_detalle, caja_detalle = marco_con_titulo("Detalle del día")
        marco_detalle.set_size_request(420, -1)
        self.detalle_titulo = etiqueta("", "panel-title")
        caja_detalle.pack_start(self.detalle_titulo, False, False, 0)

        tarjetas = Gtk.Grid()
        tarjetas.set_column_spacing(10)
        tarjetas.set_column_homogeneous(True)
        self.tarjeta_ing, self.valor_ing = tarjeta("Ingresos", "verde")
        self.tarjeta_gas, self.valor_gas = tarjeta("Gastos", "rojo")
        self.tarjeta_neto, self.valor_neto = tarjeta("Neto")
        for i, widget in enumerate((self.tarjeta_ing, self.tarjeta_gas, self.tarjeta_neto)):
            tarjetas.attach(widget, i, 0, 1, 1)
        caja_detalle.pack_start(tarjetas, False, False, 0)

        self.movs_titulo = etiqueta("Movimientos", "panel-title")
        caja_detalle.pack_start(self.movs_titulo, False, False, 0)
        columnas_mov = [
            {"titulo": "Tipo", "indice": 0, "ancho": 75,
             "color": lambda v: theme.INGRESO if v == "Ingreso" else theme.GASTO},
            {"titulo": "Concepto", "indice": 1, "expandir": True},
            {"titulo": "Monto", "indice": 2, "ancho": 115, "tipo": int,
             "formato": formatear_monto,
             "color": lambda v: theme.INGRESO if v >= 0 else theme.GASTO},
        ]
        self.tree_mov, self.modelo_mov = crear_tabla(columnas_mov)
        caja_detalle.pack_start(self._scroll(self.tree_mov), True, True, 0)

        self.proy_titulo = etiqueta("Proyectos", "panel-title")
        caja_detalle.pack_start(self.proy_titulo, False, False, 0)
        columnas_proy = [
            {"titulo": "Proyecto", "indice": 0, "expandir": True},
            {"titulo": "Evento", "indice": 1, "ancho": 80,
             "color": lambda v: theme.ACENTO if v == "Entrega" else theme.ADVERTENCIA},
            {"titulo": "Estado", "indice": 2, "ancho": 100},
        ]
        self.tree_proy, self.modelo_proy = crear_tabla(columnas_proy)
        caja_detalle.pack_start(self._scroll(self.tree_proy), True, True, 0)

        principal.pack_start(marco_detalle, True, True, 0)
        self.pack_start(principal, True, True, 0)

        self.resumen_label = etiqueta("", "muted")
        self.pack_start(self.resumen_label, False, False, 0)

        self.recargar()

    @staticmethod
    def _scroll(tree):
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(tree)
        scroll.set_size_request(-1, 120)
        return scroll

    # ------------------------------------------------------------ navegación

    def _cambiar_mes(self, delta: int):
        self.mes_actual = sumar_meses(self.mes_actual, delta)
        ultimo = calendar.monthrange(self.mes_actual.year, self.mes_actual.month)[1]
        dia = min(self.dia_seleccionado.day, ultimo)
        self.dia_seleccionado = date(self.mes_actual.year, self.mes_actual.month, dia)
        self.recargar()

    def _ir_hoy(self):
        hoy = date.today()
        self.mes_actual = primer_dia_mes(hoy)
        self.dia_seleccionado = hoy
        self.recargar()

    def _dia_clicked(self, boton):
        dia = date.fromisoformat(boton.get_name())
        self.dia_seleccionado = dia
        if (dia.year, dia.month) != (self.mes_actual.year, self.mes_actual.month):
            self.mes_actual = primer_dia_mes(dia)
        self.recargar()

    # --------------------------------------------------------------- dibujo

    def recargar(self):
        inicio = self.mes_actual - timedelta(days=self.mes_actual.weekday())
        fin = inicio + timedelta(days=41)
        desde, hasta = inicio.isoformat(), fin.isoformat()
        self.datos_dia = self.db.resumen_diario(desde, hasta)
        self.hitos = self.db.hitos_proyectos(desde, hasta)

        nombre_mes = MESES_LARGOS[self.mes_actual.month - 1].capitalize()
        self.mes_titulo.set_label(f"{nombre_mes} {self.mes_actual.year}")
        self._actualizar_celdas(inicio)
        self._actualizar_detalle()
        self._actualizar_resumen_mes()

    def _crear_celdas(self):
        """Crea una sola vez los 42 botones del calendario."""
        for columna, nombre in enumerate(DIAS_SEMANA):
            cabecera = etiqueta(nombre, "dia-semana", xalign=0.5)
            self.grid.attach(cabecera, columna, 0, 1, 1)

        for i in range(42):
            boton_dia = Gtk.Button()
            boton_dia.get_style_context().add_class("caldia")
            boton_dia.set_size_request(52, 58)

            caja = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
            numero = Gtk.Label(label="1", xalign=0.0)
            numero.get_style_context().add_class("numero")
            indicadores = Gtk.Label(label=" ", xalign=0.0)
            caja.pack_start(numero, False, False, 0)
            caja.pack_start(indicadores, False, False, 0)
            boton_dia.add(caja)

            boton_dia.connect("clicked", self._dia_clicked)
            self.grid.attach(boton_dia, i % 7, i // 7 + 1, 1, 1)
            self.celdas.append((boton_dia, numero, indicadores))

    def _actualizar_celdas(self, inicio: date):
        """Actualiza las celdas existentes sin destruir ningún widget."""
        hoy = date.today().isoformat()
        seleccionado = self.dia_seleccionado.isoformat()

        for i, (boton, numero, indicadores) in enumerate(self.celdas):
            dia = inicio + timedelta(days=i)
            iso = dia.isoformat()
            mov = self.datos_dia.get(iso, {})
            hitos = self.hitos.get(iso, {})

            numero.set_label(str(dia.day))
            puntos = []
            if mov.get("ingresos"):
                puntos.append(f'<span foreground="{theme.INGRESO}">●</span>')
            if mov.get("gastos"):
                puntos.append(f'<span foreground="{theme.GASTO}">●</span>')
            if hitos.get("entregas"):
                puntos.append(f'<span foreground="{theme.ACENTO}">●</span>')
            if hitos.get("inicios"):
                puntos.append(f'<span foreground="{theme.ADVERTENCIA}">●</span>')
            indicadores.set_markup(" ".join(puntos) if puntos else " ")

            contexto = boton.get_style_context()
            for clase in ("otro-mes", "hoy", "seleccionado"):
                contexto.remove_class(clase)
            if (dia.year, dia.month) != (self.mes_actual.year, self.mes_actual.month):
                contexto.add_class("otro-mes")
            if iso == hoy:
                contexto.add_class("hoy")
            if iso == seleccionado:
                contexto.add_class("seleccionado")

            boton.set_name(iso)
            boton.set_tooltip_text(self._tooltip(dia, mov, hitos))

    @staticmethod
    def _tooltip(dia: date, mov: dict, hitos: dict) -> str:
        lineas = [fecha_legible(dia.isoformat())]
        if mov.get("ingresos"):
            lineas.append(f"Ingresos: {formatear_monto(mov['ingresos'])} ({mov['n_ingresos']})")
        if mov.get("gastos"):
            lineas.append(f"Gastos: {formatear_monto(mov['gastos'])} ({mov['n_gastos']})")
        if hitos.get("entregas"):
            lineas.append("Entregas: " + ", ".join(p["nombre"] for p in hitos["entregas"]))
        if hitos.get("inicios"):
            lineas.append("Inicios: " + ", ".join(p["nombre"] for p in hitos["inicios"]))
        return "\n".join(lineas)

    def _actualizar_detalle(self):
        dia = self.dia_seleccionado
        self.detalle_titulo.set_label(
            f"{DIAS_LARGOS[dia.weekday()].capitalize()}, {dia.day} de "
            f"{MESES_LARGOS[dia.month - 1]} de {dia.year}"
        )

        iso = dia.isoformat()
        movimientos = self.db.listar_movimientos(desde=iso, hasta=iso)
        ingresos = sum(f["monto_cents"] for f in movimientos if f["tipo"] == "Ingreso")
        gastos = sum(f["monto_cents"] for f in movimientos if f["tipo"] == "Gasto")
        self.valor_ing.set_label(formatear_monto(ingresos))
        self.valor_gas.set_label(formatear_monto(gastos))
        self.valor_neto.set_label(formatear_monto(ingresos - gastos))

        self.modelo_mov.clear()
        for fila in movimientos:
            self.modelo_mov.append([
                fila["tipo"], fila["concepto"],
                fila["monto_cents"] if fila["tipo"] == "Ingreso" else -fila["monto_cents"],
            ])
        self.movs_titulo.set_label(f"Movimientos ({len(movimientos)})")

        proyectos = self.db.proyectos_en_fecha(iso)
        self.modelo_proy.clear()
        for fila in proyectos:
            self.modelo_proy.append([fila["nombre"], fila["evento"], fila["estado"]])
        self.proy_titulo.set_label(f"Proyectos ({len(proyectos)})")

    def _actualizar_resumen_mes(self):
        primero = primer_dia_mes(self.mes_actual)
        ultimo_day = calendar.monthrange(self.mes_actual.year, self.mes_actual.month)[1]
        ultimo = date(self.mes_actual.year, self.mes_actual.month, ultimo_day)
        diario = self.db.resumen_diario(primero.isoformat(), ultimo.isoformat())
        hitos = self.db.hitos_proyectos(primero.isoformat(), ultimo.isoformat())
        n_ing = sum(v["n_ingresos"] for v in diario.values())
        n_gas = sum(v["n_gastos"] for v in diario.values())
        entregas = sum(len(v["entregas"]) for v in hitos.values())
        total_ing = sum(v["ingresos"] for v in diario.values())
        total_gas = sum(v["gastos"] for v in diario.values())
        nombre_mes = MESES_LARGOS[self.mes_actual.month - 1].capitalize()
        self.resumen_label.set_label(
            f"{nombre_mes} {self.mes_actual.year}: {n_ing} ingresos "
            f"({formatear_monto(total_ing)})   •   {n_gas} gastos "
            f"({formatear_monto(total_gas)})   •   {entregas} entregas programadas"
        )
