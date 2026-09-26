# THEFORGE_RM_MOD_BUILD_1 — build RM_TheForge as its own RimMandrake mod

**the Forge**

Phase A row 21 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.


## 🔑 STATE — MEASURED 2026-09-23

### 1. Step table

| step | state |
|---|---|
| 1 scaffold | ⛔ OWED — `src/RimMandrake/TheForge` does not exist (checked: `ls src/RimMandrake/` — 34 sibling mods, no TheForge). Not a twin: §2a row 21 says `PROPOSED`, no "EXISTS" |
| 2 copy content | ⛔ OWED — nothing copied yet; see §2/§3/§4/§6 below for exactly what moves |
| 3 freeze the twin | ⛔ OWED — `RUT_TheForge.xml` carries no freeze header today (read whole file, 178 lines, header is only the authoring note) |
| 4 retarget | ⛔ OWED — not started; §7 below lists the ~55 files naming `RUT_TheForge`, sorted |
| 5 prove it loads | ⛔ Desktop-only, blocked on steps 1–4 |
| 6 commit/push | owed with step 5 |
| paint-list append | ✅ DONE — row present, `infrastructure/state/facts/biome_paint_list.md:42`: `RUT_TheForge | the Forge | UtinniPatches / mandrake.rut.patches | yes | terrain+plants+fauna present (176 lines) | Dune Sea, Anvil | 44 | PAINT` |

**This is a from-scratch build, not a Greentide-style narrowing** — Forge has none of the twin-pair head start; every step is owed.

### 2. The def today

`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheForge.xml`, 178 lines (`wc -l`). `workerClass`
`AlphaBiomes.BiomeWorker_PyroclasticConflagration` — a **donor type**, so this build owes its own
`RM_BiomeWorker_TheForge` (RimMandrake tier may not assume Alpha Biomes). No `modExtension` on
the BiomeDef itself. MEASURED via `xml.etree` parse, not grep:

- `diseases`: 6 (`Disease_Flu`, `Disease_Plague`, `Disease_GutWorms`, `Disease_MuscleParasites`,
  `Disease_FibrousMechanites`, `Disease_SensoryMechanites`) — all vanilla, none SW.
- `terrainsByFertility`: 3 bands, all `AB_*` (Alpha Biomes donor terrain family).
- `baseWeatherCommonalities`: 8 entries — `Clear` 40, `AB_VolcanicAsh`/`AB_VolcanicAshRain`
  (`MayRequire="sarg.alphabiomes"`) 20/6, **`RSW_SW_RedFog` (`MayRequire="mandrake.rsw.swbestiary"`) 8**
  — this is a Star Wars-tagged weather entry sitting in what would become an RM_ def; `Rain`/
  `RainyThunderstorm`/`SnowGentle`/`SnowHard` all zeroed (ban 6, no ordinary rain).
- `wildAnimals`: 7 (shorthand form, `len(list(node))`, not `<li>`) — see §3.
- `wildPlants`: 10 (shorthand form) — see §4.
- `allowRivers` false, `allowFarmingCamps` true, `animalDensity` 1.2, `plantDensity` 0.4,
  `diseaseMtbDays` 65.

### 3. wildAnimals split (7 rows, MEASURED via parser)

