"""aefm_utils.py - shared constants and writers for AncientEgyptianFuneraryMonuments.

No generator in this repository reads the clock. Dates come from RELEASE or from the
source data, so that a rebuild changes a file exactly when data or model changed.
"""
import hashlib
import json
from pathlib import Path

RELEASE = "0.1.0"
RELEASE_DATE = "2026-11-04"

REPO = Path(__file__).resolve().parent.parent
RAW = REPO / "data" / "raw"
CURATED = REPO / "data" / "curated"
DIST = REPO / "dist"
ONTOLOGY = DIST / "ontology"
TABLES = DIST / "tables"
REPORTS = DIST / "reports"
VISUALS = REPO / "visuals"

# Proposed namespace; the w3id.org entry still has to be requested (PRIMER.md A4).
AEFM = "https://w3id.org/aefm/"

OWL_SOURCE = RAW / "furnishing_funerary_monument_thebes_element_classes.owl"


def ensure_dirs():
    for d in (ONTOLOGY, TABLES, REPORTS):
        d.mkdir(parents=True, exist_ok=True)


def write_text(path, text):
    """UTF-8, LF line endings, exactly one trailing newline."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip("\n") + "\n", encoding="utf-8", newline="\n")


def write_json(path, obj):
    write_text(path, json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False))


def write_turtle(graph, path):
    """Serialise a graph without blank nodes; subjects come out sorted."""
    if any(True for s in graph.subjects() if s.__class__.__name__ == "BNode"):
        raise ValueError(f"{path}: blank nodes break byte-stable output; skolemise them")
    write_text(path, graph.serialize(format="turtle"))


def content_fingerprint(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:12]
