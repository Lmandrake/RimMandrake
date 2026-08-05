#!/usr/bin/env python3
"""
loop_run.py  —  execute an LLM-authored improvement PLAN and score the result
=============================================================================

This is the executor half of the LLM-in-the-loop workflow. The REASONING (region
decomposition, per-region judgment, and the specific edits with real
coordinates) is authored by the LLM and handed in as a PLAN (JSON or a Python
dict). This script:
  1. loads the base map + perceives it (before metrics),
  2. applies each edit in the plan via map_agent primitives,
  3. re-perceives (after metrics),
  4. renders before/after,
  5. writes a report pairing each edit with the LLM's stated judgment + rationale
     and shows the metric deltas so the LLM can decide whether to iterate.

Plan schema (see coastal_mesa plan at bottom for a worked example):
  {
    "base": "coastal_mesa.map.json",
    "regions": [ {name, judgment:{realism,interest,tactical,artificiality},
                  problem, intent} ... ],       # the LLM's decomposition+scores
    "edits":  [ {region, op, rationale, args:{...}} ... ]  # executed in order
  }

Usage:
  python3 loop_run.py <plan.json> [--out DIR] [--scale 5]
"""

import os
import sys
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import map_agent as MA                       # noqa: E402
from mapkit import GameMap, render, render_pair   # noqa: E402


def run_plan(plan, base_dir, out_dir, scale=5):
    base_path = os.path.join(base_dir, plan["base"])
    gm = GameMap.load_json(base_path)
    stem = plan.get("stem") or os.path.basename(base_path).split(".")[0]

    before = gm.copy()
    m_before = MA.metrics(gm)

    log = []
    for e in plan["edits"]:
        op = e["op"]
        args = dict(e.get("args", {}))
        try:
            changed = MA.apply_edit(gm, op, **args)
            log.append({**e, "cells_changed": changed, "ok": True})
        except Exception as ex:
            log.append({**e, "cells_changed": 0, "ok": False,
                        "error": "%s: %s" % (type(ex).__name__, ex)})

    # optional final cleanup smoothing pass if the plan asked for it
    m_after = MA.metrics(gm)
    gm.name = before.name + "_v" + str(plan.get("iteration", 1))

    os.makedirs(out_dir, exist_ok=True)
    render_pair(before, gm, os.path.join(out_dir, "%s_loop_beforeafter.png" % stem),
                scale=scale,
                titles=("BEFORE: %s" % before.name, "AFTER (LLM plan)"))
    render(gm, os.path.join(out_dir, "%s_loop_after.png" % stem), scale=scale,
           title="IMPROVED: %s" % gm.name)
    gm.save_json(os.path.join(out_dir, "%s_loop.map.json" % stem))

    # -------- report --------
    R = []
    R.append("# LLM-in-the-loop improvement — `%s` (iteration %d)\n"
             % (before.name, plan.get("iteration", 1)))
    R.append("The region decomposition, judgments, and edits below were "
             "authored by the LLM reasoning over the perceived map; this script "
             "only executed the primitives and measured the result.\n")

    R.append("## Region decomposition + judgment (LLM)\n")
    R.append("Scores 0-10. realism = looks like a real place · interest = worth "
             "exploring/fighting over · tactical = meaningful combat geography · "
             "artificiality = looks generator-stamped (LOWER is better).\n")
    R.append("| Region | Real | Intr | Tact | Artif | Problem → Intent |")
    R.append("|---|---|---|---|---|---|")
    for rg in plan["regions"]:
        j = rg["judgment"]
        R.append("| %s | %d | %d | %d | %d | %s → %s |" % (
            rg["name"], j["realism"], j["interest"], j["tactical"],
            j["artificiality"], rg["problem"], rg["intent"]))
    R.append("")

    R.append("## Edits executed (each tied to a region + rationale)\n")
    for i, e in enumerate(log, 1):
        status = "" if e["ok"] else "  ⚠️ FAILED: %s" % e.get("error", "")
        R.append("%d. **%s** _(region: %s, op: `%s`, %d cells)_%s"
                 % (i, e.get("what", e["op"]), e.get("region", "-"),
                    e["op"], e["cells_changed"], status))
        R.append("   - %s" % e.get("rationale", ""))
    R.append("")

    R.append("## Metric deltas (objective guardrails, not the judge)\n")
    def line(k, lo_better):
        b, a = m_before[k], m_after[k]
        d = a - b
        arrow = "→"
        good = (d < 0) if lo_better else (d > 0)
        tag = "improved" if (d != 0 and good) else ("worse" if d != 0 else "flat")
        return "- **%s**: %s %s %s  (%s)" % (k, b, arrow, a, tag)
    R.append(line("transition_coherence", lo_better=False))
    R.append(line("fragmentation_tiny_patches", lo_better=True))
    R.append(line("family_diversity", lo_better=False)
             + "  _(diversity is informational — interpret in context)_")
    R.append("")
    if "notes" in plan:
        R.append("## Layering notes (pawns / items / story)\n")
        for n in plan["notes"]:
            R.append("- %s" % n)
        R.append("")

    rep_path = os.path.join(out_dir, "%s_loop_report.md" % stem)
    with open(rep_path, "w") as fh:
        fh.write("\n".join(R))

    # console summary
    print("Applied %d edits to '%s'." % (len(log), before.name))
    for e in log:
        flag = "" if e["ok"] else "  FAILED"
        print("  [%s] %-22s %5d cells%s"
              % (e.get("region", "-")[:10].ljust(10), e["op"],
                 e["cells_changed"], flag))
    print("\nmetrics before:", json.dumps(m_before))
    print("metrics after :", json.dumps(m_after))
    print("report:", rep_path)
    return m_before, m_after, log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--out", default=None)
    ap.add_argument("--scale", type=int, default=5)
    args = ap.parse_args()
    with open(args.plan) as fh:
        plan = json.load(fh)
    base_dir = os.path.dirname(os.path.abspath(args.plan))
    out_dir = args.out or base_dir
    run_plan(plan, base_dir, out_dir, scale=args.scale)


if __name__ == "__main__":
    main()
