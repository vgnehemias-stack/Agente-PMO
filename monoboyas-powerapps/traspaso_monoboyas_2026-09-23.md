# Acta de traspaso — App de Monoboyas (TAMOIN · Repsol La Pampilla)

**Fecha:** 2026-09-23 · **Repo:** `vgnehemias-stack/Agente-PMO`, rama `claude/blissful-ritchie-s3ewsq`, commit `b2dd3cc` · **Paquete:** `monoboyas-powerapps/`

> Este documento no repite los entregables: los referencia por ruta. Readjúntalo al abrir el chat nuevo.

---

## 1. Objetivo y entregable final

- **Objetivo:** aplicación para **centralizar y consultar** la información del sistema de monoboyas de Repsol La Pampilla. Consulta y trazabilidad, **no ejecución** — la supervisión del trabajo sigue siendo de Repsol.
- **Entregable:** el paquete `monoboyas-powerapps/`, completo y verificado:
  - `01-plan/` — plan maestro v2.0, modelo de datos (9 tablas Dataverse + 2 catálogos), 21 decisiones abiertas.
  - `02-levantamiento/` — 6 plantillas CSV con la jerarquía precargada + `INSTRUCCIONES.md`.
  - `03-mockups/` — documento consolidado de cliente (`mockup-pantallas.html`) + PDF ejecutivo.
  - `04-construccion/` — runbook de 28 pasos para construirlo en Power Platform.
  - `05-prototipo/` — prototipo navegable cargado con los datos reales del levantamiento.
- **Artifacts publicados:**
  - Documento de cliente → `claude.ai/artifact/ESJQuSq58Ugb2HvHcTuWyp`
  - Runbook de construcción → `claude.ai/artifact/VW57WCA1dRFUtBuZiuHA7Q`
  - Prototipo navegable → `claude.ai/artifact/59MQUSdFe1FPjWSHB7RvzJ`

---

## 2. Decisiones y criterios acordados

**Alcance**

- El eje de la app es la **codificación de subsistemas**, **no** la Orden de Trabajo (OT).
- Se eliminó todo lo orientado al perfil ejecutor (partes de trabajo, firmas, avance).
- Recorrido: **vista global → desglose** por subsistema → ficha del nodo con 4 pestañas.
- Lista y esquemático son **la misma vista con distinta visual**: se cambia con un selector presente desde el inicio, no son dos aplicaciones.
- La visualización dinámica va **dentro de la app** (SVG generado con `Concat()`), sin Power BI aparte.

**Plataforma**

- **Power Platform**, no sólo Power Apps: Dataverse (dato), Power Apps (pantallas), Power Automate (avisos y ruta del árbol). El plazo de 12–17 días cubre las tres.

**Formato y tono**

- Tono informativo y ejecutivo, en español, dirigido a gerencia y a Repsol. Sin prometer de más: lo que no está verificado se marca como tal.
- Tema claro para lo impreso; fondo crema hasta el borde de la hoja.
- **«Se genera, no se edita a mano»:** `03-mockups/exportar.py` → HTML autónomo; `03-mockups/generar-pdf.py` → PDF; `05-prototipo/construir-prototipo.py` → prototipo. La fuente única es `mockup-pantallas.html` / `plantilla.html`.

**Supuestos incorporados al diseño** (si alguno es falso, hay que ajustar antes de construir)

- La monoboya es de tipo **CALM**.
- La codificación de subsistemas es **jerárquica**.
- El equipo tiene cuenta corporativa de Microsoft 365.

---

## 3. Datos y cifras clave, con su origen

| Cifra | Archivo | Columna / detalle |
|---|---|---|
| **81 nodos** = 1 monoboya + **12 subsistemas** + **68 equipos** | `02-levantamiento/01_jerarquia_subsistemas.csv` | `nivel` (1/2/3); jerarquía por `codigo_padre` |
| Códigos **provisionales** en uso | mismo archivo | `codigo_oficial` está **vacío**: manda `codigo_provisional` hasta que llegue la codificación real |
| Coordenadas de los 12 puntos del esquema | mismo archivo | `coordenada_x`, `coordenada_y` — **% sobre un viewBox de 660×380** |
| **40 frecuencias** de referencia | `02-levantamiento/02_frecuencias_referencia.csv` | `frecuencia_valor` + `frecuencia_unidad`; `norma_referencia` (OCIMF, API RP 2SK, DICAPI) |
| **27 materiales** | `02-levantamiento/03_catalogo_materiales.csv` | `codigo_interno` es la llave; `codigo_sap` **sin confirmar** |
| **26 vínculos** material–nodo | `02-levantamiento/04_materiales_por_nodo.csv` | `codigo_nodo` + `codigo_material` |
| **26 documentos**, de ellos **13 planos** | `02-levantamiento/05_documentos_planos.csv` | `tipo`; los avisos salen de `fecha_vencimiento` |
| **5 perfiles**, **0 personas nombradas** | `02-levantamiento/06_personal_accesos.csv` | plantilla vacía: `nombre_completo` y `correo` sin rellenar |
| **9 tablas Dataverse + 2 catálogos** | `01-plan/modelo-datos.md` | `Nodo del sistema` es **autorreferenciada** (nodo → nodo padre) |
| **12–17 días** de trabajo · 28 pasos · 7 fases | `04-construccion/runbook-powerapps.html` | sin contar la espera de decisiones |
| **21 decisiones abiertas**, 4 bloqueantes | `01-plan/decisiones-abiertas.md` | D-01 a D-21 |
| PDF: **8 páginas**, A3 vertical, tema claro | `03-mockups/propuesta-monoboyas.pdf` | margen de página 0; el aire lo pone el CSS |

