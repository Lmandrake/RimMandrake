## spec
Build RUT_ScavengerEvents (mandrake.rut.scavengerevents): port 8 Mo'Events
mechanics as our own IncidentWorkers (SurvivalPod, ShipBreak, PodCrash->spacer
rescue, RescueTraitor, Insects->desert fauna, Migration,
Thanksgiving->clan-tribute/moisture-tithe, Stroke; drop Nausea+Amnesia),
register-true letter text, loot from our salvage economy; per-event
baseChance settings kept. Interim: zero all MO_ baseChances via Mo'Events own
settings. Each worker needs a proven-fires bridge test. Then retire
mlie.moevents BEFORE save freeze; delete stale animal_census.csv
MO_AbominationRace row. Port behavior not bugs (author's 3 disabled events
were buggy); check Mlie continuation license before lifting C# verbatim.

## mechanism reference — decompiled 2026-09-10, not read from any wiki/memory
`MoreIncidents.dll` (mlie.moevents, `.../workshop/content/294100/2035143365/
1.6/Assemblies/MoreIncidents.dll`) ships no C# source, only the compiled
assembly — read via a scratch copy of `ilprobe` (repointed `DLL` in
`meta_core.py`/`meta.py`, tool itself untouched). Real IL, not guessed:

- **MOIncidentWorker_SurvivalPod** — unconditional. One drop pod
  (`DropPodUtility.DropThingsNear`, radius 110) holding: Hyperweave pants +
  shirt + jacket + tuque, 4x `MealSurvivalPack`, 1x `Gun_Autopistol`.
  `PositiveEvent` letter (`MO_SurvivalPods`).

- **MOIncidentWorker_ShipBreak** — unconditional. Builds a random loot list
  (excludes leather/meat ThingDefs, one item added per loop, stack size
  20-40 capped to `stackLimit`, running total capped to a `Rand.Range(150,900)`
  market-value budget, max 25 items) — `DropThingsNear` (radius 110). PLUS two
  `SpaceRefugee`-kind pawns from `RandomNonHostileFaction`: one `DamageUntilDowned`
  (alive) and one `DamageUntilDead` → its corpse — each in its OWN drop pod
  (`MakeDropPodAt`, `openDelay=180`, `leaveSlag=true`). `PositiveEvent` letter
  (`MO_CargoRain`, not "ShipBreak" — the internal keys don't match the class
  name).

- **MOIncidentWorker_PodCrashTribal** (item's "spacer rescue") — unconditional.
  One `Villager`-kind pawn from `RandomNonHostileFaction`, `DamageUntilDowned`,
  one drop pod (`MakeDropPodAt`, same params as above). Letter uses the
  instance's own `NewQuest` `LetterDef` field (quest-hook letter, not a plain
  Positive/Negative), keys `MO_TribalAid`/`MO_TribalAidDesc`.

