<!-- status: state-of-play, Fable design pass 2026-09-06 for BENCH. Sibling:
     DROID_UNIFIED_FRAMEWORK_DESIGN.md (the Foundry-ready design + packets).
     No prior design/Jawa/droids/ folder existed; the droid docs live flat in
     design/Jawa/ (droid_ruling.md, droid_system_spec.md,
     droid_system_build_spec.md, droidworks_assumptions.md, droid_census_*.md,
     droid_verbs_decisions.json) and in reconciled_lore/08_droids.md (the live
     lore précis). This folder is NEW and holds only the program-level docs;
     nothing was moved. -->
# The droid program — where it actually stands (2026-09-06)

**One paragraph.** The owner remembers three moves in sequence: (1) tell FOUNDRY
to build "a huge amount of beautiful Droidworks", (2) retire three or four
problematic mods, (3) unify every droid on one framework (mechanoids excepted)
and then improve them. **Moves 1 and 3 are further along than he thinks — the
platform is built, compiled, code-reviewed and 80/80 kinds are already
generated onto it. Move 2 has not happened for any droid mod.** The whole
program is stalled at one gate: **Droidworks has never been enabled in the
real mod list**, so its five-state loop has never been proven live, and no
donor can retire until it is. Everything below is evidence for that sentence.

## 1. The ledger trail (rimflow, MEASURED 2026-09-06)

| item | state | what it is |
|---|---|---|
| `DROID_SYSTEM_EMBRACE_1` | done (closed `bbea1609`, 2026-08-29) | census → owner curates 39-row sheet → spec. Item file now at `infrastructure/state/items/` (moved by BENCH 2026-09-06) |
| `DROID_SYSTEM_BUILD_1` | **doing** (FOUNDRY) | the parent build item; greenlit 2026-09-01; open criteria: port waves at save boundaries, Cherry Picker cuts, DroidsAreMachines retirement |
| `DROIDWORKS_DLL_COMPILE_1` · `PHASE0_XML_1` · `ION_GUARD_1` · `DEF_GENERATOR_1` · `PILOT_GONK_1` · `CHARGING_TRIO_1` · `BOLT_CORE_1` · `WIPE_AND_SPIKE_1` · `FAMILY_LAYER_1` · `FLESHTYPE_NEEDS_GAP_1` · `ISFLESH_RELATIONS_CRASH_1` · `POWEREDDOWN_NOT_WIRED_1` · `CHARGER_STATE_MACHINE_SWEEP_1` · `GENERATOR_NAMING_DRIFT_1` | all **done** | Phase 0 + most of Phase 1 verbs, built 2026-08-30 → 09-05 |
| `DROID_PSYCHICENTROPY_NULL_GAP_1` · `DROID_DATASPIKE_SURVIVES_FAILON_1` | done (`fe5dfe7d`) | code-review bugs, 2026-09-05 |
| `DROID_KOTORDROIDS_PORT_WAVE1_1` | **ready** (freed 2026-09-05) | wave 1 found already generated; recipes wired; live proof owed |
| `DROID_DONOR_PATCH_GATE_1` | **ready** (freed 2026-09-05) | sites 2–10 patched (`src/RimStarWars/StarWarsPatches/Patches/DroidDonor_ABFGate.xml`, fires on ABF absence); Site 1 + cold load owed |
| `DROID_TILES_SOURED_TERRAIN_1` | doing, BLOCKED | needs Phase 3 (FDE goodwill layer) |
| `BUILDING_THEFT_HAULER_1` | doing | built (`src/RimMandrake/TheftHauler/`), Muckraker patch `MayRequire`-gated on Droidworks — inert until activation |
| `STARWARS_DONOR_SUNSET_1` | open | wave 1 (TSDA, themedsounds, swlights) EXECUTED 2026-09-02; wave 3 = the droid donors, "point at DROID_SYSTEM_BUILD_1, don't duplicate" |
| `WEAPONS_DONOR_RETIREMENT_1` | open on kotorcore only | kotorcore blocked on `_DroidsBase` (the KotOR droid race parent) |
| `KOTORWEAPONS_ABSORPTION_DANGLING_REFS_1` | proposed | 4 Armoury files dangle the day kotorcore retires — the pattern for every retirement below |
| `MECHANOID_ORIGIN_CANON_1` | proposed (owner) | the mindstone droid-mind race; touches the mechanoid/droid wall |
| `ION_STUN_IGNORES_BODY_SIZE_1` · `OTHER_STUN_WEAPONS_SURVEY_1` · `ION_TIERS_MEASURED_LIVE_1` (closed) | — | the ion side, already tracked separately |

