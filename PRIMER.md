# PRIMER – AncientEgyptianFuneraryMonuments

Arbeitsplan für die semantische Modellierung und das Linked Open Data der spätzeitlichen Felsgräber von Theben (CHNT31-Beitrag von Anja Wutte und Florian Thiery). Wird zu Beginn jedes Chats hochgeladen und am Ende zurückgeschrieben. Dieses Dokument ist deutsch, alles andere im Repository (Code, README, Ontologie) ist britisches Englisch.

Stand: 2026-11-04.

---

## Teil A – Immer gültig

### A1 Ausgangslage

| Was | Wo | Rolle |
|---|---|---|
| Elementklassen-Ontologie (Manchester-Syntax) | `data/raw/furnishing_funerary_monument_thebes_element_classes.owl` | Eingang, unverändert wie erhalten |
| Shape Grammar (31 Regeln, 5 Stufen) | `data/curated/grammar_*.csv` | Abschrift aus Grammar.pdf (Wutte und Duarte 2021) |
| Raumfunktionen mit Maßspannen | `data/curated/space_functions.csv` | Abschrift der Tabelle aus Grammar.pdf, Seite 1 |
| Zehn Grundrisse, BIM-Abbildungen, Abstract | nicht im Repository | Lizenz ungeklärt (Memo 01, D4), liegen bei Anja und im Chat-ZIP |
| Memos und Ideen-Dokument | Google Drive, Ordner „Funerals“ | Fragen an Anja, lebendes Ideen-Dokument |

**Nicht neu bauen:** Die 105 Elementklassen und ihre Hierarchie sind Anjas Modell. Wir ergänzen und verankern, wir ersetzen nichts.

**Befunde (geprüft 2026-11-04 an den erhaltenen Dateien):**

- Die OWL deklariert 105 Klassen: 104 mit `SubClassOf`, dazu die importierte Wurzel `SpaceElement`. Tiefen unter der Wurzel: 3, 8, 25, 47, 21 (Stufen 1 bis 5). Zweige: DecorationElement 85, Sculpture 14, FurnishingElement 5 (jeweils mit der Klasse selbst).
- Die Datei enthält nur `SubClassOf`, ein `acronym` je Klasse und drei `DisjointClasses`-Gruppen (14 Funerary Texts, 9 Götterstatuen, 3 Kapellen). Es gibt keine Labels, keine Definitionen, keine Object oder Datatype Properties und keinen CRM-Bezug.
- Die Importe `space_layout.owl` und `id_label.owl` (spacepatterns.com) liegen nicht vor. Die Ontologie ist offline nicht auflösbar. Herkunft: Georg Suter, TU Wien (Design Computing Group); zitiert als „Space ontologies“ in Suter 2022, Automation in Construction 134, 104041, Verzeichnis `spacepatterns.com/ontologies/space_ontologies_002_a_in_c_20/_ontology_directory.htm`; ASCE-Veröffentlichung JCCEE5.CPENG-6294. Lizenz der Dateien unbekannt. Die Seite sperrt automatisierte Abrufe (robots) und hat keinen Wayback-Schnappschuss; ein Zenodo-Supplement (record 13603504, `SFS-A68-16.zip`) ist aus der Arbeitsumgebung nicht abrufbar und noch ungeprüft.
- `id_label.owl` wird nicht importiert, sondern nur über die IRIs seiner sieben Annotationseigenschaften benutzt (`acronym` 104-mal, `colorFill`, `colorStroke`, `weight` je 5-mal, `domain`, `scope` je 1-mal, `name` nie).
- Das Akronym von `NephthysStatue` enthält einen Zeilenumbruch (`"Ne` / `Stat"`). Entfernt man ihn, kollidiert es mit `NeithStatue` (`NeStat`). Das gemeinte Akronym ist unbekannt.
- `HouseOFGold` hat ein großes F im Klassennamen.
- Götter (`Osiris`, `Anubis`, `Re`, `MummifiedGod`) sind Klassen unter `God`. `Owner` hat Unterklassen wie `Wife` und `Mother`.
- Grammar.pdf: 31 Regeln in fünf Stufen (4, 13, 8, 4, 2). Neun Regeln kommen in allen zehn Monumenten vor, sieben in einem. Die Regeln 26 bis 29 (Stufe IV) haben keinen Evidenzwert.
- Raumfunktionen: 23 Zeilen. Das Kürzel `CO` steht für corridor und für column. Die Länge der Rampe ist als „[67 c)“ gedruckt und nicht als Spanne lesbar. Bei middle axis und side axis fehlt die Obergrenze der Breite.
- Das Docx im ZIP ist neuer als das PDF-Abstract. Im PDF steht „Berners-Lee, 2026“ im Text, in der Referenzliste 2006.
- CRMba steht auf cidoc-crm.org als Version 1.4 mit Veröffentlichungsdatum 2016, die Seite nennt zugleich „Draft“. Der Status ist offen.

