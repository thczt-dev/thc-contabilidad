# Compilación de Windows

El instalador de la versión 1.2.1 se publica en
[GitHub Releases](https://github.com/thczt-dev/thc-contabilidad/releases/tag/free4windows)
como `THC-Contabilidad-1.2.1-Windows.exe`, dentro de la release etiquetada
`free4windows`. La edición Windows es **gratuita**: no lleva activación ni
comprobaciones de licencia. La versión también se genera en GitHub Actions y
puedes compilarla en local.

## Requisitos

1. MSYS2 con el entorno **MINGW64**:

   ```bash
   pacman -S --needed \
     mingw-w64-x86_64-gtk3 \
     mingw-w64-x86_64-python \
     mingw-w64-x86_64-python-gobject \
     mingw-w64-x86_64-python-cairo \
     mingw-w64-x86_64-pyinstaller \
     mingw-w64-x86_64-pyinstaller-hooks-contrib
   ```

2. [Inno Setup 6](https://jrsoftware.org/isinfo.php) para crear el instalador.

## Compilar

Desde PowerShell, en la raíz del repositorio:

```powershell
$env:MSYSTEM_PREFIX = 'C:\msys64\mingw64'
.\windows\build-windows.ps1 -Installer
```

El script:

1. comprueba GTK3 y PyInstaller;
2. ejecuta `windows/thc-contabilidad.spec`;
3. compila los esquemas GLib;
4. regenera `lib/gdk-pixbuf-2.0/2.10.0/loaders.cache` con rutas relativas;
5. crea `windows/Output/THC-Contabilidad-<version>-Windows.exe`.

Si `MSYSTEM_PREFIX` no está definido, se usa `C:\msys64\mingw64`. También
puedes pasar `-Prefix 'D:\msys64\mingw64'`.

## Probar el paquete

```powershell
$env:THC_CONTABILIDAD_DB = "$env:TEMP\thc-smoke\contabilidad.db"
$env:THC_CONTABILIDAD_CONFIG = "$env:TEMP\thc-smoke\config.json"
.\dist\thc-contabilidad\thc-contabilidad-diag.exe --smoke-test
```

El smoke test crea la base en una ruta temporal, escribe el JSON de
preferencias, comprueba que el icono esté incluido e inicializa GTK sin abrir
la ventana.

## Instalador

El asistente de Inno Setup incluye una página de **Preferencias iniciales** y
deja claro que la aplicación es gratuita. Solo escribe `config.json` si no
existe o si se marca la tarea *Restablecer preferencias iniciales*. La base de
datos nunca se reemplaza al reinstalar ni se borra al desinstalar.

## Release

El workflow `.github/workflows/ci.yml` publica el instalador cuando se empuja
una etiqueta. La etiqueta de esta versión es `free4windows`, distinta del número
de versión: CI lee `1.2.1` de `thc_contabilidad/__init__.py` para el título y
usa `RELEASE_NOTES_free4windows.md` como notas.
