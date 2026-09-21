# Biome mod split — fact-check for §7 open questions (2026-09-20)

Purpose: settle factual premises under BIOME_MOD_SPLIT_EXECUTION_1's 10 owner questions
(`design/RimMandrake/biome_mod_architecture.md` §7) so only genuine judgment calls reach
him. Instruments used: RimSage (decompiled 1.6 engine + def dump, live on this machine),
direct file reads, and the live Windows save at
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\CANONICAL_ASHKARR_START_2026-09-12.rws`
(reachable at `/mnt/c/...` from this session — this is the Desktop machine).

## F1 — Does vanilla 1.6 ship a biome named "Scarlands"? (under Q5)

**Yes, unambiguously — both the biome AND the worker are vanilla.** RimSage
`search_defs("Scarlands")` finds `[BiomeDef] Scarlands (label: "scarlands")` at
`Defs/Odyssey/BiomeDefs/Scarlands.xml`, `<workerClass>BiomeWorker_Scarlands</workerClass>`,
and the worker class itself lives at `Source/RimWorld/BiomeWorker_Scarlands.cs`
(`public class BiomeWorker_Scarlands : BiomeWorker`). Full def pulled via
`get_def_details` (raw): defName `Scarlands`, label `scarlands`, an Odyssey-DLC ruined-city
biome (toxic water, scaria, mechanoid ruins, `ScarlandsJunkPrefabs`/`ScarlandsJunkClusters`
gen steps). Since the project's own standing rule is that ALL test mod lists carry all
five expansions (owner, 2026-09-19), Odyssey is always loaded, so this is a live,
unavoidable label collision, not a theoretical one: `RM_Scarlands` labelled "scarlands"
would sit in the same biome-select list as vanilla's own "scarlands" on every test/play
list.

**Verdict: CONFIRMED. `RimWorld.BiomeWorker_Scarlands` is vanilla AND the biome
`Scarlands` (Odyssey) is vanilla — both halves of Q5's premise are true, so the label
collision Q5 asks about is real, not a false alarm.**
Evidence: RimSage `search_defs`, `search_source`, `get_def_details("Scarlands", "BiomeDef", "raw")`.

## F2 — Cost of renaming RM_FE_Pyrelands → RM_Pyrelands (under Q3)

**Source-code cost (repo, `src/` only, excludes docs/handoffs/items which are historical
prose and cost nothing to leave stale):**
14 files under `src/` contain the literal string `RM_FE_Pyrelands`, 52 occurrences total:
`FlowWorks/Source/ManyWaters/RiverSteamHook.cs`(3, comments only),
`Pyrelands/validation.py`(6), `Pyrelands/Defs/BiomeDefs/Pyrelands.xml`(3),
`Pyrelands/Defs/GenStepDefs/PyrelandsGenSteps.xml`(1),
`Pyrelands/Source/WildPlantAllowlist.cs`(1), `Pyrelands/Source/FireEcologyHook.cs`(4,
comments only), `Pyrelands/Source/RM_PyrelandsDensityEnforcer.cs`(1),
`RimUtinni/PyrelandsMechanics/Source/PyrelandsTuning.cs`(2),
`UtinniPatches/Patches/AnoobaDrawSize_Fix.xml`(1), `.../AshStorms_Pyrelands.xml`(3),
`.../BiomeDescriptions_Ashkarr.xml`(2), `.../FlowWorks_SubsurfaceLiquid_Ashkarr.xml`(7),
`.../ManyWaters_RiverSteam_Ashkarr.xml`(11), `.../WildAnimals_Pyrelands.xml`(7).

**The spec's claim of "one C# string in `PyrelandsMechanics`" is FALSE — corrected in
place.** The defName is a live string LITERAL (not just a comment) in at least THREE C#
files, two of them outside `PyrelandsMechanics`: `PyrelandsTuning.cs`
(`"ZBiome_Grasslands", "RM_FE_Pyrelands",` — an array element),
`WildPlantAllowlist.cs` (`private const string PyrelandsDefName = "RM_FE_Pyrelands";`),
and `RM_PyrelandsDensityEnforcer.cs`
(`DefDatabase<BiomeDef>.GetNamedSilentFail("RM_FE_Pyrelands")`). `FireEcologyHook.cs` and
`RiverSteamHook.cs` carry it only in comments (cosmetic, zero functional risk).

Beyond the biome defName itself, `src/` carries 32 distinct `RM_FE_`-prefixed tokens
(terrain, plant, weather and item defNames plus the `RM_FE_BiomeWorker_Pyrelands` class
name) — the spec's "22 defs" figure is in the right order of magnitude but not exact;
not every `RM_FE_` token is a full defName (e.g. `RM_FE_Ground_` is a shared prefix
fragment across four terrain defs).

**Save cost: ZERO, right now.** Grepped the LIVE canonical save
(`CANONICAL_ASHKARR_START_2026-09-12.rws`, 17,500,721 bytes, mtime 2026-09-20 07:28 —
this is the current live file, not a repo backup) for `<def>RM_FE_Pyrelands</def>` and
for the bare string `RM_FE_Pyrelands` anywhere: **0 matches, either form.** It does
contain `ZBiome_Grasslands` (2 matches) and exactly three unrelated `RM_FE_` item-level
tokens (`RM_FE_FirefoamSprayer`, `RM_FE_Fulgurite`, `RM_FE_ScorchFruitYield` — placed
items, not the biome). This is independent, live confirmation of
`PYRELANDS_WRONG_BIOME_DEF_1`'s finding: the Pyrelands tiles currently carry
`ZBiome_Grasslands`'s hash, not `RM_FE_Pyrelands`'s — so `RM_FE_Pyrelands` has no
tileBiomeDeflate hash anywhere in the live save to break, and no map's plaintext `<biome>`
field names it either. Renaming it today costs nothing on the save side; the hazard the
spec's §5 describes only bites once a def IS painted and then gets deleted (Phase B),
which has not happened here.

**Verdict: CONFIRMED — cheap. Source cost is real but small (14 files, ~52
occurrences, 3 live C# string literals needing updates, not 1); save cost is
currently zero because the live save does not reference `RM_FE_Pyrelands` at all.**
Evidence: `grep -rn "RM_FE_Pyrelands" src/`; `grep -ac` against
`/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Saves/CANONICAL_ASHKARR_START_2026-09-12.rws`.

## F3 — Are RM_FloodedCanyon and RUT_CrackedLands the same place? (under Q4)

**What each ACTUALLY says**, read in full:

- **Terrain/worldgen role differ sharply.** `RUT_CrackedLands` (`generatesNaturally=false`,
  `workerClass=VanillaBiomes.BiomeWorker_Badlands`, texture `World/Biomes/ZBiome_Badlands`)
  is a hand-painted, non-generating biome sitting on 970 tiles of the frozen world — it
  never scores in worldgen, it's just paint. `RM_FloodedCanyon`
  (`workerClass=RimMandrake.FloodedCanyon.RM_BiomeWorker_FloodedCanyon`, texture
  `World/Biomes/ExtremeDesert`, a `spawnChance=0.03` rarity-slider `modExtension`) is a
  real generic worldgen biome meant to appear rarely on ANY generated planet.
- **Weather tables differ.** `RUT_CrackedLands`: Clear 85, DryThunderstorm 3, Sandstorm
  (Odyssey) 8, everything wet zeroed (Rain/RainyThunderstorm/FoggyRain/Fog/Snow all 0) —
  explicitly "no rain in the canyons" per its own header comment. `RM_FloodedCanyon`:
  Clear 20, Rain 0.5, DryThunderstorm 2, RainyThunderstorm 0.3, Snow 1/1 — a different,
  less extreme table with some ordinary rain and snow present.
- **Fauna/flora differ completely.** `RUT_CrackedLands` carries 10 Star-Wars/donor
  entries (`RSW_MutagenicNorphea`, `Gornt`, `Eopie`, `RSW_SandLeaper`, `CanCell`,
  `Convor`, `AA_Murkling`, `RSW_Creature_Mantrap`, `Woolamander`, `AA_SandSquid`) plus
  campaign `RUT_Twisting*` plants and a full Odyssey `fishTypes` table (`RUT_Tubbik`,
  `RUT_Zhurr`, `RUT_Hurrok`, `RUT_Vhessa`, `RSW_DuneCrawler`, `BMT_*`). `RM_FloodedCanyon`
  ships a vanilla-Core-only roster by explicit design choice (Iguana, Dromedary,
  Fox_Fennec, Warg, Rat, Cougar / Plant_Grass, cacti, Agave, Bush, Dandelion) and no fish
  table at all.
- **The flood mechanism itself: `RUT_CrackedLands` has NONE.** Its own header comment
  says flatly: *"NOT this pass's scope: the flood as an engine event (warning, wall of
  water, drowning, soil deposition — SS Owed)"* — the sheet describes the flood in prose
  (`the_cracked_lands.md`: rare, violent, downward, hot, "crud-laden" — Contagion
  runoff — chimes ring through the stone before the wall arrives, water then SEEPS INTO
  CRACKS and hides afterward) but nothing in `RUT_CrackedLands.xml` or any Utinni patch
  implements it. `RM_FloodedCanyon` DOES implement a flood: `FLOOD_CANYON_BIOME_1`
  (closed, verified live 2026-09-12) built `RM_MapComponent_CanyonFlood` — a per-map
  clock, chime warning, bounded flood-fill wall (`WaterMovingShallow`), one light
  non-fatal hit, recede to `SoilRich`, soak-driven plant-growth-rate coupling — and its
  source does reference `FlowWorks` (confirmed: `grep -l FlowWorks` hits
  `RM_MapComponent_CanyonFlood.cs`, its `.csproj`, and `About.xml`) for excavated-ground
  handling, matching the mod's own description. This is genuinely the SAME core image
  (chime → wall of water → drowns → leaves soil) as the sheet, but built as a *periodic
  clock* (period/lead-time/duration sliders), not as an externally-triggered event tied
  to the Contagion's storms, and it does not model the sheet's "water then hides in the
  cracks" follow-on.
- Not literally the same code: `RUT_CrackedLands` has zero flood code of its own: what
  runs on it today, if anything, would have to be `RM_FloodedCanyon`'s mechanic
  cross-biome-enabled onto it via Mod Settings (per §6's cross-biome allowlist pattern)
  — nothing in the repo currently wires that.

**No verdict rendered — this is the owner's call, per the task brief. The comparison
above is what he needs to rule Q4 in one glance: same central image (chime/flood/soil),
different worldgen role, different weather, completely different roster, and the actual
flood ENGINE only exists in one of the two.**
Evidence: `src/RimMandrake/FloodedCanyon/{About/About.xml,Defs/BiomeDefs/RM_FloodedCanyon_Biome.xml,Source/RM_MapComponent_CanyonFlood.cs}`,
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_CrackedLands.xml`,
`design/Jawa/worldbuilding/biomes/the_cracked_lands.md`,
`infrastructure/state/items/closed/FLOOD_CANYON_BIOME_1.md`.

