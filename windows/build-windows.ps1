param(
    [switch]$Installer,
    [string]$Prefix
)

$ErrorActionPreference = 'Stop'

$Proyecto = Split-Path -Parent $PSScriptRoot
$Especificacion = Join-Path $PSScriptRoot 'thc-contabilidad.spec'
$Dist = Join-Path $Proyecto 'dist\thc-contabilidad'

if (-not $Prefix) {
    $Prefix = $env:MSYSTEM_PREFIX
}
if (-not $Prefix) {
    $RaizMsys = $env:MSYSTEM_ROOT
    if (-not $RaizMsys) { $RaizMsys = 'C:\msys64' }
    $Prefix = Join-Path $RaizMsys 'mingw64'
}

if (-not (Test-Path $Prefix)) {
    throw "No se encontró MSYS2 en $Prefix. Define -Prefix o MSYSTEM_PREFIX."
}

$Python = Join-Path $Prefix 'python.exe'
if (-not (Test-Path $Python)) {
    throw "No se encontró python.exe dentro de $Prefix."
}

$env:MSYSTEM_PREFIX = $Prefix
$env:PATH = "$Prefix\bin;$env:PATH"
Write-Host "Usando MSYS2: $Prefix"

& $Python -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; import PyInstaller; print('Dependencias GTK y PyInstaller OK')"
if ($LASTEXITCODE -ne 0) {
    throw 'Faltan dependencias. Instala gtk3, python-gobject, python-cairo, pyinstaller y pyinstaller-hooks-contrib desde MSYS2.'
}

Push-Location $Proyecto
try {
    Write-Host 'Compilando con PyInstaller...'
    & $Python -m PyInstaller $Especificacion --noconfirm --clean `
        --distpath (Join-Path $Proyecto 'dist') `
        --workpath (Join-Path $Proyecto 'build')
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller falló.' }

    $Schemas = Join-Path $Dist 'share\glib-2.0\schemas'
    if (-not (Test-Path $Schemas)) { throw "Faltan los esquemas GLib en $Schemas" }
    Write-Host 'Compilando esquemas GLib...'
    & (Join-Path $Prefix 'bin\glib-compile-schemas.exe') $Schemas
    if ($LASTEXITCODE -ne 0) { throw 'No se pudieron compilar los esquemas GLib.' }

    $LoadersDir = Join-Path $Dist 'lib\gdk-pixbuf-2.0\2.10.0\loaders'
    if (-not (Test-Path $LoadersDir)) { throw "Faltan los loaders de GdkPixbuf en $LoadersDir" }
    $Loaders = Get-ChildItem -Path $LoadersDir -Filter '*.dll' | ForEach-Object {
        $_.FullName.Substring($Dist.Length + 1).Replace('\', '/')
    }
    if ($Loaders.Count -eq 0) { throw 'No hay loaders de GdkPixbuf para registrar.' }

    Write-Host 'Generando loaders.cache relativo...'
    $Cache = Join-Path $Dist 'lib\gdk-pixbuf-2.0\2.10.0\loaders.cache'
    & (Join-Path $Prefix 'bin\gdk-pixbuf-query-loaders.exe') @Loaders | Set-Content -Path $Cache -Encoding ascii
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo generar loaders.cache.' }

    Write-Host "Paquete listo en: $Dist"

    if ($Installer) {
        $Iscc = $null
        $Comando = Get-Command 'iscc.exe' -ErrorAction SilentlyContinue
        if ($Comando) { $Iscc = $Comando.Source }
        if (-not $Iscc) {
            $Candidatos = @(
                'C:\Program Files (x86)\Inno Setup 6\ISCC.exe',
                'C:\Program Files\Inno Setup 6\ISCC.exe'
            )
            $Iscc = $Candidatos | Where-Object { Test-Path $_ } | Select-Object -First 1
        }
        if (-not $Iscc) { throw 'No se encontró ISCC.exe. Instala Inno Setup 6.' }

        Write-Host 'Creando instalador con Inno Setup...'
        & $Iscc (Join-Path $PSScriptRoot 'instalar-windows.iss')
        if ($LASTEXITCODE -ne 0) { throw 'Inno Setup falló.' }
        Write-Host "Instalador listo en: $(Join-Path $PSScriptRoot 'Output')"
    }
}
finally {
    Pop-Location
}
