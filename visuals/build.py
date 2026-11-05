#!/usr/bin/env python3
"""build.py - slide figures for the semantic-modelling section of the CHNT31 talk.

Figures in the *-visuals house pattern (1750x1000, Fira Sans, SVG plus PNG) and a caption
page, written to docs/visuals/ (GitHub Pages). Every number and label drawn here is read from the
repository's own tables (dist/tables/, data/curated/), never typed in by hand.

    python visuals/build.py

The numbering follows the figure plan in PRIMER.md (V01 to V10); only the figures whose
data exist are built.
"""
import csv
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import resvg_py
from PIL import ImageFont

VISUALS = Path(__file__).resolve().parent
REPO = VISUALS.parent
sys.path.insert(0, str(REPO / "py"))
import site_kit  # noqa: E402

SITE, IMG = REPO / "docs" / "visuals", REPO / "docs" / "visuals" / "img"
TABLES, CURATED = REPO / "dist" / "tables", REPO / "data" / "curated"

R, M = VISUALS / "fonts/FiraSans-Regular.ttf", VISUALS / "fonts/FiraSans-Medium.ttf"
W, H = 1750, 1000
# Semantic colour scheme of the Research Squirrel Engineers figures
INST = ("#e2e8f0", "#000000", "#000000")
REAL = ("#166534", "#000000", "#ffffff")
CLS = ("#9a3412", "#000000", "#ffffff")
TERM = ("#4c1d95", "#000000", "#ffffff")
OWL = ("#ffffff", "#000000", "#000000")
PROP = ("#fbbf24", "#000000", "#000000")
DARK, MUTED, LINE = "#1f1f1d", "#55544f", "#55544f"


def tw(s, size, med=False):
    # BASIC layout: raqm is not on every machine, and a width that differs between
    # Windows and Linux would show up as a diff in every figure.
    font = ImageFont.truetype(str(M if med else R), 100, layout_engine=ImageFont.Layout.BASIC)
    return round(font.getlength(s) * size / 100, 1)


def wrap(text, size, maxw, med=False, maxlines=3):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if tw(trial, size, med) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur); cur = word
    lines.append(cur)
    if len(lines) > maxlines or any(tw(l, size, med) > maxw for l in lines):
        raise ValueError(f"does not fit in {maxlines} lines of {maxw}px: {text}")
    return lines


class Fig:
    def __init__(s, name, title):
        s.name = name
        s.o = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img"><title>{escape(title)}</title>',
               f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
               f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M1 1L9 5L1 9" fill="none" stroke="{LINE}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>']

    def text(s, x, y, t, size=22, med=False, color=DARK, anchor="middle", maxw=None):
        if maxw and tw(t, size, med) > maxw:
            raise ValueError(f"{s.name}: too wide ({tw(t, size, med):.0f}>{maxw}): {t}")
        wt = ' font-weight="500"' if med else ""
        s.o.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" dominant-baseline="central" font-family="Fira Sans" font-size="{size}"{wt} fill="{color}">{escape(t)}</text>')

    def rect(s, x, y, w, h, fill, stroke="none", rx=0, sw=1, dash=False):
        ds = ' stroke-dasharray="7 5"' if dash else ""
        s.o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{ds}/>')

    def circle(s, x, y, r, fill, stroke="#000000", sw=1):
        s.o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def box(s, x, y, w, h, title, sub=None, st=INST, ts=23, ss=19, rx=6, dash=False):
        f, b, c = st
        ds = ' stroke-dasharray="8 6" stroke-width="2"' if dash else ' stroke-width="1"'
        s.o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{f}" stroke="{b}"{ds}/>')
        cx = x + w / 2
        if sub:
            s.text(cx, y + h / 2 - ts * .58, title, ts, True, c, maxw=w - 14)
            s.text(cx, y + h / 2 + ts * .66, sub, ss, False, c, maxw=w - 14)
        else:
            s.text(cx, y + h / 2, title, ts, True, c, maxw=w - 14)

    def line(s, x1, y1, x2, y2, m="a", dash=False, w=1.6, color=LINE):
        d = ' stroke-dasharray="7 6"' if dash else ""
        mk = f' marker-end="url(#{m})"' if m else ""
        s.o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{w}"{d}{mk}/>')

    def legend(s, y, items, x=None):
        sizes = [34 + tw(t, 19) + 34 for _, t in items]
        x = (W - sum(sizes)) / 2 if x is None else x
        for (st, t), sz in zip(items, sizes):
            s.rect(x, y - 11, 22, 22, st[0], "#000000", 3)
            s.text(x + 32, y, t, 19, color=MUTED, anchor="start")
            x += sz

    def caption(s, t):
        s.text(45, 978, t, 19, color=MUTED, anchor="start", maxw=W - 90)

    def save(s):
        IMG.mkdir(parents=True, exist_ok=True)
        p = IMG / f"{s.name}.svg"
        p.write_text("\n".join(s.o + ["</svg>"]) + "\n", encoding="utf-8", newline="\n")
        (IMG / f"{s.name}.png").write_bytes(resvg_py.svg_to_bytes(
            svg_path=str(p), background="#ffffff", skip_system_fonts=True, font_files=[str(R), str(M)], zoom=2.0))


