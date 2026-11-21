#!/usr/bin/env bash
# Crea el repositorio en GitHub, sube el código y publica la release v1.0.0.
# Requiere: gh auth login (una sola vez).

set -euo pipefail

# Usa la sesión guardada por `gh auth login`, no tokens heredados del entorno.
unset GH_TOKEN GITHUB_TOKEN

cd "$(dirname "${BASH_SOURCE[0]}")"

REPO="${GH_REPO:-thc-contabilidad}"
VISIBILIDAD="${GH_VISIBILITY:-public}"
VERSION="${GH_VERSION:-v1.0.0}"

case "$VISIBILIDAD" in
    public|private|internal) ;;
    *) echo "Error: GH_VISIBILITY debe ser public, private o internal." >&2; exit 1 ;;
esac

if ! command -v gh >/dev/null 2>&1; then
    echo "Error: falta GitHub CLI. Instálalo con: sudo apt install gh" >&2
    exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
    echo "No hay sesión de GitHub. Ejecuta primero: gh auth login" >&2
    exit 1
fi

USUARIO="$(gh api user --jq .login)"
echo "GitHub: $USUARIO · repositorio: $REPO · visibilidad: $VISIBILIDAD"

if git remote get-url origin >/dev/null 2>&1; then
    echo "El remote 'origin' ya existe; subiendo cambios..."
    git push -u origin main
else
    echo "Creando repositorio remoto..."
    gh repo create "$REPO" "--$VISIBILIDAD" --source=. --remote=origin --push
fi

git push origin "$VERSION"

if gh release view "$VERSION" >/dev/null 2>&1; then
    echo "La release $VERSION ya existe; no se modifica."
else
    echo "Publicando release $VERSION..."
    gh release create "$VERSION" \
        --title "THC Contabilidad $VERSION" \
        --notes-file RELEASE_NOTES.md
fi

echo
echo "Listo:"
echo "  Repositorio: https://github.com/$USUARIO/$REPO"
echo "  Release:     https://github.com/$USUARIO/$REPO/releases/tag/$VERSION"
