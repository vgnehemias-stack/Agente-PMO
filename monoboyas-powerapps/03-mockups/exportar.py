#!/usr/bin/env python3
"""Genera el HTML autonomo para presentar a partir del mockup publicado.

El mockup (`mockup-pantallas.html`) es un fragmento: la plataforma de artifacts
le anade el doctype, el head y un reset al publicarlo. Este script lo convierte
en un documento completo, con las tipografias incrustadas, barra de indice y
modo presentacion, para poder abrirlo con doble clic y sin internet.

    python3 exportar.py

La fuente no se modifica nunca: si cambia la propuesta, se vuelve a ejecutar.
"""

import base64
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

AQUI = Path(__file__).parent
FUENTE = AQUI / "mockup-pantallas.html"
SALIDA = AQUI / "propuesta-monoboyas.html"

TITULO = "Mantenimiento de Monoboyas"  # el mismo nombre con el que se publica
DESCRIPCION = (
    "Propuesta de aplicacion en Power Apps para centralizar la informacion del "
    "sistema de monoboya. TAMOIN para Repsol - Refineria La Pampilla."
)
NAVEGADOR = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120 Safari/537.36"
)

APARTADOS = [
    ("problema", "01 · El problema"),
    ("estructura", "02 · La estructura"),
    ("pantallas", "03 · Qué verá el equipo"),
    ("dinamicas", "04 · Las dinámicas"),
    ("construccion", "05 · Cómo se construye"),
    ("ruta", "06 · La ruta"),
]

# Rotulo con el que empieza cada apartado, para poder anclarlos sin tocar la fuente
ANCLAS = {
    "problema": "01 · El problema",
    "estructura": "02 · La estructura",
    "pantallas": "03 · Qué verá el equipo",
    "dinamicas": "04 · Las dinámicas",
    "construccion": "05 · Cómo se construye",
    "ruta": "06 · La ruta",
}


class ErrorExport(Exception):
    """Algo impide generar el archivo."""


# --------------------------------------------------------------------------- #
# Tipografias
# --------------------------------------------------------------------------- #

def _bajar(url: str) -> bytes:
    pet = urllib.request.Request(url, headers={"User-Agent": NAVEGADOR})
    with urllib.request.urlopen(pet, timeout=30) as r:
        return r.read()


def incrustar_tipografias(url_css: str) -> str | None:
    """Devuelve los @font-face del subconjunto latino con el woff2 en base64.

    Si la descarga falla devuelve None y el documento conserva el enlace a
    Google Fonts: se vera bien con internet y con la fuente del sistema sin el.
    """
    try:
        css = _bajar(url_css).decode("utf-8")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print(f"  aviso: no se pudo bajar el CSS de tipografias ({e})", file=sys.stderr)
        return None

    bloques, pesos = [], 0
    for bloque in re.findall(r"@font-face\s*\{[^}]*\}", css):
        # Solo el subconjunto latino basico: es el unico que usa el documento
        if "U+0000-00FF" not in bloque:
            continue
        m = re.search(r"url\((https://fonts\.gstatic\.com[^)]+\.woff2)\)", bloque)
        if not m:
            continue
        try:
            datos = _bajar(m.group(1))
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            print(f"  aviso: no se pudo bajar una tipografia ({e})", file=sys.stderr)
            return None
        pesos += len(datos)
        b64 = base64.b64encode(datos).decode("ascii")
        bloques.append(bloque.replace(m.group(1), f"data:font/woff2;base64,{b64}"))

    if not bloques:
        print("  aviso: no se encontro ningun @font-face latino", file=sys.stderr)
        return None

    print(f"  tipografias: {len(bloques)} archivos · "
          f"{pesos // 1024} KB · {pesos * 4 // 3 // 1024} KB en base64")
    return "\n".join(bloques)


# --------------------------------------------------------------------------- #
# Piezas que se anaden al documento
# --------------------------------------------------------------------------- #

