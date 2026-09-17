# Plan maestro — Aplicación Power Apps de consulta centralizada de Monoboyas

**Cliente final:** Repsol — Refinería La Pampilla
**Ejecutor:** TAMOIN
**Activo:** Monoboya (SPM — *Single Point Mooring*, configuración tipo CALM)
**Versión:** 2.0 — reorientada a consulta. Sujeta a validación en Fase 0

---

## 1. Qué es esta aplicación, y qué no es

> **Es un repositorio navegable del sistema de monoboya.** Centraliza y muestra con claridad la
> información del activo, organizada por la codificación de subsistemas que ya existe: una vista
> global primero, y desde ahí se desglosa hasta el detalle de cada parte.

**No es una aplicación de ejecución.** No genera órdenes de trabajo, no lleva checklists, no
registra firmas ni avances. La supervisión del trabajo la lleva Repsol; lo que TAMOIN necesita es
tener la información del sistema centralizada, clara y actualizada.

| La app **sí** | La app **no** |
|---|---|
| Muestra el árbol completo del sistema por código de subsistema | Genera órdenes de trabajo |
| Da la ficha técnica de cada parte | Lleva checklists de ejecución |
| Dice qué repuestos corresponden a cada subsistema y si hay stock | Registra firmas, horas ni avance físico |
| Informa cada cuánto corresponde mantener, como dato de referencia | Programa ni dispara mantenimientos |
| Guarda planos, manuales y certificados, y avisa de vencimientos | Gestiona permisos de trabajo ni HSE |
| Permite **actualizar** materiales, stock y documentos | Valoriza ni factura |

### El problema que resuelve

La información del sistema de monoboya está dispersa: los planos en una carpeta, los certificados
en otra, el catálogo de repuestos en un Excel, las características de cada equipo en la memoria de
quien lleva años en el activo. Cuando alguien necesita saber algo concreto de un subsistema —qué
modelo es, qué repuesto le corresponde, dónde está el plano, si el certificado sigue vigente—
tiene que buscarlo en cuatro sitios y preguntar a dos personas.

La aplicación pone todo eso detrás de un único código de subsistema.

---

## 2. Decisiones de arquitectura

| Decisión | Elección | Justificación |
|---|---|---|
| **Eje de identificación** | El **código de subsistema** de la codificación existente | Es como el equipo ya piensa el activo. Nada de identificadores nuevos |
| **Backend** | Dataverse | Jerarquía real, seguridad por rol, auditoría nativa de cada cambio. Requiere licencia Power Apps Premium |
| **Tipo de aplicación** | **Una sola app model-driven** | Ver §3 |
| **Inventario / ERP** | Autónomo, sin integración SAP | El código de reserva se registra a mano como campo de trazabilidad |
| **Offline** | No requerido | Simplifica sustancialmente la aplicación |
| **Vista sinóptica gráfica** | No se construye | Descartada explícitamente |

---

## 3. Por qué una sola aplicación, y por qué model-driven

La versión anterior de este plan proponía dos apps: una *canvas* para el técnico en campo y una
*model-driven* para el back-office. **Al desaparecer la ejecución, desaparece la razón de ser de
la canvas**: ya no hay nadie llenando un checklist con guantes puestos.

Lo que queda —navegar una jerarquía, leer fichas, abrir planos, adjuntar documentos, corregir un
stock— es exactamente lo que una app *model-driven* de Dataverse hace de fábrica:

- **Navegación jerárquica y búsqueda global** sin construir una sola pantalla.
- **Formularios con pestañas** generados desde las tablas.
- **Edición con permisos por rol** y auditoría automática de quién cambió qué y cuándo.
- **La misma app funciona en escritorio y en móvil**, sin desarrollo aparte.
- **Vistas filtrables y exportables a Excel** sin desarrollo.

Construir esto en canvas significaría replicar a mano, durante semanas, lo que Dataverse regala.

