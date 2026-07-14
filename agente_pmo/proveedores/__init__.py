"""Registro de proveedores LLM disponibles."""

from .base import ErrorProveedor, ProveedorLLM

PROVEEDORES = ("claude", "ollama", "openai")


def crear_proveedor(
    nombre: str,
    modelo: str = None,
    base_url: str = None,
) -> ProveedorLLM:
    """Crea el proveedor pedido. Importa perezosamente para que un proveedor
    no instalado (ej. sin SDK de anthropic) no rompa a los demás."""
    if nombre == "claude":
        from .claude import ProveedorClaude

        return ProveedorClaude(modelo=modelo)
    if nombre == "ollama":
        from .ollama import ProveedorOllama

        return ProveedorOllama(modelo=modelo, base_url=base_url)
    if nombre == "openai":
        from .openai_compat import ProveedorOpenAICompat

        return ProveedorOpenAICompat(modelo=modelo, base_url=base_url)
    raise ErrorProveedor(
        f"Proveedor desconocido: '{nombre}'. Opciones: {', '.join(PROVEEDORES)}"
    )