### A2 Zielbild

```
data/raw/*.owl ──► step_owl ───────► dist/ontology/aefm_elements_source.ttl
                                     dist/tables/element_classes.csv
data/curated/*.csv ─► step_grammar ─► dist/ontology/aefm_grammar.ttl
                                     (SKOS-Schema der Raumfunktionen)
BIM-Export (offen) ─► step_data ───► dist/data/<monument>.ttl      [S8]
                                     │
dist/** + data/curated ─► visuals ──► docs/visuals/ (V01 bis V10)
                     └─► docs ─────► docs/*.md, Layout, Stylesheet (GitHub Pages)
                                     SPARQL-Seite, SHACL, Metadaten  [S10, S11]
```

Eigenschaften, die der fertige Stand haben muss:

1. Jede Figur zieht ihre Zahlen und Beschriftungen aus den Tabellen des Repository. Ändert sich ein Wert dort, bricht der Bau ab oder die Figur ändert sich.
2. `python main.py` zweimal hintereinander lässt `git status` sauber.
3. Die Evidenzwerte `e = n/10` lassen sich aus den Regelanwendungen der zehn Monumente per SPARQL nachzählen und stimmen mit der Abschrift überein.
4. Jede Klasse und jeder Begriff hat einen Anker in CIDOC CRM oder CRMba und eine IRI unter dem eigenen Namensraum.

### A3 Querschnittsregeln

- Rohdaten liegen unter `data/raw/`, unverändert wie erhalten. Was ein Skript daraus macht, liegt unter `dist/`. Abschriften von Hand liegen unter `data/curated/` und sagen im Dateikopf oder Bericht, woher sie stammen.
- Kein Generator ruft `datetime.now()` auf. Datumsangaben kommen aus `RELEASE_DATE` in `py/aefm_utils.py` oder aus den Daten.
- Zweimal laufen lassen, `git status` bleibt sauber. Turtle wird ohne Blank Nodes geschrieben (Skolemisierung oder Paarweise statt `AllDisjointClasses`).
- Netzwerkzugriff gibt es nur in einem eigenen Schritt (z. B. Wikidata-Abgleich), nie im Standardlauf.
- Jeder Schritt läuft auch einzeln (`python py/step_owl.py`). `main.py` ist die Bequemlichkeit, nicht der einzige Weg.
- Kommandos für Windows `cmd` stehen in einer Zeile, zusammengehörige mit `&&`.
- Der Dateiname der Figuren trägt die Figurennummer aus dem Figurenplan (`04-…`, `06-…`, `07-…`).

### A4 Beschlusslage

