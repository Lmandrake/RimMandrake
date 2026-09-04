#!/usr/bin/env python3
"""Generate the research retag patches from the frozen manifest.

Owner rulings 2026-09-04 (RESEARCH_TREE_NORMALIZATION_1 rulings block):
retag GO. Emits src/RimUtinni/ResearchRetag/Patches/RUT_ResearchRetag.xml
rewriting, for every SURVIVING manifest row that differs from the live dump:

  techLevel      -> the tier grammar's canonical level (only when the live
                    level is outside the tier's allowed set)
  baseCost       -> the manifest's re-costed value
  prerequisites  -> the manifest's joined prereq list, EXCLUDING RR_* entries
                    (Research Reinvented re-splices its techprint prereqs at
                    runtime; baking them into XML would double-write them)

Every def is wrapped in a PatchOperationConditional on the def node itself, so
a def that exists only at runtime (not in any mod XML) is skipped silently —
that skip is deliberate and counted in the generator's report, not a trap.
Field-level Conditionals use match=Replace / nomatch=Add because a def whose
XML omits the node (techLevel defaulting to Undefined) fails a bare Replace.

Run from repo root:  python3 design/Jawa/research_review/build_retag_patches.py
Then validate:       python3 skills/rimworld-modding/scripts/validate_patch.py \
                         src/RimUtinni/ResearchRetag/Patches/RUT_ResearchRetag.xml --defs <dump>
"""
import csv
import json
import os
from xml.sax.saxutils import escape

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MANIFEST = os.path.join(REPO, "infrastructure/output/research_manifest_draft.csv")
import sys as _sys
_sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
from game_paths import DUMP_ROOT as _DUMP_ROOT  # one-path seam: never a LocalLow literal
# Pinned to the capture the manifest was built against (its header fingerprint)
# on purpose - regenerating against a newer capture without re-deriving the
# manifest would patch against defs the manifest never saw.
CAP = os.path.join(_DUMP_ROOT, "captures", "2026-09-04T02-23-44Z")
OUT = os.path.join(REPO, "src/RimUtinni/ResearchRetag/Patches/RUT_ResearchRetag.xml")

TIER_TECHLEVELS = {  # mirror of research_manifest_validate.py, canonical first
    "T0": (["Neolithic"], {"Neolithic", "Medieval", "Industrial"}),
    "T1": (["Industrial"], {"Industrial"}),
    "T2": (["Industrial"], {"Industrial"}),
    "T3": (["Spacer"], {"Spacer"}),
    "T4": (["Ultra"], {"Ultra", "Archotech"}),
}
SURV = {"untouched", "keep", "reflavor"}


def field_patch(dn, node, value_xml, present):
    """One field, guarded: Replace when the node exists, Add when it does not."""
    base = 'Defs/ResearchProjectDef[defName="%s"]' % dn
    return """      <li Class="PatchOperationConditional">
        <xpath>%(base)s/%(node)s</xpath>
        <match Class="PatchOperationReplace">
          <xpath>%(base)s/%(node)s</xpath>
          <value>%(val)s</value>
        </match>
        <nomatch Class="PatchOperationAdd">
          <xpath>%(base)s</xpath>
          <value>%(val)s</value>
        </nomatch>
      </li>""" % {"base": base, "node": node, "val": value_xml}


def prereq_remove(dn):
    base = 'Defs/ResearchProjectDef[defName="%s"]' % dn
    return """      <li Class="PatchOperationConditional">
        <xpath>%(base)s/prerequisites</xpath>
        <match Class="PatchOperationRemove">
          <xpath>%(base)s/prerequisites</xpath>
        </match>
      </li>""" % {"base": base}


def main():
    with open(MANIFEST) as fh:
        fh.readline()
        man = {r["defName"]: r for r in csv.DictReader(fh)}
    D = json.load(open(os.path.join(CAP, "defs", "ResearchProjectDef.json"),
                       encoding="utf-8"))
    live = {d["defName"]: d for d in D["defs"]}

    blocks, n_tl, n_cost, n_pre = [], 0, 0, 0
    for dn in sorted(man):
        r = man[dn]
        if r["fate"] not in SURV or dn not in live:
            continue
        f = live[dn].get("fields") or {}
        ops = []

        canon, allowed = TIER_TECHLEVELS.get(r["tier"] or "", (None, None))
        live_tl = f.get("techLevel") or "Undefined"
        if canon and live_tl not in allowed:
            ops.append(field_patch(dn, "techLevel",
                                   "<techLevel>%s</techLevel>" % canon[0], True))
            n_tl += 1

        try:
            want_cost = float(r["cost"] or 0)
        except ValueError:
            want_cost = 0
        live_cost = float(f.get("baseCost") or 0)
        if want_cost and abs(want_cost - live_cost) > 0.01:
            ops.append(field_patch(dn, "baseCost",
                                   "<baseCost>%g</baseCost>" % want_cost, True))
            n_cost += 1

        want_pre = [p for p in (r["prereqs"] or "").split(";")
                    if p and not p.startswith("RR_")]
        live_pre = [p for p in (f.get("prerequisites") or [])
                    if not str(p).startswith("RR_")]
        if sorted(want_pre) != sorted(live_pre):
            if want_pre:
                val = ("<prerequisites>%s</prerequisites>"
                       % "".join("<li>%s</li>" % escape(p) for p in want_pre))
                ops.append(field_patch(dn, "prerequisites", val, True))
            else:
                ops.append(prereq_remove(dn))
            n_pre += 1

        if not ops:
            continue
        blocks.append("""  <Operation Class="PatchOperationConditional">
    <xpath>Defs/ResearchProjectDef[defName="%s"]</xpath>
    <match Class="PatchOperationSequence">
      <operations>
%s
      </operations>
    </match>
  </Operation>""" % (dn, "\n".join(ops)))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<Patch>\n")
        fh.write("  <!-- GENERATED by design/Jawa/research_review/build_retag_patches.py\n"
                 "       from research_manifest_draft.csv (frozen deck). Do not hand-edit;\n"
                 "       change the manifest and regenerate. -->\n")
        fh.write("\n".join(blocks))
        fh.write("\n</Patch>\n")
    print("wrote %s: %d defs patched (%d techLevel, %d baseCost, %d prereq lists)"
          % (OUT, len(blocks), n_tl, n_cost, n_pre))


if __name__ == "__main__":
    main()
