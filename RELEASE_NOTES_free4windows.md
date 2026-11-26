# THC Contabilidad 1.2.1 · free4windows

**Fecha:** 26 de noviembre de 2026

## Gratis también en Windows

Después de pensarlo mejor, la edición Windows pasa a ser **gratuita e idéntica
a la de Linux**. Se eliminaron por completo el sistema de suscripción, el
diálogo de activación, el generador de claves y todo el código asociado.
No hay claves, archivos firmados, límite de equipos ni control de caducidad.
Tampoco se necesita internet.

## Novedades pequeñas de esta versión

- `Ctrl + 1 … 7` para saltar entre las siete pestañas sin usar el ratón.
- `Ctrl + F` enfoca directamente el buscador de **Movimientos**.
- Nuevo diálogo **Atajos de teclado** (`Ctrl + F1`) dentro del menú de la app.
- El asistente de instalación de Windows menciona que la app es gratuita.

## Descarga

- Windows: **[THC-Contabilidad-1.2.1-Windows.exe](https://github.com/thczt-dev/thc-contabilidad/releases/download/free4windows/THC-Contabilidad-1.2.1-Windows.exe)**
- Linux: instalación en un comando:

  ```bash
  bash <(curl -fsSL https://raw.githubusercontent.com/thczt-dev/thc-contabilidad/free4windows/instalar-github.sh)
  ```

  O clonar `git clone --branch free4windows https://github.com/thczt-dev/thc-contabilidad.git`.

## Instalación en Windows

Ejecuta el instalador. La página de **Preferencias iniciales** elige idioma,
tema, tamaño del texto, moneda, formato de importes y confirmación al eliminar.
Solo escribe `%APPDATA%\THC Contabilidad\config.json`; la base de datos se crea
sola al abrir la aplicación. No hay ningún paso adicional.

## Detalles

- SQLite local con importes guardados como enteros en centavos.
- Los datos se guardan en `%APPDATA%\THC Contabilidad\` en Windows y en `datos/`
  en Linux; nunca se suben al repositorio.
- El código fuente se distribuye bajo [MIT](LICENSE).
