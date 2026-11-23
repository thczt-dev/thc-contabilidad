"""Pestañas de la interfaz de THC Contabilidad."""

from .resumen import ResumenView
from .movimientos import MovimientosView
from .proyectos import ProyectosView
from .calendario import CalendarioView
from .cobros import CobrosView
from .contactos import ContactosView
from .reportes import ReportesView
from .ajustes import AjustesDialog
from .licencia import LicenciaDialog

__all__ = [
    "AjustesDialog",
    "LicenciaDialog",
    "ResumenView",
    "MovimientosView",
    "ProyectosView",
    "CalendarioView",
    "CobrosView",
    "ContactosView",
    "ReportesView",
]
