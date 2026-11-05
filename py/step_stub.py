"""step_stub.py - S2b: a reconstructed stand-in for the two ontologies we cannot read.

The element-class ontology imports space_layout.owl and uses the annotation properties of
id_label.owl (G. Suter, TU Wien, spacepatterns.com). Neither file came with the data and the
site is closed to automated access. This step writes only what our own file demonstrably
uses of them:

    dist/ontology/aefm_reference_stub.ttl   root class and annotation properties, marked as reconstructed

Nothing here is a copy of the originals. The IRIs stay those of spacepatterns.com, so that the
element classes remain valid against the real files once they are available. The stub is
for local checks and is not to be imported by other ontologies.

    python py/step_stub.py
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aefm_utils as u  # noqa: E402
from rdflib import Graph, Literal, URIRef  # noqa: E402
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS  # noqa: E402

ROOT = "http://spacepatterns.com/ontologies/space_model/common/space_layout.owl"
IDLABEL = "http://spacepatterns.com/ontologies/space_model/common/id_label.owl"
NOTE = ("Reconstructed from its use in the element-class ontology; not the original definition. "
        "The original has to come from its author, Georg Suter (TU Wien).")


def main():
    u.ensure_dirs()
    with open(u.TABLES / "owl_inventory.csv", encoding="utf-8", newline="") as h:
        inv = list(csv.DictReader(h))
    g = Graph()
    g.bind("owl", OWL); g.bind("rdfs", RDFS); g.bind("dcterms", DCTERMS)
    stub = URIRef(u.AEFM + "reference-stub")
    g.add((stub, RDF.type, OWL.Ontology))
    g.add((stub, RDFS.label, Literal("Reconstructed stand-in for space_layout.owl and id_label.owl", lang="en")))
    g.add((stub, RDFS.comment, Literal("Declares only what the element-class ontology uses. Not for import.", lang="en")))
    g.add((stub, OWL.versionInfo, Literal(u.RELEASE)))
    root = URIRef(ROOT + "#SpaceElement")
    g.add((root, RDF.type, OWL.Class)); g.add((root, RDFS.isDefinedBy, URIRef(ROOT)))
    g.add((root, RDFS.comment, Literal(NOTE, lang="en")))
    props = [r["name"] for r in inv if r["kind"] == "annotation_property"]
    for name in props:
        p = URIRef(IDLABEL + "#" + name)
        g.add((p, RDF.type, OWL.AnnotationProperty)); g.add((p, RDFS.isDefinedBy, URIRef(IDLABEL)))
        g.add((p, RDFS.comment, Literal(NOTE, lang="en")))
    u.write_turtle(g, u.ONTOLOGY / "aefm_reference_stub.ttl")
    print(f"stub: 1 class, {len(props)} annotation properties, {len(g)} triples")


if __name__ == "__main__":
    main()
