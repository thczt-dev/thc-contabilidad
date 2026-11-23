#!/usr/bin/env bash
# Instala el generador de licencias en el menú de aplicaciones del editor.
set -euo pipefail

BASE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APLICACIONES="$HOME/.local/share/applications"
ICONOS="$HOME/.local/share/icons/hicolor/256x256/apps"

mkdir -p "$APLICACIONES" "$ICONOS"
chmod +x "$BASE_DIR/generador-licencias"
cp "$BASE_DIR/../thc-contabilidad.png" "$ICONOS/thc-licencias.png"

cat > "$APLICACIONES/thc-generador-licencias.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Generador de licencias THC
Comment=Emitir claves y licencias de THC Contabilidad
Exec="$BASE_DIR/generador-licencias"
Icon=thc-licencias
Terminal=false
Categories=Utility;
Keywords=licencias;thc;contabilidad;
EOF

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APLICACIONES" >/dev/null 2>&1 || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true
fi

echo "Generador de licencias instalado."
echo "  Acceso directo: $APLICACIONES/thc-generador-licencias.desktop"
echo "  También puedes ejecutarlo con: $BASE_DIR/generador-licencias"
