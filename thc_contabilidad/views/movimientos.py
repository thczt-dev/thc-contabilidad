"""Pestaña de ingresos y gastos, con formulario de alta/edición."""

from __future__ import annotations

import sqlite3

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from .. import theme  # noqa: E402
from ..ui_helpers import (  # noqa: E402
    DateEntry, boton, combo, confirmar, crear_tabla, etiqueta, mostrar_error, texto_combo,
)
from ..utils import (  # noqa: E402
    CATEGORIAS_GASTO, CATEGORIAS_INGRESO, METODOS_PAGO, SIN_CONTACTO,
    TIPOS_MOVIMIENTO, a_centros, formatear_monto, hoy_iso, validar_fecha,
)


def _color_tipo(valor):
    return theme.INGRESO if valor == "Ingreso" else theme.GASTO


class MovimientoDialog(Gtk.Dialog):
    """Diálogo para crear o editar un movimiento."""

    def __init__(self, parent, db, fila=None):
        super().__init__(
            title="Editar movimiento" if fila else "Nuevo movimiento",
            parent=parent,
            modal=True,
        )
        self.db = db
        self.resultado = None
        self.set_default_size(540, 600)
        self.set_resizable(True)

        area = self.get_content_area()
        area.set_spacing(14)
        area.set_margin_start(24)
        area.set_margin_end(24)
        area.set_margin_top(20)
        area.set_margin_bottom(16)

        rejilla = Gtk.Grid()
        rejilla.set_row_spacing(12)
        rejilla.set_column_spacing(16)

        tipos = list(TIPOS_MOVIMIENTO)
        categorias = list(dict.fromkeys(CATEGORIAS_INGRESO + CATEGORIAS_GASTO))
        if fila and fila["categoria"] and fila["categoria"] not in categorias:
            categorias.insert(0, fila["categoria"])

        self.contactos = db.opciones_contactos()
        opciones_contacto = list(self.contactos.keys())
        contacto_actual = SIN_CONTACTO
        if fila and fila.get("contacto_id"):
            for etiqueta_contacto, cid in self.contactos.items():
                if cid == fila["contacto_id"]:
                    contacto_actual = etiqueta_contacto
                    break

        self.tipo = combo(tipos, fila["tipo"] if fila else "Gasto")
        self.fecha = DateEntry(fila["fecha"] if fila and fila["fecha"] else hoy_iso())
        self.concepto = Gtk.Entry()
        self.concepto.set_placeholder_text("Ej. Pago de servicios, venta a cliente…")
        self.monto = Gtk.Entry()
        self.monto.set_placeholder_text("Ej. 1.250.000")
        self.categoria = combo(categorias, fila["categoria"] if fila else None, editable=True)
        self.contacto = combo(opciones_contacto, contacto_actual)
        self.metodo = combo(METODOS_PAGO, fila["metodo_pago"] if fila else "Transferencia", editable=True)
        self.notas = Gtk.TextView()
        self.notas.set_wrap_mode(Gtk.WrapMode.WORD)
        self.notas.set_size_request(-1, 84)
        scroll_notas = Gtk.ScrolledWindow()
        scroll_notas.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll_notas.add(self.notas)

        if fila:
            self.concepto.set_text(fila["concepto"])
            self.monto.set_text(str(fila["monto_cents"] / 100))
            self.notas.get_buffer().set_text(fila["notas"] or "")

        campos = [
            ("Tipo:", self.tipo),
            ("Fecha:", self.fecha),
            ("Concepto:", self.concepto),
            ("Monto ($):", self.monto),
            ("Categoría:", self.categoria),
            ("Contacto:", self.contacto),
            ("Método de pago:", self.metodo),
            ("Notas:", scroll_notas),
        ]
        for fila_num, (texto, widget) in enumerate(campos):
            rejilla.attach(etiqueta(texto, "field-label"), 0, fila_num, 1, 1)
            rejilla.attach(widget, 1, fila_num, 1, 1)
        area.pack_start(rejilla, True, True, 0)

        self.add_button("Cancelar", Gtk.ResponseType.CANCEL)
        guardar = self.add_button("Guardar", Gtk.ResponseType.OK)
        guardar.get_style_context().add_class("suggested-action")
        self.connect("response", self._al_responder)
        self.show_all()
        self.concepto.grab_focus()

    def _al_responder(self, _dialogo, respuesta):
        if respuesta != Gtk.ResponseType.OK:
            return
        try:
            concepto = self.concepto.get_text().strip()
            if not concepto:
                raise ValueError("Escribe un concepto para el movimiento.")
            monto = a_centros(self.monto.get_text())
            if monto <= 0:
                raise ValueError("El monto debe ser mayor que cero.")
            datos = {
                "fecha": self.fecha.get_fecha(obligatorio=True),
                "tipo": texto_combo(self.tipo),
                "concepto": concepto,
                "monto_cents": monto,
                "categoria": texto_combo(self.categoria) or "General",
                "contacto_id": self.contactos.get(texto_combo(self.contacto)),
                "metodo_pago": texto_combo(self.metodo),
                "notas": self.notas.get_buffer().get_text(
                    self.notas.get_buffer().get_start_iter(),
                    self.notas.get_buffer().get_end_iter(), False,
                ).strip(),
            }
        except ValueError as exc:
            mostrar_error(self, str(exc))
            self.stop_emission_by_name("response")
            return
        self.resultado = datos

    def _leer_resultado(self):
        return self.resultado


