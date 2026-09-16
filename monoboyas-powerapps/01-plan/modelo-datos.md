# Modelo de datos — Dataverse

Nueve tablas y dos catálogos menores. Nomenclatura en español, prefijo de publicador sugerido
`tam_` (TAMOIN).

**Convenciones:** `PK` clave primaria · `FK →` búsqueda (*lookup*) · `Choice` conjunto de opciones
· `Calc` columna calculada o de acumulación · ⚠️ campo a confirmar en Fase 0.

---

## Diagrama

```
Monoboya
   └─1:N─ Nodo del sistema ◄──────┐
              │  └──── nodo padre ─┘   (auto-referencia: cualquier profundidad)
              │
              ├─1:1─ Atributos técnicos
              ├─1:N─ Frecuencia de referencia
              ├─1:N─ Documento
              └─1:N─ Material por nodo ─N:1─ Material
                                              ├─1:N─ Stock ─N:1─ Almacén
                                              └─1:N─ Solicitud de material
Personal ──(perfil de acceso)──► toda la solución
```

La pieza central es **Nodo del sistema**: subsistemas y equipos viven en la misma tabla, y la
relación padre-hijo es la que produce tanto la vista global como el desglose.

---

## 1. Monoboya

| Campo | Tipo | Notas |
|---|---|---|
| Código | Texto (20) | PK |
| Nombre | Texto (100) | |
| Tipo | Choice | CALM / SALM / Otro ⚠️ |
| Terminal | Texto (100) | |
| Fabricante | Texto (100) | ⚠️ |
| Año de fabricación | Número entero | ⚠️ |
| Profundidad de operación (m) | Decimal | ⚠️ |
| Estado | Choice | Operativa / En mantenimiento / Fuera de servicio |
| Nodo raíz | FK → Nodo del sistema | La raíz de su árbol |

## 2. Nodo del sistema ⭐

**Tabla auto-referenciada.** Es la columna vertebral de la aplicación.

| Campo | Tipo | Notas |
|---|---|---|
| **Código oficial** | Texto (40) | PK — el código de la codificación de subsistemas. **Indexado y único** |
| Código provisional | Texto (40) | Puente temporal mientras llega la codificación oficial. Se retira tras la carga |
| Nombre | Texto (200) | |
| **Nodo padre** | FK → Nodo del sistema | Vacío solo en la raíz |
| Monoboya | FK → Monoboya | Denormalizado a propósito: evita recorrer el árbol en cada consulta |
| Nivel | Número entero | 1 monoboya · 2 subsistema · 3 equipo · 4 componente |
| Tipo de nodo | Choice | Monoboya / Subsistema / Equipo / Componente |
| Criticidad | Choice | A (crítico) / B (importante) / C (normal) |
| Estado | Choice | Operativo / Degradado / Fuera de servicio / Retirado |
| Descripción | Texto multilínea | |
| Ruta completa | Calc | `MB-01 ▸ Rodamiento ▸ Sistema de lubricación`. Facilita búsqueda y migas de pan |
| N° de partes | Calc | Hijos directos. Es lo que la vista global muestra por subsistema |
| **Coordenada X (%)** | Decimal 0–100 | Posición horizontal del punto sobre el esquema de la monoboya |
| **Coordenada Y (%)** | Decimal 0–100 | Posición vertical |
| Imagen de referencia | URL | Foto o recorte de plano que se muestra en el panel visual |

### Por qué auto-referenciada y no una tabla por nivel

1. **La codificación real puede tener más niveles de los previstos.** Un árbol los absorbe sin
   rehacer nada; cuatro tablas fijas obligarían a migrar.
2. **Un subsistema puede contener sub-subsistemas.** Con tablas por nivel, eso no se representa.
3. **La vista global y el desglose son la misma consulta** a distinta altura del árbol: filtrar
   por `nodo padre`. Una sola vista sirve para todos los niveles.
4. **Permite arrancar hoy**, sin esperar a ver la codificación.

### Reglas de integridad

- Un nodo no puede ser su propio ancestro (sin ciclos).
- Exactamente **una raíz por monoboya**.
- `nivel` debe coincidir con la profundidad real respecto de la raíz.
- El código oficial es **único en toda la solución**.

Las tres primeras se validan en la carga; la cuarta, con una clave alternativa de Dataverse.

### Las coordenadas son dato, no maqueta

Los tres campos del final son los que sostienen el panel visual (ver el plan maestro). Guardarlos
**en la tabla** y no en la pantalla es lo que evita que el esquema se vuelva inmanejable:

