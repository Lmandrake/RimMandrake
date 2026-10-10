#!/usr/bin/env python3
"""modaudit/facts_delta.py - which stage-1 assessor verdicts/severities a facts regeneration would change.

    python3 src/RimMandrake/Utils/modaudit/facts_delta.py --before <old mod_facts.jsonl>   # writes FACTS_REGEN_DELTA.md

Compares old vs new facts per mod, joins assessments/batch_NN.jsonl (verdict, problems, retirement_cost, source) and
FLAGS rows by rule. It never re-assesses: each row names the rule that fires and the fact that moved.
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from universe import FACTS_DIR  # noqa: E402

AUDIT = os.path.dirname(FACTS_DIR)
OUT = os.path.join(AUDIT, "FACTS_REGEN_DELTA.md")
SHORT = {"KEEP": "KEEP", "KEEP-TEMPORARILY-THEN-PHASE-OUT": "PHASE-OUT", "ELIMINATE-COMPLETELY": "ELIMINATE",
         "REPLACE-NOW-WITH-OUR-OWN": "REPLACE"}


def band(mb):
    """RUBRIC §3 memory severity from texture_decoded_mb_est. Pure."""
    if mb is None:
        return "U"
    return 1 if mb < 50 else (2 if mb <= 250 else 3)


def load(p):
    return {r["packageId"]: r for r in (json.loads(l) for l in open(p) if l.strip())}


def dep_str(det, verdicts, n=3):
    out = []
    for x in det[:n]:
        v = SHORT.get(verdicts.get(x["packageId"], ""), "?")
        out.append("%s (%s; %s)" % (x["packageId"], "+".join(x["kinds"]), v))
    if len(det) > n:
        out.append("+%d more" % (len(det) - n))
    return ", ".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True)
    a = ap.parse_args(argv)
    old, new = load(a.before), load(os.path.join(FACTS_DIR, "mod_facts.jsonl"))
    asm = {}
    for f in sorted(glob.glob(os.path.join(AUDIT, "assessments", "batch_[0-9][0-9].jsonl"))):
        for r in load(f).values():
            asm[r["packageId"]] = r
    verdicts = {k: v.get("verdict") for k, v in asm.items()}
    rules = {k: [] for k in ("R1", "R2", "R3", "R4", "R5", "R6")}
    for pid, n in sorted(new.items()):
        o, s = old.get(pid) or {}, asm.get(pid)
        if not s:
            continue
        v = SHORT.get(s.get("verdict"), s.get("verdict"))
        b = "%02d" % s.get("batch", 0)
        det = n.get("dependants_detail") or []
        olddeps = set(o.get("dependants") or [])
        newsrc = [x for x in det if x["packageId"] not in olddeps]
        # R1: retire-type verdict whose dependants are now non-empty (beyond old), or include a KEEP mod
        if v in ("ELIMINATE", "PHASE-OUT", "REPLACE") and newsrc:
            keep = [x for x in det if verdicts.get(x["packageId"]) == "KEEP"]
            imp = ("breaks %d KEEP dependant(s)" % len(keep)) if keep else "list in retirement_cost"
            if v == "ELIMINATE" or keep:
                rules["R1"].append((pid, b, v, "%d -> %d: %s" % (len(olddeps), len(det), dep_str(newsrc, verdicts)), imp))
        # R2: our mods depend on it but the assessor's retirement_cost.dependants misses them
        rc = set(((s.get("retirement_cost") or {}).get("dependants") or [])) if isinstance(
            (s.get("retirement_cost") or {}).get("dependants"), list) else set()
        ours_missing = [x for x in n.get("dependants_ours") or [] if x not in rc]
        if v != "KEEP" and ours_missing and not (rules["R1"] and rules["R1"][-1][0] == pid):
            rules["R2"].append((pid, b, v, "ours: %s" % dep_str([x for x in det if x["packageId"] in ours_missing], verdicts, 2),
                                "add to retirement_cost"))
        # R3: memory band moves with the Textures-only figure
        ob, nb = band(o.get("texture_decoded_mb_est")), band(n.get("texture_decoded_mb_est"))
        sev = [p.get("severity") for p in s.get("problems") or [] if p.get("kind") == "memory"]
        if ob != nb and sev and sev[0] != nb:
            rules["R3"].append((pid, b, v, "%s -> %s MB (band %s -> %s; assessor severity %s)" % (
                o.get("texture_decoded_mb_est"), n.get("texture_decoded_mb_est"), ob, nb, sev[0] if sev else "none"),
                "memory severity should be %s" % nb))
        # R4: source changed, rejected, or downgraded
        su = (s.get("source") or {}).get("url")
        if (o.get("source_url"), o.get("source_confidence")) != (n.get("source_url"), n.get("source_confidence")) or \
                n.get("source_rejected"):
            if o.get("source_url") != n.get("source_url") or o.get("source_confidence") != n.get("source_confidence"):
                rules["R4"].append((pid, b, v, "%s %s %s -> %s %s %s" % (
                    o.get("source_kind"), o.get("source_confidence"), o.get("source_url"),
                    n.get("source_kind"), n.get("source_confidence"), n.get("source_url")),
                    "assessor used %s (available=%s); rejected: %s" % (su, (s.get("source") or {}).get("available"),
                                                                       ", ".join(n.get("source_rejected") or []) or "-")))
        # R5: Cherry Picker shell
        if n.get("cherry_picker_shell") or (n.get("cherry_picker_cut_defs") or 0) >= 0.5 * max(n.get("def_total") or 0, 1) \
                and (n.get("cherry_picker_cut_defs") or 0) >= 10:
            rules["R5"].append((pid, b, v, "%d of %d defs cut; shell=%s" % (n.get("cherry_picker_cut_defs"), n.get("def_total"),
                                                                           n.get("cherry_picker_shell")),
                                "KEEP of a shell: what does it still supply?" if v == "KEEP" and n.get("cherry_picker_shell")
                                else ("content is mostly cut: the 'adds' line overstates it" if v == "KEEP" else "consistent")))
        # R6: Defs outside the loaded dirs
        if n.get("defs_outside_loaded_dirs"):
            rules["R6"].append((pid, b, v, "%d Defs XML in %s (census counted %d defs)" % (
                n.get("defs_xml_files_outside_loaded"), ", ".join(n["defs_outside_loaded_dirs"][:4]) +
                (" +%d" % (len(n["defs_outside_loaded_dirs"]) - 4) if len(n["defs_outside_loaded_dirs"]) > 4 else ""),
                n.get("def_total")), "gated compat defs: census undercounts"))
    titles = {
        "R1": "ELIMINATE (any new dependant) or PHASE-OUT/REPLACE (a KEEP dependant) whose dependants, all kinds, are now non-empty",
        "R2": "Non-KEEP rows (not already in R1) where a mod of ours depends on it but `retirement_cost.dependants` omits it",
        "R3": "Memory band moves (RUBRIC §3: <50 / 50-250 / >250 MB) with the Textures-only figure AND the assessor's memory severity differs from the new band",
        "R4": "Source changed: candidate REJECTED, NOT_FOUND no longer available, or fallen through",
        "R5": "Cherry Picker: shell (>= 90% of player-facing defs cut) or >= half of all defs cut",
        "R6": "Defs XML outside the dirs the 1.6 load set reads (not older version folders)",
    }
    lines = ["# Facts regeneration delta (2026-10-10)", "",
             "Generated by `src/RimMandrake/Utils/modaudit/facts_delta.py`: old facts (stage-0 `mod_facts.jsonl`, before this "
             "regeneration) vs the regenerated `facts/mod_facts.jsonl`, joined with `assessments/batch_NN.jsonl`. "
             "**Nothing is re-assessed here**: each row is a flag with the rule that fires. Kinds in dependants: "
             "hard_dep, hard_dep_v1.6, load_after, patch_xpath, findmod, mayrequire, class_ref, def_ref (def_ref is a "
             "CANDIDATE name match). The verdict after each dependant is that dependant's own assessor verdict.", "",
             "| rule | rows flagged | what |", "|---|---|---|"]
    for k in rules:
        lines.append("| %s | %d | %s |" % (k, len(rules[k]), titles[k]))
    lines.append("")
    for k, rows in rules.items():
        lines += ["## %s: %s" % (k, titles[k]), "", "| packageId | batch | verdict | old -> new fact | implication |",
                  "|---|---|---|---|---|"]
        for r in rows:
            cells = [str(x).replace("|", "/") for x in r]
            cells[3:] = [c if len(c) <= 170 else c[:167] + "..." for c in cells[3:]]
            lines.append("| `%s` | %s | %s | %s | %s |" % tuple(cells))
        lines.append("")
    open(OUT, "w").write("\n".join(lines))
    print("facts_delta: %s -> %s (%d bytes)" % ({k: len(v) for k, v in rules.items()}, OUT, os.path.getsize(OUT)))


if __name__ == "__main__":
    main()
