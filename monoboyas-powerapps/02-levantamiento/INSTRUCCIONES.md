# Plantillas de levantamiento — Instrucciones

Seis plantillas que recogen la información que la aplicación va a centralizar. Son el entregable
de la **Fase 0** y son bloqueantes: sin ellas no hay nada que mostrar.

La aplicación es de **consulta e información**, no de ejecución. Estas plantillas describen
*qué es* el sistema de monoboya, no *cómo se trabaja* en él.

---

## 🔴 Lo primero: la codificación oficial

Toda la estructura gira alrededor del **código de subsistema**. Ese código ya existe del lado de
ustedes y todavía no lo tenemos.

Por eso cada nodo del archivo `01` tiene **dos columnas de código**:

| Columna | Quién la llena | Para qué |
|---|---|---|
| `codigo_provisional` | Ya viene llena | Un código temporal (`MB-01.S02.ROD-001`) que sostiene el árbol mientras tanto. **No lo modifiques**: los otros cinco archivos apuntan a él |
| `codigo_oficial` | **Ustedes** | El código real de la codificación de subsistemas. Es el que la app va a mostrar |

Cuando la columna `codigo_oficial` esté completa, nosotros reemplazamos las referencias en todos
los archivos de una sola pasada. **Hasta entonces no se carga nada a la aplicación.**

Si la codificación real tiene más niveles de los que propusimos (por ejemplo, un subsistema que se
divide en sub-subsistemas), **agrega las filas que hagan falta**: el modelo es un árbol y acepta
cualquier profundidad.

---

## ⚠️ Lo precargado es una propuesta, no un dato

Todo lo que viene lleno está marcado con **`PROPUESTA - VALIDAR`** en la columna `observaciones`.
Es una monoboya tipo CALM genérica, armada con la configuración estándar del sector.

Tu trabajo es **corregir**, **borrar lo que no aplica**, **agregar lo que falta** y **vaciar la
columna `observaciones`** de cada fila validada. Cuando no quede ningún `PROPUESTA - VALIDAR`, el
archivo está cerrado.

---

## Los seis archivos

### `01_jerarquia_subsistemas.csv` — El árbol del sistema ⭐

**81 nodos: 1 monoboya + 12 subsistemas + 68 equipos.** Es la base de todo; los otros cinco
archivos cuelgan de aquí.

Cada fila es un nodo del árbol y apunta a su padre:

```
MB-01                          nivel 1   Monoboya
 └─ MB-01.S02                  nivel 2   Rodamiento principal y girador
     └─ MB-01.S02.ROD-001      nivel 3   Rodamiento principal (main bearing)
```

| Columna | Qué poner |
|---|---|
| `codigo_oficial` | **El código real de su codificación.** Obligatorio antes de cargar |
| `codigo_provisional` | Ya viene. No tocar |
| `codigo_padre` | El `codigo_provisional` del nodo que lo contiene. La raíz lo lleva vacío |
| `nivel` | 1 monoboya · 2 subsistema · 3 equipo · 4 componente, si hiciera falta |
| `tipo_nodo` | `Monoboya` / `Subsistema` / `Equipo` / `Componente` |
| `criticidad` | `A` = su falla para la operación · `B` = la degrada · `C` = no la afecta |
| `fabricante`, `modelo`, `n_serie`, `fecha_instalacion` | De la placa del equipo o del manual. Si no hay, déjalo vacío — **no lo inventes** |
| `ubicacion_fisica` | `Cubierta` / `Casco` / `Interior` / `Superficie` / `Submarino` / `Fondo marino` |
| `requiere_buzo_rov` | `SI` / `NO` |
| `coordenada_x`, `coordenada_y` | **Solo en los subsistemas.** Dónde cae su punto sobre el esquema de la monoboya, en porcentaje de 0 a 100. Vienen precargadas: revísalas contra el dibujo del prototipo y corrígelas si el punto no está donde debería |
| `imagen_referencia` | Opcional. Enlace a una foto o recorte de plano de esa parte, que se muestra en el panel visual |

> **Puntos a confirmar:** precargamos 6 líneas de fondeo y 4 tramos de manguera flotante más el
> tramo de acople. Corrígelo según la configuración real.

> **Sobre las coordenadas:** no hace falta que sean exactas al milímetro. Son el sitio donde se
> pone el punto que representa al subsistema sobre el dibujo, y **se pueden ajustar después desde
> la propia aplicación** sin tocar nada más. Están aquí para que el panel visual arranque con algo
> razonable el primer día.

### `02_frecuencias_referencia.csv` — Cada cuánto corresponde mantener

