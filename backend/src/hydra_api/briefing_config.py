"""HYDRA API — Briefing module constants.

All constants are module-level and read-only.
No Settings, no environment reads, no import-time side effects.
"""

from __future__ import annotations

# Title used in briefing markdown output.
BRIEFING_TITLE: str = "Briefing de inteligencia narrativa"

# Mandatory limitation text that must appear in every briefing,
# stating that the analysis is limited to the available corpus.
MANDATORY_CORPUS_LIMITATION: str = (
    "Limitación del corpus: el presente briefing se basa exclusivamente "
    "en los documentos disponibles en el corpus. Las conclusiones pueden "
    "no reflejar información externa no incluida en este corpus."
)

# Required sections that must appear in the final briefing markdown.
REQUIRED_BRIEFING_SECTIONS: list[str] = [
    "Resumen ejecutivo",
    "Análisis narrativo",
    "Evaluación de evidencia",
    "Nivel de riesgo",
    "Limitaciones",
]

# Maximum character count for evidence snippets included in briefing output.
BRIEFING_EVIDENCE_SNIPPET_CHARS: int = 500
