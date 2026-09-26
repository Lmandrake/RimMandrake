# SCARLANDS_STANDALONE_MOD_1 — Scarlands biome-mod split: RM_Warscar, absorb ScarlandsLadder

## 🔑 STATE — MEASURED 2026-09-23 (Windows Desktop/WSL; RimSage answered; nothing live touched)

⚠️ **Shape note:** this item was filed BEFORE the mass-filed `*_RM_MOD_BUILD_1` batch, so it has
no `**subtitle**` line, no "Phase A row N … Governed by …" paragraph, and **no `## verify`
section** — it has `## the ask` / `## spec` / `## Watch out` / `## criteria` only. For the record:
this is **Phase A row 20** of `design/RimMandrake/biome_mod_architecture.md` (line 100). Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`. Not a §4 twin — it is
a fresh row-20 build, so all six steps apply. ⛔ Authoring the missing `## verify` is not this
pass's job; BENCH decides.

### 1. Step table

| step | state |
|---|---|
| 1 scaffold | ⛔ OWED — `src/RimMandrake/` has no `Scarlands`/`Warscar` folder (MEASURED: `ls src/RimMandrake \| grep -i 'scar\|war'` → empty). `mandrake.rm.warscar` appears in exactly 2 files, both prose (`biome_mod_architecture.md`, this item) |
| 2 copy content | ⛔ OWED — the only BiomeDef is `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Scarlands.xml` (181 lines, ElementTree-parsed) |
| 3 freeze the twin | ⛔ OWED — 0 occurrences of `carrying the world` in that file; its header is the 2026-09-09 authoring comment |
| 4 retarget | ⛔ OWED but SMALL — 9 files genuinely owed, 20 live files contain the string (see §7) |
| 5 prove it loads | ⛔ Windows Desktop only |
| 6 commit/push | owed with step 5 |
| paint-list append | ⚠️ PARTIAL — `infrastructure/state/facts/biome_paint_list.md:39` carries the `RUT_Scarlands` row; there is **no `RM_Warscar` row**, and that row's label column still reads *"the Scarlands"*, superseded by the Q5 ruling |

### 2. The def today

