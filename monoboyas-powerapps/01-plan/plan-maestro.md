# Plan maestro — Aplicación Power Apps para gestión de mantenimiento de Monoboyas

**Cliente final:** Repsol — Refinería La Pampilla
**Ejecutor:** TAMOIN
**Activo:** Monoboya (SPM — *Single Point Mooring*, configuración tipo CALM)
**Versión:** 1.0 — propuesta inicial, sujeta a validación en Fase 0

---

## 1. Problema y objetivo

TAMOIN presta mantenimiento integral de equipos oil & gas a Repsol y debe gestionar el
mantenimiento de las monoboyas. Hoy esa gestión no tiene soporte digital: no existe una fuente
única que diga **qué se mantiene, cada cuánto, con qué materiales y con qué evidencia**. Eso se
traduce en tres problemas concretos:

1. **Trazabilidad**: no hay historial consultable por equipo. Ante una auditoría de Repsol, DICAPI
   o una certificadora, la evidencia hay que reconstruirla a mano.
2. **Planificación**: las frecuencias viven en Excel y en la cabeza de las personas. Se detectan
   los vencimientos tarde.
3. **Materiales**: se descubre que falta el repuesto el día de la intervención, no semanas antes.
   En una monoboya, donde la ventana operativa depende del mar y de la programación de buques,
   perder una ventana cuesta mucho.

**Objetivo:** una aplicación Power Apps *user friendly* para el equipo de mantenimiento que haga la
gestión **eficiente y trazable**, cubriendo el circuito completo:

```
frecuencia de mantenimiento
   → sistemas planificados a mantener
      → materiales que requiere cada intervención
         → ¿hay stock?
            → solicitud y código de reserva
               → ejecución en campo con evidencia
                  → cierre, historial y reporte
```

### Qué significa "user friendly" aquí

No es un adjetivo decorativo. Para este equipo significa:

- El técnico abre la app y en **un toque** ve lo que le toca hoy.
- **No escribe lo que puede seleccionar.** Nada de teclear TAGs ni códigos de material.
- La foto es el registro principal. Es más rápido fotografiar una brida corroída que describirla.
- La app **nunca pierde trabajo**: cada paso del checklist se guarda al completarse, no al final.
- Si algo falta (un material, una firma), la app lo dice **antes**, no al intentar cerrar.

---

## 2. Decisiones de arquitectura ya tomadas

| Decisión | Elección | Justificación y consecuencia |
|---|---|---|
| **Backend de datos** | Dataverse | Relaciones reales entre 16 tablas, seguridad por rol y por registro, auditoría nativa (quién cambió qué y cuándo — indispensable para trazabilidad). Habilita la app *model-driven*, que se genera casi sola. **Costo:** requiere licencia Power Apps Premium. |
| **Inventario / ERP** | App autónoma, sin integración SAP | La app gestiona su propio catálogo, stock y solicitudes. El **código de reserva** de SAP se registra manualmente como campo de trazabilidad. Evita depender de TI de Repsol para arrancar. El modelo queda preparado para integrar después sin rehacer tablas. |
| **Offline** | No requerido | Sin caché local ni cola de sincronización. Simplifica sustancialmente la app de campo. Si el piloto revela zonas sin señal, se agrega como cambio de alcance (ver Riesgo 7). |
| **Número de apps** | Dos | Canvas para campo, model-driven para back-office. Ver §4. |

---

## 3. Alcance funcional

### Dentro de alcance

- Jerarquía de activos de la monoboya en 4 niveles, con TAG por equipo.
- Planes de mantenimiento con frecuencia (preventivo, predictivo, inspección legal).
- Gamas de tareas (checklists) por plan, con tipos de registro tipados.
- Generación automática de órdenes de trabajo según frecuencia.
- Lista de materiales por plan (BOM) y verificación anticipada de stock.
- Catálogo de materiales, stock por almacén y movimientos de inventario.
- Solicitudes de material con flujo de aprobación y registro del código de reserva.
- Ejecución en campo: checklist, mediciones, fotos, firmas.
- Hallazgos y generación de órdenes correctivas.
- Certificados y documentos con control de vencimiento.
- Tableros de control en Power BI y reporte PDF por orden cerrada.

### Fuera de alcance (explícito)

- Integración con SAP (decidida como no incluida — ver §8, Fase 6 opcional).
- Modo offline.
- Gestión de permisos de trabajo (PTW), HSE y planificación de embarcaciones.
- Gestión de costos, horas-hombre valorizadas y facturación.
- Mantenimiento de otros activos del terminal (se diseña para escalar, no se implementa).

---

## 4. Arquitectura

