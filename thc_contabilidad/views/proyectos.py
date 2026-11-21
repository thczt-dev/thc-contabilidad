"""Pestaña de proyectos pendientes y su formulario de gestión."""

from __future__ import annotations

from datetime import date

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from .. import theme  # noqa: E402
from ..ui_helpers import (  # noqa: E402
    DateEntry, boton, combo, confirmar, crear_tabla, etiqueta, mostrar_error, texto_combo,
)
from ..utils import (  # noqa: E402
    ESTADOS_PROYECTO, PRIORIDADES, SIN_CONTACTO, a_centros, fecha_legible,
    formatear_monto, hoy_iso,
)

COLOR_ESTADO = {
    "Pendiente": theme.ADVERTENCIA,
    "En curso": theme.ACENTO,
    "Completado": theme.INGRESO,
    "Cancelado": theme.NEUTRO,
}
COLOR_PRIORIDAD = {
    "Alta": theme.GASTO,
    "Media": theme.ADVERTENCIA,
    "Baja": theme.INGRESO,
}


class ProyectoDialog(Gtk.Dialog):
    def __init__(self, parent, db, fila=None):
        super().__init__(
            title="Editar proyecto" if fila else "Nuevo proyecto",
            parent=parent,
            modal=True,
        )
        self.db = db
        self.resultado = None
        self.set_default_size(580, 680)

        area = self.get_content_area()
        area.set_spacing(14)
        area.set_margin_start(24)
        area.set_margin_end(24)
        area.set_margin_top(20)
        area.set_margin_bottom(16)

        rejilla = Gtk.Grid()
        rejilla.set_row_spacing(12)
        rejilla.set_column_spacing(16)

        self.contactos = db.opciones_contactos()
        opciones = list(self.contactos.keys())
        actual = SIN_CONTACTO
        if fila and fila.get("contacto_id"):
            for texto, cid in self.contactos.items():
                if cid == fila["contacto_id"]:
                    actual = texto
                    break

        self.nombre = Gtk.Entry()
        self.nombre.set_placeholder_text("Nombre del proyecto")
        self.cliente = combo(opciones, actual)
        self.descripcion, self.descripcion_vista = self._area_texto(70)
        self.estado = combo(ESTADOS_PROYECTO, fila["estado"] if fila else "Pendiente")
        self.prioridad = combo(PRIORIDADES, fila["prioridad"] if fila else "Media")
        self.inicio = DateEntry(fila["fecha_inicio"] if fila and fila["fecha_inicio"] else hoy_iso())
        self.limite = DateEntry(fila["fecha_limite"] if fila else "")
        self.presupuesto = Gtk.Entry()
        self.presupuesto.set_placeholder_text("Opcional. Ej. 2.500.000")
        self.notas, self.notas_vista = self._area_texto(70)

        if fila:
            self.nombre.set_text(fila["nombre"])
            self.descripcion_vista.get_buffer().set_text(fila["descripcion"] or "")
            self.presupuesto.set_text(str(fila["presupuesto_cents"] / 100))
            self.notas_vista.get_buffer().set_text(fila["notas"] or "")

        campos = [
            ("Nombre:", self.nombre),
            ("Cliente:", self.cliente),
            ("Descripción:", self.descripcion),
            ("Estado:", self.estado),
            ("Prioridad:", self.prioridad),
            ("Fecha de inicio:", self.inicio),
            ("Fecha límite:", self.limite),
            ("Presupuesto ($):", self.presupuesto),
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

    @staticmethod
    def _texto_de(vista):
        buffer = vista.get_buffer()
        return buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False).strip()

    def _al_responder(self, _dialogo, respuesta):
        if respuesta != Gtk.ResponseType.OK:
            return
        try:
            nombre = self.nombre.get_text().strip()
            if not nombre:
                raise ValueError("Escribe el nombre del proyecto.")
            presupuesto_texto = self.presupuesto.get_text().strip()
            datos = {
                "nombre": nombre,
                "contacto_id": self.contactos.get(texto_combo(self.cliente)),
                "descripcion": self._texto_de(self.descripcion_vista),
                "estado": texto_combo(self.estado),
                "prioridad": texto_combo(self.prioridad),
                "fecha_inicio": self.inicio.get_fecha(),
                "fecha_limite": self.limite.get_fecha(),
                "presupuesto_cents": a_centros(presupuesto_texto) if presupuesto_texto else 0,
                "notas": self._texto_de(self.notas_vista),
            }
        except ValueError as exc:
            mostrar_error(self, str(exc))
            self.stop_emission_by_name("response")
            return
        self.resultado = datos


