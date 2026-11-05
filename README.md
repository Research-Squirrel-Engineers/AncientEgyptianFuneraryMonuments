# AncientEgyptianFuneraryMonuments

Semantic model and Linked Open Data for the Late Period rock-cut funerary monuments at Thebes
(Twenty-fifth and Twenty-sixth Dynasty). It accompanies the CHNT31 contribution
*From Single Monuments to Systematic Comparison* by Anja Wutte and Florian Thiery: the BIM
system holds geometry and measurements, this repository holds meaning, classification and
relations as an ontology and a knowledge graph.

The work plan is in German in [`PRIMER.md`](PRIMER.md).

## Run

    pip install -r requirements.txt
    python main.py

`python main.py --list` shows the steps, `--only`, `--from` and `--skip` select some of them.
Every step also runs on its own, for example `python py/step_owl.py`.

## What is here

| Path | Content |
|---|---|
| `data/raw/` | The element-class ontology as received (OWL, Manchester syntax). |
| `data/curated/` | Hand transcriptions: the shape grammar (stages, rules, evidence) and its table of space functions. |
| `py/` | One module per step, plus `aefm_utils.py`. |
| `dist/ontology/` | `aefm_elements_source.ttl` (faithful conversion, original IRIs) and `aefm_grammar.ttl` (grammar individuals, SKOS scheme of space functions). |
| `dist/tables/`, `dist/reports/` | Class table and reports on what the sources contain and leave open. |
| `visuals/` | `build.py` draws the slide figures in the house pattern of the Research Squirrel Engineers (1750x1000, Fira Sans, SVG and PNG). |
| `docs/` | The published site (GitHub Pages): Jekyll pages, the figure page `docs/visuals/` with the figures, stylesheet and fonts. Generated. |

Everything under `dist/` and `docs/` is generated. Nothing in the pipeline reads the clock,
so running `python main.py` twice leaves `git status` clean.

## Namespace

New resources use `https://w3id.org/aefm/`. The name is a proposal and the w3id.org entry has not
been requested yet, so these IRIs do not resolve at the moment.

## Sources

- Wutte, A. and Duarte, J. P. (2021). Shape Grammar as a Typology Defining Tool for Ancient Egyptian
  Funerary Monuments. *Nexus Network Journal*, 319-336. <https://doi.org/10.1007/s00004-020-00543-8>
- Wutte, A., Ferschin, P. and Suter, G. (2015). Excavation goes BIM. 20th International Conference on
  Cultural Heritage and New Technologies, Vienna.
- Eigner, D. (1984). *Die monumentalen Grabbauten der Spätzeit in der thebanischen Nekropole I.* Vienna.

## Licence

Code: MIT. Figures: CC BY 4.0. Fonts: Fira Sans, SIL OFL 1.1, see `visuals/fonts/`.
The licence of the ontology and the transcribed tables is not settled yet; see `PRIMER.md`, part D.

## Site

The pages in `docs/` are published with GitHub Pages: Settings, Pages, Deploy from a branch, branch `main`, folder `/docs`. The site is then served at https://research-squirrel-engineers.github.io/AncientEgyptianFuneraryMonuments/. The pages show only what the tables say; internal notes stay in `PRIMER.md`.
