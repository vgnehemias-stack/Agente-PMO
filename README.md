# Agente PMO

Agente que convierte **data no estructurada de planificación de proyectos** — notas de reunión, correos, hojas de cálculo desordenadas, actas en Word, PDFs — en un **plan de proyecto estructurado**: tareas con responsables, fechas y dependencias, hitos, riesgos e interesados.

## Qué hace

1. **Lee** tus fuentes: `.txt`, `.md`, `.eml`, `.csv`, `.xlsx`, `.docx`, `.pdf` (archivos sueltos o directorios completos).
2. **Extrae y consolida** la información con un modelo de IA, sin inventar datos: lo que no aparece en las fuentes queda marcado como faltante.
3. **Exporta** el plan a:
   - `plan.xlsx` — libro Excel con hojas Resumen, Tareas, Hitos, Riesgos e Interesados
   - `tareas.csv`, `hitos.csv`, `riesgos.csv`
   - `plan.json` — estructura completa para integrar con otros sistemas
   - `plan.md` — reporte legible con tablas por fase

## Instalación

Requiere Python 3.9+.

```bash
pip install -r requirements.txt
```

## Uso

### Con Claude (recomendado, proveedor de referencia)

Necesitas una API key de Anthropic ([console.anthropic.com](https://console.anthropic.com)):

```bash
export ANTHROPIC_API_KEY="tu-api-key"
python -m agente_pmo ejemplos/ -o salida/
```

### Con Ollama (gratis, 100% local)

Instala [Ollama](https://ollama.com), descarga un modelo y ejecuta:

```bash
ollama pull llama3.1
python -m agente_pmo ejemplos/ -o salida/ --proveedor ollama --modelo llama3.1
```

No requiere API key ni conexión a internet.

### Con cualquier servidor compatible con OpenAI

Sirve para LM Studio, Groq, llama.cpp server, etc.:

```bash
# LM Studio local
python -m agente_pmo ejemplos/ -o salida/ --proveedor openai \
  --base-url http://localhost:1234/v1 --modelo <nombre-del-modelo>

# Servicio remoto con API key
export OPENAI_API_KEY="tu-key"
python -m agente_pmo ejemplos/ -o salida/ --proveedor openai \
  --base-url https://api.groq.com/openai/v1 --modelo llama-3.3-70b-versatile
```

### Opciones

| Opción | Descripción | Default |
|---|---|---|
| `rutas` | Archivos y/o directorios con la data | (obligatorio) |
| `-o, --salida` | Directorio de resultados | `./salida` |
| `--proveedor` | `claude`, `ollama` u `openai` | `claude` |
| `--modelo` | Modelo a usar | `claude-opus-4-8` / `llama3.1` |
| `--base-url` | URL del servidor (ollama / openai-compatible) | según proveedor |
| `--formato` | Salidas: `xlsx,csv,json,md` (separadas por coma) | todas |
| `--contexto` | Contexto adicional para la extracción | — |

Ejemplo con varias fuentes y contexto:

```bash
python -m agente_pmo notas.txt acta.docx seguimiento.xlsx correo.eml \
  -o salida/ --contexto "Proyecto de migración de intranet, sponsor Carla"
```

## Cómo funciona

- La extracción usa **salidas estructuradas**: el modelo está obligado a devolver JSON que cumple el esquema del plan (Pydantic, en `agente_pmo/schemas.py`).
- Con Claude la validación es nativa (`messages.parse`). Con proveedores locales, si el JSON no valida, el agente reenvía los errores al modelo para que corrija (hasta 2 reintentos).
- Reglas clave del prompt: no inventar fechas ni responsables, normalizar fechas a ISO, consolidar duplicados entre fuentes, registrar dependencias solo si son explícitas, y listar en `informacion_faltante` lo que un PMO debería solicitar.

> **Nota sobre calidad:** la fiabilidad de la extracción depende del modelo. Las pruebas de referencia del proyecto se hacen con Claude (`claude-opus-4-8`); los modelos locales pequeños pueden omitir detalles o requerir los reintentos de reparación.

## Estructura del proyecto

```
agente_pmo/
├── cli.py             # línea de comandos
├── lectores.py        # txt/md/csv/xlsx/docx/pdf → texto
├── schemas.py         # esquema Pydantic del plan
├── extractor.py       # prompt + validación + reparación
├── exportadores.py    # xlsx / csv / json / md
└── proveedores/
    ├── claude.py      # Anthropic (referencia)
    ├── ollama.py      # Ollama local (gratis)
    └── openai_compat.py  # cualquier endpoint estilo OpenAI
```
