"""reconnect_orphans.py — find river systems whose LOW POINT has no outlet.

Owner, 2026-08-25: *"near 12.84N 46.84W there are several little rivers that are not
well connected to the main flow, please fix"*. That tile is 15156, Scald Spine. The
defect there was structural, not cosmetic:

    sys11 chain: 7041(387m) -> 17326(148m) -> 17328(1m) -> 11915(1m)
                 -> 7054(34m) -> 15157(266m) -> 15155(551m)

a V — two headwaters running DOWN into a trough at 1 m with no outlet, while the
LargeRiver trunk sat at 1 m directly adjacent and unjoined. sys12 was a 2-tile creek
with no river neighbour at all.

⚠️ The first drainage pass missed both because it demanded a >=15 m drop into the trunk.
On a floodplain everything is at 1 m, so the rule that protects against merging BASINS
also blocked the confluence that a delta is supposed to have.

⛔ Still NOT joined, deliberately: sys2 (109 tiles) and sys8 (11), both landlocked in the
Dune Sea. Linking them drains nothing — neither reaches a sea — and doctrine is explicit
that rivers peter out into salt flats rather than connect basins. Same for sys1 and sys9,
which have no route at all and die in place, which is legal.

Applied 2026-08-25:  7055 -> 17328          (trough discharges into the trunk)
                     17328 -> 1674 -> 17324 (sys12 extended down to that trough)
Verified from the engine: systems 14 -> 12, landlocked 6 -> 4, and all nine orphan tiles
now share system 0, which reaches the Scald via tile 7791.
"""
