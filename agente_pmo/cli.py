"""Interfaz de línea de comandos del Agente PMO."""

import argparse
import sys
from pathlib import Path

from .exportadores import FORMATOS, exportar
from .extractor import ErrorExtraccion, extraer_plan
from .lectores import ErrorLectura, recolectar_fuentes
from .proveedores import PROVEEDORES, ErrorProveedor, crear_proveedor


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agente_pmo",
        description=(
            "Agente PMO: convierte data no estructurada de planificación "
            "(notas, correos, Excel, Word, PDF) en un plan de proyecto "
            "estructurado (Excel, CSV, JSON, Markdown)."
        ),
    )
    parser.add_argument(
        "rutas",
        nargs="+",
        help="Archivos o directorios con la data de planificación",
    )
    parser.add_argument(
        "-o",
        "--salida",
        default="salida",
        help="Directorio donde se generan los resultados (default: ./salida)",
    )
    parser.add_argument(
        "--proveedor",
        choices=PROVEEDORES,
        default="claude",
        help="Proveedor de IA a usar (default: claude)",
    )
    parser.add_argument(
        "--modelo",
        default=None,
        help=(
            "Modelo a usar. Defaults: claude-opus-4-8 (claude), llama3.1 (ollama), "
            "gemini-2.5-flash (gemini), llama-3.3-70b-versatile (groq); "
            "obligatorio con --proveedor openai"
        ),
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help=(
            "URL del servidor para ollama (default: http://localhost:11434) "
            "u openai-compatible (default: http://localhost:1234/v1)"
        ),
    )
    parser.add_argument(
        "--formato",
        default=",".join(FORMATOS),
        help=f"Formatos de salida separados por coma (default: {','.join(FORMATOS)})",
    )
    parser.add_argument(
        "--contexto",
        default=None,
        help="Contexto adicional para la extracción (ej. 'proyecto de migración SAP')",
    )
    return parser


def main(argv=None) -> int:
    args = construir_parser().parse_args(argv)

    formatos = [f.strip().lower() for f in args.formato.split(",") if f.strip()]
    invalidos = [f for f in formatos if f not in FORMATOS]
    if invalidos:
        print(
            f"Error: formato(s) no soportado(s): {', '.join(invalidos)}. "
            f"Opciones: {', '.join(FORMATOS)}",
            file=sys.stderr,
        )
        return 2

    try:
        fuentes = recolectar_fuentes(args.rutas)
        print(f"Fuentes leídas ({len(fuentes)}):")
        for nombre in fuentes:
            print(f"  - {nombre}")

        proveedor = crear_proveedor(
            args.proveedor, modelo=args.modelo, base_url=args.base_url
        )
        print(f"\nExtrayendo plan con {args.proveedor} ({proveedor.modelo})...")
        plan = extraer_plan(proveedor, fuentes, contexto=args.contexto)
    except (ErrorLectura, ErrorProveedor, ErrorExtraccion) as exc:
        print(f"\nError: {exc}", file=sys.stderr)
        return 1

    salida = Path(args.salida)
    generados = exportar(plan, salida, formatos)

    print(f"\nPlan extraído: {plan.nombre_proyecto}")
    print(
        f"  {len(plan.tareas)} tareas · {len(plan.hitos)} hitos · "
        f"{len(plan.riesgos)} riesgos · {len(plan.interesados)} interesados"
    )
    if plan.informacion_faltante:
        print("\nInformación faltante detectada:")
        for faltante in plan.informacion_faltante:
            print(f"  - {faltante}")
    print("\nArchivos generados:")
    for ruta in generados:
        print(f"  - {ruta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
