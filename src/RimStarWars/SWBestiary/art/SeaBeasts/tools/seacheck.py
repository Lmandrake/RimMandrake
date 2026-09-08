#!/usr/bin/env python3
"""seacheck.py — grade a whole Graphic_Multi facing SET, offline.

validate_sprite.py grades a candidate against a reference sibling. A new
creature has no prior sprite, so the reference-relative half of that gate does
not apply; the ABSOLUTE half still does, and this runs exactly those checks by
importing validate_sprite's own measure() and constants (thresholds stay in one
place; this file owns none of them).

It then adds the check a per-file validator structurally cannot make: the four
facings must be one canvas and one animal size. Graphic_Multi failures are
silent - a missing or mis-scaled facing renders nothing or renders wrong, and
magenta never fires.

    python3 seacheck.py src/RimStarWars/SeaBeasts/art/final/CrimsonOpee

Exit 0 all clear (warnings allowed), 1 any REJECT, 2 the set is incomplete.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, "/mnt/d/Luke/dev/Rimworld/skills/generating-rimworld-sprites/scripts")
import validate_sprite as V  # noqa: E402

FACINGS = ("south", "east", "north", "west")
# Facings of one creature are scaled to a common long axis by seafit.py, so
# they must agree exactly; 2% absorbs integer rounding on the paste only.
SET_SPAN_TOLERANCE = 0.02


def absolute_findings(s: dict) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []

    def add(level, msg):
        out.append((level, msg))

    if not s["has_alpha"]:
        add(V.REJECT, "no alpha channel - renders as an opaque block.")
    hot = [i for i, a in enumerate(s["corners"]) if a > V.CORNER_MAX_ALPHA]
    if hot:
        add(V.REJECT, f"{len(hot)} of 4 corners opaque - key not fully removed.")

    fringe_frac = s["fringe"] / s["n"]
    if s["bbox"] and s["vis_bbox"]:
        reach = max(
            (s["bbox"][0] - s["vis_bbox"][0]) / s["w"],
            (s["bbox"][1] - s["vis_bbox"][1]) / s["h"],
            (s["vis_bbox"][2] - s["bbox"][2]) / s["w"],
            (s["vis_bbox"][3] - s["bbox"][3]) / s["h"],
        )
        if reach > V.FRINGE_REACH_TOLERANCE:
            add(V.REJECT, f"faint pixels reach {reach:.1%} of canvas beyond the "
                          f"solid silhouette - raise the key's lower threshold.")
        elif fringe_frac > V.FRINGE_MAX_FRACTION:
            add(V.WARN, f"{fringe_frac:.2%} faint pixels inside the silhouette "
                        f"- consistent with glow; confirm intentional.")

    mid_frac = s["midtone"] / s["n"]
    if mid_frac > V.MIDTONE_MAX_FRACTION:
        add(V.REJECT, f"{mid_frac:.1%} semi-transparent - renders washed out.")

    if s["mean_edge"] and s["mean_opaque"]:
        deltas = [s["mean_edge"][c] - s["mean_opaque"][c] for c in range(3)]
        worst = max(range(3), key=lambda c: deltas[c])
        if deltas[worst] > V.SPILL_CHANNEL_DELTA:
            add(V.WARN, f"rim is {deltas[worst]:.0f}/255 more {'RGB'[worst]} "
                        f"than the body - residual key spill.")

    if s["coverage"] < V.EMPTY_COVERAGE:
        add(V.REJECT, f"effectively empty ({s['coverage']:.3%} solid).")
    if s["touches"]:
        add(V.WARN, f"subject touches the canvas edge ({', '.join(sorted(s['touches']))}) "
                    f"- the art may be clipped.")

    frag = V.fragment_fraction(s)
    if frag is not None and frag > V.FRAGMENT_MAX_FRACTION:
        add(V.WARN, f"{frag:.1%} of solid pixels are detached fragments.")
    return out


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    d = Path(sys.argv[1])
    slug = d.name
    paths = {f: d / f"{slug}_{f}.png" for f in FACINGS}
    missing = [f for f, p in paths.items() if not p.exists()]
    if missing:
        print(f"INCOMPLETE {slug}: missing {', '.join(missing)} - a partial "
              f"Graphic_Multi set is a SILENT failure in game.", file=sys.stderr)
        return 2

    stats, rejects, warns = {}, 0, 0
    for f in FACINGS:
        s = V.measure(str(paths[f]))
        stats[f] = s
        print(f"  {f:<6} {s['w']}x{s['h']}  subject {s['span_w']}x{s['span_h']} "
              f"cov {s['coverage']:.1%}  fringe {s['fringe']/s['n']:.2%}  "
              f"mid {s['midtone']/s['n']:.2%}  sha {s['sha'][:8]}")
        for lvl, msg in absolute_findings(s):
            print(f"    {lvl} {msg}")
            rejects += lvl == V.REJECT
            warns += lvl == V.WARN

    canvases = {(s["w"], s["h"]) for s in stats.values()}
    if len(canvases) != 1:
        print(f"  REJECT facings disagree on canvas: {sorted(canvases)}")
        rejects += 1

    longs = {f: max(s["span_w"], s["span_h"]) for f, s in stats.items()}
    lo, hi = min(longs.values()), max(longs.values())
    if lo and (hi - lo) / hi > SET_SPAN_TOLERANCE:
        print(f"  REJECT the four facings are not one animal size: long axis "
              f"{longs} - the creature would change size as it turns.")
        rejects += 1

    if stats["east"]["sha"] == stats["west"]["sha"]:
        print("  REJECT east and west are pixel-identical - west was not mirrored.")
        rejects += 1

    shas = {f: s["sha"] for f, s in stats.items()}
    if len(set(shas.values())) != 4:
        print(f"  REJECT duplicate facings: {shas}")
        rejects += 1

    print(f"  == {slug}: {rejects} REJECT, {warns} WARN")
    return 1 if rejects else 0


if __name__ == "__main__":
    sys.exit(main())
