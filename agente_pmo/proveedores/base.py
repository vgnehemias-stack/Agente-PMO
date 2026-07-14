"""Interfaz común de proveedores LLM."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class ErrorProveedor(RuntimeError):
    """Error al comunicarse con un proveedor LLM, con mensaje accionable."""


class ProveedorLLM(ABC):
    """Un proveedor recibe una conversación y devuelve un dict con la forma
    del JSON Schema indicado. La validación final la hace el extractor."""

    nombre: str = "base"

    @abstractmethod
    def generar_json(
        self,
        system: str,
        mensajes: List[Dict[str, str]],
        json_schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Genera un dict que debería cumplir `json_schema`.

        `mensajes` es una lista [{"role": "user"|"assistant", "content": str}]
        para permitir el reintento de reparación con historial.
        """
        raise NotImplementedError