```
┌──── APP MODEL-DRIVEN (escritorio y móvil) ────────────────┐
│                                                            │
│  Vista global      →   Subsistema    →   Equipo/Componente │
│  (subsistemas           (sus partes       (ficha completa  │
│   con su código)         y resumen)        en pestañas)    │
│                                                            │
│  Ficha = Técnico · Materiales · Frecuencias · Documentos   │
└─────────────────────────┬──────────────────────────────────┘
                ┌─────────▼──────────┐
                │     DATAVERSE      │   9 tablas
                └─────────┬──────────┘
        ┌─────────────────┼─────────────────┐
┌───────▼────────┐ ┌──────▼───────┐ ┌───────▼────────┐
│ POWER AUTOMATE │ │  SHAREPOINT  │ │   POWER BI     │
│ · Stock        │ │ · Planos     │ │ · Inventario   │
│ · Alertas de   │ │ · Manuales   │ │ · Vencimientos │
│   vencimiento  │ │ · Certific.  │ │   (opcional)   │
└────────────────┘ └──────────────┘ └────────────────┘
```

> Si más adelante se quiere una portada más visual que una lista, se agrega **una** pantalla canvas
> embebida con tarjetas por subsistema. No hace falta para arrancar.

### Almacenamiento de archivos

Los planos, manuales y certificados van a **SharePoint**, no a Dataverse. La capacidad de archivos
en Dataverse es cara, y un plano en DWG o un informe de inspección subacuática con fotos pesan.
Dataverse guarda el enlace y los metadatos: tipo, emisor, fechas y de qué nodo cuelga.

---

## 4. El árbol del sistema

Detalle completo del modelo en [`modelo-datos.md`](modelo-datos.md).

La jerarquía **no** se modela con una tabla por nivel, sino con **una sola tabla auto-referenciada**
donde cada nodo apunta a su padre:

```
Monoboya MB-01                         nivel 1
 ├─ Casco y estructura flotante        nivel 2   ← subsistema
 │   ├─ Casco flotante principal       nivel 3   ← equipo
 │   └─ Compartimentos estancos        nivel 3
 └─ Rodamiento principal y girador     nivel 2
     ├─ Rodamiento principal           nivel 3
     └─ Sistema de lubricación         nivel 3
```

**Por qué importa:** la codificación real de subsistemas todavía no la tenemos, y puede tener más
niveles de los que supusimos. Un árbol acepta cualquier profundidad, permite que un subsistema
contenga sub-subsistemas, y hace que la vista global y el desglose sean **la misma consulta a
distinta altura**. Es también lo que permite arrancar el modelo hoy sin esperar a ver la
codificación.

---

## 5. Qué se puede actualizar desde la aplicación

La app no es solo de lectura: mantener la información al día es parte de su propósito.

| Información | ¿Editable? | Perfil |
|---|---|---|
| Materiales asociados a un nodo y cantidades | **Sí** | Materiales, Administrador |
| Stock disponible y reservado | **Sí** | Materiales, Administrador |
| Solicitudes de material y **código de reserva** | **Sí** | Materiales, Administrador |
| Documentos, planos y certificados: alta, reemplazo, fechas | **Sí** | Documentación, Administrador |
| Atributos técnicos del nodo | **Sí** | Técnico, Administrador |
| Frecuencias de referencia | **Sí** | Técnico, Administrador |
| Jerarquía y códigos de subsistema | **No** desde la app | Carga controlada |

Dataverse audita cada cambio con usuario y fecha sin desarrollo adicional. La jerarquía queda
fuera de la edición a propósito: es la columna vertebral del sistema y un cambio accidental
rompería todas las referencias.

---

## 6. Las pantallas

Prototipo navegable en [`../03-mockups/mockup-pantallas.html`](../03-mockups/mockup-pantallas.html).

| # | Pantalla | Qué muestra |
|---|---|---|
| 1 | **Vista global — lista** | Los subsistemas con su código oficial, nombre, criticidad y número de partes. Búsqueda por código. Es la puerta de entrada |
| 2 | **Vista global — esquema** | La **misma pantalla** con el selector *Ver como* en Esquema: el dibujo de la monoboya con un punto por subsistema |
| 3 | **Esquema con un subsistema elegido** | El punto resaltado y el resto atenuado, con el resumen de esa parte al lado |
| 4 | **Subsistema** | Su código y descripción, las partes que lo componen, y accesos directos a sus materiales y documentos |
| 5 | **Ficha — Técnico** | Fabricante, modelo, n° de serie, fecha de instalación, criticidad, ubicación física |
| 6 | **Ficha — Materiales** | Repuestos del nodo con stock disponible, mínimo, plazo de reposición y código de reserva. Editable |
| 7 | **Ficha — Frecuencias** | Cada cuánto corresponde mantener, última vez registrada y norma aplicable. Informativo |
| 8 | **Ficha — Documentos y planos** | Planos, manuales, certificados e informes con su vigencia. Se abren y se suben desde aquí |
| 9 | **Actualizar información** | Formulario de edición con el rastro de auditoría visible |

