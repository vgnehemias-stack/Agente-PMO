# Modelo de datos — Dataverse

Especificación de las 16 tablas de la solución. Nomenclatura en español, prefijo de publicador
sugerido `tam_` (TAMOIN).

**Convenciones:**
- `PK` = clave primaria (columna principal de Dataverse)
- `FK` → = búsqueda (*lookup*) hacia otra tabla
- `Choice` = conjunto de opciones
- `Calc` = columna calculada o de acumulación (*rollup*)
- ⚠️ = campo cuyo contenido debe confirmarse en Fase 0

---

## Diagrama de relaciones

```
Terminal
   └─1:N─ Monoboya
             └─1:N─ Sistema
                       └─1:N─ Equipo ──────────────┬─1:N─ Plan de mantenimiento
                                │                  │            ├─1:N─ Tarea de plan (gama)
                                │                  │            └─1:N─ Material por plan (BOM) ─N:1─ Material
                                ├─1:N─ Medición    │
                                ├─1:N─ Documento   │
                                └─1:N─ Orden de Trabajo ◄──────┘
                                           ├─1:N─ Tarea de OT
                                           ├─1:N─ Hallazgo ──(genera)──► Orden de Trabajo
                                           ├─1:N─ Movimiento de inventario ─N:1─ Material
                                           └─1:N─ Solicitud de material ───N:1─ Material

Material ─1:N─ Stock ─N:1─ Almacén
Personal ─(responsable / ejecutor)─► Orden de Trabajo
```

---

# Bloque A — Tablas maestras

## A1. Terminal

Permite que la solución escale a otros terminales de Repsol sin rediseño.

| Campo | Tipo | Notas |
|---|---|---|
| Código | Texto (20) | PK |
| Nombre | Texto (100) | |
| Ubicación | Texto (200) | |
| Cliente | Texto (100) | Repsol / La Pampilla |
| Activo | Sí/No | |

## A2. Monoboya (Activo)

| Campo | Tipo | Notas |
|---|---|---|
| Código | Texto (20) | PK |
| Nombre | Texto (100) | |
| Terminal | FK → Terminal | |
| Tipo | Choice | CALM / SALM / Otro ⚠️ |
| Fabricante | Texto (100) | ⚠️ |
| Año de fabricación | Número entero | ⚠️ |
| Profundidad de operación (m) | Decimal | ⚠️ |
| Estado operativo | Choice | Operativa / En mantenimiento / Fuera de servicio |
| Fecha última inspección mayor | Fecha | |
| Observaciones | Texto multilínea | |

## A3. Sistema

Segundo nivel de la jerarquía. Agrupa equipos por función.

| Campo | Tipo | Notas |
|---|---|---|
| Código | Texto (20) | PK |
| Nombre | Texto (100) | |
| Monoboya | FK → Monoboya | |
| Criticidad | Choice | A (crítico) / B (importante) / C (normal) |
| Responsable técnico | FK → Personal | |
| Descripción | Texto multilínea | |

## A4. Equipo / Componente

Nivel operativo. Es el objeto al que se le cuelgan planes, mediciones y documentos.

| Campo | Tipo | Notas |
|---|---|---|
| TAG | Texto (30) | PK — identificador único del equipo |
| Descripción | Texto (200) | |
| Sistema | FK → Sistema | |
| Fabricante | Texto (100) | |
| Modelo | Texto (100) | |
| N° de serie | Texto (50) | |
| Fecha de instalación | Fecha | |
| Criticidad | Choice | A / B / C |
| Ubicación física | Choice | Cubierta / Casco / Submarino / Fondo marino / Interior |
| Estado | Choice | Operativo / Degradado / Fuera de servicio / Retirado |
| Requiere buzo/ROV | Sí/No | Determina logística de la intervención |
| Observaciones | Texto multilínea | |

## A5. Material

Catálogo de repuestos y consumibles.

| Campo | Tipo | Notas |
|---|---|---|
| Código interno | Texto (30) | PK |
| **Código SAP** | Texto (30) | Puente con el ERP. Indexado. |
| Descripción | Texto (200) | |
| Unidad de medida | Choice | UN / M / KG / L / JGO / GLB |
| Categoría | Choice | Repuesto / Consumible / Herramienta / EPP / Servicio ⚠️ |
| Criticidad | Choice | Crítico / Normal |
| *Lead time* (días) | Número entero | Plazo de reposición |
| Stock mínimo | Decimal | Dispara alerta |
| Stock máximo | Decimal | |
| Activo | Sí/No | |

