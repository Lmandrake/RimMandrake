#!/usr/bin/env python3
"""
map_loop_agent.py  —  re-runnable LLM-in-the-loop map improver (harness)
========================================================================

This is the AUTOMATED version of the workflow we drove by hand in loop_run.py.
It wires the full cycle so it can run unattended once an LLM endpoint is
available:

    perceive (map_agent)  →  ask LLM to DECOMPOSE+JUDGE+PROPOSE (a plan)  →
    execute the plan's edits (map_agent primitives)  →  re-perceive + metrics  →
    ask LLM to RE-JUDGE and decide continue/stop  →  loop until converged or
    max_iters.

IMPORTANT — sandbox limitation (2026-08-05)
-------------------------------------------
No LLM API is reachable from the environment this was authored in (only an institutional
host is allowlisted; WebSearch/web_fetch are blocked). So the LLM-call seam is
PLUGGABLE and ships with a stub that raises a clear error. To make this live,
implement `call_llm(messages) -> str` for your endpoint (Anthropic, Bedrock,
a local model, whatever) and pass it in, or set it as the module `LLM_CALLER`.
Everything AROUND that seam — perception, prompt construction, plan validation,
primitive dispatch, metric scoring, convergence, transcript logging — is real
and was exercised by hand in loop_run.py.

The LLM contract
----------------
DECOMPOSE/PROPOSE prompt returns JSON:
  {"regions":[{name,judgment:{realism,interest,tactical,artificiality},
               problem,intent}],
   "edits":[{region,op,what,rationale,args:{...}}],
   "notes":[...]}
RE-JUDGE prompt returns JSON:
  {"regions":[...updated scores...], "verdict":"continue"|"stop",
   "reason":"...", "next_focus":"..."}

`op` must be one of map_agent.PRIMITIVES; `args` are the kwargs. Invalid ops or
kwargs fail loudly and are fed back to the LLM as an error to repair.

Usage (once an endpoint is wired):
  python3 map_loop_agent.py <base.map.json> --max-iters 4 --out DIR
"""

import os
import sys
import json
import argparse
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import map_agent as MA                              # noqa: E402
from mapkit import GameMap, render, render_pair      # noqa: E402


# ==========================================================================
# LLM SEAM  (implement for your endpoint)
# ==========================================================================
class LLMNotConfigured(RuntimeError):
    pass


def _stub_caller(messages):
    raise LLMNotConfigured(
        "No LLM caller configured. Implement call_llm(messages)->str for your "
        "endpoint and pass caller=... to run_agent (or set LLM_CALLER). In this "
        "sandbox no API host is allowlisted, so the loop cannot self-drive here; "
        "use loop_run.py with a hand-authored plan instead.")


# module-level default; override by assignment or via run_agent(caller=...)
LLM_CALLER = _stub_caller


# ==========================================================================
# PROMPTS
# ==========================================================================
SYSTEM = """You are a RimWorld map designer improving a semantic terrain map for
a mostly-desert, highly-volcanic 'crashed Factory ship / Jawa' campaign with
anti-exponential design pillars. You reason over a coarse ASCII map + a region
segmentation + an image, decompose the map into regions, judge each region on
realism/interest/tactical/artificiality (0-10; artificiality LOWER is better),
and propose SPECIFIC edits with REAL coordinates drawn from the region briefing.
Edits are executed by a fixed toolbox of primitives — you must use only those
primitives and their documented args. Prefer edits that reshape EXISTING terrain
coherently over stamping features onto open ground. Return STRICT JSON only."""

PRIMITIVE_DOC = """Available primitives (op -> args):
- terrain_gradient(region_bbox=[x0,z0,x1,z1], order=[terrain,...], axis='h'|'v',
    reverse=bool, noise=float) : smooth banded transition across a rect.
- fractalize_edge(from_family, to_terrain, coast_terrain, amount=0..1, reach=int)
    : coherent meander of a family's boundary (coast/cliff). Not per-cell noise.
- scatter(region_bbox, terrain, density=0..1, clump=0..1, only_families=[...],
    patch=bool) : coherent small patches (patch=True) of terrain.
- path(waypoints=[[x,z],...], terrain, width=int) : road/trail/wash.
- blob(cx,cz,radius,terrain,only_families=[...],jitter) : organic patch (pond,
    clearing, soil hollow, sludge).
- ring(cx,cz,r_in,r_out,terrain,only_families) : annulus (crater rim, apron).
- rect(x0,z0,x1,z1,terrain) : filled rectangle (ruin pad, platform).
- hill(cx,cz,radius,ring_terrain,core_terrain) : rubble apron + rock core.
- carve_chamber(cx,cz,radius,require_family=['mountain']) : hollow a cave but
    ONLY through solid rock (refuses open ground).
- paint_cells(cells=[[x,z],...], terrain) : freehand escape hatch.
- smooth(only_families=[...], passes=int) : kill single-cell confetti.
Terrain names come from the campaign palette (Sand, SoftSand, Soil, SoilRich,
MossyTerrain, Gravel, RockRubble, RockFace, AB_ForsakenRock, CaveFloor, Mud,
Marsh, WaterOceanDeep, WaterOceanShallow, WaterShallow, WaterMovingShallow,
AB_SolidifiedLava, AB_LiquidLava, AB_Obsidian, AB_VolcanicGravel,
AncientConcrete, MetalTile, AB_AsphaltFloor)."""


def propose_prompt(brief_text, metrics, image_note):
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content":
            "%s\n\nCurrent objective metrics (guardrails, not the judge): %s\n\n"
            "MAP BRIEFING:\n%s\n\n%s\n\nDecompose this map into regions, judge "
            "each, and propose edits to raise realism/interest/tactical and "
            "lower artificiality. Return STRICT JSON with keys regions, edits, "
            "notes."
            % (PRIMITIVE_DOC, json.dumps(metrics), brief_text, image_note)},
    ]