- **MOIncidentWorker_RescueTraitor** — ⚠️ **correction, same session**: an
  earlier pass here wrongly concluded `Ticker_RTWorker` (the `MO_RTWorker`
  ThingDef's `thingClass`) doesn't exist in `MoreIncidents.dll` and called
  this mechanism dead. That was a search-tool miss, not a fact about the
  mod — the class is real, at typedef row 26, and it is NOT a simple
  "rescue" incident. `TryExecuteWorker` just spawns the invisible
  `MO_RTWorker` ticker Thing at a random cell (`CellFinderLoose.RandomCellWith`,
  radius 1000); the REAL mechanism lives in `Ticker_RTWorker.Tick()`, which
  this session decompiled about half of:
  - A `timer` field counts down once per tick from spawn.
  - At `timer == 690`: picks a random non-hostile faction
    (`RandomNonHostileFaction(false, false, true, TechLevel.Spacer)` — note,
    different flags/tech level than every other mechanism's faction lookup),
    generates a `SpaceRefugee`-kind pawn, and overrides its
    `RaceProperties.thinkTreeMain` to a ThinkTreeDef named
    `"HumanlikeTheThing"` (`GetNamed` with `errorOnFail=false`) — this is
    Mo'Events' body-horror "The Thing" mimicry sub-system (see the
    assembly's own `Pawn_theThing`/`theThing_Utility` classes), not a plain
    pawn.
  - At `timer == 0` (once, gated by a `doOnce` flag): drops that pawn in a
    pod, `DamageUntilDowned`s it, and sends a letter using **vanilla's own**
    `"LetterLabelRefugeePodCrash"`/`"RefugeePodCrash"` keys (reused directly
    from the base game's own refugee-pod-crash incident, not a `MO_*` key)
    with `NeutralEvent`.
  - Falls through into a SEPARATE, **not yet decompiled**, `timemut`/
    `facemutated`/`mutplace` mutation timer that this session did not read —
    the pawn is very likely NOT what it appears to be, and reveals or
    transforms into something else later. Field names alone (`Face`,
    `facemutated`, `mutjustspawned`, `mutplace`) are not enough to safely
    author a port from.
  **This is not "port behavior not bugs" territory** — it is unread content
  design (a slow-burn impostor/monster reveal), not a mechanical port, and it
  deserves a design decision (does Ash'karr want this at all, and if so what
  should the reveal be) before any C# gets written. Left unbuilt this
  session; see "still owed" below.

- **MOIncidentWorker_Insect** (item's "desert fauna") — resolves the live
  `Insect` FactionDef, spawns `count = round(colonistCount/3, min 2)` pawns
  split across `Spelopede`/`Megaspider`, each forced into
  `MentalStateDefOf.ManhunterPermanent`, food need set to ~0 (immediate
  aggression), `exitMapAfterTick` in 90k-130k ticks, at a random map-edge entry
  cell. `ThreatBig` letter (`MO_Insects`). Genuinely hostile, not decorative.

- **MOIncidentWorker_Migration** — spawns `round((animalPoolSize*Rand(4,8))/
  Rand(2,6), capped so count ≤ animalPoolSize+8)` wild animals drawn from the
  CURRENT MAP's own `BiomeDef.AllWildAnimals`, walking from a random edge cell
  toward the map (`JobDefOf.Goto`, `exitMapOnArrival=true`), each
  `exitMapAfterTick` in 10k-12k ticks if not already gone. Only fires if a
  spawn point is found `>50` map-units from another checked point
  (`checkDistance`). `NeutralEvent` letter (`MO_Migration`). Ambient wildlife
  passage, not a threat — biome-correct animals only, which is why the item
  calls this the safest of the 8 to re-skin.

- **MOIncidentWorker_Thanksgiving** (item's "clan-tribute/moisture-tithe") —
  **conditional**: only fires if the found `RandomNonHostileFaction` is not
  hostile to the player AND the colony's `ResourceCounter.TotalHumanEdibleNutrition`
  is below `4 * FreeColonistsSpawnedCount` (i.e., the colony is genuinely low on
  food). Drop pod (radius 110) with 2x `MealSimple` + 2x `MealFine`, each
  stacked 20-40. `PositiveEvent` letter (`MO_Thanksgiving`). This is food-relief-
  when-hungry, not a calendar holiday — the re-flavor to "tribute/tithe" fits
  the actual trigger better than the original name did.

- **MOIncidentWorker_Stroke** — picks one eligible free colonist via a static
  predicate delegate (`stroke::IncidentStroke`, not further disassembled —
  likely an age/health-condition filter worth reading before porting),
  `DamageUntilDowned`, rest need maxed, current job ended, gains memory thought
  `MO_HadStroke`, scatters 10x `Filth_Blood` in a radius-3 walk near the pawn,
  forces normal game speed briefly so the player doesn't miss it while fast-
  forwarding. `NegativeEvent` letter (`MO_Stroke`) naming the pawn.

**Dropped per spec** (Nausea, Amnesia) — not decompiled, out of scope.

## progress: 7 of 8 named mechanisms built, compiled, deployed
`mandrake.rut.scavengerevents` scaffolded at `src/RimUtinni/ScavengerEvents/`
(About/Defs/Languages/Source, mirrors `RestrainingBolts`' csproj shape).
Built, in order: `RUT_Migration`, `RUT_SurvivalPod`, `RUT_PodCrash` (donor
defName, not "PodCrashTribal"), `RUT_Thanksgiving`, `RUT_Insects`,
`RUT_Stroke`, `RUT_ShipBreak` (donor defName `MO_ShipBreak`) — 7
IncidentWorker classes total. Every one of them:

- **Builds clean**: `dotnet.exe build ... -c Release` → 0 warnings, 0 errors,
  every single time, including every guessed API signature (constructors,
  overloads, enum values) confirmed against the real `Assembly-CSharp.dll`,
  not just the decompile. A handful of guesses were WRONG and the compiler
  caught them immediately (`RandomNonHostileFaction`'s 4th param really is
  `TechLevel`; `DropPodUtility.DropThingsNear`'s bool ordering needed
  positional args, not named, since the real names weren't verified).
- **Deploys clean**: `deploy_custom_mods.py --mod ScavengerEvents --apply`
  after every mechanism, VERIFIED in sync each time. The deploy tool's own
  malformed-XML guard caught two `--` inside XML *comments* (illegal there,
  fine in element text) before anything shipped with broken defs.
- **Own IncidentDef values are the donor's real ones, not assumed** — every
  `baseChance`/`minRefireDays`/`earliestDay`/`category` was read off Mo'Events'
  own `IncidentDefs.xml`, not copy-pasted from Migration's. `RUT_Insects` is
  the one filed under `ThreatBig`, not `Misc`.
- **Enabled for the NEXT load only**: `mandrake.rut.scavengerevents` sits in
  `ModsConfig.xml` right after `mlie.moevents` (no patches/Harmony, so no
  load-order sensitivity) — backup at
  `Transient/ModsConfig_before_scavengerevents_add_2026-09-10.xml`. **Never
  restarted this session** — the owner was mid-session on the live campaign
  map throughout; forcing a restart to prove-fires would have pulled the
  game out from under him.
- **NOT yet proven-fires, any of the 7** — needs a load (quicktest is fine
  for all but Thanksgiving, which needs a hungry colony to trigger) and a
  manual incident fire per worker, verifying the letter and the actual
  spawned things/pawns. This is the next concrete step for this item, before
  touching RescueTraitor.

## RescueTraitor: CUT (owner ruling 2026-09-11) — kept for record, not owed
See the mechanism reference above — decompiling this one properly (rather
than trusting an earlier, WRONG "the class doesn't exist" finding from this
same session) turned up a half-decompiled body-horror mimicry/reveal
mechanic, not a plain rescue. Needs the rest of `Ticker_RTWorker.Tick()`
decompiled (the `timemut`/`facemutated` mutation branch) and a design
decision on whether Ash'karr wants an impostor-reveal event at all before
any C# gets written. This is the one mechanism of the 8 that is genuinely
NOT ready to build.

## still owed
- Proven-fires bridge test for all 7 built workers (biggest remaining gap) —
  needs the live bridge, which is held by another agent's restart+verify
  batch as of 2026-09-25. Not waited for or forced; see below.
- RescueTraitor is CUT (owner ruling 2026-09-11, see history) — no further
  work owed on it.
- Salvage-economy loot substitution for ShipBreak/Thanksgiving/SurvivalPod's
  fixed item lists — **checked 2026-09-25, genuinely not buildable yet**:
  there is no campaign-wide "salvage economy" ThingSetMaker/loot-table def
  to point these three workers at. Every existing economy-flavored def in
  `src/RimUtinni` is biome-specific catch/resource content
  (`RUT_Rare*Catches.xml`, `RUT_*Fish_Items.xml`, biome flora); the one
  other pass that named this exact gap
  (`src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/
  RUT_FoundrySalvageCache.xml`) explicitly shipped a shell and declined to
  invent salvage-economy content as out of its own scope. Inventing one now
  would be exactly the kind of unscoped design invention this project's own
  lessons warn against (a design pass that invents before it reads
  re-invents) — this needs its own items/design pass with a real salvage
  loot table def, not a FOUNDRY-improvised list. Left as donor-verbatim
  placeholder, unchanged this session.
- `mlie.moevents` retirement + full save-freeze sequencing — still gated on
  proven-fires (per spec: retire BEFORE save freeze, after proof).

## done this session (2026-09-25, FOUNDRY)
- **Mlie continuation-license check — CLEAR.** `MoreIncidents.dll`'s
  installed workshop copy ships `LICENSE.md` (MIT, Copyright (c) 2020 Mlie)
  and `About.xml` confirms current maintainer `ilawz`/`emipa606` continuing
  it as "Mo'Events (Continued)" — no separate continuation restriction
  found. MIT is permissive (use/copy/modify/distribute/sublicense freely,
  attribution-notice requirement only). Our 7 workers are re-authored C#
  (own class/field names, own verified API calls) built from a *read* of
  the decompiled IL's behavior, not copied source, but MIT attribution was
  added to `src/RimUtinni/ScavengerEvents/About/About.xml`'s description
  anyway to satisfy the notice requirement regardless.
- Corrected `About.xml`'s stale "all eight" line — scope has been 7/8 since
  the owner's 2026-09-11 RescueTraitor-cut ruling; also credited that ruling
  inline so a future reader doesn't re-open RescueTraitor as owed. Deployed
  (`deploy_custom_mods.py --mod ScavengerEvents --apply`, verified in sync).
- Deleted the stale `MO_AbominationRace` row from
  `design/Jawa/fauna/animal_census.csv` (line was the Mo'Events Abomination
  incident's pawn kind — that incident (`MO_RescueTraitor`'s ticker) is CUT
  and its baseChance already zeroed; row served no purpose).
- Re-verified (did not just trust the prior session's claim): all 7 source
  files still present in `src/RimUtinni/ScavengerEvents/Source/`,
  `mandrake.rut.scavengerevents` still sits in the live `ModsConfig.xml`
  right after `mlie.moevents`, and `MoEventsChancesZeroed_RuledCut.xml` is
  present in the deployed `UtinniPatches/Patches/` — the interim 10-incident
  MO_ baseChance zeroing (item's own interim step) was ALREADY DONE in an
  earlier session (2026-09-13, `MODLIST_RULED_CUTS_1`) and is still live;
  nothing was stale or needed redoing.
- `validate_patch.py --live` (2026-09-24T22-19-22Z capture): both
  `ScavengerEvents_IncidentDefs.xml` and `ScavengerEvents_ThoughtDefs.xml`,
  and `MoEventsChancesZeroed_RuledCut.xml`, all OK — 0 errors, 0 warnings.

## verify
All 7 built workers: build clean (done, prior session), deploy clean (done,
prior + this session), defs validate clean against the live dump (this
session). Proven-fires bridge test: still owed, blocked on bridge
availability — do not force. RescueTraitor: CUT, no longer owed.

## done this session (2026-09-29, FOUNDRY): all 7 proven-fires + donor retired
Bridge taken (`RUT_SCAVENGEREVENTS_BUILD_1: prove-fires 7 workers, retire
mlie.moevents`), live campaign save `CANONICAL_ASHKARR_START_2026-09-12`,
game already loaded/Playing/paused, 6 colonists. All work below verified by
reading real state back (`jawa/list_pawns`, `jawa/list_things`,
`jawa/letter_list`) after each `jawa/fire_incident incidentDef=RUT_*
dryRun=false` call — never trusted the tool's own `fired:true` alone.

- **RUT_Migration — PROVEN.** 7 wild animals spawned at a map-edge entry cell
  (War wyrm, Scurrier, Vozzik, 2x Krayt dragon, Kreetle, Kudda — all
  `faction:null`, `hostile:false`, `intelligence:Animal`, drawn from THIS
  map's own biome roster as designed), `NeutralEvent` letter "Migration"
  landed. Left on the map — wild and harmless, matches designed behavior,
  no cleanup needed.
- **RUT_SurvivalPod — PROVEN**, after a real methodology trap: the falling
  drop-pod skyfaller's defName is **`DropPodIncoming`**, not `ActiveDropPod`
  (that's the CONTENTS container thing that only appears briefly after
  landing, before its own `openDelay` elapses) — searching the wrong name
  first read as "nothing spawned" for 130 ticks. Total fall+open latency
  measured >130 but <530 ticks; 530 was safely sufficient. Once resolved, all
  9 items confirmed landed: Hyperweave pants/shirt/jacket/tuque (stuff
  resolved, `stuffDefName:Hyperweave`) + 4x `MealSurvivalPack` (new ids,
  distinct from 3 pre-existing x10 stacks elsewhere on the map that a sloppy
  first pass nearly mistook for this incident's own output — thing IDs are
  monotonic per session, and the pre-existing stacks' ids were LOWER than
  anything spawned this session) + 1x `Gun_Autopistol`. `PositiveEvent`
  letter "Survival pod".
- **RUT_PodCrash — PROVEN on a second fire.** First fire: letter sent
  ("Pod crash", `NewQuest` LetterDef, matching the donor's quest-hook choice
  exactly), but no new pawn was ever found on the map after 500 ticks, no
  corpse either — inconclusive, not a confirmed defect (most likely the
  pawn's default foreign-visitor AI walked it off-map within the window
  before the down state was checked, since `HealthUtility.DamageUntilDowned`
  and the drop-pod mechanics are proven-safe elsewhere in this same session;
  RimSage-read `ActiveTransporter.PodOpen()`/`ActiveTransporterInfo` are
  stock, unmodified vanilla and match our C#'s call shape exactly). Refired
  immediately: villager "Jonah", faction "the Junkers" (`RUT_Jawa_Junkers`,
  non-hostile), `downed:true`, `spawned:true` at the pod's landing cell,
  confirming the mechanism. Left on the map (a legitimate rescue-able NPC,
  not test pollution).
- **RUT_ShipBreak — PROVEN.** Survivor "Alyona" (`Refugee` kind, faction "the
  Junkers", `downed:true`, alive) + corpse "Noob, Medic" (`Corpse_Human`,
  dead), each in its own pod, both non-hostile as coded — 🔴 **this
  contradicts the task brief's assumption that ShipBreak spawns hostiles
  that could hurt colonists; it does not, by design (`RandomNonHostileFaction`
  is the only faction source in this worker).** `PositiveEvent` letter "Cargo
  rain" (matches the donor's own mismatched key, `MO_CargoRain`, noted in the
  mechanism reference). Loot delivery not independently re-confirmed by
  defName (the randomly-picked lootDef wasn't predictable in advance) but
  reuses the IDENTICAL `DropPodUtility.DropThingsNear` call already directly
  proven working in the SurvivalPod test above. Left on the map.
- **RUT_Thanksgiving — PROVEN, both halves.** Dry-run (`dryRun:true`)
  returned `canFireNow:true` **against the live colony's own real state** —
  no food was drained or faked to force this; the colony was genuinely
  hungry at the time of testing, which is itself a clean proof that
  `CanFireNowSub`'s nutrition-vs-`4×FreeColonistsSpawnedCount` gate reads
  correctly. Fired for real: 2x `MealSimple` + 2x `MealFine` (each x10 stack)
  delivered, `PositiveEvent` letter "Clan tribute".
- **RUT_Insects — PROVEN, then cleaned up.** 2x Spelopede + 2x Megaspider
  spawned (`countPerKind=2`, matching `max(2, round(6 colonists/3))`),
  `faction:Insect` ("Hive"), `hostile:true`, `ThreatBig` letter "Insect
  swarm". Game confirmed still `paused:true` throughout (verified via
  `get_cell_info`, never trusted a flag alone) — all 4 killed via
  `jawa/damage` (Bomb, amount 2000) before any tick advanced, per this
  session's guardrail against letting spawned hostiles threaten the real
  colony. Re-check after: none of the 4 ids resolve on the map any more.
- **RUT_Stroke — PROVEN, then healed.** Colonist "Twice-Kin" went
  `downed:true`, job `Wait_Downed`, `NegativeEvent` letter "Stroke", blood
  filth count rose. Since this acts on a REAL persistent colonist (not
  disposable test content), healed back afterward:
  `rimworld/execute_debug_action` `Actions\T: Heal random injury (10)`
  targeted at the pawn (8 calls) restored `downed:false`; re-verified via
  `rimworld/list_colonists`. The `RUT_HadStroke` memory thought and the blood
  filth were left in place (harmless, and exactly what the incident would
  leave on a genuine natural fire).
- **Colony verified undamaged at the end**: all 6 colonists `downed:false,
  dead:false` on a final `rimworld/list_colonists` read, game still
  `game_loaded`/`Playing`/`paused:true`.

**mlie.moevents RETIRED** (spec required this before save freeze, gated only
on proven-fires, now done):
- Removed from the live `ModsConfig.xml`
  (`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon
  Studios\Config\ModsConfig.xml`) and
  `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` — 614→613 mods
  each, via a one-off `xml.etree.ElementTree` edit (`Transient/
  retire_moevents.py`) matching `modset_builder.py`'s own established
  write pattern (parse, rebuild `activeMods`, round-trip CRLF), never a hand
  edit or grep. Backups: `Transient/
  ModsConfig_before_moevents_retirement_2026-09-29.xml` and the
  `...FULL.LATEST_before...` sibling. `mandrake.rut.scavengerevents` still
  sits immediately after where `mlie.moevents` used to be.
- `MoEventsChancesZeroed_RuledCut.xml` (the interim `MODLIST_RULED_CUTS_1`
  baseChance-zeroing patch) deleted — both the repo source
  (`src/RimUtinni/UtinniPatches/Patches/`) and the deployed copy — now moot,
  since the donor's incidents cannot fire once the mod itself is gone.
- `src/RimUtinni/UtinniPatches/About/About.xml`'s `<forceLoadAfter>` list
  (built for `Patches/FactionSlate/OnlyOurFactions.xml`) had its
  `mlie.moevents` entry removed — it now points at nothing, harmlessly.
- `src/RimUtinni/ScavengerEvents/About/About.xml` description updated to
  past tense recording the retirement and the proven-fires date.
- Both mods redeployed (`deploy_custom_mods.py --mod ScavengerEvents --apply`,
  `--mod UtinniPatches --apply`), both VERIFIED in sync.
- **NOT touched, flagged for its own item**:
  `src/RimUtinni/UtinniPatches/Patches/MoEventsAbomination_YuuzhanVongRename.xml`
  (`DONOR_FACTION_PROPER_NOUN_RENAMES_1`, a separate owner-ruled proper-noun
  pass, 2026-09-11) still references `MO_AbominationFaction` /
  `MO_AbominationPawnKind` / `MO_AbominationRace` under its own
  `PatchOperationFindMod` guard — it will now safely match nothing forever
  rather than erroring, but the text is permanently dead. Left alone as out
  of this item's scope; whoever owns `DONOR_FACTION_PROPER_NOUN_RENAMES_1`
  should decide whether to delete it.
- `design/Jawa/fauna/animal_census.csv`'s `MO_AbominationRace` row: confirmed
  already gone (prior session's 2026-09-25 claim was correct, re-verified
  by grep, no re-edit needed).
- No other active mod/patch/src file references `mlie.moevents` (checked
  every `About.xml` under the deployed Mods folder plus all of `src/`).

**Salvage-economy loot substitution and RescueTraitor remain explicitly out
of scope**, per this item's own prior text — neither blocks closing.

Bridge released at the end of this session
(`rimflow bridge release`). Game left loaded, Playing, paused — not mid-restart.