ESTILOS_EXPORT = """
  /* ===== Barra superior ===== */
  :root { --barra: 46px; }
  body { padding-top: var(--barra); }
  .barra {
    position: fixed; top: 0; left: 0; right: 0; height: var(--barra); z-index: 50;
    background: var(--surface); border-bottom: 1px solid var(--line);
    display: flex; align-items: center; gap: 4px;
    padding-inline: 14px; overflow-x: auto; scrollbar-width: none;
  }
  .barra::-webkit-scrollbar { display: none; }
  .barra .marca {
    font-family: Archivo, sans-serif; font-weight: 700; font-size: 13px;
    letter-spacing: -.01em; margin-right: 12px; white-space: nowrap;
  }
  .barra a {
    font-size: 12px; color: var(--ink-2); text-decoration: none;
    padding: 5px 9px; border-radius: 4px; white-space: nowrap;
  }
  .barra a:hover { background: var(--surface-2); color: var(--ink); }
  .barra a:focus-visible, .barra button:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }
  .barra .der { margin-left: auto; display: flex; gap: 6px; padding-left: 12px; }
  .barra button {
    font-family: "IBM Plex Sans", sans-serif; font-size: 12px; cursor: pointer;
    background: var(--surface); color: var(--ink-2);
    border: 1px solid var(--line-2); border-radius: 4px; padding: 5px 11px;
    white-space: nowrap;
  }
  .barra button:hover { background: var(--surface-2); color: var(--ink); }
  .barra .pres { background: var(--accent); border-color: var(--accent); color: #fff; font-weight: 600; }

  /* ===== Modo presentacion ===== */
  body.presentando { padding-top: 0; overflow: hidden; }
  body.presentando .barra { display: none; }
  body.presentando .wrap { max-width: none; padding: 0; }
  body.presentando main > * { display: none; }
  body.presentando .paso { display: none; }
  /* los contenedores que envuelven al paso activo siguen visibles */
  body.presentando .visible { display: block; }
  body.presentando .paso.activo {
    display: block;
    position: fixed; inset: 0;
    overflow-y: auto; overscroll-behavior: contain;
    padding: 46px clamp(20px, 5vw, 76px) 72px;
    background: var(--ground);
  }
  body.presentando .paso.activo > * { max-width: 1120px; margin-inline: auto; }
  body.presentando section { padding-block: 0; }

  .mando {
    position: fixed; bottom: 0; left: 0; right: 0; z-index: 60;
    display: none; align-items: center; gap: 14px;
    padding: 9px clamp(16px, 4vw, 30px);
    background: var(--surface); border-top: 1px solid var(--line);
  }
  body.presentando .mando { display: flex; }
  .mando .cuenta {
    font-family: "IBM Plex Mono", monospace; font-size: 11.5px;
    color: var(--ink-3); font-variant-numeric: tabular-nums; white-space: nowrap;
  }
  .mando .pista { font-size: 11.5px; color: var(--ink-3); }
  .mando .progreso { flex: 1; height: 3px; background: var(--surface-2); border-radius: 2px; overflow: hidden; }
  .mando .progreso i { display: block; height: 100%; background: var(--accent); transition: width .18s ease; }
  .mando button {
    font-family: "IBM Plex Sans", sans-serif; font-size: 12px; cursor: pointer;
    background: var(--surface); color: var(--ink-2);
    border: 1px solid var(--line-2); border-radius: 4px; padding: 4px 11px;
  }
  .mando button:hover { background: var(--surface-2); color: var(--ink); }

  @media (max-width: 720px) { .mando .pista { display: none; } }
  @media (prefers-reduced-motion: reduce) {
    html { scroll-behavior: auto; }
    .mando .progreso i { transition: none; }
  }

  html { scroll-behavior: smooth; }
  [id] { scroll-margin-top: calc(var(--barra) + 14px); }

  /* ===== Impresion y PDF · formato ejecutivo =====
     Tres cosas que este bloque resuelve, y que no son obvias:

     1. Chromium IGNORA `break-inside: avoid` dentro de contenedores flex y
        grid. Por eso los mockups salian cortados entre hojas aunque caben de
        sobra: viven dentro de un .stack (flex) y un .duo (grid). Al pasarlos a
        bloque en impresion, la paginacion normal vuelve a respetarlos.
     2. Un contenedor con desplazamiento no se desplaza al imprimir: se RECORTA.
        Hay que devolverle el desbordamiento visible a tablas y codigo.
     3. El PDF es un documento ejecutivo, no la pagina web impresa: tipografia
        mas densa y fuera la prosa que ya dicen las tablas y los mockups. */
  @media print {
    :root { --barra: 0px; }
    .barra, .mando { display: none !important; }
    /* El PDF se genera con margen de pagina CERO, porque con cualquier margen
       Chromium deja esa franja en blanco y no hay forma de pintarla. Asi el
       crema del body llega hasta el borde de la hoja, y el aire de los bordes
       lo pone este padding. */
    body {
      padding: 0; font-size: 12.5px; line-height: 1.5;
      background: var(--ground);
    }
    .wrap { max-width: none; padding: 20mm 18mm 22mm; }

    /* En las hojas de continuacion el padding del .wrap no se repite, y los
       MARGENES se truncan en un corte de pagina. Los BORDES no: un borde del
       color del fondo es aire garantizado tambien cuando el bloque estrena
       hoja. Es lo que evita que nada arranque pegado al filo. */
    section { padding-block: 0; border-block: 9mm solid var(--ground); }
    .stack > *, .duo > *,
    section > div:has(> .app) { border-block: 9mm solid var(--ground); }

    /* --- 1. Paginacion ---
       Chromium no fragmenta bien dentro de flex ni grid: los contenedores que
       tienen que poder cortarse entre hojas pasan a bloque. */
    .stack, .duo, .fleet, .check, .niveles, .need, .fases, .abiertas { display: block; }
    .stack > *, .duo > * { margin-bottom: 26px; }
    .check > *, .niveles > *, .abiertas > * { border-bottom: 1px solid var(--line); }

    /* Lo que nunca debe partirse: cabe de sobra en una hoja */
    .app, .frag, figure, .arbol,
    .nivel, .din, .ck, .nd, .fase, .gl, .block, .aviso, .sub, .stat, .toc > * {
      break-inside: avoid;
    }
    .app { break-after: avoid; }          /* el pie se queda con su mockup */

    /* Un mockup no puede partirse, asi que cuanto mas alto sea, mas a menudo no
       cabe en lo que resta de hoja y deja un cuarto de pagina en blanco. Se le
       quita el alto minimo de pantalla y se aprieta por dentro: en papel no
       hace falta el aire que pide una interfaz de uso. */
    .app .shell { min-height: 0; }
    .app .main { padding: 13px 15px 15px; gap: 11px; }
    .app .nav { padding: 8px 0; }
    .app .nav a { padding: 5px 13px; }
    .app .nav .grp { padding: 9px 13px 3px; }
    .app .stat { padding: 7px 10px 8px; }
    .app .tarjeta { padding: 9px 11px 10px; }
    .app .li { padding: 5px 9px; }
    .app tbody td { padding: 6px 10px; }
    .app .kv { padding: 6px 0; }
    .app .pestanas button, .app .tabs div { padding: 6px 12px; }
    .cap { break-before: avoid; break-inside: avoid; }

    /* Las tablas largas SI se parten entre hojas, repitiendo su cabecera.
       Forzarlas enteras era lo que dejaba un tercio de pagina en blanco. */
    .tablewrap, .cmp, .dec { break-inside: auto; }
    thead { display: table-header-group; }
    tr { break-inside: avoid; }

    /* Ningun rotulo ni titulo se queda solo al pie de una hoja */
    .sec-head { break-inside: avoid; break-after: avoid; }
    h2, h3, h4, .eyebrow { break-after: avoid; }

    /* --- 2. Recuperar lo que se recortaria --- */
    .tablewrap, pre, .listcol { overflow: visible; }
    table { min-width: 0; }
    .listcol { max-height: none; }

    /* --- 3. Densidad ejecutiva --- */
    .sec-head { margin-bottom: 16px; }
    header.hero { padding-block: 0 26px; }
    header.hero h1 { font-size: 30px; }
    header.hero .lead { font-size: 13.5px; max-width: 78ch; }
    .sec-head h2 { font-size: 18px; }
    .sec-head p { font-size: 12.5px; max-width: 86ch; }
    .toc { grid-template-columns: repeat(6, minmax(0, 1fr)); }
    .cap { margin-top: 8px; }
    .cap .t { font-size: 13px; }
    .cap p { font-size: 11.5px; }
    table { font-size: 11.5px; }
    tbody td { padding: 6px 10px; }
    thead th { padding: 6px 10px; }
    .aviso { padding: 12px 14px; }
    .aviso p { font-size: 12px; }
    .din p, .gl p, .block li, .nivel p, .nd p, .ck p { font-size: 11.5px; }

    /* Fuera lo que repite lo que ya dicen las tablas y los mockups.
       Los bloques marcados data-pdf="omitir" son pantallas redundantes en
       papel: la tercera vista del esquema y las pestanas sueltas de la ficha.
       En la version interactiva siguen estando. */
    .nota, figcaption, .niveles .cost, [data-pdf="omitir"] { display: none; }

    /* --- Paleta clara forzada, ademas del tema que fija el guion --- */
    :root, :root[data-theme="dark"] {
      --ground: #F2F1EE; --surface: #FFFFFF; --surface-2: #E9E8E4; --surface-3: #F7F6F4;
      --ink: #1B2228; --ink-2: #4A555E; --ink-3: #7A858E;
      --line: #D6D5D0; --line-2: #C2C1BB;
      --accent: #D2570D; --accent-soft: #FBEEE4; --steel: #2B3A45; --steel-ink: #F2F1EE;
      --ok: #1C6E48; --ok-soft: #E2F0E8; --warn: #9B6A05; --warn-soft: #F8EED6;
      --bad: #A8291F; --bad-soft: #F8E5E2;
      --sky: #E4EBF0; --sea: #BBD2E0; --sea-deep: #9DBBCD; --bed: #D8D2C4;
      --hull: #43535F; --linea: #6C7F8C;
      --shadow: none;
    }
    .app { box-shadow: none; }
  }
"""