class ProyectosView(Gtk.Box):
    def __init__(self, ventana):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.ventana = ventana
        self.db = ventana.db
        self.set_margin_start(30)
        self.set_margin_end(30)
        self.set_margin_top(26)
        self.set_margin_bottom(24)
        self.pack_start(etiqueta("Proyectos pendientes", "view-title"), False, False, 0)

        filtros = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.buscar = Gtk.Entry()
        self.buscar.set_placeholder_text("Buscar proyecto, cliente o descripción…")
        self.buscar.set_width_chars(34)
        self.buscar.connect("changed", lambda *_: self.recargar())
        filtros.pack_start(self.buscar, True, True, 0)
        self.estado = combo(["Todos", *ESTADOS_PROYECTO])
        self.estado.connect("changed", lambda *_: self.recargar())
        filtros.pack_start(self.estado, False, False, 0)
        self.prioridad = combo(["Todas", *PRIORIDADES])
        self.prioridad.connect("changed", lambda *_: self.recargar())
        filtros.pack_start(self.prioridad, False, False, 0)
        limpiar = Gtk.Button(label="Limpiar")
        limpiar.connect("clicked", self._limpiar)
        filtros.pack_start(limpiar, False, False, 0)
        self.pack_start(filtros, False, False, 0)

        barra = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        nuevo = boton("list-add-symbolic", "Nuevo proyecto", "Crear proyecto (Ctrl+P)")
        nuevo.get_style_context().add_class("suggested-action")
        nuevo.connect("clicked", lambda *_: self.abrir_dialogo())
        editar = boton("document-edit-symbolic", "Editar")
        editar.connect("clicked", lambda *_: self.abrir_dialogo(self._seleccionado()))
        eliminar = boton("edit-delete-symbolic", "Eliminar")
        eliminar.connect("clicked", lambda *_: self._eliminar())
        completar = boton("object-select-symbolic", "Marcar completado")
        completar.connect("clicked", lambda *_: self._completar())
        actualizar = boton("view-refresh-symbolic", "Actualizar")
        actualizar.connect("clicked", lambda *_: self.recargar())
        for widget in (nuevo, editar, eliminar, completar, actualizar):
            barra.pack_start(widget, False, False, 0)
        self.resumen = etiqueta("", "total-label", xalign=1.0)
        barra.pack_end(self.resumen, True, True, 0)
        self.pack_start(barra, False, False, 0)

        def color_limite(valor):
            if valor and valor < date.today().isoformat():
                return theme.GASTO
            return None

        columnas = [
            {"titulo": "Proyecto", "indice": 0, "expandir": True},
            {"titulo": "Cliente", "indice": 1, "ancho": 130},
            {"titulo": "Estado", "indice": 2, "ancho": 110,
             "color": lambda v: COLOR_ESTADO.get(v)},
            {"titulo": "Prioridad", "indice": 3, "ancho": 95,
             "color": lambda v: COLOR_PRIORIDAD.get(v)},
            {"titulo": "Inicio", "indice": 4, "ancho": 100, "formato": fecha_legible},
            {"titulo": "Límite", "indice": 5, "ancho": 100,
             "formato": fecha_legible, "color": color_limite},
            {"titulo": "Presupuesto", "indice": 6, "ancho": 125, "tipo": int,
             "formato": formatear_monto, "orden": 6},
        ]
        # Columna extra oculta con el id.
        self.tree, self.modelo = crear_tabla(columnas, tipos_extra=(int,))
        self.tree.connect("row-activated", self._al_activar)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.tree)
        self.pack_start(scroll, True, True, 0)

        self.recargar()

    def _limpiar(self, *_):
        self.buscar.set_text("")
        self.estado.set_active(0)
        self.prioridad.set_active(0)
        self.recargar()

    def recargar(self):
        filas = self.db.listar_proyectos(
            buscar=self.buscar.get_text().strip(),
            estado=texto_combo(self.estado),
            prioridad=texto_combo(self.prioridad),
        )
        self.modelo.clear()
        for fila in filas:
            self.modelo.append([
                fila["nombre"], fila["cliente"] or "—", fila["estado"], fila["prioridad"],
                fila["fecha_inicio"], fila["fecha_limite"],
                fila["presupuesto_cents"], fila["id"],
            ])
        activos = sum(1 for f in filas if f["estado"] in ("Pendiente", "En curso"))
        presupuesto = sum(f["presupuesto_cents"] for f in filas)
        self.resumen.set_label(
            f"{activos} activos de {len(filas)} proyectos   •   Presupuesto total: "
            f"{formatear_monto(presupuesto)}"
        )

    def _seleccionado(self):
        modelo, iterador = self.tree.get_selection().get_selected()
        if iterador is None:
            return None
        return self.db.obtener("proyectos", modelo.get_value(iterador, 7))

    def _al_activar(self, _tree, _ruta, _columna):
        self.abrir_dialogo(self._seleccionado())

    def abrir_dialogo(self, fila=None):
        dialogo = ProyectoDialog(self.ventana, self.db, fila)
        respuesta = dialogo.run()
        datos = dialogo.resultado
        dialogo.destroy()
        if respuesta == Gtk.ResponseType.OK and datos:
            self.db.guardar_proyecto(datos, fila["id"] if fila else None)
            self.recargar()
            self.ventana.actualizar_resumen()
            self.ventana.set_status(f"Proyecto guardado: {datos['nombre']}")

    def _completar(self):
        fila = self._seleccionado()
        if not fila:
            self.ventana.set_status("Selecciona un proyecto para marcarlo como completado.")
            return
        fila["estado"] = "Completado"
        self.db.guardar_proyecto(fila, fila["id"])
        self.recargar()
        self.ventana.actualizar_resumen()
        self.ventana.set_status(f"Proyecto completado: {fila['nombre']}")

    def _eliminar(self):
        fila = self._seleccionado()
        if not fila:
            self.ventana.set_status("Selecciona un proyecto para eliminar.")
            return
        if confirmar(self.ventana, "Eliminar proyecto", f"¿Eliminar el proyecto '{fila['nombre']}'?"):
            self.db.eliminar_proyecto(fila["id"])
            self.recargar()
            self.ventana.actualizar_resumen()
            self.ventana.set_status("Proyecto eliminado.")