```
┌─ App CANVAS (móvil/tablet) ──────┐   ┌─ App MODEL-DRIVEN (escritorio) ─┐
│  Técnico de campo                │   │  Planificador / Supervisor      │
│  · Mis órdenes de trabajo        │   │  · Maestros: activos, sistemas  │
│  · Ejecutar checklist + fotos    │   │  · Planes y gamas               │
│  · Reportar hallazgo             │   │  · Inventario y solicitudes     │
│  · Consultar stock               │   │  · Aprobaciones                 │
└──────────────┬───────────────────┘   └───────────────┬─────────────────┘
               └───────────────┬───────────────────────┘
                     ┌─────────▼──────────┐
                     │     DATAVERSE      │   16 tablas
                     └─────────┬──────────┘
          ┌────────────────────┼────────────────────┐
┌─────────▼────────┐  ┌────────▼─────────┐  ┌───────▼────────┐
│ POWER AUTOMATE   │  │  POWER BI        │  │ SHAREPOINT     │
│ · Generar OT     │  │ · Cumplimiento   │  │ · Fotos, PDF   │
│ · Chequear stock │  │ · Backlog        │  │ · Certificados │
│ · Aprobaciones   │  │ · Consumo rep.   │  │                │
│ · Alertas Teams  │  │ · Vencimientos   │  │                │
└──────────────────┘  └──────────────────┘  └────────────────┘
```

### Por qué dos aplicaciones

La app *model-driven* se genera automáticamente a partir de las tablas de Dataverse: formularios,
vistas, búsquedas y filtros salen sin escribir una pantalla. Resuelve todo el back-office
(maestros, planes, inventario, aprobaciones) con un esfuerzo marginal.

La app *canvas* se reserva para donde el diseño realmente importa: el técnico en campo, con
guantes, en movimiento, posiblemente bajo sol directo. Ahí cada toque cuenta.

Construir el back-office en canvas sería semanas de trabajo desperdiciadas replicando a mano lo
que Dataverse regala.

### Almacenamiento de archivos

Las fotos y los PDF van a **SharePoint**, no a Dataverse. La capacidad de archivos en Dataverse es
cara, y las fotos de inspección de mangueras, cadenas y protección catódica se acumulan rápido.
Dataverse guarda solo el enlace.

---

## 5. Modelo de datos

Detalle completo de tablas, campos y relaciones en [`modelo-datos.md`](modelo-datos.md).

Resumen de la jerarquía de activos, al estilo de *ubicación técnica* de SAP para que resulte
familiar al equipo y compatible con una futura integración:

```
Terminal ▸ Monoboya ▸ Sistema ▸ Equipo/Componente (TAG)
```

Las 16 tablas se agrupan en tres bloques:

- **Maestras** (7): Terminal, Monoboya, Sistema, Equipo, Material, Almacén, Personal.
- **Planificación** (3): Plan de mantenimiento, Tarea de plan (gama), Material por plan (BOM).
- **Transaccionales** (6): Orden de Trabajo, Tarea de OT, Hallazgo, Movimiento de inventario,
  Stock, Solicitud de material. Más dos auxiliares: Medición y Documento/Certificado.

La tabla **Material por plan (BOM)** es la pieza que hace posible la pregunta central del
proyecto: *"¿tengo los repuestos para los mantenimientos del próximo mes?"*. Sin ella, la app
sabe qué mantener y sabe qué hay en almacén, pero no puede cruzar ambas cosas.

---

## 6. Automatizaciones (Power Automate)

| Flujo | Disparador | Qué hace |
|---|---|---|
| **Generador de OT** | Diario, programado | Recorre planes activos; donde `fecha próxima ≤ hoy + horizonte`, crea la OT y copia la gama a `Tarea de OT`. Control de duplicados por plan + fecha programada. |
| **Verificación de materiales** | Al crear una OT | Lee el BOM del plan, contrasta contra `Stock`, marca el semáforo de la OT (Completo / Parcial / Sin stock) y crea `Solicitud de material` en borrador por lo faltante. |
| **Aprobación de solicitudes** | Al pasar a *Solicitada* | Aprobación al supervisor vía Teams/correo. Al aprobar, queda a la espera del código de reserva. |
| **Recálculo de stock** | Al crear un movimiento | Recalcula disponible / reservado del material en ese almacén. |
| **Alertas** | Diario | OT vencidas, stock bajo mínimo, certificados por vencer (60/30/7 días). A Teams y correo. |
| **Reporte de OT cerrada** | Al cerrar una OT | Genera PDF con checklist, mediciones, fotos y firmas; lo archiva en SharePoint. |

**Regla de integridad:** la tabla `Stock` **nunca se edita a mano**. Se deriva de los
`Movimiento de inventario` por flujo. Así el saldo siempre es auditable contra sus movimientos —
si alguien cuestiona una cifra, se puede reconstruir.

---

## 7. Pantallas de la app canvas

Prototipo navegable en [`../03-mockups/mockup-pantallas.html`](../03-mockups/mockup-pantallas.html).

