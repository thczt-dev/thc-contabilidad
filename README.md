# THC Contabilidad

![Versión](https://img.shields.io/badge/versión-1.2.1-blue)
![Código](https://img.shields.io/badge/código-MIT-green)
![Plataforma](https://img.shields.io/badge/plataforma-Linux%20%7C%20Windows-brightgreen)
![Windows](https://img.shields.io/badge/Windows-gratuito-brightgreen)

Programa de escritorio nativo para Linux y Windows que permite llevar un control sencillo de
**ingresos, gastos, proyectos pendientes, calendario, cobros (POS), contactos y
reportes**. Todo funciona sin internet: la información se guarda en una base de
datos SQLite local. **Es gratuito en los dos sistemas, sin claves ni registros.**

Moneda por defecto: **peso colombiano (COP)**. Puedes cambiarla desde
**Ajustes** (solo cambia la presentación; los importes siguen guardados en
centavos y nunca se convierten).

Interfaz: **modo oscuro moderno y minimalista**, con acento en azul pastel
(`#8ab4ff`) y espaciado amplio. Desde **Ajustes** puedes elegir también el tema
claro o seguir el tema del sistema, cambiar el tamaño del texto y elegir entre
10 idiomas. Los colores están centralizados en `thc_contabilidad/theme.py`.

## Descargas

La versión estable es **1.2.1** (26 de noviembre de 2026), publicada con la
etiqueta **`free4windows`**. Windows pasa a ser gratuita como Linux: se eliminó
por completo el sistema de suscripción y sus herramientas. Además, esta versión
añade atajos `Ctrl + 1 … 7` para cambiar de pestaña, un diálogo **Atajos de
teclado** y `Ctrl + F` para ir al buscador de movimientos.

Los archivos de cada lanzamiento se publican en
[GitHub Releases](https://github.com/thczt-dev/thc-contabilidad/releases).
Los paquetes de Windows se llaman `THC-Contabilidad-<versión>-Windows.exe` y los
genera automáticamente GitHub Actions. El historial de cambios está en
[`CHANGELOG.md`](CHANGELOG.md).

### Windows

Descarga `THC-Contabilidad-1.2.1-Windows.exe` de la
[release `free4windows`](https://github.com/thczt-dev/thc-contabilidad/releases/tag/free4windows)
y ejecútalo. La edición Windows se empaqueta con **MSYS2 + PyInstaller** y se
distribuye mediante un instalador visual creado con **Inno Setup**. Durante la
instalación puedes elegir idioma, tema, tamaño del texto, moneda, formato de
importes y confirmación al eliminar; esos valores se guardan en
`%APPDATA%\THC Contabilidad\config.json` y la app arranca ya configurada.
No pide activación, clave, archivo firmado ni conexión a internet.

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

### Windows

Descarga `THC-Contabilidad-1.2.1-Windows.exe` desde la
[release `free4windows`](https://github.com/thczt-dev/thc-contabilidad/releases/tag/free4windows)
y ejecútalo. El asistente de Inno Setup pregunta por idioma, tema, tamaño del
texto, moneda, formato de importes y confirmación al eliminar antes del primer
arranque. No necesitas terminal ni ningún paso extra.

### Linux

#### Opción A: un solo comando (recomendada)

Copia y pega esta línea en la terminal. Descarga el instalador, clona el
repositorio, comprueba las dependencias, crea el acceso directo y abre el
**asistente gráfico de preferencias** al terminar:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/thczt-dev/thc-contabilidad/free4windows/instalar-github.sh)
```

El instalador guarda el código en `~/.local/share/thc-contabilidad`. Cuando
vuelvas a ejecutarlo, actualiza la instalación con `git pull`.

En Debian/Ubuntu instala las dependencias con `apt`; en Arch, Manjaro y otras
distros base Arch detecta `pacman` e instala `gtk3`, `python-gobject`,
`python-cairo`, `adwaita-icon-theme` y `desktop-file-utils`.

#### Opción B: clonar manualmente

```bash
git clone --branch free4windows https://github.com/thczt-dev/thc-contabilidad.git
cd thc-contabilidad
./instalar.sh
```

`instalar.sh` crea el acceso directo **THC Contabilidad** en el menú de
aplicaciones, copia el icono a `~/.local/share/icons/` y abre el asistente
gráfico de preferencias. No necesita `sudo`. Si omites el asistente, aparece de
nuevo en el primer arranque de la app. Para abrirlo más tarde:

```bash
python3 -m thc_contabilidad.asistente
```

Si el instalador detecta que faltan `python3-gi`, `gir1.2-gtk-3.0` o
`python3-cairo`, intenta instalarlos con `apt` (te pedirá la contraseña).
También puedes instalarlos antes:

```bash
sudo apt install python3-gi gir1.2-gtk-3.0 python3-cairo
```

#### Personalizar la instalación

| Variable | Para qué | Valor por defecto |
|---|---|---|
| `THC_REPO_URL` | URL del repositorio a clonar | `https://github.com/thczt-dev/thc-contabilidad.git` |
| `THC_VERSION` | Etiqueta a instalar | `free4windows` |
| `THC_INSTALL_DIR` | Carpeta de destino | `~/.local/share/thc-contabilidad` |
| `THC_CONTABILIDAD_DB` | Ruta de la base de datos | `datos/contabilidad.db` dentro del proyecto |
| `THC_SIN_ASISTENTE` | Ponlo a `1` para no abrir el asistente al instalar | `0` |

Ejemplo:

```bash
THC_INSTALL_DIR="$HOME/Apps/thc-contabilidad" \
bash <(curl -fsSL https://raw.githubusercontent.com/thczt-dev/thc-contabilidad/free4windows/instalar-github.sh)
```

## Uso

Abre el programa de una de estas formas:

- Desde el menú de aplicaciones: **THC Contabilidad** (en Windows también desde
  el menú Inicio o el escritorio, según lo elegido al instalar).
- Desde la carpeta del proyecto en Linux: `./thc-contabilidad`
- Desde la terminal: `python3 -m thc_contabilidad.main`
- Para consultar la versión: `./thc-contabilidad --version`

Si aún no elegiste preferencias, aparece el asistente inicial. En Windows esas
mismas preferencias se piden al instalar.

## Ajustes

Pulsa el icono de engranaje de la cabecera (o `Ctrl + ,`) para personalizar la
app. Todo se guarda en `datos/config.json` en Linux y en
`%APPDATA%\THC Contabilidad\config.json` en Windows, y **no modifica la
contabilidad**. Estas mismas opciones se eligen al instalar: en Windows en el
asistente de Inno Setup y en Linux en el asistente gráfico que se abre tras la
instalación o en el primer arranque:

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

## Gratuito en Linux y Windows

Las dos ediciones son gratuitas y funcionan igual: no hay suscripción, claves de
activación, archivos firmados, límite de equipos ni comprobaciones de fecha.
Tampoco se envía nada a internet: los datos se quedan en tu computadora.
El código fuente está disponible bajo [MIT](LICENSE).

## Módulos

| Pestaña | Qué permite hacer |
|---|---|
| **Resumen** | Indicadores del mes, balance acumulado, últimos movimientos, próximos vencimientos y gráfico de ingresos vs. gastos. |
| **Movimientos** | Registrar ingresos y gastos con fecha, concepto, monto, categoría, contacto, método de pago y notas. Buscar (`Ctrl + F`), filtrar, editar y eliminar. |
| **Proyectos** | Crear proyectos con cliente, estado, prioridad, fechas y presupuesto. Marcar como completados y ver vencimientos. |
| **Calendario** | Vista mensual con puntos de color por día: ingresos, gastos, entregas e inicios de proyectos. Panel lateral con el detalle del día seleccionado y resumen del mes. |
| **Cobros** | Punto de cobro en dos pantallas: catálogo editable de productos, servicios y paquetes, carrito, descuento final en `%` o `$`, impuestos e histórico de ventas. Cada cobro se registra como ingreso en el resto de módulos. |
| **Contactos** | Directorio de clientes y proveedores con NIT, teléfono, correo y dirección. |
| **Reportes** | Balances por período, resumen mensual, distribución por categoría y exportación a CSV. |

## Atajos de teclado

Pulsa `Ctrl + F1` o abre **Atajos de teclado** desde el menú para ver esta lista
dentro de la aplicación.

- `Ctrl + 1 … 7` — ir a Resumen, Movimientos, Proyectos, Calendario, Cobros, Contactos o Reportes
- `Ctrl + F` — enfocar el buscador de Movimientos
- `Ctrl + N` — nuevo movimiento
- `Ctrl + P` — nuevo proyecto
- `Ctrl + Shift + C` — abrir calendario
- `Ctrl + Shift + V` — nuevo cobro (POS)
- `Ctrl + E` — exportar movimientos a CSV
- `Ctrl + ,` — abrir Ajustes
- `Ctrl + F1` — ver los atajos en la aplicación
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
`Program Files` sin permisos de escritura allí. El instalador (o el asistente
gráfico en Linux) escribe solo el `config.json` inicial; la base de datos la
crea la app al abrir. Ningún archivo de datos se sube a GitHub: están excluidos
en `.gitignore` porque contienen información real. Para cambiar la ubicación de
la base de datos, define `THC_CONTABILIDAD_DB` antes de iniciar la app; para las
preferencias, `THC_CONTABILIDAD_CONFIG`.

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
├── RELEASE_NOTES_free4windows.md # notas de la release 1.2.1
├── LICENSE                   # MIT
├── thc-contabilidad          # lanzador ejecutable de Linux
├── thc-contabilidad.desktop  # plantilla del acceso directo de Linux
├── thc-contabilidad.svg      # icono fuente
├── thc-contabilidad.png      # icono PNG incluido en la app
├── thc-contabilidad.ico      # icono Windows
├── instalar.sh               # lanzador, icono y asistente inicial en ~/.local
├── instalar-github.sh        # clona, instala dependencias y abre el asistente
├── publicar.sh               # crea la repo y publica la release con gh CLI
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
    ├── asistente.py          # asistente gráfico de preferencias iniciales
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
        ├── ajustes.py        # preferencias personales
        └── atajos.py         # diálogo con los atajos de teclado
```

## Desarrollo

```bash
python3 -m compileall -q thc_contabilidad   # comprobar sintaxis
python3 -m thc_contabilidad.main            # ejecutar desde el código fuente
python3 -m thc_contabilidad.asistente       # volver a abrir el asistente inicial
```

El flujo de CI de GitHub ejecuta la comprobación de sintaxis, valida
`proyecto.json` y compila el instalador de Windows en cada push y pull request.

### Publicar una release

Con GitHub CLI autenticado (`gh auth login`), un solo comando sube el código,
empuja la etiqueta y publica la release con las notas:

```bash
./publicar.sh                       # free4windows por defecto
GH_VERSION=otra-etiqueta ./publicar.sh
```

El workflow de Windows compila el instalador, ejecuta el smoke test y lo adjunta
a la release cuando se empuja una etiqueta. Si la release ya existe (por
ejemplo, porque la creó `publicar.sh`), CI reemplaza el instalador adjunto.
El título de la release y el nombre del instalador salen de `__version__`, así
que la etiqueta puede tener un nombre distinto a la versión.

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
- **No apareció el asistente al instalar:** ejecuta
  `python3 -m thc_contabilidad.asistente` desde la carpeta de instalación.

## Código abierto

El código se distribuye bajo la [licencia MIT](LICENSE). Hecho por **ThcDev**.
Linux y Windows son gratuitas, sin restricciones de uso.