## A6. Almacén

| Campo | Tipo | Notas |
|---|---|---|
| Código | Texto (20) | PK |
| Nombre | Texto (100) | |
| Ubicación | Texto (200) | |
| Responsable | FK → Personal | |
| Tipo | Choice | Central / Obra / Embarcación ⚠️ |

## A7. Personal

| Campo | Tipo | Notas |
|---|---|---|
| Nombre completo | Texto (100) | PK |
| Usuario | FK → Usuario (Entra ID) | Vincula con la identidad de M365 |
| Correo | Correo | |
| Rol | Choice | Técnico / Supervisor / Planificador / Almacenero / Administrador |
| Especialidad | Choice | Mecánica / Eléctrica / Instrumentación / Estructuras / Buceo / Pintura ⚠️ |
| Certificaciones | Texto multilínea | |
| Activo | Sí/No | |

---

# Bloque B — Planificación

## B1. Plan de mantenimiento

El corazón de la app. Define **qué se mantiene y cada cuánto**.

| Campo | Tipo | Notas |
|---|---|---|
| Código | Texto (30) | PK |
| Nombre | Texto (200) | |
| Equipo | FK → Equipo | |
| Tipo | Choice | Preventivo / Predictivo / Inspección legal / Lubricación / Limpieza |
| **Frecuencia — valor** | Número entero | p. ej. `3` |
| **Frecuencia — unidad** | Choice | Días / Semanas / Meses / Años |
| Fecha última ejecución | Fecha | Se actualiza al cerrar una OT |
| **Fecha próxima ejecución** | Fecha | Calculada por flujo: última + frecuencia |
| Horizonte de generación (días) | Número entero | Con cuánta anticipación se crea la OT. Por defecto 30 |
| Duración estimada (h) | Decimal | |
| Especialidad requerida | Choice | Igual que Personal.Especialidad |
| N° de técnicos | Número entero | |
| Requiere parada operativa | Sí/No | |
| Requiere buzo/ROV | Sí/No | |
| Norma de referencia | Texto (100) | OCIMF, API RP 2SK, DICAPI… ⚠️ |
| Activo | Sí/No | Permite desactivar sin borrar historial |

> **Nota de diseño:** la frecuencia se guarda como *valor + unidad*, no como un texto libre ni como
> días. Así "cada 3 meses" no se degrada a "90 días" y el cálculo de la próxima fecha respeta los
> meses calendario, que es como lo piensa el equipo.

## B2. Tarea de plan (gama)

Los pasos del checklist. Es la plantilla que se copia a cada OT.

| Campo | Tipo | Notas |
|---|---|---|
| Plan | FK → Plan de mantenimiento | |
| N° de paso | Número entero | Orden de ejecución |
| Descripción | Texto (500) | |
| **Tipo de registro** | Choice | OK/NO OK / Numérico / Texto / Foto / Firma / Selección |
| Valor mínimo | Decimal | Solo si Numérico — valida el rango |
| Valor máximo | Decimal | Solo si Numérico |
| Unidad | Texto (20) | mm, mV, bar, °C… |
| Obligatorio | Sí/No | Bloquea el cierre de la OT si queda pendiente |
| Requiere foto | Sí/No | Fuerza evidencia gráfica |
| Ayuda | Texto (500) | Instrucción que ve el técnico al tocar el "?" |

## B3. Material por plan (BOM)

**Tabla clave del proyecto.** Es la que permite responder *"¿tengo stock para lo que viene?"*.

| Campo | Tipo | Notas |
|---|---|---|
| Plan | FK → Plan de mantenimiento | |
| Material | FK → Material | |
| Cantidad por ejecución | Decimal | |
| Obligatorio | Sí/No | Si falta y es obligatorio, la OT no se libera |

---

# Bloque C — Transaccionales

## C1. Orden de Trabajo (OT)

