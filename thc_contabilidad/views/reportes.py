"""Reportes, balance y exportación a CSV."""

from __future__ import annotations

import csv
from datetime import date

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from .. import theme  # noqa: E402
from ..ui_helpers import boton, combo, crear_tabla, etiqueta, marco_con_titulo, mostrar_error, tarjeta, texto_combo  # noqa: E402
from ..utils import (  # noqa: E402
    barra_texto, fecha_legible, formatear_monto, formatear_porcentaje, hoy_iso,
    mes_legible, porcentaje, primer_dia_mes, rango_periodo, sumar_meses,
)

PERIODOS = ("Este mes", "Últimos 3 meses", "Últimos 6 meses", "Este año", "Todo")

COLOR_NETO = lambda v: theme.INGRESO if v >= 0 else theme.GASTO  # noqa: E731


class ReportesView(Gtk.Box):
    def __init__(self, ventana):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.ventana = ventana
        self.db = ventana.db
        self.set_margin_start(30)
        self.set_margin_end(30)
        self.set_margin_top(26)
        self.set_margin_bottom(24)
        self.pack_start(etiqueta("Reportes y balance", "view-title"), False, False, 0)

        controles = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        controles.pack_start(etiqueta("Período:", "muted"), False, False, 0)
        self.periodo = combo(PERIODOS, "Últimos 6 meses")
        self.periodo.connect("changed", lambda *_: self.recargar())
        controles.pack_start(self.periodo, False, False, 0)
        actualizar = boton("view-refresh-symbolic", "Actualizar")
        actualizar.connect("clicked", lambda *_: self.recargar())
        controles.pack_start(actualizar, False, False, 0)
        exportar_mov = boton("document-save-symbolic", "Exportar movimientos (CSV)")
        exportar_mov.connect("clicked", lambda *_: self._exportar("movimientos"))
        controles.pack_start(exportar_mov, False, False, 0)
        exportar_proy = boton("document-save-symbolic", "Exportar proyectos (CSV)")
        exportar_proy.connect("clicked", lambda *_: self._exportar("proyectos"))
        controles.pack_start(exportar_proy, False, False, 0)
        self.pack_start(controles, False, False, 0)

        tarjetas = Gtk.Grid()
        tarjetas.set_column_spacing(16)
        tarjetas.set_column_homogeneous(True)
        self.t_ingresos, self.v_ingresos = tarjeta("Ingresos del período", "verde")
        self.t_gastos, self.v_gastos = tarjeta("Gastos del período", "rojo")
        self.t_balance, self.v_balance = tarjeta("Balance del período")
        self.t_ahorro, self.v_ahorro = tarjeta("Tasa de ahorro", "azul")
        for i, widget in enumerate((self.t_ingresos, self.t_gastos, self.t_balance, self.t_ahorro)):
            tarjetas.attach(widget, i, 0, 1, 1)
        self.pack_start(tarjetas, False, False, 0)

        detalles = Gtk.Grid()
        detalles.set_column_spacing(16)
        detalles.set_column_homogeneous(True)

        marco_mes, caja_mes = marco_con_titulo("Resumen por mes")
        columnas_mes = [
            {"titulo": "Mes", "indice": 0, "ancho": 100},
            {"titulo": "Ingresos", "indice": 1, "ancho": 120, "tipo": int,
             "formato": formatear_monto},
            {"titulo": "Gastos", "indice": 2, "ancho": 120, "tipo": int,
             "formato": formatear_monto},
            {"titulo": "Neto", "indice": 3, "ancho": 120, "tipo": int,
             "formato": formatear_monto, "color": COLOR_NETO},
        ]
        self.tree_mes, self.modelo_mes = crear_tabla(columnas_mes)
        caja_mes.pack_start(self._scroll(self.tree_mes), True, True, 0)

        marco_cat, caja_cat = marco_con_titulo("Distribución por categoría")
        columnas_cat = [
            {"titulo": "Categoría", "indice": 0, "ancho": 150},
            {"titulo": "Tipo", "indice": 1, "ancho": 80,
             "color": lambda v: theme.INGRESO if v == "Ingreso" else theme.GASTO},
            {"titulo": "N.º", "indice": 2, "ancho": 50, "tipo": int},
            {"titulo": "Total", "indice": 3, "ancho": 115, "tipo": int,
             "formato": formatear_monto},
            {"titulo": "Participación", "indice": 4, "expandir": True},
        ]
        self.tree_cat, self.modelo_cat = crear_tabla(columnas_cat)
        caja_cat.pack_start(self._scroll(self.tree_cat), True, True, 0)

        detalles.attach(marco_mes, 0, 0, 1, 1)
        detalles.attach(marco_cat, 1, 0, 1, 1)
        self.pack_start(detalles, True, True, 0)

        self.recargar()

    @staticmethod
    def _scroll(tree):
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(tree)
        return scroll

    def recargar(self):
        desde, hasta = rango_periodo(texto_combo(self.periodo))
        totales = self.db.totales(desde, hasta)
        ingresos, gastos = totales["ingresos"], totales["gastos"]
        balance = ingresos - gastos

        self.v_ingresos.set_label(formatear_monto(ingresos))
        self.v_gastos.set_label(formatear_monto(gastos))
        self.v_balance.set_label(formatear_monto(balance))
        ahorro = porcentaje(balance, ingresos) if ingresos else 0.0
        self.v_ahorro.set_label(formatear_porcentaje(ahorro))

        datos_mes = self.db.por_mes(desde, hasta)
        meses = self._meses_del_rango(desde, hasta, datos_mes)
        self.modelo_mes.clear()
        for mes in meses:
            fila = datos_mes.get(mes, {"ingresos": 0, "gastos": 0})
            neto = fila["ingresos"] - fila["gastos"]
            self.modelo_mes.append([
                mes_legible(mes), fila["ingresos"], fila["gastos"], neto,
            ])

        categorias = self.db.por_categoria(desde, hasta)
        maximo = max((fila["total"] for fila in categorias), default=0)
        self.modelo_cat.clear()
        for fila in categorias:
            fraccion = fila["total"] / maximo if maximo else 0
            self.modelo_cat.append([
                fila["categoria"], fila["tipo"], fila["cantidad"], fila["total"],
                f"{barra_texto(fraccion)}  {formatear_porcentaje(porcentaje(fila['total'], ingresos if fila['tipo'] == 'Ingreso' else gastos))}",
            ])

    @staticmethod
    def _meses_del_rango(desde, hasta, datos):
        if not desde or not hasta:
            return sorted(datos)
        try:
            actual = primer_dia_mes(date.fromisoformat(desde))
            final = primer_dia_mes(date.fromisoformat(hasta))
        except ValueError:
            return sorted(datos)
        resultado = []
        while actual <= final and len(resultado) < 240:
            resultado.append(actual.strftime("%Y-%m"))
            actual = sumar_meses(actual, 1)
        return resultado

    def _exportar(self, clase):
        dialogo = Gtk.FileChooserDialog(
            title=f"Guardar {clase} en CSV",
            parent=self.ventana,
            action=Gtk.FileChooserAction.SAVE,
            buttons=("_Cancelar", Gtk.ResponseType.CANCEL, "_Guardar", Gtk.ResponseType.OK),
        )
        dialogo.set_current_name(f"thc_{clase}_{hoy_iso()}.csv")
        filtro = Gtk.FileFilter()
        filtro.set_name("Archivos CSV (*.csv)")
        filtro.add_pattern("*.csv")
        dialogo.add_filter(filtro)

        respuesta = dialogo.run()
        if respuesta == Gtk.ResponseType.OK:
            ruta = dialogo.get_filename()
            try:
                cantidad = self._escribir_csv(ruta, clase)
                self.ventana.set_status(f"Exportados {cantidad} registros a {ruta}")
            except OSError as exc:
                mostrar_error(self.ventana, str(exc), "No se pudo exportar")
        dialogo.destroy()

    def _escribir_csv(self, ruta, clase) -> int:
        desde, hasta = rango_periodo(texto_combo(self.periodo))
        with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
            escritor = csv.writer(archivo, delimiter=";")
            if clase == "movimientos":
                escritor.writerow([
                    "ID", "Fecha", "Tipo", "Concepto", "Categoría", "Contacto",
                    "Monto COP", "Método de pago", "Notas",
                ])
                filas = self.db.listar_movimientos(desde=desde, hasta=hasta)
                for fila in filas:
                    escritor.writerow([
                        fila["id"], fila["fecha"], fila["tipo"], fila["concepto"],
                        fila["categoria"], fila["contacto"],
                        fila["monto_cents"] / 100, fila["metodo_pago"], fila["notas"],
                    ])
            else:
                escritor.writerow([
                    "ID", "Proyecto", "Cliente", "Descripción", "Estado", "Prioridad",
                    "Fecha inicio", "Fecha límite", "Presupuesto COP", "Notas",
                ])
                filas = self.db.listar_proyectos()
                if desde and hasta:
                    filas = [
                        fila for fila in filas
                        if any(desde <= fecha <= hasta for fecha in (
                            fila["fecha_inicio"] or "", fila["fecha_limite"] or ""
                        ))
                    ]
                for fila in filas:
                    escritor.writerow([
                        fila["id"], fila["nombre"], fila["cliente"], fila["descripcion"],
                        fila["estado"], fila["prioridad"], fila["fecha_inicio"] or "",
                        fila["fecha_limite"] or "", fila["presupuesto_cents"] / 100,
                        fila["notas"],
                    ])
            return len(filas)
