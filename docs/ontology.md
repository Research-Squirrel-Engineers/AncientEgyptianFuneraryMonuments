---
layout: default
title: "Element classes"
intro: "The element-class ontology as received: 105 classes below one root, converted to Turtle without changing the model."
---


## What the file contains

105 classes in one tree below `SpaceElement`, 5 levels deep, in three branches:

| Branch | Classes |
|---|---|
| DecorationElement | 85 |
| Sculpture | 14 |
| FurnishingElement | 5 |

Each class carries an acronym. The file has no labels, definitions or properties beyond subclass relations and disjointness. Nothing was renamed in the conversion.

![How the received ontology and the new modules fit together]({{ '/visuals/img/03-owl-docking.png' | relative_url }})

## Received files and provenance

The element classes build on two ontologies by Georg Suter (TU Wien, Design Computing Group), described in Suter (2022), *Automation in Construction* 134, 104041. `space_layout.owl` is imported. `id_label.owl` is not imported; only the IRIs of its 7 annotation properties are used. Neither file is part of this repository, and their licence is not yet known.

The original IRIs are kept as references. New resources are planned in their own namespace and will point to the old IRIs. A small stand-in, marked as reconstructed, declares only what the element classes use. It is meant for local checks and not for import by others.

## Files

* [`dist/ontology/aefm_elements_source.ttl`](https://github.com/Research-Squirrel-Engineers/AncientEgyptianFuneraryMonuments/blob/main/dist/ontology/aefm_elements_source.ttl): the element classes as Turtle.
* [`dist/ontology/aefm_reference_stub.ttl`](https://github.com/Research-Squirrel-Engineers/AncientEgyptianFuneraryMonuments/blob/main/dist/ontology/aefm_reference_stub.ttl): the reconstructed stand-in.
* [`dist/tables/element_classes.csv`](https://github.com/Research-Squirrel-Engineers/AncientEgyptianFuneraryMonuments/blob/main/dist/tables/element_classes.csv): one row per class.
* [`dist/reports/owl_report.txt`](https://github.com/Research-Squirrel-Engineers/AncientEgyptianFuneraryMonuments/blob/main/dist/reports/owl_report.txt): findings about the source.