def read(path):
    if not Path(path).exists():
        raise SystemExit(f"{path} is missing; run python main.py first (the figures read what the steps wrote)")
    with open(path, encoding="utf-8", newline="") as h:
        return list(csv.DictReader(h))


# ---------------------------------------------------------------- V04 element classes
def fig_element_classes():
    """The class tree: a superclass above, its subclasses indented below, joined by lines."""
    rows = read(TABLES / "element_classes.csv")
    if len(rows) != 105:
        raise SystemExit(f"element_classes.csv has {len(rows)} rows, expected 105")
    kids, info = {}, {}
    for r in rows:
        info[r["class"]] = r
        kids.setdefault(r["parent"], []).append(r["class"])
    for k in kids:
        kids[k].sort()
    f = Fig("04-element-classes", "The class tree of the 105 element classes")
    SIZE, CH, RH, IND, LW = 16, 24, 29, 18, 1.3
    colw, gap, x1 = 320, 17, 40
    colx = [x1 + i * (colw + gap) for i in range(5)]
    seen = []

    def chip(x, y, name, right):
        st = CLS if name in kids else OWL
        w = tw(name, SIZE, st is CLS) + 16
        if x + w > right:
            raise ValueError(f"{f.name}: {name} runs past its column ({x + w:.0f}>{right:.0f})")
        f.rect(x, y, w, CH, st[0], st[1], 4, 1)
        f.text(x + w / 2, y + CH / 2, name, SIZE, st is CLS, st[2])
        seen.append(name)

    def branch(children, trunk_x, trunk_y, x, y, right):
        """Draw `children` as chips at x, one per row from y, joined to a trunk."""
        last = None
        for k in children:
            cy = y + CH / 2
            f.line(trunk_x, cy, x - 2, cy, None, w=LW)
            y = tree(k, x, y, right)
            last = cy
        if last is not None:
            f.line(trunk_x, trunk_y, trunk_x, last, None, w=LW)
        return y

    def tree(name, x, y, right):
        chip(x, y, name, right)
        return branch(kids.get(name, []), x + 9, y + CH, x + IND, y + RH, right)

    def header(col, y, name, count_label):
        x = colx[col]
        f.rect(x, y, colw, 54, CLS[0], CLS[1], 6, 1)
        f.text(x + 12, y + 19, name, 21, True, CLS[2], "start", maxw=colw - 24)
        f.text(x + 12, y + 40, count_label, 15, False, "#ffffff", "start")
        seen.append(name)
        return x, y + 54

    def group(col, y, name, children=None, count_label=None):
        x, yb = header(col, y, name, count_label or (f"{info[name]['descendants']} subclasses" if kids.get(name) else "class"))
        ch = kids.get(name, []) if children is None else children
        return branch(ch, x + 14, yb, x + 14 + IND, yb + 10, x + colw)

    top = 118
    scene = kids["Scene"]
    part_a = [k for k in scene if k in ("GeometricPattern", "UnknownScene", "DailyLifeScene", "FuneraryScene", "God")]
    part_b = [k for k in scene if k in ("Offering", "Owner")]
    if sorted(part_a + part_b) != scene:
        raise ValueError(f"{f.name}: Scene has other children than the two column parts")
    f.rect(x1 - 10, 38, 4 * colw + 3 * gap + 14, 70, "#eceff3", "none", 10)
    f.text(x1 + 8, 73, "DecorationElement", 28, True, anchor="start")
    seen.append("DecorationElement")
    f.text(x1 + 4 * colw + 3 * gap - 8, 73, f"{info['DecorationElement']['descendants']} subclasses", 20, color=MUTED, anchor="end")
    f.rect(colx[4] - 10, 38, colw + 20, 70, "#eceff3", "none", 10)
    f.text(colx[4] + 8, 73, "Furnishing, Sculpture", 28, True, anchor="start", maxw=colw)
    ends = [group(0, top, "ArchitecturalDecoration")]
    y = group(1, top, "Text")
    ends.append(group(1, y + 14, "UnknownDecorationObject"))
    ends.append(group(2, top, "Scene", part_a, f"{info['Scene']['descendants']} subclasses"))
    ends.append(group(3, top, "Scene", part_b, "continued"))
    seen.remove("Scene")
    y = group(4, top, "FurnishingElement")
    ends.append(group(4, y + 14, "Sculpture"))
    if max(ends) > 925:
        raise ValueError(f"{f.name}: content ends at y={max(ends):.0f}, beyond 925")
    missing = set(info) - set(seen) - {"SpaceElement"}
    if missing or len(seen) != len(set(seen)):
        raise ValueError(f"{f.name}: classes not drawn exactly once: {sorted(missing)}")
    f.legend(950, [(CLS, "Class with subclasses"), (OWL, "Class without subclasses")], x=45)
    f.line(640, 950, 668, 950, None, w=LW); f.text(680, 950, "is a: a class hangs below its superclass", 19, color=MUTED, anchor="start")
    f.caption("The 105 classes of furnishing_funerary_monument_thebes_element_classes.owl under the imported SpaceElement; labels, definitions and properties are not in the file.")
    f.save()
    return "The element classes form one tree of 105 classes with no labels, no properties and no link to CIDOC CRM yet."


