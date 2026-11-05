#!/usr/bin/env python3
"""selftest_fungalweevil_label.py — the fungal weevil carries its judged label.

WHY: FUNGALWEEVIL_LABEL_JUDGE_PROPOSES_NEW. The fungal weevil's label "grellik"
is a canon Star Wars proper name (a named nexu on Voss). A judge agent proposed
candidates, a second judge picked one; the verdict is committed at
infrastructure/state/delegated/2026-11-02/FUNGALWEEVIL_LABEL_JUDGE_PROPOSES_NEW.json.
This test holds the source to that verdict:

  1. the verdict holds 3-5 candidates, a pick among them, and the pick's verdict is KEEP;
  2. RM_Grellik in TheRot, ThingDef and PawnKindDef, carries the pick as <label>
     (parsed as XML elements; its SWBestiary twin RSW_FungalWeevil was deleted by
     BIOMES_PORT_PRUNE_FORTY_TWO_HITCHHIKERS);
  3. no <label> anywhere under src/ (nested and abstract included) still says "grellik";
  4. no other def under src/ uses the pick as its label or shares its four-letter
     stem in a label (the eggs, "<pick> egg (...)", are the twins' own);
  5. nor in the def dump (DUMP_ROOT/defs.sqlite, every mod incl. donors): no label
     uses the pick, no creature label shares its stem; a missing db fails UNMEASURED;
  6. a planted copy with the old label is caught (the instrument can see).

defNames (RM_Grellik, texture folders) are unchanged on purpose: renaming a defName
is alias work, and a defName is never shown to a player.
Exit 0 pass, 1 fail.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
VERDICT = os.path.join(REPO, "infrastructure", "state", "delegated", "2026-11-02",
                       "FUNGALWEEVIL_LABEL_JUDGE_PROPOSES_NEW.json")
TWINS = {
    "RM_Grellik": "src/RimMandrake/TheRot/Defs/Fauna/RM_TheRot_Fauna_ThingDefs_Races.xml",
}
OLD = "grellik"
# the twins' own eggs carry "<pick> egg (...)"; the SWBestiary eggs already say "fungal weevil"
EGGS = {"RM_EggFungalWeevilFertilized", "RM_EggFungalWeevilUnfertilized"}
EGG_FILE = "src/RimMandrake/TheRot/Defs/Fauna/RM_TheRot_Fauna_ThingDefs_Items.xml"


def twin_labels(path, defname):
    """{def tag: [label, ...]} for every top-level def named `defname` in `path`."""
    out = {}
    for el in ET.parse(path).getroot():
        if el.findtext("defName") == defname:
            out.setdefault(el.tag, []).append((el.findtext("label") or "").strip())
    return out


def src_labels():
    """[(file, owner, label)] for EVERY <label> element in every XML file under src/.

    `owner` is "<DefTag>/<defName>" of the top-level def holding it (abstract defs
    use their Name attribute), so a nested or abstract label is scanned too. A file
    that does not parse yields one row with label None, which label_findings fails."""
    rows = []
    for root, _dirs, files in os.walk(os.path.join(REPO, "src")):
        for f in files:
            if not f.endswith(".xml"):
                continue
            p = os.path.join(root, f)
            rel = os.path.relpath(p, REPO)
            try:
                top = ET.parse(p).getroot()
            except ET.ParseError:
                rows.append((rel, "?unparsed", None))   # a file we cannot read is a FAIL, never skipped
                continue
            for d in list(top) or [top]:
                owner = "%s/%s" % (d.tag, d.findtext("defName") or d.get("Name") or "?")
                for lab in d.iter("label"):
                    if lab.text and lab.text.strip():
                        rows.append((rel, owner, lab.text.strip().lower()))
    return rows


def label_findings(pick, rows):
    bad = []
    stem = pick[:4]
    # exemptions are (file, owner): a second copy of a twin in another file is checked like a stranger
    own = {(TWINS[d], "%s/%s" % (t, d)) for d in TWINS for t in ("ThingDef", "PawnKindDef")}
    own |= {(EGG_FILE, "ThingDef/" + e) for e in EGGS}
    for f, dn, lab in rows:
        if lab is None:
            bad.append("%s does not parse as XML: its labels are unseen" % f)
            continue
        if OLD in lab:
            bad.append("%s %s still labelled %r" % (f, dn, lab))
        if (f.replace(os.sep, "/"), dn) in own:
            continue
        words = re.findall(r"[a-z]+", lab)
        if pick in words or any(w[:4] == stem and len(w) >= 4 for w in words):
            bad.append("%s %s label %r collides with %r (word or 4-letter stem)" % (f, dn, lab, pick))
    return bad


def dump_findings(pick):
    """The pick against every label in the def dump (all mods, ours and donors).

    Exact label anywhere, or a 4-letter stem clash with a creature (race-bearing
    ThingDef/PawnKindDef) label, outside the twins and their eggs. Returns
    (findings, labels seen); an unreadable db is a finding, never a pass."""
    sys.path.insert(0, HERE)
    from game_paths import DUMP_ROOT
    db = os.path.join(DUMP_ROOT, "defs.sqlite")
    if not os.path.exists(db):
        return ["UNMEASURED: no def dump db at %s (run `measure build`)" % db], 0
    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    rows = con.execute("select def_type, def_name, lower(label), json "
                       "from defs where label is not null and label <> ''").fetchall()
    con.close()
    own = {(t, d) for d in TWINS for t in ("ThingDef", "PawnKindDef")} | {("ThingDef", e) for e in EGGS}
    bad = []
    for dtype, dn, lab, js in rows:
        if (dtype, dn) in own:
            continue
        is_creature = False
        if dtype in ("ThingDef", "PawnKindDef") and js and '"race"' in js:
            try:
                # the record keeps def fields under "fields" (label_collision_check reads it the same way)
                fields = json.loads(js).get("fields") or {}
                is_creature = bool(fields.get("race"))
            except (ValueError, AttributeError):
                is_creature = True                       # unreadable row: judge it, do not skip it
        words = re.findall(r"[a-z]+", lab)
        if lab == pick or pick in words:
            bad.append("dump %s %s label %r uses the pick" % (dtype, dn, lab))
        elif is_creature and any(w[:4] == pick[:4] for w in words if len(w) >= 4):
            bad.append("dump creature %s %s label %r shares the pick's stem" % (dtype, dn, lab))
    if len(rows) < 10000:
        bad.append("only %d labels in the dump db — it cannot see" % len(rows))
    return bad, len(rows)


def main():
    bad = []
    v = json.load(open(VERDICT, encoding="utf-8"))
    cands = [c["label"] for c in v["candidates"]]
    pick = v["pick"]
    if not 3 <= len(cands) <= 5:
        bad.append("verdict has %d candidates, not 3-5" % len(cands))
    if pick not in cands:
        bad.append("pick %r is not among the candidates %s" % (pick, cands))
    if not str(v["verdicts"].get(pick, "")).startswith("KEEP"):
        bad.append("the judge's verdict on the pick is not KEEP")
    if pick == OLD:
        bad.append("pick is the old label")
    for dn, rel in TWINS.items():
        labs = twin_labels(os.path.join(REPO, rel), dn)
        for tag in ("ThingDef", "PawnKindDef"):
            if labs.get(tag) != [pick]:
                bad.append("%s %s label is %r, not %r" % (rel, dn + "/" + tag, labs.get(tag), pick))
    rows = src_labels()
    if len(rows) < 1000:
        bad.append("only %d labels read under src/ — the scan is blind" % len(rows))
    bad += label_findings(pick, rows)
    # planted: the old label on a twin, and a stranger sharing the pick's stem, must both be caught
    planted = [("x.xml", "ThingDef/RM_Grellik", OLD),
               ("y.xml", "ThingDef/RM_Other", pick[:4] + "zz"),
               ("z.xml", "ThingDef/RM_OtherEgg", pick + " egg (fert.)"),
               ("w.xml", "ThingDef/RSW_FungalWeevil", pick[:4] + "yy"),
               ("v.xml", "?unparsed", None)]
    missed = [row for row in planted if not label_findings(pick, [row])]
    if missed:
        bad.append("planted cases not caught: %s" % missed)
    dbad, dn = dump_findings(pick)
    bad += dbad
    print("labels scanned: %d in src/, %d in the def dump; pick %r; candidates %s" % (len(rows), dn, pick, cands))
    for b in bad:
        print("FAIL " + b)
    print("PASS" if not bad else "FAIL (%d)" % len(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
