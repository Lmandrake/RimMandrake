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

## Update 2026-08-29, same session: 8 attempts, 1 apparent success delivering ZERO pawns

**Read the actual `pawnGroupMakers[].options[]` off the fresh capture's raw JSON** (not
`jawa/get_defs`, which stubs complex nested types) — Empire's `Combat` makers are well-formed,
NOT the cause:
```
Combat (commonality 100): Jawa_Empire_Grunt(w5) · Jawa_Empire_Heavy(w2) · Jawa_Empire_Specialist(w1.5)
Combat (commonality  10): + OuterRim_ImpRangeTrooper(w2) · OuterRim_ImpDeathTrooper(w1.5) · OuterRim_ImpISBAgent(w1)
```
`combatPower`: Grunt 101, Heavy 129, Specialist 119 — trivially affordable at 500 points.
`MinPointsToGenerateAnything` cannot be the blocker. `jawa/drain_log` after a failed fire shows
**no `Log.Error`** for "no usable PawnGroupMakers" — `TryGetRandomPawnGroupMaker` IS finding and
choosing a maker; the failure is downstream of that.

**Pinning `strategy=ImmediateAttack, arrivalMode=EdgeWalkIn` explicitly (instead of letting
`fire_raid` auto-resolve) got exactly ONE `executed: true` out of 8 total attempts** (4
auto-resolved + 3 pinned-but-failed + 1 pinned-success), and even that one delivered **zero
Empire pawns** to `jawa/list_pawns` after stepping 300+ ticks — the pawn census stayed at
the pre-existing Pirate raid's 8 `Jawa_Blackstar_Grunt`, nothing Empire-flagged ever appeared.
This is a WORSE ratio than the general intermittency `AUTHORED_FACTION_RAID_SPAWNS_NOTHING_1`
documented for `Jawa_HuttCartel` (4/7 successes, and every success delivered real pawns) — here
it's ~1/8 and the one "success" was empty, consistent with the hypothesis that
`IncidentWorker_Raid.TryGenerateRaidInfo`'s non-`debugTest` path
(`parms.raidStrategy.Worker.SpawnThreats(parms)`) can return a NON-NULL, EMPTY pawns list — the
`if (pawns == null)` fallback to `PawnGroupMakerUtility.GeneratePawns` only triggers on `null`,
never on empty, so an empty-but-non-null result sails through as `TryExecuteWorker` returning
TRUE with nothing generated. Not confirmed by reading `SpawnThreats`/the strategy worker's own
source this session — that is the next read, not the group maker or budget.

## verify
🔴 **The empty-but-non-null `SpawnThreats` hypothesis is REFUTED, read from source, not
guessed.** `RaidStrategyWorker.SpawnThreats` (base, `Source/RimWorld/RaidStrategyWorker.cs:118`)
only enters its pawn-generating branch `if (parms.pawnKind != null)` — for a normal group raid
`pawnKind` is null, so it falls straight through to `return null;`. `ImmediateAttack` has no
override (only `SiegeMechanoid` does). So the base returns **null**, not empty, and
`TryGenerateRaidInfo`'s `if (pawns == null)` fallback to `PawnGroupMakerUtility.GeneratePawns`
DOES fire correctly. The empty result is therefore inside `PawnGroupKindWorker_Normal
.GeneratePawns` (or whichever `PawnGroupKindDef "Combat"`'s `.Worker` resolves to) itself — NOT
read this session. That class's actual pawn-selection loop (likely `ChooseKindsToGenerate` or
similarly named) is the next and final read to close this item.
Also worth checking: `[Isekai Raid] Hostile group incoming!` printed in `Player.log` on every
attempt (execute or not) — an unrelated mod hooking the same incident type; probably just
flavor text, not confirmed harmless, not chased further this session.

## criteria
- [ ] Confirmed: pawnGroupMakers/options/combatPower are NOT the cause (done — well-formed,
      trivially affordable).
- [ ] Read `SpawnThreats` / the auto-resolved strategy worker to find where an empty pawn list
      can originate and still report `executed: true`.
- [ ] A raid delivers Empire's own kinds (Jawa_Empire_*) at least once, reproducibly — not yet
      achieved in 8 attempts across two firing modes.