# ------------------------------------------------------------------ V06 shape grammar
def fig_shape_grammar():
    stages = read(CURATED / "grammar_stages.csv")
    rules = read(CURATED / "grammar_rules.csv")
    if len(rules) != 31 or len(stages) != 5:
        raise SystemExit(f"expected 31 rules in 5 stages, found {len(rules)} in {len(stages)}")
    f = Fig("06-shape-grammar", "The shape grammar as a graph of stages and rules")
    cw, gap, x0 = 322, 15, 40
    rh, rg, top = 52, 5, 136
    SIZE = 14
    for i, s in enumerate(stages):
        x = x0 + i * (cw + gap)
        mine = [r for r in rules if r["stage"] == s["stage"]]
        f.box(x, 40, cw, 76, f"Stage {s['stage']}", s["title"], TERM, 25, 18)
        if i:
            f.line(x - gap - 1, 78, x + 1, 78, "a")
        y = top
        for r in mine:
            has = bool(r["evidence_count"])
            f.rect(x, y, cw, rh, INST[0] if has else "#ffffff", "#000000", 6, 1 if has else 2, dash=not has)
            f.text(x + 24, y + rh / 2, "R" + r["rule"], 17, True, anchor="middle")
            lines = wrap(r["title"], SIZE, cw - 44 - 96)
            ly = y + rh / 2 - (len(lines) - 1) * 8
            for j, l in enumerate(lines):
                f.text(x + 46, ly + j * 16, l, SIZE, anchor="start")
            if has:
                n, d = int(r["evidence_count"]), int(r["evidence_base"])
                ex = x + cw - 86
                for k in range(d):
                    f.circle(ex + k * 7.4, y + 17, 3, "#000000" if k < n else "#ffffff")
                f.text(x + cw - 12, y + 37, f"e = {n}/{d}", 14, False, MUTED, "end")
            else:
                f.text(x + cw - 12, y + rh / 2, "no e given", 14, False, MUTED, "end")
            y += rh + rg
    allten = [r for r in rules if r["evidence_count"] and r["evidence_count"] == r["evidence_base"]]
    once = [r for r in rules if r["evidence_count"] == "1"]
    none = [r for r in rules if not r["evidence_count"]]
    f.legend(930, [(TERM, "Stage"), (INST, "Rule, an individual in the graph"), (OWL, "Rule without evidence value")], x=45)
    f.circle(1062, 930, 3, "#000000"); f.text(1074, 930, "applied in a monument", 19, color=MUTED, anchor="start")
    f.circle(1292, 930, 3, "#ffffff"); f.text(1304, 930, "not applied", 19, color=MUTED, anchor="start")
    f.caption(f"{len(rules)} rules in {len(stages)} stages; {len(allten)} rules occur in all ten monuments, {len(once)} in one monument only, {len(none)} (stage IV) carry no evidence value.")
    f.save()
    return "The shape grammar is data: 31 rules in five stages, each with the number of monuments (of ten) that apply it."