Ledger events since 09-02 on any `DROID*` id: only bugfix closes and two
"still Phase-0" re-verifications (BENCH 09-04, FOUNDRY 09-05). **No Phase 1/2/3
feature work has started since 2026-09-01.**

## 2. What the owner ruled, verbatim, in order

- 2026-08-12 — *"a wreck has no power, hence it cannot explode. POWER DENSITY
  explodes, not the fact it's a machine."* (`droid_ruling.md` §6)
- 2026-08-13 — three-family capture ruling (KotOR = capture line; JDS force-kill
  "a feature"). **Superseded 2026-08-29** for JDS, see below.
- 2026-08-20 — *"Mechanoids are absolutely ON and are called the Forgotten Arsenal
  or the Forsaken Arsenal of the ancient Rakata race that built this place.
  Period."* (`droid_ruling.md`)
- 2026-08-29 morning — *"I'd love to just expand out and take in all the droid
  complexity right now… wrap our arms around what exists in the mods we've
  accepted already, then build it up, embrace it, and robustify it right now"*
  (files `DROID_SYSTEM_EMBRACE_1`).
- 2026-08-29 midday — *"This is such a big job, we're going to spec it out but
  then set it aside again for now… V1 we're just going to play with all three of
  these weird systems"* (parks it).
- 2026-08-29, the frozen sheet (`droid_verbs_decisions.json`, 39 decisions): the
  five states; *"Everything in Star Wars should feel like bringing it in to the
  shop, not magical tech"*; *"I think we're going to build our own mod bringing
  everything together"*; *"No. They recharge, not eat"*; *"Hate it. I'd really
  like there to always be parts. Except for the 'mechanoids' of the Forgotten
  Arsenal, because they are a totally different self-replicating tech (ancients)
  and are utterly incompatible with modern tech."*; JDS: *"if we're going to
  redo everything into one frame, no, they should work by the same logic"*;
  data spikes *"faction-oriented… obtained by destructively consuming a damaged
  droid head from that faction"*; the bolt *"is a big deal to the game"*; wipe
  *"Doesn't clear traits: randomizes them."*
- 2026-08-29 later — *"We've fallen in love with the full droid item… we will not
  build on any one of the packs, they all have too many flaws. Rather, we will
  borrow from them and make our own… port all the droids in the game to that
  one platform"* (reopens as `DROID_SYSTEM_BUILD_1`). Same day: name is
  **Droidworks**; packs *retire with credit*; art yanked in; HAR stays; chassis
  families over 1:1; JDS become capturable; shop CUSTOMER layer is a quest pack
  on top (`droid_system_build_spec.md` §8, `droidworks_assumptions.md` 1/4/17).
- 2026-08-31 — *"A hauler droid that can steal buildings is a fantastic idea! Use
  that too."* (`canon.yml wrecked_machines`)
- 2026-09-01 (question card) — *"Yes, start now"*; activation *"whenever the
  build + gate work is ready"* (`canon.yml droid_system`, `build_greenlit: true`).
- 2026-09-02 — *"file this as a ticket to track to get rid of them all… I bet we
  can get rid of Mlie and TSDA very quickly"* (`STARWARS_DONOR_SUNSET_1`).
- 2026-09-06 — the mindstone: a droid mind made from it *"is not really a droid
  any more: a new race"*; mechanoids + Rust Cathedral are *"a very different form
  of AI, not so artificial after all"* (`MECHANOID_ORIGIN_CANON_1`).

