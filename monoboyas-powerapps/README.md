# App de consulta centralizada del sistema de Monoboya — TAMOIN / Repsol

Paquete de diseño para la aplicación en Power Apps que centralizará la información del sistema de
monoboya (SPM tipo CALM) de Repsol — Refinería La Pampilla.

**Estado:** propuesta v4.0, pendiente de validación en Fase 0.
**Documento para el cliente:** https://claude.ai/artifact/ESJQuSq58Ugb2HvHcTuWyp

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
| Muestra un **esquema interactivo** de la monoboya dentro de la propia app | Necesita un Power BI aparte |

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
| `01_jerarquia_subsistemas.csv` | 81 nodos | El árbol: 1 monoboya + 12 subsistemas + 68 equipos, con las coordenadas de cada subsistema sobre el esquema |
| `02_frecuencias_referencia.csv` | 40 | Cada cuánto corresponde mantener, como dato informativo |
| `03_catalogo_materiales.csv` | 27 | Repuestos y consumibles, con código SAP y plazo de reposición |
| `04_materiales_por_nodo.csv` | 26 | Qué repuesto corresponde a qué parte del sistema |
| `05_documentos_planos.csv` | 26 (13 planos) | Planos, manuales, certificados e informes con su vigencia |
| `06_personal_accesos.csv` | vacío | Quién consulta y quién actualiza |

### El panel visual

La visualización dinámica vive **dentro de la misma aplicación**, no en un Power BI aparte: una
página con la lista de subsistemas a la izquierda y el esquema de la monoboya a la derecha,
sincronizados en las dos direcciones. Lo que evita que se vuelva inmanejable es que **las
posiciones de los puntos se guardan como dato** (`coordenada_x`, `coordenada_y` en la tabla del
nodo): mover un punto es cambiar un número desde la propia ficha, y el color de cada marca sale del
estado de su información. El clic sobre cada punto sí necesita un botón por subsistema — el matiz
está explicado en el plan maestro y en el runbook.

Power BI queda reservado para lo único que Dataverse no puede — **tendencia en el tiempo** — y aun
entonces se embebe como un panel más de la app. Detalle y limitaciones en
[`plan-maestro.md`](01-plan/plan-maestro.md), sección 6 bis.

### `05-prototipo/` — Prototipo navegable ⭐

[`prototipo-monoboyas-offline.html`](05-prototipo/prototipo-monoboyas-offline.html) — **la app se
puede usar, no solo ver.** Publicado en https://claude.ai/artifact/59MQUSdFe1FPjWSHB7RvzJ

Funciona con los **datos reales del levantamiento**: 12 subsistemas, 68 equipos, 27 materiales,
40 frecuencias y 26 documentos. Se navega de la vista global al subsistema y de ahí a la ficha del
equipo, con sus cuatro pestañas; el selector *Ver como* cambia entre lista y esquema, y los puntos
del esquema se tocan.

Los campos técnicos salen **vacíos a propósito**: es justo lo que falta por llenar en la Fase 0.
El botón **Datos de ejemplo** añade fechas y stock inventados para ver los avisos y el semáforo,
sin mezclarlos nunca con los reales.

```bash
cd monoboyas-powerapps/05-prototipo && python3 construir-prototipo.py
```

### `04-construccion/` — Runbook de construcción ⭐

[`runbook-powerapps.html`](04-construccion/runbook-powerapps.html) — **la guía para quien se siente
a construir.** 28 pasos en 7 fases, escrita para alguien sin experiencia previa en Power Platform.
Publicada en https://claude.ai/artifact/VW57WCA1dRFUtBuZiuHA7Q

Cada paso dice **dónde** se hace, **qué** hay que hacer, **qué se debe ver al terminar** y cuánto
tarda. Incluye las fórmulas del panel visual, las diez trampas que hacen perder días, un glosario
de los términos que la plataforma da por sabidos, y las cuatro cosas donde conviene pedir ayuda.

Esfuerzo estimado: **12–17 días de trabajo**, sin contar la espera de decisiones.

### `03-mockups/` — Documento consolidado para el cliente ⭐

[`mockup-pantallas.html`](03-mockups/mockup-pantallas.html) — **es el entregable que se presenta**.
Reúne toda la propuesta en una sola página navegable, publicada además como artifact:

| | |
|---|---|
| 01 · El problema | Qué resuelve y qué deliberadamente no hace |
| 02 · La estructura | El árbol del sistema y por qué se modela así |
| 03 · Qué verá el equipo | Las nueve pantallas y el recorrido entre ellas |
| 04 · Las dinámicas | Navegación, sincronía, quién actualiza qué, avisos y auditoría |
| 05 · Cómo se construye | Arquitectura, los tres niveles de visualización y las nueve tablas |
| 06 · La ruta | Las seis fases y qué se necesita del cliente para arrancar |

Se abre en cualquier navegador, sin servidor.

### Para presentar: `propuesta-monoboyas.html` ⭐

[`03-mockups/propuesta-monoboyas.html`](03-mockups/propuesta-monoboyas.html) — **el archivo que se
lleva a la reunión.** Es el mismo documento, convertido en un HTML completo y autónomo:

- Se abre con **doble clic** y funciona **sin internet**: las tipografías van incrustadas y no
  pide nada a la red.
- **Barra superior** con el índice, para saltar a cualquier apartado cuando alguien pregunte.
- **Modo presentación**: la tecla `P` o el botón *Presentar* pasa a pantalla completa y avanza
  apartado por apartado — `→` y `←` para moverse, `Esc` para salir. Son 22 pasos, con un mockup
  por paso.
- Arranca en **tema claro** aunque el equipo esté en oscuro, con conmutador en la barra.

Pesa 470 KB: se envía por correo sin problema.

### Y en PDF: `propuesta-monoboyas.pdf`

[`03-mockups/propuesta-monoboyas.pdf`](03-mockups/propuesta-monoboyas.pdf) — el mismo documento en
**A3 vertical y tema claro**, 11 páginas. El contenido corre en flujo continuo —varios apartados
por hoja, como un documento y no como una presentación impresa— y ningún mockup queda partido
entre dos páginas.

Se eligió A3 porque el diseño mide 1180 px de ancho: en A4 habría que encogerlo a dos tercios y los
mockups quedarían ilegibles. Para papel corriente, `python3 generar-pdf.py --a4`.

**Se genera, no se edita a mano.** Si cambia la propuesta, se vuelven a ejecutar los dos, en orden:

```bash
cd monoboyas-powerapps/03-mockups
python3 exportar.py        # el HTML autónomo
python3 generar-pdf.py     # el PDF, a partir del HTML
```

Así el artifact publicado y el archivo para presentar no se separan nunca. La fuente sigue siendo
`mockup-pantallas.html`.

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
