#!/usr/bin/env python3
"""main.py - the single entry point of AncientEgyptianFuneraryMonuments.

    python main.py                     all steps, in order
    python main.py --list              print steps and exit
    python main.py --only grammar      one step
    python main.py --from grammar      this step and everything after
    python main.py --skip visuals      everything but this
    python main.py --dry-run           print the plan, run nothing
    python main.py --strict            a warning in any step's output fails the run

Every step stays runnable on its own (python py/step_owl.py). Step output is passed
through line by line and written to dist/pipeline_report.txt. The report carries no
timings or dates, so a rebuild changes it only when a step's output changes.
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent
STEPS = [  # name, script, what it writes
    ("owl", "py/step_owl.py", "dist/ontology/aefm_elements_source.ttl, dist/tables/, dist/reports/owl_report.txt"),
    ("stub", "py/step_stub.py", "dist/ontology/aefm_reference_stub.ttl"),
    ("grammar", "py/step_grammar.py", "dist/ontology/aefm_grammar.ttl, dist/reports/grammar_report.txt"),
    ("visuals", "visuals/build.py", "docs/visuals/ (figures and the figure page), docs/assets/"),
    ("docs", "py/step_docs.py", "docs/*.md, docs/_layouts/, docs/_config.yml"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("--from", dest="start")
    ap.add_argument("--skip")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    names = [s[0] for s in STEPS]
    for opt in (a.only, a.start, a.skip):
        if opt and opt not in names:
            sys.exit(f"unknown step {opt!r}; steps are: {', '.join(names)}")
    if a.list:
        for n, s, w in STEPS:
            print(f"{n:10s}{s:22s}{w}")
        return
    plan = STEPS
    if a.only:
        plan = [s for s in plan if s[0] == a.only]
    if a.start:
        plan = plan[names.index(a.start):]
    if a.skip:
        plan = [s for s in plan if s[0] != a.skip]
    if a.dry_run:
        for n, s, _ in plan:
            print(f"would run {n}: {s}")
        return
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    log, timing = [], []
    for n, script, _ in plan:
        t0 = time.perf_counter()
        p = subprocess.run([sys.executable, "-I", str(REPO / script)], cwd=REPO, env=env,
                           capture_output=True, text=True, encoding="utf-8")
        timing.append((n, time.perf_counter() - t0))
        out = (p.stdout + p.stderr).rstrip("\n")
        for line in out.splitlines():
            print(f"[{n}] {line}")
            log.append(f"[{n}] {line}")
        if p.returncode:
            sys.exit(f"step {n} failed with exit code {p.returncode}")
        if a.strict and "warning" in out.lower():
            sys.exit(f"step {n} printed a warning and --strict is set")
    if not (a.only or a.start or a.skip):
        (REPO / "dist").mkdir(exist_ok=True)
        (REPO / "dist" / "pipeline_report.txt").write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
    total = sum(t for _, t in timing) or 1
    print("\nstep        seconds   share")
    for n, t in timing:
        print(f"{n:10s}{t:8.1f}{100 * t / total:7.0f}%")


if __name__ == "__main__":
    main()
