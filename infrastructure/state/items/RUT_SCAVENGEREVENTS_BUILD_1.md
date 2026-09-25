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