# ------------------------------------------------------------------ V07 space functions
def fig_space_functions():
    rows = read(CURATED / "space_functions.csv")
    if len(rows) != 23:
        raise SystemExit(f"expected 23 space functions, found {len(rows)}")
    f = Fig("07-space-functions", "Space functions of the shape grammar with their dimension ranges in cubits")
    lx, lw, lmax = 440, 560, 70.0
    wx, ww, wmax = 1050, 380, 30.0
    ax = 1470
    top, rh = 150, 31
    placeholder = {"nave component": ("", "= width of side nave"), "nave corner": ("no dimensions in the source", ""),
                   "ramp": ("unclear in the source: [67 c)", ""), "middle axis": ("", "[0 c, ] no upper bound"),
                   "side axis": ("", "[0 c, ] no upper bound")}

    def sx(v, x0, w, vmax):
        return x0 + float(v) / vmax * w

    for x0, w, vmax, step, head in ((lx, lw, lmax, 10, "Length in cubits"), (wx, ww, wmax, 5, "Width or diameter in cubits")):
        f.text(x0, 60, head, 24, True, anchor="start")
        for v in range(0, int(vmax) + 1, step):
            xx = sx(v, x0, w, vmax)
            f.line(xx, 108, xx, top + rh * len(rows), None, w=.8, color="#d8d6ce")
            f.text(xx, 98, str(v), 16, color=MUTED)
    f.text(ax, 60, "Angle", 24, True, anchor="start")
    f.text(40, 60, "Space function", 24, True, anchor="start")
    for i, r in enumerate(rows):
        y = top + i * rh
        cy = y + rh / 2
        if i % 2 == 0:
            f.rect(30, y, W - 60, rh, "#f6f6f3")
        f.text(46, cy, r["name"], 18, anchor="start", maxw=300)
        cw = tw(r["code"], 16, True) + 14
        f.rect(360, cy - 12, cw, 24, PROP[0], "#000000", 4, 1)
        f.text(360 + cw / 2, cy, r["code"], 16, True, "#000000")
        ph = placeholder.get(r["name"], ("", ""))
        # length
        if r["length_min"] and r["length_max"]:
            a, b = float(r["length_min"]), float(r["length_max"])
            f.rect(sx(a, lx, lw, lmax), cy - 7, max(sx(b, lx, lw, lmax) - sx(a, lx, lw, lmax), 3), 14, REAL[0], "#000000", 2, 1)
            f.text(sx(b, lx, lw, lmax) + 8, cy, f"{r['length_min']}–{r['length_max']}", 15, color=MUTED, anchor="start")
            if r["name"] == "staircase":
                f.text(sx(b, lx, lw, lmax) + 72, cy, "upper bound open", 14, color=MUTED, anchor="start")
        elif ph[0]:
            f.text(lx + 4, cy, ph[0], 15, color=MUTED, anchor="start")
        # width or diameter
        if r["width_min"] and r["width_max"]:
            a, b = float(r["width_min"]), float(r["width_max"])
            f.rect(sx(a, wx, ww, wmax), cy - 7, max(sx(b, wx, ww, wmax) - sx(a, wx, ww, wmax), 3), 14, TERM[0], "#000000", 2, 1)
            f.text(sx(b, wx, ww, wmax) + 8, cy, f"{r['width_min']}–{r['width_max']}", 15, color=MUTED, anchor="start")
        elif r["diameter_min"]:
            a, b = float(r["diameter_min"]), float(r["diameter_max"])
            f.rect(sx(a, wx, ww, wmax), cy - 7, sx(b, wx, ww, wmax) - sx(a, wx, ww, wmax), 14, "#ffffff", "#4c1d95", 2, 2)
            f.text(sx(b, wx, ww, wmax) + 8, cy, f"d {r['diameter_min']}–{r['diameter_max']}", 15, color=MUTED, anchor="start")
        elif ph[1]:
            f.text(wx + 4, cy, ph[1], 15, color=MUTED, anchor="start")
        if r["angle_min"]:
            f.text(ax, cy, f"α {r['angle_min']}–{r['angle_max']}°", 16, anchor="start")
    ey = top + rh * len(rows) + 28
    f.legend(ey, [(REAL, "Length range"), (TERM, "Width range"), (("#ffffff", "#4c1d95", "#000000"), "Diameter of a column")], x=45)
    f.caption("Table of space functions from the shape grammar, transcribed in data/curated/space_functions.csv; c is the cubit, its length in metres is not yet stated.")
    f.save()
    return "Every space function carries a range of lengths, widths and angles in cubits, which makes room types comparable across monuments."


