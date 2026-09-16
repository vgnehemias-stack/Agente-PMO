# App de consulta centralizada del sistema de Monoboya — TAMOIN / Repsol

Paquete de diseño para la aplicación en Power Apps que centralizará la información del sistema de
monoboya (SPM tipo CALM) de Repsol — Refinería La Pampilla.

**Estado:** propuesta v2.0, pendiente de validación en Fase 0.
**Prototipo publicado:** https://claude.ai/artifact/ESJQuSq58Ugb2HvHcTuWyp

---

## Qué es

Un repositorio navegable del sistema de monoboya, organizado por la **codificación de
subsistemas** que ya existe: una vista global primero, y desde ahí el desglose hasta el detalle de
cada parte.

```
Vista global  →  Subsistema  →  Equipo/Componente
                                  └─ Técnico · Materiales · Frecuencias · Documentos y planos
```

**Informar, no ejecutar.** La supervisión del trabajo la lleva Repsol.

| La app **sí** | La app **no** |
|---|---|
| Muestra el árbol del sistema por código de subsistema | Genera órdenes de trabajo |
| Da la ficha técnica de cada parte | Lleva checklists de ejecución |
| Dice qué repuestos corresponden y si hay existencias | Registra firmas, horas ni avance físico |
| Informa cada cuánto corresponde mantener, como referencia | Programa ni dispara mantenimientos |
| Guarda planos y certificados, y avisa de vencimientos | Valoriza ni factura |
| Permite **actualizar** materiales, stock y documentos | Gestiona permisos de trabajo ni HSE |

## Decisiones tomadas

| Decisión | Elección |
|---|---|
| Eje de identificación | **Código de subsistema** de la codificación existente |
| Backend | **Dataverse** (requiere licencia Power Apps Premium) |
| Tipo de aplicación | **Una sola app model-driven**, escritorio y móvil |
| Inventario / ERP | Autónomo, sin integración SAP. El código de reserva se registra manualmente |
| Offline | No requerido |
| Vista sinóptica gráfica | No se construye |

---

## 🔴 Bloqueante: la codificación oficial

Toda la estructura gira alrededor del código de subsistema. **Esa codificación existe del lado de
TAMOIN y todavía no está en este paquete.**

Mientras tanto, cada nodo lleva un `codigo_provisional` (`MB-01.S02.ROD-001`) que sostiene el
árbol. Al recibir la codificación oficial se reemplazan las referencias en todos los archivos de
una sola pasada. **Hasta entonces no se carga nada a la aplicación.**

El modelo usa un **árbol auto-referenciado**, así que absorbe la codificación real tenga los
niveles que tenga, sin rehacerse.

---

## Contenido

### `01-plan/` — Documentación de diseño

| Archivo | Qué contiene |
|---|---|
| [`plan-maestro.md`](01-plan/plan-maestro.md) | Propósito, alcance, arquitectura, pantallas, fases, riesgos |
| [`modelo-datos.md`](01-plan/modelo-datos.md) | Las 9 tablas de Dataverse, el árbol auto-referenciado, perfiles de acceso y qué se puede editar |
| [`decisiones-abiertas.md`](01-plan/decisiones-abiertas.md) | Las 19 preguntas sin responder y los supuestos incorporados al diseño |

### `02-levantamiento/` — Plantillas para el equipo ⭐

**El entregable accionable.** Seis CSV que el equipo completa en Fase 0. Empieza por
[`INSTRUCCIONES.md`](02-levantamiento/INSTRUCCIONES.md).

| Archivo | Precargado | Qué recoge |
|---|---|---|
| `01_jerarquia_subsistemas.csv` | 81 nodos | El árbol: 1 monoboya + 12 subsistemas + 68 equipos |
| `02_frecuencias_referencia.csv` | 40 | Cada cuánto corresponde mantener, como dato informativo |
| `03_catalogo_materiales.csv` | 27 | Repuestos y consumibles, con código SAP y plazo de reposición |
| `04_materiales_por_nodo.csv` | 26 | Qué repuesto corresponde a qué parte del sistema |
| `05_documentos_planos.csv` | 26 (13 planos) | Planos, manuales, certificados e informes con su vigencia |
| `06_personal_accesos.csv` | vacío | Quién consulta y quién actualiza |

### `03-mockups/` — Prototipo visual

[`mockup-pantallas.html`](03-mockups/mockup-pantallas.html) — las siete pantallas de la
aplicación, el árbol del sistema, el modelo de datos y la ruta de fases. Es el mismo archivo
publicado como artifact. Se abre en cualquier navegador, sin servidor.

---

## ⚠️ Nada aquí es todavía un dato confirmado

Los 12 subsistemas, los 68 equipos, las 40 frecuencias y los 26 documentos precargados son una
**propuesta** armada a partir de la configuración estándar de una monoboya tipo CALM y de las guías
del sector (OCIMF SMOG, OCIMF GMPHOM 2009, OCIMF MEG4, API RP 2SK).

Se entregan precargados porque corregir una lista es mucho más rápido que escribirla desde cero.
Cada línea va marcada como `PROPUESTA - VALIDAR` en su columna `observaciones`.

---

## Siguiente paso

1. **Compartir la codificación oficial de subsistemas.** Es lo primero y bloquea la carga.
2. Responder las otras tres preguntas bloqueantes de
   [`decisiones-abiertas.md`](01-plan/decisiones-abiertas.md) — sobre todo en qué tenant de
   Microsoft 365 vive la solución.
3. Taller con el equipo: validar la navegación sobre el prototipo, contrastar la jerarquía contra
   la codificación real y repartir las plantillas con responsable y fecha.

---

## Verificar la integridad de las plantillas

Al recibir las plantillas llenas, este comando comprueba que el árbol cierra y que los códigos
cruzados existen:

```bash
cd monoboyas-powerapps/02-levantamiento && python3 - <<'PY'
import csv
rows = list(csv.DictReader(open('01_jerarquia_subsistemas.csv', newline='', encoding='utf-8')))
cods = {r['codigo_provisional'] for r in rows}
padres = {r['codigo_provisional']: r['codigo_padre'] for r in rows}

def ciclo(c):
    visto = set()
    while padres.get(c):
        if c in visto: return True
        visto.add(c); c = padres[c]
    return False

col = lambda f, c: {r[c].strip() for r in csv.DictReader(open(f, newline='', encoding='utf-8')) if r[c].strip()}
pruebas = [
    ('Sin huerfanos',        {r['codigo_provisional'] for r in rows if r['codigo_padre'] and r['codigo_padre'] not in cods}),
    ('Sin ciclos',           {c for c in cods if ciclo(c)}),
    ('Una sola raiz',        set() if sum(1 for r in rows if not r['codigo_padre']) == 1 else {'revisar raices'}),
    ('Codigo oficial completo', {r['codigo_provisional'] for r in rows if not r['codigo_oficial'].strip()}),
    ('Nodos de frecuencias', col('02_frecuencias_referencia.csv','codigo_nodo') - cods),
    ('Nodos de materiales',  col('04_materiales_por_nodo.csv','codigo_nodo') - cods),
    ('Materiales asociados', col('04_materiales_por_nodo.csv','codigo_material') - col('03_catalogo_materiales.csv','codigo_interno')),
    ('Nodos de documentos',  col('05_documentos_planos.csv','codigo_nodo') - cods),
]
for nombre, mal in pruebas:
    print(f"{'OK   ' if not mal else 'FALLA'} {nombre}", sorted(mal)[:5] if mal else '')
PY
```