BARRA = """<nav class="barra" aria-label="Índice del documento">
  <span class="marca">Monoboyas</span>
{enlaces}
  <span class="der">
    <button type="button" id="tema" aria-pressed="false">Tema oscuro</button>
    <button type="button" id="abrirPres" class="pres">Presentar</button>
  </span>
</nav>
"""

MANDO = """<div class="mando" role="toolbar" aria-label="Controles de la presentación">
  <button type="button" id="atras" aria-label="Apartado anterior">‹ Atrás</button>
  <button type="button" id="siguiente" aria-label="Apartado siguiente">Siguiente ›</button>
  <span class="cuenta" id="cuenta">1 / 1</span>
  <span class="progreso"><i id="progreso"></i></span>
  <span class="pista">← → para moverse · Esc para salir</span>
  <button type="button" id="salirPres">Salir</button>
</div>
"""

GUION = """<script>
(function () {
  "use strict";

  /* ---- Tema: arranca en claro, para no proyectar en oscuro por accidente ---- */
  var raiz = document.documentElement;
  var btnTema = document.getElementById("tema");
  function ponerTema(t) {
    raiz.setAttribute("data-theme", t);
    btnTema.textContent = t === "dark" ? "Tema claro" : "Tema oscuro";
    btnTema.setAttribute("aria-pressed", String(t === "dark"));
  }
  ponerTema("light");
  btnTema.addEventListener("click", function () {
    ponerTema(raiz.getAttribute("data-theme") === "dark" ? "light" : "dark");
  });

  /* ---- Pasos ----
     Cada bloque con un marco de aplicacion es un paso; los bloques sin marco se
     agrupan con sus vecinos. Un contenedor con varios marcos se reparte por
     dentro. Los nodos se MUEVEN a su envoltorio, nunca se clonan. */
  function envolver(grupo) {
    if (grupo.length === 1) return grupo[0];
    var w = document.createElement("div");
    grupo[0].parentNode.insertBefore(w, grupo[0]);
    grupo.forEach(function (e) { w.appendChild(e); });
    return w;
  }

  function recoger(contenedor, agrupar) {
    var pasos = [], pendientes = [];
    function volcar() {
      if (pendientes.length) { pasos.push(envolver(pendientes)); pendientes = []; }
    }
    Array.prototype.slice.call(contenedor.children).forEach(function (hijo) {
      if (hijo.tagName === "FOOTER") return;   // el pie no da para diapositiva
      var marcos = hijo.querySelectorAll(".app").length;
      if (marcos > 1) { volcar(); pasos = pasos.concat(recoger(hijo, true)); }
      else if (marcos === 1 || !agrupar) { volcar(); pasos.push(hijo); }
      else { pendientes.push(hijo); }
    });
    volcar();
    return pasos;
  }

  // En el nivel superior cada seccion es su propio paso: solo se agrupa
  // dentro de una seccion que haya que repartir por tener varios mockups.
  var pasos = recoger(document.querySelector("main"), false);
  pasos.forEach(function (p) { p.classList.add("paso"); });

  var i = 0, cuerpo = document.body;
  var cuenta = document.getElementById("cuenta");
  var progreso = document.getElementById("progreso");

  function mostrar(n) {
    i = Math.max(0, Math.min(n, pasos.length - 1));
    pasos.forEach(function (p, k) { p.classList.toggle("activo", k === i); });
    Array.prototype.forEach.call(document.querySelectorAll(".visible"), function (e) {
      e.classList.remove("visible");
    });
    for (var a = pasos[i].parentElement; a && a.tagName !== "BODY"; a = a.parentElement) {
      a.classList.add("visible");
    }
    pasos[i].scrollTop = 0;
    cuenta.textContent = (i + 1) + " / " + pasos.length;
    progreso.style.width = ((i + 1) / pasos.length * 100) + "%";
  }

  function entrar() { cuerpo.classList.add("presentando"); mostrar(i); }
  function salir() {
    cuerpo.classList.remove("presentando");
    pasos.forEach(function (p) { p.classList.remove("activo"); });
    Array.prototype.forEach.call(document.querySelectorAll(".visible"), function (e) {
      e.classList.remove("visible");
    });
    pasos[i].scrollIntoView({ block: "start" });
  }

  document.getElementById("abrirPres").addEventListener("click", entrar);
  document.getElementById("salirPres").addEventListener("click", salir);
  document.getElementById("atras").addEventListener("click", function () { mostrar(i - 1); });
  document.getElementById("siguiente").addEventListener("click", function () { mostrar(i + 1); });

  document.addEventListener("keydown", function (e) {
    var escribiendo = /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName) || e.target.isContentEditable;
    if (escribiendo) return;
    if (!cuerpo.classList.contains("presentando")) {
      if (e.key === "p" || e.key === "P") { e.preventDefault(); entrar(); }
      return;
    }
    if (e.key === "ArrowRight" || e.key === "PageDown" || e.key === " ") { e.preventDefault(); mostrar(i + 1); }
    else if (e.key === "ArrowLeft" || e.key === "PageUp") { e.preventDefault(); mostrar(i - 1); }
    else if (e.key === "Escape") { e.preventDefault(); salir(); }
    else if (e.key === "Home") { e.preventDefault(); mostrar(0); }
    else if (e.key === "End") { e.preventDefault(); mostrar(pasos.length - 1); }
  });
})();
</script>
"""