# ---------------------------------------------------------------- V03 existing OWL and docking
def fig_owl_docking():
    inv = read(TABLES / "owl_inventory.csv")
    classes = read(TABLES / "element_classes.csv")
    rules, stages, spaces = (len(read(CURATED / n)) for n in ("grammar_rules.csv", "grammar_stages.csv", "space_functions.csv"))
    props = [r for r in inv if r["kind"] == "annotation_property"]
    branches = [r for r in inv if r["kind"] == "branch"]
    groups = [r["count"] for r in inv if r["kind"] == "disjoint_group"]
    total = next(r["count"] for r in inv if r["kind"] == "classes")
    f = Fig("03-owl-docking", "The received element-class ontology and the modules that dock onto it")
    lx, lw, mx, mw, rx, rw = 40, 540, 670, 520, 1280, 430

    for x, w, t in ((lx, lw, "Received: spacepatterns.com"), (mx, mw, "New: this repository"), (rx, rw, "Reference models")):
        f.text(x, 48, t, 26, True, anchor="start")

    # --- left, top: the two ontologies we cannot read
    f.rect(lx, 85, 260, 220, "#ffffff", "#000000", 6, 2, dash=True)
    f.text(lx + 130, 112, "space_layout.owl", 22, True, maxw=240)
    for i, t in enumerate(("imported by IRI", "root class SpaceElement", "file not available")):
        f.text(lx + 130, 150 + i * 27, t, 18, color=MUTED, maxw=240)
    f.box(lx + 30, 245, 200, 38, "SpaceElement", st=INST, ts=19)
    f.rect(lx + 280, 85, 260, 220, "#ffffff", "#000000", 6, 2, dash=True)
    f.text(lx + 410, 112, "id_label.owl", 22, True, maxw=240)
    for i, p in enumerate(props):
        yy = 142 + i * 23.5
        label = f"{p['name']}  {p['count']}"
        cw = tw(label, 16, True) + 18
        f.rect(lx + 410 - cw / 2, yy - 10, cw, 21, PROP[0], "#000000", 4, 1)
        f.text(lx + 410, yy, label, 16, True, "#000000")

    # --- left, middle: the element-class ontology
    f.box(lx, 345, lw, 90, "Element-class ontology", "furnishing_funerary_monument_thebes_element_classes.owl", st=CLS, ts=24, ss=17)
    bw = (lw - 20) / 3
    for i, b in enumerate(branches):
        x = lx + i * (bw + 10)
        f.line(lx + lw / 2, 435, x + bw / 2, 470, None, w=1.3)
        f.box(x, 470, bw, 72, b["name"], f"{b['count']} classes", st=CLS, ts=16, ss=17, rx=5)
    f.text(lx, 570, f"{total} classes in one tree; disjoint groups of {', '.join(groups)}", 17, color=MUTED, anchor="start", maxw=lw)
    f.line(lx + 130, 345, lx + 130, 305, w=1.6)
    f.text(lx + 138, 326, "owl:imports", 17, color=MUTED, anchor="start")
    f.line(lx + 410, 345, lx + 410, 305, w=1.6, dash=True)
    f.text(lx + 418, 326, "uses its properties", 17, color=MUTED, anchor="start")

    # --- left, bottom: classes per depth, read from the class table
    depth = {}
    for r in classes:
        depth[int(r["depth"])] = depth.get(int(r["depth"]), 0) + 1
    f.text(lx, 620, "Classes per level below SpaceElement", 19, True, anchor="start")
    base, scale = 850, 150 / max(depth.values())
    for d in sorted(depth):
        x = lx + 14 + d * 88
        hgt = depth[d] * scale
        f.rect(x, base - hgt, 62, hgt, CLS[0], "#000000", 3, 1)
        f.text(x + 31, base - hgt - 14, str(depth[d]), 18, True)
        f.text(x + 31, base + 18, "root" if d == 0 else f"level {d}", 15, color=MUTED)

    # --- middle: our modules
    def mod(y, title, sub, st, planned, ts=22):
        f.box(mx, y, mw, 90, title, sub, st=st, ts=ts, ss=17, dash=planned)

    mod(150, "aefm_reference_stub.ttl", "root class and 7 annotation properties, reconstructed", OWL, False)
    mod(345, "aefm_elements_source.ttl", f"{total} classes, converted to Turtle, original IRIs kept", CLS, False)
    mod(455, "aefm-skos", "element classes as a concept scheme (SKOS twin)", TERM, True)
    mod(565, "aefm_grammar.ttl", f"{rules} rules, {stages} stages, {spaces} space functions as SKOS", TERM, False)
    mod(675, "aefm-core", "Monument, Room, Wall, Scene, Text, Measure", CLS, True)
    mod(785, "aefm-applications", "rule applications per monument, evidence by SPARQL", INST, True)
    f.line(lx + lw, 195, mx, 195, w=1.6, dash=True)
    f.text((lx + lw + mx) / 2, 176, "stands in", 16, color=MUTED)
    f.line(lx + lw, 390, mx, 390, w=1.6)
    f.text((lx + lw + mx) / 2, 371, "converts", 16, color=MUTED)
    f.line(mx + mw / 2, 435, mx + mw / 2, 455, w=1.6, dash=True)
    f.text(mx + mw / 2 + 12, 445, "exactMatch to the old IRIs", 15, color=MUTED, anchor="start")

    # --- right: provenance note and reference models
    f.rect(rx, 85, rw, 220, "#f6f6f3", "#d8d6ce", 6, 1)
    for i, (t, med) in enumerate((("Provenance", True), ("Georg Suter, TU Wien", False), ("Design Computing Group", False),
                                    ("Suter 2022, Automation in", False), ("Construction 134, 104041", False), ("Licence of the files: unknown", False))):
        f.text(rx + 18, 112 + i * 32, t, 21 if med else 19, med, anchor="start", maxw=rw - 30)
    f.box(rx, 345, rw, 90, "CIDOC CRM", "E55 Type, E36 Visual Item, E54 Dimension", st=OWL, ts=22, ss=17)
    f.box(rx, 455, rw, 200, "SKOS", "concept scheme, notation, exactMatch", st=OWL, ts=22, ss=17)
    f.box(rx, 675, rw, 90, "CRMba", "B1 Built Work, B2 Section, BP11", st=OWL, ts=22, ss=17, dash=True)
    f.box(rx, 785, rw, 90, "PROV-O", "a rule application is an activity", st=OWL, ts=22, ss=17, dash=True)
    for y, planned in ((390, True), (500, True), (610, False), (720, True), (830, True)):
        src = {390: 390, 500: 500, 610: 610, 720: 720, 830: 830}[y]
        f.line(mx + mw, src, rx, y, w=1.6, dash=planned)

    f.legend(920, [(CLS, "Class"), (TERM, "Vocabulary"), (OWL, "Ontology or model"), (PROP, "Annotation property"), (INST, "Planned data")])
    f.text(W / 2, 950, "Solid frame and line: exists in this repository. Dashed: planned, reconstructed or file not available.", 17, color=MUTED, maxw=W - 90)
    f.caption("Inventory read from dist/tables/owl_inventory.csv and element_classes.csv. Numbers after the property names count their uses in the received file.")
    f.save()
    return "The received element-class ontology rests on two files we cannot read; the new modules convert it, keep its IRIs as references and dock onto SKOS, CIDOC CRM and CRMba."


