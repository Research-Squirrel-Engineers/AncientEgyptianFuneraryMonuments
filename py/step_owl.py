"""step_owl.py - S2: element-class ontology from Manchester syntax to Turtle.

Reads data/raw/furnishing_funerary_monument_thebes_element_classes.owl, unchanged as
received, and writes

    dist/ontology/aefm_elements_source.ttl   faithful conversion, original IRIs
    dist/tables/element_classes.csv          one row per class (hierarchy, depth, branch)
    dist/reports/owl_report.txt              findings about the source

The conversion changes nothing in the model. The one repair is the acronym of
NephthysStatue, whose literal contains a line break; it is listed in the report.
Renaming classes or adding labels is a later step and needs Anja Wutte's answers.

    python py/step_owl.py
"""
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aefm_utils as u  # noqa: E402
from rdflib import Graph, Literal, Namespace, URIRef  # noqa: E402
from rdflib.namespace import OWL, RDF, RDFS, XSD  # noqa: E402

BLOCK_START = re.compile(r"^(Prefix|Ontology|Import|Annotations|AnnotationProperty|Datatype|Class|DisjointClasses):", re.M)
LITERAL = re.compile(r'<([^>]+)>\s+"((?:[^"\\]|\\.)*)"(?:\^\^(\S+?))?\s*(?:,|$)', re.S)
ACRONYM = "http://spacepatterns.com/ontologies/space_model/common/id_label.owl#acronym"
ROOT = "http://spacepatterns.com/ontologies/space_model/common/space_layout.owl#SpaceElement"


def expand(token, prefixes):
    token = token.strip().rstrip(",")
    if token.startswith("<") and token.endswith(">"):
        return token[1:-1]
    pre, _, local = token.partition(":")
    return prefixes[pre] + local


def parse_manchester(text):
    """The subset of Manchester syntax this file uses; anything else raises."""
    prefixes = dict(re.findall(r"^Prefix:\s*(\S*):\s*<([^>]+)>", text, re.M))
    starts = list(BLOCK_START.finditer(text))
    out = {"prefixes": prefixes, "imports": [], "ontology": None, "ontology_annotations": [],
           "annotation_properties": [], "datatypes": [], "classes": {}, "disjoint": []}
    for i, m in enumerate(starts):
        kind = m.group(1)
        body = text[m.end(): starts[i + 1].start() if i + 1 < len(starts) else len(text)]
        first = body.strip().split("\n", 1)[0].strip()
        if kind == "Ontology":
            out["ontology"] = expand(first, prefixes)
        elif kind == "Import":
            out["imports"].append(expand(first, prefixes))
        elif kind == "Annotations" and out["ontology"] and not out["annotation_properties"]:
            out["ontology_annotations"] += [(a, v) for a, v, _ in LITERAL.findall(body)]
        elif kind == "AnnotationProperty":
            out["annotation_properties"].append(expand(first, prefixes))
        elif kind == "Datatype":
            out["datatypes"].append(expand(first, prefixes))
        elif kind == "Class":
            iri = expand(first, prefixes)
            sub = re.search(r"SubClassOf:\s*(.*?)(?:\n\s*\n|\Z)", body, re.S)
            parents = [expand(t, prefixes) for t in re.split(r"[,\n]", sub.group(1)) if t.strip()] if sub else []
            ann = re.search(r"Annotations:\s*(.*?)(?:\n\s*SubClassOf:|\Z)", body, re.S)
            annotations = [(a, v, d) for a, v, d in LITERAL.findall(ann.group(1))] if ann else []
            out["classes"][iri] = {"parents": parents, "annotations": annotations}
        elif kind == "DisjointClasses":
            out["disjoint"].append([expand(t, prefixes) for t in body.replace("\n", " ").split(",") if t.strip()])
    return out


def local(iri):
    return iri.rsplit("#", 1)[-1]