# --------------------------------------------------------------------------- #

def exportar() -> Path:
    if not FUENTE.exists():
        raise ErrorExport(f"no se encuentra la fuente: {FUENTE}")
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

    estilos += ESTILOS_EXPORT

    # 3. Anclas en cada apartado, para que la barra pueda saltar
    puestas = 0
    for ident, rotulo in ANCLAS.items():
        viejo = f'<p class="eyebrow">{rotulo}</p>'
        if viejo in cuerpo:
            cuerpo = cuerpo.replace(viejo, f'<p class="eyebrow" id="{ident}">{rotulo}</p>', 1)
            puestas += 1
    if puestas != len(ANCLAS):
        raise ErrorExport(f"solo se anclaron {puestas} de {len(ANCLAS)} apartados")

    # 4. El contenido pasa a <main>, que es de donde el guion saca los pasos
    cuerpo = cuerpo.replace('<div class="wrap">', '<main class="wrap">', 1)
    if not cuerpo.rstrip().endswith("</div>"):
        raise ErrorExport("el cuerpo no termina como se esperaba")
    cuerpo = cuerpo.rstrip()[: -len("</div>")].rstrip() + "\n</main>"

    enlaces = "\n".join(
        f'  <a href="#{ident}">{rotulo}</a>' for ident, rotulo in APARTADOS
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
{BARRA.format(enlaces=enlaces)}
{cuerpo}
{MANDO}
{GUION}</body>
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
    kb = ruta.stat().st_size // 1024
    print(f"  generado: {ruta.name} · {kb} KB")
