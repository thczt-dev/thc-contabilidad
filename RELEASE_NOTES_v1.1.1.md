# THC Contabilidad v1.1.1

Versión de **pulido visual y personalización**. No añade funciones de negocio
nuevas: la contabilidad, la base de datos y los cálculos son idénticos a la
v1.1.0. Si vienes de la v1.1.0, basta con actualizar el código; tus datos no se
tocan.

## Novedades

- **Menú de Ajustes** nuevo, accesible desde el engranaje de la cabecera, desde
  el menú principal o con `Ctrl + ,`:
  - **Apariencia**: tema oscuro (el de siempre, con acento azul pastel), tema
    claro y opción de seguir el tema del sistema. También tamaño de texto
    pequeño, normal o grande.
  - **Idioma**: español, inglés, alemán, ruso, chino, japonés, francés,
    portugués, italiano y coreano. La ventana se reconstruye al guardar para que
    todos los textos cambien a la vez.
  - **Moneda**: COP, USD, EUR, GBP, MXN, ARS, BRL, CLP, PEN y JPY, con formato
    de símbolo, código o sin símbolo y una vista previa antes de guardar.
  - **Opciones generales**: confirmación al eliminar y botón para restablecer
    preferencias.
- **Interfaz más ordenada y amigable**: encabezado agrupado, pestañas con icono,
  paneles y tarjetas con bordes suaves, espaciado más consistente y textos
  secundarios más legibles.
- Los temas se aplican **en caliente** al guardar, sin reiniciar la app.
- Las etiquetas comerciales del catálogo («Desde», «Adicional desde»,
  «por producto») se traducen sin modificar los valores guardados.

## Tus datos siguen igual

Las preferencias se guardan en `datos/config.json`, un archivo **separado** de
`datos/contabilidad.db`. Cambiar idioma, tema o moneda nunca escribe en la base
de datos. Los importes continúan almacenándose como enteros en centavos: elegir
otra moneda **solo cambia cómo se muestran**, no los convierte ni los altera.
Tanto `config.json` como la base de datos siguen excluidos de GitHub.

## Compatibilidad

No hay migraciones de base de datos. Las bases creadas con v1.0.0 o v1.1.0 se
abren directamente. Si no existe `config.json`, la app usa los valores por
defecto: español, tema oscuro, tamaño normal, COP con símbolo y confirmación al
eliminar activada.

## Instalación

Si ya tienes la v1.1.0, ejecuta el instalador otra vez para actualizar:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/thczt-dev/thc-contabilidad/v1.1.1/instalar-github.sh)
```

Instalación nueva:

```bash
git clone --branch v1.1.1 https://github.com/thczt-dev/thc-contabilidad.git
cd thc-contabilidad
./instalar.sh
```

Cambios completos: [`CHANGELOG.md`](CHANGELOG.md).
