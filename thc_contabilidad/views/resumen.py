"""Panel principal con indicadores, actividad reciente y gráfico de balance."""

from __future__ import annotations

from datetime import date

import cairo
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from .. import theme  # noqa: E402
from ..ui_helpers import crear_tabla, etiqueta, marco_con_titulo, tarjeta  # noqa: E402
from ..utils import (  # noqa: E402
    formatear_monto, fecha_legible, mes_legible, meses_recientes, primer_dia_mes,
)

COLOR_ESTADO = {
    "Pendiente": theme.ADVERTENCIA,
    "En curso": theme.ACENTO,
    "Completado": theme.INGRESO,
    "Cancelado": theme.NEUTRO,
}

COLOR_INGRESO = (0.494, 0.878, 0.722)   # theme.INGRESO en RGB
COLOR_GASTO = (1.000, 0.604, 0.620)     # theme.GASTO en RGB
COLOR_BASE = (0.090, 0.114, 0.169)      # theme.PANEL
COLOR_SUAVE = (0.576, 0.631, 0.722)     # theme.TEXTO_SUAVE
COLOR_LINEA = (0.145, 0.176, 0.239)     # theme.BORDE


class BalanceChart(Gtk.DrawingArea):
    """Gráfico de barras simple: ingresos vs. gastos en los últimos meses."""

    def __init__(self):
        super().__init__()
        self.datos: list[tuple[str, int, int]] = []
        self.set_size_request(-1, 190)
        self.connect("draw", self._dibujar)

    def set_datos(self, datos: list[tuple[str, int, int]]):
        self.datos = datos
        self.queue_draw()

    def _dibujar(self, _area, cr):
        ancho = self.get_allocated_width()
        alto = self.get_allocated_height()
        cr.set_source_rgb(*COLOR_BASE)
        cr.paint()

        if not self.datos:
            cr.set_source_rgb(*COLOR_SUAVE)
            cr.set_font_size(11)
            cr.move_to(14, alto / 2)
            cr.show_text("Registra movimientos para ver la evolución mensual")
            return

        superior, base, margen = 34, alto - 26, 14
        maximo = max(max(ingresos, gastos) for _, ingresos, gastos in self.datos) or 1
        grupo = (ancho - margen * 2) / len(self.datos)
        ancho_barra = min(18, max(5, grupo * 0.28))

        cr.set_source_rgb(*COLOR_LINEA)
        cr.set_line_width(1)
        cr.move_to(margen, base + 0.5)
        cr.line_to(ancho - margen, base + 0.5)
        cr.stroke()

        for i, (mes, ingresos, gastos) in enumerate(self.datos):
            centro = margen + i * grupo + grupo / 2
            alto_ing = (ingresos / maximo) * (base - superior)
            alto_gas = (gastos / maximo) * (base - superior)

            cr.set_source_rgb(*COLOR_INGRESO)
            cr.rectangle(centro - ancho_barra - 1, base - alto_ing, ancho_barra, alto_ing)
            cr.fill()

            cr.set_source_rgb(*COLOR_GASTO)
            cr.rectangle(centro + 1, base - alto_gas, ancho_barra, alto_gas)
            cr.fill()

            texto = mes_legible(mes).split()[0]
            medidas = cr.text_extents(texto)
            cr.set_source_rgb(*COLOR_SUAVE)
            cr.set_font_size(9)
            cr.move_to(centro - medidas.width / 2 - medidas.x_bearing, alto - 7)
            cr.show_text(texto)

        for x, color, texto in ((margen, COLOR_INGRESO, "Ingresos"),
                                (margen + 92, COLOR_GASTO, "Gastos")):
            cr.set_source_rgb(*color)
            cr.rectangle(x, 11, 10, 10)
            cr.fill()
            cr.set_source_rgb(*COLOR_SUAVE)
            cr.set_font_size(10)
            cr.move_to(x + 15, 20)
            cr.show_text(texto)