class MovimientosView(Gtk.Box):
    def __init__(self, ventana):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.ventana = ventana
        self.db = ventana.db
        self.set_margin_start(30)
        self.set_margin_end(30)
        self.set_margin_top(26)
        self.set_margin_bottom(24)
        self.pack_start(etiqueta("Ingresos y gastos", "view-title"), False, False, 0)

        filtros = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.buscar = Gtk.Entry()
        self.buscar.set_placeholder_text("Buscar concepto, categoría o contacto…")
        self.buscar.set_tooltip_text("Buscar por concepto, categoría, contacto o notas (Ctrl+F)")
        self.buscar.set_width_chars(34)
        self.buscar.connect("changed", lambda *_: self.recargar())
        filtros.pack_start(self.buscar, True, True, 0)

        self.tipo = combo(["Todos", *TIPOS_MOVIMIENTO])
        self.tipo.connect("changed", lambda *_: self.recargar())
        filtros.pack_start(self.tipo, False, False, 0)

        filtros.pack_start(etiqueta("Desde", "muted"), False, False, 0)
        self.desde = DateEntry()
        self.desde.entry.connect("changed", lambda *_: self.recargar())
        filtros.pack_start(self.desde, False, False, 0)

        filtros.pack_start(etiqueta("Hasta", "muted"), False, False, 0)
        self.hasta = DateEntry()
        self.hasta.entry.connect("changed", lambda *_: self.recargar())
        filtros.pack_start(self.hasta, False, False, 0)

        limpiar = Gtk.Button(label="Limpiar")
        limpiar.connect("clicked", self._limpiar)
        filtros.pack_start(limpiar, False, False, 0)
        self.pack_start(filtros, False, False, 0)

        barra = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        nuevo = boton("list-add-symbolic", "Nuevo movimiento", "Agregar ingreso o gasto (Ctrl+N)")
        nuevo.get_style_context().add_class("suggested-action")
        nuevo.connect("clicked", lambda *_: self.abrir_dialogo())
        editar = boton("document-edit-symbolic", "Editar", "Editar movimiento seleccionado")
        editar.connect("clicked", lambda *_: self.abrir_dialogo(self._seleccionado()))
        eliminar = boton("edit-delete-symbolic", "Eliminar", "Eliminar movimiento seleccionado")
        eliminar.connect("clicked", lambda *_: self._eliminar())
        actualizar = boton("view-refresh-symbolic", "Actualizar")
        actualizar.connect("clicked", lambda *_: self.recargar())
        for widget in (nuevo, editar, eliminar, actualizar):
            barra.pack_start(widget, False, False, 0)
        self.resumen = etiqueta("", "total-label", xalign=1.0)
        barra.pack_end(self.resumen, True, True, 0)
        self.pack_start(barra, False, False, 0)

        columnas = [
            {"titulo": "Fecha", "indice": 0, "ancho": 100, "formato": None},
            {"titulo": "Tipo", "indice": 1, "ancho": 85, "color": _color_tipo},
            {"titulo": "Concepto", "indice": 2, "expandir": True},
            {"titulo": "Categoría", "indice": 3, "ancho": 140},
            {"titulo": "Contacto", "indice": 4, "ancho": 130},
            {"titulo": "Monto", "indice": 5, "ancho": 125, "tipo": int,
             "formato": formatear_monto,
             "color": lambda v: theme.INGRESO if v >= 0 else theme.GASTO, "orden": 5},
        ]
        # La fecha se muestra tal cual (ISO) para que ordene correctamente.
        columnas[0]["formato"] = lambda v: v
        # Columna extra oculta con el id (el monto con signo sirve para ordenar).
        self.tree, self.modelo = crear_tabla(columnas, tipos_extra=(int,))
        self.tree.connect("row-activated", self._al_activar)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.tree)
        self.pack_start(scroll, True, True, 0)

        self.recargar()

    def _limpiar(self, *_):
        self.buscar.set_text("")
        self.tipo.set_active(0)
        self.desde.set_text("")
        self.hasta.set_text("")
        self.recargar()

    def _filtros(self):
        def fecha(entry):
            try:
                return validar_fecha(entry.get_text())
            except ValueError:
                return None
        return {
            "buscar": self.buscar.get_text().strip(),
            "tipo": texto_combo(self.tipo),
            "desde": fecha(self.desde),
            "hasta": fecha(self.hasta),
        }

    def recargar(self):
        filas = self.db.listar_movimientos(**self._filtros())
        self.modelo.clear()
        for fila in filas:
            self.modelo.append([
                fila["fecha"], fila["tipo"], fila["concepto"], fila["categoria"],
                fila["contacto"] or "—",
                fila["monto_cents"] if fila["tipo"] == "Ingreso" else -fila["monto_cents"],
                fila["id"],
            ])
        ingresos = sum(f["monto_cents"] for f in filas if f["tipo"] == "Ingreso")
        gastos = sum(f["monto_cents"] for f in filas if f["tipo"] == "Gasto")
        self.resumen.set_label(
            f"{len(filas)} movimientos   •   Ingresos: {formatear_monto(ingresos)}"
            f"   •   Gastos: {formatear_monto(gastos)}"
            f"   •   Neto: {formatear_monto(ingresos - gastos)}"
        )

    def _seleccionado(self):
        modelo, iterador = self.tree.get_selection().get_selected()
        if iterador is None:
            return None
        return self.db.obtener("movimientos", modelo.get_value(iterador, 6))

    def _al_activar(self, _tree, _ruta, _columna):
        self.abrir_dialogo(self._seleccionado())

    def abrir_dialogo(self, fila=None):
        if fila:
            venta_id = self.db.venta_de_movimiento(fila["id"])
            if venta_id:
                mostrar_error(
                    self.ventana,
                    f"Este ingreso lo generó la venta #{venta_id}. Para cambiarlo, "
                    "elimina o vuelve a cobrar esa venta desde Cobros › Ventas.",
                    "Ingreso vinculado a una venta",
                )
                return
        dialogo = MovimientoDialog(self.ventana, self.db, fila)
        respuesta = dialogo.run()
        datos = dialogo.resultado
        dialogo.destroy()
        if respuesta == Gtk.ResponseType.OK and datos:
            try:
                self.db.guardar_movimiento(datos, fila["id"] if fila else None)
            except (ValueError, sqlite3.IntegrityError) as exc:
                mostrar_error(self.ventana, str(exc), "No se pudo guardar")
                return
            self.recargar()
            self.ventana.actualizar_resumen()
            accion = "actualizado" if fila else "registrado"
            self.ventana.set_status(f"Movimiento {accion}: {datos['concepto']}")

    def _eliminar(self):
        fila = self._seleccionado()
        if not fila:
            self.ventana.set_status("Selecciona un movimiento para eliminar.")
            return
        venta_id = self.db.venta_de_movimiento(fila["id"])
        if venta_id:
            mostrar_error(
                self.ventana,
                f"Este ingreso lo generó la venta #{venta_id}. Elimina la venta "
                "desde Cobros › Ventas para quitar también su ingreso.",
                "Ingreso vinculado a una venta",
            )
            return
        if confirmar(
            self.ventana, "Eliminar movimiento",
            f"¿Eliminar '{fila['concepto']}' por {formatear_monto(fila['monto_cents'])}?",
        ):
            try:
                self.db.eliminar_movimiento(fila["id"])
            except (ValueError, sqlite3.IntegrityError) as exc:
                mostrar_error(self.ventana, str(exc), "No se pudo eliminar")
                return
            self.recargar()
            self.ventana.actualizar_resumen()
            self.ventana.set_status("Movimiento eliminado.")
