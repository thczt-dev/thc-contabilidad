#!/usr/bin/env bash
# Instalador de THC Contabilidad directamente desde GitHub.
# Uso: bash <(curl -fsSL https://raw.githubusercontent.com/thczt-dev/thc-contabilidad/v1.1.0/instalar-github.sh)
# También puedes ejecutarlo desde un clon: ./instalar-github.sh

set -euo pipefail

REPO="${THC_REPO_URL:-https://github.com/thczt-dev/thc-contabilidad.git}"
VERSION="${THC_VERSION:-v1.1.0}"
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
    else
        echo "Error: instala manualmente python3-gi, gir1.2-gtk-3.0 y python3-cairo." >&2
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