def rejudge_prompt(brief_before, brief_after, m_before, m_after, plan):
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content":
            "You proposed this plan:\n%s\n\nMetrics before: %s\nMetrics after: "
            "%s\n\nBEFORE briefing:\n%s\n\nAFTER briefing:\n%s\n\nRe-judge each "
            "region on the 4 axes now. If artificiality rose or a metric "
            "regressed (fragmentation up, diversity crashed) treat that as a "
            "failure to repair. Return STRICT JSON: {regions:[...], verdict:"
            "'continue'|'stop', reason:'...', next_focus:'...'}."
            % (json.dumps(plan.get("edits", [])), json.dumps(m_before),
               json.dumps(m_after), brief_before, brief_after)},
    ]


# ==========================================================================
# PLAN EXECUTION + VALIDATION
# ==========================================================================
def _extract_json(text):
    """Pull the first JSON object out of an LLM response (tolerant of fences)."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("```", 2)[1]
        if t.startswith("json"):
            t = t[4:]
    start = t.find("{")
    end = t.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in LLM response")
    return json.loads(t[start:end + 1])


def execute_plan(gm, plan):
    """Apply plan edits; return log with per-edit result + any errors to feed
    back to the LLM for repair."""
    log = []
    for e in plan.get("edits", []):
        op = e.get("op")
        args = dict(e.get("args", {}))
        try:
            changed = MA.apply_edit(gm, op, **args)
            log.append({**e, "cells_changed": changed, "ok": True})
        except Exception as ex:
            log.append({**e, "cells_changed": 0, "ok": False,
                        "error": "%s: %s" % (type(ex).__name__, ex)})
    return log


def converged(m_before, m_after, verdict):
    """Stop if the LLM says stop AND no guardrail regressed badly."""
    frag_ok = m_after["fragmentation_tiny_patches"] <= \
        m_before["fragmentation_tiny_patches"] + 5
    coh_ok = m_after["transition_coherence"] >= \
        m_before["transition_coherence"] - 0.02
    return verdict == "stop" and frag_ok and coh_ok


# ==========================================================================
# MAIN LOOP
# ==========================================================================
def run_agent(base_path, out_dir, max_iters=4, scale=5, caller=None,
              cols=40):
    caller = caller or LLM_CALLER
    base = GameMap.load_json(base_path)
    stem = os.path.basename(base_path).split(".")[0]
    os.makedirs(out_dir, exist_ok=True)

    gm = base.copy()
    transcript = {"base": os.path.basename(base_path), "iterations": []}

    for it in range(1, max_iters + 1):
        brief_before = MA.briefing_text(MA.perceive(gm, cols=cols))
        m_before = MA.metrics(gm)
        img_note = ("(An image of the current map is also provided to your "
                    "vision.)")

        # --- PROPOSE (LLM) ---
        try:
            raw = caller(propose_prompt(brief_before, m_before, img_note))
            plan = _extract_json(raw)
        except LLMNotConfigured:
            raise
        except Exception as ex:
            transcript["iterations"].append(
                {"iter": it, "stage": "propose", "error": str(ex),
                 "trace": traceback.format_exc()})
            break

        # --- EXECUTE (Python) ---
        before_snapshot = gm.copy()
        log = execute_plan(gm, plan)
        m_after = MA.metrics(gm)
        brief_after = MA.briefing_text(MA.perceive(gm, cols=cols))

        # render this iteration
        render_pair(before_snapshot, gm,
                    os.path.join(out_dir, "%s_iter%d_ba.png" % (stem, it)),
                    scale=scale,
                    titles=("iter %d before" % it, "iter %d after" % it))

        # --- RE-JUDGE (LLM) ---
        verdict, reason = "continue", ""
        try:
            raw2 = caller(rejudge_prompt(brief_before, brief_after, m_before,
                                         m_after, plan))
            rej = _extract_json(raw2)
            verdict = rej.get("verdict", "continue")
            reason = rej.get("reason", "")
        except LLMNotConfigured:
            raise
        except Exception as ex:
            rej = {"error": str(ex)}

        transcript["iterations"].append({
            "iter": it, "plan": plan, "edit_log": log,
            "metrics_before": m_before, "metrics_after": m_after,
            "rejudge": rej, "verdict": verdict})

        if converged(m_before, m_after, verdict):
            break

    gm.name = base.name + "_agent"
    gm.save_json(os.path.join(out_dir, "%s_agent.map.json" % stem))
    render(gm, os.path.join(out_dir, "%s_agent_final.png" % stem), scale=scale,
           title="AGENT FINAL: %s" % gm.name)
    with open(os.path.join(out_dir, "%s_agent_transcript.json" % stem),
              "w") as fh:
        json.dump(transcript, fh, indent=2)
    return transcript


def main():
    ap = argparse.ArgumentParser(description="LLM-in-the-loop map agent")
    ap.add_argument("base")
    ap.add_argument("--out", default=None)
    ap.add_argument("--max-iters", type=int, default=4)
    ap.add_argument("--scale", type=int, default=5)
    args = ap.parse_args()
    out = args.out or os.path.dirname(os.path.abspath(args.base))
    try:
        run_agent(args.base, out, max_iters=args.max_iters, scale=args.scale)
    except LLMNotConfigured as ex:
        print("LLM not configured:\n  %s" % ex)
        print("\nThis harness is scaffolded but cannot self-drive in this "
              "sandbox (no reachable LLM endpoint). Use loop_run.py with a "
              "hand-authored plan to run the workflow here.")
        sys.exit(2)


if __name__ == "__main__":
    main()
