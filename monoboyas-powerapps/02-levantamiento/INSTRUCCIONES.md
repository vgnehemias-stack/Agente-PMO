# Plantillas de levantamiento — Instrucciones

Estas siete plantillas recogen la información que la aplicación necesita para funcionar. Son el
**entregable de la Fase 0** y son bloqueantes: sin ellas no hay nada que planificar.

---

## ⚠️ Lo primero que tienes que saber

Las plantillas vienen **precargadas con una propuesta**, no con datos reales. Todo lo precargado
está marcado en la columna `observaciones` con **`PROPUESTA - VALIDAR`**.

**Nada de eso es dato confirmado.** Es una monoboya tipo CALM genérica, armada a partir de la
configuración estándar del sector. Sirve para que no partas de una hoja en blanco — corregir una
lista es mucho más rápido que inventarla.

Tu trabajo es:

1. **Corregir** lo que está mal.
2. **Borrar** las filas que no aplican a nuestra monoboya.
3. **Agregar** lo que falta.
4. **Vaciar la columna `observaciones`** de cada fila que ya validaste. Cuando no quede ningún
   `PROPUESTA - VALIDAR` en el archivo, ese archivo está listo.

Esa última regla es la que nos permite medir el avance sin preguntar.

---

## Orden de llenado

Hay dependencias entre archivos. Llénalos en este orden:

```
1. 01_jerarquia_activos.csv      ──► define los TAG
2. 04_catalogo_materiales.csv    ──► define los códigos de material
3. 02_planes_mantenimiento.csv   ──► usa los TAG de (1)
4. 03_gamas_tareas.csv           ──► usa los planes de (3)
5. 05_materiales_por_plan.csv    ──► usa (3) y (2)
6. 06_personal_roles.csv         ──► independiente
7. 07_documentos_certificados.csv──► usa los TAG de (1)
```

---

## Archivo por archivo

### 1. `01_jerarquia_activos.csv` — La base de todo

Define la jerarquía `Terminal ▸ Monoboya ▸ Sistema ▸ Equipo`. **68 equipos precargados en 12
sistemas.**

| Columna | Qué poner |
|---|---|
| `tag_equipo` | **El campo más importante del proyecto.** Identificador único del equipo. Si ya existe una convención de TAG en uso, úsala y avísanos — la propuesta `MB01-XXX-000` es solo un punto de partida |
| `criticidad_equipo` | `A` = su falla para la operación · `B` = la degrada · `C` = no la afecta |
| `ubicacion_fisica` | `Cubierta` / `Casco` / `Interior` / `Superficie` / `Submarino` / `Fondo marino` |
| `requiere_buzo_rov` | `SI` / `NO`. Determina la logística y el costo de cada intervención |
| `fabricante`, `modelo`, `n_serie` | Sácalo de la placa del equipo o del manual. Si no lo hay, déjalo vacío — **no lo inventes** |

> **Decisión pendiente:** el número de líneas de fondeo (precargamos 6) y de tramos de manguera
> flotante (precargamos 4 + tail hose) es una suposición. Corrígelo según la configuración real.

### 2. `04_catalogo_materiales.csv` — Qué se consume

**36 materiales precargados.**

| Columna | Qué poner |
|---|---|
| `codigo_sap` | **Crítico.** Es el único puente con SAP, ya que no hay integración automática. Si no lo tienes a mano, pídelo a almacén antes de cerrar el archivo |
| `lead_time_dias` | Días desde que se pide hasta que llega. Manguera importada ≠ trapo industrial. Es lo que permite avisar con tiempo |
| `stock_minimo` | Por debajo de este número salta la alerta. Regla práctica: consumo durante el `lead_time` + un margen |
| `categoria` | `Repuesto` / `Consumible` / `Herramienta` / `EPP` / `Servicio` |

> Los `Servicio` (embarcación, cuadrilla de buceo) van con stock 0: no se almacenan, se contratan
> por evento. Están en el catálogo para poder planificarlos y costearlos.

### 3. `02_planes_mantenimiento.csv` — Frecuencias

**40 planes precargados.** Este archivo responde *"¿qué se mantiene y cada cuánto?"*.

| Columna | Qué poner |
|---|---|
| `frecuencia_valor` + `frecuencia_unidad` | Separados a propósito: "cada 3 `Meses`", no "cada 90 días". Así respetamos el mes calendario, que es como lo piensa el equipo |
| `tipo` | `Preventivo` / `Predictivo` / `Inspeccion legal` / `Lubricacion` / `Limpieza` |
| `requiere_parada` | ¿Obliga a detener la operación de carga/descarga? Cambia por completo la planificación |
| `norma_referencia` | OCIMF SMOG, GMPHOM 2009, MEG4, API RP 2SK, DICAPI, manual del fabricante… Déjalo vacío si no hay norma |
| `fecha_ultima_ejecucion` | Si la sabes, ponla: la app calcula la próxima a partir de ahí. Si no, la app arrancará desde la fecha de carga |

