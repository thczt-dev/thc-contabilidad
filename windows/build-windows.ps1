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

$Python = Join-Path $Prefix 'bin\python.exe'
if (-not (Test-Path $Python)) {
    throw "No se encontró python.exe en $Prefix\bin."
}

function Ruta-Recurso([string]$Relativo) {
    # PyInstaller 6 coloca los datos en _internal; versiones anteriores los
    # dejan en la raíz del paquete. Devolvemos la base y la ruta encontrada.
    foreach ($base in @((Join-Path $Dist '_internal'), $Dist)) {
        $candidato = Join-Path $base $Relativo
        if (Test-Path $candidato) {
            return [pscustomobject]@{ Base = $base; Ruta = $candidato }
        }
    }
    return $null
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

    $Schemas = Ruta-Recurso 'share\glib-2.0\schemas'
    if (-not $Schemas) { throw 'Faltan los esquemas GLib en el paquete compilado.' }
    Write-Host "Compilando esquemas GLib en $($Schemas.Ruta)..."
    & (Join-Path $Prefix 'bin\glib-compile-schemas.exe') $Schemas.Ruta
    if ($LASTEXITCODE -ne 0) { throw 'No se pudieron compilar los esquemas GLib.' }

    $Loaders = Ruta-Recurso 'lib\gdk-pixbuf-2.0\2.10.0\loaders'
    if (-not $Loaders) { throw 'Faltan los loaders de GdkPixbuf en el paquete compilado.' }
    $Modulos = @(Get-ChildItem -Path $Loaders.Ruta -Filter '*.dll' | ForEach-Object {
        $_.FullName.Substring($Loaders.Base.Length + 1).Replace('\', '/')
    })
    if ($Modulos.Count -eq 0) { throw 'No hay loaders de GdkPixbuf para registrar.' }

    Write-Host 'Generando loaders.cache relativo...'
    $Cache = Join-Path (Split-Path $Loaders.Ruta -Parent) 'loaders.cache'
    # Ejecutamos la herramienta desde la base del paquete para que las rutas
    # escritas en loaders.cache sean relativas y sigan sirviendo al mover {app}.
    Push-Location $Loaders.Base
    try {
        & (Join-Path $Prefix 'bin\gdk-pixbuf-query-loaders.exe') @Modulos | Set-Content -Path $Cache -Encoding ascii
    }
    finally {
        Pop-Location
    }
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
