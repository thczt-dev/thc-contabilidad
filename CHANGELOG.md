# Registro de cambios

Todas las versiones notables de THC Contabilidad se documentan aquí.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el proyecto usa [Versionado Semántico](https://semver.org/lang/es/).

## [1.1.1] - 2026-11-23

Versión de pulido visual y personalización. No incorpora funciones de negocio
nuevas: la contabilidad, la base de datos y los cálculos siguen siendo los mismos.

### Añadido

- Menú **Ajustes** en la cabecera y en el menú principal (atajo `Ctrl + ,`), con
  preferencias guardadas en `datos/config.json`, separadas de la base de datos.
- **Idioma**: español, inglés, alemán, ruso, chino, japonés, francés, portugués,
  italiano y coreano. La interfaz se reconstruye al cambiar de idioma y los
  valores internos de los combos siguen siendo canónicos.
- **Apariencia**: temas oscuro (predeterminado, con acento azul pastel), claro y
  «sistema», además de tres tamaños de texto.
- **Moneda**: selector de 10 monedas y formato de símbolo, código o sin símbolo,
  con vista previa. Solo cambia la presentación: los importes siguen guardados
  como enteros en centavos y no se convierten.
- **Opciones generales**: confirmación al eliminar y botón para restablecer
  preferencias.
- Iconos en las pestañas principales y en las secciones **Cobrar** / **Ventas**.

### Cambiado

- Encabezado más claro y agrupado, pestañas con icono, panels y tarjetas con
  bordes suaves, y espaciado más consistente en todas las vistas.
- Los temas se generan desde paletas centralizadas y se aplican en caliente al
  guardar Ajustes, sin reiniciar la app.
- Etiquetas de precio del catálogo («Desde», «Adicional desde», «por producto»)
  traducidas sin tocar los valores guardados.

[1.1.1]: https://github.com/thczt-dev/thc-contabilidad/releases/tag/v1.1.1

## [1.1.0] - 2026-11-21

### Añadido

- Pestaña **Cobros** con punto de venta en dos secciones: **Cobrar** y **Ventas**.
- **Cobrar**: catálogo editable en la misma página (crear, editar y borrar
  productos, servicios o paquetes), carrito con cantidades, descuento final en `%` o en
  `$`, impuesto configurable (atajos para 0, 5 y 19 %) y totales en vivo de
  subtotal, descuento, base, impuesto y total.
- Cada cobro se registra como un ingreso en `movimientos`, por lo que aparece
  igual en Resumen, Movimientos, Calendario y Reportes. Al eliminar una venta
  se quita también su ingreso.
- **Ventas**: histórico filtrable con detalle por item y exportación CSV.
- Atajo `Ctrl + Shift + V` y botón **Cobrar** en la cabecera.
- Tablas `productos`, `ventas` y `venta_items` en SQLite, con cálculos en
  centavos compartidos entre la interfaz y la base de datos.
- Catálogo inicial de 33 items (30 servicios y los paquetes *STARTER*,
  *BUSINESS* y *PROFESSIONAL*) con precios en COP, descripciones y etiquetas
  «Desde» / «Adicional desde» / «por producto». Los paquetes tienen un estilo
  visual más destacado y *BUSINESS* un distintivo discreto de «Recomendado».
- Campos `precio_etiqueta` y `destacado` en `productos`, editables desde el POS
  y con migración automática para bases existentes.

### Corregido

- Las tarjetas del catálogo del POS quedaban invisibles y no respondían al clic
  al entrar a **Cobros**: la vista se reconstruye después de mostrar la ventana
  y los widgets nuevos no se mostraban solos. Ahora cada tarjeta se muestra
  explícitamente al crearla.
- Los atajos y botones de navegación abrían pestañas equivocadas (Cobros y
  Reportes estaban desplazados en el orden del `Notebook`). Ahora se navega por
  referencia de vista.
- Los montos negativos ya no llegan a SQLite: se rechazan con un mensaje claro
  y el monto de movimientos debe ser mayor que cero.
- Los ingresos generados por una venta ya no se pueden editar ni borrar desde
  Movimientos, evitando que el balance y el histórico de ventas divergieran.
- La exportación CSV de Reportes ahora respeta el período seleccionado.
- `publicar.sh` falla con un mensaje claro si faltan las notas de la versión,
  en lugar de publicar por error las notas de v1.0.0.

[1.1.0]: https://github.com/thczt-dev/thc-contabilidad/releases/tag/v1.1.0

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

[1.0.0]: https://github.com/thczt-dev/thc-contabilidad/releases/tag/v1.0.0
