# Gestión de licencias (solo editor)

Esta carpeta contiene las herramientas para emitir licencias de la edición
Windows de pago. **No se distribuye con la app.**

## Archivos

- `private_key.pem`: clave privada Ed25519. Nunca subirla.
- `public_key.pem`: clave pública. Debe coincidir con `CLAVE_PUBLICA_PEM` en
  `thc_contabilidad/licencia.py`.
- `activaciones.json`: registro de claves y equipos activados. Nunca subirlo.
- `salida/`: licencias generadas para enviar al cliente.

Los tres primeros están protegidos por `.gitignore`.

## Flujo

```bash
# Solo la primera vez, si no existe ya el par de claves
python licencias/generar.py claves

# Crear una clave de suscripción de 1 año para 2 equipos
python licencias/generar.py nueva-clave --dias 365 --max-equipos 2

# Ver claves, caducidad y activaciones
python licencias/generar.py listar

# Emitir license.json a partir del código de máquina que envía el cliente
python licencias/generar.py activar \
  --clave THCW-XXXX-XXXX-XXXX \
  --codigo THCW1-... \
  --salida licencias/salida/license-THCW-XXXX-XXXX-XXXX.json
```

El usuario carga ese `license.json` desde **Licencia...** dentro de la app.

## Renovaciones

Una renovación es simplemente una clave nueva con otra fecha de caducidad. La
app muestra los días restantes y bloquea el arranque cuando la licencia vence.
Si el cliente cambia de PC, vuelve a enviar su código de máquina: si comparte
algún componente con la activación anterior, se reemite sin consumir otra
activación; si no, se aplica el límite de equipos de la clave.

## Seguridad

La verificación es offline, así que no es inviolable: una persona con
conocimientos podría parchear el binario. Lo que sí evita es la edición manual
del archivo, el uso en otro equipo y el cambio de fecha del sistema más allá de
un día. La clave privada jamás debe viajar dentro del instalador.
