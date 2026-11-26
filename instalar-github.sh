#!/usr/bin/env bash
# Instalador de THC Contabilidad directamente desde GitHub.
# Uso: bash <(curl -fsSL https://raw.githubusercontent.com/thczt-dev/thc-contabilidad/free4windows/instalar-github.sh)
# También puedes ejecutarlo desde un clon: ./instalar-github.sh

set -euo pipefail

REPO="${THC_REPO_URL:-https://github.com/thczt-dev/thc-contabilidad.git}"
VERSION="${THC_VERSION:-free4windows}"
DEST="${THC_INSTALL_DIR:-$HOME/.local/share/thc-contabilidad}"

echo "============================================"
echo "  THC Contabilidad · instalación desde GitHub"
echo "============================================"

for herramienta in git python3; do
    if ! command -v "$herramienta" >/dev/null 2>&1; then
        echo "Error: falta '$herramienta'. Instálalo e inténtalo de nuevo." >&2
        exit 1
    fi
done

if [ -e "$DEST" ]; then
    if [ -d "$DEST/.git" ]; then
        echo "Ya existe una instalación en: $DEST"
        echo "Actualizando..."
        if git -C "$DEST" symbolic-ref -q --short HEAD >/dev/null 2>&1; then
            if ! git -C "$DEST" pull --ff-only; then
                echo "Aviso: no se pudo actualizar; se conserva la versión instalada."
            fi
        else
            # La instalación quedó fijada a una etiqueta (p. ej. v1.0.0).
            git -C "$DEST" fetch --tags --depth 1
            git -C "$DEST" -c advice.detachedHead=false checkout --force "$VERSION"
        fi
    else
        echo "Error: '$DEST' existe pero no es un clon de git." >&2
        echo "Elige otra ruta con THC_INSTALL_DIR o mueve esa carpeta." >&2
        exit 1
    fi
else
    echo "Descargando el código en: $DEST"
    mkdir -p "$(dirname "$DEST")"
    if git ls-remote --exit-code --tags "$REPO" "refs/tags/$VERSION" >/dev/null 2>&1; then
        git -c advice.detachedHead=false clone --depth 1 --branch "$VERSION" "$REPO" "$DEST"
    else
        echo "No se encontró la etiqueta $VERSION; se instala la rama principal."
        git clone --depth 1 "$REPO" "$DEST"
    fi
fi

echo "Comprobando dependencias de GTK..."
if ! python3 -c 'import gi; gi.require_version("Gtk", "3.0"); from gi.repository import Gtk' >/dev/null 2>&1; then
    echo "Instalando paquetes del sistema (puede pedir tu contraseña)..."
    if command -v apt-get >/dev/null 2>&1 && command -v sudo >/dev/null 2>&1; then
        sudo apt-get update
        sudo apt-get install -y python3-gi gir1.2-gtk-3.0 python3-cairo
    elif command -v pacman >/dev/null 2>&1 && command -v sudo >/dev/null 2>&1; then
        sudo pacman -S --needed gtk3 python-gobject python-cairo adwaita-icon-theme desktop-file-utils
    else
        echo "Error: instala manualmente las dependencias de GTK 3 para tu distro." >&2
        echo "  Debian/Ubuntu: python3-gi gir1.2-gtk-3.0 python3-cairo" >&2
        echo "  Arch:          gtk3 python-gobject python-cairo adwaita-icon-theme" >&2
        exit 1
    fi

    if ! python3 -c 'import gi; gi.require_version("Gtk", "3.0"); from gi.repository import Gtk' >/dev/null 2>&1; then
        echo "Error: las dependencias se instalaron pero 'gi' sigue sin funcionar." >&2
        echo "Cierra la terminal y vuelve a intentarlo." >&2
        exit 1
    fi
fi

echo "Creando el acceso directo en el menú de aplicaciones..."
chmod +x "$DEST/instalar.sh" "$DEST/thc-contabilidad"
"$DEST/instalar.sh"

echo
echo "Listo. Abre 'THC Contabilidad' desde el menú de aplicaciones,"
echo "o ejecútalo con:"
echo "  $DEST/thc-contabilidad"