## F4 — Lantern Deeps host test: temperature or biome allowlist? (under Q6b)

**The premise is STALE — this was already ruled and rebuilt, 2026-09-18/19, and the
spec's framing of "allowlist vs. temperature test" is a false dichotomy today.**

`GenStep_ScatterCavePortal.cs` (43 lines) — the actual shipped gate — reads:
```
if (!LanternDeepsSettings.emergenceEnabled) return;
if (!LanternDeepsSettings.IsEntranceBiome(map.Biome)) return;
if (!Rand.Chance(...)) return;
```
(`src/RimUtinni/LanternDeeps/Source/GenStep_ScatterCavePortal.cs:26-38`). There is no
hardcoded biome list in this file at all any more — `IsEntranceBiome` checks a **Mod
Settings list** (`LanternDeepsSettings.entranceBiomes`, "any biome selectable" per its
own comment). Its class lives at
`src/RimUtinni/LanternDeeps/Source/LanternDeepsMod.cs:20-90`. The DEFAULT value of that
list is `UtinniDefaultEntranceBiomes = {"BiomeGRimond", "RUT_NightsideIce",
"RUT_PropaneLake"}` (line 51-56), and the code's own comment states exactly why:
*"the DEFAULT is exactly the three the Utinni campaign ruled ≤ -40°C
(the_lantern_deeps.md 'Injection rule'), which is what both GenSteps hardcoded before
this setting existed."* This traces to a closed item, `DEEP_ENTRANCE_BIOMES_SETTING_1`
(ledger: claimed/built/closed 2026-09-18→19, sha `21378169a`, verified live: *"Deep
generated from the canonical map through the settings-driven portal GenStep, no
entranceBiomes Scribe error"*) whose owner-quote is recorded inline: *"The mod itself
will be (3) but for the Utinni scenario it's definitely (1)"* — i.e., the owner already
distinguished "the mod's own general behavior" from "what Ash'karr ships as its
default," which is exactly Q6b's question.

So: the FROZEN sheet's temperature rule is not contradicted by the code — it is the
generative rule the shipped DEFAULT was derived FROM, and it is now a configurable
default rather than a hardcoded check. What is still genuinely open for the owner (not
settled by this fact-check) is only the narrower mechanical question: should the
RimMandrake-tier version of this mod compute "is this biome ≤ -40°C" directly from
`BiomeDef` temperature data (so it works correctly on a stranger's generated planet with
none of these three biomes present), or is a configurable defName-list default
sufficient for the RimMandrake tier too? That's a design choice, not a fact.

**Verdict: CONFIRMED — the "shipped code carries a fixed biome allowlist that
contradicts the FROZEN sheet's temperature rule" premise is FALSE as of
`DEEP_ENTRANCE_BIOMES_SETTING_1` (closed 2026-09-19). It is a Mod-Settings-driven list
whose default was derived from the temperature rule.** `RUT_LanternDeeps` confirmed live
at `src/RimUtinni/LanternDeeps/Defs/Biomes/RUT_LanternDeeps.xml`, 178 lines (exact match
to spec).
Evidence: `src/RimUtinni/LanternDeeps/Source/{GenStep_ScatterCavePortal.cs,LanternDeepsMod.cs}`,
`infrastructure/state/ledger/events.jsonl` (grep `DEEP_ENTRANCE_BIOMES_SETTING_1`).

## F5 — Which RUT_ creatures sit in wildAnimals/wildPlants and are they Star Wars? (under Q10)

Swept every `.xml` under `src/RimUtinni` and `src/RimMandrake` for `RUT_`-prefixed tokens
inside (a) inline `BiomeDef` `<wildAnimals>`/`<wildPlants>` blocks and (b)
`PatchOperationAdd`/`Replace` `<value>` blocks whose `<xpath>` targets a def's
`wildAnimals`/`wildPlants` node (the first sweep undercounted — Pyrelands' patches add
animals as bare `<value>` children with no wrapping `<wildAnimals>` tag, which a naive
tag-matched regex misses entirely).

**RUT_ creatures in `<wildAnimals>` (7 distinct, not "three" as the spec's Q10 asserts —
corrected in place there):**

| defName | biome(s) | Star Wars canon? |
|---|---|---|
| `RUT_FireHawk` | Pyrelands (`RM_FE_Pyrelands`, patched) | No — 137-entry canon library has no matching folder; comment identifies it as "igniter-flier", campaign-original |
| `RUT_FurnaceBeast` | Pyrelands | No — "igniter-megafauna", campaign-original |
| `RUT_Emberscythe` | Pyrelands | No — re-authored off donor `GR_Mantistanis` (Vanilla Genetics Expanded), `EMBERSCYTHE_MANTIS_REAUTHOR_1` |
| `RUT_FireWasp` | Pyrelands | No — re-authored off donor `AA_FireWasp` (Alpha Animals) |
| `RUT_Flamefang` | Pyrelands | No — re-authored off donor `GR_Boomsnake` (Vanilla Genetics Expanded) |
| `RUT_Barbslinger` | Pyrelands | No — re-authored off donor `AA_Barbslinger` (Alpha Animals) |
| `RUT_Sytheclaw` | Pyrelands, Greentide, the Contagion (inline in all three) | No — re-authored off donor `AA_Razorjack` (Alpha Animals) |

None of the 7 has a folder under `design/RimStarWars/canon_references/` (checked all 137
entry names). Every one is explicitly commented in-repo as "OUR OWN" / re-authored off a
donor mod, per owner rulings `EMBERSCYTHE_MANTIS_REAUTHOR_1` and `PYRELANDS_DONOR_PORT_4`
(2026-09-19, *"The flamefang should be added to the biome and any donors cut... port all
four"*) — i.e. they are campaign-originated creature defs currently living at the Utinni
tier, matching Q10's third bucket ("neither Star Wars nor generic — misfiled RimMandrake
creature"). This directly answers Q10's factual half for all 7, not just the 3 it named.

**RUT_ plants in `<wildPlants>` (much larger set, ~35 distinct tokens):** the bulk sit in
`UtinniPatches/Patches/BiomeFlora_Ashkarr.xml` (the 35-file `mandrake.rut.ashkarrflora`
pack Q8 already asks about) plus per-biome inline defs on `RUT_CrackedLands`,
`RUT_FeverWood`, `RUT_Greentide`, `RUT_PoisonForest`, `RUT_Scarlands`, `RUT_TheForge`,
`RUT_TheScald`, `RUT_WeepingStones`, and the whole 13-species `RUT_LanternDeeps` cave
flora roster. None of these read as Star Wars canon names (Brellik Bulb, Kuvra Spout,
Prenna Lace, Twitching Puffer, etc. — invented flora); this fact-check did not run each
through the 137-entry canon library since Q10 is scoped to creatures, but flags for
whoever answers Q8 that plants are a separate, much larger population from the 7
creatures above.

**Verdict: CONFIRMED. 7 distinct RUT_ creatures sit in wildAnimals (Pyrelands ×6,
Contagion/Greentide share `RUT_Sytheclaw`), all campaign-original re-authorings of
donor creatures, none Star Wars canon — Q10's premise ("three... if one of them is
neither Star Wars nor Ash'karr-specific") undercounts the set but the underlying test
(none are Star Wars) holds for all seven.**
Evidence: python sweep of `src/RimUtinni/**/*.xml` + `src/RimMandrake/**/*.xml` against
`wildAnimals`/`wildPlants` inline blocks and PatchOperation `<value>` blocks;
`design/RimStarWars/canon_references/` (137 folder names, no match);
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml`.

---

## Corrections made to `biome_mod_architecture.md` in this pass

Two provably-false statements were corrected in place per CLAUDE.md ("correctness
outranks seat ownership" / "inaccurate material is deleted, not superseded-in-place"):

1. **Q3**: "one C# string in `PyrelandsMechanics`" → corrected to name the actual three
   files carrying live string literals (see F2).
2. **Q10**: "Three `RUT_` creatures sit in `<wildAnimals>` today" → corrected to seven,
   naming all of them (see F5).