| Campo | Tipo | Notas |
|---|---|---|
| Número | Autonumérico | PK — `OT-{SEQNUM:00000}` |
| Plan origen | FK → Plan de mantenimiento | Vacío si es correctiva |
| Equipo | FK → Equipo | |
| Tipo | Choice | Preventiva / Correctiva / Predictiva / Inspección legal |
| **Estado** | Choice | Planificada → Con materiales → Liberada → En ejecución → Ejecutada → Cerrada / Cancelada |
| Prioridad | Choice | Urgente / Alta / Normal / Baja |
| Fecha programada | Fecha | |
| Fecha inicio real | Fecha y hora | |
| Fecha fin real | Fecha y hora | |
| Responsable | FK → Personal | |
| Ejecutores | N:N → Personal | |
| **Semáforo de materiales** | Choice | Completo / Parcial / Sin stock |
| Horas reales | Decimal | |
| Ventana operativa | Texto (100) | Restricción de marea, buque, clima ⚠️ |
| Observaciones | Texto multilínea | |
| % avance | Calc | Tareas conformes / total de tareas |
| Enlace al reporte PDF | URL | SharePoint |

### Máquina de estados

```
Planificada ──(flujo verifica BOM)──► Con materiales ──(supervisor)──► Liberada
                                            │
                                    (falta material)
                                            ▼
                                   genera Solicitud
                                            
Liberada ──(técnico inicia)──► En ejecución ──(checklist completo)──► Ejecutada
                                                                          │
                                                             (supervisor valida + firma)
                                                                          ▼
                                                                       Cerrada
```

Al pasar a **Cerrada**: se actualiza `fecha última ejecución` del plan, se recalcula
`fecha próxima ejecución`, se descuenta el stock consumido y se genera el PDF.

## C2. Tarea de OT

Instancia de la gama. **Se copia al crear la OT y queda congelada** — si mañana cambia el plan, el
historial de lo que realmente se hizo no se altera. Esto es esencial para auditoría.

| Campo | Tipo | Notas |
|---|---|---|
| OT | FK → Orden de Trabajo | |
| N° de paso | Número entero | |
| Descripción | Texto (500) | Copiada de la gama |
| Tipo de registro | Choice | Copiado de la gama |
| Resultado | Texto (500) | |
| Valor medido | Decimal | |
| Conforme | Sí/No | |
| Fuera de rango | Calc | Verdadero si el valor medido sale de mín/máx |
| Comentario | Texto multilínea | |
| Foto | URL | SharePoint |
| Completada por | FK → Personal | |
| Fecha de registro | Fecha y hora | |

## C3. Hallazgo

| Campo | Tipo | Notas |
|---|---|---|
| Número | Autonumérico | `HA-{SEQNUM:00000}` |
| OT origen | FK → Orden de Trabajo | Puede ser nulo (hallazgo espontáneo) |
| Equipo | FK → Equipo | |
| Descripción | Texto multilínea | |
| Severidad | Choice | Crítica / Alta / Media / Baja |
| Foto | URL | |
| Reportado por | FK → Personal | |
| Fecha | Fecha y hora | |
| Estado | Choice | Abierto / En análisis / En ejecución / Cerrado / Descartado |
| OT correctiva | FK → Orden de Trabajo | La que se generó para resolverlo |

## C4. Stock

**No se edita a mano.** Se deriva de los movimientos por flujo.

| Campo | Tipo | Notas |
|---|---|---|
| Material | FK → Material | |
| Almacén | FK → Almacén | |
| Cantidad disponible | Decimal | Libre para consumir |
| Cantidad reservada | Decimal | Comprometida a una OT liberada |
| Cantidad en tránsito | Decimal | Solicitada y aprobada, aún no recibida |
| Bajo mínimo | Calc | Disponible < Material.Stock mínimo |
| Última actualización | Fecha y hora | |

Clave única: `Material + Almacén`.

## C5. Movimiento de inventario

Libro mayor del inventario. **Solo se inserta, nunca se modifica ni se borra** — esa es la
garantía de auditabilidad.

| Campo | Tipo | Notas |
|---|---|---|
| Número | Autonumérico | `MV-{SEQNUM:00000}` |
| Material | FK → Material | |
| Almacén | FK → Almacén | |
| Tipo | Choice | Entrada / Salida / Ajuste / Devolución / Traspaso |
| Cantidad | Decimal | Positiva; el tipo define el signo |
| OT asociada | FK → Orden de Trabajo | |
| Solicitud asociada | FK → Solicitud de material | |
| Motivo | Texto (200) | |
| Usuario | FK → Personal | |
| Fecha | Fecha y hora | |