| # | Pantalla | Propósito |
|---|---|---|
| 1 | **Inicio** | Cuatro tarjetas grandes con contadores: *OT de hoy*, *Vencidas*, *Reportar hallazgo*, *Consultar stock*. |
| 2 | **Lista de OT** | Filtro por estado / monoboya / fecha. Cada tarjeta: TAG, sistema, fecha, semáforo de materiales. |
| 3 | **Detalle de OT** | Datos del equipo, materiales requeridos con disponibilidad, botón *Iniciar*. |
| 4 | **Ejecución de checklist** | Un control por tipo de registro (toggle, numérico con validación de rango, cámara, texto). Barra de progreso. Bloquea el cierre con pasos obligatorios pendientes. |
| 5 | **Cierre de OT** | Resumen, horas reales, consumo de materiales, firma de técnico y supervisor. |
| 6 | **Hallazgo** | Foto + severidad + descripción en menos de 30 segundos. |
| 7 | **Consulta de stock** | Búsqueda por código o descripción, disponibilidad por almacén, botón *Solicitar*. |

### Reglas de UX de obligado cumplimiento

- Objetivos táctiles ≥ 44 px — el técnico usa guantes.
- Máximo dos niveles de navegación desde el inicio.
- Estados comunicados con **color y texto**, nunca solo color (hay daltonismo, y hay sol directo).
- Contraste alto: la pantalla se lee a la intemperie.
- Guardado incremental por paso.
- Mensajes de error que dicen **qué hacer**, no qué falló.

---

## 8. Fases de ejecución

| Fase | Duración est. | Entregable | Bloqueante |
|---|---|---|---|
| **0. Levantamiento** | 2–3 sem | Plantillas llenas: jerarquía de sistemas, frecuencias, gamas, catálogo de materiales. Taller de validación. | **Sí** |
| **1. Fundación** | 1 sem | Entornos DEV/UAT/PROD, solución gestionada, tablas Dataverse, roles de seguridad, carga de maestros. | — |
| **2. MVP de mantenimiento** | 3–4 sem | Planes + generador de OT + app canvas de ejecución + app model-driven. | — |
| **3. Inventario y materiales** | 2–3 sem | Stock, movimientos, BOM, solicitudes, código de reserva, aprobaciones. | — |
| **4. Visibilidad y control** | 2 sem | Power BI, certificados y vencimientos, hallazgos, reporte PDF. | — |
| **5. Piloto y go-live** | 2 sem | Piloto con una monoboya, capacitación, manual, paso a producción. | — |
| **6. Integración SAP** *(opcional)* | por definir | Sincronización de stock y creación automática de reservas. | — |

Las fases 2 y 3 se pueden solapar parcialmente. **La Fase 0 es bloqueante**: sin la jerarquía de
sistemas y sin las gamas de tareas no hay nada que planificar, y construir la app antes de
tenerlas garantiza retrabajo.

### Gobierno y ALM

- Tres entornos: **DEV → UAT → PROD**, con despliegue por **solución gestionada**.
- La app y los flujos son propiedad de una **cuenta de servicio**, nunca de una persona. Si esa
  persona deja la empresa, la app no se cae.
- Conexiones compartidas explícitamente, no heredadas.
- Política DLP aplicada al entorno.
- Control de versiones de la solución exportada.

---

## 9. Riesgos y puntos abiertos

Detalle y seguimiento en [`decisiones-abiertas.md`](decisiones-abiertas.md).

| # | Riesgo / Pregunta | Impacto | Acción |
|---|---|---|---|
| 1 | **¿En qué tenant vive la app: TAMOIN o Repsol?** Define licencias, propiedad del dato y visibilidad para el cliente. | **Alto** | Resolver **antes** de Fase 1 |
| 2 | Licenciamiento Premium de Power Apps para todos los técnicos | Alto (costo) | Evaluar plan *por aplicación* vs *por usuario* según headcount real |
| 3 | Fase 0 se demora o llega incompleta | Alto (bloquea todo) | Plantillas precargadas + taller presencial + responsable nombrado por sistema |
| 4 | Códigos de reserva ingresados a mano → error de tipeo, desfase con SAP | Medio | Validación de formato, campo obligatorio para cerrar la solicitud, integración en Fase 6 |
| 5 | Stock de la app diverge del stock real de almacén | Medio | Inventario cíclico obligatorio + reporte de diferencias en Power BI |
| 6 | Adopción: el técnico sigue usando papel | Alto | Piloto acotado, retroalimentación, el papel se retira solo cuando la app ya funciona |
| 7 | Conectividad en la monoboya peor de lo previsto | Medio | Offline descartado. Si aparece en el piloto, se agrega caché local como cambio de alcance |
| 8 | Requisitos regulatorios (DICAPI, OCIMF, auditoría Repsol) no considerados | Medio | Confirmar en Fase 0 qué evidencia exige cada auditoría y modelarla desde el inicio |

---

## 10. Principio de trabajo

**No se inventan datos.** Todo lo que este paquete propone sobre la monoboya —sistemas, equipos,
frecuencias, materiales— está marcado como **propuesta a validar**, no como dato confirmado. El
equipo de mantenimiento de TAMOIN corrige, elimina lo que no aplica y agrega lo que falta.

Se entrega precargado porque es mucho más rápido corregir una lista que partir de una hoja en
blanco. Pero nada de lo precargado entra a la aplicación sin la firma de quien conoce el activo.