| Frage | Beschluss | seit |
|---|---|---|
| Ausgabeform der Slides | Nur Figuren im visuals-Stil (SVG und PNG) mit Bildunterschrift, keine fertigen Folien | 2026-11-04 |
| Umfang | 8 bis 10 Figuren | 2026-11-04 |
| Elementklassen | OWL behalten, SKOS-Zwilling ergänzen | 2026-11-04 |
| Namensraum | `https://w3id.org/aefm/` (Name noch zu bestätigen, Eintrag noch zu beantragen) | Vorschlag 2026-11-04 |
| Alte IRIs (spacepatterns.com) | Nur als Verweis mitführen (`skos:exactMatch`, Alternative `owl:equivalentClass`); neue Ressourcen im eigenen Namensraum; Fremdontologien nicht importieren | 2026-11-04 |
| Platzhalter für Fremdontologien | Rekonstruierter Stub mit Wurzelklasse und Annotationseigenschaften, als rekonstruiert markiert, nur für lokale Prüfungen | Vorschlag 2026-11-04 |
| Konvertierung der OWL | Treue Umwandlung mit den Original-IRIs (spacepatterns.com); Umbenennung erst nach Antwort von Anja | Vorschlag 2026-11-04 |
| Akronym `NephthysStatue` | Zeilenumbruch wird entfernt und im Bericht als Kollision gemeldet, kein Ersatzwert geraten | Vorschlag 2026-11-04 |
| Abbildung auf CRM | Monument B1, Raum B2, Raumvolumen und Türöffnung B4, Wand B3, Verbindung BP11 mit BP11.2; Szene E36, Text E33 oder E34, Maß E54 | Vorschlag 2026-11-04 |
| Maßeinheit | Elle (`c`), Länge in Metern offen (Memo 01, C1) | Vorschlag 2026-11-04 |
| Lizenz Code | MIT; Figuren CC BY 4.0; Daten und Ontologie: offen | Vorschlag 2026-11-04 |
| Eingangsdaten im Repository | Nur die OWL und die Abschriften; keine PDFs, keine Grundrisse, solange die Lizenz ungeklärt ist | Vorschlag 2026-11-04 |

### A5 Was in welchem Chat hochgeladen wird

Jeden Chat mit `PRIMER.md` und dem Bündel beginnen. Das Bündel enthält die Quellen und die kleinen Berichte, nicht die erzeugten Figuren.

```cmd
powershell -NoProfile -Command "Compress-Archive -Path main.py,PRIMER.md,README.md,requirements.txt,CITATION.cff,py,data,visuals\build.py,dist\reports,dist\tables -DestinationPath ..\aefm-bundle.zip -Force"
```

Nicht hochladen: `.git/`, `.venv/`, `config.local.json`, `docs/`, große Turtle-Dateien. Neue Eingangsdaten von Anja (BIM-Export, Zuordnungstabellen) kommen als eigene Dateien dazu.

### A6 IRI-Landkarte

| Pfad | Inhalt | Ziel des Redirects | Status |
|---|---|---|---|
| `https://w3id.org/aefm/` | Wurzel, Landing-Page | GitHub Pages des Repository | geplant |
| `https://w3id.org/aefm/grammar/…` | Stufen und Regeln als Individuen | `dist/ontology/aefm_grammar.ttl` | geplant (IRIs stehen schon im Turtle) |
| `https://w3id.org/aefm/vocab/spaceFunction/…` | SKOS-Konzepte der Raumfunktionen | `dist/ontology/aefm_grammar.ttl` | geplant (IRIs stehen schon im Turtle) |
| `https://w3id.org/aefm/unit/cubit` | Maßeinheit Elle | `dist/ontology/aefm_grammar.ttl` | geplant |
| `http://spacepatterns.com/ontologies/space_model/…` | Original-IRIs der Elementklassen | bleiben unverändert | aktiv (extern) |

Offen: Beantragung des w3id-Eintrags (Pull Request im Repository `perma-id/w3id.org`), Content Negotiation (Turtle, RDF/XML, HTML).

---

## Teil B – Schrittübersicht