## 3. What exists on disk (MEASURED 2026-09-06 unless marked)

**`src/RimStarWars/Droidworks/`**, packageId `mandrake.rsw.droidworks`, deps HAR +
Harmony only, C# namespace `RimMandrake.StarWars.Droidworks`, defName prefix
`RSW_DW_` (naming grammar already applied).

| layer | content | state |
|---|---|---|
| C# | 20 files, ~1,280 lines (`wc -l`, excl. the 1,091-line generator): `Need_Power` + Harmony gate (`Patch_ShouldHaveNeed_Power`, also null-backfills `pawn.relations`/`psychicEntropy` for non-flesh humanlikes), `CompDWCharger`, `HediffComp_PoweredDown`, `HediffComp_IonOverloadsDroid`, `CompDroidDetonation` (charge × energyDensity, `GenExplosion`), bolt (install/remove/clamp job, `HediffComp_DWBoltResentment` — a stub accumulator nothing reads), `Recipe_DWMemoryWipe` (randomizes traits, clears relations/social, faction→player), data spike (`CompDWDataSpike` keyed to one faction, `JobDriver_DWDataSpike`), `Recipe_RebootDroid`, recharge think-tree job. Two DLLs compiled 2026-09-05 | five code-review passes (`78944107` latest); `code_review_status` reads CLEAN at `78944107` for the files checked |
| Defs | `RSW_DW_FleshType_Droid` (isOrganic false, mech corpse/wounds); `DW_Race_Base` (ParentName Human, foodType None, needsRest false, **intelligence Humanlike kept on purpose**, 4 recipes wired); 7 family abstracts `DW_Family_{Labour,Protocol,Astromech,Battle,Heavy,Probe,Power}` carrying `powerFallPerDay`/`energyDensity`/`chassisClass`; **57 races** (19 OuterRim + 22 KotOR + 16 JDS) and **80 kinds** (20 + 44 + 16); 3 chargers (socket / dock / nimbus r6.9); hediffs PoweredDown / IonOverload(placeholder) / RestrainingBolt / BoltResentment; items RestrainingBoltItem, DroidHead (**placeholder, one generic**), DataSpike (**one def, keyed `guy762_KotORFaction_RogueDroids`**) | `validate_patch.py` 0/0 at every close |
| Patches | `IonBuildup_PowersDownDroid.xml` (adds our comp to `RSW_JawaIon_Stun`) | FindMod-gated |
| Textures | 457 PNGs yanked at original texPaths (OuterRim/KotOR/JDS) | private play only |
| Generator | `Source/gen_droidworks_defs.py` + `extraction.json`; regenerates to scratch, diffs, `COMPS_OVERRIDE` table (GNK detonation); detonation rolled to 20 more energyDensity>0 races (`908094c3`) | deterministic |
| **PawnKindDef faction** | **0 of 80 kinds carry a faction** (grep `defaultFactionType`: 0/0/0) | no droid raids, no FDE membership on the platform yet |
| Research | **zero ResearchProjectDefs** (`waking_mind_ai_deep_dive.md`, MEASURED) | benches/spikes are ungated |

**Live proof achieved**: gonk pilot on a Droidworks-tier quicktest (2026-08-30):
spawn → ion ×20 → downed — but via vanilla `JawaIon_Stun` capMods, not
`RSW_DW_PoweredDown` (the wiring was then fixed twice, `483d5c4f`, and the
game-ending needClass bug caught by re-review `09d890c4`). The relations NRE fix
verified 60/60 on the *shipped* droid packs, not on a DW race. **Live proof
owed (8 open checkboxes across 6 items)**: PoweredDown lands and does not
self-clear; reboot recipe fires; a DW pawn generates without NRE; bolt/wipe/
spike offered and run on a ported KotOR kind; decay curve; ABF-absent cold load.

## 4. The live mod list vs the plan (MEASURED from the live `ModsConfig.xml`, 2026-09-06)

