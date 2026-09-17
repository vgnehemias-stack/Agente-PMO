#!/usr/bin/env python3
"""Arma el prototipo navegable con los datos reales del levantamiento.

Lee los seis CSV de `02-levantamiento/`, los inyecta en `plantilla.html` y
produce dos archivos:

  prototipo-monoboyas.html          fragmento para publicar como artifact
  prototipo-monoboyas-offline.html  documento completo, con las tipografias
                                    incrustadas, para abrir con doble clic

    python3 construir-prototipo.py

Los datos del levantamiento y los de ejemplo viajan separados: el prototipo
solo usa los de ejemplo cuando se activa el conmutador, y lo dice.
"""

import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).parent
PAQUETE = AQUI.parent
DATOS = PAQUETE / "02-levantamiento"
PLANTILLA = AQUI / "plantilla.html"
ESCENA = AQUI / "_escena.svg"
SALIDA = AQUI / "prototipo-monoboyas.html"
SALIDA_OFFLINE = AQUI / "prototipo-monoboyas-offline.html"

# Reutiliza el incrustador de tipografias del exportador del mockup
sys.path.insert(0, str(PAQUETE / "03-mockups"))
from exportar import incrustar_tipografias  # noqa: E402

HOY = dt.date.today()


class ErrorPrototipo(Exception):
    """Falta algo para armar el prototipo."""