> **Las frecuencias precargadas son las típicas del sector, no las nuestras.** Es lo que más hay
> que revisar de todo el paquete. Si Repsol o el fabricante exigen otra frecuencia, manda esa.

### 4. `03_gamas_tareas.csv` — Los checklists

**49 pasos precargados, pero solo para 6 planes de ejemplo** (PM-001, PM-002, PM-003, PM-011,
PM-018, PM-024). Están elegidos para mostrar todos los tipos de registro. **Faltan los otros 34
planes** — esa es la parte gruesa del trabajo.

| `tipo_registro` | Qué muestra la app | Cuándo usarlo |
|---|---|---|
| `OK/NO OK` | Un interruptor | Verificaciones de sí o no |
| `Numerico` | Teclado numérico con validación de rango | Mediciones. Llena `valor_minimo`, `valor_maximo` y `unidad` |
| `Texto` | Campo de texto | Observaciones |
| `Foto` | Cámara | Evidencia gráfica |
| `Firma` | Panel de firma | Cierre de responsabilidad |
| `Seleccion` | Lista desplegable | Opciones fijas. Escríbelas en `ayuda` |

**Consejos para escribir una buena gama:**

- Un paso = una acción verificable. Si el paso dice "revisar todo", no sirve.
- Los rangos (`valor_minimo` / `valor_maximo`) son los que hacen que la app avise sola cuando algo
  está fuera de norma. Vale la pena el esfuerzo de definirlos.
- Usa `ayuda` para lo que un técnico nuevo necesitaría preguntar. Es la memoria del equipo.
- `obligatorio = SI` bloquea el cierre de la orden. Úsalo con criterio: si todo es obligatorio, el
  técnico se queda trabado en campo por una tontería.

### 5. `05_materiales_por_plan.csv` — La pieza clave

**54 líneas precargadas para 25 de los 40 planes.**

Este archivo es el que hace posible la pregunta central del proyecto:

> *"¿Tengo los repuestos para los mantenimientos del próximo mes?"*

Sin él, la app sabe qué mantener y sabe qué hay en almacén, pero **no puede cruzar ambas cosas**.
Es el archivo que más valor aporta por línea llenada.

- `cantidad_por_ejecucion`: lo que se consume **cada vez** que se ejecuta el plan.
- Si un material solo se usa a veces (p. ej. se reemplaza un perno solo si está dañado), ponlo con
  cantidad `0` y `obligatorio = NO`. Queda registrado como material posible sin bloquear la orden.
- `obligatorio = SI` significa que **sin ese material la orden no se libera**.

### 6. `06_personal_roles.csv` — Quién usa la app

Viene **vacío**, solo con la estructura de roles. Se necesita el correo corporativo de Microsoft
365 de cada persona: es lo que vincula a la persona con su identidad y con sus permisos.

| Rol | Qué puede hacer |
|---|---|
| `Tecnico` | Ejecuta sus órdenes, reporta hallazgos, solicita materiales |
| `Supervisor` | Libera y cierra órdenes, aprueba solicitudes, firma |
| `Planificador` | Crea y edita planes, gamas y BOM |
| `Almacenero` | Registra movimientos de inventario y códigos de reserva |
| `Administrador` | Todo |

### 7. `07_documentos_certificados.csv` — Vencimientos

**12 documentos precargados.** La columna que importa es `fecha_vencimiento`: la app avisa a 60,
30 y 7 días. Es lo que evita descubrir un certificado vencido durante una auditoría.

---

## Reglas de llenado

1. **No inventes datos.** Si no lo sabes, déjalo vacío y anótalo en `observaciones`. Un campo
   vacío es honesto; un dato inventado contamina la app desde el día uno.
2. **No cambies los nombres de las columnas** ni el orden. La carga a Dataverse los usa.
3. **No uses comas dentro de los campos** — son archivos CSV separados por coma. Si necesitas
   separar ideas, usa un guion.
4. **Sin tildes ni ñ en códigos y TAG.** En el texto descriptivo sí, sin problema.
5. **Fechas en formato `AAAA-MM-DD`** (ejemplo: `2026-03-15`).
6. **Sí/No siempre como `SI` / `NO`** en mayúsculas.
7. Si abres los archivos en Excel, **guárdalos como CSV UTF-8**, no como `.xlsx`.

---

## Cómo sabemos que está listo

Un archivo está cerrado cuando:

- [ ] No queda ninguna celda con `PROPUESTA - VALIDAR`
- [ ] Tiene un responsable nombrado que lo firma
- [ ] Los códigos cruzados existen (los TAG de los planes están en la jerarquía, los materiales del
      BOM están en el catálogo)

El último punto lo verificamos nosotros automáticamente al recibir los archivos. Si algo no cruza,
te lo devolvemos indicando exactamente qué fila y qué código falta.

---

## Dudas

Todo lo que no esté claro, anótalo en la columna `observaciones` de la fila correspondiente en vez
de resolverlo por tu cuenta. Lo revisamos juntos en el taller de cierre de Fase 0.