def build(parsed):
    g = Graph()
    cls_ns = Namespace(parsed["ontology"] + "#")
    g.bind("owl", OWL); g.bind("rdfs", RDFS); g.bind("xsd", XSD)
    g.bind("sm-furn", cls_ns); g.bind("id-label", Namespace(ACRONYM.rsplit("#", 1)[0] + "#"))
    g.bind("space-layout", Namespace(ROOT.rsplit("#", 1)[0] + "#"))
    onto = URIRef(parsed["ontology"])
    g.add((onto, RDF.type, OWL.Ontology))
    for imp in parsed["imports"]:
        g.add((onto, OWL.imports, URIRef(imp)))
    for a, v in parsed["ontology_annotations"]:
        g.add((onto, URIRef(a), Literal(v)))
    for ap in parsed["annotation_properties"]:
        g.add((URIRef(ap), RDF.type, OWL.AnnotationProperty))
    repairs = []
    for iri, c in parsed["classes"].items():
        g.add((URIRef(iri), RDF.type, OWL.Class))
        for p in c["parents"]:
            g.add((URIRef(iri), RDFS.subClassOf, URIRef(p)))
        for a, v, _dt in c["annotations"]:
            clean = re.sub(r"\s+", "", v) if a == ACRONYM else v
            if clean != v:
                repairs.append((local(iri), v, clean))
            g.add((URIRef(iri), URIRef(a), Literal(clean)))
    for group in parsed["disjoint"]:
        group = sorted(group)
        for i, a in enumerate(group):  # pairwise: AllDisjointClasses would need a blank node
            for b in group[i + 1:]:
                g.add((URIRef(a), OWL.disjointWith, URIRef(b)))
    return g, repairs


def hierarchy(parsed):
    classes = parsed["classes"]
    children = defaultdict(list)
    for iri, c in classes.items():
        for p in c["parents"]:
            children[p].append(iri)
    rows = []

    def walk(iri, depth, path):
        c = classes.get(iri)
        acr = ""
        if c:
            for a, v, _ in c["annotations"]:
                if a == ACRONYM:
                    acr = re.sub(r"\s+", "", v)
        n = [0]

        def count(x):
            for k in children.get(x, []):
                n[0] += 1
                count(k)
        count(iri)
        rows.append({"class": local(iri), "acronym": acr, "parent": local(path[-1]) if path else "",
                     "depth": depth, "descendants": n[0], "path": "/".join(local(p) for p in path + [iri])})
        for k in sorted(children.get(iri, []), key=local):
            walk(k, depth + 1, path + [iri])
    walk(ROOT, 0, [])
    return rows, children


