#!/usr/bin/env bash
# Instala el lanzador en el menú de aplicaciones del usuario.
set -euo pipefail

BASE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APLICACIONES="$HOME/.local/share/applications"
ICONOS="$HOME/.local/share/icons/hicolor/scalable/apps"
ICONOS_256="$HOME/.local/share/icons/hicolor/256x256/apps"

mkdir -p "$APLICACIONES" "$ICONOS" "$ICONOS_256"
chmod +x "$BASE_DIR/thc-contabilidad"

sed "s|__EXEC_PATH__|$BASE_DIR/thc-contabilidad|" \
    "$BASE_DIR/thc-contabilidad.desktop" > "$APLICACIONES/thc-contabilidad.desktop"
cp "$BASE_DIR/thc-contabilidad.svg" "$ICONOS/thc-contabilidad.svg"
cp "$BASE_DIR/thc-contabilidad.png" "$ICONOS_256/thc-contabilidad.png"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APLICACIONES" >/dev/null 2>&1 || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true
fi

# Primera configuración visual: se abre al terminar la instalación. Si se
# omite, la app lo volverá a mostrar en el primer arranque.
if [ "${THC_SIN_ASISTENTE:-0}" != "1" ] && \
   { [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; }; then
    echo "Abriendo el asistente de preferencias..."
    (
        cd "$BASE_DIR"
        nohup python3 -m thc_contabilidad.asistente >/dev/null 2>&1 &
    )
fi

echo "THC Contabilidad instalado."
echo "  Lanzador: $APLICACIONES/thc-contabilidad.desktop"
echo "  Datos:    $BASE_DIR/datos/contabilidad.db"
