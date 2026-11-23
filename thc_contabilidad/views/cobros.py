"""Punto de cobro (POS): catálogo editable, carrito, descuentos, impuestos y ventas."""

from __future__ import annotations

import csv

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from .. import theme  # noqa: E402
from ..i18n import tr, tr_etiqueta_precio  # noqa: E402
from ..ui_helpers import (  # noqa: E402
    DateEntry, boton, combo, confirmar, crear_tabla, etiqueta, marco_con_titulo,
    mostrar_error, mostrar_info, texto_combo,
)
from ..utils import (  # noqa: E402
    METODOS_PAGO, SIN_CONTACTO, TIPOS_PRODUCTO, a_centros, calcular_totales,
    formatear_monto, hoy_iso, validar_fecha,
)

TIPOS_DESCUENTO = ("%", "$")
IMPUESTOS_PRESET = ("0", "5", "19")


def _scroll(widget, alto: int = 180) -> Gtk.ScrolledWindow:
    scroll = Gtk.ScrolledWindow()
    scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    scroll.add(widget)
    scroll.set_size_request(-1, alto)
    return scroll


def _pestana(titulo: str, icono: str) -> Gtk.Box:
    """Etiqueta de pestaña con icono y texto traducido."""
    caja = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    caja.pack_start(
        Gtk.Image.new_from_icon_name(icono, Gtk.IconSize.MENU), False, False, 0
    )
    caja.pack_start(etiqueta(titulo, "tab-label"), False, False, 0)
    caja.show_all()
    return caja


