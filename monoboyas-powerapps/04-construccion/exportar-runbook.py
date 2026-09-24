#!/usr/bin/env python3
"""Genera el runbook autonomo a partir del fragmento publicado.

`runbook-powerapps.html` es un fragmento: la plataforma de artifacts le anade
el doctype y el head al publicarlo, y su tipografia viene de un enlace a Google
Fonts. Este script lo convierte en un documento completo, con las tipografias
incrustadas y una barra de indice para moverse entre las siete fases, que se
abre con doble clic y sin internet.

    python3 exportar-runbook.py

La fuente no se modifica nunca: si cambia el runbook, se vuelve a ejecutar.
"""

import re
import sys
from pathlib import Path

AQUI = Path(__file__).parent
PAQUETE = AQUI.parent
FUENTE = AQUI / "runbook-powerapps.html"
SALIDA = AQUI / "construir-app-monoboyas.html"

# Reutiliza el incrustador de tipografias del exportador del mockup: es el
# mismo trabajo y no tiene sentido tenerlo dos veces.
sys.path.insert(0, str(PAQUETE / "03-mockups"))
from exportar import incrustar_tipografias  # noqa: E402

TITULO = "Construir la app de Monoboyas"  # el mismo nombre con el que se publica
DESCRIPCION = (
    "Runbook de construccion en Power Platform: 28 pasos en 7 fases, para el "
    "sistema de monoboya de TAMOIN para Repsol - Refineria La Pampilla."
)

# Cada apartado se ancla por el rotulo con el que empieza, que es unico en el
# documento. Asi la barra puede saltar sin tocar la fuente.
APARTADOS = [
    ("empezar", "Antes de empezar", "Antes de empezar"),
    ("recorrido", "El recorrido", "El recorrido"),
    ("fase1", "Fase 1", "1 · Entorno"),
    ("fase2", "Fase 2", "2 · Tablas"),
    ("fase3", "Fase 3", "3 · Datos"),
    ("fase4", "Fase 4", "4 · App"),
    ("fase5", "Fase 5", "5 · Panel"),
    ("fase6", "Fase 6", "6 · Avisos"),
    ("fase7", "Fase 7", "7 · Publicar"),
    ("trampas", "Léelo antes, no después", "Trampas"),
    ("glosario", "Para entender los pasos", "Glosario"),
    ("ayuda", "Sé honesto contigo mismo", "Pedir ayuda"),
]

ESTILOS_BARRA = """
  /* ===== Barra de indice ===== */
  :root { --barra: 44px; }
  body { padding-top: var(--barra); }
  .barra {
    position: fixed; top: 0; left: 0; right: 0; height: var(--barra); z-index: 50;
    background: var(--surface); border-bottom: 1px solid var(--line);
    display: flex; align-items: center; gap: 2px;
    padding-inline: 14px; overflow-x: auto; scrollbar-width: none;
  }
  .barra::-webkit-scrollbar { display: none; }
  .barra .marca {
    font-family: Archivo, sans-serif; font-weight: 700; font-size: 13px;
    letter-spacing: -.01em; margin-right: 12px; white-space: nowrap; color: var(--ink);
  }
  .barra a {
    font-size: 12px; color: var(--ink-2); text-decoration: none;
    padding: 5px 8px; border-radius: 4px; white-space: nowrap;
  }
  .barra a:hover { background: var(--surface-2); color: var(--ink); }
  /* El ancla queda bajo la barra si no se le reserva su altura */
  .wrap [id] { scroll-margin-top: calc(var(--barra) + 12px); }
  html { scroll-behavior: smooth; }
  @media print {
    :root { --barra: 0px; }
    .barra { display: none; }
  }
"""


class ErrorExport(Exception):
    """Algo impide generar el archivo."""


def exportar() -> Path:
    if not FUENTE.exists():
        raise ErrorExport(f"no se encuentra la fuente: {FUENTE.name}")
    doc = FUENTE.read_text(encoding="utf-8")

    # 1. Separar el <title>, el <link> de tipografias y el <style> del cuerpo
    m_link = re.search(r'<link rel="stylesheet" href="([^"]+)">\n?', doc)
    if not m_link:
        raise ErrorExport("no se encontro el enlace a las tipografias")
    url_css = m_link.group(1).replace("&amp;", "&")
    doc = doc.replace(m_link.group(0), "")
    doc = re.sub(r"<title>.*?</title>\n?", "", doc, count=1)

    m_style = re.search(r"<style>(.*?)</style>", doc, re.S)
    if not m_style:
        raise ErrorExport("no se encontro el bloque de estilos")
    estilos = m_style.group(1)
    cuerpo = doc[m_style.end():].strip()

    # 2. Tipografias incrustadas, o el enlace externo si la descarga falla
    caras = incrustar_tipografias(url_css)
    if caras:
        estilos = caras + "\n" + estilos
        enlace_fuentes = ""
    else:
        enlace_fuentes = f'\n  <link rel="stylesheet" href="{url_css}">'
        print("  aviso: el archivo necesitara internet para su tipografia", file=sys.stderr)

    estilos += ESTILOS_BARRA

    # 3. Anclas en cada apartado
    for ident, rotulo, _ in APARTADOS:
        viejo = f'<p class="eyebrow">{rotulo}</p>'
        if cuerpo.count(viejo) != 1:
            raise ErrorExport(f"el rotulo «{rotulo}» no aparece exactamente una vez")
        cuerpo = cuerpo.replace(viejo, f'<p class="eyebrow" id="{ident}">{rotulo}</p>', 1)

    enlaces = "\n".join(
        f'  <a href="#{ident}">{etiqueta}</a>' for ident, _, etiqueta in APARTADOS
    )

    salida = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{TITULO}</title>
  <meta name="description" content="{DESCRIPCION}">
  <meta name="color-scheme" content="light dark">{enlace_fuentes}
  <style>
  html, body {{ margin: 0; }}
  img {{ max-width: 100%; }}
{estilos}
  </style>
</head>
<body>
<nav class="barra">
  <span class="marca">Construir la app</span>
{enlaces}
</nav>
{cuerpo}
</body>
</html>
"""
    SALIDA.write_text(salida, encoding="utf-8")
    return SALIDA


if __name__ == "__main__":
    try:
        ruta = exportar()
    except ErrorExport as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"  generado: {ruta.name} · {ruta.stat().st_size // 1024} KB")
