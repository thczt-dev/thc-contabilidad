# THC Contabilidad

![Versión](https://img.shields.io/badge/versión-1.0.0-blue)
![Licencia](https://img.shields.io/badge/licencia-MIT-green)
![Plataforma](https://img.shields.io/badge/plataforma-Linux-orange)

Programa de escritorio nativo para Linux que permite llevar un control sencillo de
**ingresos, gastos, proyectos pendientes, calendario, contactos y reportes**. Todo
funciona sin internet: la información se guarda en una base de datos SQLite local.

Moneda configurada: **peso colombiano (COP)**.

Interfaz: **modo oscuro moderno y minimalista**, con acento en azul pastel y
espaciado amplio. Los colores están centralizados en `thc_contabilidad/theme.py`,
así que el aspecto no depende del tema del sistema.

## Descargas

La versión estable es **v1.0.0** (21 de noviembre de 2026).
Los binarios/archivos de cada lanzamiento se publican en
[GitHub Releases](https://github.com/ThcDev/thc-contabilidad/releases).
El historial de cambios está en [`CHANGELOG.md`](CHANGELOG.md).

## Requisitos

- Linux con GTK 3 y Python 3.11 o superior.
- Paquetes del sistema: `python3-gi`, `gir1.2-gtk-3.0` (y `python3-cairo` para el gráfico).
  En Debian/Ubuntu:

  ```bash
  sudo apt install python3-gi gir1.2-gtk-3.0 python3-cairo
  ```

- No se necesita conexión a internet para usar la aplicación.

## Instalación fácil

### Opción A: un solo comando (recomendada)

Copia y pega esta línea en la terminal. Descarga el instalador, clona el
repositorio, comprueba las dependencias y crea el acceso directo:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/ThcDev/thc-contabilidad/v1.0.0/instalar-github.sh)
```

El instalador guarda el código en `~/.local/share/thc-contabilidad`. Cuando
vuelvas a ejecutarlo, actualiza la instalación con `git pull`.

### Opción B: clonar manualmente

```bash
git clone https://github.com/ThcDev/thc-contabilidad.git
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
| `THC_REPO_URL` | URL del repositorio a clonar | `https://github.com/ThcDev/thc-contabilidad.git` |
| `THC_VERSION` | Etiqueta a instalar | `v1.0.0` |
| `THC_INSTALL_DIR` | Carpeta de destino | `~/.local/share/thc-contabilidad` |
| `THC_CONTABILIDAD_DB` | Ruta de la base de datos | `datos/contabilidad.db` dentro del proyecto |

Ejemplo:

```bash
THC_INSTALL_DIR="$HOME/Apps/thc-contabilidad" \
bash <(curl -fsSL https://raw.githubusercontent.com/ThcDev/thc-contabilidad/v1.0.0/instalar-github.sh)
```

## Uso

Abre el programa de una de estas formas:

- Desde el menú de aplicaciones: **THC Contabilidad**.
- Desde la carpeta del proyecto: `./thc-contabilidad`
- Desde la terminal: `python3 -m thc_contabilidad.main`
- Para consultar la versión: `./thc-contabilidad --version`

## Módulos

| Pestaña | Qué permite hacer |
|---|---|
| **Resumen** | Indicadores del mes, balance acumulado, últimos movimientos, próximos vencimientos y gráfico de ingresos vs. gastos. |
| **Movimientos** | Registrar ingresos y gastos con fecha, concepto, monto, categoría, contacto, método de pago y notas. Buscar, filtrar, editar y eliminar. |
| **Proyectos** | Crear proyectos con cliente, estado, prioridad, fechas y presupuesto. Marcar como completados y ver vencimientos. |
| **Calendario** | Vista mensual con puntos de color por día: ingresos, gastos, entregas e inicios de proyectos. Panel lateral con el detalle del día seleccionado y resumen del mes. |
| **Contactos** | Directorio de clientes y proveedores con NIT, teléfono, correo y dirección. |
| **Reportes** | Balances por período, resumen mensual, distribución por categoría y exportación a CSV. |

## Atajos de teclado

- `Ctrl + N` — nuevo movimiento
- `Ctrl + P` — nuevo proyecto
- `Ctrl + Shift + C` — abrir calendario
- `Ctrl + E` — exportar movimientos a CSV
- `Ctrl + Q` — salir

## Formato de montos

Puedes escribir los valores de varias formas; el programa los normaliza a COP:

- `1250000`
- `1.250.000`
- `1250.50`
- `$ 1.250,50`

## Datos y respaldo

La base de datos se crea automáticamente en:

```
datos/contabilidad.db
```

Ese archivo **no se sube a GitHub** (está en `.gitignore`) porque contiene
información real. Para cambiar la ubicación, define la variable de entorno
`THC_CONTABILIDAD_DB` con la ruta deseada antes de iniciar la app.

Para hacer una copia de seguridad, basta con copiar ese archivo mientras la
aplicación esté cerrada. Los CSV exportados se guardan con codificación
`UTF-8 con BOM` y separador `;` para que abran correctamente en Excel.

## Estructura del proyecto

```
thc-contabilidad/
├── .github/workflows/ci.yml  # verificación de sintaxis en GitHub Actions
├── CHANGELOG.md              # historial de versiones
├── RELEASE_NOTES.md           # notas de la release v1.0.0
├── LICENSE                   # MIT
├── thc-contabilidad          # lanzador ejecutable
├── thc-contabilidad.desktop  # plantilla del acceso directo
├── thc-contabilidad.svg      # icono
├── instalar.sh               # instala lanzador e icono en ~/.local
├── instalar-github.sh        # clona, instala dependencias y crea el lanzador
├── publicar.sh               # crea el repo y la release v1.0.0 con gh CLI
├── proyecto.json             # metadatos para el portafolio web
├── datos/                    # base de datos SQLite (se crea sola)
│   └── .gitkeep
└── thc_contabilidad/
    ├── __init__.py           # versión del paquete
    ├── main.py               # aplicación y ventana principal
    ├── db.py                 # esquema y consultas SQLite
    ├── theme.py              # paleta oscura y estilos GTK
    ├── utils.py              # formatos, montos y fechas
    ├── ui_helpers.py         # widgets reutilizables
    └── views/                # pestañas de la interfaz
        ├── resumen.py
        ├── movimientos.py
        ├── proyectos.py
        ├── calendario.py     # vista mensual y detalle por día
        ├── contactos.py
        └── reportes.py
```

## Desarrollo

```bash
python3 -m compileall -q thc_contabilidad   # comprobar sintaxis
python3 -m thc_contabilidad.main            # ejecutar desde el código fuente
```

El flujo de CI de GitHub ejecuta la comprobación de sintaxis y valida
`proyecto.json` en cada push y pull request.

### Publicar la release v1.0.0

Con GitHub CLI autenticado (`gh auth login`), un solo comando crea el
repositorio, sube el código, empuja el tag y publica la release con las notas:

```bash
./publicar.sh
```

Por defecto crea `thc-contabilidad` público bajo tu usuario. Para cambiarlo:

```bash
GH_REPO=mi-contabilidad GH_VISIBILITY=private ./publicar.sh
```

Las URLs de ejemplo de este README usan `ThcDev` como propietario; si tu
usuario es otro, reemplázalo al clonar.

## Solución de problemas

- **No abre desde el menú:** ejecuta `./instalar.sh` y cierra sesión/abre sesión.
- **Error al iniciar:** comprueba que `python3 -c "import gi"` funcione en la terminal.
- **Quieres empezar de cero:** borra `datos/contabilidad.db` con la aplicación cerrada.

## Licencia

Distribuido bajo la [licencia MIT](LICENSE). Hecho por **ThcDev**.
