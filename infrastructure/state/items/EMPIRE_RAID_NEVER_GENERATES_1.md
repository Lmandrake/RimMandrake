# EMPIRE_RAID_NEVER_GENERATES_1 — Empire's own raid generation fails every time, even Hostile

Split from `EMPIRE_RAID_QUICKTEST_1`, 2026-08-29. Full evidence there; summary here.

## spec
With Empire forced Hostile (`jawa/faction_relations_set`, workaround for
`EMPIRE_WHITELIST_OVERRIDDEN_1`) and confirmed `canStageAttacks: true` in `jawa/raid_preview`,
`jawa/fire_raid faction=Empire points=500` returned `executed: false` ("TryExecute returned
false - the worker refused these parms") on **4 consecutive tries**, on a fresh 584-mod
quicktest map. The identical call against `Pirate` on the **same map, same session** returned
`executed: true` on the first try — ruling out a map-level limitation (e.g.
`TryResolveRaidSpawnCenter` failing on a small quicktest map) as the cause, since Pirate
proves the map itself can host a raid. This is Empire-specific.

## mechanism, known but not finished (from AUTHORED_FACTION_RAID_SPAWNS_NOTHING_1, same session)
`IncidentWorker_Raid.TryGenerateRaidInfo` returns false when
`PawnGroupMakerUtility.GeneratePawns` yields zero pawns — silently, except under `debugTest`.
Empire has 5 `PawnGroupMaker`s (confirmed non-empty via `jawa/get_defs`, but their internal
`options` were NOT inspected — the generic reflection tool stubs complex nested types).
Candidates, none tested: every option in Empire's `Combat` maker(s) costing more than the
raid's points budget once `maxPawnCostPerTotalPointsCurve` applies; a filter failing at
generation time; or the pawn kinds' own weaponTags pool being too narrow post-patch (see
`PAWN_WEAPON_POOL_JOIN_TOOL_1` — several Empire kinds are ranged-only within budget, but that
explains BARE pawns, not zero pawns generated for the whole raid).

## verify
Read Empire's actual `pawnGroupMakers[].options[]` (defName + cost) off the live dump directly
— `jawa/get_defs` can't reach it; either a raw def-dump JSON read (`captures/<id>/defs/
FactionDef.json`) or a small companion addition. Compare against 500-point and higher budgets
to see if EVERY option prices out. Retry at higher points (this session tested points=500 only)
before concluding budget is not the cause.

## criteria
- [ ] The exact reason `GeneratePawns` returns empty for Empire named from the def, not guessed.
- [ ] A raid at SOME points value delivers Empire's own kinds (Jawa_Empire_*), proving the
      pipeline works at all.
- [ ] If budget-related: a fix decided (raise the group's floor, widen weaponTags) — owner's
      call, this is canon/faction-identity territory per `PAWN_WEAPON_GEN_TAG_POOL_READ_1`'s
      own precedent.
