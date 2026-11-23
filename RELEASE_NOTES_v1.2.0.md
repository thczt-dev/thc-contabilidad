# THC Contabilidad v1.2.0

Primera versión con **instalador de Windows**. La edición Linux sigue siendo
gratuita y se instala igual que en v1.1.1; la edición Windows es de suscripción
y se activa sin conexión a internet.

## Windows

Descarga **`THC-Contabilidad-1.2.0-Windows.exe`** de esta release y ejecútalo.
Requiere Windows 10 u 11 de 64 bits. El paquete incluye el runtime GTK3, así que
no hay que instalar Python ni MSYS2 por separado.

El asistente permite elegir idioma, tema, tamaño del texto, moneda, formato de
importes y confirmación al eliminar antes del primer arranque. Los datos y las
preferencias se guardan en `%APPDATA%\THC Contabilidad\`.

### Activación

1. Abre **Licencia...** en el menú de la app.
2. Copia el **código de máquina** y envíalo junto con tu clave de suscripción.
3. Recibe el archivo `license.json` firmado y cárgalo desde el mismo diálogo.

La suscripción muestra los días restantes y limita automáticamente el número de
equipos por clave. Sin licencia activa la edición Windows no arranca.

## Linux

Sin cambios funcionales respecto a v1.1.1. Puedes actualizar con:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/thczt-dev/thc-contabilidad/v1.2.0/instalar-github.sh)
```

o clonar la etiqueta `v1.2.0`. La edición Linux no pide licencia. Tras la
instalación se abre un **asistente gráfico** para elegir idioma, tema, tamaño
del texto, moneda, formato y confirmación al eliminar; si se omite, aparece en
el primer arranque. Puedes volver a abrirlo con
`python3 -m thc_contabilidad.asistente`.

## Cambios

- Empaquetado Windows con MSYS2 + PyInstaller e instalador visual con Inno Setup.
- Rutas de datos en `%APPDATA%\THC Contabilidad\` e iconos propios PNG/ICO.
- Licencia por suscripción offline con firma Ed25519, huella de equipo, control
  de caducidad, reloj y límite de activaciones.
- Diálogo **Licencia...** y herramientas para el editor: `licencias/generar.py`,
  generador gráfico y su acceso directo.
- Instrucciones de instalación para Debian/Ubuntu y distros base Arch.

El detalle completo está en [`CHANGELOG.md`](CHANGELOG.md).
