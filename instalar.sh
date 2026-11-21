#!/usr/bin/env bash
# Instala el lanzador en el menú de aplicaciones del usuario.
set -euo pipefail

BASE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APLICACIONES="$HOME/.local/share/applications"
ICONOS="$HOME/.local/share/icons/hicolor/scalable/apps"

mkdir -p "$APLICACIONES" "$ICONOS"
chmod +x "$BASE_DIR/thc-contabilidad"

sed "s|__EXEC_PATH__|$BASE_DIR/thc-contabilidad|" \
    "$BASE_DIR/thc-contabilidad.desktop" > "$APLICACIONES/thc-contabilidad.desktop"
cp "$BASE_DIR/thc-contabilidad.svg" "$ICONOS/thc-contabilidad.svg"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APLICACIONES" >/dev/null 2>&1 || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true
fi

echo "THC Contabilidad instalado."
echo "  Lanzador: $APLICACIONES/thc-contabilidad.desktop"
echo "  Datos:    $BASE_DIR/datos/contabilidad.db"
