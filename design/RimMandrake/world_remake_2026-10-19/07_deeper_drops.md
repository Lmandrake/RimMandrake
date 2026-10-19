# World remake 07: deeper drops and a four-profile mod structure (2026-10-19)

FOUNDRY, offline. No game, no bridge, no ModsConfig write. **Nothing here is a ruling**; every row is a
recommendation for the owner. Asked for by the owner 2026-10-19: *"Drop things like map edit as well that sometimes
create problems. If we're going to drop things we might add back later, suggest going deeper."*
Builds on 01 (classes A–F), 05 (112 SAFE / 12 HOLD, the 367 candidate). Per-mod table:
`07_profile_assignment.tsv` (536 rows: packageId, name, profile, 01 class, kind, reason).

## 0. Answer

**Go deeper by splitting the one list into four profiles**, not by deleting more mods. 157 mods leave every profile.
The rest sit in the smallest profile that needs them, so the day-to-day DEV list drops from 367 (05's candidate)
to **117**.

| profile | built as | mods | what it is for |
|---|---|---:|---|
| **DEV** | Core+5 DLC, our 62 (less 1 demo), the frameworks our content hard-depends on, test instruments, and their closure | **117** | every proof, quicktest, bridge session, def dump. Minimal and deterministic: no map-gen editors, no event mods, no combat rewrites, no UI/QoL |
| **TEST** | DEV + content that ships and that the scenario needs, incl. world-borne mods (factions, sites, outposts) | **205** | scenario tests and **the profile the start save is made on**. Without these mods at the faction pass, the world never gets their content |
| **AUTHORING** | TEST + 20 editors/world-gen tools | **225** | only when we author (world remake, pawn/ideo/scenario edits). **Never loaded for a test.** Anything saved under it is censused against TEST before use (§6) |
| **SHIP** | TEST − instruments + 130 QoL/UI/cosmetic/decor/library + ruled ship features | **329** (+ up to 24 pending rulings) | what a player gets, and what the owner plays |

| label in the TSV | mods | meaning |
|---|---:|---|
| DEV | 111 | in DEV, TEST, AUTHORING, SHIP |
| DEV-INSTR | 6 | in DEV, TEST, AUTHORING; **not** SHIP (RimBridgeServer, Incident Disabler, Better Stacktraces, LogAfterDefError, our LoadTracer and RimDefDump) |
| TEST | 88 | TEST, AUTHORING, SHIP |
| AUTHORING | 20 | AUTHORING only |
| SHIP | 130 | SHIP only (incl. the ruled fog pair and Facial Animation) |
| SHIP-PENDING | 24 | class E and map-gen mods: never in DEV/TEST; in SHIP only if the owner rules them in |
| DROP-W1 | 39 | Retirement Wave 1 (owner 2026-10-10) |
| DROP-112 | 112 | 05 SAFE drops |
| **DROP-DEEPER** | **6** | **new here** (§4): Map Designer, Biome Transitions, Better Traders, Tribal Furniture, Biomes! Fossils, Ancient urban ruins |
| total | 536 | 111+6+88+20+130+24+39+112+6 |

**The deeper cut, compared with 05's 367 candidate:**

- **6 drop outright** (§4).
- **20 authoring tools** go to AUTHORING (§2).
- **154 leave DEV and TEST but stay in SHIP**:
  - 130 QoL, UI, cosmetic, decor and library mods (§3);
  - the fog pair and Facial Animation, which are ruled or kept for ship but hostile to evaluation;
  - the 7 class-E "tier exceptions" that 05 had kept in its base profile;
  - Geological Landforms;
  - Yayo and Stronger Scaling.

**Top 10 problem mods** (§4b, each cited):

1. Real Fog of War
2. Map Designer
3. Better Traders
4. Tribal Furniture
5. Yayo's Combat 3
6. CAI 5000
7. Worldbuilder
8. Rimsential Total Control (Faction Loadout)
9. Facial Animation
10. Out of Combat ReBoost

Four more are HIGH or MED but cannot leave DEV, because our content hard-depends on them:

- Vehicle Framework
- Research Reinvented
- Outer Rim Core
- RimBridgeServer

## 1. Method and instruments

- Base: the 536 of `infrastructure/state/modlists/ModsConfig.FULL.DONOR_FREE_536_weathersuite_2026-10-19.xml`.
  Classes are parsed from 01's tables and 05's HOLD/SAFE tables; the counts reproduce exactly (B 39, C1 28, C2 124,
  D 21, E 32, F1 24, F2 232, HOLD 12, SAFE 112).
- **Closure** (the same method as 05, extended to every profile):
  - Every one of the 536 About.xml files was read FRESH from its Steam/workshop folder (0 missing). Each
    `modDependencies` entry (plus `v1.6` by-version) counts as an edge.
  - So does the 10-10 `class_ref` edge from `mod_audit/facts/mod_facts.jsonl`.
  - The rule: a mod in profile P pulls everything it needs into P or lower. AUTHORING may only need DEV or AUTHORING.
  - Run to a fixpoint. Result: **0 retained mod needs a dropped one**, and 15 mods were pulled down (§5).
- **Authoring-tool use:**
  - `git grep` of each tool's packageId, name and DLL namespace over `src/` (.cs/.xml, excluding obj/bin), every
    `*.py`, `skills/` and the live `infrastructure/state/items/`.
  - Each tool's live `Config/Mod_*.xml` was read to see whether leaving it would lose any settings.
- **Problem history:**
  - A fan-out over `infrastructure/state/lessons/`, `facts/instrument_traps.md` and `facts/tool_traps.md`, the
    memory notes, the handoffs, the ledger shards, live and closed items, `mod_audit/` deep dives, the skills'
    references, and `mod_facts.jsonl` `log_error_occurrences`.
  - That found 46 rows. 8 citations were re-read by hand and all 8 matched.
- **QoL / cosmetic / UI classification** is my judgment from name, def types (`defs_by_type`) and registry `fit`. It
  is recorded per mod in the TSV `kind` column (UI, QOL, COS, DECOR, FW, SCEN, WORLD, blank = content).
- **UNMEASURED:**
  1. **Save-borne residue.** Whether any SHIP-only or AUTHORING mod leaves classes or defs in a save made under
     its profile. Run `save_class_census.py` / `save_def_census.py` against TEST before a save is promoted.
  2. **Load time and TPS** of each profile. No profile has been loaded.
  3. **Per-mod Player.log attribution.** It is by prefix or frame, and it charges our own ResearchRetag
     collisions to DBH, Roots and Stews.
  4. **Hidden runtime behaviour.** Whether any SHIP-only QoL mod changes a number one of our tests asserts.
     Out of Combat ReBoost is the one measured case.
  5. **Faction Loadout's preset store.** No `Config/Mod_*` file for it was found, so I could not tell whether its
     presets are what bypass Jawa apparel.

## 2. The 21 authoring and dev tools (01 class D)

Our bridge already authors most of what these tools do:

- the planet: tiles, biomes, rivers, roads, mutators, landmarks, settlements (`skills/rimbridge/SKILL.md:31`);
- map terrain, plants and things;
- deep pawn editing;
- faction relations (`design/Jawa/bridge/BRIDGE_CAPABILITY_ROSTER.md` §6).

The GUI editors stay useful for hand authoring, but **no test needs them**.

| tool | uses found in our code | live config | profile | why |
|---|---|---|---|---|
| RimBridgeServer | 101 src files, csproj of JawaBench.BridgeTools | — | DEV-INSTR | the test instrument; never ships |
| Incident Disabler | none | — | DEV-INSTR | evaluation aid (01 §7) |
| Better Stacktraces | `GimmeSomeSlack/northstar/proof_all.py:123` parses its `[Ref]` lines | — | DEV-INSTR | log instrument |
| Log After Def Error | `Utils/harvest_log.py:638` parses its manifest | — | DEV-INSTR | log instrument |
| Cherry Picker | 16 src, 55 py, 10 live items | 99.7 KB of cuts | **DEV** | its cuts shape the def set; leaving brings the cut defs back. Out only when the cuts are baked into our patches (`CHERRY_PICKER_RESTORE_FROM_SHIP_PROFILE`) |
| Map Designer | 3 src: our two **countermeasures** (`RM_PyrelandsDensityEnforcer.cs`, `RM_SeabedFloorLife.cs:67`) | 7.8 KB: ore commonality, mutators, rocks, `niSize 0.75` | **DROP-DEEPER** | the owner's "map edit" example; a measured antagonist (§4) |
| Worldbuilder | skills only (`generating-a-world.md:8`) | `Worldbuilder/` folder | AUTHORING | loads the TidallyLocked preset at generation; ConfigErrors NRE every load (`config_error_baseline_2026-09-06.json:52`) |
| WorldEdit 2.0 | 0 (JawaBenchWorldEdit2.cs is our own, named after it) | — | AUTHORING | owner-adopted world editor |
| Character Editor (+ Retextured) | 2 src comments, 1 skill **warning** (`rimworld-xenotypes/references/appearance.md:78`: editing a non-human head breaks it) | `CharacterEditor/` folder | AUTHORING | the bridge covers scripted pawn edits; hand edits only |
| Rimsential Total Control (`co.uk.epicguru.factionloadout`) | `SpeciesStartingGear_Tuning.xml:37` names it the prime suspect for bypassing pawnkind apparel | not found (UNMEASURED) | AUTHORING | **must not be in a test**: it may override the gear we tune |
| Rim Control | 0 | `Mod_3774299554_ItemControlMod.xml`: **every override list empty** (MEASURED) | AUTHORING | leaving it loses nothing |
| Faction Customizer | 0 | empty settings (MEASURED) | AUTHORING | |
| Prepare Landing, Map Preview, Modify Tiles at Game Start, MutatorWorldIcons | skills only | `PrepareLanding/` is a surface the game deserialises at startup (`rimworld-savegame/SKILL.md:24`) | AUTHORING | world-map/landing UI; no world-making for players |
| Persistent Precepts, Scenario Amender | 0 | — | AUTHORING | ideoligion/scenario editing only |
| What's That Mod, Better ModMismatch Window | 0 (`def_diff.py` "modMismatch" is a false hit) | — | AUTHORING | manual dev aids with no consumer |

Our own mod `mandrake.rut.birthhatchdemo` (About.xml: *"A DEMONSTRATION mod, not campaign content"*) also goes to
AUTHORING.

World-generation HOLDs from 05 go to AUTHORING too:

- `7f.alienworlds` and `7f.alienworlds.tidallylocked`;
- `boots.sensiblefactions`;
- `oblitus.mylittleplanet`, whose scale slider Worldbuilder overwrites (`generating-a-world.md:8`).

`broms.deeporbit` stays in **DEV**. The fixtures' `Orbit2` layer needs it to load at all (lesson
`20261016T155408Z`). It leaves when the `_AREAFIX2` fixtures do.

