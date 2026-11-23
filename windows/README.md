# Compilación de Windows

El instalador de la versión 1.2.0 se publica en
[GitHub Releases](https://github.com/thczt-dev/thc-contabilidad/releases/latest)
como `THC-Contabilidad-1.2.0-Windows.exe`. La versión también se genera en
GitHub Actions, y puedes compilarla en local.

## Requisitos

1. MSYS2 con el entorno **MINGW64**:

   ```bash
   pacman -S --needed \
     mingw-w64-x86_64-gtk3 \
     mingw-w64-x86_64-python \
     mingw-w64-x86_64-python-gobject \
     mingw-w64-x86_64-python-cairo \
     mingw-w64-x86_64-pyinstaller \
     mingw-w64-x86_64-pyinstaller-hooks-contrib \
     mingw-w64-x86_64-python-cryptography
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

## Licencias

La edición empaquetada exige licencia; la ejecución desde código fuente en
Linux no. El flujo es:

1. El usuario abre **Licencia...** en el menú y copia su código de máquina.
2. Con su clave y ese código, ejecutas
   `python licencias/generar.py activar --clave ... --codigo ...`.
3. Envías el `license.json` generado; el usuario lo carga desde el diálogo.

También puedes hacerlo desde el generador gráfico del editor:
`./licencias/generador-licencias` (o instala el acceso directo con
`./licencias/instalar-generador.sh`).

El registro `licencias/activaciones.json` controla el máximo de equipos por
clave. La clave privada `licencias/private_key.pem` y ese registro están en
`.gitignore`: **no los subas**. Si regeneras las claves, actualiza
`CLAVE_PUBLICA_PEM` en `thc_contabilidad/licencia.py` y recompila.
