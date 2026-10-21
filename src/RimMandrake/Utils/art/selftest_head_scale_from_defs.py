#!/usr/bin/env python3
"""Selftest: recompute every painted species' size and head scale FROM THE DEFS and hold head_envelope.json to it.

Owner card 2026-10-20 ("How should head sizes be set?" -> "Tune in the def"): the on-screen skull is set by a
SM_HeadSize_Cosmetic statOffset on the species' head gene, the art stays in the canvas frame (ratio 1.0). So for
each species in head_envelope.json species_render, from source (species_size.py: xenotype genes after
BodySizeIsReal.xml, gene statOffsets, Big and Small's head rule):
  - size_offset, head_size_multiplier and engine_head_scale match the defs;
  - engine_head_scale is the on-screen target (art at canvas 1.0 => on screen = engine scale), within 0.01;
  - Big and Small frame offsets in species_size.BS_FRAMES agree with the live def dump (UNMEASURED if absent).
Sanity probe: a wrong multiplier in a copy of the table is caught.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import fit_head_canvas as F  # noqa: E402
import species_size as S  # noqa: E402

XENO = {"Lasat": "RSW_RimMandrakeLasat", "Mimbanese": "RSW_RimMandrakeMimbanese",
        "Nelvaanian": "RSW_RimMandrakeNelvaanian", "Ortolan": "RSW_RimMandrakeOrtolan"}
HEAD_GENE = {sp: "RSW_%sHead" % sp for sp in XENO}

fails = 0


def check(ok, what, detail=None):
    global fails
    print(("PASS " if ok else "FAIL ") + what + ("" if ok or detail is None else "  -> %r" % (detail,)))
    if not ok:
        fails += 1


def disagreements(sr, xen, ours):
    out = []
    for sp, x in XENO.items():
        r = sr.get(sp)
        if r is None or x not in xen:
            out.append((sp, "missing", r is None, x in xen))
            continue
        if HEAD_GENE[sp] not in xen[x]:
            out.append((sp, "xenotype lacks " + HEAD_GENE[sp]))
        got = S.size_of(xen[x], ours)
        for key, val in (("size_offset", got["render_offset"]), ("head_size_multiplier", got["head_mult"]),
                         ("engine_head_scale", got["head_render"])):
            if abs(r.get(key, 1.0 if key == "head_size_multiplier" else -9) - val) > 0.002:
                out.append((sp, key, r.get(key), val))
        t = r.get("onscreen_skull_target")
        if t is None or abs(t - got["head_render"]) > 0.01:
            out.append((sp, "on-screen target vs engine scale (art is canvas 1.0)", t, got["head_render"]))
    return out


env = F.load_envelope()
sr = env["species_render"]
xen = S.patched_xenotypes()
ours = S.our_gene_stats()
for sp, x in XENO.items():
    if x in xen:
        g = S.size_of(xen[x], ours)
        print("     %-10s real size %.2f  render offset %+.2f  head rule x%.3f  mult %.2f  on screen x%.3f"
              % (sp, g["mech_size"], g["render_offset"], g["head_render"] / g["head_mult"], g["head_mult"],
                 g["head_render"]))
bad = disagreements(sr, xen, ours)
check(not bad, "head_envelope.json species_render matches the defs (size, head multiplier, engine scale = target)",
      bad)

check("HalfJotunFrame" in xen.get(XENO["Lasat"], []), "sanity: BodySizeIsReal.xml applied (Lasat carries HalfJotunFrame)")
check(abs(F.bs_render_size(0.75)[1] - 1.369) < 0.002, "sanity: B&S head rule gives x1.369 at +0.75")

wrong = json.loads(json.dumps(sr))
wrong["Lasat"]["head_size_multiplier"] = 1.0
wrong["Lasat"]["engine_head_scale"] = 1.369
check(any(d[0] == "Lasat" for d in disagreements(wrong, xen, ours)), "sanity: a table that ignores the def multiplier is caught")

frames = S.check_frames_against_dump()
if frames is None:
    print("UNMEASURED: no live def dump reachable; BS_FRAMES not cross-checked")
else:
    check(not frames, "species_size.BS_FRAMES agrees with the live def dump", frames)

print("OK: 0 failure(s)" if not fails else "FAILED: %d failure(s)" % fails)
sys.exit(1 if fails else 0)