class CobrosView(Gtk.Box):
    """Cobra en una sola página y conserva el histórico de ventas."""

    def __init__(self, ventana):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.ventana = ventana
        self.db = ventana.db
        self.set_margin_start(30)
        self.set_margin_end(30)
        self.set_margin_top(26)
        self.set_margin_bottom(24)

        self.contactos = self.db.opciones_contactos()
        self.celdas_productos: list[tuple[Gtk.Widget, dict]] = []
        self.carrito: list[dict] = []
        self.editando_id: int | None = None
        self._actualizando = False

        self.pack_start(etiqueta("Cobros", "view-title"), False, False, 0)
        self.pack_start(
            etiqueta(
                "Edita tu catálogo, cobra en un solo lugar y lleva el registro de cada venta.",
                "muted",
            ),
            False, False, 0,
        )

        self.sub = Gtk.Notebook()
        self._construir_cobrar()
        self._construir_ventas()
        self.pack_start(self.sub, True, True, 0)

        self.recargar()

    # --------------------------------------------------------------- construcción

    def _construir_cobrar(self):
        pagina = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)

        # ------------------------------------------------------------ catálogo
        marco_cat, caja_cat = marco_con_titulo("Catálogo · clic para agregar")

        filtros = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.buscar_producto = Gtk.Entry()
        self.buscar_producto.set_placeholder_text("Buscar producto o servicio…")
        self.buscar_producto.connect("changed", lambda *_: self._filtrar_catalogo())
        filtros.pack_start(self.buscar_producto, True, True, 0)
        self.tipo_catalogo = combo(["Todos", *TIPOS_PRODUCTO])
        self.tipo_catalogo.connect("changed", lambda *_: self._filtrar_catalogo())
        filtros.pack_start(self.tipo_catalogo, False, False, 0)
        nuevo = boton("document-new-symbolic", "Nuevo")
        nuevo.connect("clicked", lambda *_: self._limpiar_producto())
        filtros.pack_start(nuevo, False, False, 0)
        caja_cat.pack_start(filtros, False, False, 0)

        self.flow = Gtk.FlowBox()
        self.flow.set_max_children_per_line(2)
        self.flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flow.set_row_spacing(8)
        self.flow.set_column_spacing(8)
        caja_cat.pack_start(_scroll(self.flow, 210), True, True, 0)
        self.vacio_catalogo = etiqueta(
            "Aún no hay productos. Agrégalos abajo con el botón «Nuevo».", "muted"
        )
        caja_cat.pack_start(self.vacio_catalogo, False, False, 0)

        separador = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        caja_cat.pack_start(separador, False, False, 0)
        caja_cat.pack_start(etiqueta("Editar catálogo", "panel-title"), False, False, 0)

        rejilla = Gtk.Grid()
        rejilla.set_row_spacing(8)
        rejilla.set_column_spacing(10)
        self.prod_nombre = Gtk.Entry()
        self.prod_nombre.set_placeholder_text("Ej. Café americano")
        self.prod_precio = Gtk.Entry()
        self.prod_precio.set_placeholder_text(tr("Precio"))
        self.prod_tipo = combo(TIPOS_PRODUCTO)
        self.prod_categoria = Gtk.Entry()
        self.prod_categoria.set_placeholder_text("Categoría")
        self.prod_activo = Gtk.CheckButton(label="Disponible")
        self.prod_activo.set_active(True)
        self.prod_notas = Gtk.Entry()
        self.prod_notas.set_placeholder_text("Notas (opcional)")
        self.prod_etiqueta = Gtk.Entry()
        self.prod_etiqueta.set_placeholder_text("Ej. Desde, por producto")
        self.prod_destacado = Gtk.CheckButton(label="Recomendado")
        for fila, (a, b) in enumerate((
            (("Nombre:", self.prod_nombre), ("Precio:", self.prod_precio)),
            (("Tipo:", self.prod_tipo), ("Categoría:", self.prod_categoria)),
            (("Estado:", self.prod_activo), ("Notas:", self.prod_notas)),
            (("Etiqueta:", self.prod_etiqueta), ("Destacado:", self.prod_destacado)),
        )):
            rejilla.attach(etiqueta(a[0], "field-label"), 0, fila, 1, 1)
            rejilla.attach(a[1], 1, fila, 1, 1)
            rejilla.attach(etiqueta(b[0], "field-label"), 2, fila, 1, 1)
            rejilla.attach(b[1], 3, fila, 1, 1)
        caja_cat.pack_start(rejilla, False, False, 0)

        botones_cat = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        guardar = boton("document-save-symbolic", "Guardar")
        guardar.get_style_context().add_class("suggested-action")
        guardar.connect("clicked", lambda *_: self._guardar_producto())
        limpiar = boton("document-new-symbolic", "Limpiar")
        limpiar.connect("clicked", lambda *_: self._limpiar_producto())
        borrar = boton("edit-delete-symbolic", "Eliminar")
        borrar.connect("clicked", lambda *_: self._eliminar_producto())
        for widget in (guardar, limpiar, borrar):
            botones_cat.pack_start(widget, False, False, 0)
        caja_cat.pack_start(botones_cat, False, False, 0)
        pagina.pack_start(marco_cat, True, True, 0)

        # -------------------------------------------------------------- carrito
        marco_car, caja_car = marco_con_titulo("Carrito de cobro")

        datos = Gtk.Grid()
        datos.set_row_spacing(8)
        datos.set_column_spacing(12)
        self.fecha_cobro = DateEntry(hoy_iso())
        self.cliente_cobro = combo(list(self.contactos.keys()), SIN_CONTACTO)
        self.metodo_cobro = combo(METODOS_PAGO, "Efectivo", editable=True)
        self.notas_cobro = Gtk.Entry()
        self.notas_cobro.set_placeholder_text("Notas de la venta (opcional)")
        for fila, (a, b) in enumerate((
            (("Fecha:", self.fecha_cobro), ("Cliente:", self.cliente_cobro)),
            (("Método de pago:", self.metodo_cobro), ("Notas:", self.notas_cobro)),
        )):
            datos.attach(etiqueta(a[0], "field-label"), 0, fila, 1, 1)
            datos.attach(a[1], 1, fila, 1, 1)
            datos.attach(etiqueta(b[0], "field-label"), 2, fila, 1, 1)
            datos.attach(b[1], 3, fila, 1, 1)
        caja_car.pack_start(datos, False, False, 0)

        columnas = [
            {"titulo": "Producto / servicio", "indice": 0, "expandir": True},
            {"titulo": "Cant.", "indice": 1, "ancho": 50, "tipo": int},
            {"titulo": "Precio", "indice": 2, "ancho": 100, "tipo": int,
             "formato": formatear_monto},
            {"titulo": "Subtotal", "indice": 3, "ancho": 110, "tipo": int,
             "formato": formatear_monto, "color": lambda v: theme.INGRESO},
        ]
        self.tree_carrito, self.modelo_carrito = crear_tabla(columnas, tipos_extra=(int,))
        self.tree_carrito.get_selection().connect("changed", self._seleccion_carrito)
        caja_car.pack_start(_scroll(self.tree_carrito, 150), True, True, 0)

        controles = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        controles.pack_start(etiqueta("Cantidad", "field-label"), False, False, 0)
        self.cantidad_spin = Gtk.SpinButton(
            adjustment=Gtk.Adjustment(value=1, lower=1, upper=999,
                                      step_increment=1, page_increment=1),
            climb_rate=1, digits=0,
        )
        self.cantidad_spin.set_width_chars(4)
        self.cantidad_spin.connect("value-changed", self._item_modificado)
        controles.pack_start(self.cantidad_spin, False, False, 0)
        quitar = boton("list-remove-symbolic", "Quitar")
        quitar.connect("clicked", lambda *_: self._quitar_item())
        controles.pack_start(quitar, False, False, 0)
        vaciar = Gtk.Button(label="Vaciar")
        vaciar.connect("clicked", lambda *_: self._limpiar_carrito())
        controles.pack_start(vaciar, False, False, 0)
        caja_car.pack_start(controles, False, False, 0)

        # Descuento e impuesto al final del cobro
        extras = Gtk.Grid()
        extras.set_row_spacing(8)
        extras.set_column_spacing(10)
        self.desc_tipo = combo(TIPOS_DESCUENTO)
        self.desc_tipo.set_tooltip_text("Elige si el descuento es un porcentaje o un valor fijo en pesos.")
        self.desc_tipo.connect("changed", lambda *_: self._tipo_descuento_cambiado())
        self.desc_valor = Gtk.Entry()
        self.desc_valor.set_text("0")
        self.desc_valor.set_width_chars(10)
        self.desc_valor.connect("changed", lambda *_: self._actualizar_totales())
        self.desc_ayuda = etiqueta("", "muted")
        self.impuesto_pct = combo(IMPUESTOS_PRESET, activo="0", editable=True)
        self.impuesto_pct.set_tooltip_text(
            "Impuesto sobre la base ya descontada. En Colombia el IVA general es 19 %; "
            "ajusta el valor según tu caso."
        )
        self.impuesto_pct.connect("changed", lambda *_: self._actualizar_totales())
        hijo = self.impuesto_pct.get_child()
        if isinstance(hijo, Gtk.Entry):
            hijo.connect("changed", lambda *_: self._actualizar_totales())
        self.impuesto_ayuda = etiqueta("", "muted")
        extras.attach(etiqueta("Descuento", "field-label"), 0, 0, 1, 1)
        extras.attach(self.desc_tipo, 1, 0, 1, 1)
        extras.attach(self.desc_valor, 2, 0, 1, 1)
        extras.attach(self.desc_ayuda, 3, 0, 1, 1)
        extras.attach(etiqueta("Impuesto", "field-label"), 0, 1, 1, 1)
        extras.attach(self.impuesto_pct, 1, 1, 1, 1)
        extras.attach(etiqueta("%", "muted"), 2, 1, 1, 1)
        extras.attach(self.impuesto_ayuda, 3, 1, 1, 1)
        caja_car.pack_start(extras, False, False, 0)

        totales = Gtk.Grid()
        totales.set_row_spacing(4)
        totales.set_column_spacing(12)
        self.val_sub = etiqueta("—", xalign=1.0)
        self.val_desc = etiqueta("—", "rojo", xalign=1.0)
        self.val_base = etiqueta("—", xalign=1.0)
        self.val_impuesto = etiqueta("—", "azul", xalign=1.0)
        self.val_total = etiqueta("—", "card-value verde", xalign=1.0)
        filas_totales = (
            ("Subtotal:", self.val_sub, "field-label"),
            ("Descuento:", self.val_desc, "field-label"),
            ("Base:", self.val_base, "field-label"),
            ("Impuesto:", self.val_impuesto, "field-label"),
            ("TOTAL A COBRAR:", self.val_total, "total-label"),
        )
        for fila, (texto, valor, clase) in enumerate(filas_totales):
            totales.attach(etiqueta(texto, clase), 0, fila, 1, 1)
            totales.attach(valor, 1, fila, 1, 1)
        caja_car.pack_start(totales, False, False, 0)

        self.cobrar_boton = boton("accessories-calculator-symbolic", "Cobrar")
        self.cobrar_boton.get_style_context().add_class("suggested-action")
        self.cobrar_boton.connect("clicked", lambda *_: self._cobrar())
        caja_car.pack_start(self.cobrar_boton, False, False, 0)

        pagina.pack_start(marco_car, True, True, 0)
        self.sub.append_page(
            pagina, _pestana("Cobrar", "accessories-calculator-symbolic")
        )

    def _construir_ventas(self):
        pagina = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)

        filtros = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.buscar_venta = Gtk.Entry()
        self.buscar_venta.set_placeholder_text("Buscar cliente, número o nota…")
        self.buscar_venta.connect("changed", lambda *_: self._recargar_ventas())
        filtros.pack_start(self.buscar_venta, True, True, 0)
        filtros.pack_start(etiqueta("Desde", "muted"), False, False, 0)
        self.venta_desde = DateEntry()
        self.venta_desde.entry.connect("changed", lambda *_: self._recargar_ventas())
        filtros.pack_start(self.venta_desde, False, False, 0)
        filtros.pack_start(etiqueta("Hasta", "muted"), False, False, 0)
        self.venta_hasta = DateEntry()
        self.venta_hasta.entry.connect("changed", lambda *_: self._recargar_ventas())
        filtros.pack_start(self.venta_hasta, False, False, 0)
        pagina.pack_start(filtros, False, False, 0)

        barra = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        detalle = boton("document-properties-symbolic", "Ver detalle")
        detalle.connect("clicked", lambda *_: self._detalle_venta())
        eliminar = boton("edit-delete-symbolic", "Eliminar venta")
        eliminar.connect("clicked", lambda *_: self._eliminar_venta())
        exportar = boton("document-save-symbolic", "Exportar CSV")
        exportar.connect("clicked", lambda *_: self._exportar_ventas())
        actualizar = boton("view-refresh-symbolic", "Actualizar")
        actualizar.connect("clicked", lambda *_: self._recargar_ventas())
        for widget in (detalle, eliminar, exportar, actualizar):
            barra.pack_start(widget, False, False, 0)
        self.resumen_ventas_label = etiqueta("", "total-label", xalign=1.0)
        barra.pack_end(self.resumen_ventas_label, True, True, 0)
        pagina.pack_start(barra, False, False, 0)

        columnas = [
            {"titulo": "Fecha", "indice": 0, "ancho": 100},
            {"titulo": "Cliente", "indice": 1, "ancho": 150},
            {"titulo": "Items", "indice": 2, "ancho": 55, "tipo": int},
            {"titulo": "Subtotal", "indice": 3, "ancho": 105, "tipo": int,
             "formato": formatear_monto},
            {"titulo": "Descuento", "indice": 4, "ancho": 105, "tipo": int,
             "formato": formatear_monto, "color": lambda v: theme.GASTO if v else None},
            {"titulo": "Impuesto", "indice": 5, "ancho": 100, "tipo": int,
             "formato": formatear_monto, "color": lambda v: theme.ACENTO if v else None},
            {"titulo": "Total", "indice": 6, "ancho": 115, "tipo": int,
             "formato": formatear_monto, "color": lambda v: theme.INGRESO},
            {"titulo": "Método", "indice": 7, "ancho": 100},
        ]
        self.tree_ventas, self.modelo_ventas = crear_tabla(columnas, tipos_extra=(int,))
        self.tree_ventas.connect("row-activated", lambda *_: self._detalle_venta())
        pagina.pack_start(_scroll(self.tree_ventas, 320), True, True, 0)
        self.sub.append_page(
            pagina, _pestana("Ventas", "x-office-spreadsheet-symbolic")
        )

    # ------------------------------------------------------------------ recarga

    def recargar(self):
        self.contactos = self.db.opciones_contactos()
        opciones = list(self.contactos.keys())
        self.cliente_cobro.get_model().clear()
        for opcion in opciones:
            self.cliente_cobro.append_text(opcion)
        self.cliente_cobro.set_active(0)
        self._recargar_catalogo()
        self._recargar_ventas()
        self._actualizar_carrito()

    def _recargar_catalogo(self):
        for hijo in self.flow.get_children():
            self.flow.remove(hijo)
        self.celdas_productos.clear()

        for producto in self.db.listar_productos(solo_activos=True):
            marco = Gtk.Frame()
            marco.get_style_context().add_class("producto-card")
            if producto["tipo"] == "Paquete":
                marco.get_style_context().add_class("paquete-card")
            caja = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            caja.set_border_width(2)

            agregar = Gtk.Button()
            agregar.set_relief(Gtk.ReliefStyle.NONE)
            descripcion = (producto.get("notas") or "").strip()
            if descripcion:
                agregar.set_tooltip_text(descripcion)
            info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            nombre = etiqueta(producto["nombre"], "producto-nombre")
            nombre.set_line_wrap(True)
            texto_precio = " ".join(
                parte for parte in (
                    tr_etiqueta_precio((producto.get("precio_etiqueta") or "").strip()),
                    formatear_monto(producto["precio_cents"]),
                ) if parte
            )
            precio = etiqueta(texto_precio, "producto-precio")
            categoria = (producto.get("categoria") or "").strip()
            texto_tipo = (
                f"{producto['tipo']} · {categoria}" if categoria else producto["tipo"]
            )
            tipo = etiqueta(texto_tipo, "producto-tipo")
            for widget in (nombre, precio, tipo):
                info.pack_start(widget, False, False, 0)
            if producto.get("destacado"):
                info.pack_start(etiqueta("★ Recomendado", "recomendado-badge"),
                                False, False, 0)
            agregar.add(info)
            agregar.connect("clicked", self._agregar_producto, producto)

            editar = Gtk.Button.new_from_icon_name("document-edit-symbolic", Gtk.IconSize.BUTTON)
            editar.set_tooltip_text("Editar este producto")
            editar.connect("clicked", lambda *_p, p=producto: self._editar_producto(p))
            borrar = Gtk.Button.new_from_icon_name("edit-delete-symbolic", Gtk.IconSize.BUTTON)
            borrar.set_tooltip_text("Eliminar este producto")
            borrar.connect("clicked", lambda *_p, p=producto: self._eliminar_producto(
                p["id"], p["nombre"]
            ))

            caja.pack_start(agregar, True, True, 0)
            caja.pack_start(editar, False, False, 0)
            caja.pack_start(borrar, False, False, 0)
            marco.add(caja)
            self.flow.add(marco)
            # El catálogo se reconstruye cada vez que se entra a Cobros, es
            # decir, después de que la ventana ya fue mostrada. En GTK3 los
            # widgets nuevos no se muestran solos: sin esto las tarjetas quedan
            # invisibles (y no se puede hacer clic en ellas).
            marco.show_all()
            self.celdas_productos.append((marco, producto))

        self.vacio_catalogo.set_visible(not self.celdas_productos)
        self._filtrar_catalogo()

    def _filtrar_catalogo(self):
        texto = self.buscar_producto.get_text().strip().lower()
        tipo = texto_combo(self.tipo_catalogo)
        for marco, producto in self.celdas_productos:
            coincide = (not texto or texto in producto["nombre"].lower()
                        or texto in (producto["categoria"] or "").lower()
                        or texto in (producto.get("notas") or "").lower())
            coincide = coincide and (tipo == "Todos" or producto["tipo"] == tipo)
            marco.set_visible(coincide)

    def _recargar_ventas(self):
        desde = self._fecha(self.venta_desde)
        hasta = self._fecha(self.venta_hasta)
        filas = self.db.listar_ventas(
            buscar=self.buscar_venta.get_text().strip(), desde=desde, hasta=hasta,
        )
        self.modelo_ventas.clear()
        for fila in filas:
            self.modelo_ventas.append([
                fila["fecha"], fila["contacto"] or "—", fila["n_items"],
                fila["subtotal_cents"], fila["descuento_cents"],
                fila["impuesto_cents"], fila["total_cents"],
                fila["metodo_pago"], fila["id"],
            ])
        resumen = self.db.resumen_ventas(desde, hasta)
        self.resumen_ventas_label.set_label(
            f"{resumen['n']} ventas  •  Bruto: {formatear_monto(resumen['subtotal'])}"
            f"  •  -Desc: {formatear_monto(resumen['descuento'])}"
            f"  •  +Imp: {formatear_monto(resumen['impuesto'])}"
            f"  •  Recibido: {formatear_monto(resumen['total'])}"
        )

    @staticmethod
    def _fecha(entry: DateEntry):
        try:
            return validar_fecha(entry.get_text())
        except ValueError:
            return None

    # -------------------------------------------------------------- conversiones

    @staticmethod
    def _centavos(texto: str) -> int:
        valor = (texto or "").strip()
        if not valor:
            return 0
        limpio = valor.replace("$", "").replace(" ", "").replace(".", "").replace(",", "")
        if limpio and set(limpio) == {"0"}:
            return 0
        return a_centros(valor)

    @staticmethod
    def _pct(texto: str) -> float:
        valor = (texto or "").strip().replace(",", ".")
        if not valor:
            return 0.0
        try:
            pct = float(valor)
        except ValueError as exc:
            raise ValueError("Escribe un porcentaje válido.") from exc
        if pct < 0 or pct > 100:
            raise ValueError("El porcentaje debe estar entre 0 y 100.")
        return pct

    def _tipo_descuento(self) -> str:
        return texto_combo(self.desc_tipo) or "%"

    def _valor_descuento(self, tipo: str | None = None):
        tipo = tipo or self._tipo_descuento()
        if tipo == "%":
            return self._pct(self.desc_valor.get_text())
        return self._centavos(self.desc_valor.get_text())

    def _tipo_descuento_cambiado(self):
        texto = texto_combo(self.desc_tipo) or "%"
        self.desc_valor.set_placeholder_text(
            "Ej. 10" if texto == "%" else "Ej. 5000"
        )
        self._actualizar_totales()

    # ------------------------------------------------------------------ catálogo

    def _guardar_producto(self):
        try:
            nombre = self.prod_nombre.get_text().strip()
            if not nombre:
                raise ValueError("Escribe el nombre del producto o servicio.")
            datos = {
                "nombre": nombre,
                "tipo": texto_combo(self.prod_tipo) or "Producto",
                "precio_cents": self._centavos(self.prod_precio.get_text()),
                "categoria": self.prod_categoria.get_text().strip(),
                "precio_etiqueta": self.prod_etiqueta.get_text().strip(),
                "activo": 1 if self.prod_activo.get_active() else 0,
                "destacado": 1 if self.prod_destacado.get_active() else 0,
                "notas": self.prod_notas.get_text().strip(),
            }
        except ValueError as exc:
            mostrar_error(self.ventana, str(exc), "No se pudo guardar")
            return

        self.db.guardar_producto(datos, self.editando_id)
        accion = "actualizado" if self.editando_id else "creado"
        self._limpiar_producto()
        self._recargar_catalogo()
        self.ventana.set_status(f"Producto {accion}: {nombre}")

    def _editar_producto(self, producto: dict):
        self.editando_id = producto["id"]
        self.prod_nombre.set_text(producto["nombre"])
        tipo = producto["tipo"]
        self.prod_tipo.set_active(TIPOS_PRODUCTO.index(tipo) if tipo in TIPOS_PRODUCTO else 0)
        self.prod_precio.set_text(formatear_monto(producto["precio_cents"], simbolo=False))
        self.prod_categoria.set_text(producto["categoria"] or "")
        self.prod_etiqueta.set_text(producto.get("precio_etiqueta") or "")
        self.prod_activo.set_active(bool(producto["activo"]))
        self.prod_destacado.set_active(bool(producto.get("destacado")))
        self.prod_notas.set_text(producto["notas"] or "")
        self.ventana.set_status(f"Editando: {producto['nombre']}")

    def _limpiar_producto(self):
        self.editando_id = None
        self.prod_nombre.set_text("")
        self.prod_tipo.set_active(0)
        self.prod_precio.set_text("")
        self.prod_categoria.set_text("")
        self.prod_etiqueta.set_text("")
        self.prod_activo.set_active(True)
        self.prod_destacado.set_active(False)
        self.prod_notas.set_text("")

    def _eliminar_producto(self, id_producto=None, nombre=None):
        id_producto = id_producto if id_producto is not None else self.editando_id
        if id_producto is None:
            self.ventana.set_status("Selecciona un producto para eliminarlo.")
            return
        fila = self.db.obtener("productos", id_producto)
        nombre = nombre or (fila["nombre"] if fila else "este producto")
        if confirmar(
            self.ventana, "Eliminar producto",
            f"¿Eliminar '{nombre}' del catálogo? Las ventas ya registradas no cambian.",
        ):
            self.db.eliminar_producto(id_producto)
            self._limpiar_producto()
            self._recargar_catalogo()
            self.ventana.set_status("Producto eliminado del catálogo.")

    # ------------------------------------------------------------------- carrito

    def _agregar_producto(self, _boton, producto: dict):
        for item in self.carrito:
            if item["producto_id"] == producto["id"]:
                item["cantidad"] += 1
                self._actualizar_carrito()
                self.ventana.set_status(f"Agregado: {producto['nombre']} (x{item['cantidad']})")
                return
        self.carrito.append({
            "producto_id": producto["id"],
            "nombre": producto["nombre"],
            "tipo": producto["tipo"],
            "precio_cents": producto["precio_cents"],
            "cantidad": 1,
        })
        self._actualizar_carrito()
        self.ventana.set_status(f"Agregado al carrito: {producto['nombre']}")

    def _indice_carrito(self):
        modelo, iterador = self.tree_carrito.get_selection().get_selected()
        return modelo.get_value(iterador, 4) if iterador else None

    def _seleccion_carrito(self, seleccion):
        if self._actualizando:
            return
        modelo, iterador = seleccion.get_selected()
        if iterador is None:
            return
        indice = modelo.get_value(iterador, 4)
        if indice >= len(self.carrito):
            return
        self._actualizando = True
        self.cantidad_spin.set_value(self.carrito[indice]["cantidad"])
        self._actualizando = False

    def _item_modificado(self, _widget):
        if self._actualizando:
            return
        indice = self._indice_carrito()
        if indice is None or indice >= len(self.carrito):
            return
        self.carrito[indice]["cantidad"] = int(self.cantidad_spin.get_value())
        self._actualizar_carrito(mantener=indice)

    def _quitar_item(self):
        indice = self._indice_carrito()
        if indice is None:
            self.ventana.set_status("Selecciona un item del carrito para quitarlo.")
            return
        nombre = self.carrito[indice]["nombre"]
        self.carrito.pop(indice)
        self._actualizar_carrito()
        self.ventana.set_status(f"Quitado del carrito: {nombre}")

    def _limpiar_carrito(self):
        self.carrito.clear()
        self._actualizar_carrito()

    def _actualizar_carrito(self, mantener: int | None = None):
        self._actualizando = True
        self.modelo_carrito.clear()
        for indice, item in enumerate(self.carrito):
            bruto = item["precio_cents"] * item["cantidad"]
            self.modelo_carrito.append([
                item["nombre"], item["cantidad"], item["precio_cents"], bruto, indice,
            ])
        self.cobrar_boton.set_sensitive(bool(self.carrito))
        if mantener is not None and mantener < len(self.carrito):
            self.tree_carrito.get_selection().select_path(Gtk.TreePath(mantener))
        self._actualizando = False
        self._actualizar_totales()

    def _actualizar_totales(self):
        bruto = sum(i["precio_cents"] * i["cantidad"] for i in self.carrito)
        try:
            calculo = calcular_totales(
                self.carrito,
                descuento_tipo=self._tipo_descuento(),
                descuento_valor=self._valor_descuento(),
                impuesto_pct=self._pct(texto_combo(self.impuesto_pct)),
            )
            self.desc_ayuda.set_label("=" + formatear_monto(calculo["descuento"]))
            self.impuesto_ayuda.set_label("=" + formatear_monto(calculo["impuesto"]))
        except ValueError as exc:
            calculo = {"subtotal": bruto, "descuento": 0, "base": bruto,
                       "impuesto": 0, "total": bruto}
            self.desc_ayuda.set_label(str(exc))
            self.impuesto_ayuda.set_label("")

        self.val_sub.set_label(formatear_monto(calculo["subtotal"]))
        self.val_desc.set_label("-" + formatear_monto(calculo["descuento"]))
        self.val_base.set_label(formatear_monto(calculo["base"]))
        self.val_impuesto.set_label("+" + formatear_monto(calculo["impuesto"]))
        self.val_total.set_label(formatear_monto(calculo["total"]))

    def _cobrar(self):
        try:
            fecha = self.fecha_cobro.get_fecha(obligatorio=True)
            datos = {
                "fecha": fecha,
                "contacto_id": self.contactos.get(texto_combo(self.cliente_cobro)),
                "metodo_pago": texto_combo(self.metodo_cobro) or "Efectivo",
                "notas": self.notas_cobro.get_text().strip(),
                "items": [dict(item) for item in self.carrito],
                "descuento_tipo": self._tipo_descuento(),
                "descuento_valor": self._valor_descuento(),
                "impuesto_pct": self._pct(texto_combo(self.impuesto_pct)),
            }
            venta_id = self.db.registrar_venta(datos)
        except ValueError as exc:
            mostrar_error(self.ventana, str(exc), "No se pudo cobrar")
            return

        venta = self.db.obtener_venta(venta_id)
        mensaje = (
            f"Venta #{venta_id} registrada.\n\n"
            f"Subtotal: {formatear_monto(venta['subtotal_cents'])}\n"
            f"Descuento: -{formatear_monto(venta['descuento_cents'])}\n"
            f"Impuesto: +{formatear_monto(venta['impuesto_cents'])}\n"
            f"Total cobrado: {formatear_monto(venta['total_cents'])}\n\n"
            "Se registró como ingreso en Resumen, Movimientos, Calendario y Reportes."
        )
        mostrar_info(self.ventana, mensaje, "Cobro realizado")
        self._limpiar_carrito()
        self.desc_valor.set_text("0")
        self.notas_cobro.set_text("")
        self._recargar_ventas()
        self.ventana.actualizar_resumen()
        self.ventana.set_status(
            f"Cobro #{venta_id} registrado por {formatear_monto(venta['total_cents'])}"
        )

    # -------------------------------------------------------------------- ventas

    def _venta_seleccionada(self):
        modelo, iterador = self.tree_ventas.get_selection().get_selected()
        if iterador is None:
            return None
        return self.db.obtener_venta(modelo.get_value(iterador, 8))

    def _detalle_venta(self):
        venta = self._venta_seleccionada()
        if not venta:
            self.ventana.set_status("Selecciona una venta para ver el detalle.")
            return

        dialogo = Gtk.Dialog(
            title=f"Detalle de la venta #{venta['id']}",
            parent=self.ventana, modal=True,
        )
        dialogo.set_default_size(640, 440)
        area = dialogo.get_content_area()
        area.set_spacing(12)
        area.set_margin_start(20)
        area.set_margin_end(20)
        area.set_margin_top(16)
        area.set_margin_bottom(12)

        area.pack_start(etiqueta(
            f"{venta['fecha']}   ·   {venta['metodo_pago']}", "panel-title"
        ), False, False, 0)

        columnas = [
            {"titulo": "Producto / servicio", "indice": 0, "expandir": True},
            {"titulo": "Cant.", "indice": 1, "ancho": 55, "tipo": int},
            {"titulo": "Precio", "indice": 2, "ancho": 105, "tipo": int,
             "formato": formatear_monto},
            {"titulo": "Subtotal", "indice": 3, "ancho": 115, "tipo": int,
             "formato": formatear_monto, "color": lambda v: theme.INGRESO},
        ]
        tree, modelo = crear_tabla(columnas, tipos_extra=(int,))
        for item in venta["items"]:
            modelo.append([
                item["nombre"], item["cantidad"], item["precio_cents"],
                item["precio_cents"] * item["cantidad"],
            ])
        area.pack_start(_scroll(tree, 200), True, True, 0)

        resumen = Gtk.Grid()
        resumen.set_row_spacing(4)
        resumen.set_column_spacing(12)
        lineas = (
            ("Subtotal:", formatear_monto(venta["subtotal_cents"]), "field-label"),
            ("Descuento:", "-" + formatear_monto(venta["descuento_cents"]), "field-label"),
            ("Base:", formatear_monto(venta["base_cents"]), "field-label"),
            ("Impuesto:", "+" + formatear_monto(venta["impuesto_cents"]), "field-label"),
            ("Total cobrado:", formatear_monto(venta["total_cents"]), "total-label"),
        )
        for fila, (texto, valor, clase) in enumerate(lineas):
            resumen.attach(etiqueta(texto, clase), 0, fila, 1, 1)
            resumen.attach(etiqueta(valor, clase, xalign=1.0), 1, fila, 1, 1)
        area.pack_start(resumen, False, False, 0)
        if venta["notas"]:
            area.pack_start(etiqueta(f"Notas: {venta['notas']}", "muted"), False, False, 0)
        dialogo.add_button("Cerrar", Gtk.ResponseType.CLOSE)
        dialogo.run()
        dialogo.destroy()

    def _eliminar_venta(self):
        venta = self._venta_seleccionada()
        if not venta:
            self.ventana.set_status("Selecciona una venta para eliminarla.")
            return
        if confirmar(
            self.ventana, "Eliminar venta",
            f"¿Eliminar la venta #{venta['id']} por {formatear_monto(venta['total_cents'])}? "
            "También se quitará el ingreso asociado del balance.",
        ):
            self.db.eliminar_venta(venta["id"])
            self._recargar_ventas()
            self.ventana.actualizar_resumen()
            self.ventana.set_status("Venta eliminada y balance actualizado.")

    def _exportar_ventas(self):
        dialogo = Gtk.FileChooserDialog(
            title="Guardar ventas en CSV",
            parent=self.ventana,
            action=Gtk.FileChooserAction.SAVE,
            buttons=("_Cancelar", Gtk.ResponseType.CANCEL, "_Guardar", Gtk.ResponseType.OK),
        )
        dialogo.set_current_name(f"thc_ventas_{hoy_iso()}.csv")
        filtro = Gtk.FileFilter()
        filtro.set_name("Archivos CSV (*.csv)")
        filtro.add_pattern("*.csv")
        dialogo.add_filter(filtro)
        respuesta = dialogo.run()
        if respuesta == Gtk.ResponseType.OK:
            ruta = dialogo.get_filename()
            try:
                self._escribir_csv(ruta)
                self.ventana.set_status(f"Ventas exportadas a {ruta}")
            except OSError as exc:
                mostrar_error(self.ventana, str(exc), "No se pudo exportar")
        dialogo.destroy()

    def _escribir_csv(self, ruta: str) -> int:
        filas = self.db.listar_ventas(
            buscar=self.buscar_venta.get_text().strip(),
            desde=self._fecha(self.venta_desde),
            hasta=self._fecha(self.venta_hasta),
        )
        with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
            escritor = csv.writer(archivo, delimiter=";")
            escritor.writerow([
                "ID", "Fecha", "Cliente", "Items", "Subtotal COP", "Descuento COP",
                "Base COP", "Impuesto COP", "Total COP", "Método de pago", "Notas",
            ])
            for fila in filas:
                escritor.writerow([
                    fila["id"], fila["fecha"], fila["contacto"] or "", fila["n_items"],
                    fila["subtotal_cents"] / 100, fila["descuento_cents"] / 100,
                    fila["base_cents"] / 100, fila["impuesto_cents"] / 100,
                    fila["total_cents"] / 100, fila["metodo_pago"], fila["notas"],
                ])
        return len(filas)
