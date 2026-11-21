"""Pestañas de la interfaz de THC Contabilidad."""

from .resumen import ResumenView
from .movimientos import MovimientosView
from .proyectos import ProyectosView
from .calendario import CalendarioView
from .contactos import ContactosView
from .reportes import ReportesView

__all__ = [
    "ResumenView",
    "MovimientosView",
    "ProyectosView",
    "CalendarioView",
    "ContactosView",
    "ReportesView",
]
