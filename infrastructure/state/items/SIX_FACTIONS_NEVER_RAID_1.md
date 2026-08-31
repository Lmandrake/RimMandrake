# SIX_FACTIONS_NEVER_RAID_1 — eight authored factions and two VANILLA ones spawn no raiders

🔴 **READ THE 2026-08-30 LIVE SECTION AT THE BOTTOM FIRST.** The title above and the
2026-08-27 table below are both WRONG, and the reason is named there: the harness that
produced them could not make a faction hostile, so all 18 "firings" were substituted
raids under another flag. The measured fact is now: **`Jawa_HuttCartel` never raids
either, and neither do vanilla `Pirate` and `CASacrilegHunters`** — while `Empire`,
`Insect`, `OutlanderCivil` and `TribeCivil` raid 8/8 on the same map, same tick, same
points. This is not a property of the factions this repo authors.


## The 2026-08-27 run is RETRACTED
It recorded each authored faction as the sole hostile, then three `fire_raid` firings
each, and reported the Hutt raiding while six others delivered nothing. **None of those
factions was ever hostile** — see §1 of the 2026-08-30 section — so every firing was
substituted onto a different faction and the table measured nothing about its subjects.
Its three derived conclusions ("not hostility", "not the pawn kinds", "not the group
makers") are superseded by the live reads below, which re-established the last two
properly and refuted the first. Provenance is in git.

⚠️ One thing from that run survives and is still true: `resolved.faction` on a `fire_raid`
response ECHOES THE REQUEST (`FIRE_RAID_ECHOES_REQUESTED_FACTION_1`). Read `actual` and
`arrived`, which the tool now returns and which are counted off the map.

## 2026-08-30 (FOUNDRY), pass 1 — the engine gate read, from source only

### The gate, named: `PawnGroupMakerUtility.UsableFactions`
`Source/RimWorld/PawnGroupMakerUtility.cs:355` is the only place the engine decides which
factions may source a combat group. A faction must satisfy **all** of:

    !Hidden · !temporary · !defeated · def.humanlikeFaction · HostileTo(player)
    def.pawnGroupMakers != null
    def.pawnGroupMakers.Any(x => x.kindDef == PawnGroupKindDefOf.Combat)
    !def.raidsForbidden
    points >= def.MinPointsToGeneratePawnGroup(Combat)

`TryGetRandomFactionForCombatPawnGroup` (line 360) is its only caller of consequence.

### ✅ `Jawa_DeepwaterCompact` is ANSWERED — `raidsForbidden = true`
Read live off the def, 585-mod set: Deepwater is the **only** one of the seven with
`raidsForbidden: true`. `UsableFactions` filters on `!def.raidsForbidden`, so the
storyteller can never select it, and `TimedDetectionRaids` skips it too
(`Planet/TimedDetectionRaids.cs:51`). ⇒ **Deepwater will never raid in play, by design of
its own def.** Whether that is what the owner wants is a separate question and belongs to
whoever owns the faction spec; mechanically it is not a bug and needs no further probing.
⚠️ Pass 2 read the same field live off `OutlanderCivil`, which carries `raidsForbidden:true`
in this load and raids 8/8 under an explicit firing — so the flag bears on STORYTELLER
selection only, exactly as this section says, and never on `fire_raid`.

### ⛔ The points gate is REFUTED as an explanation — do not re-test it
`MinPointsToGeneratePawnGroup(Combat)` resolves to the cheapest `isFighter` option's
`combatPower` (`PawnGenOption.Cost => kind.combatPower`). Computed for all five remaining
factions off their own rosters:

    Jawa_GeonosianFoundryHive   Jawa_Geonosian_Grunt      56
    Jawa_Junkers                Jawa_Junkers_Grunt        56
    Jawa_WildsteamClan          Jawa_Wildsteam_Specialist 82
    Jawa_FreeDroidEnclaves      Jawa_Droid_Grunt          90
    Jawa_AscendantHelix         Jawa_Helix_Grunt         130

Every one clears the 3000 points the firings used by **more than twentyfold**. Also
checked and clean: all five set `humanlikeFaction` true, and the two factions with only
**2** `pawnGroupMakers` (Geonosian, Junkers) are missing the **Trader** maker, not the
Combat one — both carry an intact 4-option Combat maker.

### 🔴 The correction that matters: none of the above can explain the 18 firings
`IncidentWorker_RaidEnemy.TryResolveRaidFaction` (lines 58-73) returns **true immediately**
when `parms.faction` is already set and hostile:

    if (parms.faction != null && parms.faction.HostileTo(Faction.OfPlayer)
        && (!parms.faction.deactivated || parms.forced))
        return true;

`fire_raid` names the faction, so `UsableFactions` is never reached — `raidsForbidden`,
`MinPointsToGeneratePawnGroup` and the whole line-355 filter are **bypassed** on the exact
path the 18 firings took. ⇒ The empty firings are **downstream of faction resolution**, in
pawn-group generation, the raid strategy, or the arrival mode. Every FactionDef-field
hypothesis is now exhausted; the def is not where the answer is.

⭐ Consequence for whoever picks this up: the two findings above are about **play**
(the storyteller's own selection), not about `fire_raid`. Deepwater is answered for play
and still unexplained for `fire_raid`, like the other five.

### A map WAS available — pass 2 found one and used it
`rimworld/get_game_info` reported `mapCount: 1` on a scratch quicktest colony already
loaded in the running game. No world generation and no restart were needed. ⇒ Before
budgeting a quicktest load for this kind of item, **ask the bridge whether a map is
already up**; the campaign save being world-only says nothing about the live session.

## 2026-08-30 (FOUNDRY), pass 2 — LIVE RAIDS FIRED. The premise is refuted; the split is not ours

Measured on the running 590-entry game, Map_0, paused, `ticksGame` 1176→4236, three
colonists, ~90 raids fired. Evidence, with the firing scripts and the full 122-field def
dumps: `infrastructure/state/evidence/raid_split_2026-08-30/`.

### 🔴 1. The 2026-08-27 evidence is VOID — the factions were never hostile
`jawa/set_faction_relation kind=Hostile` **cannot make an ordinary faction hostile.** It
calls `Faction.SetRelationDirect`, and `RimWorld/Faction.cs:641` opens with

    if (HasGoodwill && other.HasGoodwill) { Log.Error("Tried to use SetRelationDirect
        for factions which use goodwill..."); return; }

`HasGoodwill` is `!Hidden && !temporary` — true for every ordinary faction and for the
player — so the setter **returns without writing**. Its sibling `goodwill=` parameter
writes `rel.baseGoodwill` on ONE side and never calls `FactionRelation.CheckKindThresholds`,
so goodwill −100 sits under `kind = Neutral` and `HostileTo` stays FALSE. ⭐ The tool
reports this honestly — `kind:{was:Neutral, now:Neutral, asked:Hostile, ok:false}`,
`success:false`, `hostileToPlayer:false` — it was simply not read.
⇒ Every 2026-08-27 firing hit `TryResolveRaidFaction`'s substitution path. Reproduced
live: requesting `Jawa_HuttCartel` this way delivered **19 `Empire` pawns**,
`substituted:true`.
✅ **`jawa/faction_relations_set` (JawaBenchWorldTools) is the correct tool** — it writes
both records and fires `Notify_RelationKindChanged` itself. Use it, never the older one.

### 2. With real hostility, `substituted:false` every time — and still nothing arrives
Forced `strategy=ImmediateAttack`, `arrivalMode=EdgeWalkIn`, 3000 points, 8 consecutive
firings each, pawns counted off `map.mapPawns.AllPawnsSpawned` and the map cleared between:

    Empire                8/8   (27–35 pawns)      Jawa_HuttCartel            0/8
    Insect                8/8   (29–44)            Jawa_Junkers               0/8
    OutlanderCivil        8/8   (26–47)            Jawa_AscendantHelix        0/8
    TribeCivil            ✅     (69–78)            Jawa_FreeDroidEnclaves     0/8
    TradersGuild          4/8   (19–20)            Jawa_IndigenousTribes      0/N
    ⛔ Pirate             0/8    ← VANILLA          Jawa_WildsteamClan         0/N
    ⛔ CASacrilegHunters  0/8    ← a MOD's faction  Jawa_GeonosianFoundryHive  0/N
                                                   Jawa_DeepwaterCompact      0/N

🔑 **The Hutt Cartel is on the failing side, and two factions this repo did not author are
there with it.** The 2026-08-27 asymmetry does not exist. `Jawa_DeepwaterCompact`
behaves exactly like the other seven under `fire_raid`, `raidsForbidden` notwithstanding
— and `OutlanderCivil` carries `raidsForbidden:true` in this load and raids 8/8, so that
field is confirmed irrelevant to an explicit-faction firing.

### 3. What the failure looks like, from the inside
- `executed:true`, `substituted:false`, `actual.faction` = the one requested.
- **No Lord is created** (`jawa/lord_pawn_move action=list` count unchanged), no pawns,
  no letter. Working factions add exactly one `LordJob_AssaultColony`.
- **Not a points gate:** 70 · 150 · 400 · 1000 · 3000 · 10000 · 30000 → 0 at every value
  for Hutt and Trade Moot; `OutlanderCivil` produced pawns at all of them.
- **Not the strategy:** `jawa/raid_preview` with each as the SOLE hostile reports
  `ImmediateAttack · ImmediateAttackSmart · StageThenAttack · Siege · VREA_Archon…`
  usable for Hutt and Pirate exactly as for Empire.
- **Not the kinds:** all 49 roster `PawnKindDef`s read live — every one found,
  `isFighter:true`, sane `combatPower`. `Jawa_Empire_*` (Empire) and `Jawa_DeepDesert_*`
  (TribeCivil) are OUR kinds and they raid fine.
- **Not any FactionDef scalar:** all 122 public fields read live off 7 defs and diffed
  failing-vs-working — **zero fields separate the two groups**.
- **Nothing is logged.** `drain_log` (fresh process, buffer alive, `contains=` verified
  working) finds none of `Exception while generating pawn group` · `Got no pawns` ·
  `Cannot generate pawns for` · `no usable PawnGroupMakers` · `Pawn generation error`.
- The `Isekai Raid` mod logs `Hostile group incoming! Points: 3000, Faction: X, Type:
  ImmediateAttack` for BOTH groups, then per-pawn grading and `Processed N hostile pawns,
  Lord: LordJob_AssaultColony` only for the working ones.
- `jawa/fire_incident RaidEnemy` reproduces the same split, so it is not `fire_raid`.

### 4. Where the mechanism has to be, and why it needs the game DOWN
Three vanilla paths can end a raid with an empty group; two of them `Log.Error`, and
neither error appears. The third is silent: `PawnGroupMakerUtility.ChoosePawnGenOptionsByPoints`
breaks out of its loop when `TryRandomElementByWeight` finds every candidate at weight 0
(weight = `selectionWeight × xenotypeChance × PawnWeightFactorByMostExpensivePawnCostFractionCurve`),
and `PawnGroupKindWorker_Normal.GeneratePawns` then returns an empty list with no message.
⚠️ That is a HYPOTHESIS, not a finding — nothing on the bridge can see inside it, and
`executed:true` on a zero-pawn raid is impossible in vanilla 1.6
(`IncidentWorker_Raid.TryGenerateRaidInfo` returns false), so at least one Harmony patch
is already in the path.

## criteria
- [x] The 2026-08-27 table is retracted, with the harness defect that produced it named
      from the engine (`Faction.SetRelationDirect` refuses goodwill-bearing pairs).
- [x] `Jawa_DeepwaterCompact` — `raidsForbidden:true` keeps it out of
      `PawnGroupMakerUtility.UsableFactions` and so out of STORYTELLER selection. Still
      true, still not a bug. It does not explain the `fire_raid` result, and this load
      shows `OutlanderCivil` raiding with the same flag set.
- [ ] The mechanism. **Next step, in order, and neither is another def read:**
      1. On a minimal / dependency-scoped tier (`modset_builder.py`), quicktest map, fire
         at `Jawa_HuttCartel` and at vanilla `Pirate`. If both raid, the defect is a mod
         in the 590 stack and the job becomes bisecting it — `Isekai Raid` first, it is
         demonstrably in the path. If both stay empty, it is ours after all.
      2. If a live read inside generation is still needed, add ONE companion tool
         (`rimbridge-companion`) that, for a named faction, reports in one call:
         `TryGetRandomPawnGroupMaker` → chosen maker; `PawnGroupMaker.CanGenerateFrom`;
         `PawnGroupMakerUtility.AnyOptions`; `GetOptions(...).Count` with each entry's
         `Cost`, `SelectionWeight` and xenotype; and `GeneratePawnKindsExample`. That
         names the gate directly instead of inferring it.
      Both need the game CLOSED (a companion DLL cannot deploy while it runs), so this
      item is parked on the next game-down window.

### 5. 🔑 The polarity FLIPS between worlds — so it is not a def property at all
`EMPIRE_RAID_NEVER_GENERATES_1` measured, on 2026-08-29 and a different world,
**`Empire` failing 4/4 while `Pirate` succeeded first try.** This session, same call,
different world: **`Empire` 8/8, `Pirate` 0/8.** The two factions that item contrasted
are both reversed. ⇒ Which faction yields an empty pawn group is **per-world state**, not
a FactionDef field — consistent with the 122-field diff finding nothing.
⭐ The one input to pawn-group weighting that is generated per world rather than read from
a def: the **ideo**. `PawnGenerator.XenotypesAvailableFor` folds
`faction.ideos.PrimaryIdeo.memes[].xenotypeSet` in beside `factionDef.xenotypeSet`, and its
chances become the `SelectionWeight` multiplier that `ChoosePawnGenOptionsByPoints` can
drive to zero. HYPOTHESIS, untested — but it is the first one that survives the flip.

## ⚠️ Escalation — this is bigger than the item
If a faction that yields an empty pawn group under an explicit firing also yields one
under the storyteller, then **8 of 15 factions in this world, including vanilla `Pirate`,
can never send a raid in play.** That was not tested (the storyteller path was not
exercised) and it would be a campaign-level defect, not a bridge curiosity.