- Agregar un subsistema es **agregar una fila**, no editar la aplicación.
- Mover un punto es **cambiar un número** desde la propia ficha.
- Al ser porcentajes y no píxeles, el esquema **escala solo** en cualquier pantalla.
- El color de cada punto sale de los datos del nodo, no de la maqueta.

Se guardan en `Nodo del sistema` y no en una tabla aparte porque son un atributo del nodo: cada
subsistema tiene un único sitio en el dibujo.

## 3. Atributos técnicos

Separada del nodo porque solo aplica a equipos y componentes, no a subsistemas, y porque su
edición corresponde a un perfil distinto.

| Campo | Tipo | Notas |
|---|---|---|
| Nodo | FK → Nodo del sistema | 1:1 |
| Fabricante | Texto (100) | |
| Modelo | Texto (100) | |
| N° de serie | Texto (50) | |
| Fecha de instalación | Fecha | |
| Ubicación física | Choice | Cubierta / Casco / Interior / Superficie / Submarino / Fondo marino |
| Requiere buzo o ROV | Sí/No | Condiciona el acceso a la parte |
| Dimensiones | Texto (100) | Diámetro, longitud, capacidad ⚠️ |
| Material de construcción | Texto (100) | ⚠️ |
| Observaciones | Texto multilínea | |

## 4. Material

| Campo | Tipo | Notas |
|---|---|---|
| Código interno | Texto (30) | PK |
| **Código SAP** | Texto (30) | Puente con el ERP. Indexado |
| Descripción | Texto (200) | |
| Unidad de medida | Choice | UN / M / KG / L / JGO |
| Categoría | Choice | Repuesto / Consumible |
| Criticidad | Choice | Crítico / Normal |
| *Lead time* (días) | Número entero | Plazo de reposición |
| Stock mínimo | Decimal | Dispara alerta |
| Stock máximo | Decimal | |
| Activo | Sí/No | |

> Herramientas, EPP y servicios quedaron fuera del catálogo: pertenecen a la ejecución del
> trabajo, no a la composición del sistema.

## 5. Material por nodo

Lo que permite que al abrir un subsistema se vea de inmediato qué repuestos le corresponden.

| Campo | Tipo | Notas |
|---|---|---|
| Nodo | FK → Nodo del sistema | |
| Material | FK → Material | |
| Cantidad referencial | Decimal | Cuánto se suele necesitar. Referencia, no compromiso |
| Disponibilidad | Calc | Trae el stock del material para mostrarlo en la ficha del nodo |
| Observaciones | Texto (200) | |

Un mismo material puede colgar de varios nodos.

## 6. Stock

| Campo | Tipo | Notas |
|---|---|---|
| Material | FK → Material | |
| Almacén | FK → Almacén | |
| Cantidad disponible | Decimal | **Editable por el perfil Materiales** |
| Cantidad reservada | Decimal | Comprometida a una solicitud |
| Bajo mínimo | Calc | Disponible < Material.Stock mínimo |
| Fecha de último inventario | Fecha | Cuándo se contrastó contra el físico |
| Última actualización | Fecha y hora | Automática |

Clave única: `Material + Almacén`.

> **Diferencia con la versión anterior:** el stock ahora se edita directamente, con auditoría de
> Dataverse, en vez de derivarse de un libro de movimientos. Sin órdenes de trabajo que consuman
> material automáticamente, un libro de movimientos añadía complejidad sin aportar exactitud.
> El campo *fecha de último inventario* es lo que sostiene la confianza en la cifra.

## 7. Solicitud de material

Aquí vive el **código de reserva**.

| Campo | Tipo | Notas |
|---|---|---|
| Número | Autonumérico | `SM-{SEQNUM:00000}` |
| Material | FK → Material | |
| Nodo | FK → Nodo del sistema | Para qué parte del sistema se solicita |
| Cantidad solicitada | Decimal | |
| Solicitante | FK → Personal | |
| Fecha de solicitud | Fecha | |
| Estado | Choice | Solicitada → **Reservada** → Entregada → Cerrada / Rechazada |
| **Código de reserva** | Texto (30) | Ingreso manual. Obligatorio para pasar a *Reservada* |
| Fecha estimada de entrega | Fecha | |
| Comentarios | Texto multilínea | |

> **Sobre el código de reserva:** al no haber integración con SAP, este campo es el único puente
> con el ERP. Por eso es obligatorio para avanzar a *Reservada*, lleva validación de formato (a
> definir en Fase 0 ⚠️) y queda auditado. Es el punto más frágil del circuito.