603 `<li>` entries active. Droid-relevant:

| packageId | active | role in the plan |
|---|---|---|
| `mandrake.rsw.droidworks` | **NO** | the platform — deployed to `Mods/`, never enabled |
| `killathon.artificialbeings` + `.syncore` (ABF/Synstructs) | yes | framework under KotOR droids — **retire** |
| `neronix17.asimov` | yes | framework under Droid Depot (auto-crafter) — **retire**; leaves 82 inert `Asimov.Need_Energy` entries in `WORLDMAP_V1_original.rws` (MEASURED 2026-08-30) |
| `neronix17.outerrim.droiddepot` | yes | 20 kinds/19 races, wave 2 — **retire after port** |
| `guy762.kotordroids` | yes | 44 kinds/22 races, wave 1, pure XML — **retire after port**; carries `guy762_KotORFaction_RogueDroids`, the only permanent-enemy droid faction |
| `guy762.mm.kotorcore` | yes | its `_DroidsBase` folder (gated `IfModActive="guy762.KotORDroids"`) holds the KotOR race parent, 9 droid-equipment apparel files (the six-slot module system), batteries, backstories, research — **Droidworks' absorb list**; `STARWARS_DONOR_SUNSET_1` wave 3 |
| `m3.continued.jangodsoul.starwars.tsda` (JDS) | **NO — retired 2026-09-02** | wave 3's 16 races already regenerated on Droidworks; the CIS faction went with it |
| `guy762.kotorweapons` | NO (retired 2026-09-01) | — |
| `erdelf.humanoidalienraces` | yes | stays (ruled) |
| `frozensnowfox.complexjobs` | yes | ~30 Asimov patches, all `MayRequire`-gated — no-op on retirement (verified 2026-08-30) |
| `neronix17.outerrim.galacticempire` | yes | `OuterRim_ImperialKXSecurityDroid` rides a Droid Depot race — dangles when Depot retires |
| `mandrake.rsw.msedroidfix` | yes | our fix for a Droid Depot texture — dies with Depot |
| `mandrake.rut.doctrine` | yes | `DroidsAreMachines.xml` (retires per wave), `NoDroidManufacture.xml` (Depot factory unbuildable — moot after Depot) |
| `mandrake.rut.patches` | yes | `Jawa_Droid_{Grunt,Heavy,Specialist,Leader}` (`JawaFactionRoster.xml`) on **Droid Depot races**; `Jawa_FreeDroidEnclaves` FactionDef; `RimUtinni/PawnFlavor` FDE droid backstories |

## 5. The "three or four problematic mods" — named

The owner's memory maps onto **three frameworks and two content packs** (TSDA
being the third content pack, already gone):

1. **ABF + SynCore** (`killathon.artificialbeings`, `.syncore`) — retires when
   nothing loads that references `ArtificialBeings.*`. Sites 2–10 already
   auto-patch on its absence. Site 1 (`guy762_KotORDroidBase`'s
   `CompCoherenceNeed` + `ParentName="ABF_Thing_Synstruct_HumanlikeBase"`)
   **becomes moot the moment `guy762.kotordroids` retires**, because kotorcore
   only loads `_DroidsBase` when kotordroids is active. Order matters.
2. **Asimov** (`neronix17.asimov`) — retires clean once Droid Depot retires
   (verified 2026-08-30); save-scrub of 82 need entries optional.
3. **Outer Rim – Droid Depot** — retires once the 4 FDE kinds, the Galactic
   Empire KX kind, `NoDroidManufacture.xml`, `MSEDroidFix`, `DroidFemaleTexture_Fix.xml`
   and every `OuterRim_*Droid*` reference in our own XML are repointed/gated.
4. **KotOR Droids** (`guy762.kotordroids`) — retires once its equipment/module
   defs are absorbed, its rogue-droid faction is replaced or re-keyed, and the
   frozen save is checked for its FactionDef.

## 6. What is designed vs what is open

