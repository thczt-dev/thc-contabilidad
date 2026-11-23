# THC Contabilidad

![Versión](https://img.shields.io/badge/versión-1.1.1-blue)
![Licencia](https://img.shields.io/badge/licencia-MIT-green)
![Plataforma](https://img.shields.io/badge/plataforma-Linux%20%7C%20Windows%20WIP-orange)

Programa de escritorio nativo para Linux y Windows que permite llevar un control sencillo de
**ingresos, gastos, proyectos pendientes, calendario, cobros (POS), contactos y
reportes**. Todo funciona sin internet: la información se guarda en una base de
datos SQLite local.

Moneda por defecto: **peso colombiano (COP)**. Puedes cambiarla desde
**Ajustes** (solo cambia la presentación; los importes siguen guardados en
centavos y nunca se convierten).

Interfaz: **modo oscuro moderno y minimalista**, con acento en azul pastel
(`#8ab4ff`) y espaciado amplio. Desde **Ajustes** puedes elegir también el tema
claro o seguir el tema del sistema, cambiar el tamaño del texto y elegir entre
10 idiomas. Los colores están centralizados en `thc_contabilidad/theme.py`.

## Descargas

La versión estable es **v1.1.1** (23 de noviembre de 2026): interfaz ordenada,
menú de Ajustes e idiomas. v1.1.0 añadió el punto de cobro y la v1.0.0 sigue
disponible para quien no necesite POS.
Los archivos de cada lanzamiento se publican en
[GitHub Releases](https://github.com/thczt-dev/thc-contabilidad/releases).
El historial de cambios está en [`CHANGELOG.md`](CHANGELOG.md).

### Windows (en preparación)

La versión de Windows se empaqueta con **MSYS2 + PyInstaller** y se distribuye
mediante un instalador visual creado con **Inno Setup**. Durante la instalación
puedes elegir idioma, tema, tamaño del texto, moneda, formato de importes y
confirmación al eliminar; esos valores se guardan en
`%APPDATA%\THC Contabilidad\config.json` y la app arranca ya configurada.
Todavía no hay release pública de Windows: el instalador se genera en GitHub
Actions como artefacto de CI hasta que se publique la primera versión.

La edición Windows será de **suscripción**: se activa con un archivo firmado,
sin conexión a internet. En **Licencia...** verás el estado de tu suscripción,
los días restantes y el código de máquina que debes enviar junto con tu clave
para recibir el archivo de activación. La edición Linux sigue siendo gratuita y
no pide licencia.

## Requisitos

- Linux con GTK 3 y Python 3.11 o superior.
- Paquetes del sistema: `python3-gi`, `gir1.2-gtk-3.0` (y `python3-cairo` para el gráfico).

  Debian/Ubuntu y derivados:

  ```bash
  sudo apt install python3-gi gir1.2-gtk-3.0 python3-cairo
  ```

  Arch Linux, Manjaro y otras distros base Arch:

  ```bash
  sudo pacman -S --needed gtk3 python-gobject python-cairo adwaita-icon-theme desktop-file-utils
  ```

  En base Arch, `python-gobject` aporta el módulo `gi` y `gtk3` incluye el
  typelib de GTK 3. `adwaita-icon-theme` asegura los iconos symbolic de la
  interfaz; `desktop-file-utils` permite actualizar el menú de aplicaciones.

- Windows 10 u 11 de 64 bits para el instalador. El paquete incluye el runtime
  GTK3, así que no hay que instalar MSYS2 ni Python por separado.
- No se necesita conexión a internet para usar la aplicación.

## Instalación fácil

### Opción A: un solo comando (recomendada)

Copia y pega esta línea en la terminal. Descarga el instalador, clona el
repositorio, comprueba las dependencias y crea el acceso directo:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/thczt-dev/thc-contabilidad/v1.1.1/instalar-github.sh)
```

El instalador guarda el código en `~/.local/share/thc-contabilidad`. Cuando
vuelvas a ejecutarlo, actualiza la instalación con `git pull`.

En Debian/Ubuntu instala las dependencias con `apt`; en Arch, Manjaro y otras
distros base Arch detecta `pacman` e instala `gtk3`, `python-gobject`,
`python-cairo`, `adwaita-icon-theme` y `desktop-file-utils`.

### Opción B: clonar manualmente

```bash
git clone --branch v1.1.1 https://github.com/thczt-dev/thc-contabilidad.git
cd thc-contabilidad
./instalar.sh
```

`instalar.sh` crea el acceso directo **THC Contabilidad** en el menú de
aplicaciones y copia el icono a `~/.local/share/icons/`. No necesita `sudo`.

Si el instalador detecta que faltan `python3-gi`, `gir1.2-gtk-3.0` o
`python3-cairo`, intenta instalarlos con `apt` (te pedirá la contraseña).
También puedes instalarlos antes:

```bash
sudo apt install python3-gi gir1.2-gtk-3.0 python3-cairo
```

### Personalizar la instalación

| Variable | Para qué | Valor por defecto |
|---|---|---|
| `THC_REPO_URL` | URL del repositorio a clonar | `https://github.com/thczt-dev/thc-contabilidad.git` |
| `THC_VERSION` | Etiqueta a instalar | `v1.1.1` |
| `THC_INSTALL_DIR` | Carpeta de destino | `~/.local/share/thc-contabilidad` |
| `THC_CONTABILIDAD_DB` | Ruta de la base de datos | `datos/contabilidad.db` dentro del proyecto |

Ejemplo:

```bash
THC_INSTALL_DIR="$HOME/Apps/thc-contabilidad" \
bash <(curl -fsSL https://raw.githubusercontent.com/thczt-dev/thc-contabilidad/v1.1.1/instalar-github.sh)
```

## Uso

Abre el programa de una de estas formas:

- Desde el menú de aplicaciones: **THC Contabilidad**.
- Desde la carpeta del proyecto: `./thc-contabilidad`
- Desde la terminal: `python3 -m thc_contabilidad.main`
- Para consultar la versión: `./thc-contabilidad --version`

## Ajustes

Pulsa el icono de engranaje de la cabecera (o `Ctrl + ,`) para personalizar la
app. Todo se guarda en `datos/config.json` y **no modifica la contabilidad**:

| Sección | Opciones |
|---|---|
| **Apariencia** | Tema oscuro, claro o según el sistema; tamaño del texto pequeño, normal o grande. |
| **Idioma** | Español, inglés, alemán, ruso, chino, japonés, francés, portugués, italiano y coreano. |
| **Moneda** | COP, USD, EUR, GBP, MXN, ARS, BRL, CLP, PEN y JPY, con formato de símbolo, código o sin símbolo y vista previa. |
| **Opciones generales** | Confirmación al eliminar y botón para restablecer preferencias. |

Cambiar de idioma reconstruye la ventana para que todos los textos se vean en
el idioma elegido. El tema y la moneda se aplican al guardar. Los importes
siempre se almacenan como enteros en centavos: elegir otra moneda **no** convierte
los valores, solo cambia cómo se muestran.

## Módulos

| Pestaña | Qué permite hacer |
|---|---|
| **Resumen** | Indicadores del mes, balance acumulado, últimos movimientos, próximos vencimientos y gráfico de ingresos vs. gastos. |
| **Movimientos** | Registrar ingresos y gastos con fecha, concepto, monto, categoría, contacto, método de pago y notas. Buscar, filtrar, editar y eliminar. |
| **Proyectos** | Crear proyectos con cliente, estado, prioridad, fechas y presupuesto. Marcar como completados y ver vencimientos. |
| **Calendario** | Vista mensual con puntos de color por día: ingresos, gastos, entregas e inicios de proyectos. Panel lateral con el detalle del día seleccionado y resumen del mes. |
| **Cobros** | Punto de cobro en dos pantallas: catálogo editable de productos, servicios y paquetes, carrito, descuento final en `%` o `$`, impuestos e histórico de ventas. Cada cobro se registra como ingreso en el resto de módulos. |
| **Contactos** | Directorio de clientes y proveedores con NIT, teléfono, correo y dirección. |
| **Reportes** | Balances por período, resumen mensual, distribución por categoría y exportación a CSV. |

## Atajos de teclado

- `Ctrl + N` — nuevo movimiento
- `Ctrl + P` — nuevo proyecto
- `Ctrl + Shift + C` — abrir calendario
- `Ctrl + Shift + V` — nuevo cobro (POS)
- `Ctrl + E` — exportar movimientos a CSV
- `Ctrl + ,` — abrir Ajustes
- `Ctrl + Q` — salir

## Punto de cobro (POS)

La pestaña **Cobros** tiene solo dos secciones:

1. **Cobrar** — una única pantalla con todo:
   - **Catálogo editable**: haz clic en una tarjeta para agregarla al carrito;
     usa ✎ para editarla o ✕ para borrarla. Abajo está el formulario para crear
     o modificar productos, servicios o paquetes (nombre, tipo, precio COP,
     categoría, disponibilidad y notas). También permite poner una etiqueta al
     precio («Desde», «por producto») y marcar un item como *Recomendado*.
   - **Carrito**: selecciona un item para cambiar su cantidad o quitarlo.
   - **Descuento al final**: elige `%` o `$` y escribe el valor. El panel muestra
     cuánto dinero dejaste de recibir.
   - **Impuesto**: escribe un porcentaje (hay atajos para 0, 5 y 19 %) y se
     calcula sobre la base ya descontada.
   - **Totales en vivo**: subtotal, descuento, base, impuesto y total a cobrar.
     Al pulsar **Cobrar** se guarda la venta y se crea automáticamente un
     ingreso en *Resumen*, *Movimientos*, *Calendario* y *Reportes*.
2. **Ventas** — histórico con filtros por fecha y búsqueda, detalle de los items,
   eliminación (que también quita el ingreso asociado del balance) y exportación
   a CSV con subtotal, descuento, base, impuesto y total.

Todos los cálculos se hacen en centavos, con el mismo código para la interfaz y
la base de datos, para que los totales nunca difieran.

### Catálogo inicial

Las bases nuevas se crean con 33 items listos para cobrar: 30 servicios
(páginas web, catálogos y comercio digital, sistemas y funcionalidades y
adicionales) y 3 paquetes (*STARTER*, *BUSINESS* y *PROFESSIONAL*). Los paquetes
tienen una tarjeta con más relieve que los servicios y *BUSINESS* lleva un
distintivo discreto de «Recomendado». Los precios que son «Desde» o «por
producto» conservan esa etiqueta en la tarjeta y en el editor. Todo se puede
editar o borrar; si tienes una base antigua, puedes cargar el catálogo sin
duplicados con:

```bash
python3 -c "from thc_contabilidad.db import Database; print(Database('datos/contabilidad.db').sembrar_catalogo_inicial())"
```

## Formato de montos

Puedes escribir los valores de varias formas; el programa los normaliza a COP:

- `1250000`
- `1.250.000`
- `1250.50`
- `$ 1.250,50`

## Datos y respaldo

La base de datos se crea automáticamente en:

| Sistema | Base de datos | Preferencias |
|---|---|---|
| Linux | `datos/contabilidad.db` dentro del proyecto | `datos/config.json` |
| Windows | `%APPDATA%\THC Contabilidad\contabilidad.db` | `%APPDATA%\THC Contabilidad\config.json` |

En Windows los datos van a `%APPDATA%` para que la app pueda instalarse en
`Program Files` sin permisos de escritura allí. El instalador escribe solo el
`config.json` inicial; la base de datos la crea la app al abrir.

Ese archivo **no se sube a GitHub** (está en `.gitignore`) porque contiene
información real. Para cambiar la ubicación de la base de datos, define
`THC_CONTABILIDAD_DB` antes de iniciar la app; para las preferencias,
`THC_CONTABILIDAD_CONFIG`.

Para hacer una copia de seguridad, basta con copiar ese archivo mientras la
aplicación esté cerrada. Los CSV exportados se guardan con codificación
`UTF-8 con BOM` y separador `;` para que abran correctamente en Excel.

## Estructura del proyecto

```
thc-contabilidad/
├── .github/workflows/ci.yml  # CI de Linux y build/smoke test de Windows
├── CHANGELOG.md              # historial de versiones
├── RELEASE_NOTES.md           # notas de la release v1.0.0
├── RELEASE_NOTES_v1.1.0.md    # notas de la release v1.1.0
├── RELEASE_NOTES_v1.1.1.md    # notas de la release v1.1.1
├── LICENSE                   # MIT
├── thc-contabilidad          # lanzador ejecutable de Linux
├── thc-contabilidad.desktop  # plantilla del acceso directo de Linux
├── thc-contabilidad.svg      # icono fuente
├── thc-contabilidad.png      # icono PNG incluido en la app
├── thc-contabilidad.ico      # icono Windows
├── instalar.sh               # instala lanzador e icono en ~/.local
├── instalar-github.sh        # clona, instala dependencias y crea el lanzador
├── publicar.sh               # crea el repo y publica la release con gh CLI
├── proyecto.json             # metadatos para el portafolio web
├── windows/                  # empaquetado Windows
│   ├── entrypoint.py         # entrada usada por PyInstaller
│   ├── thc-contabilidad.spec # especificación de PyInstaller
│   ├── build-windows.ps1     # compila el paquete y el instalador
│   ├── instalar-windows.iss  # asistente visual de Inno Setup
│   └── Output/               # instaladores generados (no se suben)
├── datos/                    # datos locales en Linux (no se suben)
│   ├── .gitkeep
│   ├── contabilidad.db       # base de datos SQLite
│   └── config.json           # preferencias: idioma, tema, moneda, etc.
└── thc_contabilidad/
    ├── __init__.py           # versión del paquete
    ├── rutas.py              # rutas de datos/recursos por sistema operativo
    ├── main.py               # aplicación y ventana principal
    ├── db.py                 # esquema y consultas SQLite
    ├── config.py             # preferencias y definiciones de tema/moneda/idioma
    ├── i18n.py               # traducción con respaldo al español
    ├── i18n_data.py          # textos traducidos a 10 idiomas
    ├── theme.py              # paletas oscura/clara y estilos GTK
    ├── utils.py              # formatos, montos y fechas
    ├── ui_helpers.py         # widgets reutilizables
    └── views/                # pestañas y diálogos de la interfaz
        ├── resumen.py
        ├── movimientos.py
        ├── proyectos.py
        ├── calendario.py     # vista mensual y detalle por día
        ├── cobros.py         # POS, catálogo editable, descuentos, impuestos y ventas
        ├── contactos.py
        ├── reportes.py
        └── ajustes.py        # preferencias personales
```

## Desarrollo

```bash
python3 -m compileall -q thc_contabilidad   # comprobar sintaxis
python3 -m thc_contabilidad.main            # ejecutar desde el código fuente
```

El flujo de CI de GitHub ejecuta la comprobación de sintaxis y valida
`proyecto.json` en cada push y pull request.

### Publicar una release

Con GitHub CLI autenticado (`gh auth login`), un solo comando sube el código,
empuja el tag y publica la release con las notas:

```bash
./publicar.sh                       # v1.1.1 por defecto
GH_VERSION=v1.2.0 ./publicar.sh     # otra versión, si existe su tag
```

Por defecto usa el repositorio `thc-contabilidad` bajo tu usuario. Para
crear otro con otra visibilidad:

```bash
GH_REPO=mi-contabilidad GH_VISIBILITY=private ./publicar.sh
```

## Solución de problemas

- **No abre desde el menú:** ejecuta `./instalar.sh` y cierra sesión/abre sesión.
- **Error al iniciar:** comprueba que `python3 -c "import gi"` funcione en la terminal.
- **En Arch/Manjaro falta `gi`:** instala `python-gobject` y `gtk3` con
  `sudo pacman -S --needed gtk3 python-gobject python-cairo`.
- **Quieres empezar de cero:** borra `datos/contabilidad.db` con la aplicación cerrada
  (en Windows, `%APPDATA%\THC Contabilidad\contabilidad.db`).

## Licencia

Distribuido bajo la [licencia MIT](LICENSE). Hecho por **ThcDev**.