class ResumenView(Gtk.Box):
    def __init__(self, ventana):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.ventana = ventana
        self.db = ventana.db
        self.set_margin_start(30)
        self.set_margin_end(30)
        self.set_margin_top(26)
        self.set_margin_bottom(24)

        cabecera = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        cabecera.pack_start(etiqueta("Resumen general", "view-title"), False, False, 0)
        self.actualizado = etiqueta("", "muted", xalign=1.0)
        cabecera.pack_end(self.actualizado, False, False, 0)
        self.pack_start(cabecera, False, False, 0)

        tarjetas = Gtk.Grid()
        tarjetas.set_column_spacing(16)
        tarjetas.set_row_spacing(16)
        tarjetas.set_column_homogeneous(True)
        self.tarjeta_ingresos, self.valor_ingresos = tarjeta("Ingresos del mes", "verde")
        self.tarjeta_gastos, self.valor_gastos = tarjeta("Gastos del mes", "rojo")
        self.tarjeta_balance, self.valor_balance = tarjeta("Balance acumulado")
        self.tarjeta_proyectos, self.valor_proyectos = tarjeta("Proyectos activos", "azul")
        for i, widget in enumerate((self.tarjeta_ingresos, self.tarjeta_gastos,
                                    self.tarjeta_balance, self.tarjeta_proyectos)):
            tarjetas.attach(widget, i % 2, i // 2, 1, 1)
        self.pack_start(tarjetas, False, False, 0)

        detalles = Gtk.Grid()
        detalles.set_column_spacing(16)
        detalles.set_column_homogeneous(True)

        marco_mov, caja_mov = marco_con_titulo("Últimos movimientos")
        self.tree_mov, self.modelo_mov = self._tabla_movimientos()
        caja_mov.pack_start(self._scroll(self.tree_mov), True, True, 0)
        marco_mov.set_size_request(-1, 250)

        marco_proy, caja_proy = marco_con_titulo("Próximos vencimientos")
        self.tree_proy, self.modelo_proy = self._tabla_proyectos()
        caja_proy.pack_start(self._scroll(self.tree_proy), True, True, 0)
        marco_proy.set_size_request(-1, 250)

        detalles.attach(marco_mov, 0, 0, 1, 1)
        detalles.attach(marco_proy, 1, 0, 1, 1)
        self.pack_start(detalles, True, True, 0)

        marco_grafico, caja_grafico = marco_con_titulo("Evolución de los últimos 6 meses")
        self.grafico = BalanceChart()
        caja_grafico.pack_start(self.grafico, False, False, 0)
        self.pack_start(marco_grafico, False, False, 0)

        self.recargar()

    @staticmethod
    def _scroll(tree):
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(tree)
        return scroll

    @staticmethod
    def _tabla_movimientos():
        columnas = [
            {"titulo": "Fecha", "indice": 0, "ancho": 95, "formato": fecha_legible},
            {"titulo": "Concepto", "indice": 1, "expandir": True},
            {"titulo": "Categoría", "indice": 2, "ancho": 120},
            {"titulo": "Monto", "indice": 3, "ancho": 110, "tipo": int,
             "formato": lambda v: formatear_monto(v),
             "color": lambda v: theme.INGRESO if v > 0 else theme.GASTO},
        ]
        tree, modelo = crear_tabla(columnas)
        return tree, modelo

    @staticmethod
    def _tabla_proyectos():
        def color_limite(valor):
            if not valor:
                return None
            if valor < date.today().isoformat():
                return theme.GASTO
            return None

        columnas = [
            {"titulo": "Proyecto", "indice": 0, "expandir": True},
            {"titulo": "Cliente", "indice": 1, "ancho": 110},
            {"titulo": "Límite", "indice": 2, "ancho": 95,
             "formato": fecha_legible, "color": color_limite},
            {"titulo": "Estado", "indice": 3, "ancho": 95,
             "color": lambda v: COLOR_ESTADO.get(v)},
        ]
        tree, modelo = crear_tabla(columnas)
        return tree, modelo

    def recargar(self):
        hoy = date.today()
        desde = primer_dia_mes(hoy).isoformat()
        hasta = hoy.isoformat()

        mes = self.db.totales(desde, hasta)
        total = self.db.totales()
        self.valor_ingresos.set_label(formatear_monto(mes["ingresos"]))
        self.valor_gastos.set_label(formatear_monto(mes["gastos"]))
        self.valor_balance.set_label(formatear_monto(total["ingresos"] - total["gastos"]))
        self.valor_proyectos.set_label(str(self.db.contar_proyectos_pendientes()))
        self.actualizado.set_label(f"Actualizado: {fecha_legible(hoy.isoformat())}")

        self.modelo_mov.clear()
        for fila in self.db.listar_movimientos(limite=7):
            self.modelo_mov.append([
                fila["fecha"], fila["concepto"], fila["categoria"],
                fila["monto_cents"] if fila["tipo"] == "Ingreso" else -fila["monto_cents"],
            ])

        self.modelo_proy.clear()
        for fila in self.db.proximos_proyectos(limite=7):
            self.modelo_proy.append([
                fila["nombre"], fila["cliente"] or "—",
                fila["fecha_limite"], fila["estado"],
            ])

        meses = meses_recientes(6)
        datos_mes = self.db.por_mes(desde=meses[0], hasta=hasta)
        self.grafico.set_datos([
            (mes, datos_mes.get(mes, {}).get("ingresos", 0),
             datos_mes.get(mes, {}).get("gastos", 0))
            for mes in meses
        ])
