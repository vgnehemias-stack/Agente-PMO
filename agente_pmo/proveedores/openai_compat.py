"""Proveedor genérico compatible con la API de OpenAI.

Cubre servidores gratuitos o locales que exponen /chat/completions:
LM Studio, Groq, llama.cpp server, Ollama en modo compatible, etc.
Intenta salidas estructuradas (`response_format: json_schema`); si el
servidor no las soporta, degrada a `json_object` y luego a texto plano
(el extractor valida y repara en cualquier caso).
"""

import json
import os
import re
from typing import Any, Dict, List, Optional

import requests

from .base import ErrorProveedor, ProveedorLLM


def _extraer_json(texto: str) -> Dict[str, Any]:
    """Extrae el primer objeto JSON del texto (tolera cercos ```json ... ```)."""
    texto = texto.strip()
    cerco = re.search(r"```(?:json)?\s*(\{.*\})\s*```", texto, re.DOTALL)
    if cerco:
        texto = cerco.group(1)
    else:
        inicio = texto.find("{")
        fin = texto.rfind("}")
        if inicio != -1 and fin > inicio:
            texto = texto[inicio : fin + 1]
    return json.loads(texto)


class ProveedorOpenAICompat(ProveedorLLM):
    nombre = "openai"

    def __init__(self, modelo: str = None, base_url: str = None, api_key: str = None):
        if not modelo:
            raise ErrorProveedor(
                f"Con --proveedor {self.nombre} debes indicar el modelo con --modelo."
            )
        self.modelo = modelo
        self.base_url = (base_url or "http://localhost:1234/v1").rstrip("/")
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")

    def _post(self, payload: Dict[str, Any]) -> requests.Response:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        try:
            return requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=900,
            )
        except requests.ConnectionError as exc:
            raise ErrorProveedor(
                f"No se pudo conectar con el servidor en {self.base_url}. "
                "Verifica que esté corriendo y que --base-url sea correcto."
            ) from exc
        except requests.Timeout as exc:
            raise ErrorProveedor(
                "El servidor tardó demasiado en responder. Prueba con un modelo "
                "más pequeño o con menos archivos de entrada."
            ) from exc

    def generar_json(
        self,
        system: str,
        mensajes: List[Dict[str, str]],
        json_schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        intentos: List[Optional[Dict[str, Any]]] = [
            {
                "type": "json_schema",
                "json_schema": {"name": "plan_proyecto", "schema": json_schema},
            },
            {"type": "json_object"},
            None,  # sin response_format: el prompt exige JSON
        ]
        # Cuando el servidor no recibe el esquema vía response_format, el modelo
        # debe conocerlo por el prompt.
        system_con_schema = (
            system
            + "\n\nDevuelve ÚNICAMENTE un objeto JSON (sin texto adicional) que "
            "cumpla exactamente este JSON Schema:\n"
            + json.dumps(json_schema, ensure_ascii=False)
        )

        resp = None
        for response_format in intentos:
            usa_schema_nativo = (
                response_format is not None
                and response_format.get("type") == "json_schema"
            )
            payload = {
                "model": self.modelo,
                "messages": [
                    {
                        "role": "system",
                        "content": system if usa_schema_nativo else system_con_schema,
                    }
                ]
                + mensajes,
                "temperature": 0,
            }
            if response_format is not None:
                payload["response_format"] = response_format
            resp = self._post(payload)
            if resp.ok:
                break
            # Cualquier fallo (algunos servidores devuelven 4xx y otros 500 ante
            # un response_format no soportado) degrada al siguiente intento;
            # el último error se reporta si ninguno funciona.

        if resp is None or not resp.ok:
            detalle = resp.text[:500] if resp is not None else "sin respuesta"
            raise ErrorProveedor(
                f"Error del servidor compatible con OpenAI: {detalle}"
            )

        try:
            contenido = resp.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as exc:
            raise ErrorProveedor(
                f"Respuesta inesperada del servidor: {resp.text[:300]}"
            ) from exc

        try:
            return _extraer_json(contenido)
        except json.JSONDecodeError as exc:
            raise ErrorProveedor(
                f"El modelo no devolvió JSON válido: {contenido[:300]}"
            ) from exc


class ProveedorGemini(ProveedorOpenAICompat):
    """Google Gemini vía su endpoint compatible con OpenAI.

    Tiene nivel gratuito sin tarjeta: crea una API key en
    https://aistudio.google.com/apikey y expórtala como GEMINI_API_KEY.
    """

    nombre = "gemini"
    MODELO_POR_DEFECTO = "gemini-2.5-flash"

    def __init__(self, modelo: str = None, base_url: str = None):
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ErrorProveedor(
                "Falta la API key de Gemini. Es gratuita y no pide tarjeta: "
                "créala en https://aistudio.google.com/apikey y exporta "
                "GEMINI_API_KEY antes de ejecutar el agente."
            )
        super().__init__(
            modelo=modelo or self.MODELO_POR_DEFECTO,
            base_url=base_url
            or "https://generativelanguage.googleapis.com/v1beta/openai",
            api_key=api_key,
        )


class ProveedorGroq(ProveedorOpenAICompat):
    """Groq — inferencia rápida de modelos abiertos, con nivel gratuito.

    Crea una API key gratuita en https://console.groq.com/keys y expórtala
    como GROQ_API_KEY.
    """

    nombre = "groq"
    MODELO_POR_DEFECTO = "llama-3.3-70b-versatile"

    def __init__(self, modelo: str = None, base_url: str = None):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ErrorProveedor(
                "Falta la API key de Groq. Es gratuita: créala en "
                "https://console.groq.com/keys y exporta GROQ_API_KEY "
                "antes de ejecutar el agente."
            )
        super().__init__(
            modelo=modelo or self.MODELO_POR_DEFECTO,
            base_url=base_url or "https://api.groq.com/openai/v1",
            api_key=api_key,
        )