| field | value |
|---|---|
| path / size | `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Scarlands.xml`, **181 lines**, single `<BiomeDef MayRequire="Ludeon.RimWorld.Odyssey">` |
| `defName` / `label` | `RUT_Scarlands` / `Warscar` — the label collision fix is CONFIRMED in place (line 65) |
| `workerClass` | `RimWorld.BiomeWorker_Scarlands` — **not a donor mod**: MEASURED via RimSage, `./Source/RimWorld/BiomeWorker_Scarlands.cs`, `public class BiomeWorker_Scarlands : BiomeWorker`, i.e. first-party **Odyssey**. §5 step 2's donor-workerClass clause does not literally fire, but keeping it makes `mandrake.rm.warscar` hard-require Odyssey ⇒ recommend `RM_BiomeWorker_Warscar` anyway (decision, §10) |
| `modExtensions` | **NONE** (MEASURED: `<modExtensions>` absent; the def's 28 children are all vanilla `BiomeDef` fields) |
| `biomeMapConditions` | `RUT_ScarlandsMarkLock`, `RUT_ScariaOnsetArming` — both `MayRequire="mandrake.rm.environmentalhazards"` (lines 92–93). This is the ONLY shared-library reference the def makes |
| `extraGenSteps` (7) | `AncientRuins_Scarlands`, `CratersLarge/Medium/Small`, `ScarlandsJunkClusters`, `ScarlandsJunkPrefabs` (all Odyssey donor gensteps) + our `RUT_ScarlandsSprungDangers` |
| `terrainsByFertility` (2) | `AncientMegastructure` (Odyssey), `Soil` |
| weather (11 keys) | `Clear 50`, `Fog 1`, `DryThunderstorm 1`, `GrayPall 10` (Anomaly), `ToxRain 10` (Biotech), `Overcast 6` (Odyssey); `Rain`/`RainyThunderstorm`/`FoggyRain`/`SnowGentle`/`SnowHard` all **0** |
| diseases (10) | Flu, Plague, Malaria, GutWorms, FibrousMechanites, SensoryMechanites, MuscleParasites, AnimalFlu, AnimalPlague, OrganDecay |
| other | `wildAnimalScariaChance 0.5`, `plantDensity 0.15`, `animalDensity 1.0`, `texture World/Biomes/Scarlands`, `coastalWildAnimals` empty, no `fishTypes` (roster rules no fish) |

### 3. wildAnimals split — 9 rows, **6 go to Utinni**

⛔ `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Warscar.xml` **does not exist** (MEASURED: the
Patches dir holds only `WildAnimals_CrackedLands.xml`, `_Greentide.xml`, `_Pyrelands.xml`).

| defName | comm | prefix class | verdict |
|---|---|---|---|
| `Mynock` | 0.5 | donor `mlie.starwarsanimalcollection`, Star Wars canon | → Utinni patch. ⚠️ **our own `RSW_Mynock` clone already ships** (`src/RimStarWars/SWBestiary/Defs/ShipVermin/ThingDefs_Races/RSW_Mynock.xml`) per kit ruling 3 — the patch row should be `RSW_Mynock`, not the donor. That swap is `DONOR_DEFS_PORT_TO_OURS_1` scope, not this item's |
| `SW_Electrictick` | 0.3 | `SW_`, donor `who.vfee.isopodageneline` | → Utinni patch (§5 step 2 names the `SW_` prefix). ⚠️ UNCERTAIN whether that donor's `SW_` means Star Wars at all — flag, don't re-classify |
| `RSW_FoundryBeetle` | 0.18 | `RSW_`, ours (`SWBestiary`) | → Utinni patch |
| `AA_SpinedGow` | 0.15 | donor `sarg.alphaanimals` | **stays in `RM_Warscar`** |
| `RSW_Korrum` | 0.05 | `RSW_`, ours | → Utinni patch |
| `SW_Electricgryllotalpa` | 0.15 | `SW_` donor | → Utinni patch |
| `RG_Rimclaw` | 0.1 | donor `regrowth.botr.core` | **stays** |
| `AA_Helixien` | 0.08 | donor `sarg.alphaanimals` | **stays** |
| `SW_Juggernautbeetles` | 0.05 | `SW_` donor | → Utinni patch |

⇒ `RM_Warscar` keeps **3** rows; **6** rows become `WildAnimals_Warscar.xml`. Every row keeps its
own `MayRequire`.

### 4. wildPlants split — 1 row, and it is a genuine decision

| defName | comm | prefix class | verdict |
|---|---|---|---|
| `RUT_ScorchedStars` | 0.25 | `RUT_`, but **not Star Wars and not campaign** — a burnt-crust plant ported from the retiring Polluted Lands donor (`POLLUTED_LANDS_FLORA_PORT_1`, closed). Def at `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RUT_PollutedFlora.xml:159`, `texPath Things/Plant/ScorchedStars`, art PRESENT (`…/Textures/Things/Plant/ScorchedStars/ScorchedStars_a.png`, `_b.png`) | §3a says RimMandrake ⇒ it should move with the def, because §3c requires *"the RimMandrake def's `wildPlants` must point at defs the same mod ships"*. 🔴 **BUT** `RUT_Wasteland.xml:177` also uses it at 0.3, so moving it into `mandrake.rm.warscar` makes Wasteland depend on Warscar. **Decision owed (§10).** |

✅ **No owner-rejected vanilla filler here** — unlike Greentide. The roster's `flora_purged` records
*"(donor vanilla wildPlants, wholesale)"* already evicted per sheet §0 and bans 2/3 (no fertile
ground, no green), and the def carries **zero** vanilla plant rows (MEASURED: `wildPlants` has 1
child). ⛔ Do not invent a rejection list for this biome.

### 5. Roster vs def diff — `rosters/the_scarlands.json` (15 fauna, 1 flora)

**In roster, NOT in the def (7):**

| defName | comm | ours or donor | art |
|---|---|---|---|
| `AA_AcanthamoebaGiganteaSmall` | 0.1 | donor `sarg.alphaanimals` | UNMEASURED |
| `BMT_CrystalFairyMole` | 0.5 | donor BiomesTeam | UNMEASURED — rides `ROSTER_DEAD_BMT_NAMES_SWEEP_1` (proposed; "14 ported-but-unwired `BMT_` rows … wire-or-drop, never bulk-wire") |
| `BMT_MegaphoridLarva` | 0.5 | donor BiomesTeam | same |
| `RSW_ShaleGorger` | 0.5 | **OURS — def EXISTS**, `src/RimStarWars/SWBestiary/Defs/SeaBeasts/ThingDefs_Races/SeaBeasts_Opee.xml` | **PRESENT**: `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/SeaBeasts/ShaleGorger/ShaleGorger_south.png`. ⚠️ it is a **sea** silt-ambusher (`art/SeaBeasts/final/README.md:16`) rostered into a dry crater biome — a row for this biome's own review sitting, not a fix |
| `SW_Electricfish` | 0.5 | donor | 🔴 **the roster contradicts itself**: `SW_Electricfish` is in `fauna` at 0.5 **and** in `evictions` with disposition `homeless-reserve`. Report only |
| `SW_Grenadierworm` | 0.5 | donor | UNMEASURED |
| `RUT_ScarRoach` | 0.08 | **OURS — def EXISTS**, `src/RimUtinni/RustCathedralRoaches/Defs/ThingDefs_Races/RUT_ScarRoach.xml` | **PRESENT**: `…/Textures/Things/Pawn/Animal/RUT_ScarRoach/RUT_ScarRoach_south.png`. It declares `<wildBiomes><RUT_Scarlands>0.08` (line 95), which a BiomeDef never reads ⇒ owed as a row in `WildAnimals_Warscar.xml` |

**In the def, NOT in the roster (1):** `AA_SpinedGow` 0.15 — **not a defect.** The roster's
`new_defs` names *"plated grazer signature … `AA_SpinedGow` is the interim body"*; the def's own
comment says the same. Deliberate.

**Flora:** roster 1 = def 1, matched. `new_defs` still owes the bespoke **"Glowers"** def (black
radiotrophic crust, the biome's only native flora) — **UNFILED**, per
`Transient/biome_owed_audit_20260920/hazard.md:209-217`. `RUT_ScorchedStars` is the acknowledged
interim placeholder with an *"eye test owed: must read black/glass, never green (ban 3)"*.

### 6. Content to move into the mod

**MOVES (RimMandrake per §3a) — 9 files:**

| path | reason |
|---|---|
| `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Scarlands.xml` | the def itself → copy as `RM_Warscar`, freeze the original |
| `src/RimUtinni/UtinniPatches/Defs/HediffDefs/RUT_ScarlandsMark.xml` (107 l) | a mark hediff works on any planet |
| `src/RimUtinni/UtinniPatches/Defs/HediffDefs/RUT_ScariaIncubation.xml` | scaria onset, mechanism not campaign |
| `src/RimUtinni/UtinniPatches/Defs/GameConditionDefs/RUT_ScarlandsMarkLock.xml` (57 l) | the def's own `biomeMapConditions` entry |
| `src/RimUtinni/UtinniPatches/Defs/GameConditionDefs/RUT_ScariaOnsetArming.xml` (74 l) | the def's other `biomeMapConditions` entry |
| `src/RimUtinni/UtinniPatches/Defs/ThoughtDefs/RUT_ScarlandsMarkThoughts.xml` (45 l) | index-aligned to the hediff |
| `src/RimUtinni/UtinniPatches/Defs/PrefabDefs/RUT_ScarlandsSprungDangers.xml` (122 l) + `Defs/MapGeneration/RUT_ScarlandsSprungDangers_GenStep.xml` (68 l) | pre-sprung ruin dressing; wired at `RUT_Scarlands.xml:89` |
| `src/RimUtinni/ScarlandsLadder/` (2 files: `About/About.xml`, `Defs/LoreStageTableDefs/RUT_ScarlandsLadder.xml` 105 l) | §3c names `mandrake.rut.scarlandsladder` as a kit at the wrong tier — **but see §10 (i), the mod itself argues otherwise** |

🔴 **This contradicts this item's own `## spec`**, which says the satellite `RUT_Scarlands*` defs
*"do NOT need renaming for this item's criteria."* §5 step 2 moves *"its terrain, plant, weather,
condition and hediff defs"* with the def, and their player-facing strings still say **"the
Scarlands"** (`RUT_ScarlandsMark.xml:57-58`, `RUT_ScarlandsMarkLock.xml:43-44`,
`RUT_ScarlandsMarkThoughts.xml:28,33,38-39`) — retired text after the Q5 ruling. ⇒ BENCH should
reconcile the spec bullet; FOUNDRY should not silently pick one.

**STAYS in Utinni:**

- `Patches/WildAnimals_Warscar.xml` (to be CREATED) — the 6 fauna rows of §3.
- `Patches/BiomeNames_Ashkarr.xml:201-204` and `Patches/BiomeDescriptions_Ashkarr.xml:233-247` —
  these target the **vanilla Odyssey `Scarlands`** def, never `RUT_Scarlands`; campaign text, stay.
  (The `BiomeNames` op still writes the label *"the Scarlands"* — superseded by the Q5 ruling.)
- `src/RimUtinni/RustCathedralRoaches/` — `RUT_ScarRoach`'s mod, owned by
  `RUST_CATHEDRAL_MECHANICS_1`; the roach pair is split by biome by the roster's own note.
- `world/biome_world_switch_apply.py:24` — Phase B painting, Utinni per §3b.
- `Patches/BiomeFlora_Ashkarr.xml:43` — its *"deliberately does NOT patch"* block. ⛔ Leave.

**C# — MEASURED, and the answer is "almost none":**

- `ScarlandsLadder` ships **no assembly, no `Source/`, no `.csproj`, no `Textures/`** — 2 XML files
  total. ⇒ **no `<Compile Include>` trap for the absorb.**
- The kit's C# already lives at RimMandrake tier in `mandrake.rm.environmentalhazards`
  (`RM_HediffComp_SeverityFloor.cs`, `ArmLatentHazardExtension.cs`, `RM_LordJob_DefendPerimeter`)
  and `mandrake.rm.shipvermin`/`…creaturebehaviors`. ⛔ **None of it moves** (§2d).
- 🔴 **False-tier class found:** `src/RimMandrake/EnvironmentalHazards/Source/RUT_LordJob_SentinelDefend.cs:27`
  declares `public class RUT_LordJob_SentinelDefend : RM_LordJob_DefendPerimeter` inside
  `namespace RimMandrake.EnvironmentalHazards` — a `RUT_` class name in a RimMandrake shared
  library, against `NAMING_SCHEME_PLAN.md` and §2d's *"nothing in them names a biome."* Not this
  item's to rename; flagged.
- **New C# owed:** one file, `RM_WarscarMod.cs` (`RM_WarscarSettings : ModSettings`) + its csproj.

### 7. References to `RUT_Scarlands` — MEASURED 104 files repo-wide, 62 never-edited history

62 of the 104 are `Transient/`, `Player.log*`, `ledger/events.jsonl`, `handoffs/`, `closed/` items
and generated dashboards — ⛔ never edited. Of the 42 live files:

**(a) retarget outright (9) —** `design/Jawa/fauna/biome_name_migration.py:42` ·
`design/Jawa/mods/biome_flora.py:273` · `design/Jawa/worldbuilding/biomes/_def_bindings_2026-09-09.md:43,120`
· `design/Jawa/worldbuilding/biome_flora_rosters.md:303` · `infrastructure/state/facts/biome_rosters.md:68`
· `infrastructure/state/facts/biome_paint_list.md:39` · `design/Jawa/worldbuilding/biomes/rosters/the_scarlands.json`
(`defNames: ["RUT_Scarlands"]`) · `design/Jawa/worldbuilding/biomes/kits/scarlands_kit_spec.md:149-182`
· `src/RimMandrake/Utils/build_landmark_density_sheet.py:67`.
⚠️ `design/Jawa/fauna/cast_assignment.csv` and `design/Jawa/worldbuilding/review/creature_register_rows.json`
are derived data — UNMEASURED whether their generators still run; do not hand-edit.

**(b) needs a SECOND op for `RM_Warscar` — NONE.** Checked file by file: `BiomeNames_Ashkarr.xml`
and `BiomeDescriptions_Ashkarr.xml` patch the **vanilla** `Scarlands`, not ours (so no second op is
owed by the rename — only the retire-or-keep question this item's `## spec` already raises);
`world/biome_world_switch_apply.py:24` is the Phase B `MAP` list and changes at the paint, not now;
`RUT_ScarRoach.xml:95`'s `<wildBiomes>` is donor metadata a BiomeDef never reads (the Greentide
precedent) — its real wiring is the `WildAnimals_Warscar.xml` row in §5.

**(c) comment / prose — ⛔ LEAVE (7):** `RM_HediffComp_SeverityFloor.cs:16` ·
`LoreStageDefDatabase.cs:7` · `RUT_Wasteland.xml:172` · `RUT_PollutedFlora.xml:8,157` ·
`RustCathedralRoaches/About/About.xml:36` · `BiomeFlora_Ashkarr.xml:43` · the six satellite defs'
own header comments. ⛔ Do not "retarget" a comment.

### 8. Mechanics/kit state — the kit is MUCH further along than its own item says

`SCARLANDS_MECHANICS_2` — **doing**, FOUNDRY, needs offline (`rimflow show`).

**SHIPPED (⛔ does not move into this mod, and must NOT be waited on):**

| kit § | what | where |
|---|---|---|
| §1 mynock ship-infestation, whole | `RM_SeekTargetExtension`, `RM_CompVerminBreeder`, `RM_GnawTargetExtension`, `RM_Alert_ShipVermin`, `RSW_Mynock` | `mandrake.rm.shipvermin` / `…creaturebehaviors` / `SWBestiary` (`SHIP_VERMIN_MOD_1`, `WRECKAGE_VERMIN_SPAWN_1`, both closed) |
| §2 the mark | `RM_HediffComp_SeverityFloor.cs` **+ content**: `RUT_ScarlandsMark.xml`, `…MarkLock.xml`, `…MarkThoughts.xml` | `mandrake.rm.environmentalhazards` + UtinniPatches |
| §3 scaria onset | RC5 `pawnKindFilter`/`requiredHediff` in `ArmLatentHazardExtension.cs` **+ content**: `RUT_ScariaIncubation.xml`, `RUT_ScariaOnsetArming.xml` | same |
| §4 Sentinels | `RM_LordJob_DefendPerimeter` + `RM_LordToil_DefendPerimeter` + `RUT_LordJob_SentinelDefend.cs`, `RUT_SentinelDefend.xml` DutyDef, `RUT_SentinelGraveWard.xml` spawner | same |
| §5 pre-sprung dressing | zero C# needed (`PrefabThingData.hp` resolved YES) **+ content**: `RUT_ScarlandsSprungDangers.xml` + GenStep, wired at `RUT_Scarlands.xml:89` | UtinniPatches |

**GENUINELY UNBUILT (MEASURED):** the Sentinel **PawnKindDefs** — `grep -rn 'defName>RUT_Sentinel' src/`
returns only the DutyDef and the grave-ward building; no `RUT_Sentinel*` pawn kind exists. Mod
Settings for the kit are also unbuilt (this mod does not exist yet).

🔴 **`SCARLANDS_MECHANICS_2.md`'s *"What is genuinely still unbuilt"* paragraph is STALE** — it
lists §2's mark HediffDef, §3's `RUT_ScariaIncubation`, §4's duty wiring and §5's prefab content as
not built; all four are on disk, each stamped *"SCARLANDS_MECHANICS_2 build pass"* in its own
header. Only the Sentinel kinds remain. BENCH: that paragraph needs correcting.

### 9. Dependencies & items building INTO this mod

| item | `rimflow show` state | bearing |
|---|---|---|
| `SW_FAUNA_NEVER_IN_RM_TIER_1` | proposed, FOUNDRY, offline | ⚠️ **overlaps step 2 exactly** — "97 rows, 12 biomes" out of RM defs. Whoever runs first authors `WildAnimals_Warscar.xml`; the other must not duplicate it |
| `SCARLANDS_MECHANICS_2` | doing, FOUNDRY, offline | lands later; the Sentinel kinds are the only gap. Does NOT block steps 1–4 |
| `BIOME_KITS_PUSH_TO_TEST_1` | doing, FOUNDRY, offline | Scarlands is 1 of its 8 kits; lands later |
| `BIOME_MOD_SPLIT_EXECUTION_1` | proposed, BENCH, build | parent. 🔴 its one-line summary still says *"BLOCKED on 10 owner questions … above all … whether Scarlands must be renamed"* — false since 2026-09-21 (§7 reads *"Nothing is open"*) |
| `ROSTER_DEAD_BMT_NAMES_SWEEP_1` | proposed, FOUNDRY, offline | owns the 2 unwired `BMT_` roster rows (§5). Lands later; ⛔ never bulk-wire |
| `KORRUM_ART_REGEN_1` | proposed, FOUNDRY, offline | `RSW_Korrum` has no art of ours; it rides the Utinni patch, not `RM_Warscar`. Not a blocker |
| `RUST_CATHEDRAL_MECHANICS_1` | doing, FOUNDRY, needs bridge | owns `RUT_ScarRoach`'s mod; stays Utinni. Not a blocker |
| `MOD_OPTIONS_RETROFIT_1` | ready/BLOCKED (live verification), FOUNDRY | this mod ships settings from birth per §6a; it does not wait on the retrofit's live proof |
| `ECOSYSTEM_PYRAMID_LAW_1` | proposed, BENCH, needs deploy | why `RSW_Korrum` sits at 0.05 not the roster's 0.5 (`RUT_Scarlands.xml:168`). ⛔ Do not "fix" that to the roster figure |
| `BIOME_WORLD_SWITCH_WAVE_1` | doing, FOUNDRY, needs bridge | Phase B painting. Out of scope |

### 10. Blockers

**None for steps 1–4.** Step 5 is Desktop-only and is not a blocker of 1–4. Three **decisions** a
builder should not take alone:

1. 🔴 **Does `ScarlandsLadder` actually belong in `mandrake.rm.warscar`?** §3c says yes (kit at the
   wrong tier). The mod's own `About.xml:17` says the opposite — *"the mechanism is
   mandrake.rm.lorestages (RimMandrake tier …); this mod is the RimUtinni half, per the
   engine/content rule in design/NAMING_SCHEME_PLAN.md §2"* — and its stage-5 text names **the
   Ashfall Road**, an Ash'karr place (`RUT_ScarlandsLadder.xml:77`), which §3a routes to Utinni.
   Also: the mod **IS DEPLOYED** (`test -e "/mnt/c/…/Mods/ScarlandsLadder/About/About.xml"` → present),
   so absorbing it retires a live mod folder and a `ModsConfig.xml` entry — a Desktop step.
2. **`RUT_ScorchedStars` is shared** with `RUT_Wasteland` (§4) — moving it into this mod makes
   Wasteland depend on Warscar. Alternatives: a shared flora home (§3c / §7 Q8's open
   `mandrake.rut.ashkarrflora` question) or leave it Utinni and accept a cross-tier `wildPlants`
   reference, which §3c forbids.
3. **`RM_BiomeWorker_Warscar` or keep `RimWorld.BiomeWorker_Scarlands`?** See §2.

### 11. Concrete step plan for Warscar

1. **Scaffold** `src/RimMandrake/Scarlands/` (folder name per the item's target; ⚠️ `deploy_custom_mods.py`
   needs mod folder names unique across tiers — `Scarlands` is free, `ScarlandsLadder` is a
   different folder) with `About/About.xml`: `packageId mandrake.rm.warscar`, name
   *RimMandrake: Warscar*, `supportedVersions 1.6`.
   **`loadAfter`, derived from what the moved content actually references:** `Ludeon.RimWorld`,
   `Ludeon.RimWorld.Odyssey` (the def is `MayRequire`-Odyssey and its gensteps/terrain are Odyssey),
   `mandrake.rm.environmentalhazards` (cited: `RUT_Scarlands.xml:92-93` `biomeMapConditions`
   `MayRequire`, plus `RM_HediffComp_SeverityFloor`/`ArmLatentHazardExtension`/`RM_LordJob_DefendPerimeter`
   all live there), and `mandrake.rm.lorestages` **only if** decision 10(i) absorbs the ladder
   (cited: `ScarlandsLadder/About/About.xml:24`, a HARD dependency). ⛔ **Not** `creaturebehaviors`,
   `flowworks` or `weathersuite` — nothing moved references them (MEASURED). `mandrake.rut.patches`
   gets the `loadAfter` on *this* mod, per §3d — not the reverse.
   Then `deploy_custom_mods.py --mod Scarlands` dry run, read the plan, `--apply`.
2. **Copy content** as `Defs/BiomeDefs/RM_Warscar.xml`: `defName RM_Warscar`, `label Warscar`,
   description/settleWarning verbatim, the 3 non-SW fauna rows only (`AA_SpinedGow`, `RG_Rimclaw`,
   `AA_Helixien`), `wildPlants` per decision 10(ii), all 10 diseases, both terrains, all 11 weather
   keys, 7 gensteps, both `biomeMapConditions`, `wildAnimalScariaChance 0.5`, `texture World/Biomes/Scarlands`.
   Move the 8 satellite defs of §6 under `Defs/` (renaming `RUT_*` → `RM_*` and their player-facing
   "the Scarlands" strings → "Warscar", subject to the spec reconciliation in §6), plus
   `Textures/Things/Plant/ScorchedStars/{ScorchedStars_a,_b}.png` if 10(ii) moves the plant.
   Add `Source/RM_WarscarMod.cs` + `RM_Warscar.csproj`.
   **Create** `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Warscar.xml` — a `PatchOperationAdd`
   onto `/Defs/BiomeDef[defName="RM_Warscar"]/wildAnimals` with the 6 rows of §3 (each keeping its
   `MayRequire`) plus the owed `RUT_ScarRoach` 0.08 row from §5. `WildAnimals_Pyrelands.xml` is the shape.
3. **Freeze** `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Scarlands.xml` — byte-for-byte, one
   header line: *"carrying the world until the terminal paint; content lives in
   `mandrake.rm.warscar`; do not edit here."* ⛔ Do not delete it.
4. **Retarget** the 9 files in §7(a). ⛔ No second ops are owed. ⛔ Do not touch §7(c).
5. **Prove it loads** (Desktop) — minimal list + `mandrake.rm.warscar` + `mandrake.rut.patches` +
   `mandrake.rm.environmentalhazards` + **all five expansions**. Zero new Config errors (grep the
   log). `validate_patch.py src/RimUtinni/UtinniPatches/Patches/WildAnimals_Warscar.xml --live --defs`
   — an unmatched `PatchOperationAdd` is silent, so confirm the 7 rows from a post-load def dump.
   Quicktest on a **scratch** world tile set to `RM_Warscar`. ⛔ Never the canonical save.
6. **Commit** explicit paths, one commit; append `mandrake.rm.warscar` / `RM_Warscar` to
   `infrastructure/state/facts/biome_paint_list.md` and `WORLD_REMAKE_FINAL_STEP_1`'s paint list.

**Settings screen (§6a)** — master `warscarEnabled`; per-mechanic `markEnabled` (+ severity floor),
`scariaOnsetEnabled`, `sentinelsEnabled` (+ the ruled radii 72/80/24/80), `sprungDressingEnabled`
(+ density, labelled **new maps only**); cross-biome block `enabled`/`everywhere`/allowlist/coverage,
default off. ⛔ The mynock infestation is **not** a toggle here — it belongs to
`mandrake.rm.shipvermin`'s own screen.

### False statements found elsewhere — for BENCH

- `infrastructure/state/facts/biome_paint_list.md:39` — label column reads *"the Scarlands"*;
  the ruled name is **Warscar** (article dropped, `biome_mod_architecture.md` §7 Q5).
- `infrastructure/state/items/BIOME_MOD_SPLIT_EXECUTION_1.md` — its summary still says the item is
  *"BLOCKED on 10 owner questions … above all … whether Scarlands must be renamed"*. All ten landed;
  §7 of the architecture doc ends *"Nothing is open."*
- `infrastructure/state/items/SCARLANDS_MECHANICS_2.md` — the *"What is genuinely still unbuilt"*
  paragraph names four things that are all on disk (see §8). Only the Sentinel PawnKindDefs remain.
- `src/RimStarWars/SWBestiary/art/SeaBeasts/final/ShaleGorger/PLAN.md:48` — *"No `RSW_ShaleGorger`
  ThingDef exists yet"*. It does: `src/RimStarWars/SWBestiary/Defs/SeaBeasts/ThingDefs_Races/SeaBeasts_Opee.xml`.
- `design/Jawa/worldbuilding/biomes/rosters/the_scarlands.json` — `SW_Electricfish` appears in
  `fauna` at 0.5 **and** in `evictions` as `homeless-reserve`. One of the two is wrong.
- `src/RimMandrake/EnvironmentalHazards/Source/RUT_LordJob_SentinelDefend.cs:27` — a `RUT_`-named
  class inside `namespace RimMandrake.EnvironmentalHazards`, against §2d and `NAMING_SCHEME_PLAN.md`.

## the ask

`biome_mod_architecture.md` §7 Q5 / row 20's own twin-pair migration, unblocked now that
`SCARLANDS_RENAME_OURS_1` closed the naming pick: owner ruled `Warscar`, article dropped.
`RUT_Scarlands`'s `<label>` already carries the new name (immediate collision fix, done);
this item is the rest of row 20 — the actual defName move and mod consolidation, the same
weight of work Pyrelands (`PYRELANDS_DEFNAME_RENAME_1`, and its own earlier standalone-mod
landing) and Greentide (`GREENTIDE_STANDALONE_MOD_1`) already got.

## spec

- **New biome def:** `RM_Warscar`, label `Warscar` (no article — deliberate, per the
  owner's ruling; every other row in the architecture table keeps `the Xxx`), tier
  RimMandrake, packageId `mandrake.rm.warscar`. Same content as `RUT_Scarlands` carries
  today (crater fields/slag hills flavor, `RimWorld.BiomeWorker_Scarlands` reused per the
  architecture table's existing note, settleWarning, terrain).
- **Absorb `mandrake.rut.scarlandsladder`** (the `ScarlandsLadder` mod, currently its own
  package under `src/RimUtinni/ScarlandsLadder/` — `RUT_ScarlandsLadder.xml` lore stage
  table) into the new RimMandrake mod, per the architecture table's row-20 note.
- **Live-tile safety — MEASURED 2026-09-21:** `RUT_Scarlands` carries 90 live tiles on
  `CANONICAL_ASHKARR_START_2026-09-12.rws` (`worldmap.py` census, cross-checked against the
  def dump's shortHash table). Follow the exact `UMBRA_IS_A_REGION_NOT_A_BIOME_1` pattern —
  do NOT delete `RUT_Scarlands` outright. Either keep it as a compatibility duplicate
  (old name, old content) until the terminal repaint reassigns those 90 tiles to
  `RM_Warscar`, or repoint them live via the bridge if that is judged lower-risk this time —
  the Umbra item's own addendum explains why the duplicate was chosen there.
- **The satellite `RUT_Scarlands*` defs** (`RUT_ScarlandsMark` hediff, `RUT_ScarlandsMarkLock`
  / `RUT_ScariaOnsetArming` game conditions, `RUT_ScarlandsSprungDangers` genstep+prefab,
  `RUT_ScarlandsMarkThoughts`) do NOT need renaming for this item's criteria — they are not
  part of the measured collision and are not referenced by name anywhere outside their own
  patches. Rename them only if the row-20 migration's own naming consistency demands it;
  don't invent extra scope.
- **Found and unresolved, worth checking here:** `BiomeNames_Ashkarr.xml` /
  `BiomeDescriptions_Ashkarr.xml` separately patch the VANILLA Odyssey `Scarlands` defName
  (bare) with our own flavor text (`BIOME_TEXT_PORT_1`) — a second, 0-live-tile entry
  carrying near-identical lore to ours. Once `RM_Warscar` exists and (eventually) owns all
  90 tiles, decide whether that vanilla-biome text-port patch is still doing anything or is
  dead weight to retire.

## Watch out

- Don't cite a tile count as evidence about paint-readiness — the planet is painted once at
  the end (`BIOME_PAINT_ONCE_AT_THE_END_1`).
- `validate_patch.py --live --defs` after any defName move; the xpaths in
  `BiomeNames_Ashkarr.xml`/`BiomeDescriptions_Ashkarr.xml` target `Scarlands` (vanilla,
  unrelated to this rename) and `RUT_Scarlands`'s own satellite patches — check each still
  resolves.

## criteria

`RM_Warscar` exists as a real RimMandrake-tier biome, `mandrake.rut.scarlandsladder` is
absorbed into it, the 90 live tiles on the canonical save are not orphaned (re-measure with
`worldmap.py`, not trusted from this note), and row 20 in `biome_mod_architecture.md` reads
DONE instead of PROPOSED.