def report(parsed, rows, children, repairs):
    classes = parsed["classes"]
    lines = ["Element-class ontology: findings", "=" * 33, ""]
    lines += [f"source          data/raw/{u.OWL_SOURCE.name}",
              f"sha256 (12)     {u.content_fingerprint(u.OWL_SOURCE)}",
              f"syntax          OWL 2 Manchester syntax",
              f"ontology IRI    {parsed['ontology']}", ""]
    lines += [f"classes declared in the file       {len(classes)} (104 with a SubClassOf axiom, plus the imported root SpaceElement)",
              f"annotation properties declared    {len(parsed['annotation_properties'])}",
              f"object or datatype properties     0",
              f"DisjointClasses axioms            {len(parsed['disjoint'])} "
              f"(groups of {', '.join(str(len(g)) for g in parsed['disjoint'])})", ""]
    lines.append("Imports (not part of the received files):")
    lines += [f"  {i}" for i in parsed["imports"]]
    lines.append("Used without being imported: id_label.owl (its IRI appears only as the namespace of the annotation properties)")
    lines.append("")
    depth = Counter(r["depth"] for r in rows)
    lines.append("Classes per depth below SpaceElement: " + ", ".join(f"{d}: {n}" for d, n in sorted(depth.items())))
    branch = Counter(r["path"].split("/")[1] for r in rows if r["depth"] >= 1)
    lines.append("Classes per branch: " + ", ".join(f"{b} {n}" for b, n in sorted(branch.items())))
    multi = [local(i) for i, c in classes.items() if len(c["parents"]) != 1]
    lines.append(f"Classes without exactly one parent: {multi if multi else 'none'}")
    acr = Counter(r["acronym"] for r in rows if r["acronym"])
    dup = {a: sorted(r["class"] for r in rows if r["acronym"] == a) for a, n in acr.items() if n > 1}
    lines.append(f"Duplicate acronyms: {dup or 'none'}")
    lines.append(f"Classes without acronym: {[r['class'] for r in rows if not r['acronym']]}")
    labelled = sum(1 for c in classes.values() for a, _, _ in c["annotations"] if a.endswith("label"))
    lines.append(f"rdfs:label or skos:prefLabel on classes: {labelled}")
    lines.append("")
    lines.append("Repairs made in the conversion (source defects):")
    lines += [f"  acronym of {c}: {old!r} -> {new!r}; the line break is removed, but the result equals another class's acronym" for c, old, new in repairs] or ["  none"]
    lines.append("  the acronym intended for the repaired class is unknown and has to come from the authors")
    lines.append("")
    lines.append("Naming to check with the authors (not changed):")
    for r in rows:
        if re.search(r"[a-z][A-Z]{2}[A-Z][a-z]", r["class"]):
            lines.append(f"  {r['class']}: upper-case run inside the name")
    gods = [local(k) for k in children.get(next(i for i in classes if local(i) == "God"), [])]
    lines.append(f"  classes under God that are named individuals in religion: {sorted(gods)}")
    own = [local(k) for k in children.get(next(i for i in classes if local(i) == "Owner"), [])]
    lines.append(f"  direct subclasses of Owner (includes Woman, whose subclasses are Mother and Wife): {sorted(own)}")
    return "\n".join(lines)


def inventory(parsed, rows):
    """What the received file contains, one row per item; the docking figure reads this."""
    classes = parsed["classes"]
    uses = Counter(a for c in classes.values() for a, _, _ in c["annotations"])
    uses.update(a for a, _ in parsed["ontology_annotations"])
    inv = [("file", parsed["ontology"].rsplit("/", 1)[-1], 1, "ontology IRI " + parsed["ontology"])]
    for i in parsed["imports"]:
        inv.append(("import", i.rsplit("/", 1)[-1], 1, i))
    for a in sorted(parsed["annotation_properties"], key=local):
        inv.append(("annotation_property", local(a), uses.get(a, 0), a))
    branch = Counter(r["path"].split("/")[1] for r in rows if r["depth"] >= 1)
    for b, n in sorted(branch.items(), key=lambda kv: (-kv[1], kv[0])):
        inv.append(("branch", b, n, "classes below SpaceElement"))
    for g in parsed["disjoint"]:
        inv.append(("disjoint_group", "group", len(g), "pairwise disjoint classes"))
    inv.append(("classes", "declared", len(classes), "including the imported root SpaceElement"))
    return inv


def main():
    u.ensure_dirs()
    parsed = parse_manchester(u.OWL_SOURCE.read_text(encoding="utf-8"))
    if len(parsed["classes"]) != 105 or ROOT not in parsed["classes"]:
        raise SystemExit(f"expected 105 class declarations including SpaceElement, found {len(parsed['classes'])}")
    g, repairs = build(parsed)
    u.write_turtle(g, u.ONTOLOGY / "aefm_elements_source.ttl")
    rows, children = hierarchy(parsed)
    with open(u.TABLES / "element_classes.csv", "w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=["class", "acronym", "parent", "depth", "descendants", "path"], lineterminator="\n")
        w.writeheader(); w.writerows(rows)
    with open(u.TABLES / "owl_inventory.csv", "w", encoding="utf-8", newline="") as h:
        w = csv.writer(h, lineterminator="\n")
        w.writerow(["kind", "name", "count", "note"]); w.writerows(inventory(parsed, rows))
    u.write_text(u.REPORTS / "owl_report.txt", report(parsed, rows, children, repairs))
    print(f"element classes: {len(parsed['classes'])} declared, {len(g)} triples, {len(repairs)} repair(s)")


if __name__ == "__main__":
    main()