Sin botones de *iniciar*, sin firmas, sin checklists, sin estados de trabajo.

### Reglas de presentación

- El **código del nodo** es lo primero que se lee en cualquier pantalla.
- Los estados se comunican con **color y texto**, nunca solo color.
- Las cifras que se comparan entre sí van alineadas por dígito.
- Un documento vencido se ve como vencido antes de tener que leerlo.

---

## 6 bis. El panel visual: visualización dinámica dentro de la app

No hace falta un Power BI aparte. La visualización dinámica se construye como **una página más de
la misma aplicación**: la lista a la izquierda, el esquema de la monoboya a la derecha,
sincronizados en las dos direcciones.

```
  clic en la lista   ─────────►  se resalta en el esquema
  clic en el esquema ─────────►  se selecciona en la lista y se abre su ficha
```

Técnicamente es una **página personalizada (canvas) embebida en la app model-driven**: misma barra
lateral, mismos permisos, misma sesión. El usuario no percibe que cambió de herramienta.

### Cómo se accede: un selector, no una pantalla aparte

El esquema **no es una entrada nueva en el menú**. La vista global lleva en su cabecera un
selector **«Ver como»** con dos opciones, *Lista* y *Esquema*:

- Son **la misma pantalla**: mismos datos, misma selección, misma entrada en el menú lateral.
  Cambia solo cómo se presentan.
- Lo que esté seleccionado se mantiene al cambiar de una a otra.
- La aplicación **recuerda la última elección de cada persona**, de modo que quien prefiere la
  lista no vuelve a ver el dibujo y quien prefiere el dibujo lo encuentra ya puesto.

Es deliberado que no sea una opción de menú aparte: dos entradas distintas para los mismos datos
obligan al usuario a recordar en cuál estaba y parten la navegación en dos caminos. Un selector
dentro de la pantalla mantiene un solo camino.

### La decisión que evita la sobreparametrización

El riesgo real de un esquema con zonas clicables es que las posiciones queden incrustadas en la
pantalla: doce botones colocados a mano, y cada vez que cambia el dibujo o se agrega un subsistema
hay que reabrir el editor y recolocarlos.

**Se evita guardando las posiciones como dato**, en tres campos de `Nodo del sistema`:
`Coordenada X (%)`, `Coordenada Y (%)` e `Imagen de referencia`.

La página dibuja una **galería de puntos posicionada por fórmula**, no doce controles colocados a
mano. Consecuencias:

| | |
|---|---|
| Agregar un subsistema | Es agregar una fila y duplicar su botón transparente — ver el matiz de abajo |
| Mover un punto | Es cambiar un número desde la propia ficha |
| Color de cada punto | Sale del dato (documento vencido, stock bajo mínimo), no de la maqueta |
| Pantallas distintas | Al ser porcentajes y no píxeles, el esquema escala solo |

Esa es la diferencia entre una pantalla que se mantiene sola y una que hay que tocar cada vez.

> **Matiz, para no prometer de más:** el **dibujo** de los puntos —dónde va cada uno y de qué
> color— sale del dato por completo. El **clic** no: una galería de Power Apps coloca sus elementos
> en fila o columna, no en posiciones libres, así que cada punto necesita un botón transparente
> enlazado al dato. Con 12 subsistemas es un trabajo menor, y duplicar un botón al añadir uno nuevo
> lleva un par de minutos. La versión completamente sin tocar la pantalla exige un componente de
> código (PCF), que ya es trabajo de desarrollador.

### Tres niveles, en orden de costo

| Nivel | Qué es | Costo | Cuándo |
|---|---|---|---|
| **1. Panel visual sincronizado** | Página canvas embebida: esquema con puntos clicables y lista, bidireccional | Una página + 3 campos. Sin licencia adicional | Fase 4 |
| **2. Gráficos nativos de Dataverse** | Documentos por vencer, materiales bajo mínimo, completitud de la información. Al hacer clic filtran la lista de abajo | Configuración, cero código. Sin licencia adicional | Fase 4 |
| **3. Power BI embebido *dentro* de la app** | Solo para **tendencia en el tiempo** | Licencias + un informe que mantener | Solo si se pide |