## 3. QoL, UI, cosmetic, decor, library (130 → SHIP only)

These mods have zero hard dependence from us or from any TEST mod (the closure in §1). They leave DEV and TEST, and
the owner still plays with them in SHIP:

| kind | n | examples |
|---|---:|---|
| QoL | 54 | Achtung!, Allow Tool, Pick Up And Haul, Common Sense, Replace Stuff, [FSF] Complex Jobs, **Out of Combat ReBoost** |
| UI | 34 | Numbers, RimHUD, Work Tab, Dubs Mint Menus/Minimap, Camera+, Designator Shapes |
| cosmetic/sound | 19 | Show Me Your Hands/Tools, Large Pawns, Dynamic Effects Forge, RimTunes, Better Explosions |
| decor | 14 | Floor Lights 2, Signs and Comments, Uncle Boris' Furniture, Gerrymon's Dungeon props |
| library | 5 | HugsLib, Prepatcher (CAI needs it), Linkable Settings, Dubs Rimkit, B&S Optional |
| ruled ship features | 3 | Real FoW + CAI 5000 (Route B; **always together**), Facial Animation (C16 keep) |

The full list is in the TSV (`profile=SHIP`).

🔑 **Behaviour-changing QoL is the reason to go this deep.** Out of Combat ReBoost walks colonists ~2 ticks/cell
while `MoveSpeed` still reads 4.6, a wrong number for any fixed-tick bridge test (lesson
`20261011T025641Z-BENCH-owner-s-full-list-out-combat.md`). Pick Up And Haul, Common Sense and Complex Jobs change jobs
and work types in the same way.

