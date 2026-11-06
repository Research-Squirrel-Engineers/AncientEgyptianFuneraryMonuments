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
    f.caption("Table of space functions from the shape grammar, transcribed in data/curated/space_functions.csv; c is the cubit (0.5 m).")
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


# ---------------------------------------------------------------- talk slides: V01, V02, V05
def _facts():
    inv = read(TABLES / "owl_inventory.csv")
    rules = read(CURATED / "grammar_rules.csv")
    spaces = {r["name"]: r for r in read(CURATED / "space_functions.csv")}
    classes = {r["class"] for r in read(TABLES / "element_classes.csv")}
    total = next(r["count"] for r in inv if r["kind"] == "classes")
    monuments = max(int(r["evidence_base"]) for r in rules if r["evidence_base"])
    return total, len(spaces), monuments, spaces, classes


def _chip(f, cx, y, label):
    cw = tw(label, 17, True) + 20
    f.rect(cx - cw / 2, y - 12, cw, 25, PROP[0], "#000000", 5, 1)
    f.text(cx, y, label, 17, True, "#000000")


def fig_monument_parts():
    total, n_spaces, monuments, spaces, classes = _facts()
    # Rooms as labelled on the plan of Harwa (TT37); each must be a space function of the grammar's table.
    rooms = [("courtyard", "courtyard"), ("vestibul", "vestibul"), ("niche entrance", "niche entrance"),
             ("pillared hall I", "pillared hall"), ("pillared hall II", "pillared hall"), ("sanctuary", "sanctuary"), ("corridor", "corridor")]
    for _, key in rooms:
        if key not in spaces:
            raise SystemExit(f"room label {key!r} is not a space function")
    tree = [("Text", 0, "Text"), ("FuneraryText", 1, "FuneraryText"), ("Scene", 0, "Scene"), ("DailyLifeScene", 1, "DailyLifeScene"),
            ("FuneraryScene", 1, "FuneraryScene"), ("Owner", 1, "Owner"), ("StandingMan", 2, "StandingMan"), ("SittingMan", 2, "SittingMan"),
            ("KneeingMan", 2, "KneeingMan")]
    for _, _, c in tree:
        if c not in classes:
            raise SystemExit(f"class {c!r} is not in the element-class ontology")
    f = Fig("01-monument-parts", "From a monument to its rooms and decoration, shown for Harwa")
    lx, lw, mx, mw, rx, rw = 40, 520, 620, 480, 1260, 450
    for x, t in ((lx, "Plan"), (mx, "Monument and rooms"), (rx, "Decoration")):
        f.text(x, 48, t, 26, True, anchor="start")
    # plan placeholder: the plan itself is placed on the slide, not drawn here
    f.rect(lx, 85, lw, 480, "#ffffff", "#000000", 6, 2, dash=True)
    for i, (t, sz, med, col) in enumerate((("Plan of Harwa (TT37)", 24, True, DARK), ("to be placed on the slide", 19, False, MUTED),
                                            ("digitised plan: Anja Wutte", 19, False, MUTED), ("site plans: Eigner 1984", 19, False, MUTED))):
        f.text(lx + lw / 2, 270 + i * 38, t, sz, med, col)
    f.text(lx, 600, "From the title block of the plan", 19, True, anchor="start")
    for i, t in enumerate(("25th Dynasty, Shabaka and Taharka", "Asasif North", "Chief Steward")):
        f.text(lx, 632 + i * 28, t, 18, color=MUTED, anchor="start")
    # monument and rooms
    f.box(mx, 85, mw, 90, "Harwa", "TT37, a funerary monument", st=REAL, ts=26, ss=19)
    f.line(mx + 400, 175, mx + 400, 205, w=1.6, dash=True)
    f.text(mx + 412, 190, "has part", 17, True, anchor="start")
    f.text(mx, 218, "Rooms, named as on the plan", 19, True, anchor="start")
    cw = (mw - 20) / 2
    for i, (label, key) in enumerate(rooms):
        x = mx + (i % 2) * (cw + 20)
        y = 245 + (i // 2) * 72
        f.box(x, y, cw, 58, label, spaces[key]["code"], st=TERM, ts=20, ss=17, dash=False)
    # decoration
    f.rect(rx - 14, 75, rw + 28, 600, "#f6f6f3", "#d8d6ce", 8, 1)
    ys = {"Text": 90, "FuneraryText": 160, "Scene": 255, "DailyLifeScene": 325, "FuneraryScene": 381, "Owner": 437,
          "StandingMan": 493, "SittingMan": 549, "KneeingMan": 605}
    for name, level, _ in tree:
        x = rx + level * 40
        h = 56 if level == 0 else 44
        f.box(x, ys[name], rw - level * 40, h, name, st=CLS, ts=21 if level == 0 else 19)
    for parent, kids, tx in (("Text", ["FuneraryText"], rx + 20), ("Scene", ["DailyLifeScene", "FuneraryScene", "Owner"], rx + 20),
                             ("Owner", ["StandingMan", "SittingMan", "KneeingMan"], rx + 60)):
        top = ys[parent] + (56 if parent in ("Text", "Scene") else 44)
        last = ys[kids[-1]] + 22
        f.line(tx, top, tx, last, None, w=1.3)
        for k in kids:
            f.line(tx, ys[k] + 22, tx + 20, ys[k] + 22, None, w=1.3)
    f.line(mx + mw, 383, rx - 14, 383, w=1.6, dash=True)
    f.text((mx + mw + rx - 14) / 2, 362, "has decoration", 17, True)
    # proposed mapping
    f.text(lx, 725, "Proposed mapping to CIDOC CRM and CRMba (planned)", 19, True, anchor="start")
    bw = (1670 - 3 * 20) / 4
    for i, (t, s) in enumerate((("Monument", "CRMba B1 Built Work"), ("Room", "B2 Morphological Building Section"),
                                ("Scene", "CIDOC CRM E36 Visual Item"), ("Text", "E33 Linguistic Object"))):
        f.box(lx + i * (bw + 20), 755, bw, 84, t, s, st=OWL, ts=22, ss=17, dash=True)
    f.legend(905, [(REAL, "Monument"), (TERM, "Space function"), (CLS, "Class"), (OWL, "Planned mapping")])
    f.text(W / 2, 940, "Dashed: planned. The relations have no property in the model yet.", 17, color=MUTED, maxw=W - 90)
    f.caption("Room labels from the plan of Harwa; classes from the element-class ontology; space-function codes from the grammar's table.")
    f.save()


def fig_data_situation():
    total, n_spaces, monuments, spaces, classes = _facts()
    f = Fig("02-data-situation", "Research data on Egyptian funerary monuments today and with a shared model")
    f.text(40, 48, "Today", 26, True, anchor="start")
    f.text(880, 48, "With a shared model", 26, True, anchor="start")
    srcs = ["Analogue plans", "Digitised plans", "Space model (BIM)", "Decoration records", "Publications"]
    scatter = [(40, 100), (300, 150), (80, 260), (330, 340), (170, 450)]
    for t, (x, y) in zip(srcs, scatter):
        f.box(x, y, 240, 64, t, st=INST, ts=21, dash=True)
    f.line(830, 90, 830, 560, None, dash=True, w=1.3, color="#d8d6ce")
    f.text(40, 600, "Egyptian research data today", 21, True, anchor="start")
    for i, t in enumerate(("No unified system", "Little connection to shareable data", "Terms differ between authors")):
        f.text(40, 640 + i * 34, t, 20, color=MUTED, anchor="start")
    sx, sw_, mx, mw, ox, ow = 880, 220, 1170, 230, 1470, 240
    ys = [100, 186, 272, 358, 444]
    for t, y in zip(srcs, ys):
        f.box(sx, y, sw_, 64, t, st=INST, ts=20)
        f.line(sx + sw_, y + 32, mx, y + 32, w=1.6, dash=True)
    f.box(mx, 100, mw, 408, "Shared model", "stable identifiers", st=OWL, ts=24, ss=19)
    for t, y, dash in (("Wikidata", 130, True), ("Getty AAT", 260, True), ("Open files", 390, False)):
        sub = {"Wikidata": "links, planned", "Getty AAT": "links, planned", "Open files": "Turtle and CSV"}[t]
        f.box(ox, y, ow, 70, t, sub, st=OWL, ts=21, ss=17, dash=dash)
        f.line(mx + mw, y + 35, ox, y + 35, w=1.6, dash=dash)
    for i, (n, t, st, dash) in enumerate(((total, "element classes", CLS, False), (n_spaces, "space functions", TERM, False),
                                          (monuments, "monuments, data planned", REAL, True))):
        bw = (830 - 40) / 3
        f.box(880 + i * (bw + 20), 560, bw, 84, str(n), t, st=st, ts=30, ss=17, dash=dash)
    f.text(880, 690, "Exists: element classes as Turtle, space functions as SKOS.", 19, color=MUTED, anchor="start")
    f.text(880, 722, "Planned: monument data, links, queries.", 19, color=MUTED, anchor="start")
    f.legend(905, [(INST, "Source"), (OWL, "Model or target"), (CLS, "Class"), (TERM, "Vocabulary"), (REAL, "Monument")])
    f.text(W / 2, 940, "Solid frame: exists. Dashed: planned, or not yet connected.", 17, color=MUTED, maxw=W - 90)
    f.caption("The sources are those named for Harwa and the ten monuments; the statements on the left are Anja Wutte's assessment.")
    f.save()


def fig_linking_plan():
    total, n_spaces, monuments, spaces, classes = _facts()
    f = Fig("05-linking-plan", "How identifiers of the model are meant to link to other sources")
    f.box(40, 85, 1670, 64, "https://w3id.org/aefm/", "proposed namespace, not yet registered", st=OWL, ts=22, ss=17, dash=True)
    rows = [((f"Element classes", f"{total} classes, original IRIs kept", CLS, False), "skos:exactMatch",
             ("spacepatterns.com IRIs", "reference only, the files are not available", OWL, True), False),
            (("Space functions", f"{n_spaces} concepts in a SKOS scheme", TERM, False), "skos:closeMatch",
             ("Getty AAT", "building terms", OWL, True), True),
            (("Monuments", f"{monuments}, data planned", REAL, True), "owl:sameAs",
             ("Wikidata", "monuments and their kinds", OWL, True), True)]
    for i, (a, rel, b, dash) in enumerate(rows):
        y = 200 + i * 150
        f.box(40, y, 520, 100, a[0], a[1], st=a[2], ts=26, ss=19, dash=a[3])
        f.line(560, y + 50, 1190, y + 50, w=1.6, dash=dash)
        _chip(f, 875, y + 24, rel)
        f.box(1190, y, 520, 100, b[0], b[1], st=b[2], ts=26, ss=19, dash=b[3])
    f.text(40, 700, "Exists: classes and space functions as Turtle. Planned: the links, the monument data, queries.", 19, color=MUTED, anchor="start")
    f.text(40, 734, "Not decided yet: the licence of the data.", 19, color=MUTED, anchor="start")
    f.legend(905, [(CLS, "Class"), (TERM, "Vocabulary"), (REAL, "Monument"), (OWL, "Target"), (PROP, "Relation (planned)")])
    f.text(W / 2, 940, "Solid frame: exists. Dashed: planned or not available. No vocabulary is prescribed by the subject experts; Wikidata and Getty AAT are the plan.", 17, color=MUTED, maxw=W - 90)
    f.caption("Match relations are proposals; owl:equivalentClass would be the stronger alternative for the old IRIs.")
    f.save()


def fig_ontology_contents():
    inv = read(TABLES / "owl_inventory.csv")
    rows = read(TABLES / "element_classes.csv")
    val = {(r["kind"], r["name"]): int(r["count"]) for r in inv if r["count"].lstrip("-").isdigit()}
    total = val[("classes", "declared")]
    labelled = val[("classes", "with label")]
    props = val[("classes", "object or datatype properties")]
    codes = val[("annotation_property", "acronym")]
    groups = [r["count"] for r in inv if r["kind"] == "disjoint_group"]
    depth = max(int(r["depth"]) for r in rows)
    f = Fig("08-ontology-contents", "What the received element-class ontology contains and what it does not yet contain")
    f.box(700, 85, 350, 70, "SpaceElement", "root class, from an imported file", st=OWL, ts=24, ss=17, dash=True)
    branches = [r for r in inv if r["kind"] == "branch"]
    colw, xs = 520, [40, 615, 1190]
    for x, b in zip(xs, branches):
        f.line(875, 155, x + colw / 2, 215, w=1.5)
        f.box(x, 215, colw, 84, b["name"], f"{b['count']} classes", st=CLS, ts=26, ss=19)
        kids = [r for r in rows if r["parent"] == b["name"]]
        kids.sort(key=lambda r: (-int(r["descendants"]), r["class"]))
        for i, k in enumerate(kids[:3]):
            n = int(k["descendants"])
            sub = f"{n} subclass" + ("es" if n != 1 else "") if n else "no subclasses"
            f.box(x + 20, 320 + i * 72, colw - 40, 60, k["class"], sub, st=CLS, ts=21, ss=16)
        more = len(kids) - 3
        note = f"{len(kids)} direct subclass" + ("es" if len(kids) != 1 else "") + (", the three largest shown" if more > 0 else "")
        f.text(x + 20, 320 + 3 * 72 + 4, note, 17, color=MUTED, anchor="start")
    lx, rx, pw = 40, 890, 820
    for x, title in ((lx, "The file contains"), (rx, "The file does not yet contain")):
        f.rect(x, 640, pw, 235, "#f6f6f3", "#d8d6ce", 8, 1)
        f.text(x + 20, 668, title, 22, True, anchor="start")
    has = [f"{total} classes in one tree, {depth} levels deep", f"a short code for {codes} of them",
           f"{len(groups)} groups of classes that exclude each other", "the three branches above"]
    lack = [f"labels: {labelled} of {total} classes have one", "definitions of the classes",
            f"relations between classes: {props} properties", "instances: no gods, scenes or monuments as data"]
    for i, t in enumerate(has):
        f.text(lx + 20, 712 + i * 40, t, 20, color=DARK, anchor="start", maxw=pw - 40)
    for i, t in enumerate(lack):
        f.text(rx + 20, 712 + i * 40, t, 20, color=DARK, anchor="start", maxw=pw - 40)
    f.legend(920, [(CLS, "Class"), (OWL, "Root class (imported file, not available)")])
    f.caption("Counts read from dist/tables/owl_inventory.csv and element_classes.csv. The three largest subclasses of each branch are shown.")
    f.save()


def fig_roadmap():
    rows = read(TABLES / "element_classes.csv")
    total = len(rows)
    acr = {}
    for r in rows:
        if r["acronym"]:
            acr.setdefault(r["acronym"], []).append(r["class"])
    clashes = sum(1 for v in acr.values() if len(v) > 1)
    f = Fig("09-roadmap", "Four steps from the received ontology to linked data, and where we stand")
    steps = [("Convert", f"{total} classes from Manchester syntax to Turtle, original IRIs kept", "done", CLS, False),
             ("Clean and describe", f"{clashes} clashing short code found; labels and definitions are missing", "planned", INST, True),
             ("Dock onto standards", "SKOS concepts, CIDOC CRM and CRMba for monuments, rooms and decoration", "planned", INST, True),
             ("Link", "Wikidata, Getty AAT and the old IRIs as references", "planned", INST, True)]
    bw, gap, x0 = 380, 50, 40
    for i, (title, text, status, st, planned) in enumerate(steps):
        x = x0 + i * (bw + gap)
        f.box(x, 200, bw, 100, title, st=st, ts=28, dash=planned)
        f.circle(x + 30, 200, 20, "#ffffff", "#000000", 1.5)
        f.text(x + 30, 200, str(i + 1), 22, True)
        lines = wrap(text, 20, bw - 20, maxlines=4)
        for j, t in enumerate(lines):
            f.text(x + 10, 345 + j * 30, t, 20, color=DARK, anchor="start")
        cw = tw(status, 18, True) + 24
        f.rect(x + 10, 420, cw, 30, PROP[0] if status == "planned" else "#166534", "#000000", 6, 1)
        f.text(x + 10 + cw / 2, 435, status, 18, True, "#000000" if status == "planned" else "#ffffff")
        if i < len(steps) - 1:
            f.line(x + bw + 4, 250, x + bw + gap - 4, 250, w=1.8, dash=steps[i + 1][2] == "planned")
    f.rect(x0 + bw + gap, 490, bw, 170, "#f6f6f3", "#d8d6ce", 8, 1)
    f.text(x0 + bw + gap + 15, 518, "Needs the experts' answers", 20, True, anchor="start")
    for j, t in enumerate(("which short code is meant", "what the classes are called", "what a class stands for")):
        f.text(x0 + bw + gap + 15, 560 + j * 32, t, 19, color=DARK, anchor="start")
    f.legend(905, [(CLS, "Step done"), (INST, "Step planned")])
    f.text(W / 2, 940, "Solid frame: exists in the repository. Dashed: planned.", 17, color=MUTED, maxw=W - 90)
    f.caption("The state of the first step is read from dist/tables/element_classes.csv. The later steps are plans and depend on answers from the subject experts.")
    f.save()


CREDIT = "Figure CC BY 4.0. Numbers read from "
CREDITS = {
    "08-ontology-contents": CREDIT + "dist/tables/owl_inventory.csv and element_classes.csv; the ontology is as received from Anja Wutte.",
    "09-roadmap": CREDIT + "dist/tables/element_classes.csv. The steps after the first are plans.",
    "01-monument-parts": CREDIT + "dist/tables/element_classes.csv and data/curated/space_functions.csv. Room labels from the plan of Harwa (TT37), digitised by Anja Wutte after Eigner (1984); the plan is not part of the figure.",
    "02-data-situation": CREDIT + "dist/tables/owl_inventory.csv and data/curated/grammar_rules.csv. The statements on the left are Anja Wutte's assessment of the field.",
    "05-linking-plan": CREDIT + "dist/tables/owl_inventory.csv and data/curated/space_functions.csv. Match relations and targets are planned.",
    "03-owl-docking": CREDIT + "dist/tables/owl_inventory.csv and element_classes.csv. The ontologies space_layout.owl and id_label.owl are by Georg Suter (TU Wien); licence not yet known.",
    "04-element-classes": CREDIT + "dist/tables/element_classes.csv, converted from the element-class ontology as received.",
    "06-shape-grammar": CREDIT + "data/curated/grammar_rules.csv, transcribed from the shape grammar of Wutte and Duarte (2021).",
    "07-space-functions": CREDIT + "data/curated/space_functions.csv; c is the cubit (0.5 m).",
}

FIGURES = [
    ("01-monument-parts", "V01", fig_monument_parts, "From a monument to its rooms and decoration, shown for Harwa."),
    ("02-data-situation", "V02", fig_data_situation, "Research data on funerary monuments today, and with a shared model."),
    ("08-ontology-contents", "V08", fig_ontology_contents, "What the received ontology contains, and what it does not yet contain."),
    ("09-roadmap", "V09", fig_roadmap, "Four steps from the received ontology to linked data."),
    ("05-linking-plan", "V05", fig_linking_plan, "How the model's identifiers are meant to link to other sources."),
    ("03-owl-docking", "V03", fig_owl_docking, "The received ontology and how the new modules dock onto it."),
    ("04-element-classes", "V04", fig_element_classes, "Element classes: 105 classes, one tree."),
    ("06-shape-grammar", "V06", fig_shape_grammar, "Shape grammar: 31 rules in five stages, with evidence."),
    ("07-space-functions", "V07", fig_space_functions, "Space functions with dimension ranges in cubits."),
]


def index(entries):
    """docs/visuals/index.html: the figure cards, grouped by what they show."""
    cards = {n: site_kit.fig_card(IMG, n, code, cap, cr) for n, code, cap, cr in entries}
    groups = [("The six slides", ["02-data-situation", "01-monument-parts", "08-ontology-contents", "09-roadmap", "05-linking-plan", "03-owl-docking"]),
              ("Backup: the ontology in detail", ["04-element-classes"]),
              ("Shape grammar (second contribution)", ["06-shape-grammar", "07-space-functions"])]
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