**40 frecuencias precargadas.** Es **información de referencia**: la app la muestra en la ficha del
nodo, no genera órdenes ni programa nada.

| Columna | Qué poner |
|---|---|
| `codigo_nodo` | A qué parte del árbol corresponde |
| `frecuencia_valor` + `frecuencia_unidad` | Separados a propósito: «cada 3 `Meses`», no «cada 90 días» |
| `tipo` | `Preventivo` / `Predictivo` / `Inspeccion legal` / `Lubricacion` / `Limpieza` |
| `fecha_ultima_ejecucion` | Cuándo se hizo por última vez, si se sabe |
| `norma_referencia` | OCIMF SMOG, GMPHOM 2009, MEG4, API RP 2SK, DICAPI, manual del fabricante |

> **Las frecuencias precargadas son las típicas del sector, no las de ustedes.** Es lo que más hay
> que revisar de todo el paquete.

### `03_catalogo_materiales.csv` — Repuestos y consumibles

**27 materiales.** Solo repuestos y consumibles: lo que forma parte del sistema o se consume en él.
Herramientas, EPP y servicios quedaron fuera, porque pertenecen a la ejecución del trabajo.

| Columna | Qué poner |
|---|---|
| `codigo_sap` | **Crítico.** Es el único puente con SAP, ya que no hay integración automática |
| `lead_time_dias` | Días desde que se pide hasta que llega. Manguera importada ≠ trapo industrial |
| `stock_minimo` | Por debajo de este número la app avisa |

### `04_materiales_por_nodo.csv` — Qué repuesto corresponde a qué parte

**26 asociaciones precargadas.** Es lo que permite que al abrir un subsistema se vea de inmediato
qué repuestos le corresponden y si hay existencias.

- `cantidad_referencial`: cuánto se suele necesitar. Es una referencia, no un compromiso.
- Un mismo material puede colgar de varios nodos.

### `05_documentos_planos.csv` — Planos, manuales y certificados

**26 documentos, de los cuales 13 son planos.** La columna clave es `fecha_vencimiento`: la app
avisa a 60, 30 y 7 días. Es lo que evita descubrir un certificado vencido en plena auditoría.

Tipos: `Plano` · `Manual` · `Memoria tecnica` · `Certificado de manguera` · `Certificado DICAPI` ·
`Certificado de fabricacion` · `Informe de inspeccion` · `Procedimiento`.

El archivo en sí (PDF, DWG) se sube después desde la aplicación; aquí solo se declara qué
documentos deben existir y de qué nodo cuelgan.

### `06_personal_accesos.csv` — Quién consulta y quién actualiza

Viene **vacío**, solo con la estructura de perfiles. Se necesita el correo corporativo de Microsoft
365 de cada persona.

| Perfil | Puede actualizar |
|---|---|
| `Consulta` | Nada. Solo lee |
| `Materiales` | Materiales asociados y stock |
| `Documentacion` | Documentos, planos y certificados |
| `Tecnico` | Atributos técnicos y frecuencias de referencia |
| `Administrador` | Todo, incluida la jerarquía |

---

## Reglas de llenado

1. **No inventes datos.** Si no lo sabes, déjalo vacío y anótalo en `observaciones`.
2. **No cambies los nombres de las columnas** ni el orden. La carga a Dataverse los usa.
3. **No modifiques `codigo_provisional` ni `codigo_padre`** — sostienen el árbol. Si agregas un
   nodo nuevo, invéntale un provisional que siga el mismo patrón y apúntalo a su padre.
4. **No uses comas dentro de los campos** — son CSV separados por coma. Usa un guion.
5. **Sin tildes ni ñ en los códigos.** En el texto descriptivo sí, sin problema.
6. **Fechas en formato `AAAA-MM-DD`.** Sí/No siempre como `SI` / `NO` en mayúsculas.
7. Si los abres en Excel, **guárdalos como CSV UTF-8**, no como `.xlsx`.

---

## Cómo sabemos que está listo

- [ ] La columna `codigo_oficial` está completa en `01`
- [ ] No queda ninguna celda con `PROPUESTA - VALIDAR`
- [ ] Cada archivo tiene un responsable nombrado que lo firma
- [ ] El árbol cierra: todo `codigo_padre` existe, sin ciclos, con una sola raíz

Los dos últimos puntos los verificamos nosotros automáticamente al recibir los archivos (el
comando está en el `README.md` del paquete). Si algo no cruza, te devolvemos exactamente qué fila
y qué código falta.

---

## Dudas

Anótalas en la columna `observaciones` de la fila correspondiente en vez de resolverlas por tu
cuenta. Las revisamos juntos en el taller de cierre de Fase 0.