## 4. Deeper drops and problem mods

### 4a. DROP-DEEPER (6): leave every profile

All six have **0 retained dependants** (closure). Our src still names three of them in soft form: Map Designer's two
countermeasures, and `loadAfter` lines for Fossils and Ancient urban ruins. Delete those references in the same change.

| mod | evidence | what we would miss | add back when / where |
|---|---|---|---|
| Map Designer `zylle.mapdesigner` | Silently caps XML `plantDensity` at 1.0 at startup and folds the ratio into regrow days, with no log line (lesson `20261011T163154Z-BENCH-map-designer-zylle-mapdesigner-silently-caps.md`; bisected 2026-09-18, `Pyrelands.xml:120`). Re-applies biome densities **inside** `GetOrGenerateMap` (`RM_SeabedFloorLife.cs:67`). | the owner's hand-repair of a badly generated landed map | if a landed map needs hand repair: AUTHORING only, never TEST. Cost: none; the enforcers stay harmless |
| Biome Transitions `m00nl1ght.geologicallandforms.biometransitions` | map-generation edit; no dependence of ours (01 §4; C06) | blended biome edges on maps | C06 experiment (`BIOME_TRANSITIONS_WITH_BAROQUE_JUDGE`), SHIP only |
| Better Traders `jm.bettertraders` | full-def replace of trader kinds; a runtime remover cut `Base_Outlander_Standard` 69→64 rows and **our trader rows were absent**; hours lost, unresolved (`bridge_debugging_system.md:488`) | 20 rebalanced TraderKindDefs | never into TEST; SHIP only after our trader rows are proven present with it loaded |
| Tribal Furniture `xercaine.tribal.furniture` | ships 26 DLLs including the game's own Assembly-CSharp; silently killed Interaction Bubbles, which **our** SpeakUp → JawaVoice chain needs (`skills/rimworld-modding/references/traps-mods-and-managers.md:67`) | 16 tribal furniture defs | re-add a fixed upload, or port 2–3 pieces as `RM_` decor |
| Biomes! Fossils `biomesteam.biomesfossils` | top Player.log error source among the 468: 51 distinct `BMT_` errors (`mod_facts.jsonl:77`). Attribution UNMEASURED: the prefix is shared with retired Biomes! Caverns. Dropping it is also the measurement | 74 fossil ThingDefs | SHIP, if the 51 errors persist without it (then they were not its) |
| Ancient urban ruins `xmb.ancienturbanruins.mo` | 6-DLL custom map generation, a live faction, 2 def errors (`mod_facts.jsonl:182`); 51% already cut | ruins on maps, its faction | "not save-safe" (RETIREMENT_WAVE_1.md:30) binds OLD saves only. **The new start save is the cheapest excision we will ever get.** The `_AREAFIX2` fixture loads keep it until they retire |

