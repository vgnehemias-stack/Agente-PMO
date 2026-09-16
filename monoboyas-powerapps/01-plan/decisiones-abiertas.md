# Decisiones abiertas e información faltante

Registro de todo lo que **no se sabe todavía** y hay que cerrar para ejecutar. Nada de esto se ha
supuesto en silencio: si aparece precargado en las plantillas, está marcado como propuesta.

**Leyenda de estado:** 🔴 Bloqueante · 🟡 Necesario para la fase indicada · 🟢 Deseable

---

## Bloqueantes — resolver antes de la Fase 1

| # | Pregunta | Por qué importa | Responsable sugerido |
|---|---|---|---|
| D-01 🔴 | **¿En qué tenant de Microsoft 365 vive la solución: el de TAMOIN o el de Repsol?** | Define quién paga las licencias, quién es dueño del dato, si Repsol puede consultar la app directamente, y qué pasa al terminar el contrato. Cambiar de tenant después es una migración completa. | Gerencia TAMOIN + TI Repsol |
| D-02 🔴 | **¿Cuántos usuarios y con qué rol?** (técnicos, supervisores, planificadores, almaceneros) | Determina el modelo de licenciamiento: *por usuario* (~US$20/mes) vs *por aplicación*. A partir de cierto número el cálculo se invierte. | TAMOIN Mantenimiento |
| D-03 🔴 | **¿Cuántas monoboyas entran al alcance?** ¿Solo una, o todas las del terminal? | Afecta el esfuerzo de Fase 0 (levantamiento) más que el de desarrollo. | TAMOIN + Repsol |
| D-04 🔴 | **¿Existe un plan de mantenimiento documentado hoy?** (Excel, procedimiento, plan del fabricante) | Si existe, la Fase 0 se reduce de semanas a días: se transcribe en vez de construirse. | TAMOIN Mantenimiento |

---

## Necesarios para la Fase 0 (levantamiento)

| # | Pregunta | Dónde impacta |
|---|---|---|
| D-05 🟡 | Jerarquía real de sistemas de la monoboya: ¿la propuesta de 12 sistemas aplica? ¿Sobra o falta alguno? | `01_jerarquia_activos.csv` |
| D-06 🟡 | ¿Existe una convención de TAG ya en uso? ¿Cuál? Si no, hay que definirla antes de cargar nada. | Todo el modelo — el TAG es la llave |
| D-07 🟡 | Frecuencias reales por equipo. ¿Vienen del fabricante, de OCIMF, de la experiencia, o de una exigencia de Repsol? | `02_planes_mantenimiento.csv` |
| D-08 🟡 | ¿Qué normas son de cumplimiento obligatorio? (OCIMF SMOG, GMPHOM 2009, API RP 2SK, DICAPI, sociedad clasificadora) | Campo `norma_referencia`, y qué evidencia guardar |
| D-09 🟡 | ¿Qué evidencia exige cada auditoría? (foto, medición firmada, informe de tercero) | Diseño de las gamas y del reporte PDF |
| D-10 🟡 | Catálogo actual de materiales: ¿existe en Excel? ¿Con códigos SAP? | `04_catalogo_materiales.csv` |
| D-11 🟡 | ¿Cuántos almacenes hay y dónde? ¿Hay stock a bordo de embarcación? | Tabla Almacén |
| D-12 🟡 | **Formato del código de reserva de SAP.** ¿Longitud fija? ¿Prefijo? Se necesita para validarlo. | Tabla Solicitud de material |
| D-13 🟡 | ¿Quién aprueba una solicitud de material, y hay monto o criticidad que escale la aprobación? | Flujo de aprobación |

---

## Necesarios para fases posteriores

| # | Pregunta | Fase |
|---|---|---|
| D-14 🟡 | ¿Se usa Microsoft Teams? ¿A qué canal van las alertas? | 2 |
| D-15 🟡 | ¿La firma del técnico tiene valor legal para Repsol, o basta con la trazabilidad de usuario? | 2 |
| D-16 🟡 | ¿Qué indicadores quiere ver la gerencia? (cumplimiento del plan, backlog, MTBF, costo) | 4 |
| D-17 🟡 | ¿Repsol necesita acceso de lectura a los tableros? | 4 |
| D-18 🟢 | ¿Hay histórico de mantenimientos anteriores que migrar? | 1 |
| D-19 🟢 | ¿Se quiere gestión de permisos de trabajo (PTW) dentro de la app? | Fuera de alcance hoy |
| D-20 🟢 | ¿Integración futura con SAP: lectura, escritura o ambas? ¿TI de Repsol la habilitaría? | 6 |

---

## Supuestos que estamos haciendo (y hay que confirmar)

Estos supuestos están incorporados en el diseño. Si alguno es falso, hay que ajustar antes de
construir.

1. **La monoboya es de tipo CALM** (*Catenary Anchor Leg Mooring*), la configuración más común para
   descarga de crudo. Si es SALM u otra, la jerarquía de sistemas cambia.
2. **El equipo de mantenimiento tiene smartphones o tablets** con Android o iOS razonablemente
   recientes, y cuenta corporativa de Microsoft 365.
3. **Hay conectividad aceptable** en los puntos donde se registra el trabajo (decisión ya tomada:
   sin offline).
4. **El inventario lo gestiona TAMOIN**, no Repsol. Si el almacén es de Repsol, el modelo de stock
   cambia de "gestionar" a "consultar".
5. **Una intervención en monoboya requiere embarcación y ventana operativa**, por lo que la
   planificación no puede ser puramente por fecha: hay una restricción logística real que la app
   debe reflejar (campo `ventana operativa` en la OT).
6. **El código de reserva lo genera SAP y alguien lo transcribe.** Si hoy nadie lo hace, hay que
   definir quién y cuándo.

---

## Cómo se cierra esto

La Fase 0 se cierra con un **taller presencial** con el equipo de mantenimiento donde:

1. Se recorre pantalla por pantalla el mockup (`03-mockups/mockup-pantallas.html`) para validar el
   flujo antes de construirlo.
2. Se revisa la jerarquía de sistemas propuesta, sistema por sistema.
3. Se asigna un **responsable nombrado por sistema** para llenar las plantillas, con fecha.
4. Se resuelven en la sala todas las preguntas 🔴 y las 🟡 de Fase 0.

Lo que no se resuelva en el taller se documenta aquí con responsable y fecha límite. **Sin dueño y
sin fecha, una pregunta abierta no se cierra sola.**
