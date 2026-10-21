#!/usr/bin/env python3
"""Selftest: RM_TidalSunGlowPatch's light, modelled offline on every Ash'karr tile (SUN_GLOW_DECIDE_WEST_TERMINATOR_SUNBATHING).

Owner, by card 2026-10-20: "Light follows the sun". Uses world_physics_audit.glow_geo (a line-for-line port of
CreatureBehaviors/Source/RM_TidalSunGlowMath.cs) over the engine-truth lat/long in world/world_tiles_sub7b.csv.

Asserts, on all tiles:
  - the instrument can see: the Alien Worlds port (glow_tidal) still shows its known ~448 lit-night / ~1,796 dark-day
    tiles (audit §2; 450/1,794 unrounded) — a 0/0 below is only meaningful if the same counter finds those;
  - with our glow: 0 night-side tiles read daytime and 0 day-side tiles read night;
  - home tile 17011 reads >= 0.99; west/east mirror tiles read the same; beyond the dusk band glow is exactly 0.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import world_physics_audit as A  # noqa: E402

TILES = os.path.join(A.REPO, "world", "world_tiles_sub7b.csv")


def main():
    rows = list(csv.DictReader(open(TILES, encoding="utf-8")))
    ll = {int(r["tile"]): (float(r["lat"]), float(r["long"])) for r in rows}
    fails = []
    if len(ll) != 21872:
        fails.append(f"geometry CSV has {len(ll)} tiles, expected 21,872")
    mod = A.day_night_mismatch(ll.values(), A.glow_tidal)
    # the audit's 448/1,796 counted ROUNDED glow and arc; unrounded it is 450/1,794 — allow that, not a blind 0
    if abs(mod[0] - 448) > 5 or abs(mod[1] - 1796) > 5:
        fails.append(f"sanity: the Alien Worlds port gives {mod}, expected ~(448, 1796) — the counter cannot see")
    geo = A.day_night_mismatch(ll.values(), A.glow_geo)
    if geo != (0, 0):
        fails.append(f"our glow: {geo[0]} night-side tiles read day, {geo[1]} day-side tiles read night (want 0, 0)")
    home = A.glow_geo(*ll[17011])
    if home < 0.99:
        fails.append(f"home tile 17011 glow {home:.3f} < 0.99")
    for lat, lon in ll.values():
        if abs(A.glow_geo(lat, lon) - A.glow_geo(lat, -lon)) > 1e-9:
            fails.append(f"west/east asymmetric at {lat},{lon}")
            break
        if 90 - A.arc_deg(lat, lon) <= -A.TWILIGHT_BAND and A.glow_geo(lat, lon) != 0.0:
            fails.append(f"glow beyond the dusk band at {lat},{lon}")
            break
    print(f"tiles {len(ll)}  mod lit-night/dark-day {mod}  ours {geo}  home 17011 {home:.3f}")
    for f in fails:
        print("FAIL", f)
    print("PASS" if not fails else f"{len(fails)} FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
