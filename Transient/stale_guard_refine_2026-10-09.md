# Stale guard refine, 2026-10-09 (BENCH helper)

Change: `ingest.stale_letter_rows(doc, ruled, now, versions=None)` now exempts a letter only when the snapshot current at
click time (newest git/disk version of the sheet snapshot with `built` <= click; `L.snapshot_versions`) resolves it to
exactly the same per-facing shas as the current snapshot. Renamed rows are looked up under the decisions row's
`carriedFrom` (the snapshot has no carry map; the decisions file does). Unknown anything (no click-time snapshot, letter
absent then, differing sha) stays a CONFLICT. Selftests: same-sha exempt, changed-sha stale, none known stale, snapshot
built after click stale, carried same-sha exempt, carried changed-sha stale.

## Previews (dry run, no --apply): "clicked before" stale conflicts (total conflicts)
| sheet | before | after |
|---|---|---|
| abyss | 20 (22) | 4 (8) |
| deep_desert | 13 (16) | 0 (3) |
| greentide | 38 (38) | 1 (58)* |
| twilightsea | 2 (12) | 2 (12) |
| warscar | 4 (4) | 4 (4) |
| rustcathedral | 0 (3) | 0 (3) |
| thescald | 1 (3) | 0 (2) |
*greentide total rose: the 37 exempted rows now proceed into the plan and surface their ordinary conflicts (owner-kept etc.), previously masked by the stale guard.

## Spot checks of remaining
- warscar RM_Bileworm A (carried from AA_Helixien): shas differ click-time vs now -> genuine change.
- twilightsea RM_DancingSkresh A (carried from RM_Hollu): shas differ -> genuine change.
- abyss RM_GlowingGrass E: letter absent in click-time snapshot (no snapshot committed with it) -> unprovable, stays conflict (conservative).
- greentide RSW_Beldon H,J: clicked ~11 min before first committed snapshot containing them (audit: identical later) -> unprovable, stays.