**Designed and ruled (no design work left)**: five states; shop-centric verbs
(what's cut/what replaces it); embodied software / head identity / wipe
randomizes; behaviour triad (born/installed/experienced); faction-keyed spikes;
bolt consequences; detonation model; HAR substrate; chassis families; JDS
capturable; mechanoid wall; customer layer = quest pack; FDE goodwill cap
mechanism (`GoodwillSituationDef`, `restraining_bolt_technical.md`).

**Built but untested live**: every verb in §3.

**Designed, unbuilt (build spec §3 units)**: #10 format tiers · #11 service-record
drift · #12 module personality · #13 shop benches / reassembly harness / head
identity comp · #14 wild-droid faction + reprogram-as-recruit · bolt
consequence layer beyond the accumulator (#7 payoff) · per-faction heads and
spikes (#8 as specced) · ion shield-break + body-size scaling (#3 halves) ·
research rows · droid factions on the platform.

**Ruled by the owner 2026-09-06 (15 cards, verbatim in
`DROID_UNIFIED_FRAMEWORK_DESIGN.md` §0)**: activation = minimal-list proof then
full list · **no rogue droid faction, ever** — droids ride every faction's
loadouts (Empire attack droids are the capture line; traders carry protocol
droids with a real trade advantage; FDE hostile only in-territory; Trade Moot
buys/sells) · mindstone race = chassis + special head · needs by format tier ·
fine parts from the start · head-gate confirmed, brains import-only forever ·
wipes severe with permanent hardware quirks · modules loot-only, a grossly
inferior Primitive fabricable tier + the G2 · detonation reviewed as a savegame ·
port at the next fresh start · scrub the 82 Asimov entries · reboot Crafting 4 ·
Distress Call re-pointed as the crashed-droid rescue · Oracle voice designed
dormant · B and C before D.

**Still open after the rulings (not owner calls — measure or build)**: which
droid FactionDefs are scribed in the frozen/campaign saves (A3, haiku — ⚠️ the
sibling file `A3_frozen_save_droid_census.md` in this folder is a scan-grade
string count whose comparison BENCH has already voided: its second file was a
25-mod Droidworks quicktest autosave, not the campaign; it does not answer A3,
which needs `<def>NAME</def>`-shaped reads via the `rimworld-savegame` skill); the
exact per-faction droid share of raid points (C1 tunes at the bench); the G2's
art (owner's eye, B9); whether `btd.gbp.shippack.kotor.vge`'s quest sub-mod is
`LoadFolders`-gated on kotordroids (C7 reads it before patching).

**Housekeeping already done**: `DROID_SYSTEM_EMBRACE_1.md` moved to
`infrastructure/state/items/` (BENCH, 2026-09-06).

## 7. Cross-links that pull on this program

`BUILDING_THEFT_HAULER_1` (Muckraker chassis) · `DROID_TILES_SOURED_TERRAIN_1`
(FDE goodwill) · `PAWN_FLAVOR` FDE droid backstories (already authored against
KotOR spawnCategories — must survive the port) · `NINEFOLD_MISSING_EVENT_HOOKS_1`
("droid-online" hook for Ohm) · `waking_mind_ai_deep_dive.md` (The Unbolting
research tab: droid construction rows as the liberation curriculum) ·
`sw_mod_concepts_triage.md` §G (chassis personality bias, protocol-droid
pedantry, repair-shop pack) · `ORACLE_EXPERIMENT_SPIKE_1` (client rewrite to
`claude -p`; droid dialogue rides it) · `MECHANOID_BIOME_PRESENCE_REVIEW_1` ·
`design/Jawa/explosion_energy_model.md` (the general detonation model
Droidworks' comp is the pawn half of).

UNMEASURED and worth a haiku sweep before any retirement: whether
`guy762_KotORFaction_RogueDroids`, `JDSCIS_CIS_Faction` or
`OuterRim_RogueDroidColony` are scribed in `world/WORLDMAP_V1_original.rws` and in
the campaign save (a FactionDef in a save that no mod defines is a Scribe
failure on load, not a def-loader warning — `rimworld-savegame` skill).