**Cuándo sí hace falta Power BI:** Dataverse guarda el estado de hoy, no fotos del pasado. Ver
*cómo evolucionó* la completitud de la información mes a mes, o el consumo histórico de repuestos,
exige acumular historia — y eso es territorio de Power BI. Todo lo que sea "cómo está hoy" se
resuelve nativo.

Y cuando llegue ese momento, **tampoco será un Power BI aparte**: se embebe como un panel más de
la propia aplicación.

### Limitaciones, por delante

- **El esquema es una imagen de fondo.** Si la configuración de la monoboya cambia de forma
  sustancial hay que rehacer el dibujo. Los puntos no: esos son datos.
- **Un dibujo por tipo de monoboya.** Si todas son CALM, uno solo sirve para todas.
- **En móvil el panel se apila** debajo de la lista en vez de ir al lado. Hay que diseñarlo así
  desde el principio.
- **Los gráficos nativos agregan sobre una tabla a la vez** (conteo, suma, promedio, mín, máx), sin
  medidas calculadas ni cruces complejos. Para eso está el nivel 3.
- **La llamada exacta para navegar** desde la página canvas al registro de la app model-driven se
  valida con una prueba corta en Fase 1, antes de comprometer el diseño de la página.

---

## 7. Fases de ejecución

| Fase | Duración est. | Entregable | Bloqueante |
|---|---|---|---|
| **0. Levantamiento** | 2–3 sem | **La codificación oficial de subsistemas** + las seis plantillas llenas. Taller de validación | **Sí** |
| **1. Fundación** | 1 sem | Entornos DEV/UAT/PROD, solución gestionada, tablas Dataverse, perfiles de acceso, carga del árbol | — |
| **2. Consulta** | 2–3 sem | App model-driven: vista global, desglose y fichas completas | — |
| **3. Materiales y documentos** | 2 sem | Stock, solicitudes, código de reserva, carga de planos y certificados a SharePoint | — |
| **4. Panel visual y alertas** | 2 sem | Página del esquema interactivo, gráficos nativos de Dataverse, avisos de vencimiento y de stock bajo mínimo | — |
| **5. Piloto y puesta en marcha** | 2 sem | Piloto con una monoboya, capacitación, manual, paso a producción | — |

**La Fase 0 es bloqueante**, y dentro de ella lo primero es la codificación: sin ella no hay
identificadores sobre los que construir.

### Gobierno y ALM

- Tres entornos: **DEV → UAT → PROD**, con despliegue por **solución gestionada**.
- La app y los flujos son propiedad de una **cuenta de servicio**, nunca de una persona.
- Política DLP aplicada al entorno y control de versiones de la solución exportada.

---

## 8. Riesgos y puntos abiertos

Detalle y seguimiento en [`decisiones-abiertas.md`](decisiones-abiertas.md).

| # | Riesgo / Pregunta | Impacto | Acción |
|---|---|---|---|
| 1 | **La codificación oficial de subsistemas aún no está en nuestras manos** | **Alto** | Solicitarla ya. Bloquea la carga |
| 2 | **¿En qué tenant vive la app: TAMOIN o Repsol?** | **Alto** | Resolver antes de Fase 1 |
| 3 | Licenciamiento Premium de Power Apps | Alto (costo) | Evaluar plan *por aplicación* vs *por usuario* |
| 4 | La información se carga y luego se desactualiza | **Alto** | Es el riesgo principal de una app de consulta. Responsable nombrado por tipo de información e inventario cíclico |
| 5 | Los planos y manuales no existen en digital | Medio | Inventariar en Fase 0 qué hay y qué falta digitalizar |
| 6 | Códigos de reserva ingresados a mano → desfase con SAP | Medio | Validación de formato y campo auditado |
| 7 | La codificación real tiene más niveles de los previstos | Bajo | Ya mitigado: el árbol acepta cualquier profundidad |
| 8 | No existe un plano o esquema digital que sirva de base al panel visual | Bajo | Se dibuja uno esquemático: el valor está en los puntos y en el dato, no en el detalle del dibujo |

---

## 9. Principio de trabajo

**No se inventan datos.** Todo lo que este paquete propone sobre la monoboya —subsistemas, equipos,
frecuencias, materiales, documentos— está marcado como **propuesta a validar**, nunca como dato
confirmado. El equipo de TAMOIN corrige, elimina lo que no aplica y agrega lo que falta.

Se entrega precargado porque es mucho más rápido corregir una lista que partir de una hoja en
blanco. Pero nada de lo precargado entra a la aplicación sin la firma de quien conoce el activo.
