"""step_docs.py - S4b: the documentation pages of the site (docs/*.md, Jekyll layout "default").

Pages show only what is settled and what the repository's own tables say. Internal notes (questions to
partners, open points) stay in PRIMER.md. Numbers are read from dist/tables/ and data/curated/.

    docs/index.md       overview, numbers, status
    docs/ontology.md    element classes, received files, provenance
    docs/grammar.md     stages, rules with evidence, space functions

The figure page docs/visuals/index.html is written by visuals/build.py.

    python py/step_docs.py
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aefm_utils as u  # noqa: E402
import site_kit  # noqa: E402

GH = "https://github.com/Research-Squirrel-Engineers/AncientEgyptianFuneraryMonuments/blob/main/"


def read(path):
    with open(path, encoding="utf-8", newline="") as h:
        return list(csv.DictReader(h))


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |" for r in rows]
    return "\n".join(out)


def front(title, intro):
    return f'---\nlayout: default\ntitle: "{title}"\nintro: "{intro}"\n---\n\n'


def rng(lo, hi):
    return f"{lo} to {hi}" if lo and hi else (lo or hi or "")


def build():
    inv = read(u.TABLES / "owl_inventory.csv")
    classes = read(u.TABLES / "element_classes.csv")
    stages, rules = read(u.CURATED / "grammar_stages.csv"), read(u.CURATED / "grammar_rules.csv")
    spaces = read(u.CURATED / "space_functions.csv")
    total = next(r["count"] for r in inv if r["kind"] == "classes")
    branches = [r for r in inv if r["kind"] == "branch"]
    props = [r for r in inv if r["kind"] == "annotation_property"]
    depth = max(int(r["depth"]) for r in classes)
    monuments = max(int(r["evidence_base"]) for r in rules if r["evidence_base"])

    stat = ('<div class="stat">'
            f'<div><b>{total}</b><span>element classes</span></div>'
            f'<div><b>{len(rules)}</b><span>shape rules in {len(stages)} stages</span></div>'
            f'<div><b>{len(spaces)}</b><span>space functions</span></div>'
            f'<div><b>{monuments}</b><span>monuments compared</span></div></div>')
    index = front("Ancient Egyptian funerary monuments: semantic model",
                  "Working state of the semantic model and Linked Open Data for Late Period rock-cut funerary monuments at Thebes (Dynasties 25 and 26), for the CHNT31 contribution.") + f"""
{stat}

> **Work in progress.** This site shows what exists. Figures mark planned parts with dashed frames. The namespace `https://w3id.org/aefm/` is proposed and does not resolve yet.

## What this is

The contribution moves from single monuments to a systematic comparison. The model gives stable names to the parts of a monument (rooms, openings, decoration) and to the rules by which monuments are built, so that statements about them can be counted, checked and linked.

## Pages

* [Element classes]({{{{ '/ontology.html' | relative_url }}}}): the {total} classes of the received element-class ontology and where they come from.
* [Shape grammar]({{{{ '/grammar.html' | relative_url }}}}): {len(rules)} rules with their evidence over the ten monuments, and the {len(spaces)} space functions with dimension ranges in cubits.
* [Slide figures]({{{{ '/visuals/' | relative_url }}}}): the figures for the talk, as PNG and SVG.

## Licence

Code MIT. Figures CC BY 4.0. Fonts: Fira Sans, SIL OFL 1.1. The licence of the data and the ontology is not yet decided.
"""
    ontology = front("Element classes", f"The element-class ontology as received: {total} classes below one root, converted to Turtle without changing the model.") + f"""
## What the file contains

{total} classes in one tree below `SpaceElement`, {depth} levels deep, in three branches:

{table(["Branch", "Classes"], [(b["name"], b["count"]) for b in branches])}

Each class carries an acronym. The file has no labels, definitions or properties beyond subclass relations and disjointness. Nothing was renamed in the conversion.

![How the received ontology and the new modules fit together]({{{{ '/visuals/img/03-owl-docking.png' | relative_url }}}})

## Received files and provenance

The element classes build on two ontologies by Georg Suter (TU Wien, Design Computing Group), described in Suter (2022), *Automation in Construction* 134, 104041. `space_layout.owl` is imported. `id_label.owl` is not imported; only the IRIs of its {len(props)} annotation properties are used. Neither file is part of this repository, and their licence is not yet known.

The original IRIs are kept as references. New resources are planned in their own namespace and will point to the old IRIs. A small stand-in, marked as reconstructed, declares only what the element classes use. It is meant for local checks and not for import by others.

## Files

* [`dist/ontology/aefm_elements_source.ttl`]({GH}dist/ontology/aefm_elements_source.ttl): the element classes as Turtle.
* [`dist/ontology/aefm_reference_stub.ttl`]({GH}dist/ontology/aefm_reference_stub.ttl): the reconstructed stand-in.
* [`dist/tables/element_classes.csv`]({GH}dist/tables/element_classes.csv): one row per class.
* [`dist/reports/owl_report.txt`]({GH}dist/reports/owl_report.txt): findings about the source.
"""
    stage_rows = [(s["stage"], s["title"], sum(1 for r in rules if r["stage"] == s["stage"])) for s in stages]
    rule_rows = [(r["rule"], r["stage"], r["title"], f"{r['evidence_count']}/{r['evidence_base']}" if r["evidence_count"] else "not given") for r in rules]
    space_rows = [(s["name"], s["code"], rng(s["length_min"], s["length_max"]),
                   rng(s["width_min"], s["width_max"]) or (("diameter " + rng(s["diameter_min"], s["diameter_max"])) if s["diameter_min"] else ""),
                   rng(s["angle_min"], s["angle_max"])) for s in spaces]
    grammar = front("Shape grammar", f"{len(rules)} rules in {len(stages)} stages, transcribed from Wutte and Duarte (2021), with the space functions they refer to.") + f"""
## Stages

{table(["Stage", "Title", "Rules"], stage_rows)}

![Shape grammar: rules in five stages, with evidence]({{{{ '/visuals/img/06-shape-grammar.png' | relative_url }}}})

## Rules and evidence

The evidence value is printed in the source as e = n/10 over the ten monuments. It is kept as given. The plan is to record the rule applications per monument and recount the values from them. Rules without a value in the source are marked as such.

{table(["Rule", "Stage", "Title", "Evidence"], rule_rows)}

## Space functions

Dimensions are in cubits (written c in the source); the length of the cubit in metres is not yet stated. Empty cells are empty in the source.

{table(["Space function", "Code", "Length (c)", "Width (c)", "Angle (degrees)"], space_rows)}

![Space functions with dimension ranges]({{{{ '/visuals/img/07-space-functions.png' | relative_url }}}})
"""
    return {"index.md": index, "ontology.md": ontology, "grammar.md": grammar}


def main():
    site_kit.write_assets()
    pages = build()
    for name, text in pages.items():
        site_kit.write_text(site_kit.DOCS / name, text.rstrip("\n") + "\n")
    print(f"docs: {len(pages)} pages, assets and layout")


if __name__ == "__main__":
    main()