## C6. Solicitud de material

Aquí vive el **código de reserva**.

| Campo | Tipo | Notas |
|---|---|---|
| Número | Autonumérico | `SM-{SEQNUM:00000}` |
| OT | FK → Orden de Trabajo | |
| Material | FK → Material | |
| Cantidad solicitada | Decimal | |
| Cantidad atendida | Decimal | |
| Solicitante | FK → Personal | |
| Fecha de solicitud | Fecha | |
| **Estado** | Choice | Borrador → Solicitada → Aprobada → Reservada → Entregada → Cerrada / Rechazada |
| Aprobador | FK → Personal | |
| Fecha de aprobación | Fecha | |
| **Código de reserva** | Texto (30) | Ingreso manual. Obligatorio para pasar a *Reservada* |
| Fecha estimada de entrega | Fecha | |
| Comentarios | Texto multilínea | |

> **Sobre el código de reserva:** al no haber integración con SAP, este campo es el único puente
> con el ERP. Por eso es obligatorio para avanzar de *Aprobada* a *Reservada*, lleva validación de
> formato (a definir en Fase 0 ⚠️) y queda auditado. Es el punto más frágil del circuito y hay que
> tratarlo como tal.

---

# Bloque D — Auxiliares

## D1. Medición

Habilita mantenimiento predictivo en fases posteriores: si se guardan las lecturas, se pueden
graficar tendencias y anticipar fallas en vez de esperar la frecuencia.

| Campo | Tipo | Notas |
|---|---|---|
| Equipo | FK → Equipo | |
| Tipo de medición | Choice | Potencial catódico / Espesor de cadena / Tensión de amarre / Horas de operación / Presión / Espesor de pared ⚠️ |
| Valor | Decimal | |
| Unidad | Texto (20) | |
| Fecha | Fecha y hora | |
| OT | FK → Orden de Trabajo | |
| Registrado por | FK → Personal | |
| Dentro de rango | Sí/No | |

## D2. Documento / Certificado

| Campo | Tipo | Notas |
|---|---|---|
| Nombre | Texto (200) | PK |
| Equipo | FK → Equipo | |
| Monoboya | FK → Monoboya | Para documentos del activo completo |
| Tipo | Choice | Certificado de manguera (GMPHOM) / Certificado DICAPI / Informe de inspección subacuática / Plano / Manual / Procedimiento ⚠️ |
| Entidad emisora | Texto (100) | |
| N° de documento | Texto (50) | |
| Fecha de emisión | Fecha | |
| **Fecha de vencimiento** | Fecha | Dispara alertas a 60/30/7 días |
| Estado | Calc | Vigente / Por vencer / Vencido |
| Enlace | URL | SharePoint |

---

# Roles de seguridad

| Rol | Permisos |
|---|---|
| **Técnico** | Lee maestros y planes. Lee y actualiza **sus** OT. Crea hallazgos y mediciones. Crea solicitudes en borrador. No ve ni edita stock. |
| **Supervisor** | Todo lo del técnico sobre cualquier OT. Libera y cierra OT. Aprueba solicitudes. Firma. |
| **Planificador** | Crea y edita planes, gamas y BOM. Crea OT manuales. Lectura total. |
| **Almacenero** | Crea movimientos de inventario. Registra código de reserva. Atiende solicitudes. Lectura de OT. |
| **Administrador** | Todo, incluyendo maestros y configuración. |

La seguridad a nivel de registro de Dataverse permite que el técnico solo vea sus propias OT sin
filtros en la app — es el servidor el que restringe, no la pantalla. Eso importa: un filtro en la
app es cosmético, un permiso de Dataverse es real.

---

# Volumetría estimada

| Tabla | Registros año 1 (estimado, 1 monoboya) |
|---|---|
| Equipo | 80 – 150 ⚠️ |
| Plan de mantenimiento | 100 – 250 ⚠️ |
| Tarea de plan | 800 – 2.500 |
| Orden de Trabajo | 600 – 1.500 |
| Tarea de OT | 6.000 – 20.000 |
| Movimiento de inventario | 1.000 – 3.000 |

Volumen cómodo para Dataverse. La tabla `Tarea de OT` es la que más crece: conviene indexar por
`OT` y archivar OT cerradas con más de 3 años si el volumen molesta.
