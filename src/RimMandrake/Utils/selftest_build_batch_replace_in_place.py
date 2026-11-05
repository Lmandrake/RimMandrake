#!/usr/bin/env python3
"""Selftest: jawa/build_batch really removes the thing it reports replacing (BUILDBATCH_FIX_REPLACE_LEAVES_OLD_THING).

The defect: build_batch with wipeExisting=true over an unowned RM_Ladder reported displaced[] 'destroyed RM_Ladder,
sameDefReplacedInPlace' while the old ladder stayed spawned beside the new one. GenSpawn.Spawn wipes only what
GenSpawn.SpawningWipes allows, and two NON-EDIFICE buildings of one def (RM_Ladder has isEdifice=false) never wipe
each other; the tool wrote its displaced row before the spawn, on the assumption that they did.

The engine half is the live proof (prove_build_batch_replace.py, clause A1). This test pins the source shape of
BuildBatch in JawaBenchMapTools.cs, read as text, no game, no build:
  1. a same-def-at-same-cell thing is Destroy()ed by the tool itself BEFORE GenSpawn.Spawn;
  2. wipeExisting=false refuses that replacement (it used to place a duplicate);
  3. every displaced[] row is written AFTER GenSpawn.Spawn and only under a Destroyed check, and a survivor is a
     failure naming its ThingID;
  4. the `placedByThisBatch` flag is taken before anything dies (spawnedThings.Contains still answers).
Each check is also run against a copy of the source with the fix reverted, so a check that cannot fail is caught.
Run: python3 src/RimMandrake/Utils/selftest_build_batch_replace_in_place.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "bridgetools", "JawaBench.BridgeTools", "JawaBenchMapTools.cs")


def build_batch_body(text):
    """The BuildBatch method's text, from its signature to the next [Tool( attribute."""
    i = text.find("public static async Task<object> BuildBatch(")
    if i < 0:
        return None
    j = text.find("[Tool(", i)
    return text[i:j if j > 0 else len(text)]


def strip_comments(body):
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", ln) for ln in body.splitlines())


def checks(body):
    """[(name, ok, detail)] over BuildBatch's code (comments removed)."""
    code = strip_comments(body)
    out = []
    spawn = code.find("GenSpawn.Spawn(t, c, map, rot)")
    out.append(("spawn call found", spawn > 0, "GenSpawn.Spawn(t, c, map, rot)"))
    m = re.search(r"foreach\s*\(var (\w+) in replacedInPlace\)\s*if\s*\(!\1\.Destroyed\)\s*\1\.Destroy\(DestroyMode\.Vanish\)", code)
    out.append(("same-def thing destroyed by the tool", bool(m), "Destroy(DestroyMode.Vanish) over replacedInPlace"))
    out.append(("... and before the spawn", bool(m) and spawn > 0 and m.start() < spawn, "destroy precedes GenSpawn.Spawn"))
    r = re.search(r"if\s*\(replacedInPlace\.Count\s*>\s*0\s*&&\s*!wipeExisting\)\s*\{.{0,600}?failures\.Add.{0,600}?continue;", code, flags=re.S)
    out.append(("wipeExisting=false refuses a same-def replacement", bool(r), "refusal + continue"))
    adds = [a.start() for a in re.finditer(r"displaced\.Add\(", code)]
    out.append(("displaced rows exist", bool(adds), "%d displaced.Add" % len(adds)))
    out.append(("every displaced row is written after the spawn", bool(adds) and spawn > 0 and all(a > spawn for a in adds),
                "displaced.Add offsets %s vs spawn %d" % (adds, spawn)))
    guarded = bool(adds)
    for a in adds:
        before = code[max(0, a - 200):a]
        if not re.search(r"if\s*\(\s*\w+\.Destroyed\s*\)\s*$", before.rstrip()):
            guarded = False
    out.append(("every displaced row is under a Destroyed check", guarded, "if (d.Destroyed) displaced.Add"))
    out.append(("a survivor is a failure naming its ThingID", bool(re.search(r"still spawned beside the new thing", code))
                and "d.ThingID" in code, "failures.Add(... still spawned ...)"))
    pb = code.find("victimsPlacedHere")
    out.append(("placedByThisBatch taken before anything dies", pb > 0 and m is not None and pb < m.start(),
                "victimsPlacedHere computed before the destroy"))
    return out


def reverted(body):
    """The fix undone, the way the defect looked: no explicit destroy, no refusal, rows written before the spawn."""
    b = re.sub(r"foreach\s*\(var (\w+) in replacedInPlace\)\s*if\s*\(!\1\.Destroyed\)\s*\1\.Destroy\(DestroyMode\.Vanish\);", "", body)
    b = re.sub(r"if\s*\(replacedInPlace\.Count\s*>\s*0\s*&&\s*!wipeExisting\)", "if (false)", b)
    b = b.replace("if (d.Destroyed)\n", "\n")
    return b


def main():
    if not os.path.isfile(SRC):
        print("FAIL source absent: %s" % SRC)
        return 1
    with open(SRC, encoding="utf-8") as f:
        body = build_batch_body(f.read())
    if not body:
        print("FAIL BuildBatch not found in %s" % SRC)
        return 1
    bad = 0
    for name, ok, detail in checks(body):
        print(("ok   " if ok else "FAIL ") + name + " (" + detail + ")")
        bad += 0 if ok else 1
    # Sanity probe: the checks must be able to see the defect.
    rv = {n: ok for n, ok, _ in checks(reverted(body))}
    must_fail = ["same-def thing destroyed by the tool", "wipeExisting=false refuses a same-def replacement",
                 "every displaced row is under a Destroyed check"]
    for n in must_fail:
        if rv.get(n):
            print("FAIL sanity: check %r still passes with the fix reverted" % n)
            bad += 1
        else:
            print("ok   sanity: %r fails on the reverted source" % n)
    print("build_batch replace-in-place: %s" % ("FAIL (%d)" % bad if bad else "all passed"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
