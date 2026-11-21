"""Capa de persistencia SQLite de THC Contabilidad."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager

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

CREATE INDEX IF NOT EXISTS idx_movimientos_fecha ON movimientos(fecha);
CREATE INDEX IF NOT EXISTS idx_movimientos_tipo ON movimientos(tipo);
CREATE INDEX IF NOT EXISTS idx_proyectos_estado ON proyectos(estado);
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


class Database:
    """Maneja la conexión y todas las consultas de la aplicación."""

    def __init__(self, ruta: str):
        self.ruta = ruta
        os.makedirs(os.path.dirname(os.path.abspath(ruta)), exist_ok=True)
        with self.conexion() as conn:
            conn.executescript(ESQUEMA)

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

    def guardar_movimiento(self, datos: dict, id: int | None = None) -> int:
        return self._guardar("movimientos", MOVIMIENTO_CAMPOS, datos, id)

    def eliminar_movimiento(self, id: int) -> int:
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
        if tabla not in {"movimientos", "proyectos", "contactos"}:
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
