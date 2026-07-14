"""Proveedor Ollama — modelos gratuitos ejecutados localmente.

Usa la API de chat de Ollama con el parámetro `format` (JSON Schema),
disponible desde Ollama 0.5, para forzar salida estructurada.
"""

import json
from typing import Any, Dict, List

import requests

from .base import ErrorProveedor, ProveedorLLM

URL_POR_DEFECTO = "http://localhost:11434"
MODELO_POR_DEFECTO = "llama3.1"


class ProveedorOllama(ProveedorLLM):
    nombre = "ollama"

    def __init__(self, modelo: str = None, base_url: str = None):
        self.modelo = modelo or MODELO_POR_DEFECTO
        self.base_url = (base_url or URL_POR_DEFECTO).rstrip("/")

    def generar_json(
        self,
        system: str,
        mensajes: List[Dict[str, str]],
        json_schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        payload = {
            "model": self.modelo,
            "messages": [{"role": "system", "content": system}] + mensajes,
            "format": json_schema,
            "stream": False,
            "options": {"temperature": 0},
        }
        try:
            # Timeout generoso: los modelos locales pueden tardar varios minutos.
            resp = requests.post(
                f"{self.base_url}/api/chat", json=payload, timeout=900
            )
        except requests.ConnectionError as exc:
            raise ErrorProveedor(
                f"No se pudo conectar con Ollama en {self.base_url}. "
                "¿Está corriendo? Inícialo con `ollama serve` y descarga el modelo "
                f"con `ollama pull {self.modelo}`."
            ) from exc
        except requests.Timeout as exc:
            raise ErrorProveedor(
                "Ollama tardó demasiado en responder. Prueba con un modelo más "
                "pequeño o con menos archivos de entrada."
            ) from exc

        if resp.status_code == 404:
            raise ErrorProveedor(
                f"El modelo '{self.modelo}' no está disponible en Ollama. "
                f"Descárgalo con `ollama pull {self.modelo}`."
            )
        if not resp.ok:
            raise ErrorProveedor(f"Error de Ollama ({resp.status_code}): {resp.text[:500]}")

        contenido = resp.json().get("message", {}).get("content", "")
        try:
            return json.loads(contenido)
        except json.JSONDecodeError as exc:
            raise ErrorProveedor(
                f"Ollama no devolvió JSON válido: {contenido[:300]}"
            ) from exc
