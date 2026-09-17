#!/usr/bin/env python3
"""Genera el PDF de la propuesta, en tema claro, desde el HTML autonomo.

Se parte de `propuesta-monoboyas.html` y no del mockup suelto por dos razones:
ya declara la codificacion, asi que los acentos no se rompen, y lleva las
tipografias incrustadas, asi que el PDF sale con la tipografia correcta y con
el texto seleccionable en lugar de rasterizado.

    python3 generar-pdf.py          # A3 vertical, el que conserva el tamano
    python3 generar-pdf.py --a4     # A4 vertical, para papel corriente

Requiere Chromium con Playwright. Si cambia la propuesta: primero
`exportar.py`, luego este.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).parent
FUENTE = AQUI / "propuesta-monoboyas.html"
SALIDA = AQUI / "propuesta-monoboyas.pdf"

# El diseno mide 1180 px de ancho. En A4 vertical (794 px) habria que encogerlo
# a dos tercios y los mockups quedarian ilegibles; en A3 (1123 px) entra casi a
# tamano real. Por eso A3 es el formato por defecto.
FORMATOS = {
    "a3": {"format": "A3", "scale": 1.0},
    "a4": {"format": "A4", "scale": 0.68},
}

GUION = r"""
const { chromium } = require('%(playwright)s');

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1180, height: 1400 }, colorScheme: 'light' });

  const errores = [];
  p.on('pageerror', e => errores.push(e.message));

  await p.goto('file://%(fuente)s', { waitUntil: 'load' });
  await p.waitForTimeout(2500);                       // que asienten las tipografias
  await p.evaluate(() => document.fonts.ready);

  // El tema claro se fija explicitamente: no se confia en el del sistema
  await p.evaluate(() => document.documentElement.setAttribute('data-theme', 'light'));

  // Medio de impresion, para que apliquen las reglas @media print
  await p.emulateMedia({ media: 'print', colorScheme: 'light' });
  await p.waitForTimeout(600);

  await p.pdf({
    path: '%(salida)s',
    format: '%(formato)s',
    scale: %(escala)s,
    printBackground: true,                            // sin esto saldria todo en blanco
    // Margen de pagina a cero a proposito: con cualquier margen, Chromium deja
    // esa franja en BLANCO y no la pinta ni el fondo del body ni una capa fija.
    // El aire de los bordes lo pone el CSS de impresion, dentro del contenido.
    margin: { top: '0', bottom: '0', left: '0', right: '0' },
    preferCSSPageSize: false
  });

  console.log('errores:' + (errores.length ? errores.join(' | ') : 'ninguno'));
  await b.close();
})();
"""


class ErrorPdf(Exception):
    """Algo impide generar el PDF."""


def ruta_playwright() -> str:
    """Playwright esta instalado global, no en el proyecto: hay que apuntarlo."""
    for cand in ("/opt/node22/lib/node_modules/playwright", "playwright"):
        if cand == "playwright" or Path(cand).exists():
            return cand
    raise ErrorPdf("no se encuentra playwright")


def generar(formato: str) -> Path:
    if not FUENTE.exists():
        raise ErrorPdf(f"falta {FUENTE.name}: ejecuta antes exportar.py")

    cfg = FORMATOS[formato]
    guion = GUION % {
        "playwright": ruta_playwright(),
        "fuente": FUENTE.resolve(),
        "salida": SALIDA.resolve(),
        "formato": cfg["format"],
        "escala": cfg["scale"],
    }

    # Se hereda el entorno y solo se anade NODE_PATH: construir uno minimo
    # dejaria fuera PLAYWRIGHT_BROWSERS_PATH y Chromium no se encontraria.
    entorno = dict(os.environ, NODE_PATH="/opt/node22/lib/node_modules")

    r = subprocess.run(["node", "-e", guion], capture_output=True, text=True, env=entorno)
    if r.returncode != 0:
        raise ErrorPdf(f"Chromium fallo al imprimir:\n{r.stderr.strip()[:600]}")
    if "errores:ninguno" not in r.stdout:
        print(f"  aviso: {r.stdout.strip()}", file=sys.stderr)
    if not SALIDA.exists():
        raise ErrorPdf("el PDF no se llego a escribir")
    return SALIDA


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Genera el PDF de la propuesta en tema claro.")
    ap.add_argument("--a4", action="store_true", help="A4 vertical en vez de A3")
    args = ap.parse_args()

    try:
        ruta = generar("a4" if args.a4 else "a3")
    except ErrorPdf as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"  generado: {ruta.name} · {ruta.stat().st_size // 1024} KB "
          f"· {'A4' if args.a4 else 'A3'} vertical · tema claro")
