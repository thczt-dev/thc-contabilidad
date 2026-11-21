# THC Contabilidad v1.1.0

Nueva versión con **punto de cobro (POS)** rediseñado. Mantiene todas las
funciones de la v1.0.0.

## Novedades

- **Pestaña Cobros** con solo dos secciones: **Cobrar** y **Ventas**.
- **Cobrar** reúne todo en una pantalla:
  - Catálogo editable: clic para agregar, ✎ para editar, ✕ para borrar y un
    formulario para crear productos, servicios o paquetes (nombre, tipo, precio
    COP, categoría, disponibilidad y notas).
  - Carrito con cantidades ajustables.
  - **Descuento al final**, en porcentaje (`%`) o valor fijo en pesos (`$`),
    con el monto exacto que dejaste de recibir.
  - **Impuesto** configurable (atajos para 0 %, 5 % y 19 %), aplicado sobre la
    base ya descontada.
  - Totales en vivo: subtotal, descuento, base, impuesto y total a cobrar.
- **Ventas**: histórico filtrable, detalle de items, eliminación y exportación
  a CSV con el desglose completo.
- Cada cobro crea **automáticamente un ingreso** en Movimientos, por lo que se
  refleja igual en Resumen, Calendario y Reportes. Borrar una venta quita también
  su ingreso, sin dejar el balance alterado.
- Los cálculos se hacen en **centavos** con una sola función compartida por la
  interfaz y la base de datos, así que los totales nunca difieren.
- **Catálogo inicial** de 33 items: 30 servicios organizados por categorías
  (páginas web, catálogos y comercio digital, sistemas y funcionalidades y
  adicionales) más los paquetes **STARTER** ($90.000), **BUSINESS** ($160.000)
  y **PROFESSIONAL** ($250.000), con sus descripciones y precios en COP.
- Los **paquetes** se muestran con una tarjeta más destacada que los servicios;
  **BUSINESS** lleva un pequeño distintivo de «Recomendado». Los precios
  «Desde», «Adicional desde» y «por producto» mantienen su etiqueta visible.
- Botón **Cobrar** en la cabecera y atajo `Ctrl+Shift+V`.
- Nuevas tablas SQLite: `productos`, `ventas` y `venta_items`, con migración
  automática de bases existentes.

## Compatibilidad

La base de datos se actualiza sola al abrir la aplicación: se agregan las
columnas nuevas de descuento, impuesto y catálogo sin perder los datos
anteriores. El catálogo inicial solo se siembra en bases nuevas; en una
instalación existente se puede cargar sin duplicados con
`Database(ruta).sembrar_catalogo_inicial()`.

## Instalación

Si ya tienes la v1.0.0, ejecuta el instalador otra vez para actualizar:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/thczt-dev/thc-contabilidad/v1.1.0/instalar-github.sh)
```

Instalación nueva:

```bash
git clone --branch v1.1.0 https://github.com/thczt-dev/thc-contabilidad.git
cd thc-contabilidad
./instalar.sh
```

Cambios completos: [`CHANGELOG.md`](CHANGELOG.md).
