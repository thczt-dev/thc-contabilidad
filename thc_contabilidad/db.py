"""Capa de persistencia SQLite de THC Contabilidad."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager

from .catalogo_inicial import entries as catalogo_inicial
from .utils import calcular_totales, formatear_monto

ESQUEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS contactos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT NOT NULL,
    tipo            TEXT NOT NULL DEFAULT 'Cliente',
    identificacion  TEXT NOT NULL DEFAULT '',
    telefono        TEXT NOT NULL DEFAULT '',
    email           TEXT NOT NULL DEFAULT '',
    direccion       TEXT NOT NULL DEFAULT '',
    notas           TEXT NOT NULL DEFAULT '',
    creado_en       TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS movimientos (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha         TEXT NOT NULL,
    tipo          TEXT NOT NULL CHECK (tipo IN ('Ingreso', 'Gasto')),
    concepto      TEXT NOT NULL,
    monto_cents   INTEGER NOT NULL CHECK (monto_cents > 0),
    categoria     TEXT NOT NULL DEFAULT 'General',
    contacto_id   INTEGER REFERENCES contactos(id) ON DELETE SET NULL,
    metodo_pago   TEXT NOT NULL DEFAULT '',
    notas         TEXT NOT NULL DEFAULT '',
    creado_en     TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS proyectos (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre            TEXT NOT NULL,
    contacto_id       INTEGER REFERENCES contactos(id) ON DELETE SET NULL,
    descripcion       TEXT NOT NULL DEFAULT '',
    estado            TEXT NOT NULL DEFAULT 'Pendiente',
    prioridad         TEXT NOT NULL DEFAULT 'Media',
    fecha_inicio      TEXT,
    fecha_limite      TEXT,
    presupuesto_cents INTEGER NOT NULL DEFAULT 0,
    notas             TEXT NOT NULL DEFAULT '',
    creado_en         TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS productos (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre        TEXT NOT NULL,
    tipo          TEXT NOT NULL DEFAULT 'Producto' CHECK (tipo IN ('Producto', 'Servicio', 'Paquete')),
    precio_cents  INTEGER NOT NULL DEFAULT 0 CHECK (precio_cents >= 0),
    categoria     TEXT NOT NULL DEFAULT '',
    precio_etiqueta TEXT NOT NULL DEFAULT '',
    activo        INTEGER NOT NULL DEFAULT 1,
    destacado     INTEGER NOT NULL DEFAULT 0 CHECK (destacado IN (0, 1)),
    notas         TEXT NOT NULL DEFAULT '',
    creado_en     TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS ventas (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha            TEXT NOT NULL,
    contacto_id      INTEGER REFERENCES contactos(id) ON DELETE SET NULL,
    metodo_pago      TEXT NOT NULL DEFAULT 'Efectivo',
    subtotal_cents   INTEGER NOT NULL DEFAULT 0,
    descuento_tipo   TEXT NOT NULL DEFAULT '%' CHECK (descuento_tipo IN ('%', 'Fijo')),
    descuento_valor  REAL NOT NULL DEFAULT 0,
    descuento_cents  INTEGER NOT NULL DEFAULT 0,
    base_cents       INTEGER NOT NULL DEFAULT 0,
    impuesto_pct     REAL NOT NULL DEFAULT 0,
    impuesto_cents   INTEGER NOT NULL DEFAULT 0,
    total_cents      INTEGER NOT NULL DEFAULT 0,
    movimiento_id    INTEGER REFERENCES movimientos(id) ON DELETE SET NULL,
    notas            TEXT NOT NULL DEFAULT '',
    creado_en        TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS venta_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id        INTEGER NOT NULL REFERENCES ventas(id) ON DELETE CASCADE,
    producto_id     INTEGER REFERENCES productos(id) ON DELETE SET NULL,
    nombre          TEXT NOT NULL,
    tipo            TEXT NOT NULL DEFAULT 'Producto',
    cantidad        INTEGER NOT NULL DEFAULT 1,
    precio_cents    INTEGER NOT NULL,
    descuento_pct   INTEGER NOT NULL DEFAULT 0,
    descuento_cents INTEGER NOT NULL DEFAULT 0,
    total_cents     INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_movimientos_fecha ON movimientos(fecha);
CREATE INDEX IF NOT EXISTS idx_movimientos_tipo ON movimientos(tipo);
CREATE INDEX IF NOT EXISTS idx_proyectos_estado ON proyectos(estado);
CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha);
CREATE INDEX IF NOT EXISTS idx_venta_items_venta ON venta_items(venta_id);
"""

