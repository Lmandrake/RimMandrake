# EMPIRE_RAID_QUICKTEST_1

## spec
Quicktest (~90 s map, bridge) proof of the shipped Empire reskin, against vanilla
`Empire` — successor to V2_DREAMS C2, whose spec drove the raid through the
excluded `OuterRim_GalacticEmpire` (canon.yml `empire.outerrim_faction_excluded`).
No `set_faction_relation` step: vanilla `Empire` is already hostile via the
patched `permanentEnemyToEveryoneExcept` whitelist (player factions deliberately
absent). Fire `jawa/fire_incident incidentDef=RaidEnemy faction=Empire dryRun=true`
first; abort on `canFireNow:false`. PASS `points` EXPLICITLY — `points<=0` takes
the storyteller default, tens of points on a fresh quicktest.

## verify
The live check is owed to mechanisms never once observed running together:
the `permanentEnemy false` + whitelist route to hostility, `fixedLeaderKinds` →
Jawa_Empire_Leader, and `fixedIdeo` Rising Order all BAKE at world creation and
have never been observed on a world generated after the patch landed.

## criteria
- Read the `faction` field in the REPLY, never the one you sent —
  `IncidentWorker_RaidEnemy::TryResolveRaidFaction` silently substitutes a random
  weighted faction and still reports `success:true` when the passed faction fails
  its gates (hostile + !deactivated). Reply faction must be `Empire`.
- Raiders are `Jawa_Empire_Grunt/Heavy/Specialist` wearing OuterRim stormtrooper
  armor (apparelRequired), not cataphracts.
- Faction leader is Jawa_Empire_Leader (Emperor Palpatine), title "Emperor".
- Faction ideo is "The Rising Order"; faction name "Galactic Empire".
- `OuterRim_GalacticEmpire` appears in NO faction list on the world.

## Watch out
- A world generated BEFORE the patch keeps the Stellarch and a generated ideo —
  attribute a miss to world age before blaming the patch.
- The raid groups sit inside `PatchOperationFindMod "Outer Rim - Galactic Empire"`:
  on the minimal modlist without that mod, the whole group patch is a silent no-op
  and vanilla kinds spawn. Run this on a list that includes the OuterRim mod.

## 2026-08-29 (FOUNDRY): 4/6 criteria confirmed at the def level; TWO real bugs found blocking
## the other 2 — neither is a quicktest artifact, both confirmed with an A/B control

**Confirmed clean, read straight off the LIVE loaded def via `jawa/get_defs` (584-mod set,
`OFFICIAL-2026-08-29`):**
- `fixedName: 'Galactic Empire'` ✅
- `leaderTitle: 'Emperor'`, `fixedLeaderKinds: ['Jawa_Empire_Leader']` ✅
- `fixedIdeo: True`, `ideoName: 'The Rising Order'` ✅
- `OuterRim_GalacticEmpire` absent from every faction on the world (`jawa/faction_relations_get`,
  25 factions listed, checked by name) ✅

**Bug 1 — `permanentEnemyToEveryoneExcept` is NOT what `GalacticEmpire.xml` writes.**
The item's premise ("vanilla Empire is already hostile... player factions deliberately
absent") does not hold. `jawa/get_defs FactionDef/Empire permanentEnemyToEveryoneExcept`
returns **24 entries including `PlayerColony` and `PlayerTribe`** — exactly the two entries
our patch's own comment says are "DELIBERATELY DROPPED... that single omission is what keeps
the Empire permanently hostile to the player." `validate_patch.py --live` confirms EVERY
operation in `GalacticEmpire.xml`, including this exact `PatchOperationReplace`, reports
`1 match(es)` against `Royalty: Faction_Empire.xml` — our patch's xpath is not the problem.
Something else — a compatibility patch from another mod, loading after `mandrake.jawa.patches`
(ModsConfig line 585) — re-adds `PlayerColony`/`PlayerTribe` plus a long list of other mods'
player-faction defNames (`BS_PlayerColonyXenoPlus`, `VFEI2_PlayerOutpost`, `AM_PlayerColony`,
`OuterRim_EmpirePlayerFaction`, …), consistent with a generic "except every player-faction-type
mod" compatibility patch that doesn't know this campaign wants Empire hostile.
**Not identified which mod** — `permanentEnemyToEveryoneExcept` is patched by 30+ mods in the
Workshop folder (grep across all 1256 mods), most targeting other factions; narrowing to the
one hitting Empire specifically needs a dedicated pass, not done here.
**Consequence, read straight off `FactionUtility.HostileTo`**: it is `RelationWith(other).kind
== Hostile`, nothing else — `permanentEnemyToEveryoneExcept` only feeds
`Faction.TryMakeInitialRelationsWith`'s `GetInitialGoodwill` at the moment a relation is first
created (`Source/RimWorld/Faction.cs:388-424`). With PlayerColony in the except-list, initial
goodwill is 0, kind Neutral — confirmed live: `jawa/faction_relations_get` shows Empire↔
PlayerColony `kind: Neutral, goodwill: 0, permanentEnemy: false, canChangeGoodwill: true`.