Moved out of DEV and TEST (into SHIP-PENDING or SHIP) rather than dropped:

| mod | evidence | trigger to re-admit |
|---|---|---|
| Geological Landforms | map-generation edit (C06: *"Landforms seems like a big lift"*) | C06 `LANDFORMS_REPLICATE_OR_KEEP_EXPERIMENT`; re-review biome visuals with it loaded (add-back cost) |
| Yayo's Combat 3 | +43% melee attack-speed bug and silent mech inflation (`mod_deepdive_yayo.md:22`, `:117`); Harmony NRE in quicktest map generation (`LOAD_GAME_READY_MAPGEN_CRASH_1.md:35`) | the Yayo ruling; the deep dive says remove and port |
| Stronger Quality Scaling | quality becomes a cliff with Yayo (`mod_deepdive_yayo_full.md:21`) | ruled with Yayo |
| the 7 class-E "tier exceptions" 05 kept in its base | Mood Chain Reaction (`bridge_debugging_system.md:486` blames an "MCR mood-chain logger" for the Verse.Log cap; attribution unclear), Performance Optimizer (`COLD_LOAD_STALL_INTERMITTENT_1.md:12`), Melee Animation, Realistic Darkness, Interaction Bubbles, Facial Animation, Stronger Scaling | SHIP, each by its own ruling. **Exception: Interaction Bubbles cannot leave DEV** (§5) |

