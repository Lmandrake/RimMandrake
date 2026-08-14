#!/usr/bin/env python3
"""Which wreck props can the clan actually STRIP, and what do they return?

VISION's ground-hulk arc: the clan lives in the wreck, builds into its dead
sections, and strips it for steel over years — high total yield, poor rate, never
regrows. When it is stripped, nothing holds them to the tile and they fly.

🔴 A prop that can only be removed by BLOWING IT UP breaks that arc. And the bad
ones are indistinguishable from the good ones in a mod's texture folder — the
difference only shows up when a colonist refuses the job. So this script splits
the ruins kit into a salvage list and a do-not-place list, from the LIVE merged
def state rather than from the shipped XML.

The two shipped removal routes are different and both matter:
  DECONSTRUCT  -> returns costList * resourcesFractionWhenDeconstructed
                  (RimWorld's default fraction is 0.5 when unset)
  DESTROY      -> returns killedLeavings, and only if leaveResourcesWhenKilled
                  has not been turned off

`building.deconstructible == False` is the killer: that is
NonDeconstructibleAncientBuildingBase, and such a prop can only be removed with
explosives.

Run: python3 design/Jawa/art/scan_salvage.py
Writes: salvage_palette.tsv beside this file. Derived + expiring -> gitignored.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scan_graphics import stream_objects, DUMP          # noqa: E402  (same 850 MB stream)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "salvage_palette.tsv")

# What counts as wreckage for this pass. Deliberately wide; filtered when read.
KW = ("ancient", "slag", "chunk", "rubble", "debris", "wreck", "ruin", "scrap",
      "junk", "broken", "damaged", "destroyed", "busted", "rusted", "crashed",
      "derelict", "hulk", "shipchunk", "collapsed")

COLS = ["defName", "modName", "label", "size", "graphicClass", "deconstructible",
        "alwaysDeconstructible", "claimable", "isEdifice", "passability",
        "fraction", "costList", "killedLeavings", "leaveResourcesWhenKilled",
        "designationCategory", "texPath"]


def counts(v):
    """Render a costList / killedLeavings list as 'Steel x4, Component x1'."""
    if not isinstance(v, list):
        return ""
    out = []
    for it in v:
        if isinstance(it, dict):
            out.append("%s x%s" % (it.get("thingDef"), it.get("count")))
    return ", ".join(out)


def main():
    rows = []
    for raw in stream_objects(DUMP):
        low = raw[:4000].lower()
        if not any(k in low for k in KW):
            continue
        try:
            d = json.loads(raw)
        except Exception:
            continue
        dn = d.get("defName", "")
        if dn.startswith(("Blueprint_", "Frame_")):
            continue
        blob = (dn + " " + (d.get("label") or "")).lower()
        if not any(k in blob for k in KW):
            continue
        f = d.get("fields") or {}
        if f.get("category") not in ("Building", "Item"):
            continue
        b = f.get("building") or {}
        gd = f.get("graphicData") or {}
        sz = f.get("size")
        if isinstance(sz, dict):
            sz = "%sx%s" % (sz.get("x"), sz.get("z"))
        rows.append({
            "defName": dn,
            "modName": d.get("modName", ""),
            "label": d.get("label", ""),
            "size": sz or "1x1",
            "graphicClass": gd.get("graphicClass", ""),
            # unset means inherit RimWorld's default of True
            "deconstructible": b.get("deconstructible", "(default True)"),
            "alwaysDeconstructible": b.get("alwaysDeconstructible", ""),
            "claimable": b.get("claimable", ""),
            "isEdifice": b.get("isEdifice", ""),
            "passability": f.get("passability", ""),
            "fraction": f.get("resourcesFractionWhenDeconstructed", "(default 0.5)"),
            "costList": counts(f.get("costList")),
            "killedLeavings": counts(f.get("killedLeavings")),
            "leaveResourcesWhenKilled": f.get("leaveResourcesWhenKilled", ""),
            "designationCategory": f.get("designationCategory") or "",
            "texPath": gd.get("texPath", ""),
        })

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\t".join(COLS) + "\n")
        for r in rows:
            fh.write("\t".join(str(r[c]).replace("\t", " ") for c in COLS) + "\n")

    bad = [r for r in rows if r["deconstructible"] is False]
    print("wreck-ish defs: %d | NOT deconstructible: %d -> %s"
          % (len(rows), len(bad), OUT), file=sys.stderr)


if __name__ == "__main__":
    main()
