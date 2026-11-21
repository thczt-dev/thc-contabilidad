# THC Contabilidad v1.0.0

Primera versión estable de la aplicación de escritorio para Linux.

## Incluye

- **Resumen**: indicadores del mes, balance, últimos movimientos, vencimientos y gráfico.
- **Movimientos**: ingresos y gastos con búsqueda, filtros, edición y borrado.
- **Proyectos**: cliente, estado, prioridad, fechas, presupuesto y control de plazos.
- **Calendario**: vista mensual con ingresos, gastos, entregas e inicios de proyectos; detalle por día y resumen mensual.
- **Contactos**: clientes y proveedores con NIT, teléfono, correo y dirección.
- **Reportes**: balances, resumen mensual, categorías y exportación CSV.
- Interfaz oscura minimalista con acento azul pastel.
- Datos locales en SQLite, moneda COP y montos guardados en centavos.
- Acceso directo `.desktop`, icono e instalador desde GitHub.
- Licencia MIT.

## Requisitos

Linux con Python 3.11+, GTK 3 y PyGObject (`python3-gi`, `gir1.2-gtk-3.0`, `python3-cairo`).

## Instalación

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/thczt-dev/thc-contabilidad/v1.0.0/instalar-github.sh)
```

O manualmente:

```bash
git clone --branch v1.0.0 https://github.com/thczt-dev/thc-contabilidad.git
cd thc-contabilidad
./instalar.sh
```

Cambios completos: [`CHANGELOG.md`](CHANGELOG.md).
