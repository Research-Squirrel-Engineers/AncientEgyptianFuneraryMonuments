"""step_grammar.py - S3: shape grammar and space functions as Linked Data.

Reads the curated transcriptions of the shape grammar (Wutte and Duarte 2021) and
its table of space functions

    data/curated/grammar_stages.csv
    data/curated/grammar_rules.csv
    data/curated/space_functions.csv

and writes

    dist/ontology/aefm_grammar.ttl       stages and rules as individuals, SKOS scheme of space functions
    dist/reports/grammar_report.txt      what was checked and what the source leaves open

The evidence values e = n/10 are kept as given. Once the rule applications per
monument exist as data, they are counted from the graph and compared with these.

    python py/step_grammar.py
"""
import csv
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aefm_utils as u  # noqa: E402
from rdflib import Graph, Literal, Namespace, URIRef  # noqa: E402
from rdflib.namespace import OWL, RDF, RDFS, SKOS, XSD  # noqa: E402

G = Namespace(u.AEFM + "grammar/")
V = Namespace(u.AEFM + "vocab/")
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
STAGE_RANGES = {"I": (1, 4), "II": (5, 17), "III": (18, 25), "IV": (26, 29), "V": (30, 31)}


def read(name):
    with open(u.CURATED / name, encoding="utf-8", newline="") as h:
        return list(csv.DictReader(h))


def slug(text):
    return "_".join(text.lower().split())


def dec(x):
    return Literal(Decimal(x), datatype=XSD.decimal)


def check(stages, rules, spaces):
    """Return findings; raise on anything that makes the data inconsistent."""
    problems, notes = [], []
    if [int(r["rule"]) for r in rules] != list(range(1, 32)):
        problems.append("rules are not numbered 1..31 in order")
    known = {s["stage"] for s in stages}
    for r in rules:
        lo, hi = STAGE_RANGES[r["stage"]]
        if r["stage"] not in known or not lo <= int(r["rule"]) <= hi:
            problems.append(f"rule {r['rule']} is filed under stage {r['stage']}")
        n, d = r["evidence_count"], r["evidence_base"]
        if (n == "") != (d == ""):
            problems.append(f"rule {r['rule']}: evidence is half given")
        if n and not (0 <= int(n) <= int(d)):
            problems.append(f"rule {r['rule']}: evidence {n}/{d} out of range")
    for s in spaces:
        for a, b in (("length_min", "length_max"), ("width_min", "width_max"), ("diameter_min", "diameter_max"), ("angle_min", "angle_max")):
            if s[a] and s[b] and Decimal(s[a]) > Decimal(s[b]):
                problems.append(f"{s['name']}: {a} > {b}")
    if problems:
        raise SystemExit("grammar data inconsistent:\n  " + "\n  ".join(problems))
    codes = Counter(s["code"] for s in spaces)
    notes.append("codes used more than once: " + (", ".join(f"{c} ({', '.join(s['name'] for s in spaces if s['code'] == c)})" for c, n in codes.items() if n > 1) or "none"))
    notes.append("rules without evidence value: " + ", ".join(r["rule"] for r in rules if not r["evidence_count"]))
    bases = {r["evidence_base"] for r in rules if r["evidence_base"]}
    notes.append(f"evidence base (monuments): {', '.join(sorted(bases))}")
    return notes