### 4b. Problem mods on the list, ranked

The full 46 rows (kinds, severity, ≤4 citations each) are folded into the TSV's `reason`. The table below holds the
top problems that still sit on the live list:

| # | mod | problem | cite | profile here |
|---|---|---|---|---|
| 1 | Real Fog of War | IndexOutOfRange every Update wedged `bland_world.setup` and every tick; hides things off-colony; `unfogAll` wedges 4 min | `design/RimMandrake/bridge_debugging_system.md:484`; `live_test_hang_runbook.md:16` | SHIP (Route B), never DEV/TEST |
| 2 | Map Designer | silent biome-density rewrite | lesson `20261011T163154Z…` | DROP-DEEPER |
| 3 | Better Traders | our trader rows vanish | `bridge_debugging_system.md:488` | DROP-DEEPER |
| 4 | Tribal Furniture | game DLLs killed Interaction Bubbles | `traps-mods-and-managers.md:67` | DROP-DEEPER |
| 5 | Yayo's Combat 3 | melee bug, map-gen NRE | `mod_deepdive_yayo.md:22`; `LOAD_GAME_READY_MAPGEN_CRASH_1.md:35` | SHIP-PENDING |
| 6 | CAI 5000 | strips other mods' fog; blinded gravship landing | `items/closed/GRAVSHIP_LANDING_FOG_REVEAL_1.md:4` | SHIP (with Real FoW) |
| 7 | Worldbuilder | NRE every load; overwrites My Little Planet | `config_error_baseline_2026-09-06.json:52`; `generating-a-world.md:8` | AUTHORING |
| 8 | Rimsential Total Control | suspected apparel-generation bypass | `SpeciesStartingGear_Tuning.xml:37` | AUTHORING |
| 9 | Facial Animation | removes vanilla head draw, vetoes gene render nodes | `mod_deepdive_faces.md:91`, `:97` | SHIP (C16) |
| 10 | Out of Combat ReBoost | wrong movement numbers | lesson `20261011T025641Z…` | SHIP |
| — | Vehicle Framework | `Game.Dispose` NRE crashed `start_debug_game_ready`; VehiclePathFinder NRE per map | `handoffs/FOUNDRY_REBOOT_HANDOFF_202609241836.md:66` | DEV (hard dep: F1) |
| — | Research Reinvented | self-prerequisite → infinite recursion crash (guarded by our patch) | `items/closed/QUICKTEST_POSTSETUP_CRASH_1.md:96` | DEV (F1) |
| — | Outer Rim Core | ctor NRE every load; crashed scratch tiers | `items/closed/HELIX_TELLUROX_SHELL_LOAD_CRASH_1.md:49` | DEV until replicated (01 §9). **Problem history is a reason to move that port forward** |
| — | RimBridgeServer | debug-action enumeration NREs, main-thread wedge | `items/closed/DEBUG_ACTION_ENUM_CRASH_1.md:1` | DEV-INSTR (irreplaceable) |
| — | Prepatcher | fatal when an add-on is orphaned; game loads unpatched | `traps-mods-and-managers.md:59` | SHIP (only CAI needs it): out of DEV |
| — | Show Me Your Hands | InvalidProgramException with ModularWeapons2 (MW2 retired) | `items/closed/SMYH_MODULARWEAPONS_PAWNGEN_CRASH_1.md:8` | SHIP |

Already leaving through Wave 1 or the 112, with their problems for the record:

- MinifyEverything: NRE killed the full-list load and reset ModsConfig to Core (`handoffs/BENCH_HANDOFF_202610101044.md:8`).
- Raid Protection Fee: `fire_raid` reported success with zero arrivals (`bridge_debugging_system.md:436`).
- RimAI Core/Framework: wrong load order, so the mod was silently dead (`traps-mods-and-managers.md:76`).
- Quarry: duplicate Sandstone key.
- Minerals Rock, Roots, VCE Stews, Biome Compatibility Project, Vanilla Backgrounds Expanded.

