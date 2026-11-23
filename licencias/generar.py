"""Herramienta del editor para gestionar licencias de la edición Windows.

No forma parte de la app; se ejecuta en tu máquina. La clave privada y el
registro de activaciones NO deben subirse al repositorio.

Ejemplos:

    python licencias/generar.py claves
    python licencias/generar.py nueva-clave --dias 365 --max-equipos 2
    python licencias/generar.py activar --clave THCW-XXXX-XXXX-XXXX --codigo THCW1-...
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
from datetime import date, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BASE)
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from thc_contabilidad import licencia  # noqa: E402

PRIVADA = os.path.join(BASE, "private_key.pem")
PUBLICA = os.path.join(BASE, "public_key.pem")
REGISTRO = os.path.join(BASE, "activaciones.json")
ALFABETO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def leer_registro() -> dict:
    try:
        with open(REGISTRO, encoding="utf-8") as archivo:
            datos = json.load(archivo)
        if isinstance(datos, dict) and isinstance(datos.get("claves"), dict):
            return datos
    except (OSError, ValueError):
        pass
    return {"claves": {}}


def guardar_registro(datos: dict) -> None:
    with open(REGISTRO, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
        archivo.write("\n")


def nueva_clave(dias: int, max_equipos: int) -> str:
    registro = leer_registro()
    while True:
        grupos = ["".join(secrets.choice(ALFABETO) for _ in range(4)) for _ in range(3)]
        clave = "THCW-" + "-".join(grupos)
        if clave not in registro["claves"]:
            break

    caduca = date.today() + timedelta(days=dias)
    registro["claves"][clave] = {
        "creada": date.today().isoformat(),
        "expires": caduca.isoformat(),
        "max_equipos": max_equipos,
        "activaciones": [],
    }
    guardar_registro(registro)
    return clave


def mismo_equipo(maquina: dict, activaciones: list[dict]) -> dict | None:
    """Reutiliza la activación si comparte algún componente con la máquina."""
    for item in activaciones:
        guardado = item.get("maquina") or {}
        if any(guardado.get(c) == v for c, v in maquina.items() if v):
            return item
    return None


def activar(clave: str, codigo: str, salida: str) -> str:
    if not os.path.exists(PRIVADA):
        raise SystemExit(f"Falta la clave privada en {PRIVADA}")
    registro = leer_registro()
    entrada = registro["claves"].get(clave.upper())
    if entrada is None:
        raise SystemExit("No existe esa clave de licencia.")

    if date.fromisoformat(entrada["expires"]) < date.today():
        raise SystemExit("La clave de licencia ya está vencida; emite una renovación.")

    maquina = licencia.decodificar_codigo(codigo)
    existente = mismo_equipo(maquina, entrada["activaciones"])
    if existente is None and len(entrada["activaciones"]) >= entrada["max_equipos"]:
        raise SystemExit(
            "Límite de activaciones alcanzado para esta clave. "
            "Aumenta max_equipos o emite una licencia nueva."
        )

    if existente is None:
        existente = {"maquina": maquina, "fecha": date.today().isoformat()}
        entrada["activaciones"].append(existente)
        guardar_registro(registro)

    datos = {
        "id": clave.upper(),
        "edition": "windows",
        "issued": existente["fecha"],
        "expires": entrada["expires"],
        "maquina": maquina,
        "max_equipos": entrada["max_equipos"],
        "numero_activacion": entrada["activaciones"].index(existente) + 1,
    }
    firma = licencia.firmar(licencia.canonico(datos), PRIVADA)
    contenido = {
        "licencia": datos,
        "firma": licencia._b64url_codificar(firma),
    }
    os.makedirs(os.path.dirname(os.path.abspath(salida)), exist_ok=True)
    with open(salida, "w", encoding="utf-8") as archivo:
        json.dump(contenido, archivo, ensure_ascii=False, indent=2)
        archivo.write("\n")
    return salida


def cmd_claves(_args) -> None:
    if os.path.exists(PRIVADA) and not _args.forzar:
        raise SystemExit("Ya existe private_key.pem. Usa --forzar solo si sabes lo que haces.")
    os.makedirs(BASE, exist_ok=True)
    import subprocess
    subprocess.run(["openssl", "genpkey", "-algorithm", "ED25519", "-out", PRIVADA], check=True)
    subprocess.run(["openssl", "pkey", "-in", PRIVADA, "-pubout", "-out", PUBLIC], check=True)
    os.chmod(PRIVADA, 0o600)
    print("Clave privada creada:", PRIVADA)
    print("Clave pública creada:", PUBLIC)
    print("Copia la clave pública en thc_contabilidad/licencia.py si la regeneras.")


def cmd_nueva_clave(args) -> None:
    clave = nueva_clave(args.dias, args.max_equipos)
    print("Clave creada:", clave)
    print("Caduca:", (date.today() + timedelta(days=args.dias)).isoformat())
    print("Máximo de equipos:", args.max_equipos)


def cmd_activar(args) -> None:
    ruta = activar(args.clave, args.codigo, args.salida)
    print("Licencia generada:", ruta)


def cmd_listar(_args) -> None:
    registro = leer_registro()
    if not registro["claves"]:
        print("No hay claves registradas.")
        return
    for clave, datos in registro["claves"].items():
        usadas = len(datos["activaciones"])
        print(f"{clave} · caduca {datos['expires']} · {usadas}/{datos['max_equipos']} equipos")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="comando", required=True)

    claves = sub.add_parser("claves", help="Generar el par de claves Ed25519")
    claves.add_argument("--forzar", action="store_true")
    claves.set_defaults(func=cmd_claves)

    nueva = sub.add_parser("nueva-clave", help="Crear una clave de suscripción")
    nueva.add_argument("--dias", type=int, default=365)
    nueva.add_argument("--max-equipos", type=int, default=2)
    nueva.set_defaults(func=cmd_nueva_clave)

    activacion = sub.add_parser("activar", help="Emitir license.json desde un código de máquina")
    activacion.add_argument("--clave", required=True)
    activacion.add_argument("--codigo", required=True)
    activacion.add_argument("--salida", default=os.path.join(BASE, "salida", "license.json"))
    activacion.set_defaults(func=cmd_activar)

    listado = sub.add_parser("listar", help="Listar claves y activaciones")
    listado.set_defaults(func=cmd_listar)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