CREDIT = "Figure CC BY 4.0. Numbers read from "
CREDITS = {
    "03-owl-docking": CREDIT + "dist/tables/owl_inventory.csv and element_classes.csv. The ontologies space_layout.owl and id_label.owl are by Georg Suter (TU Wien); licence not yet known.",
    "04-element-classes": CREDIT + "dist/tables/element_classes.csv, converted from the element-class ontology as received.",
    "06-shape-grammar": CREDIT + "data/curated/grammar_rules.csv, transcribed from the shape grammar of Wutte and Duarte (2021).",
    "07-space-functions": CREDIT + "data/curated/space_functions.csv; c is the cubit, its length in metres is not yet stated.",
}

FIGURES = [
    ("03-owl-docking", "V03", fig_owl_docking, "The received ontology and how the new modules dock onto it."),
    ("04-element-classes", "V04", fig_element_classes, "Element classes: 105 classes, one tree."),
    ("06-shape-grammar", "V06", fig_shape_grammar, "Shape grammar: 31 rules in five stages, with evidence."),
    ("07-space-functions", "V07", fig_space_functions, "Space functions with dimension ranges in cubits."),
]


def index(entries):
    """docs/visuals/index.html: the figure cards, grouped by what they show."""
    cards = {n: site_kit.fig_card(IMG, n, code, cap, cr) for n, code, cap, cr in entries}
    groups = [("Ontology", ["03-owl-docking", "04-element-classes"]), ("Shape grammar", ["06-shape-grammar", "07-space-functions"])]
    body = []
    for i, (title, names) in enumerate(groups, 1):
        body.append(f'<h2 class="step"><span class="n">{i}</span>{site_kit.esc(title)}</h2>')
        body += [cards[n] for n in names if n in cards]
    intro = ("Figures for the semantic-modelling part of the CHNT31 contribution. Every number and label is read from the "
             "repository's tables. Dashed frames in the figures mark what is planned or not available.")
    site_kit.write_assets()
    site_kit.write_text(SITE / "index.html", site_kit.page_static("index.html", "Slide figures", intro, "\n".join(body)))


def main():
    entries = []
    for name, code, fn, cap in FIGURES:
        fn()
        entries.append((name, code, cap, CREDITS[name]))
        print(f"{code} {name}")
    index(entries)


if __name__ == "__main__":
    main()
