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

## The empty-but-non-null `SpawnThreats` hypothesis is REFUTED, read from source
`RaidStrategyWorker.SpawnThreats` (base, `Source/RimWorld/RaidStrategyWorker.cs:118`) only
enters its pawn-generating branch `if (parms.pawnKind != null)` — for a normal group raid
`pawnKind` is null, so it falls straight through to `return null;`. `ImmediateAttack` has no
override (only `SiegeMechanoid` does). So the base returns **null**, not empty, and
`TryGenerateRaidInfo`'s `if (pawns == null)` fallback to `PawnGroupMakerUtility.GeneratePawns`
DOES fire correctly, reaching `PawnGroupKindWorker_Normal.GeneratePawns`
(`Source/RimWorld/PawnGroupKindWorker_Normal.cs:48-98`) — read in full this session.

## Traced the ENTIRE selection chain inside GeneratePawns; every gate individually cleared
`GeneratePawns` calls `PawnGroupMakerUtility.ChoosePawnGenOptionsByPoints(parms.points,
groupMaker.options, parms)`; an empty result there (zero chosen, no log anywhere in this path)
is the only way `outPawns` stays empty with no error — matches everything observed (no
"Cannot generate pawns for..." in the log). That function's per-option gate,
`GetOptions` → `CanUseOption` → `PawnGenOptionValid`, was read end to end and each individual
check ruled out for Jawa_Empire_Grunt/Heavy/Specialist:
- **Cost**: `combatPower` 101/129/119 vs 500 points — not the ceiling by any plausible curve.
- **Xenotype availability**: `PawnGenerator.XenotypesAvailableFor` (Biotech is active, gating
  this whole branch) ALWAYS returns at least `{Baseliner: 1.0}` as a fallback when explicit
  chances don't sum to 1 — structurally cannot return empty. Ruled out.
- **`generateFightersOnly`**: all three kinds have `isFighter: true` (confirmed off the dump).
- **Strategy filter** (`CanUsePawnGenOption`, base `RaidStrategyWorker`, since `ImmediateAttack`
  has no override): only rejects Animal-race kinds before a Humanlike is chosen — Empire's
  troopers are Humanlike, trivially passes.
- **`maxPerGroup`**, **bossgroup reservation**, **CreepJoinerFormKindDef**: no plausible reason
  to apply to a freshly-generated Empire trooper.

**Not fully closed**: `MaxPawnCost`'s two curve/formula inputs —
`faction.def.maxPawnCostPerTotalPointsCurve` (present, 4 `CurvePoint`s, but the dumper stubs
`CurvePoint`'s x/y values so they were NOT read numerically this session) and
`raidStrategy.Worker.MinMaxAllowedPawnGenOptionCost` (base `RaidStrategyWorker`, not read) — if
either caps the affordable-per-pawn cost below ~101, every option in `GetOptions` fails
`num > maxOptionCost` silently and `ChoosePawnGenOptionsByPoints` returns nothing, exactly
matching every observation. **This is the single remaining candidate** after eliminating
everything else in the chain.
Also noted, not chased: `[Isekai Raid] Hostile group incoming!` prints in `Player.log` on every
attempt (execute or not) — an unrelated mod hooking the same incident type; probably flavor
text, not confirmed harmless.

## 🔴 ROOT CAUSE FOUND AND CONFIRMED LIVE — closing

`Data/Royalty/Defs/FactionDefs/Faction_Empire.xml:121-128` (vanilla, UNPATCHED by
`GalacticEmpire.xml` — not in scope of any Jawa patch):
```xml
<maxPawnCostPerTotalPointsCurve>
  <points>
    <li>(500, 100)</li>   <!-- Can always use relatively strong pawns... -->
    <li>(1000, 150)</li>
    <li>(2000, 250)</li>
    <li>(2001, 10000)</li>
  </points>
</maxPawnCostPerTotalPointsCurve>
```
At `points<=500` the per-pawn cost ceiling is **100**. `Jawa_Empire_Grunt.combatPower = 101` —
**one point over** — and Heavy (129) / Specialist (119) are further over. Every option in
`CanUseOption`'s `num > maxOptionCost` check (`Source/RimWorld/PawnGroupMakerUtility.cs:172`)
therefore fails for every candidate, `GetOptions` returns empty, `ChoosePawnGenOptionsByPoints`
chooses nothing, and the raid silently generates zero pawns — exactly matching all 7-8 failed
attempts, all fired at 500 points. This is points-dependent, not Empire-broken: **at 1000+
points the ceiling rises to 150**, comfortably covering all three kinds.

**Verified live, `points=1200`**: `executed: true`, arrived **6 Jawa_Empire_Grunt · 2
Jawa_Empire_Heavy · 1 Jawa_Empire_Specialist**. `jawa/pawn_get` on one: apparel
`OuterRim_StormtrooperCuirass` + `OuterRim_StormtrooperHelmet`, equipment
`OuterRim_E11BlasterRifle` — exactly the reskin's intended gear, not cataphracts. This closes
`EMPIRE_RAID_QUICKTEST_1`'s remaining two criteria as well.

**Not a bug to fix** — this is vanilla Empire's own designed floor ("empire doesn't really have
weak ones"), and Jawa_Empire_Grunt sitting at 101 vs the 100 ceiling is presumably intentional
or a 1-point coincidence, not something this item's scope covers. Worth a one-line note to
whoever tunes `combatPower` values: **raids under 500 points can never field an Empire trooper
at all**, so any low-points Empire test (quicktest or early-game) must use `points>=1000` or
it will read as a total failure that isn't one.

## criteria
- [x] pawnGroupMakers/options/combatPower/xenotype-availability/isFighter/strategy-filter are
      NOT the cause — each read from source and individually cleared.
- [x] Root cause named from source: `maxPawnCostPerTotalPointsCurve`'s 100-cap at ≤500 points
      vs Jawa_Empire_Grunt's combatPower 101.
- [x] A raid delivers Empire's own kinds reproducibly — confirmed live at 1200 points, correct
      apparel and weapon.

## 🔴 2026-08-30 (FOUNDRY) — CORRECTION: the polarity FLIPPED, so it is not Empire-specific

Live, 590-entry list, `Map_0` of a scratch quicktest colony, paused, 8 consecutive firings
per faction at 3000 points with `strategy=ImmediateAttack`, `arrivalMode=EdgeWalkIn`,
arrivals counted off the map. Evidence:
`infrastructure/state/evidence/raid_split_2026-08-30/`.

    Empire   8/8  (27–35 pawns)        ← failed 4/4 on 2026-08-29
    Pirate   0/8                       ← succeeded first try on 2026-08-29

**Exactly the two factions this item contrasted, both reversed, on a different world.**
⇒ Which faction produces an empty pawn group is **not a property of its FactionDef** — it
is per-world state. Confirmed independently: all 122 public `FactionDef` fields were read
live off 7 factions and diffed failing-group vs working-group, and **no field separates
them** (`split.py` / `defs4.json` in the evidence folder). All 49 roster `PawnKindDef`s
read healthy, `isFighter: true`.

⭐ The remaining suspect that is per-world rather than per-def: the **generated ideo**.
`PawnGenerator.XenotypesAvailableFor` (the input to the weight that
`ChoosePawnGenOptionsByPoints` can zero out) reads
`faction.ideos.PrimaryIdeo.memes[].xenotypeSet` as well as the FactionDef's own. That is a
HYPOTHESIS, untested. See `SIX_FACTIONS_NEVER_RAID_1` for the next steps; this item is not
reopened.