| defName | commonality | MayRequire | verdict |
|---|---|---|---|
| `AA_Aerofleet` | 0.4 | `sarg.alphaanimals` | stays in `RM_` def (non-SW donor) |
| `LavaSnail` | 0.35 | `sarg.alphabiomes` | stays in `RM_` def (non-SW donor) |
| `LavaFlea` | 0.25 | `mlie.starwarsanimalcollection` | → Utinni patch (SW canon, Mustafar; repo already owns the port `RSW_LavaFlea` — cast that, not the bare donor name, per `SW_FAUNA_NEVER_IN_RM_TIER_1`'s Greentide precedent) |
| `AA_Metallovore` | 0.15 | `sarg.alphaanimals` | stays in `RM_` def (non-SW donor) |
| `Beldon` | 0.08 | `mlie.starwarsanimalcollection` | → Utinni patch (SW canon, Bespin gas-grazer). 🔴 **Finding**: the repo's owned port `RSW_Beldon` already exists and F2's `RUT_TibannaTap_BeldonWiring.xml` already patches the gas-gather comp onto `RSW_Beldon` — but this biome's own `wildAnimals` still spawns the bare donor `Beldon`, never `RSW_Beldon`. **The tibanna tap is wired onto a defName that does not spawn in this biome today.** Step 2 must cast `RSW_Beldon` in the new Utinni patch, not `Beldon` |
| `RSW_Maguana` | 0.5 | `mandrake.rsw.swbestiary` | → Utinni patch (already `RSW_`-tier, just needs the file) |
| `AA_CrescendoAnole` | 0.5 | `sarg.alphaanimals` | stays in `RM_` def (non-SW donor; `ECOSYSTEM_PYRAMID_LAW_1` ruled addition) |

**3 of 7 → Utinni** (LavaFlea, Beldon, RSW_Maguana); **4 of 7 stay inline**. `WildAnimals_TheForge.xml`
does **not exist yet** (checked `ls UtinniPatches/Patches/`). Rule source:
`SW_FAUNA_NEVER_IN_RM_TIER_1` (2026-09-22 owner ruling, supersedes this item's own generic
step-2 text which said "every `RUT_` entry stays out" — no `RUT_`-defName creature actually
appears in this biome's `wildAnimals`, so that clause is moot here but the ruling's real
bucket rule — by `MayRequire`, not by prefix — is what the table above applies).

### 4. wildPlants split (10 rows, MEASURED via parser)

| defName | commonality | verdict |
|---|---|---|
| `Plant_Fireweed` | 0.9 | stays (vanilla Odyssey; sheet's own SIGNATURE plant) |
| `Plant_MagmaCactus` | 0.7 | stays (vanilla Odyssey) |
| `RUT_FireLavender` | 0.6 | stays — ours, non-SW, franchise-free by content (ported `BMT_FLORA_ABSORPTION_1`). ⚠️ **Naming open question, not a ruling**: no §7 Q equivalent to Q10 (which renamed 7 `RUT_` **creatures** to `RM_`) exists yet for **plants** — flag for the owner, do not rename unilaterally |
| `RUT_Sagecrust` | 0.4 | stays — same flag as FireLavender |
| `IronScruff_PrimordialGrass` | 0.35 | stays (Primordial Geysers donor, non-SW) |
| `AB_TinkleGrass` | 0.3 | stays (Alpha Biomes donor, non-SW) |
| `IronScruff_PrimordialTallGrass` | 0.3 | stays (Primordial Geysers, non-SW) |
| `IronScruff_Bindweed` | 0.25 | stays (Primordial Geysers, non-SW) |
| `AB_FirevineTree` | 0.2 | stays (Alpha Biomes, non-SW) |
| `RUT_HeatsinkFungus` | 0.2 | stays — same naming flag as FireLavender/Sagecrust |

**0 of 10 → Utinni.** No row matches an owner-rejected class (no vanilla-Earth filler like
Greentide's oak/poplar — the roster's own `flora_purged` already evicted `GRimFireweed`,
`GRimMagmaCactus`, `AB_ToxicGamma` before this def was authored). Art spot-checked (not
exhaustive): `RUT_FireLavender`→`FireLavender_a.png` and `RUT_HeatsinkFungus`→`HeatsinkFungus_a.png`
both exist under `src/RimUtinni/UtinniPatches/Textures/Things/Plant/`; `RUT_Sagecrust` art
exists at `src/RimUtinni/RotSporeKit/Textures/.../Sagecrust/` (texPath match UNMEASURED — not
re-parsed). The other 7 rows' art is UNMEASURED (donor-owned, not this repo's tree).

### 5. Roster vs def diff

Roster (`rosters/the_forge.json`) fauna = 9 rows; def `wildAnimals` = 7 rows. **2 roster rows
unwired**: `AA_ColossalAerofleet` (0.5) and `Tibidee` (0.5) — both deliberately left out per
the def's own `ECOSYSTEM_PYRAMID_LAW_1` comment ("both LARGE, left out on purpose" — only the
small `AA_CrescendoAnole` was wired to fix the 50%-small ratio). Not a gap, a recorded choice.
Def rows NOT in roster: **0** (all 7 wired rows also appear in the roster's fauna list).
Roster flora (10 rows) = def `wildPlants` (10 rows), **1:1 exact match, 0 diff**.
`FORGE_ROSTER_UNRECONCILED_BMT_1` (closed 2026-09-21) already confirmed the roster's 27 `BMT_`
strings all sit under `.evictions[]` (dispositioned, not live) — re-confirmed here by reading
the JSON directly: zero `BMT_` names in `fauna`/`flora`.

### 6. Content to move into the mod

| path | verdict | reason |
|---|---|---|
| `UtinniPatches/Defs/BiomeDefs/RUT_TheForge.xml` | move (as `RM_TheForge`), freeze `RUT_` copy | the biome itself |
| `UtinniPatches/Defs/WeatherDefs/RUT_ForgeStill.xml`, `RUT_BoilingRain.xml` | move/mirror into `RM_TheForge` | franchise-free weather (F1), no SW/campaign label |
| `UtinniPatches/Defs/GameConditionDefs/RUT_ForgePulse.xml` | move/mirror | franchise-free weather-pulse condition (F1) |
| `UtinniPatches/Defs/ThingDefs_Buildings/RUT_VentSmelter.xml`, `RUT_VentForge.xml`, `RUT_VentKiln.xml` + their recipe-wiring patches | move (rename `RM_Vent*`) | generic geothermal industry (F6), no SW/campaign content — passes §3a |
| `RM_GenStep_TerrainChannels.cs`, `RM_ScattererValidator_Biome.cs`, `RM_GenStep_EdgeBandFilth.cs`, `RM_CompGatherableGas.cs`, `RM_CompScriptedDieOff.cs`, `RM_MapComponent_VaporColumns.cs`, `RM_CompVaporDrifter.cs`, `RM_MapComponent_FlashCycle.cs`, `RUT_Plant_FlashFlora.cs`, `WeatherPulseExtension.cs`, `RM_GameCondition_WeatherPulse.cs` | **no move — stays put** | already correctly filed in the §2d shared library `mandrake.rm.environmentalhazards`; generic, not Forge-owned |
| `UtinniPatches/Defs/ThingDefs_Items/RUT_TibannaGas.xml`, `Patches/RUT_TibannaTap_BeldonWiring.xml` | **stays Utinni** | tibanna is SW canon (Bespin) AND campaign plot (`TIBANNA_EMBARGO_PLOT_1`, the Empire's gas monopoly) — fails §3a both ways |
| `ThingDefs_Items/RUT_DeadCreep.xml`, `ThingDefs_Plants/RUT_DyingCreep.xml`, `MapGeneration/RUT_ContagionRingScatter*.xml`, `IncidentDefs/RUT_ContagionProbe.xml`, `RUT_IncidentWorker_ContagionProbe.cs` | **stays Utinni** | the Contagion is Ash'karr campaign lore (a named entity, "always testing the heat again") — fails §3a. 🔑 **Cross-item note**: the sibling agent on the Contagion biome build independently found this same C# (`RUT_IncidentWorker_ContagionProbe.cs`) hardcodes `RUT_TheForge`, i.e. **this content is Forge-owned, not Contagion-owned** — record so `CONTAGION_RM_MOD_BUILD_1` (if it claims this file) does not duplicate/contest it |
| `ThingDefs_Buildings/RUT_FoundryTowerEntrance.xml`, `RUT_FoundrySalvageCache.xml`, `MapGeneration/RUT_FoundryFloor*.xml`, `RUT_FoundryTowerScatter*.xml` | **stays Utinni** | F4 tower dungeon is explicit campaign plot per the sheet's own §8/§GM ("Rust Cathedral legacy... the smeltery of the god-project... asteroid mass... the glowing tenders") — fails §3a decisively. Confirms the brief's suspicion |
| `Patches/RUT_VaporDrifter_AerofleetWiring.xml` | stays a patch, unaffected by the split | patches a donor creature's comps (`AA_Aerofleet`), not gated on biome at all — mechanism is orthogonal to which mod owns the biome def |
| `UtinniPatches/Defs/DamageDefs/RUT_Scald.xml` | **UNCERTAIN, flag don't act** | shared cross-biome damage type (also used by Greentide); "scald" itself passes §3a but it was filed Utinni and is a cross-kit reuse — not this item's call to move unilaterally |
| 8 `DEPLOY_HOLD.txt` placeholder-art entries (`RUT_TibannaGas`/`DeadCreep`/`DyingCreep`/`VentSmelter`/`VentForge`/`VentKiln`/`FoundryTowerEntrance`/`FoundrySalvageCache`) | move with their def, hold stays | none has real art yet; not a step-1-4 blocker (art is separate work) |

### 7. References to `RUT_TheForge` across the repo

`grep -rl "RUT_TheForge"` (excluding `Transient/`) → **~40 non-Transient hits** (read, not counted
blind). Split:

- **(c) comment/prose — leave, do not retarget:**
  `BiomeDescriptions_Ashkarr.xml:214` — trailing comment only, the real xpath targets the donor
  `BiomeCypreJungle`-style def, not `RUT_TheForge`. `BiomeFlora_Ashkarr.xml:46` — inside that
  file's own "biomes this file deliberately does NOT patch" exclusion block (10 plants, authored
  in its own def). Same shape as Greentide's identical two false-positive hits.
- **(a) retarget outright** (design/bookkeeping, not world-facing, safe any time): `world/biome_world_switch_apply.py`
  (the `MAP` list — but this is the Phase B paint tool itself, touched only at the terminal
  paint, not now), `design/Jawa/fauna/biome_name_migration.py`, `design/Jawa/fauna/rosters_to_cast.py`,
  `design/Jawa/mods/biome_flora.py`, `design/Jawa/worldbuilding/biome_flora_rosters.md`,
  `design/Jawa/worldbuilding/biomes/_def_bindings_2026-09-09.md`, `infrastructure/state/facts/biome_rosters.md`.
- **(b) needs a second op for `RM_TheForge`** (must still work on the live/frozen world AND
  prove out on the standalone mod's own quicktest): `RUT_ForgePulse_BiomeWiring.xml` (F1 weather
  condition, gates on `RUT_TheForge` only today) — leave the `RUT_` op alone (frozen def keeps
  working), author the equivalent natively on `RM_TheForge` so step 5's quicktest can prove F1.
  `RUT_ContagionRingScatter.xml`/`RUT_FoundryTowerScatter.xml` gate on `RUT_TheForge` only —
  **UNCERTAIN whether these need a second op at all**, since both are campaign-plot content
  (§6 above) that a franchise-free `RM_TheForge` standalone mod would never ship; they can likely
  just keep targeting the still-live `RUT_TheForge` through Phase A without change. Flag for
  FOUNDRY judgment at step 4, not resolved here.
- Remaining ~15 hits are this item's own file, `FORGE_MECHANICS_1.md`'s own history, and other
  items/handoffs narrating past work — not live references needing action.

### 8. Mechanics/kit state — 🔴 ALL SIX SHIPPED, not unbuilt

`FORGE_MECHANICS_1` is `doing` but **F1–F6 all landed 2026-09-13/14**, re-verified 2026-09-18
(item's own note: "all six mechanics per forge_kit_spec.md's New-C# roster now shipped... no
real C#/wiring gap found"). Read the code, not just the note — confirmed present:

| mechanic | SHIPPED? | assembly / files |
|---|---|---|
| F1 boiling-rain weather | ✅ SHIPPED | `WeatherPulseExtension.cs`, `RM_GameCondition_WeatherPulse.cs`, `RM_MapComponent_FlashCycle.cs`, `RUT_Plant_FlashFlora.cs` in `RimMandrake.EnvironmentalHazards.dll`; `RUT_ForgePulse.xml`/`RUT_ForgeStill.xml`/`RUT_BoilingRain.xml`/`RUT_ForgePulse_BiomeWiring.xml` content |
| F2 tibanna harvest | ✅ SHIPPED (mechanism); 🔴 **wired onto the wrong live defName** (§3 above — targets `RSW_Beldon`, biome spawns bare `Beldon`) | `RM_CompGatherableGas.cs`; `RUT_TibannaGas.xml`, `RUT_TibannaTap_BeldonWiring.xml` |
| F3 vapor-column flight layer | ✅ SHIPPED (data comp + wander-root class); ⚠️ PLACEHOLDER wiring only — `RM_JobGiver_ColumnWander` compiles but is not spliced into any ThinkTreeDef, so today it grants scald immunity but does not yet bind wander | `RM_MapComponent_VaporColumns.cs`, `RM_CompVaporDrifter.cs`; `RUT_VaporDrifter_AerofleetWiring.xml` |
| F4 foundry tower dungeon shell | ✅ SHIPPED (single-floor only, per owner card 1 — no portal-chaining) | `RM_GenStep_TerrainChannels.cs`, `RM_ScattererValidator_Biome.cs`; `RUT_FoundryTowerEntrance.xml`, `RUT_FoundryFloor*.xml`, `RUT_FoundryTowerScatter*.xml` |
| F5 Contagion die-off ring | ✅ SHIPPED | `RM_GenStep_EdgeBandFilth.cs`, `RUT_IncidentWorker_ContagionProbe.cs`; `RUT_DeadCreep.xml`, `RUT_DyingCreep.xml`, `RUT_ContagionRingScatter*.xml`, `RUT_ContagionProbe.xml` |
| F6 geothermal vent industry | ✅ SHIPPED, XML-only | `RUT_VentSmelter/Forge/Kiln.xml` + recipe-wiring patches |

**Owed, explicitly not this build's job**: live quicktest verification of all six (never run —
BENCH has held the bridge), 8 art placeholders (`DEPLOY_HOLD.txt`), real forge-works room content
(vanilla `ScatterRuinsSimple` stands in), salvage loot table, tender PawnKindDef/faction,
fireweed diet content, the F3 ThinkTree wiring, Aerofleet→Fumerider rename. **None of this blocks
steps 1–4 of the mod-build item** — the mod-build item copies/moves what already exists; it does
not need to finish the mechanics kit.

### 9. Dependencies & items building INTO this mod

| item | state | blocks step 2? |
|---|---|---|
| `FORGE_MECHANICS_1` | `doing` | No — it already shipped the content this build copies/patches; only its OWN remaining work (quicktest, art) is unaffected by the mod split |
| `SW_FAUNA_NEVER_IN_RM_TIER_1` | `proposed` | Yes, in effect — this item's §3/§4 tables already apply its rule; the ruling exists (owner card 2026-09-22) even though the tracking item is still `proposed` |
| `FORGE_ROSTER_UNRECONCILED_BMT_1` | `done`/closed | No — already resolved, roster is clean |
| `BIOME_WORLD_SWITCH_WAVE_1` | `doing`, needs bridge | No — Phase B paint tool, not Phase A |
| `CUT_FALLOUT_GENERATED_DATA_1` | `doing` | No — names `RUT_TheForge`'s already-resolved flora trio, historical |
| `MIASMA_FEVERWOOD_GREENTIDE_BMT_1` | `proposed` | No — names Forge only as "already reconciled", not live work |
| `SCALD_MECHANICS_1` | `doing` | No — cites `RUT_ForgePulse.xml`/`RUT_TheForge` once as a "shape precedent" example, not a dependency |
| (implicit) `EnvironmentalHazards` shared library | live, `mandrake.rm.environmentalhazards` | **Yes — hard `loadAfter` dependency**, every F1–F6 comp/condition class lives there |

No item is filed to build directly INTO `THEFORGE_RM_MOD_BUILD_1` by name.

### 10. Blockers

**None for steps 1–4.** Step 1 (scaffold) can start immediately — no dependency is unmet.
Step 5 (prove it loads) is Desktop-only (bridge/game access), not a Mac blocker in the sense of
missing prerequisite work — it is simply a different machine's job.

### 11. Concrete step plan

1. **Scaffold** `src/RimMandrake/TheForge/About/About.xml`, packageId `mandrake.rm.theforge`,
   `loadAfter` = [`mandrake.rm.environmentalhazards`] (the only shared library this biome's
   mechanics actually reference — confirmed no `CreatureBehaviors`/`FlowWorks`/`WeatherSuite`
   symbol appears in any Forge def). `RM_TheForgeSettings : ModSettings` with: master toggle;
   per-mechanic toggles for `weatherPulseEnabled` (F1, already exists as an
   `RM_EnvironmentalHazardsSettings` field — this mod's screen should surface it), tibanna-tap
   rate (F2), vapor-column immunity (F3), tower scatter count (F4), die-off ring density (F5),
   vent work-speed bonus (F6). Empty `Defs/BiomeDefs/`. `deploy_custom_mods.py --mod TheForge`
   dry run, then `--apply`.
2. **Copy content**: `RM_TheForge` BiomeDef (own `RM_BiomeWorker_TheForge`, not the Alpha Biomes
   donor `workerClass`), the 3 terrain bands, 10 wildPlants (all inline), 4 non-SW wildAnimals
   inline (`AA_Aerofleet`, `LavaSnail`, `AA_Metallovore`, `AA_CrescendoAnole`), F1 weather/condition
   content natively, F6 vent buildings renamed `RM_Vent*`. New file
   `src/RimUtinni/UtinniPatches/Patches/WildAnimals_TheForge.xml`: `PatchOperationAdd` for
   `LavaFlea`→cast as **`RSW_LavaFlea`**, `Beldon`→cast as **`RSW_Beldon`** (fixing the F2 tibanna
   mismatch in the same move), `RSW_Maguana` unchanged — all three keep their commonality and
   `MayRequire`. `RSW_SW_RedFog` in `baseWeatherCommonalities` is RULED (owner, typed into a
   question card, 2026-09-24): *"Just make our own version and drop the SW label. RedFog has
   nothing to do with Star Wars.... it came from Alpha Biomes, and we're making our own version.
   Period."* ⇒ author our own RM_-tier red fog WeatherDef inside `mandrake.rm.theforge`, native
   in `baseWeatherCommonalities` — no Utinni patch, no `RSW_`/SW name anywhere on it.
3. **Freeze `RUT_TheForge.xml`** byte-for-byte, header: *"carrying the world until the terminal
   paint; content lives in `mandrake.rm.theforge`; do not edit here."*
4. **Retarget**: the 7 design/bookkeeping files in §7(a) — safe any time, no world dependency.
   Leave §7(b)'s biome-gated Utinni patches on `RUT_TheForge` (still the live world def); author
   F1's weather/condition content natively on `RM_TheForge` (covered by step 2) rather than a
   literal "second op" patch, since F1 belongs in the def itself once copied. Leave F4/F5/F2
   tibanna content entirely on the Utinni side (they stay Utinni, §6).
5. **Prove it loads**: minimal list + `TheForge` + `mandrake.rut.patches` +
   `mandrake.rm.environmentalhazards` + all five expansions. Quicktest on a scratch world tile
   set to `RM_TheForge`. Verify: the new `WildAnimals_TheForge.xml` rows land (post-load def
   dump, not just a clean `validate_patch.py`); F1 weather pulse actually fires on the new def
   (it inherited no `biomeMapConditions` node by default — needs the same
   `PatchOperationAdd`-onto-`RM_TheForge` treatment `RUT_ForgePulse_BiomeWiring.xml` used, or
   native authoring).
6. **Commit**: one commit, explicit paths, message naming the tibanna/Beldon defName mismatch
   fixed in the same move; append to `WORLD_REMAKE_FINAL_STEP_1`'s paint list (row already exists
   in `biome_paint_list.md`, confirm it still reads PAINT after this build).


## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.theforge`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_TheForge` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_TheForge`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.theforge`; do not edit here."* From that moment
   every content fix lands in `RM_TheForge` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_TheForge` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_TheForge` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.theforge` exists, deploys, and loads clean carrying `RM_TheForge` with its own content and its own
Mod Settings screen; the `RUT_` twin is frozen with its header and unchanged; the Star Wars
fauna ride a Utinni patch rather than the RimMandrake def; one commit, explicit paths, the
message naming what the twin got wrong; and the mod is appended to
`WORLD_REMAKE_FINAL_STEP_1`'s paint list.

## Watch out

- ⛔ **Do not paint, and do not cite a tile count as evidence about this biome.** The planet
  is painted ONCE, at the end. A def of ours carrying 0 tiles is the expected mid-migration
  state, not a defect.
- ⛔ **Do not delete the `RUT_` def.** Deleting a painted def before Phase B destroys the
  save.
- ⚠️ A `<li>` in the wrong place discards the WHOLE def, silently.
