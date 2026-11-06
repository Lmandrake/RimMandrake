#!/usr/bin/env python3
"""selftest_gss_shock_outlives_wire.py: offline proof for GSS_FALLEN_WIRE_FIX_SHOCK_OUTLIVES_WIRE.

The item: colonists were downed by fallen-wire shock beside a lone mast while "the aerial census showed 0 links and 0 fallen
wires" (2026-10-29 theft day phase). That reading came from a scratch probe that read top-level census keys `links` and
`fallen`; AerialProbe.Census never emitted them (it has anchors[].links / anchors[].fallen, spansUp, fallenCords), so the
probe would have read 0/0 next to any wire. The hotspot sat on proof_all's M14b/M15 debris (fallen cords toward (104,185) and
(110,185)). The fix is the instrument that was missing: the census now reports the shock contacts themselves (shockCells,
shockCellList) and how many of them a rebuild from the map as it stands would not produce (shockOrphans: a shock that
outlived its wire), and validation_aerial row M20e removes a live fallen wire's mast and proves the shock cells go with it.

Checks here (no game): the M20e verdict on PASS, every FAIL shape and both UNMEASURED shapes; the census / audit / row
wiring in the source; the committed DLL's stamp covering the sources as they stand. Exit 0 = all pass.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "northstar"))

import validation_aerial as VA  # noqa: E402

FAILS = []


def check(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok:
        FAILS.append(name)


SITE = (10, 10, 30, 14)
TIP = (20, 15)


def census(cells, orphans=0):
    return {"success": True, "shockCells": len(cells), "shockOrphans": orphans, "shockCellList": [list(c) for c in cells]}


def trial(shocked=False, error=None):
    return {"error": error} if error else {"id": "Muffalo1", "shocked": shocked, "dead": False, "start": TIP, "end": TIP}


wire = [(18, 15), (19, 15), TIP]
v = VA.shock_outlives_verdict

# 1. the verdict
check("1 PASS: wire removed, no cell on site, no orphan, animal unshocked",
      v(census(wire), census([]), trial(), TIP, SITE)[:2] == ("PASS", "MOD"))
check("1 PASS: another site's shock cells (proof debris elsewhere on the map) do not count",
      v(census(wire + [(104, 185)]), census([(104, 185)]), trial(), TIP, SITE)[:2] == ("PASS", "MOD"))
check("1 FAIL: a shock cell left on the site after its wire went",
      v(census(wire), census([TIP], orphans=1), trial(), TIP, SITE)[:2] == ("FAIL", "MOD"))
check("1 FAIL: an orphan left even when the cell list is off-site",
      v(census(wire), census([(104, 185)], orphans=1), trial(), TIP, SITE)[:2] == ("FAIL", "MOD"))
check("1 FAIL: an orphan already before the removal",
      v(census(wire, orphans=1), census([]), trial(), TIP, SITE)[:2] == ("FAIL", "MOD"))
check("1 FAIL: the animal on the old tip was shocked",
      v(census(wire), census([]), trial(shocked=True), TIP, SITE)[:2] == ("FAIL", "MOD"))
check("1 FAIL: a trial that read no shocked field is not a pass",
      v(census(wire), census([]), {"id": "x"}, TIP, SITE)[:2] == ("FAIL", "MOD"))
check("1 UNMEASURED SITE: census without shock fields (old DLL)",
      v({"success": True, "fallenCords": 1}, census([]), trial(), TIP, SITE)[:2] == ("UNMEASURED", "SITE"))
check("1 UNMEASURED SITE: the live half made no shock cell on its tip",
      v(census([(18, 15)]), census([]), trial(), TIP, SITE)[:2] == ("UNMEASURED", "SITE"))
check("1 UNMEASURED HARNESS: the trial animal never ran",
      v(census(wire), census([]), trial(error="spawn_pawn gave no pawn"), TIP, SITE)[:2] == ("UNMEASURED", "HARNESS"))

# 2. the blind reading that filed the item: a census holding a live fallen wire has NO top-level links/fallen keys
blind = {"success": True, "anchors": [{"id": 1, "x": 104, "z": 185, "links": [], "fallen": [{"tip": [106.2, 185.4]}]}],
         "fallenCords": 1}
check("2 the 2026-10-29 probe's keys read 0/0 on a census that holds a fallen cord",
      len(blind.get("links") or []) == 0 and len(blind.get("fallen") or []) == 0 and blind["fallenCords"] == 1)


def src(rel):
    with open(os.path.join(HERE, rel), encoding="utf-8") as f:
        return f.read()


probe = src("Source/Aerial/AerialProbe.cs")
comp = src("Source/Aerial/RM_MapComponent_Aerial.cs")
va = src("validation_aerial.py")
pa = src("northstar/proof_all.py")

# 3. wiring
check("3 census emits shockCells, shockOrphans, shockCellsFresh, externalContacts, shockCellList",
      all(('\\"%s\\":' % k) in probe for k in ("shockCells", "shockOrphans", "shockCellsFresh", "externalContacts", "shockCellList")))
check("3 census reads the audit", "comp.ShockCellAudit()" in probe)
i = comp.find("ShockCellAudit()")
body = comp[i:comp.find("\n        }\n", i)]
check("3 the audit rebuilds into scratch collections, never the live contacts",
      "RebuildContacts(this, map, freshCells, freshTips)" in body and "RebuildContacts(this, map, shockCells" not in body)
check("3 the audit counts a cached cell the fresh rebuild lacks as an orphan",
      "if (!freshCells.ContainsKey(k)) orphans++;" in body)
check("3 the audit restores the live rebuild's externalContacts reading", "RM_FallenWireShock.externalContacts = ext;" in body)
check("3 flips_block records M20e through the verdict",
      '"M20e_shock_cells_die_with_wire"' in va and "shock_outlives_verdict(before, after, gone, tip, FSITE)" in va)
j = va.find("# M20e GSS_FALLEN_WIRE_FIX_SHOCK_OUTLIVES_WIRE")
seg = va[j:va.find("V.row(rows, \"M20e_shock_cells_die_with_wire\"", j)]
check("3 M20e removes F1 between the two census reads",
      seg.find('before = B.ap("census")') < seg.find('rects="%d,%d,1,1" % F1') < seg.find('after = B.ap("census")'))
check("3 proof_all declares M20e", '"M20e_shock_cells_die_with_wire"' in pa)

# 4. the committed DLL was built from these sources (its .srchash lists each Compile item's sha256)
stamp = src("Assemblies/RimMandrakeGimmeSomeSlack.dll.srchash")
for rel in ("Aerial/AerialProbe.cs", "Aerial/RM_MapComponent_Aerial.cs", "Aerial/RM_FallenWireShock.cs"):
    with open(os.path.join(HERE, "Source", rel), "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()
    check("4 stamp covers %s as it stands" % rel, ("%s %s" % (h, rel)) in stamp.splitlines())
with open(os.path.join(HERE, "Assemblies", "RimMandrakeGimmeSomeSlack.dll"), "rb") as f:
    dh = hashlib.sha256(f.read()).hexdigest()
check("4 stamp's # dll: line is the committed DLL's bytes", ("# dll: " + dh) in stamp.splitlines())

print("\nALL PASS" if not FAILS else "\n%d FAILED: %s" % (len(FAILS), FAILS))
sys.exit(1 if FAILS else 0)