def leer(nombre):
    ruta = DATOS / nombre
    if not ruta.exists():
        raise ErrorPrototipo(f"falta {ruta.name}")
    with open(ruta, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def limpiar(v):
    """Las observaciones del tipo PROPUESTA - VALIDAR no son dato: se omiten."""
    v = (v or "").strip()
    return "" if v.upper().startswith("PROPUESTA") else v


def recoger():
    nodos_csv = leer("01_jerarquia_subsistemas.csv")
    frec_csv = leer("02_frecuencias_referencia.csv")
    mat_csv = leer("03_catalogo_materiales.csv")
    mxn_csv = leer("04_materiales_por_nodo.csv")
    doc_csv = leer("05_documentos_planos.csv")

    # El codigo oficial manda; mientras no exista se usa el provisional
    cod = lambda r: (r.get("codigo_oficial") or "").strip() or r["codigo_provisional"].strip()

    nodos = [{
        "c": cod(n),
        "n": n["nombre"].strip(),
        "p": n["codigo_padre"].strip(),
        "niv": int(n["nivel"]),
        "tipo": n["tipo_nodo"].strip(),
        "crit": n["criticidad"].strip(),
        "est": n["estado"].strip(),
        "ubi": n["ubicacion_fisica"].strip(),
        "buzo": n["requiere_buzo_rov"].strip(),
        "x": float(n["coordenada_x"]) if n["coordenada_x"].strip() else None,
        "y": float(n["coordenada_y"]) if n["coordenada_y"].strip() else None,
    } for n in nodos_csv]

    materiales = {m["codigo_interno"].strip(): {
        "sap": limpiar(m["codigo_sap"]),
        "desc": m["descripcion"].strip(),
        "un": m["unidad"].strip(),
        "cat": m["categoria"].strip(),
        "crit": m["criticidad"].strip(),
        "lead": int(m["lead_time_dias"] or 0),
        "min": float(m["stock_minimo"] or 0),
        "max": float(m["stock_maximo"] or 0),
    } for m in mat_csv}

    mat_nodo = [{"nodo": r["codigo_nodo"].strip(), "mat": r["codigo_material"].strip(),
                 "cant": r["cantidad_referencial"].strip()} for r in mxn_csv]

    frecuencias = [{"nodo": f["codigo_nodo"].strip(), "desc": f["descripcion"].strip(),
                    "tipo": f["tipo"].strip(), "val": f["frecuencia_valor"].strip(),
                    "uni": f["frecuencia_unidad"].strip(),
                    "ultima": limpiar(f["fecha_ultima_ejecucion"]),
                    "norma": limpiar(f["norma_referencia"])} for f in frec_csv]

    # k identifica cada documento: es la llave que usan los datos de ejemplo
    documentos = [{"k": i, "nodo": d["codigo_nodo"].strip(), "nombre": d["nombre_documento"].strip(),
                   "tipo": d["tipo"].strip(), "emisor": limpiar(d["entidad_emisora"])}
                  for i, d in enumerate(doc_csv)]

    return nodos, materiales, mat_nodo, frecuencias, documentos


def datos_de_ejemplo(nodos, materiales, documentos):
    """Valores inventados, solo para demostrar avisos y semaforo.

    Van aparte a proposito: el prototipo nunca los mezcla con los del
    levantamiento sin que el usuario active el conmutador.
    """
    dia = lambda n: (HOY + dt.timedelta(days=n)).isoformat()

    # Unas pocas fichas tecnicas, para que se vea el contraste con las vacias
    tecnico = {}
    plantillas = [
        ("Rodamiento principal", "SKF", "241/850 ECA/W33", "RB-4471-A", "2019-04-12"),
        ("Mesa giratoria", "SBM Offshore", "TT-1600", "TT-0932", "2019-04-12"),
        ("Swivel de producto", "Framo", "PS-16-A", "SW-2210", "2019-05-03"),
        ("Luz de navegación principal", "Sabik", "M850", "LN-7781", "2021-11-20"),
        ("Panel solar", "Sabik", "SP-85", "PS-3120", "2021-11-20"),
    ]
    for nombre, fab, mod, ser, inst in plantillas:
        for n in nodos:
            if n["n"].lower().startswith(nombre.lower()):
                tecnico[n["c"]] = {"fab": fab, "mod": mod, "ser": ser, "inst": inst}
                break

    # Stock: la mayoria holgado, dos por debajo del minimo
    stock, bajos = {}, {"MAT-004", "MAT-002"}
    for k, m in materiales.items():
        minimo = m["min"]
        stock[k] = {"disp": max(0, int(minimo * 0.5)) if k in bajos else int(minimo * 2.4) + 3}

    # Vencimientos: uno vencido, dos por vencer, el resto vigentes.
    # Los planos y manuales no vencen, asi que se quedan sin fecha.
    vence, sin_vencimiento = {}, {"Plano", "Manual", "Memoria tecnica"}
    caducan = [d for d in documentos if d["tipo"] not in sin_vencimiento]
    for i, d in enumerate(caducan):
        if i == 0:
            vence[d["k"]] = dia(-12)
        elif i in (1, 2):
            vence[d["k"]] = dia(18 + i * 9)
        else:
            vence[d["k"]] = dia(220 + i * 31)

    return {"tecnico": tecnico, "stock": stock, "vence": vence}


def construir():
    if not PLANTILLA.exists():
        raise ErrorPrototipo(f"falta {PLANTILLA.name}")
    if not ESCENA.exists():
        raise ErrorPrototipo(f"falta {ESCENA.name}")

    nodos, materiales, mat_nodo, frecuencias, documentos = recoger()
    ejemplo = datos_de_ejemplo(nodos, materiales, documentos)

    paquete = {
        "hoy": HOY.isoformat(),
        "escena": ESCENA.read_text(encoding="utf-8").strip(),
        "nodos": nodos,
        "materiales": materiales,
        "matNodo": mat_nodo,
        "frecuencias": frecuencias,
        "documentos": documentos,
        "ejemplo": ejemplo,
    }

    plantilla = PLANTILLA.read_text(encoding="utf-8")
    if "/*DATOS*/" not in plantilla:
        raise ErrorPrototipo("la plantilla no tiene el marcador /*DATOS*/")
    fragmento = plantilla.replace("/*DATOS*/", json.dumps(paquete, ensure_ascii=False), 1)
    SALIDA.write_text(fragmento, encoding="utf-8")

    # --- version autonoma, para abrir con doble clic ---
    m = re.search(r'<link rel="stylesheet" href="([^"]+)">\n?', fragmento)
    url_css = m.group(1).replace("&amp;", "&")
    cuerpo = fragmento.replace(m.group(0), "")
    cuerpo = re.sub(r"<title>.*?</title>\n?", "", cuerpo, count=1)

    caras = incrustar_tipografias(url_css)
    if caras:
        cuerpo = cuerpo.replace("<style>", "<style>\n" + caras, 1)
        enlace = ""
    else:
        enlace = f'\n  <link rel="stylesheet" href="{url_css}">'
        print("  aviso: sin tipografias incrustadas, necesitara internet", file=sys.stderr)

    SALIDA_OFFLINE.write_text(f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Prototipo de Monoboyas</title>
  <meta name="description" content="Prototipo navegable de la aplicacion de monoboyas de TAMOIN para Repsol.">
  <meta name="color-scheme" content="light dark">{enlace}
</head>
<body style="margin:0">
{cuerpo}
</body>
</html>
""", encoding="utf-8")

    return paquete


if __name__ == "__main__":
    try:
        p = construir()
    except ErrorPrototipo as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    niveles = {}
    for n in p["nodos"]:
        niveles[n["niv"]] = niveles.get(n["niv"], 0) + 1
    print(f"  datos: {len(p['nodos'])} nodos ({niveles.get(2, 0)} subsistemas, "
          f"{niveles.get(3, 0)} equipos) · {len(p['materiales'])} materiales · "
          f"{len(p['frecuencias'])} frecuencias · {len(p['documentos'])} documentos")
    print(f"  ejemplo: {len(p['ejemplo']['tecnico'])} fichas técnicas · "
          f"{len(p['ejemplo']['vence'])} vencimientos")
    print(f"  generado: {SALIDA.name} · {SALIDA.stat().st_size // 1024} KB")
    print(f"  generado: {SALIDA_OFFLINE.name} · {SALIDA_OFFLINE.stat().st_size // 1024} KB")
