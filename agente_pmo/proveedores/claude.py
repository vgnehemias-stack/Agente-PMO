"""Proveedor Claude (Anthropic) — proveedor de referencia del agente.

Usa salidas estructuradas nativas (`client.messages.parse`), por lo que el
JSON devuelto ya viene validado contra el esquema.
"""

from typing import Any, Dict, List

import anthropic

from ..schemas import PlanProyecto
from .base import ErrorProveedor, ProveedorLLM

MODELO_POR_DEFECTO = "claude-opus-4-8"


class ProveedorClaude(ProveedorLLM):
    nombre = "claude"

    def __init__(self, modelo: str = None):
        self.modelo = modelo or MODELO_POR_DEFECTO
        # La API key se resuelve desde el entorno (ANTHROPIC_API_KEY).
        self.client = anthropic.Anthropic()

    def generar_json(
        self,
        system: str,
        mensajes: List[Dict[str, str]],
        json_schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        try:
            response = self.client.messages.parse(
                model=self.modelo,
                max_tokens=16000,
                thinking={"type": "adaptive"},
                system=system,
                messages=mensajes,
                output_format=PlanProyecto,
            )
        except TypeError as exc:
            # El SDK lanza TypeError si no encuentra ninguna credencial.
            if "authentication" in str(exc).lower():
                raise ErrorProveedor(
                    "No se encontró credencial de Anthropic. Exporta la variable "
                    "de entorno ANTHROPIC_API_KEY antes de ejecutar el agente."
                ) from exc
            raise
        except anthropic.AuthenticationError as exc:
            raise ErrorProveedor(
                "API key de Anthropic inválida o ausente. Exporta la variable "
                "de entorno ANTHROPIC_API_KEY antes de ejecutar el agente."
            ) from exc
        except anthropic.RateLimitError as exc:
            raise ErrorProveedor(
                "Límite de velocidad de la API de Anthropic alcanzado. "
                "Espera unos minutos y vuelve a intentar."
            ) from exc
        except anthropic.APIStatusError as exc:
            raise ErrorProveedor(
                f"Error de la API de Anthropic ({exc.status_code}): {exc.message}"
            ) from exc
        except anthropic.APIConnectionError as exc:
            raise ErrorProveedor(
                "No se pudo conectar con la API de Anthropic. Revisa tu conexión a internet."
            ) from exc

        if response.stop_reason == "refusal":
            raise ErrorProveedor(
                "El modelo rechazó procesar el contenido por motivos de seguridad."
            )
        if response.stop_reason == "max_tokens":
            raise ErrorProveedor(
                "La respuesta excedió el límite de tokens; el plan quedó incompleto. "
                "Divide las fuentes en menos archivos por ejecución."
            )
        if response.parsed_output is None:
            raise ErrorProveedor("El modelo no devolvió un plan estructurado válido.")

        return response.parsed_output.model_dump(mode="json")