**Bug 2 — even forced Hostile, Empire's own raid generation fails every time; Pirate does not
(A/B control, same map, same call).** After `jawa/faction_relations_set faction=Empire
kind=Hostile` (workaround for Bug 1, confirmed `raid_preview` now lists Empire hostile,
`canStageAttacks: true`): `jawa/fire_raid faction=Empire points=500` returned
**`executed: false` on 4 consecutive tries** ("TryExecute returned false - the worker refused
these parms" — the honest-failure path from `AUTHORED_FACTION_RAID_SPAWNS_NOTHING_1`, not a
false positive). The SAME call against `Pirate` on the SAME map **executed: true** first try —
ruling out both a map-level limitation (quicktest maps are small; this could have been
`TryResolveRaidSpawnCenter` failing) and hostility as the cause. This is Empire-specific,
inside `TryGenerateRaidInfo`'s pawn-generation path (`PawnGroupMakerUtility.GeneratePawns`
most likely, per the mechanism already mapped in `AUTHORED_FACTION_RAID_SPAWNS_NOTHING_1`).
5 `PawnGroupMaker`s are present on Empire (not an empty list — `jawa/get_defs` reflection
only stubs complex types, so their internal options were NOT inspected here).

## 🔴 Bug 2 SOLVED (`EMPIRE_RAID_NEVER_GENERATES_1`, same session, after this was written):
not a bug at all — vanilla `Faction_Empire.xml`'s `maxPawnCostPerTotalPointsCurve` caps
per-pawn cost at 100 for any raid ≤500 points, and `Jawa_Empire_Grunt.combatPower` is 101, one
point over. **Empire cannot field a single trooper below 500 points; every attempt this session
used exactly 500.** At `points=1200`: raid fired, **6 Jawa_Empire_Grunt · 2 Jawa_Empire_Heavy ·
1 Jawa_Empire_Specialist** arrived, wearing `OuterRim_StormtrooperCuirass` +
`OuterRim_StormtrooperHelmet`, carrying `OuterRim_E11BlasterRifle` — not cataphracts. Both
remaining criteria below are now confirmed.

## criteria
- [x] `OuterRim_GalacticEmpire` in no faction list.
- [x] Faction leader Jawa_Empire_Leader, title Emperor.
- [x] Faction ideo "The Rising Order"; faction name "Galactic Empire".
- [x] Raiders in OuterRim stormtrooper armor, not cataphracts — confirmed live at
      `points=1200` (`EMPIRE_RAID_NEVER_GENERATES_1`): the 500-point ceiling, not a real defect.
- [x] Reply-faction / no-substitution: `actual.faction: Empire, substituted: false` on every
      fire this session, including the 1200-point success.
- [x] Bug 2 (raid never generating) — root-caused and closed, see above and
      `EMPIRE_RAID_NEVER_GENERATES_1`.
- [ ] Bug 1 remains open: `EMPIRE_WHITELIST_OVERRIDDEN_1` — Empire still reads Neutral to the
      player by default (the interloping mod/patch not yet named). This item's own spec ("no
      set_faction_relation step needed") does not hold until that closes.