MOVIMIENTO_CAMPOS = (
    "fecha", "tipo", "concepto", "monto_cents", "categoria",
    "contacto_id", "metodo_pago", "notas",
)
PROYECTO_CAMPOS = (
    "nombre", "contacto_id", "descripcion", "estado", "prioridad",
    "fecha_inicio", "fecha_limite", "presupuesto_cents", "notas",
)
CONTACTO_CAMPOS = (
    "nombre", "tipo", "identificacion", "telefono", "email", "direccion", "notas",
)
PRODUCTO_CAMPOS = (
    "nombre", "tipo", "precio_cents", "categoria", "precio_etiqueta",
    "activo", "destacado", "notas",
)


class Database:
    """Maneja la conexión y todas las consultas de la aplicación."""

    def __init__(self, ruta: str):
        self.ruta = ruta
        es_nueva = not os.path.exists(ruta)
        os.makedirs(os.path.dirname(os.path.abspath(ruta)), exist_ok=True)
        with self.conexion() as conn:
            conn.executescript(ESQUEMA)
        # Primero se reconstruye `productos` si su CHECK no admite Paquete;
        # después se agregan las columnas nuevas, para que no se pierdan.
        self._migrar_tipos_producto()
        self._migrar()
        if es_nueva:
            self.sembrar_catalogo_inicial()

    def _migrar(self):
        """Agrega columnas nuevas a bases creadas por versiones anteriores."""
        nuevas = {
            "descuento_tipo": "TEXT NOT NULL DEFAULT '%'",
            "descuento_valor": "REAL NOT NULL DEFAULT 0",
            "base_cents": "INTEGER NOT NULL DEFAULT 0",
            "impuesto_pct": "REAL NOT NULL DEFAULT 0",
            "impuesto_cents": "INTEGER NOT NULL DEFAULT 0",
        }
        with self.conexion() as conn:
            actuales = {fila["name"] for fila in conn.execute("PRAGMA table_info(ventas)")}
            for nombre, definicion in nuevas.items():
                if nombre not in actuales:
                    conn.execute(f"ALTER TABLE ventas ADD COLUMN {nombre} {definicion}")
            conn.execute(
                "UPDATE ventas SET base_cents = subtotal_cents - descuento_cents "
                "WHERE base_cents = 0 AND subtotal_cents > 0"
            )

            columnas_producto = {
                "precio_etiqueta": "TEXT NOT NULL DEFAULT ''",
                "destacado": "INTEGER NOT NULL DEFAULT 0 CHECK (destacado IN (0, 1))",
            }
            actuales = {fila["name"] for fila in conn.execute("PRAGMA table_info(productos)")}
            for nombre, definicion in columnas_producto.items():
                if nombre not in actuales:
                    conn.execute(f"ALTER TABLE productos ADD COLUMN {nombre} {definicion}")

    def _migrar_tipos_producto(self):
        """Habilita el tipo 'Paquete' en bases creadas por versiones anteriores.

        SQLite no permite cambiar un CHECK con ALTER TABLE, así que se recrea
        la tabla. Se usa una conexión aparte con las claves foráneas apagadas
        para que `venta_items.producto_id` siga apuntando a `productos` y no se
        pierdan los vínculos con las ventas ya registradas.
        """
        conn = sqlite3.connect(self.ruta, timeout=10)
        try:
            conn.execute("PRAGMA foreign_keys = OFF")
            conn.execute("PRAGMA legacy_alter_table = ON")
            fila = conn.execute(
                "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'productos'"
            ).fetchone()
            if fila and "Paquete" not in (fila[0] or ""):
                conn.execute("ALTER TABLE productos RENAME TO productos_old")
                conn.execute("""
                    CREATE TABLE productos (
                        id            INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre        TEXT NOT NULL,
                        tipo          TEXT NOT NULL DEFAULT 'Producto'
                                      CHECK (tipo IN ('Producto', 'Servicio', 'Paquete')),
                        precio_cents  INTEGER NOT NULL DEFAULT 0 CHECK (precio_cents >= 0),
                        categoria     TEXT NOT NULL DEFAULT '',
                        activo        INTEGER NOT NULL DEFAULT 1,
                        notas         TEXT NOT NULL DEFAULT '',
                        creado_en     TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
                    )
                """)
                conn.execute(
                    "INSERT INTO productos "
                    "(id, nombre, tipo, precio_cents, categoria, activo, notas, creado_en) "
                    "SELECT id, nombre, tipo, precio_cents, categoria, activo, notas, creado_en "
                    "FROM productos_old"
                )
                conn.execute("DROP TABLE productos_old")
            conn.commit()
        finally:
            conn.close()

    @contextmanager
    def conexion(self):
        conn = sqlite3.connect(self.ruta, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------------ movimientos

    def listar_movimientos(
        self, tipo=None, buscar="", desde=None, hasta=None,
        categoria=None, limite=None,
    ) -> list[dict]:
        sql = (
            "SELECT m.id, m.fecha, m.tipo, m.concepto, m.categoria, m.monto_cents, "
            "m.metodo_pago, m.notas, m.contacto_id, "
            "COALESCE(c.nombre, '') AS contacto "
            "FROM movimientos m LEFT JOIN contactos c ON c.id = m.contacto_id "
            "WHERE 1=1"
        )
        params: list = []
        if tipo and tipo != "Todos":
            sql += " AND m.tipo = ?"
            params.append(tipo)
        if categoria and categoria != "Todas":
            sql += " AND m.categoria = ?"
            params.append(categoria)
        if desde:
            sql += " AND m.fecha >= ?"
            params.append(desde)
        if hasta:
            sql += " AND m.fecha <= ?"
            params.append(hasta)
        if buscar:
            patron = f"%{buscar.strip().lower()}%"
            sql += (" AND (LOWER(m.concepto) LIKE ? OR LOWER(m.categoria) LIKE ? "
                    "OR LOWER(COALESCE(m.notas, '')) LIKE ? "
                    "OR LOWER(COALESCE(c.nombre, '')) LIKE ?)")
            params.extend([patron] * 4)
        sql += " ORDER BY m.fecha DESC, m.id DESC"
        if limite:
            sql += " LIMIT ?"
            params.append(limite)
        with self.conexion() as conn:
            return [dict(fila) for fila in conn.execute(sql, params)]

    def venta_de_movimiento(self, movimiento_id: int) -> int | None:
        """Devuelve la venta que generó este ingreso, si la hay."""
        with self.conexion() as conn:
            fila = conn.execute(
                "SELECT id FROM ventas WHERE movimiento_id = ?", (movimiento_id,)
            ).fetchone()
            return fila["id"] if fila else None

    def guardar_movimiento(self, datos: dict, id: int | None = None) -> int:
        if id and self.venta_de_movimiento(id):
            raise ValueError(
                "Este ingreso fue generado por una venta. Adminístralo desde Cobros › Ventas."
            )
        return self._guardar("movimientos", MOVIMIENTO_CAMPOS, datos, id)

    def eliminar_movimiento(self, id: int) -> int:
        if self.venta_de_movimiento(id):
            raise ValueError(
                "Este ingreso pertenece a una venta. Elimina la venta desde Cobros › Ventas."
            )
        return self._eliminar("movimientos", id)

    # ------------------------------------------------------------------- proyectos

    def listar_proyectos(
        self, estado=None, prioridad=None, buscar="", limite=None,
    ) -> list[dict]:
        sql = (
            "SELECT p.*, COALESCE(c.nombre, '') AS cliente "
            "FROM proyectos p LEFT JOIN contactos c ON c.id = p.contacto_id "
            "WHERE 1=1"
        )
        params: list = []
        if estado and estado != "Todos":
            sql += " AND p.estado = ?"
            params.append(estado)
        if prioridad and prioridad != "Todas":
            sql += " AND p.prioridad = ?"
            params.append(prioridad)
        if buscar:
            patron = f"%{buscar.strip().lower()}%"
            sql += (" AND (LOWER(p.nombre) LIKE ? OR LOWER(COALESCE(p.descripcion, '')) LIKE ? "
                    "OR LOWER(COALESCE(c.nombre, '')) LIKE ?)")
            params.extend([patron] * 3)
        sql += " ORDER BY (p.estado = 'Completado'), p.fecha_limite IS NULL, p.fecha_limite, p.id DESC"
        if limite:
            sql += " LIMIT ?"
            params.append(limite)
        with self.conexion() as conn:
            return [dict(fila) for fila in conn.execute(sql, params)]

    def guardar_proyecto(self, datos: dict, id: int | None = None) -> int:
        return self._guardar("proyectos", PROYECTO_CAMPOS, datos, id)

    def eliminar_proyecto(self, id: int) -> int:
        return self._eliminar("proyectos", id)

    def proximos_proyectos(self, limite: int = 6) -> list[dict]:
        sql = (
            "SELECT p.*, COALESCE(c.nombre, '') AS cliente "
            "FROM proyectos p LEFT JOIN contactos c ON c.id = p.contacto_id "
            "WHERE p.estado IN ('Pendiente', 'En curso') AND p.fecha_limite IS NOT NULL "
            "ORDER BY p.fecha_limite ASC LIMIT ?"
        )
        with self.conexion() as conn:
            return [dict(fila) for fila in conn.execute(sql, (limite,))]

    def contar_proyectos_pendientes(self) -> int:
        with self.conexion() as conn:
            fila = conn.execute(
                "SELECT COUNT(*) AS n FROM proyectos WHERE estado IN ('Pendiente', 'En curso')"
            ).fetchone()
            return fila["n"]

    def hitos_proyectos(self, desde: str, hasta: str) -> dict[str, dict]:
        """Agrupa entregas e inicios de proyectos por fecha (ISO)."""
        sql = """
            SELECT fecha_limite AS fecha, 'Entrega' AS evento, id, nombre, estado
              FROM proyectos WHERE fecha_limite BETWEEN ? AND ?
            UNION ALL
            SELECT fecha_inicio AS fecha, 'Inicio' AS evento, id, nombre, estado
              FROM proyectos WHERE fecha_inicio BETWEEN ? AND ?
            ORDER BY fecha, evento, nombre
        """
        with self.conexion() as conn:
            filas = conn.execute(sql, (desde, hasta, desde, hasta)).fetchall()
        resultado: dict[str, dict] = {}
        for fila in filas:
            entry = resultado.setdefault(
                fila["fecha"], {"entregas": [], "inicios": []}
            )
            destino = "entregas" if fila["evento"] == "Entrega" else "inicios"
            entry[destino].append(dict(fila))
        return resultado

    def proyectos_en_fecha(self, dia: str) -> list[dict]:
        """Entregas e inicios de proyectos que caen en un día concreto."""
        sql = """
            SELECT id, nombre, 'Entrega' AS evento, estado, prioridad
              FROM proyectos WHERE fecha_limite = ?
            UNION ALL
            SELECT id, nombre, 'Inicio' AS evento, estado, prioridad
              FROM proyectos WHERE fecha_inicio = ?
            ORDER BY evento, nombre
        """
        with self.conexion() as conn:
            return [dict(fila) for fila in conn.execute(sql, (dia, dia))]

    # ------------------------------------------------------------------- contactos

    def listar_contactos(self, tipo=None, buscar="") -> list[dict]:
        sql = "SELECT * FROM contactos WHERE 1=1"
        params: list = []
        if tipo and tipo != "Todos":
            sql += " AND tipo = ?"
            params.append(tipo)
        if buscar:
            patron = f"%{buscar.strip().lower()}%"
            sql += (" AND (LOWER(nombre) LIKE ? OR LOWER(COALESCE(identificacion, '')) LIKE ? "
                    "OR LOWER(COALESCE(email, '')) LIKE ?)")
            params.extend([patron] * 3)
        sql += " ORDER BY nombre COLLATE NOCASE"
        with self.conexion() as conn:
            return [dict(fila) for fila in conn.execute(sql, params)]

    def guardar_contacto(self, datos: dict, id: int | None = None) -> int:
        return self._guardar("contactos", CONTACTO_CAMPOS, datos, id)

    def eliminar_contacto(self, id: int) -> int:
        return self._eliminar("contactos", id)

    def opciones_contactos(self) -> dict[str, int | None]:
        with self.conexion() as conn:
            filas = conn.execute(
                "SELECT id, nombre, tipo FROM contactos ORDER BY nombre COLLATE NOCASE"
            ).fetchall()
        opciones = {"— Ninguno —": None}
        for fila in filas:
            opciones[f"{fila['nombre']} ({fila['tipo']})"] = fila["id"]
        return opciones

    # ------------------------------------------------------------- productos / POS

    def sembrar_catalogo_inicial(self) -> int:
        """Carga el catálogo base sin duplicar lo que el usuario ya tiene.

        Se llama al crear una base de datos nueva y puede ejecutarse cuando se
        quiera (por ejemplo desde un script) para recuperar el catálogo. La
        clave es el nombre, así que es seguro llamarla varias veces.
        """
        insertados = 0
        with self.conexion() as conn:
            existentes = {
                fila[0] for fila in conn.execute("SELECT nombre FROM productos")
            }
            for item in catalogo_inicial():
                if item["nombre"] in existentes:
                    continue
                conn.execute(
                    "INSERT INTO productos "
                    "(nombre, tipo, precio_cents, categoria, precio_etiqueta, "
                    " activo, destacado, notas) "
                    "VALUES (?, ?, ?, ?, ?, 1, ?, ?)",
                    (item["nombre"], item["tipo"], item["precio_cents"],
                     item["categoria"], item["etiqueta"], item["destacado"],
                     item["notas"]),
                )
                insertados += 1
        return insertados

    def listar_productos(self, buscar="", tipo=None, solo_activos=False) -> list[dict]:
        sql = "SELECT * FROM productos WHERE 1=1"
        params: list = []
        if tipo and tipo != "Todos":
            sql += " AND tipo = ?"
            params.append(tipo)
        if solo_activos:
            sql += " AND activo = 1"
        if buscar:
            patron = f"%{buscar.strip().lower()}%"
            sql += (" AND (LOWER(nombre) LIKE ? OR LOWER(COALESCE(categoria, '')) LIKE ?)")
            params.extend([patron, patron])
        sql += " ORDER BY activo DESC, nombre COLLATE NOCASE"
        with self.conexion() as conn:
            return [dict(fila) for fila in conn.execute(sql, params)]

    def guardar_producto(self, datos: dict, id: int | None = None) -> int:
        return self._guardar("productos", PRODUCTO_CAMPOS, datos, id)

    def eliminar_producto(self, id: int) -> int:
        return self._eliminar("productos", id)

    def listar_ventas(self, buscar="", desde=None, hasta=None, contacto_id=None) -> list[dict]:
        sql = (
            "SELECT v.*, COALESCE(c.nombre, '') AS contacto, "
            "(SELECT COUNT(*) FROM venta_items vi WHERE vi.venta_id = v.id) AS n_items "
            "FROM ventas v LEFT JOIN contactos c ON c.id = v.contacto_id "
            "WHERE 1=1"
        )
        params: list = []
        if desde:
            sql += " AND v.fecha >= ?"
            params.append(desde)
        if hasta:
            sql += " AND v.fecha <= ?"
            params.append(hasta)
        if contacto_id:
            sql += " AND v.contacto_id = ?"
            params.append(contacto_id)
        if buscar:
            patron = f"%{buscar.strip().lower()}%"
            sql += (" AND (LOWER(COALESCE(c.nombre, '')) LIKE ? "
                    "OR LOWER(COALESCE(v.notas, '')) LIKE ? "
                    "OR CAST(v.id AS TEXT) LIKE ?)")
            params.extend([patron, patron, patron])
        sql += " ORDER BY v.fecha DESC, v.id DESC"
        with self.conexion() as conn:
            return [dict(fila) for fila in conn.execute(sql, params)]

    def obtener_venta(self, id: int) -> dict | None:
        with self.conexion() as conn:
            fila = conn.execute("SELECT * FROM ventas WHERE id = ?", (id,)).fetchone()
            if fila is None:
                return None
            venta = dict(fila)
            venta["items"] = [
                dict(item) for item in conn.execute(
                    "SELECT * FROM venta_items WHERE venta_id = ? ORDER BY id", (id,)
                )
            ]
            return venta

    def registrar_venta(self, datos: dict) -> int:
        """Guarda la venta, sus items y el ingreso asociado en una transacción.

        El total (con descuento e impuesto incluidos) se registra como un
        ingreso en ``movimientos``, de modo que aparece igual en Resumen,
        Movimientos, Calendario y Reportes.
        """
        items = datos.get("items") or []
        if not items:
            raise ValueError("Agrega al menos un producto o servicio al cobro.")

        preparados = []
        for item in items:
            nombre = str(item.get("nombre") or "").strip()
            if not nombre:
                raise ValueError("Hay un item sin nombre.")
            preparados.append(item)

        calculo = calcular_totales(
            preparados,
            descuento_tipo=datos.get("descuento_tipo") or "%",
            descuento_valor=datos.get("descuento_valor") or 0,
            impuesto_pct=datos.get("impuesto_pct") or 0,
        )
        if calculo["total"] <= 0:
            raise ValueError("El total del cobro debe ser mayor que cero.")

        descuento_tipo = calculo["descuento_tipo"]
        descuento_valor = calculo["descuento_valor"]
        impuesto_pct = calculo["impuesto_pct"]

        detalle = []
        if calculo["descuento"]:
            etiqueta = (f"{descuento_valor:g} %" if descuento_tipo == "%"
                        else formatear_monto(int(descuento_valor)))
            detalle.append(f"Descuento {etiqueta}: -{formatear_monto(calculo['descuento'])}")
        if calculo["impuesto"]:
            detalle.append(
                f"Impuesto {impuesto_pct:g} %: +{formatear_monto(calculo['impuesto'])}"
            )
        notas = (datos.get("notas") or "").strip()
        if detalle:
            notas = notas + (" | " if notas else "") + "; ".join(detalle)

        with self.conexion() as conn:
            cursor = conn.execute(
                """INSERT INTO ventas
                   (fecha, contacto_id, metodo_pago, subtotal_cents, descuento_tipo,
                    descuento_valor, descuento_cents, base_cents, impuesto_pct,
                    impuesto_cents, total_cents, notas)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (datos["fecha"], datos.get("contacto_id"),
                 datos.get("metodo_pago") or "Efectivo", calculo["subtotal"],
                 descuento_tipo, descuento_valor, calculo["descuento"],
                 calculo["base"], impuesto_pct, calculo["impuesto"],
                 calculo["total"], notas),
            )
            venta_id = cursor.lastrowid
            conn.executemany(
                """INSERT INTO venta_items
                   (venta_id, producto_id, nombre, tipo, cantidad, precio_cents,
                    descuento_pct, descuento_cents, total_cents)
                   VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?)""",
                [(venta_id, item.get("producto_id"), item["nombre"].strip(),
                  item.get("tipo") or "Producto", int(item["cantidad"]),
                  int(item["precio_cents"]),
                  int(item["precio_cents"]) * int(item["cantidad"]))
                 for item in preparados],
            )
            movimiento = conn.execute(
                """INSERT INTO movimientos
                   (fecha, tipo, concepto, monto_cents, categoria, contacto_id,
                    metodo_pago, notas)
                   VALUES (?, 'Ingreso', ?, ?, 'Ventas', ?, ?, ?)""",
                (datos["fecha"], f"Venta #{venta_id} ({len(preparados)} items)",
                 calculo["total"], datos.get("contacto_id"),
                 datos.get("metodo_pago") or "Efectivo", notas),
            )
            conn.execute(
                "UPDATE ventas SET movimiento_id = ? WHERE id = ?",
                (movimiento.lastrowid, venta_id),
            )
            return venta_id

    def eliminar_venta(self, id: int) -> int:
        """Elimina la venta y el ingreso que generó, para no alterar el balance."""
        with self.conexion() as conn:
            fila = conn.execute(
                "SELECT movimiento_id FROM ventas WHERE id = ?", (id,)
            ).fetchone()
            if fila is None:
                return 0
            if fila["movimiento_id"]:
                conn.execute("DELETE FROM movimientos WHERE id = ?", (fila["movimiento_id"],))
            return conn.execute("DELETE FROM ventas WHERE id = ?", (id,)).rowcount

    def resumen_ventas(self, desde=None, hasta=None) -> dict:
        sql = (
            "SELECT COUNT(*) AS n, "
            "COALESCE(SUM(subtotal_cents), 0) AS subtotal, "
            "COALESCE(SUM(descuento_cents), 0) AS descuento, "
            "COALESCE(SUM(impuesto_cents), 0) AS impuesto, "
            "COALESCE(SUM(total_cents), 0) AS total, "
            "COALESCE(SUM(descuento_cents > 0), 0) AS con_descuento "
            "FROM ventas WHERE 1=1"
        )
        params: list = []
        if desde:
            sql += " AND fecha >= ?"
            params.append(desde)
        if hasta:
            sql += " AND fecha <= ?"
            params.append(hasta)
        with self.conexion() as conn:
            return dict(conn.execute(sql, params).fetchone())

    # -------------------------------------------------------------- reportes / stats

    def totales(self, desde=None, hasta=None) -> dict:
        sql = (
            "SELECT COALESCE(SUM(CASE WHEN tipo='Ingreso' THEN monto_cents ELSE 0 END), 0) AS ingresos, "
            "COALESCE(SUM(CASE WHEN tipo='Gasto' THEN monto_cents ELSE 0 END), 0) AS gastos, "
            "COUNT(*) AS cantidad FROM movimientos WHERE 1=1"
        )
        params: list = []
        if desde:
            sql += " AND fecha >= ?"
            params.append(desde)
        if hasta:
            sql += " AND fecha <= ?"
            params.append(hasta)
        with self.conexion() as conn:
            return dict(conn.execute(sql, params).fetchone())

    def por_mes(self, desde=None, hasta=None) -> dict[str, dict]:
        sql = (
            "SELECT strftime('%Y-%m', fecha) AS mes, "
            "COALESCE(SUM(CASE WHEN tipo='Ingreso' THEN monto_cents ELSE 0 END), 0) AS ingresos, "
            "COALESCE(SUM(CASE WHEN tipo='Gasto' THEN monto_cents ELSE 0 END), 0) AS gastos "
            "FROM movimientos WHERE 1=1"
        )
        params: list = []
        if desde:
            sql += " AND fecha >= ?"
            params.append(desde)
        if hasta:
            sql += " AND fecha <= ?"
            params.append(hasta)
        sql += " GROUP BY mes ORDER BY mes"
        with self.conexion() as conn:
            return {fila["mes"]: dict(fila) for fila in conn.execute(sql, params)}

    def resumen_diario(self, desde: str, hasta: str) -> dict[str, dict]:
        """Totales de ingresos y gastos agrupados por día."""
        sql = """
            SELECT fecha,
                   SUM(CASE WHEN tipo = 'Ingreso' THEN monto_cents ELSE 0 END) AS ingresos,
                   SUM(CASE WHEN tipo = 'Gasto' THEN monto_cents ELSE 0 END) AS gastos,
                   SUM(CASE WHEN tipo = 'Ingreso' THEN 1 ELSE 0 END) AS n_ingresos,
                   SUM(CASE WHEN tipo = 'Gasto' THEN 1 ELSE 0 END) AS n_gastos
              FROM movimientos WHERE fecha BETWEEN ? AND ?
             GROUP BY fecha
        """
        with self.conexion() as conn:
            return {fila["fecha"]: dict(fila) for fila in conn.execute(sql, (desde, hasta))}

    def por_categoria(self, desde=None, hasta=None, tipo=None) -> list[dict]:
        sql = (
            "SELECT categoria, tipo, SUM(monto_cents) AS total, COUNT(*) AS cantidad "
            "FROM movimientos WHERE 1=1"
        )
        params: list = []
        if desde:
            sql += " AND fecha >= ?"
            params.append(desde)
        if hasta:
            sql += " AND fecha <= ?"
            params.append(hasta)
        if tipo and tipo != "Todos":
            sql += " AND tipo = ?"
            params.append(tipo)
        sql += " GROUP BY categoria, tipo ORDER BY total DESC"
        with self.conexion() as conn:
            return [dict(fila) for fila in conn.execute(sql, params)]

    # ---------------------------------------------------------------------- internos

    def obtener(self, tabla: str, id: int) -> dict | None:
        """Devuelve un registro por su id (tablas internas de la aplicación)."""
        if tabla not in {"movimientos", "proyectos", "contactos", "productos"}:
            raise ValueError("Tabla no permitida")
        with self.conexion() as conn:
            fila = conn.execute(f"SELECT * FROM {tabla} WHERE id = ?", (id,)).fetchone()
            return dict(fila) if fila else None

    def _guardar(self, tabla: str, campos: tuple[str, ...], datos: dict, id=None) -> int:
        valores = [datos.get(campo) for campo in campos]
        with self.conexion() as conn:
            if id:
                asignaciones = ", ".join(f"{campo} = ?" for campo in campos)
                conn.execute(
                    f"UPDATE {tabla} SET {asignaciones} WHERE id = ?",
                    valores + [id],
                )
                return id
            columnas = ", ".join(campos)
            marcadores = ", ".join("?" for _ in campos)
            cursor = conn.execute(
                f"INSERT INTO {tabla} ({columnas}) VALUES ({marcadores})", valores
            )
            return cursor.lastrowid

    def _eliminar(self, tabla: str, id: int) -> int:
        with self.conexion() as conn:
            cursor = conn.execute(f"DELETE FROM {tabla} WHERE id = ?", (id,))
            return cursor.rowcount