def build(stages, rules, spaces):
    g = Graph()
    g.bind("aefm-g", G); g.bind("aefm-v", V); g.bind("owl", OWL); g.bind("rdfs", RDFS)
    g.bind("skos", SKOS); g.bind("xsd", XSD); g.bind("crm", CRM)
    onto = URIRef(u.AEFM + "grammar")
    g.add((onto, RDF.type, OWL.Ontology))
    g.add((onto, RDFS.label, Literal("AEFM shape grammar and space functions", lang="en")))
    g.add((onto, OWL.versionInfo, Literal(u.RELEASE)))
    for c, lab in ((G.GrammarStage, "Grammar stage"), (G.ShapeRule, "Shape rule")):
        g.add((c, RDF.type, OWL.Class)); g.add((c, RDFS.label, Literal(lab, lang="en")))
    for p, rng, lab in ((G.inStage, G.GrammarStage, "in stage"), (G.nextStage, G.GrammarStage, "next stage")):
        g.add((p, RDF.type, OWL.ObjectProperty)); g.add((p, RDFS.range, rng)); g.add((p, RDFS.label, Literal(lab, lang="en")))
    for p, lab in ((G.stageNumber, "stage number"), (G.ruleNumber, "rule number"),
                   (G.evidenceCount, "evidence count"), (G.evidenceBase, "evidence base")):
        g.add((p, RDF.type, OWL.DatatypeProperty)); g.add((p, RDFS.label, Literal(lab, lang="en")))
    g.add((G.evidenceCount, RDFS.comment, Literal("Number of monuments in which the rule is applied, as printed in the source (e = n/10).", lang="en")))

    ordered = sorted(stages, key=lambda s: int(s["number"]))
    for i, s in enumerate(ordered):
        iri = G["stage/" + s["stage"]]
        g.add((iri, RDF.type, G.GrammarStage)); g.add((iri, RDFS.label, Literal(s["title"], lang="en")))
        g.add((iri, SKOS.notation, Literal(s["stage"]))); g.add((iri, G.stageNumber, Literal(int(s["number"]), datatype=XSD.integer)))
        if i + 1 < len(ordered):
            g.add((iri, G.nextStage, G["stage/" + ordered[i + 1]["stage"]]))
    for r in rules:
        iri = G["rule/R%02d" % int(r["rule"])]
        g.add((iri, RDF.type, G.ShapeRule)); g.add((iri, RDFS.label, Literal(r["title"], lang="en")))
        g.add((iri, G.ruleNumber, Literal(int(r["rule"]), datatype=XSD.integer)))
        g.add((iri, G.inStage, G["stage/" + r["stage"]]))
        if r["evidence_count"]:
            g.add((iri, G.evidenceCount, Literal(int(r["evidence_count"]), datatype=XSD.integer)))
            g.add((iri, G.evidenceBase, Literal(int(r["evidence_base"]), datatype=XSD.integer)))

    scheme = V.spaceFunction
    g.add((scheme, RDF.type, SKOS.ConceptScheme))
    g.add((scheme, SKOS.prefLabel, Literal("Space functions of Late Period funerary monuments", lang="en")))
    cubit = URIRef(u.AEFM + "unit/cubit")
    g.add((cubit, RDF.type, CRM.E58_Measurement_Unit)); g.add((cubit, RDFS.label, Literal("cubit", lang="en")))
    g.add((cubit, RDFS.comment, Literal("Written c in the source. Its length in metres is not yet stated.", lang="en")))
    props = {"length_min": "lengthMin", "length_max": "lengthMax", "width_min": "widthMin", "width_max": "widthMax",
             "diameter_min": "diameterMin", "diameter_max": "diameterMax", "angle_min": "angleMin", "angle_max": "angleMax"}
    for s in spaces:
        iri = V["spaceFunction/" + slug(s["name"])]
        g.add((iri, RDF.type, SKOS.Concept)); g.add((iri, SKOS.inScheme, scheme)); g.add((iri, SKOS.topConceptOf, scheme))
        g.add((iri, SKOS.prefLabel, Literal(s["name"], lang="en"))); g.add((iri, SKOS.notation, Literal(s["code"])))
        if any(s[k] for k in props):
            g.add((iri, V.measuredIn, cubit))
        for col, p in props.items():
            if s[col]:
                g.add((iri, V[p], dec(s[col])))
        if s["angle_symbol"]:
            g.add((iri, V.angleSymbol, Literal(s["angle_symbol"])))
        if s["note"]:
            g.add((iri, SKOS.note, Literal(s["note"], lang="en")))
    return g


def main():
    u.ensure_dirs()
    stages, rules, spaces = read("grammar_stages.csv"), read("grammar_rules.csv"), read("space_functions.csv")
    notes = check(stages, rules, spaces)
    g = build(stages, rules, spaces)
    u.write_turtle(g, u.ONTOLOGY / "aefm_grammar.ttl")
    per_stage = Counter(r["stage"] for r in rules)
    lines = ["Shape grammar and space functions: findings", "=" * 43, "",
             f"stages {len(stages)}, rules {len(rules)}, space functions {len(spaces)}, triples {len(g)}", "",
             "rules per stage: " + ", ".join(f"{s} {per_stage[s]}" for s in sorted(per_stage, key=lambda k: STAGE_RANGES[k][0])), ""]
    lines += notes
    lines += ["", "open in the source:"]
    lines += [f"  {s['name']} ({s['code']}): {s['note']}" for s in spaces if s["note"]]
    u.write_text(u.REPORTS / "grammar_report.txt", "\n".join(lines))
    print(f"grammar: {len(rules)} rules in {len(stages)} stages, {len(spaces)} space functions, {len(g)} triples")


if __name__ == "__main__":
    main()