| ID | Schritt | Repo | hängt ab von | Status |
|---|---|---|---|---|
| S0 | Festlegungen: Namensraum, Treue der Konvertierung, CRM-Abbildung | – | Memo 01 | Vorschläge in A4, offen |
| S1 | Skelett: `main.py`, Utils, Lizenz, Zitation, Fonts | dieses | – | erledigt 2026-11-04 |
| S2 | OWL (Manchester) nach Turtle, Klassentabelle, Befundbericht | dieses | S1 | erledigt 2026-11-04 |
| S2b | Rekonstruierter Platzhalter für `space_layout.owl` und `id_label.owl`, Inventar der OWL | dieses | S2 | erledigt 2026-11-04 |
| S3 | Grammatik und Raumfunktionen als Daten (Turtle, SKOS) | dieses | S1 | erledigt 2026-11-04 |
| S4 | Figuren V03, V04, V06, V07 | dieses | S2, S3 | erledigt 2026-11-04 |
| S4b | Seiten nach `figure-pages-site`: `py/site_kit.py`, `docs/` (Jekyll), Figurenseite `docs/visuals/` | dieses | S4 | erledigt 2026-11-05 |
| S5 | Elementklassen bereinigen: Labels, Definitionen, neue IRIs, Namenskorrekturen | dieses | S0, Memo 01 (B, A) | offen |
| S6 | SKOS-Zwilling der Elementklassen, Alignment Getty AAT und Wikidata | dieses | S5 | offen |
| S7 | Ontologie `aefm-core`: Monument, Raum, Öffnung, Dekorationsprogramm, Topologie auf CRMba | dieses | S0 | offen |
| S8 | Monumentdaten aus dem BIM-Export (Räume, Öffnungen, Maße) | dieses | Memo 01 (D1), S7 | offen |
| S9 | Regelanwendung je Monument, Evidenz per SPARQL nachzählen | dieses | S8, Memo 01 (C3) | offen |
| S10 | SHACL und Metadaten (`wdt-metadata`) | dieses | S7 | offen |
| S11 | SPARQL-Seite im Browser (`wdt-sparql`) | dieses | S8 | offen |
| S12 | Figuren V01, V02, V05, V08, V09, V10 | dieses | S6 bis S9 | offen |
| S13 | Abgleich der zehn Monumente mit Wikidata | dieses | S8 | offen |
| S14 | w3id beantragen, GitHub Pages | dieses | S0 | offen |

Unabhängig voneinander laufen können S5 und S7 (beide hängen nur an Antworten von Anja), sowie S10 und S14. S3 und S2 sind unabhängig von allem Weiteren und stehen schon.

---

## Teil C – Die Schritte

### S1 – Skelett

**Ziel:** Das leere Repository hat das Gerüst der Familie, und `python main.py` läuft.

**Abnahme:** `python main.py --list` zeigt fünf Schritte, `python main.py` läuft durch, zweimal hintereinander bleibt `git status` sauber.

#### Erledigt 2026-11-04

Layout: `main.py`, `py/aefm_utils.py`, `py/step_*.py`, `py/site_kit.py`, `visuals/build.py`, `data/raw`, `data/curated`, `dist/` und `docs/` werden erzeugt und mit versioniert. `.gitignore` ignoriert `dist/` bewusst nicht. `dist/pipeline_report.txt` enthält keine Zeiten, die Zeittabelle erscheint nur im Terminal.

### S2 – OWL nach Turtle

**Ziel:** Die Elementklassen liegen als Turtle und als Tabelle vor, und die Befunde über die Quelle stehen in einem Bericht.

**Abnahme:** 105 deklarierte Klassen, `dist/reports/owl_report.txt` nennt Imports, Tiefenverteilung, Zweige und die Befunde aus A1. Zweimal laufen lassen ergibt identische Dateien.

#### Erledigt 2026-11-04

469 Tripel. Der Konverter versteht die Teilmenge der Manchester-Syntax, die die Datei verwendet, und bricht bei einer anderen Klassenzahl ab. `AllDisjointClasses` wäre ein Blank Node, deshalb steht jede Disjunktheit als `owl:disjointWith` zwischen zwei Klassen. Gefunden und gemeldet: doppeltes Akronym `NeStat` (NeithStatue, NephthysStatue), `HouseOFGold`.

### S2b – Platzhalter und Inventar

