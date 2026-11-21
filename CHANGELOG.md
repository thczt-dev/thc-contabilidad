# Registro de cambios

Todas las versiones notables de THC Contabilidad se documentan aquí.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el proyecto usa [Versionado Semántico](https://semver.org/lang/es/).

## [1.0.0] - 2026-11-21

Primera versión estable.

### Añadido

- Pestaña **Resumen** con indicadores del mes, balance acumulado, últimos
  movimientos, próximos vencimientos y gráfico de ingresos vs. gastos.
- Pestaña **Movimientos** con alta, edición, borrado, búsqueda y filtros de
  ingresos y gastos.
- Pestaña **Proyectos** con cliente, estado, prioridad, fechas, presupuesto y
  control de vencimientos.
- Pestaña **Calendario** con vista mensual, puntos de color por día
  (ingresos, gastos, entregas e inicios), tooltips, panel de detalle diario y
  resumen mensual.
- Pestaña **Contactos** para clientes y proveedores con NIT, teléfono, correo
  y dirección.
- Pestaña **Reportes** con balances por período, resumen mensual,
  distribución por categoría y exportación a CSV.
- Tema oscuro moderno y minimalista con acento azul pastel (`#8ab4ff`),
  centralizado en `thc_contabilidad/theme.py`.
- Lanzador ejecutable `thc-contabilidad`, plantilla `.desktop`, icono SVG y
  script `instalar.sh` para el menú de aplicaciones.
- Base de datos SQLite local con montos en centavos y moneda COP.
- Atajos de teclado: `Ctrl+N`, `Ctrl+P`, `Ctrl+Shift+C`, `Ctrl+E` y `Ctrl+Q`.
- Licencia MIT, `.gitignore`, integración continua básica y documentación de
  lanzamiento para GitHub.

### Corregido

- Interfaz con colores invertidos: se reemplazó por el tema oscuro propio.
- Lectura de combos no editables y declaración explícita de la versión de Gdk.
- Tipos de columnas e ids ocultos en los `ListStore`.
- Fallo de segmentación al hacer clic en el calendario: las 42 celdas ahora
  se reutilizan en lugar de destruirse dentro de la señal `clicked`.

[1.0.0]: https://github.com/ThcDev/thc-contabilidad/releases/tag/v1.0.0
