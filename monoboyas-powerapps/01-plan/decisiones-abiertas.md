# Decisiones abiertas e información faltante

Registro de lo que **no se sabe todavía** y hay que cerrar para ejecutar. Nada de esto se ha
supuesto en silencio: lo que aparece precargado en las plantillas está marcado como propuesta.

**Leyenda:** 🔴 Bloqueante · 🟡 Necesario para la fase indicada · 🟢 Deseable

---

## Bloqueantes

| # | Pregunta | Por qué importa | Responsable |
|---|---|---|---|
| D-01 🔴 | **La codificación oficial de subsistemas.** Existe y se va a compartir, pero todavía no está en nuestras manos | Es el eje de toda la aplicación: define los identificadores, cuántos niveles tiene la jerarquía y cómo se agrupa la información. Sin ella no se carga nada | TAMOIN Mantenimiento |
| D-02 🔴 | **¿En qué tenant de Microsoft 365 vive la solución: el de TAMOIN o el de Repsol?** | Define quién paga las licencias, de quién es el dato, si Repsol consulta la app directamente y qué pasa al terminar el contrato. Cambiar de tenant después es una migración completa | Gerencia TAMOIN + TI Repsol |
| D-03 🔴 | **¿Cuántos usuarios, y cuántos solo consultan?** | Determina el modelo de licenciamiento. Si la mayoría solo lee, conviene evaluar el plan *por aplicación* | TAMOIN Mantenimiento |
| D-04 🔴 | **¿Cuántas monoboyas entran al alcance?** | Afecta al esfuerzo de levantamiento más que al de desarrollo. El modelo ya soporta varias | TAMOIN + Repsol |

---

## Necesarios para la Fase 0

| # | Pregunta | Dónde impacta |
|---|---|---|
| D-05 🟡 | ¿Cuántos niveles tiene la codificación real? ¿Hay subsistemas que se dividen en sub-subsistemas? | Profundidad del árbol. Ya está mitigado, pero conviene saberlo |
| D-06 🟡 | ¿La propuesta de 12 subsistemas se corresponde con la codificación? ¿Sobra o falta alguno? | `01_jerarquia_subsistemas.csv` |
| D-07 🟡 | **¿Existen los planos y manuales en digital?** ¿Dónde están hoy? ¿Cuáles habría que digitalizar? | `05_documentos_planos.csv` y el esfuerzo de carga |
| D-08 🟡 | ¿Qué certificados son de cumplimiento obligatorio y quién los emite? (DICAPI, GMPHOM, clasificadora) | Tipos de documento y alertas de vencimiento |
| D-09 🟡 | Frecuencias reales por equipo: ¿del fabricante, de OCIMF, de la experiencia, o exigidas por Repsol? | `02_frecuencias_referencia.csv` |
| D-10 🟡 | ¿Existe el catálogo de materiales en Excel? ¿Con códigos SAP? | `03_catalogo_materiales.csv` |
| D-11 🟡 | ¿Cuántos almacenes hay y quién es responsable de cada uno? | Tabla Almacén |
| D-12 🟡 | **Formato del código de reserva de SAP.** ¿Longitud fija? ¿Prefijo? | Validación en Solicitud de material |
| D-13 🟡 | ¿Quién es responsable de mantener actualizada cada clase de información? | Es el riesgo principal del proyecto: ver D-16 |

---

## Necesarios para fases posteriores

| # | Pregunta | Fase |
|---|---|---|
| D-14 🟡 | ¿Se usa Microsoft Teams? ¿A qué canal van las alertas de vencimiento y de stock? | 4 |
| D-15 🟡 | ¿Con qué periodicidad se hace inventario físico? Define el umbral del recordatorio | 3 |
| D-16 🟡 | ¿Repsol necesita acceso de consulta a la aplicación? ¿De solo lectura? | 2 |
| D-17 🟢 | ¿Hay histórico de mantenimientos anteriores que valga la pena cargar como referencia? | 3 |
| D-18 🟢 | ¿Se quiere tablero en Power BI, o basta con las vistas de la app? | 4 |
| D-19 🟢 | ¿Integración futura con SAP para stock y reservas? ¿TI de Repsol la habilitaría? | Fuera de alcance hoy |

---

## Supuestos incorporados al diseño

Si alguno es falso, hay que ajustar antes de construir.

1. **La monoboya es de tipo CALM.** Si es SALM u otra configuración, la lista de subsistemas
   cambia.
2. **La codificación de subsistemas es jerárquica** (un código de equipo permite deducir a qué
   subsistema pertenece, o al menos existe esa relación documentada).
3. **El equipo tiene cuenta corporativa de Microsoft 365.**
4. **El inventario lo gestiona TAMOIN**, no Repsol. Si el almacén es de Repsol, el stock pasa de
   «gestionar» a «consultar» y la edición desaparece.
5. **Los planos y certificados pueden almacenarse en SharePoint** sin restricción contractual de
   confidencialidad que lo impida.
6. **El código de reserva lo genera SAP y alguien lo transcribe.** Si hoy nadie lo hace, hay que
   definir quién y cuándo.

---

## El riesgo que más vale la pena mirar

Una aplicación de consulta vive o muere por la **vigencia de su información**. Se carga completa,
se usa unos meses, y si nadie la actualiza pasa a ser una foto vieja en la que ya nadie confía.

Por eso el diseño incluye edición desde la propia app, recordatorios de inventario y alertas de
vencimiento. Pero ninguna de esas tres cosas funciona sin lo que pide **D-13**: un **responsable
nombrado por cada clase de información**. Sin dueño, la app se desactualiza aunque tenga todos los
avisos del mundo.

---

## Cómo se cierra esto

La Fase 0 se cierra con un **taller presencial** donde:

1. Se entrega y se revisa **la codificación oficial de subsistemas** — primer punto del orden del día.
2. Se recorre el prototipo (`03-mockups/mockup-pantallas.html`) para validar la navegación antes
   de construirla.
3. Se contrasta la jerarquía propuesta contra la codificación real, subsistema por subsistema.
4. Se asigna **responsable nombrado y fecha** por cada plantilla, y responsable permanente por
   cada clase de información.
5. Se resuelven en la sala todas las preguntas 🔴 y las 🟡 de Fase 0.

Lo que no se resuelva se documenta aquí con responsable y fecha límite. **Sin dueño y sin fecha,
una pregunta abierta no se cierra sola.**
