#!/usr/bin/env python3
"""selftest_xenotype_cut_spawnsets.py — VANILLA_XENOTYPE_CUT_SPAWNSETS_1 (slice 1 of the owner's
2026-10-03 cut-the-twelve ruling).

Against the offline def dump (post-inheritance), every FactionDef/PawnKindDef xenotypeSet entry naming
one of the cut xenotypes must be removed by a Remove op in Patches/XenotypeCut_SpawnSets.xml:
  * the eleven: any def, at top-level xenotypeSet/xenotypeChances (the op's xpath shape);
  * Sanguophage: only Empire_* pawnkinds (its own pawnkinds/faction are slice 2's call).
Red on: a reference the patch does not reach (other field path, missing op), a Remove not
wrapped in a Conditional (logs red on no match). UNMEASURED without a readable dump.
Sanity probe: the dump must show PirateWaster naming Waster. Mutants must go red.
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "RimMandrake" / "Utils"))
PATCH = HERE / "Patches" / "XenotypeCut_SpawnSets.xml"
ELEVEN = ["Dirtmole", "Genie", "Highmate", "Hussar", "Impid", "Neanderthal", "Pigskin", "Starjack",
          "VRESaurids_Saurid", "Waster", "Yttakin"]
SANG_KEEP = {"Sanguophage", "Sanguophage_Player"}


def patch_rules(xml_text):
    """-> ({xenotype: 'all'|'empire'}, [problems])"""
    rules, probs = {}, []
    root = ET.fromstring(xml_text.encode())
    for op in root.findall("Operation"):
        m = op.find("match")
        if op.get("Class") != "PatchOperationConditional" or m is None or m.get("Class") != "PatchOperationRemove":
            probs.append("an Operation is not Conditional>Remove: %s" % op.get("Class"))
            continue
        xp = (m.findtext("xpath") or "").strip()
        if xp != (op.findtext("xpath") or "").strip():
            probs.append("Conditional and Remove xpaths differ: %s" % xp)
        g = re.fullmatch(r"Defs/\*/xenotypeSet/xenotypeChances/(\w+)", xp)
        if g:
            rules[g.group(1)] = "all"
            continue
        g = re.fullmatch(r'Defs/PawnKindDef\[starts-with\(defName,"Empire_"\)\]/xenotypeSet/xenotypeChances/(\w+)', xp)
        if g:
            rules.setdefault(g.group(1), "empire")
            continue
        probs.append("unrecognised xpath: %s" % xp)
    return rules, probs


def dump_refs(rows_by_type):
    """[(defType, defName, path, xenotype)] for every structural mention of a cut xenotype."""
    cut = set(ELEVEN) | {"Sanguophage"}
    out = []
    for dt, rows in rows_by_type.items():
        for r in rows:
            f = r.get("fields") or {}
            xs = (f.get("xenotypeSet") or {}).get("xenotypeChances") or []
            for c in xs:
                if isinstance(c, dict) and c.get("xenotype") in cut:
                    out.append((dt, r["defName"], "xenotypeSet", c["xenotype"]))
            for k, v in f.items():
                if k != "xenotypeSet" and isinstance(v, dict) and "xenotypeChances" in v:
                    for c in v.get("xenotypeChances") or []:
                        if isinstance(c, dict) and c.get("xenotype") in cut:
                            out.append((dt, r["defName"], k, c["xenotype"]))
    return out


def uncovered(refs, rules):
    bad = []
    for dt, n, path, x in refs:
        if x == "Sanguophage" and n in SANG_KEEP:
            continue
        rule = rules.get(x)
        ok = path == "xenotypeSet" and (rule == "all" or (rule == "empire" and dt == "PawnKindDef" and n.startswith("Empire_")))
        if not ok:
            bad.append("%s %s %s.%s not removed" % (dt, n, path, x))
    return bad


def main():
    fails = []
    text = PATCH.read_text()
    rules, probs = patch_rules(text)
    fails += probs
    missing = [x for x in ELEVEN if rules.get(x) != "all"]
    if missing:
        fails.append("no all-defs Remove for %s" % missing)
    try:
        import game_paths as GP
        rows = {dt: json.load(open(os.path.join(GP.DEF_DUMP, "defs", dt + ".json")))["defs"]
                for dt in ("FactionDef", "PawnKindDef")}
    except Exception as e:
        print("UNMEASURED: no readable def dump: %s" % e)
        return 2
    refs = dump_refs(rows)
    # Sanity probe (can fail): the dump must show xenotypeSets at all -- PirateWaster with a non-empty set, and a
    # populated population of such rows. A dump captured AFTER our patch (load 14 onward) no longer names Waster there.
    waster_rows = [r for r in rows["FactionDef"] if r["defName"] == "PirateWaster"]
    sets = (((waster_rows[0].get("fields") or {}).get("xenotypeSet") or {}).get("xenotypeChances") or []) if waster_rows else []
    n_sets = sum(1 for rs in rows.values() for r in rs
                 if ((r.get("fields") or {}).get("xenotypeSet") or {}).get("xenotypeChances"))
    if not sets or n_sets < 100:
        print("UNMEASURED: sanity probe failed (PirateWaster xenotypeSet empty=%s, %d defs with a set; dump cannot see xenotypeSets)"
              % (not sets, n_sets))
        return 2
    post_patch = not any(x == "Waster" for _, n, _, x in refs if n == "PirateWaster")
    print("dump is %s our patch (PirateWaster %s Waster; %d xenotypeSet defs read)"
          % ("AFTER" if post_patch else "BEFORE", "no longer names" if post_patch else "still names", n_sets))
    bad = uncovered(refs, rules)
    print("%d cut-xenotype references in the dump; %d uncovered" % (len(refs), len(bad)))
    fails += bad
    if post_patch:
        # the dump is post-patch: any remaining reference (other than the two Sanguophage-keep kinds) means the patch
        # did not apply live -- stronger than the static coverage above
        leaks = [r for r in refs if not (r[3] == "Sanguophage" and r[1] in SANG_KEEP)]
        fails += ["live leak (patch did not remove): %s %s %s" % (r[0], r[1], r[3]) for r in leaks]
        mleak = [r for r in refs + [("PawnKindDef", "Pirate_Boss", "xenotypeSet", "Genie")] if not (r[3] == "Sanguophage" and r[1] in SANG_KEEP)]
        print("mutant leaked Genie in a post-patch dump: %s" % ("red" if mleak else "STAYED GREEN"))
        if not mleak:
            fails.append("mutant stayed green: post-patch leak")
    # mutants
    # injected Hussar reference: a post-patch dump no longer carries real ones, so the mutant brings its own
    m1 = uncovered(refs + [("PawnKindDef", "Pirate_X", "xenotypeSet", "Hussar")], {k: v for k, v in rules.items() if k != "Hussar"})
    m2 = uncovered(refs + [("PawnKindDef", "X", "someOtherSet", "Genie")], rules)
    m3 = patch_rules(text.replace('<match Class="PatchOperationRemove">', '<match Class="PatchOperationAdd">', 1))[1]
    m4 = uncovered(refs + [("PawnKindDef", "Pirate_Boss", "xenotypeSet", "Sanguophage")], rules)
    for name, res in (("Hussar op dropped", m1), ("reference on another field", m2),
                      ("Remove swapped for Add", m3), ("Sanguophage outside Empire", m4)):
        print("mutant %s: %s" % (name, "red" if res else "STAYED GREEN"))
        if not res:
            fails.append("mutant stayed green: " + name)
    print("FAIL" if fails else "PASS", *fails[:20], sep="\n  ")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
