"""Esquemas Pydantic que definen la estructura de un plan de proyecto.

Estos modelos definen el contrato de salida del agente: los proveedores LLM
generan JSON con esta forma exacta y el extractor lo valida contra ellos.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Estado(str, Enum):
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"
    BLOQUEADA = "bloqueada"
    CANCELADA = "cancelada"
    DESCONOCIDO = "desconocido"


class Prioridad(str, Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"
    DESCONOCIDA = "desconocida"


class NivelRiesgo(str, Enum):
    ALTO = "alto"
    MEDIO = "medio"
    BAJO = "bajo"
    DESCONOCIDO = "desconocido"


class Tarea(BaseModel):
    id: str = Field(description="Identificador corto y único, ej. 'T-001'")
    nombre: str = Field(description="Nombre breve de la tarea")
    descripcion: Optional[str] = Field(
        default=None, description="Detalle de la tarea si la fuente lo menciona"
    )
    fase: Optional[str] = Field(
        default=None,
        description="Fase o etapa del proyecto a la que pertenece (ej. 'Diseño', 'Ejecución')",
    )
    responsable: Optional[str] = Field(
        default=None, description="Persona o equipo responsable, si se menciona"
    )
    fecha_inicio: Optional[str] = Field(
        default=None, description="Fecha de inicio en formato ISO (AAAA-MM-DD), si se conoce"
    )
    fecha_fin: Optional[str] = Field(
        default=None, description="Fecha de fin o compromiso en formato ISO (AAAA-MM-DD)"
    )
    duracion_dias: Optional[int] = Field(
        default=None, description="Duración estimada en días, si se menciona"
    )
    estado: Estado = Field(
        default=Estado.DESCONOCIDO, description="Estado actual de la tarea"
    )
    prioridad: Prioridad = Field(
        default=Prioridad.DESCONOCIDA, description="Prioridad de la tarea"
    )
    dependencias: List[str] = Field(
        default_factory=list,
        description="IDs de tareas de las que depende esta tarea (ej. ['T-001'])",
    )
    notas: Optional[str] = Field(
        default=None,
        description="Ambigüedades, supuestos o contexto relevante detectado en la fuente",
    )


class Hito(BaseModel):
    id: str = Field(description="Identificador corto y único, ej. 'H-001'")
    nombre: str = Field(description="Nombre del hito o entregable clave")
    fecha: Optional[str] = Field(
        default=None, description="Fecha comprometida en formato ISO (AAAA-MM-DD)"
    )
    descripcion: Optional[str] = Field(default=None)
    tareas_asociadas: List[str] = Field(
        default_factory=list, description="IDs de tareas que habilitan este hito"
    )


class Riesgo(BaseModel):
    id: str = Field(description="Identificador corto y único, ej. 'R-001'")
    descripcion: str = Field(description="Descripción del riesgo o problema detectado")
    nivel: NivelRiesgo = Field(default=NivelRiesgo.DESCONOCIDO)
    mitigacion: Optional[str] = Field(
        default=None, description="Acción de mitigación si la fuente la menciona"
    )
    responsable: Optional[str] = Field(default=None)


class Interesado(BaseModel):
    nombre: str = Field(description="Nombre de la persona o área")
    rol: Optional[str] = Field(
        default=None, description="Rol en el proyecto (sponsor, PM, líder técnico, etc.)"
    )


class PlanProyecto(BaseModel):
    """Plan de proyecto consolidado extraído de fuentes no estructuradas."""

    nombre_proyecto: str = Field(
        description="Nombre del proyecto inferido de las fuentes; usa 'Proyecto sin nombre' si no es identificable"
    )
    objetivo: Optional[str] = Field(
        default=None, description="Objetivo o alcance del proyecto, si se menciona"
    )
    fecha_inicio: Optional[str] = Field(
        default=None, description="Fecha de inicio del proyecto (AAAA-MM-DD)"
    )
    fecha_fin: Optional[str] = Field(
        default=None, description="Fecha de término comprometida (AAAA-MM-DD)"
    )
    interesados: List[Interesado] = Field(default_factory=list)
    tareas: List[Tarea] = Field(default_factory=list)
    hitos: List[Hito] = Field(default_factory=list)
    riesgos: List[Riesgo] = Field(default_factory=list)
    informacion_faltante: List[str] = Field(
        default_factory=list,
        description="Datos importantes que NO aparecen en las fuentes y que un PMO debería solicitar",
    )