**Ziel:** Solange die Originale von Suter fehlen, deklariert ein klar als rekonstruiert markierter Stub nur das, was die Elementklassen-OWL benutzt. Ein Inventar der OWL liegt als Tabelle vor.

**Abnahme:** `dist/ontology/aefm_reference_stub.ttl` mit einer Klasse und sieben Annotationseigenschaften (28 Tripel), `dist/tables/owl_inventory.csv`. Beides ändert sich bei zweitem Lauf nicht.

#### Erledigt 2026-11-04

Die IRIs bleiben die von spacepatterns.com, damit die Elementklassen gegen die echten Dateien gültig bleiben. Jede Deklaration trägt einen Kommentar, dass sie rekonstruiert ist und das Original von Georg Suter kommen muss. Der Stub ist nicht zum Import gedacht. Sobald die Originale vorliegen, wird er ersetzt oder gestrichen.

### S3 – Grammatik und Raumfunktionen

**Ziel:** Stufen, Regeln und Raumfunktionen sind Daten mit stabilen IRIs.

**Abnahme:** 5 Stufen, 31 Regeln, 23 Raumfunktionen. Der Lauf bricht ab, wenn Regelnummern nicht 1 bis 31 sind, eine Regel in der falschen Stufe liegt oder eine Spanne verkehrt herum steht.

#### Erledigt 2026-11-04

464 Tripel. Die CSV-Abschrift wurde einmal maschinell aus dem Text von Grammar.pdf erzeugt (31 Regeln, Evidenzwerte stimmen mit der Seite überein) und danach von Hand kuratiert. Die Raumfunktionstabelle wurde an der gerenderten Seite 1 abgelesen. Die Bedingungen der Regeln (Längen und Breiten, Funktionsbedingungen) sind noch nicht abgebildet, Memo 01 C5 fragt, ob das nötig ist. Die SKOS-Konzepte tragen Maße als `xsd:decimal`, die Einheit hängt an der IRI `unit/cubit`.

### S4 – Figuren V03, V04, V06, V07

**Ziel:** Vier Figuren im Stil der `visuals` aus GeoScience-FAIRification-LOD (1750×1000, Fira Sans, SVG und PNG, Farbschema).

**Abnahme:** `docs/visuals/index.html` zeigt vier Figuren. Texte laufen nicht über ihre Boxen (der Bau bricht sonst ab). Die Figuren ändern sich nur, wenn sich die Tabellen ändern.

#### Erledigt 2026-11-04

V03 zeigt die empfangene OWL (die zwei fehlenden Dateien, die 105 Klassen, die Verteilung auf die Ebenen) und wie die neuen Module andocken, durchgezogen was existiert, gestrichelt was geplant oder nicht verfügbar ist; die Zahlen kommen aus `owl_inventory.csv` und `element_classes.csv`. V04 zeigt die 105 Klassen als Baum, V06 die Stufen und Regeln mit Evidenzpunkten, V07 die Raumfunktionen mit Längen- und Breitenbereichen in Ellen. V07 benennt die offenen Stellen der Quelle direkt in der Zeile (Rampe, Achsen, Treppe).

### S4b – Seiten (figure-pages-site)

**Ziel:** Ein Design für Dokumentations- und Figurenseiten, veröffentlicht mit GitHub Pages aus `docs/`.

**Abnahme:** `docs/` enthält `_config.yml`, `_layouts/default.html`, `assets/` (Stylesheet, Fira Sans), drei Seiten (`index.md`, `ontology.md`, `grammar.md`) und die statische Figurenseite `visuals/index.html` mit vier Figurenkarten. Zwei Läufe ergeben identische Dateien.

#### Erledigt 2026-11-05

