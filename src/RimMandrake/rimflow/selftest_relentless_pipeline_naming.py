#!/usr/bin/env python3
"""PIPELINE_RENAME_WORKERS_NOW_SWAPPABLE: the system is the Relentless Pipeline; its workers are Relentless-style
Builder/Judge workers from MandrakeWorkflows (owner, 2026-11-03).

Checks the RimMandrake docs and pages that name the system, and that no live doc calls the system the Relentless
Agent outside a quote or a dated history line. The MandrakeWorkflows half (the README split) is read from that repo's
origin/main when the clone is readable; otherwise that clause prints UNMEASURED and does not fail.
Exit 0 all measured clauses pass, 1 a clause fails.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MW = os.path.expanduser(os.environ.get("MANDRAKEWORKFLOWS_DIR", "~/dev/MandrakeWorkflows"))
fails = []


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name)
    if not ok:
        fails.append(name)


# 1. The docs that introduce the system name the pipeline and its workers.
claude = read("CLAUDE.md")
check("CLAUDE.md names the Relentless Pipeline and Builder/Judge workers from MandrakeWorkflows",
      "Relentless Pipeline" in claude and re.search(r"Relentless-style Builder/Judge workers from\s+MandrakeWorkflows", claude))
charter = read("infrastructure/agents/CHARTER.md")
check("CHARTER names the Relentless Pipeline and swappable Builder/Judge workers",
      "the Relentless Pipeline" in charter and "Relentless-style Builder/Judge workers from MandrakeWorkflows" in charter
      and "swappable" in charter)
doc = read("src/RimMandrake/rimflow/relentless.py").split('"""')[1]
check("relentless.py docstring: the Relentless Pipeline, workers Builder/Judge from MandrakeWorkflows",
      "the Relentless Pipeline" in doc and re.search(r"Relentless-style Builder/Judge from MandrakeWorkflows", doc))
for agent, mode in (("rm-builder", "Builder"), ("rm-judge", "Judge")):
    text = read(".claude/agents/%s.md" % agent)
    check("%s says it fills a Relentless Pipeline place as a Relentless-style %s" % (agent, mode),
          "Relentless Pipeline" in text and ("Relentless-style %s from MandrakeWorkflows" % mode) in text
          and "relentless/workers/BUILDER_JUDGE.md" in text)

# 2. The rules file still points the pipeline's places at those two agents (the swap point the docs name).
rules = json.loads(read("src/RimMandrake/rimflow/relentless_rules.json"))
check("relentless_rules.json: worker_agent rm-builder, checker_agent rm-judge",
      rules.get("worker_agent") == "rm-builder" and rules.get("checker_agent") == "rm-judge")

# 3. The RELENTLESS_NOW page's Relentless panel and text say Pipeline, Builders and Judges.
page = read("src/RimMandrake/Utils/running_now.py")
check("RELENTLESS_NOW panel: RELENTLESS PIPELINE with Builders and Judges",
      '"PIPELINE"' in page and "RELENTLESS PIPELINE" in page and "Builders %d, Judges %d" in page)

# 4. No live doc names the system the Relentless Agent, except a quote or a dated history/design-record line.
LIVE = ["CLAUDE.md", "infrastructure/agents", "src/RimMandrake/rimflow/roles", "skills", ".claude/agents",
        "infrastructure/state/CONDUCTOR_GOALS.md", "src/RimMandrake/rimflow/relentless.py"]
stale = []
for rel in LIVE:
    path = os.path.join(ROOT, rel)
    files = [path] if os.path.isfile(path) else [os.path.join(d, f) for d, _, fs in os.walk(path) for f in fs
                                                 if f.endswith((".md", ".py", ".json"))]
    for fp in files:
        with open(fp, encoding="utf-8", errors="replace") as f:
            for n, line in enumerate(f, 1):
                for m in re.finditer(r"Relentless Agent", line):
                    before, after = line[:m.start()], line[m.end():]
                    if before.count('*"') > before.count('"*') or before.count("“") > before.count("”") \
                            or after.count('"*') > after.count('*"'):
                        continue    # inside his quoted words (a quote may open on the line above)
                    stale.append("%s:%d" % (os.path.relpath(fp, ROOT), n))
check("no live doc calls the system the Relentless Agent (%s)" % (", ".join(stale[:5]) or "none"), not stale)
for rel in ("design/RimMandrake/relentless_agent_design_2026-11-01.md", "design/RimMandrake/concept_agent_design_2026-11-01.md"):
    check("%s points at workers/BUILDER_JUDGE.md, not the moved agent/RELENTLESS_AGENT.md" % rel,
          "relentless/workers/BUILDER_JUDGE.md" in read(rel) and "agent/RELENTLESS_AGENT.md" not in read(rel))

# 5. MandrakeWorkflows: the README split, read from its origin/main.
def mw_show(path):
    r = subprocess.run(["git", "-C", MW, "show", "origin/main:" + path], capture_output=True, text=True, timeout=60)
    return r.stdout if r.returncode == 0 else None

try:
    readable = os.path.isdir(os.path.join(MW, ".git")) and mw_show("README.md") is not None
except (OSError, subprocess.SubprocessError):
    readable = False
if not readable:
    print("UNMEASURED MandrakeWorkflows README split: %s not readable here" % MW)
else:
    pipe, workers, defn = mw_show("relentless/README.md"), mw_show("relentless/workers/README.md"), \
        mw_show("relentless/workers/BUILDER_JUDGE.md")
    check("MandrakeWorkflows relentless/README.md is the Relentless Pipeline page, linking its workers page",
          bool(pipe) and pipe.startswith("# Relentless Pipeline") and "workers/README.md" in pipe
          and "Relentless Agent" not in pipe)
    check("MandrakeWorkflows relentless/workers/README.md is the Builder/Judge workers page",
          bool(workers) and workers.startswith("# Relentless-style workers: Builder and Judge")
          and "BUILDER_JUDGE.md" in workers)
    check("MandrakeWorkflows workers/BUILDER_JUDGE.md is the worker definition; agent/RELENTLESS_AGENT.md is gone",
          bool(defn) and defn.startswith("# Relentless-style Builder/Judge: the worker definition")
          and mw_show("relentless/agent/RELENTLESS_AGENT.md") is None)
    top = mw_show("README.md") or ""
    check("MandrakeWorkflows top README lists the Relentless Pipeline, not the Relentless Agent",
          "**Relentless Pipeline**" in top and "Relentless Agent" not in top)

print("FAILED %d" % len(fails) if fails else "ALL PASS")
sys.exit(1 if fails else 0)