**Victims, not causes** (kept): Giddy-Up, VGE, BCP. Their errors came from our own cast/diet data
(`items/closed/GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1.md:14`).

⚠️ A 2026-10-04 handoff (`handoffs/FOUNDRY_REBOOT_HANDOFF_202610040002.md:31`) says Real Fog of War was removed from
ModsConfig. It is on today's 536 list. The handoff is stale; the list is the record.

## 5. Closure: what the profiles pulled down (15)

| mod | pulled to | by | note |
|---|---|---|---|
| Interaction Bubbles `jaxe.bubbles` | **DEV** | SpeakUp (F1, needed by our JawaVoice) | class E (clutters screenshots) but cannot leave. Turn bubbles off in review **settings** instead |
| LWM Deep Storage, then RimFridge | DEV | Outer Rim Core (C1 HARD) | they leave when the Outer Rim port lands |
| Vanilla Vehicles Expanded | DEV | Alpha Vehicles Neolithic (C1 HARD via our DesertVehicleReskin) | |
| Intimacy – Friends n' Lovers | DEV | Intimacy – Gender Works (F1, C20 founder genes) | |
| Biomes! Framework | DEV | More Vanilla Biomes (C1 HARD) | |
| CQF, VFE Architect, VAE Accessories, Minerals Framework, BiomesKit, Fortified Features Framework, Custom Ritual Framework, Map Mode Framework | TEST | their TEST dependants (05 HOLDs: Dungeon Pack, Fortifications, More Utility Packs, Minerals Sparkle, Primordial Geysers…) | 05's "drop the dependant too" is not proposed: those are shipped content |
| Gravship Exporter | SHIP-PENDING | Gravship Crashes | an authoring tool that ships only if Gravship Crashes is ruled in |

One edge reads as a conflict but is not: `aoba.fortress.industrial` → `vanillaquestsexpanded.ancients` (Wave 1). It
is a `PatchOperationFindMod` (`…/2561619583/1.6/Patches/VanillaQuestsExpandedAncients.xml:7`), which is load-safe.
**Wave 1 is not affected.**

## 6. Add-back cost by kind, and the one rule that matters

| kind | add back mid-save? | cost |
|---|---|---|
| UI, QoL, library | yes | ~free. UNMEASURED per mod: whether *removing* it later leaves Scribe residue |
| cosmetic, decor | yes | free to add. Once built, decor is save-borne: removing it later costs a save census |
| content | yes, for items/recipes/research | low; its things appear from then on |
| **world-borne** (factions, outposts, sites, trader ships; TEST `kind=WORLD`) | **no**. A faction absent at the faction pass is absent forever (CLAUDE.md, no-worldgen ruling) | that is why they are in TEST, the start-save profile |
| map-generation edits | yes, but every biome visual judged without them must be re-judged | a review sitting |
| authoring tools | yes | none for us, **if** nothing authored under AUTHORING is saved without a census |

🔴 **Run the remake in AUTHORING, and promote the start save to TEST with a census.**

1. Generate and stamp the remake world in AUTHORING (= TEST + tools). That way the WORLD mods are present at the
   faction pass.
2. Before the start save is used, run `save_class_census.py` and `save_def_census.py` against the TEST list. Any
   AUTHORING-only class or def in the save (Worldbuilder's 8 defs, Alien Worlds presets, Faction Customizer state)
   is a stop.

## 7. What to do with this

1. **Owner rulings asked for:**
   1. the profile structure;
   2. DROP-DEEPER ×6;
   3. Geological Landforms out of DEV/TEST;
   4. the 7 class-E exceptions out of DEV/TEST.
2. Build: four `modset_builder.py` tiers, `dev`/`test`/`authoring`/`ship`, generated from this TSV with the closure
   check built in. Not built here.
3. Wave 1 (running now) is unaffected. The DROP-DEEPER and profile split land after it, on a fresh candidate.
