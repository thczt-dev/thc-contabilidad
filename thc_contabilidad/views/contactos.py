"""Directorio de clientes y proveedores."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from .. import theme  # noqa: E402
from ..ui_helpers import (  # noqa: E402
    boton, combo, confirmar, crear_tabla, etiqueta, mostrar_error, texto_combo,
)
from ..utils import TIPOS_CONTACTO  # noqa: E402

COLOR_TIPO = {
    "Cliente": theme.INGRESO,
    "Proveedor": theme.ADVERTENCIA,
    "Ambos": theme.ACENTO,
}


class ContactoDialog(Gtk.Dialog):
    def __init__(self, parent, fila=None):
        super().__init__(
            title="Editar contacto" if fila else "Nuevo contacto",
            parent=parent,
            modal=True,
        )
        self.resultado = None
        self.set_default_size(520, 580)

        area = self.get_content_area()
        area.set_spacing(14)
        area.set_margin_start(24)
        area.set_margin_end(24)
        area.set_margin_top(20)
        area.set_margin_bottom(16)

        rejilla = Gtk.Grid()
        rejilla.set_row_spacing(12)
        rejilla.set_column_spacing(16)

        self.nombre = Gtk.Entry()
        self.nombre.set_placeholder_text("Nombre o razón social")
        self.tipo = combo(TIPOS_CONTACTO, fila["tipo"] if fila else "Cliente")
        self.identificacion = Gtk.Entry()
        self.identificacion.set_placeholder_text("NIT o cédula")
        self.telefono = Gtk.Entry()
        self.telefono.set_placeholder_text("300 123 4567")
        self.email = Gtk.Entry()
        self.email.set_placeholder_text("correo@ejemplo.com")
        self.direccion = Gtk.Entry()
        self.notas, self.notas_vista = self._area_texto(80)

        if fila:
            for campo, widget in (
                ("nombre", self.nombre), ("identificacion", self.identificacion),
                ("telefono", self.telefono), ("email", self.email),
                ("direccion", self.direccion),
            ):
                widget.set_text(fila[campo] or "")
            self.notas_vista.get_buffer().set_text(fila["notas"] or "")

        campos = [
            ("Nombre:", self.nombre),
            ("Tipo:", self.tipo),
            ("Identificación:", self.identificacion),
            ("Teléfono:", self.telefono),
            ("Correo electrónico:", self.email),
            ("Dirección:", self.direccion),
            ("Notas:", self.notas),
        ]
        for numero, (texto, widget) in enumerate(campos):
            rejilla.attach(etiqueta(texto, "field-label"), 0, numero, 1, 1)
            rejilla.attach(widget, 1, numero, 1, 1)
        area.pack_start(rejilla, True, True, 0)

        self.add_button("Cancelar", Gtk.ResponseType.CANCEL)
        guardar = self.add_button("Guardar", Gtk.ResponseType.OK)
        guardar.get_style_context().add_class("suggested-action")
        self.connect("response", self._al_responder)
        self.show_all()
        self.nombre.grab_focus()

    @staticmethod
    def _area_texto(alto):
        vista = Gtk.TextView()
        vista.set_wrap_mode(Gtk.WrapMode.WORD)
        vista.set_size_request(-1, alto)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(vista)
        return scroll, vista

    def _al_responder(self, _dialogo, respuesta):
        if respuesta != Gtk.ResponseType.OK:
            return
        nombre = self.nombre.get_text().strip()
        if not nombre:
            mostrar_error(self, "Escribe el nombre del contacto.")
            self.stop_emission_by_name("response")
            return
        buffer = self.notas_vista.get_buffer()
        self.resultado = {
            "nombre": nombre,
            "tipo": texto_combo(self.tipo),
            "identificacion": self.identificacion.get_text().strip(),
            "telefono": self.telefono.get_text().strip(),
            "email": self.email.get_text().strip(),
            "direccion": self.direccion.get_text().strip(),
            "notas": buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False).strip(),
        }


class ContactosView(Gtk.Box):
    def __init__(self, ventana):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.ventana = ventana
        self.db = ventana.db
        self.set_margin_start(30)
        self.set_margin_end(30)
        self.set_margin_top(26)
        self.set_margin_bottom(24)
        self.pack_start(etiqueta("Clientes y proveedores", "view-title"), False, False, 0)

        filtros = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.buscar = Gtk.Entry()
        self.buscar.set_placeholder_text("Buscar por nombre, NIT o correo…")
        self.buscar.set_width_chars(38)
        self.buscar.connect("changed", lambda *_: self.recargar())
        filtros.pack_start(self.buscar, True, True, 0)
        self.tipo = combo(["Todos", *TIPOS_CONTACTO])
        self.tipo.connect("changed", lambda *_: self.recargar())
        filtros.pack_start(self.tipo, False, False, 0)
        self.pack_start(filtros, False, False, 0)

        barra = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        nuevo = boton("list-add-symbolic", "Nuevo contacto")
        nuevo.get_style_context().add_class("suggested-action")
        nuevo.connect("clicked", lambda *_: self.abrir_dialogo())
        editar = boton("document-edit-symbolic", "Editar")
        editar.connect("clicked", lambda *_: self.abrir_dialogo(self._seleccionado()))
        eliminar = boton("edit-delete-symbolic", "Eliminar")
        eliminar.connect("clicked", lambda *_: self._eliminar())
        actualizar = boton("view-refresh-symbolic", "Actualizar")
        actualizar.connect("clicked", lambda *_: self.recargar())
        for widget in (nuevo, editar, eliminar, actualizar):
            barra.pack_start(widget, False, False, 0)
        self.resumen = etiqueta("", "total-label", xalign=1.0)
        barra.pack_end(self.resumen, True, True, 0)
        self.pack_start(barra, False, False, 0)

        columnas = [
            {"titulo": "Nombre", "indice": 0, "expandir": True},
            {"titulo": "Tipo", "indice": 1, "ancho": 110,
             "color": lambda v: COLOR_TIPO.get(v)},
            {"titulo": "Identificación", "indice": 2, "ancho": 150},
            {"titulo": "Teléfono", "indice": 3, "ancho": 140},
            {"titulo": "Correo", "indice": 4, "ancho": 200},
        ]
        # Columna extra oculta con el id del contacto.
        self.tree, self.modelo = crear_tabla(columnas, tipos_extra=(int,))
        self.tree.connect("row-activated", self._al_activar)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.tree)
        self.pack_start(scroll, True, True, 0)

        self.recargar()

    def recargar(self):
        filas = self.db.listar_contactos(
            buscar=self.buscar.get_text().strip(), tipo=texto_combo(self.tipo),
        )
        self.modelo.clear()
        for fila in filas:
            self.modelo.append([
                fila["nombre"], fila["tipo"], fila["identificacion"],
                fila["telefono"], fila["email"], fila["id"],
            ])
        clientes = sum(1 for f in filas if f["tipo"] in ("Cliente", "Ambos"))
        proveedores = sum(1 for f in filas if f["tipo"] in ("Proveedor", "Ambos"))
        self.resumen.set_label(
            f"{len(filas)} contactos   •   {clientes} clientes   •   {proveedores} proveedores"
        )

    def _seleccionado(self):
        modelo, iterador = self.tree.get_selection().get_selected()
        if iterador is None:
            return None
        return self.db.obtener("contactos", modelo.get_value(iterador, 5))

    def _al_activar(self, _tree, _ruta, _columna):
        self.abrir_dialogo(self._seleccionado())

    def abrir_dialogo(self, fila=None):
        dialogo = ContactoDialog(self.ventana, fila)
        respuesta = dialogo.run()
        datos = dialogo.resultado
        dialogo.destroy()
        if respuesta == Gtk.ResponseType.OK and datos:
            self.db.guardar_contacto(datos, fila["id"] if fila else None)
            self.recargar()
            self.ventana.set_status(f"Contacto guardado: {datos['nombre']}")
            self.ventana.actualizar_combos()

    def _eliminar(self):
        fila = self._seleccionado()
        if not fila:
            self.ventana.set_status("Selecciona un contacto para eliminar.")
            return
        if confirmar(self.ventana, "Eliminar contacto", f"¿Eliminar a '{fila['nombre']}'?"):
            self.db.eliminar_contacto(fila["id"])
            self.recargar()
            self.ventana.set_status("Contacto eliminado.")
            self.ventana.actualizar_combos()
