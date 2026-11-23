"""Licencias de la edición Windows de pago.

El archivo de licencia es un JSON firmado con Ed25519. La clave pública va
incrustada aquí; la privada se guarda fuera del repositorio y solo se usa desde
``licencias/generar.py``. La app funciona sin internet: comprueba la firma, la
fecha de caducidad y que al menos un componente de la huella del equipo coincida.

No es una protección inviolable (offline siempre puede parchearse), pero sí
impide editar la licencia a mano y permite controlar activaciones y renovaciones.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from datetime import date, timedelta

from . import rutas

CLAVE_PUBLICA_PEM = """-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAGAagf5SYHvzaUMZNKotr5YZSe5Fv+TY51zO+o7UgKj0=
-----END PUBLIC KEY-----
"""

PREFIJO_CODIGO = "THCW1-"
SAL = "thc-contabilidad/licencia/v1|"
EDICION_ESPERADA = "windows"


def es_edicion_paga() -> bool:
    """Solo el paquete Windows generado exige licencia."""
    if os.environ.get("THC_EDICION", "").strip().lower() in {"paga", "windows-paga"}:
        return True
    return rutas.es_windows() and bool(getattr(sys, "frozen", False))


def _directorio_datos() -> str:
    return os.path.dirname(os.path.abspath(rutas.ruta_config()))


def ruta_licencia() -> str:
    return os.path.join(_directorio_datos(), "license.json")


def ruta_estado() -> str:
    return os.path.join(_directorio_datos(), "estado_licencia.json")


def _hash(valor: str) -> str:
    return hashlib.sha256((SAL + str(valor)).encode("utf-8")).hexdigest()[:24]


def componentes_maquina() -> dict[str, str]:
    """Huella parcial del equipo. Nunca se guarda el valor original."""
    if rutas.es_windows():
        guid = ""
        try:
            import winreg
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography"
            ) as clave:
                guid = str(winreg.QueryValueEx(clave, "MachineGuid")[0])
        except Exception:
            guid = platform.node()

        volumen = ""
        try:
            import ctypes
            serial = ctypes.c_uint(0)
            funcion = ctypes.windll.kernel32.GetVolumeInformationW
            funcion.argtypes = [
                ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint,
                ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint),
                ctypes.POINTER(ctypes.c_uint), ctypes.c_wchar_p, ctypes.c_uint,
            ]
            funcion("C:\\", None, 0, ctypes.byref(serial), None, None, None, 0)
            volumen = str(serial.value)
        except Exception:
            volumen = platform.node()
    else:
        try:
            with open("/etc/machine-id", encoding="utf-8") as archivo:
                guid = archivo.read().strip()
        except OSError:
            guid = platform.node()
        volumen = platform.node()

    return {"guid": _hash(guid or "sin-guid"), "vol": _hash(volumen or "sin-volumen")}


def _b64url_codificar(bytes_: bytes) -> str:
    return base64.urlsafe_b64encode(bytes_).decode("ascii").rstrip("=")


def _b64url_decodificar(texto: str) -> bytes:
    texto += "=" * (-len(texto) % 4)
    return base64.urlsafe_b64decode(texto.encode("ascii"))


def canonico(datos: dict) -> bytes:
    """Serialización estable que se firma y se comprueba."""
    return json.dumps(
        datos, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def codigo_maquina() -> str:
    """Código que el usuario envía para solicitar su licencia."""
    return PREFIJO_CODIGO + _b64url_codificar(canonico(componentes_maquina()))


def decodificar_codigo(codigo: str) -> dict:
    if not codigo.startswith(PREFIJO_CODIGO):
        raise ValueError("El código de máquina no es válido.")
    datos = json.loads(_b64url_decodificar(codigo[len(PREFIJO_CODIGO):]))
    if not isinstance(datos, dict) or not datos:
        raise ValueError("El código de máquina está vacío.")
    return datos


def firmar(datos: bytes, ruta_privada: str) -> bytes:
    """Firma bytes con la clave privada del editor."""
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ed25519
        with open(ruta_privada, "rb") as archivo:
            clave = serialization.load_pem_private_key(archivo.read(), password=None)
        if not isinstance(clave, ed25519.Ed25519PrivateKey):
            raise ValueError("La clave privada debe ser Ed25519.")
        return clave.sign(datos)
    except ImportError:
        with tempfile.TemporaryDirectory() as temporal:
            entrada = os.path.join(temporal, "datos.bin")
            salida = os.path.join(temporal, "firma.bin")
            with open(entrada, "wb") as archivo:
                archivo.write(datos)
            subprocess.run(
                ["openssl", "dgst", "-sign", ruta_privada, "-out", salida, entrada],
                check=True, capture_output=True,
            )
            with open(salida, "rb") as archivo:
                return archivo.read()


def verificar_firma(datos: bytes, firma: bytes) -> bool:
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ed25519
        clave = serialization.load_pem_public_key(CLAVE_PUBLICA_PEM.encode("ascii"))
        if not isinstance(clave, ed25519.Ed25519PublicKey):
            return False
        clave.verify(firma, datos)
        return True
    except ImportError:
        with tempfile.TemporaryDirectory() as temporal:
            publica = os.path.join(temporal, "publica.pem")
            entrada = os.path.join(temporal, "datos.bin")
            firma_archivo = os.path.join(temporal, "firma.bin")
            with open(publica, "w", encoding="ascii") as archivo:
                archivo.write(CLAVE_PUBLICA_PEM)
            with open(entrada, "wb") as archivo:
                archivo.write(datos)
            with open(firma_archivo, "wb") as archivo:
                archivo.write(firma)
            resultado = subprocess.run(
                ["openssl", "dgst", "-verify", publica, "-signature", firma_archivo, entrada],
                capture_output=True, text=True,
            )
            return resultado.returncode == 0
    except (InvalidSignature, ValueError, OSError):
        return False


def _leer_json(ruta: str) -> dict | None:
    try:
        with open(ruta, encoding="utf-8") as archivo:
            datos = json.load(archivo)
        return datos if isinstance(datos, dict) else None
    except (OSError, ValueError):
        return None


def cargar_licencia() -> dict | None:
    """Devuelve los datos firmados, o None si el archivo es inválido."""
    contenido = _leer_json(ruta_licencia())
    if not contenido or "licencia" not in contenido or "firma" not in contenido:
        return None
    datos = contenido["licencia"]
    if not isinstance(datos, dict):
        return None
    try:
        firma = _b64url_decodificar(contenido["firma"])
    except Exception:
        return None
    if not verificar_firma(canonico(datos), firma):
        return None
    return datos


def _fecha(texto) -> date | None:
    try:
        return date.fromisoformat(str(texto))
    except (TypeError, ValueError):
        return None


def estado() -> dict:
    """Estado actual para mostrar en la interfaz."""
    if not es_edicion_paga():
        return {"activa": True, "motivo": "comunitaria", "caduca": None,
                "dias_restantes": None, "id": None, "codigo": codigo_maquina()}

    codigo = codigo_maquina()
    datos = cargar_licencia()
    if datos is None:
        return {"activa": False, "motivo": "sin-licencia", "caduca": None,
                "dias_restantes": None, "id": None, "codigo": codigo}

    if datos.get("edition") != EDICION_ESPERADA:
        motivo = "edicion-incorrecta"
    else:
        componentes = componentes_maquina()
        guardados = datos.get("maquina") or {}
        coincide = any(
            guardados.get(clave) == valor for clave, valor in componentes.items() if valor
        )
        if not coincide:
            motivo = "equipo-no-autorizado"
        else:
            caduca = _fecha(datos.get("expires"))
            if caduca is None:
                motivo = "caducidad-invalida"
            elif caduca < date.today():
                motivo = "caducada"
            else:
                motivo = "activa"

    ultimo = _fecha((_leer_json(ruta_estado()) or {}).get("ultimo_arranque"))
    if ultimo and ultimo > date.today() + timedelta(days=1):
        motivo = "reloj-invalidado"

    caduca = _fecha(datos.get("expires"))
    return {
        "activa": motivo == "activa",
        "motivo": motivo,
        "caduca": caduca,
        "dias_restantes": (caduca - date.today()).days if caduca else None,
        "id": datos.get("id"),
        "codigo": codigo,
    }


def registrar_arranque() -> None:
    """Guarda la fecha de uso para detectar cambios de reloj hacia atrás."""
    if not es_edicion_paga() or not estado()["activa"]:
        return
    os.makedirs(_directorio_datos(), exist_ok=True)
    with open(ruta_estado(), "w", encoding="utf-8") as archivo:
        json.dump({"ultimo_arranque": date.today().isoformat()}, archivo)
        archivo.write("\n")


def activar(contenido: str) -> dict:
    """Valida y guarda el JSON de licencia. Devuelve ``estado()``."""
    try:
        contenido_json = json.loads(contenido)
    except (TypeError, ValueError) as exc:
        raise ValueError("El archivo de licencia no contiene JSON válido.") from exc
    if not isinstance(contenido_json, dict) or "licencia" not in contenido_json:
        raise ValueError("El archivo de licencia no tiene el formato esperado.")

    datos = contenido_json["licencia"]
    try:
        firma = _b64url_decodificar(contenido_json.get("firma", ""))
    except Exception as exc:
        raise ValueError("La firma de la licencia no es válida.") from exc
    if not verificar_firma(canonico(datos), firma):
        raise ValueError("La firma de la licencia no es válida.")

    if datos.get("edition") != EDICION_ESPERADA:
        raise ValueError("Esta licencia no corresponde a la edición Windows.")
    componentes = componentes_maquina()
    guardados = datos.get("maquina") or {}
    if not any(guardados.get(c) == v for c, v in componentes.items() if v):
        raise ValueError("Esta licencia fue emitida para otro equipo.")
    caduca = _fecha(datos.get("expires"))
    if caduca is None or caduca < date.today():
        raise ValueError("Esta licencia está caducada o no tiene fecha válida.")

    os.makedirs(_directorio_datos(), exist_ok=True)
    with open(ruta_licencia(), "w", encoding="utf-8") as archivo:
        json.dump(contenido_json, archivo, ensure_ascii=False, indent=2)
        archivo.write("\n")
    return estado()


def activar_desde_archivo(ruta: str) -> dict:
    with open(ruta, encoding="utf-8") as archivo:
        return activar(archivo.read())


def texto_estado(resultado: dict | None = None) -> str:
    resultado = resultado or estado()
    if not resultado["activa"]:
        razones = {
            "sin-licencia": "Sin licencia activa",
            "caducada": "Suscripción vencida",
            "equipo-no-autorizado": "Licencia emitida para otro equipo",
            "firma-invalida": "Licencia no válida",
            "reloj-invalidado": "Fecha del sistema inconsistente",
            "edicion-incorrecta": "Edición de licencia incorrecta",
            "caducidad-invalida": "Licencia sin fecha válida",
        }
        return razones.get(resultado["motivo"], "Licencia no válida")
    dias = resultado.get("dias_restantes")
    if dias is None:
        return "Edición comunitaria (sin licencia)"
    if dias == 0:
        return "Suscripción activa hasta hoy"
    return f"Suscripción activa · {dias} días restantes"