`py/site_kit.py` ist die einzige Quelle für Stylesheet, Navigation (zwei Zeilen: Documentation, Visuals), Jekyll-Layout und Figurenkarte. `py/step_docs.py` schreibt die Markdown-Seiten aus den Tabellen; öffentliche Seiten zeigen nur Gesichertes (Befunde, Zahlen, Herkunft), interne Fragen bleiben in `PRIMER.md` und in den Memos. Die Figuren liegen unter `docs/visuals/img/`, `visuals/site/` entfällt. Einmalig im Repository einstellen: Settings, Pages, Deploy from a branch, `main`, `/docs`. Die Jekyll-Seiten wurden hier nur mit einem Ersatz für Liquid geprüft, nicht mit Jekyll selbst. `GeoScience-FAIRification-LOD` und `CAA2026-alligator` haben noch statische Seiten ohne Layout, `CHNT2026-amt` war nicht abrufbar; die Umsetzung folgt dem Skill `figure-pages-site`.

### S5 – Elementklassen bereinigen

**Ziel:** `aefm-elements` mit `rdfs:label`, `skos:definition`, bereinigten Namen und IRIs unter dem eigenen Namensraum; die Original-IRIs bleiben als `owl:equivalentClass` oder `skos:exactMatch` erhalten.

**Uploads:** Antworten zu Memo 01, Abschnitt A und B.

**Abnahme:** Jede Klasse hat ein englisches Label, kein Klassenname enthält einen Großbuchstabenlauf, die Akronyme sind eindeutig, ein Bericht listet jede umbenannte Klasse mit alter und neuer IRI.

### S6 – SKOS-Zwilling

**Ziel:** Die Elementklassen als SKOS-Konzepte mit `skos:broader`, Labels und Alignment zu Getty AAT und Wikidata.

**Abnahme:** Zahl der Konzepte gleich Zahl der Klassen, `skos:broader` stimmt mit `rdfs:subClassOf` überein, Alignments sind als `skos:exactMatch` oder `skos:closeMatch` gekennzeichnet.

### S7 – Ontologie `aefm-core`

**Ziel:** Klassen und Eigenschaften für Monument, Raum, Öffnung, Dekorationsprogramm und Topologie, verankert in CRMba.

**Uploads:** Antwort zu Memo 01, A2 (Namensraum), und der Stand von CRMba laut cidoc-crm.org.

**Abnahme:** Jede Klasse hat einen CRM- oder CRMba-Anker, die Ontologie lädt ohne die fehlenden Importe, ein SHACL-Beispiel für ein Monument besteht.

### S9 – Regelanwendung und Evidenz

**Ziel:** Pro Monument die angewendeten Regeln als Daten, Evidenz `e = n/10` aus dem Graphen.

**Uploads:** Tabelle Regel mal Monument von Anja.

**Abnahme:** Die gezählten Werte stimmen für alle 27 Regeln mit Evidenzwert mit `grammar_rules.csv` überein, Abweichungen stehen im Bericht.

---

## Teil D – Offene Punkte

- Antworten auf Memo 01 (siehe Drive-Ordner „Funerals“). Das Memo wird um die Frage nach dem gemeinten Akronym von `NephthysStatue` ergänzt.
- Originale `space_layout.owl` und `id_label.owl` samt Lizenz: Anfrage an Georg Suter über Anja (Memo 01, Abschnitt F), dazu Zenodo-Supplement prüfen, sobald die Datei vorliegt.
- Urheberschaft und Lizenz der Elementklassen-OWL und der Abschriften: Sie liegen unter `data/raw` und `data/curated` im Repository, solange die Antwort fehlt.
- Urheberrechtsvermerk in `LICENSE` und `CITATION.cff`: Anja Wutte und Florian Thiery sind aus dem Dateinamen des Abstracts abgeleitet, ORCIDs fehlen.
- Format des BIM-Exports (IFC, CSV, JSON) und Beispieldatei.
- Ob BOT oder ifcOWL als Brücke zur BIM-Geometrie nötig ist, hängt am Exportformat.
- Verankerung der Shape-Grammar-Regel im CRM (Kandidat E29 Design or Procedure) ist offen.
- Falls ein Punkt hier fünf Chats überlebt: entweder als Formular stellen oder streichen.