## 8. Frecuencia de referencia

**Información, no planificación.** Se muestra en la ficha del nodo; no genera nada.

| Campo | Tipo | Notas |
|---|---|---|
| Código | Texto (20) | PK |
| Nodo | FK → Nodo del sistema | |
| Descripción | Texto (200) | |
| Tipo | Choice | Preventivo / Predictivo / Inspección legal / Lubricación / Limpieza |
| **Frecuencia — valor** | Número entero | p. ej. `3` |
| **Frecuencia — unidad** | Choice | Días / Semanas / Meses / Años |
| Fecha última ejecución | Fecha | Dato informativo, de carga manual |
| Próxima referencial | Calc | Última + frecuencia. **Solo se muestra**; no dispara nada |
| Norma de referencia | Texto (100) | OCIMF, API RP 2SK, DICAPI, manual del fabricante ⚠️ |
| Requiere buzo o ROV | Sí/No | |

> La frecuencia se guarda como *valor + unidad*, no como texto libre ni como días: así «cada 3
> meses» no se degrada a «90 días» y el cálculo respeta el mes calendario, que es como lo piensa
> el equipo.

## 9. Documento

Planos, manuales, certificados e informes.

| Campo | Tipo | Notas |
|---|---|---|
| Nombre | Texto (200) | PK |
| Nodo | FK → Nodo del sistema | De qué parte del sistema cuelga |
| Tipo | Choice | Plano / Manual / Memoria técnica / Certificado de manguera (GMPHOM) / Certificado DICAPI / Certificado de fabricación / Informe de inspección / Procedimiento ⚠️ |
| Entidad emisora | Texto (100) | |
| N° de documento | Texto (50) | |
| Revisión | Texto (10) | Los planos se revisan: interesa la versión vigente |
| Fecha de emisión | Fecha | |
| **Fecha de vencimiento** | Fecha | Vacía en planos y manuales, que no vencen |
| Vigencia | Calc | Vigente / Por vencer / Vencido / No aplica |
| Enlace | URL | SharePoint |
| Vigente | Sí/No | Permite conservar revisiones anteriores sin que confundan |

---

## Catálogos menores

**Almacén** — código, nombre, ubicación, responsable.
**Personal** — nombre, usuario de Entra ID, correo, perfil de acceso, activo.

---

## Perfiles de acceso

| Perfil | Lee | Actualiza |
|---|---|---|
| **Consulta** | Todo | Nada |
| **Materiales** | Todo | Material por nodo, Stock, Solicitudes y código de reserva |
| **Documentación** | Todo | Documentos: alta, reemplazo, revisión y fechas |
| **Técnico** | Todo | Atributos técnicos y Frecuencias de referencia |
| **Administrador** | Todo | Todo, incluida la jerarquía |

**La jerarquía queda fuera de la edición en la app a propósito.** Es la columna vertebral del
sistema: un cambio accidental en un código rompería todas las referencias de materiales,
frecuencias y documentos. Se modifica por carga controlada.

Dataverse audita cada cambio con usuario, campo, valor anterior y fecha, sin desarrollo adicional.

---

## Automatizaciones (Power Automate)

| Flujo | Disparador | Qué hace |
|---|---|---|
| **Alerta de vencimientos** | Diario | Documentos que vencen en 60/30/7 días → Teams y correo al responsable |
| **Alerta de stock bajo mínimo** | Diario | Materiales con disponible < mínimo, priorizando los de mayor *lead time* |
| **Recordatorio de inventario** | Mensual | Materiales cuya *fecha de último inventario* supera el umbral acordado |
| **Recordatorio de código de reserva** | Diario | Solicitudes aprobadas sin código de reserva registrado |

Ningún flujo crea trabajo ni programa mantenimientos: todos avisan sobre la información.

---

## Volumetría estimada (1 monoboya)

| Tabla | Registros |
|---|---|
| Nodo del sistema | 80 – 200 ⚠️ |
| Atributos técnicos | 70 – 180 |
| Frecuencia de referencia | 40 – 120 ⚠️ |
| Material | 30 – 150 ⚠️ |
| Material por nodo | 50 – 300 |
| Documento | 30 – 200 |
| Solicitud de material | 50 – 200 / año |

Volumen holgado para Dataverse. El modelo soporta varias monoboyas sin cambios: cada una es otro
árbol bajo su propia raíz.
