"""Utilidades de formato, conversión y validación para THC Contabilidad.

Los montos se guardan en centavos (enteros) para evitar errores de coma flotante.
La moneda de la aplicación es el peso colombiano (COP).
"""

from __future__ import annotations

import calendar
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

MONEDA = "COP"
SIMBOLO = "$"

MESES = (
    "ene", "feb", "mar", "abr", "may", "jun",
    "jul", "ago", "sep", "oct", "nov", "dic",
)
MESES_LARGOS = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)

ESTADOS_PROYECTO = ("Pendiente", "En curso", "Completado", "Cancelado")
PRIORIDADES = ("Alta", "Media", "Baja")
TIPOS_MOVIMIENTO = ("Ingreso", "Gasto")
TIPOS_CONTACTO = ("Cliente", "Proveedor", "Ambos")
TIPOS_PRODUCTO = ("Producto", "Servicio", "Paquete")
METODOS_PAGO = ("Efectivo", "Transferencia", "Tarjeta", "PSE", "Otro")
CATEGORIAS_INGRESO = (
    "Ventas", "Servicios", "Honorarios", "Comisiones", "Intereses", "Otros ingresos",
)
CATEGORIAS_GASTO = (
    "Compras", "Nómina", "Arriendo", "Servicios públicos", "Transporte",
    "Marketing", "Software", "Impuestos", "Otros gastos",
)
SIN_CONTACTO = "— Ninguno —"


