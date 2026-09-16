# App de gestión de mantenimiento de Monoboyas — TAMOIN / Repsol

Paquete de diseño para la aplicación en Power Apps que gestionará el mantenimiento de las
monoboyas (SPM tipo CALM) de Repsol — Refinería La Pampilla.

**Estado:** propuesta v1.0, pendiente de validación en Fase 0.
**Prototipo publicado:** https://claude.ai/artifact/ESJQuSq58Ugb2HvHcTuWyp

---

## Qué resuelve

Une en un solo recorrido lo que hoy vive disperso entre Excel, el almacén y el teléfono de alguien:

```
frecuencia de mantenimiento → sistemas planificados → materiales que requiere cada intervención
   → ¿hay stock? → solicitud y código de reserva → ejecución con evidencia → historial trazable
```

## Decisiones tomadas

| Decisión | Elección |
|---|---|
| Backend | **Dataverse** (requiere licencia Power Apps Premium) |
| Inventario / ERP | **App autónoma, sin integración SAP.** El código de reserva se registra manualmente |
| Offline | **No requerido** |
| Aplicaciones | Canvas para campo + model-driven para back-office |

---

## Contenido

### `01-plan/` — Documentación de diseño

| Archivo | Qué contiene |
|---|---|
| [`plan-maestro.md`](01-plan/plan-maestro.md) | Problema, alcance, arquitectura, automatizaciones, pantallas, fases, riesgos |
| [`modelo-datos.md`](01-plan/modelo-datos.md) | Las 16 tablas de Dataverse con campos, tipos, relaciones, máquina de estados y roles de seguridad |
| [`decisiones-abiertas.md`](01-plan/decisiones-abiertas.md) | Las 20 preguntas sin responder, con responsable sugerido, y los supuestos que estamos haciendo |

### `02-levantamiento/` — Plantillas para el equipo ⭐

**Este es el entregable accionable.** Siete CSV que el equipo de mantenimiento llena durante la
Fase 0. Empieza por [`INSTRUCCIONES.md`](02-levantamiento/INSTRUCCIONES.md).

| Archivo | Filas precargadas | Qué recoge |
|---|---|---|
| `01_jerarquia_activos.csv` | 68 equipos en 12 sistemas | Terminal ▸ Monoboya ▸ Sistema ▸ Equipo con TAG |
| `02_planes_mantenimiento.csv` | 40 planes | Frecuencias, duración, especialidad, norma |
| `03_gamas_tareas.csv` | 49 pasos (6 planes de ejemplo) | Los checklists paso a paso |
| `04_catalogo_materiales.csv` | 36 materiales | Código SAP, plazo de reposición, stock mínimo |
| `05_materiales_por_plan.csv` | 54 líneas (25 planes) | Qué consume cada mantenimiento |
| `06_personal_roles.csv` | vacío, solo roles | Quién usa la app y con qué permisos |
| `07_documentos_certificados.csv` | 12 documentos | Certificados y sus vencimientos |

### `03-mockups/` — Prototipo visual

[`mockup-pantallas.html`](03-mockups/mockup-pantallas.html) — las siete pantallas del técnico de
campo renderizadas, más el circuito completo, el modelo de datos y la ruta de fases. Es el mismo
archivo que está publicado como artifact para presentar.

Ábrelo en cualquier navegador, no necesita servidor.

---

## ⚠️ Nada aquí es todavía un dato confirmado

Los 12 sistemas, los 68 equipos, los 40 planes y las frecuencias precargadas son una **propuesta**
armada a partir de la configuración estándar de una monoboya tipo CALM y de las guías del sector
(OCIMF SMOG, OCIMF GMPHOM 2009, OCIMF MEG4, API RP 2SK).

Se entregan precargados porque corregir una lista es mucho más rápido que escribirla desde cero.
Cada línea va marcada como `PROPUESTA - VALIDAR` en su columna `observaciones`, y ninguna entra a
la aplicación sin la firma de quien conoce el activo.

---

## Siguiente paso

1. Responder las **cuatro preguntas bloqueantes** de
   [`decisiones-abiertas.md`](01-plan/decisiones-abiertas.md) — sobre todo en qué tenant de
   Microsoft 365 vive la solución.
2. Taller con el equipo de mantenimiento para validar la jerarquía de sistemas y repartir las
   plantillas con responsable y fecha.
3. Con las plantillas cerradas, arranca la Fase 1.

## Verificar la integridad de las plantillas

Al recibir las plantillas llenas, este comando comprueba que los códigos cruzados existen:

```bash
cd monoboyas-powerapps/02-levantamiento && python3 - <<'PY'
import csv, glob
col = lambda f, c: {r[c].strip() for r in csv.DictReader(open(f, newline='', encoding='utf-8')) if r[c].strip()}
tags   = col('01_jerarquia_activos.csv', 'tag_equipo')
planes = col('02_planes_mantenimiento.csv', 'codigo_plan')
mats   = col('04_catalogo_materiales.csv', 'codigo_interno')
for nombre, faltan in [
    ('TAG de planes',      col('02_planes_mantenimiento.csv', 'tag_equipo') - tags),
    ('Planes de gamas',    col('03_gamas_tareas.csv', 'codigo_plan') - planes),
    ('Planes de BOM',      col('05_materiales_por_plan.csv', 'codigo_plan') - planes),
    ('Materiales de BOM',  col('05_materiales_por_plan.csv', 'codigo_material') - mats),
    ('TAG de documentos',  col('07_documentos_certificados.csv', 'tag_equipo') - tags)]:
    print(f"{'OK   ' if not faltan else 'FALLA'} {nombre}", sorted(faltan) or '')
PY
```
