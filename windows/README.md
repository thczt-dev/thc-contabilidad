# Compilación de Windows

La versión de Windows se genera en GitHub Actions, pero también puedes hacerlo
en local.

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

El asistente de Inno Setup incluye una página de **Preferencias iniciales**.
Solo escribe `config.json` si no existe o si se marca la tarea *Restablecer
preferencias iniciales*. La base de datos nunca se reemplaza al reinstalar ni
se borra al desinstalar.

La futura activación por licencia de Windows se añadirá a este mismo
instalador; todavía no hay ningún sistema de licencias en esta rama.