---

## 4. Archivos que hay que readjuntar en el chat nuevo

- **Este acta** (`traspaso_monoboyas_2026-09-23.md`) — primero.
- Los **6 CSV** de `02-levantamiento/` — son el dato vivo.
- `01-plan/plan-maestro.md`, `01-plan/modelo-datos.md`, `01-plan/decisiones-abiertas.md`.
- `03-mockups/mockup-pantallas.html` — fuente única del documento de cliente.
- `04-construccion/runbook-powerapps.html`.
- `05-prototipo/plantilla.html`, `05-prototipo/construir-prototipo.py`, `05-prototipo/_escena.svg`.
- **Atajo:** si el chat nuevo tiene acceso al repositorio, basta con indicar la rama `claude/blissful-ritchie-s3ewsq`; no hace falta adjuntar nada más que este acta.

---

## 5. Enfoques probados y descartados

**De producto**

- **Power BI en paralelo** → descartado: duplicaba licencia y sacaba al usuario de la app. Sustituido por un SVG construido con `Concat()` dentro de Power Apps. (Sigue en el plan como alternativa **sólo** si se pide tendencia histórica — D-20.)
- **Modelo gobernado por la OT** → descartado por el cliente: el eje es la codificación.
- **Alcance de ejecutor** (partes, firmas, avance de trabajo) → eliminado: lo supervisa Repsol.

**Técnicos (verificados, no supuestos)**

- **Galería para los puntos clicables** → no sirve: una galería de Power Apps coloca sus elementos en fila o columna, no en posiciones libres. Solución: un botón transparente por punto. **Consecuencia importante: añadir un subsistema nuevo sí obliga a tocar la pantalla, no basta con añadir una fila.**
- **`Ruta completa` como columna calculada** → imposible: recorrer el árbol hacia arriba es recursivo y Dataverse no lo permite. Se llena en la carga y la mantiene un flujo.
- **PDF de presentación** (`break-before: page` por apartado) → descartado: 20 páginas medio vacías. Se pasó a flujo continuo, 8 páginas.
- **`zoom: 0.84` en los mockups** → empeoraba el empaquetado de páginas; revertido.
- **`break-inside: avoid` dentro de flex/grid** → Chromium lo ignora; por eso se partían los mockups. Solución: esos contenedores pasan a `display: block` al imprimir.
- **Pintar el margen de página por CSS** (`html`, `body` o capa `position: fixed`) → Chromium **nunca** pinta esa franja. Solución: margen de página 0 y el aire dentro del contenido, con **bordes** (no `padding`, que se trunca al cortar la página).
- **`cloneNode` para el modo presentación** → duplicaba la cabecera; se cambió por mover los nodos.

---

## 6. Pendientes inmediatos, por prioridad

1. 🔴 **D-01 · Codificación oficial de subsistemas.** Nada se carga sin ella; hoy todo corre con códigos provisionales. — *TAMOIN Mantenimiento.*
2. 🔴 **D-02 · Tenant: TAMOIN o Repsol.** Define licencias, propiedad del dato y qué pasa al terminar el contrato. Cambiarlo después es una migración completa. — *Gerencia TAMOIN + TI Repsol.*
3. 🔴 **D-03 · Cuántos usuarios y cuántos sólo consultan.** Decide el modelo de licenciamiento (plan por aplicación si la mayoría sólo lee).
4. 🔴 **D-04 · Cuántas monoboyas entran al alcance.** Afecta al levantamiento, no al desarrollo.
5. 🟡 **D-13 · Un responsable nombrado por clase de información.** Es el principal riesgo del proyecto: sin esto la app se desactualiza en meses.
6. ⚪ **Decisión pendiente de la sesión:** el PDF omite dos bloques marcados `data-pdf="omitir"` en `03-mockups/mockup-pantallas.html` (líneas 889 y 1111: la tercera pantalla del esquemático y los fragmentos «Pantallas 06 a 08»). Decidir si se recuperan y regenerar.
7. ⚪ **Correo a gerencia:** falta cerrar la redacción — «Power Apps» (lo que reconocen) frente a «Power Platform» (lo que realmente se construye). Recomendado: nombrar ambos.

---

## 7. Prompt de arranque sugerido para el chat siguiente

```
Retomo el proyecto de la aplicación de monoboyas de TAMOIN para Repsol
La Pampilla. Adjunto el acta de traspaso del 2026-09-23; léela primero.

Contexto en una línea: aplicación de CONSULTA (no de ejecución) sobre
Power Platform, gobernada por la codificación de subsistemas y no por la
OT. El trabajo está en el repositorio vgnehemias-stack/Agente-PMO, rama
claude/blissful-ritchie-s3ewsq, carpeta monoboyas-powerapps/, y todo lo
generado sale de sus scripts: no edites a mano los HTML ni el PDF de
salida.

Lo que necesito ahora: [ELEGIR UNO]
 (a) ya tengo la codificación oficial de subsistemas — recárgala en los
     CSV de 02-levantamiento/ y regenera prototipo y documento;
 (b) prepara la reunión de gerencia sobre el tenant (D-02): opciones,
     coste e implicaciones de cada una;
 (c) empieza la Fase 0 del runbook 04-construccion/runbook-powerapps.html.

Antes de proponer nada, dime qué de lo que hay sigue vigente y qué habría
que rehacer.
```
