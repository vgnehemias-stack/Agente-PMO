"""Orquestación de la extracción: prompt + proveedor + validación Pydantic."""

import json
from typing import Dict

from pydantic import ValidationError

from .proveedores.base import ErrorProveedor, ProveedorLLM
from .schemas import PlanProyecto

PROMPT_SISTEMA = """Eres un analista PMO senior. Tu tarea es leer fuentes de \
información no estructurada sobre la planificación de un proyecto (notas de \
reunión, correos, hojas de cálculo desordenadas, actas, documentos) y \
consolidarlas en UN solo plan de proyecto estructurado.

Reglas de extracción:
- NO inventes información. Si un dato (fecha, responsable, duración) no aparece \
en las fuentes, deja el campo nulo o con valor "desconocido".
- Normaliza todas las fechas al formato ISO AAAA-MM-DD. Si una fecha es ambigua \
(ej. "el viernes", "fin de mes") y no puedes resolverla con certeza a partir \
del contexto, déjala nula y explica la ambigüedad en el campo `notas`.
- Consolida duplicados: si la misma tarea aparece en varias fuentes con \
distintos nombres, crea UNA sola tarea y combina la información.
- Asigna IDs secuenciales: tareas T-001, T-002…; hitos H-001…; riesgos R-001….
- Registra dependencias entre tareas SOLO si son explícitas o claramente \
implícitas en las fuentes ("después de", "requiere", "bloqueado por").
- Distingue tareas (trabajo con duración) de hitos (eventos o entregables \
puntuales con fecha).
- Identifica riesgos tanto explícitos como los evidentes por el contexto \
(retrasos mencionados, recursos faltantes, decisiones pendientes).
- En `informacion_faltante` lista los datos que un PMO debería solicitar porque \
no aparecen en las fuentes (ej. fechas sin definir, tareas sin responsable).
- Escribe todo el contenido en español."""


class ErrorExtraccion(RuntimeError):
    """La extracción no produjo un plan válido."""


def construir_mensaje_usuario(fuentes: Dict[str, str], contexto: str = None) -> str:
    partes = []
    if contexto:
        partes.append(f"Contexto adicional del usuario: {contexto}\n")
    partes.append(
        "Consolida las siguientes fuentes en un plan de proyecto estructurado:\n"
    )
    for nombre, contenido in fuentes.items():
        partes.append(f"=== Fuente: {nombre} ===\n{contenido}\n")
    return "\n".join(partes)


def extraer_plan(
    proveedor: ProveedorLLM,
    fuentes: Dict[str, str],
    contexto: str = None,
    max_reparaciones: int = 2,
) -> PlanProyecto:
    """Extrae un PlanProyecto validado a partir de las fuentes.

    Si el JSON del proveedor no valida contra el esquema (frecuente en modelos
    locales), se reenvían los errores de validación para que el modelo corrija,
    hasta `max_reparaciones` veces.
    """
    schema = PlanProyecto.model_json_schema()
    mensajes = [
        {"role": "user", "content": construir_mensaje_usuario(fuentes, contexto)}
    ]

    ultimo_error = None
    for intento in range(1 + max_reparaciones):
        datos = proveedor.generar_json(PROMPT_SISTEMA, mensajes, schema)
        try:
            return PlanProyecto.model_validate(datos)
        except ValidationError as exc:
            ultimo_error = exc
            if intento == max_reparaciones:
                break
            print(
                f"Aviso: la salida del proveedor no validó (intento {intento + 1}); "
                "solicitando corrección al modelo..."
            )
            mensajes = mensajes + [
                {"role": "assistant", "content": json.dumps(datos, ensure_ascii=False)},
                {
                    "role": "user",
                    "content": (
                        "El JSON anterior no cumple el esquema requerido. "
                        f"Errores de validación:\n{exc}\n\n"
                        "Devuelve el plan completo corregido, cumpliendo "
                        "exactamente el esquema."
                    ),
                },
            ]

    raise ErrorExtraccion(
        "El proveedor no produjo un plan válido tras varios intentos. "
        f"Último error de validación:\n{ultimo_error}"
    )


__all__ = [
    "ErrorExtraccion",
    "ErrorProveedor",
    "extraer_plan",
    "construir_mensaje_usuario",
    "PROMPT_SISTEMA",
]