def a_centros(texto: str) -> int:
    """Convierte texto de monto COP a centavos enteros.

    Acepta formatos comunes: 1250000, 1.250.000, 1250.50, $ 1.250,50.
    Rechaza los negativos: la app guarda montos como enteros positivos.
    """
    if texto is None:
        raise ValueError("Escribe un monto.")
    limpio = re.sub(r"[^\d.,\-]", "", str(texto).strip())
    if not limpio or limpio in {"-", ".", ","}:
        raise ValueError("Escribe un monto válido.")

    negativo = limpio.startswith("-")
    limpio = limpio.lstrip("+-")

    if "." in limpio and "," in limpio:
        if limpio.rfind(".") > limpio.rfind(","):
            limpio = limpio.replace(",", "")
        else:
            limpio = limpio.replace(".", "").replace(",", ".")
    elif "," in limpio:
        partes = limpio.split(",")
        if len(partes) == 2 and len(partes[1]) in (1, 2):
            limpio = limpio.replace(",", ".")
        else:
            limpio = limpio.replace(",", "")
    elif "." in limpio:
        partes = limpio.split(".")
        if len(partes) == 2 and len(partes[1]) in (1, 2):
            pass  # decimal, p. ej. 1250.50
        else:
            limpio = limpio.replace(".", "")  # miles, p. ej. 1.250.000

    try:
        valor = Decimal(limpio)
    except InvalidOperation as exc:
        raise ValueError("El monto no tiene un formato válido.") from exc

    if negativo or valor < 0:
        raise ValueError("El monto no puede ser negativo.")

    return int((valor * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def formatear_monto(centavos: int | None, simbolo: bool = True) -> str:
    """Devuelve un monto con el formato de moneda elegido en Ajustes.

    Los importes siguen guardándose como enteros en la unidad menor (centavos);
    cambiar de moneda solo cambia la presentación, nunca convierte valores.
    """
    if centavos is None:
        centavos = 0
    signo = "-" if centavos < 0 else ""
    entero, decimal = divmod(abs(int(centavos)), 100)
    texto = f"{signo}{entero:,}".replace(",", ".")
    if decimal:
        texto += f",{decimal:02d}"
    if not simbolo:
        return texto
    from .config import formatear_texto, moneda_actual  # importación diferida

    codigo, _simbolo, formato = moneda_actual()
    return formatear_texto(texto, codigo, formato)


def formatear_porcentaje(valor: float) -> str:
    return f"{valor:.1f} %".replace(".", ",")


def hoy_iso() -> str:
    return date.today().isoformat()


def validar_fecha(texto: str, obligatorio: bool = False) -> str | None:
    """Valifica una fecha AAAA-MM-DD. Devuelve None si está vacía y no es obligatoria."""
    valor = (texto or "").strip()
    if not valor:
        if obligatorio:
            raise ValueError("Selecciona una fecha.")
        return None
    try:
        datetime.strptime(valor, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("La fecha debe tener el formato AAAA-MM-DD.") from exc
    return valor


def fecha_legible(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        d = datetime.strptime(iso, "%Y-%m-%d").date()
    except ValueError:
        return iso
    return f"{d.day:02d} {MESES[d.month - 1]} {d.year}"


def mes_legible(ano_mes: str | None) -> str:
    if not ano_mes or len(ano_mes) < 7:
        return "—"
    try:
        ano, mes = int(ano_mes[:4]), int(ano_mes[5:7])
    except ValueError:
        return ano_mes
    return f"{MESES[mes - 1]} {ano}"


def primer_dia_mes(d: date) -> date:
    return d.replace(day=1)


def sumar_meses(d: date, cantidad: int) -> date:
    indice = d.month - 1 + cantidad
    ano = d.year + indice // 12
    mes = indice % 12 + 1
    dia = min(d.day, _dias_del_mes(ano, mes))
    return date(ano, mes, dia)


def _dias_del_mes(ano: int, mes: int) -> int:
    return calendar.monthrange(ano, mes)[1]


def rango_periodo(periodo: str) -> tuple[str | None, str | None]:
    """Devuelve (desde, hasta) en ISO para el período elegido."""
    hoy = date.today()
    if periodo == "Este mes":
        return primer_dia_mes(hoy).isoformat(), hoy.isoformat()
    if periodo == "Últimos 3 meses":
        return primer_dia_mes(sumar_meses(hoy, -2)).isoformat(), hoy.isoformat()
    if periodo == "Últimos 6 meses":
        return primer_dia_mes(sumar_meses(hoy, -5)).isoformat(), hoy.isoformat()
    if periodo == "Este año":
        return date(hoy.year, 1, 1).isoformat(), hoy.isoformat()
    return None, None


def meses_recientes(cantidad: int) -> list[str]:
    hoy = date.today()
    return [sumar_meses(primer_dia_mes(hoy), -i).strftime("%Y-%m")
            for i in range(cantidad - 1, -1, -1)]


def porcentaje(parte: int, total: int) -> float:
    return (abs(parte) / abs(total) * 100) if total else 0.0


def calcular_totales(
    items, descuento_tipo: str = "%", descuento_valor=0, impuesto_pct=0.0,
) -> dict:
    """Calcula el cobro completo, en centavos, con descuento e impuesto.

    El descuento puede ser ``%`` (sobre el subtotal) o ``Fijo`` (valor en
    centavos, admitiendo también ``$`` como alias). El impuesto se aplica sobre
    el subtotal ya descontado. La interfaz y la base de datos usan esta misma
    función para que los totales nunca difieran.
    """
    subtotal = 0
    for item in items or []:
        cantidad = int(item.get("cantidad") or 0)
        precio = int(item.get("precio_cents") or 0)
        if cantidad <= 0 or precio < 0:
            raise ValueError("Revisa las cantidades y los precios del cobro.")
        subtotal += precio * cantidad

    tipo = "Fijo" if str(descuento_tipo) in {"$", "Fijo"} else "%"
    valor = Decimal(str(descuento_valor or 0))
    if valor < 0:
        raise ValueError("El descuento no puede ser negativo.")

    if tipo == "%":
        if valor > 100:
            raise ValueError("El descuento no puede superar el 100 %.")
        descuento = int(
            (Decimal(subtotal) * valor / Decimal(100)).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
        )
    else:
        descuento = min(int(valor), subtotal)

    base = subtotal - descuento
    pct = Decimal(str(impuesto_pct or 0))
    if pct < 0 or pct > 100:
        raise ValueError("El impuesto debe estar entre 0 % y 100 %.")
    impuesto = int(
        (Decimal(base) * pct / Decimal(100)).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
    )

    return {
        "subtotal": subtotal,
        "descuento": descuento,
        "base": base,
        "impuesto": impuesto,
        "total": base + impuesto,
        "descuento_tipo": tipo,
        "descuento_valor": float(valor),
        "impuesto_pct": float(pct),
    }


def barra_texto(fraccion: float, ancho: int = 12) -> str:
    llenos = max(0, min(ancho, int(round(fraccion * ancho))))
    return "█" * llenos + "░" * (ancho - llenos)
