# The Abyss (asked as Black Crags; was the Forsaken Crags): bedazzle review, movements 1 and 2

_BENCH design pass, 2026-09-30. Row 11 of `BAROQUE_BEDAZZLE_PROGRAM_1`, the last row. Sitting
item `BLACKCRAGS_BEDAZZLE_SITTING_1`. The owner authorized opening it by question card on
2026-09-30 at 22:45 PDT. GPT consult: `Transient/bedazzle_gpt_enrich_2026-09-30/blackcrags.md`._

## 1. What is there

Everything below was read from `origin/main`:
- every file under `src/RimMandrake/ForsakenCrags/` (BiomeDef, About, settings C#);
- the frozen twin `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_ForsakenCrags.xml`, diffed
  against the RM def;
- `ForsakenCrags_Rename.xml` (the label patch);
- `SWBestiary/.../ForsakenCrags_WildSpawns.xml` and `ThingDefs_ForsakenCrags.xml`;
- `RUT_Lightfall.xml`;
- `EmpirePursuit`'s `ScenParts_EmpirePursuit.xml` and its matcher in `RuthlessPursuingMechanoids.cs`;
- the frozen sheet `forsaken_crags.md`, `rosters/forsaken_crags.json`, the batch-3a names doc, and
  `DONOR_DEFS_PORT_TO_OURS_1`;
- the closed items `FORSAKEN_CRAGS_FAUNA_1`, `FORSAKEN_CRAGS_PREDATORS_BUILD_1`,
  `FORSAKENCRAGS_RM_MOD_BUILD_1` and `LIGHTFALL_CHASM_AUTHORING_1`;
- `infrastructure/artpipe/done/`.

Creatures were read from their descriptions, not their defNames.

### Two defs, one body, and nothing on either is ours

| def | tier | what it carries |
|---|---|---|
| **`RM_ForsakenCrags`** | `mandrake.rm.forsakencrags`, free | Our own worker `RM_BiomeWorker_ForsakenCrags`, plus a settings screen with **only the rarity master toggle** (its own comment: *"no kit mechanics"*). Everything else is donor: the texture `Biomes/AB_RockyCrags`, terrain `AB_FineForsakenSand`/`AB_ForsakenSand`, the weathers `AB_ForsakenNight` 70 / `AB_ForsakenThunderstorm` 4 / `AB_ForsakenRainyNight` 4 / `Clear` 0, **14 Alpha Animals rows**, and **8 Alpha Biomes/Genetics flora rows**. About.xml says it outright: *"NOT donor-free."* |
| **`RUT_ForsakenCrags`** | UtinniPatches, the frozen twin | **Byte-identical content.** The diff is the defName, the donor workerClass (`AlphaBiomes.BiomeWorker_RockyCrags`), and two comment blocks. This is the def the world's tiles carry (§2). |

The Warscar had a poor free body and a rich campaign curse. **The Black Crags is poorer still. The
campaign twin carries no mechanics either.** Neither tier has an owned creature, plant, weather,
item or mechanic. Its "content today: 1" on the program table is generous.

### Fauna, merged (inline + patch-added)

All 14 inline rows are donor (`MayRequire="sarg.alphaanimals"`). Labels come from
`ForsakenCrags_Rename.xml` (batch 3a, owner-ruled 2026-09-24). That file is a Utinni patch, so
**the free tier shows the donor's English names** (nightling, darkbeast…).

| row | label (campaign) | comm | what it is (description / names doc) |
|---|---|---:|---|
| `AA_DuskRat` | dusk rat (kept, *the name is the joke*) | 1.5 | kitchen-soiling rat-analog. **Art redo owed** (sheet §4); no job in `done/` |
| `AA_Murkling` | kessik | 1.0 | scavenger packs, corpse decayer. ⚠ also on `RM_FloodedCanyon` 0.2 (the Flooded Canyon sitting deferred the call: *"annotate, that sitting's call"*) |
| `AA_NightMule` | hulggarok | 0.5 | the domestic pack line |
| `AA_CrepuscularBeetle` | brekkugar | 0.35 | large beetle |
| `AA_DuskProwler` | shekkur | 0.2 | medium predator |
| `AA_NightAve` | zekkra | 0.2 | flightless war-bird, ridden |
| `AA_Nightling` | vrakk | 0.2 | quill-throwing apex |
| `AA_DarkVandal` | gruzz | 0.15 | digs when hungry |
| `AA_NightRam` | dhukk | 0.09 | horned herbivore |
| `AA_ShadowCharger` | korrag | 0.09 | large charger |
| `AA_Thunderox` | bhoruk | 0.09 | large grazer |
| `AA_SandProwler` | (port-named vosska) | 0.075 | terrain-hiding graphic |
| `AA_Frostling` | thrizzik | 0.05 | the vrakk's polar cousin (owner moved it back here, 2026-09-06) |
| `AA_Darkbeast` | ulkhorr | 0.005 | *"wears a trailing halo of Dark"* (owner ruling §4). The donor's own death action is `DeathActionWorker_SummonEclipse`, so **its death already darkens the sky**. The halo itself is unbuilt. |
| `RSW_Skarnix` | skarnix | 0.09 | patch (`ForsakenCrags_WildSpawns.xml`, xpath `RM_ForsakenCrags`). A cat-sized ambush stalker that *"will not cross firelight or a heated space"* |
| `RSW_Cindermare` | cindermare | 0.04 | patch, same file. A mouthless predator that *"kills by grip, draining the warmth"* |

**Rostered but wired nowhere.** These are imports in `rosters/forsaken_crags.json`
(*"owner review 2026-09 (round2 move mapping): crag"*). Neither BiomeDef carries them, and no
patch adds them:
- **`AA_Behemoth` → ghorrumak.** The names doc calls it *"the Forsaken 'dragon': fire breath,
  regeneration, 'the thunder is their voice', 16 squares"*. Its art was approved for the
  nightside on 2026-09-06 (`creature_art_register`). bodySize is 8.0 per the names doc and 32.00
  per a `MegafaunaYield.xml` comment, so the live value is **UNMEASURED**. **This is the
  biome's giant, and it already exists.**
- **`GR_Nighthrumbo` → zhurrakor.** A bs-3 quill predator.

Two findings about the cast:
- **Cindermare and skarnix are invented, not canon.** Wookieepedia search returns 0 for both;
  the `mynock` probe returns 3. They still sit in the RSW tier. Under Q11a, an invented creature
  goes inline in `RM_`, the same move the Warscar made for the pallbearer. That is a card.
- **Done, unwired art exists for 12 of these 16** (`crags_<label>_{east,north,south}` in
  `artpipe/done/`, filed under `DONOR_DEFS_PORT_TO_OURS_1`): vrakk, dhukk, hulggarok, zekkra,
  kessik, brekkugar, korrag, bhoruk, gruzz, shekkur, ulkhorr, thrizzik, ghorrumak and
  zhurrakor. Probe: `mynock` finds 6 files. Nothing under `src/` references these textures.
  **The art for porting the cast to our own defs is already paid for.**

### Flora (all inline, all donor)

The rows are `AB_GlowingGrass` 1.0, `AB_ToxicGamma` 0.6, `AB_GiantGamma` 0.5, `AB_WildRadagast`
0.5, `AG_Gamma` 0.5, `AB_GiantStikehr` 0.3, `AG_Septimum` 0.25 and `AB_GiantSeptimum` 0.2. None
carries a `MayRequire`. Redrawn art is done for the gammas, giant stikehr, radagast and both
septimums (`*_v1`), and it is unwired. The sheet's **"farmable light" claim rests entirely on
donor behaviour.** Whether `AB_GiantGamma` really lights crops is **UNMEASURED**: it needs the
def's glower radius checked against the crop light threshold. Nothing grows here that the sheet
asks for and the donor lacks: the **crag-fungus gourmet line** (§7, owner-ruled 2026-09-06) has
no def.

### Weather, sound, ship, gods

- **Weather.** All three are donor. **The Unveiling (sheet §4b ⭐, owner-authored) does not
  exist.** Etchfall and Witchfire are names on paper over donor weathers with donor labels. No
  gust-wind variability exists either (ban 2 is unenforced, and the donor's wind is whatever
  vanilla gives).
- **Sound.** None. The register in sheet §9 is unbuilt: silence as the baseline, wind arriving
  like an impact, the tick of etch-fall on stone.
- **Ship.** Nothing. There is no row for the biome in `BIOME_SHIP_CONTRIBUTIONS_1`.
- 🔴 **The sensor shadow is BUILT, and keyed to a def the world doesn't use.**
  `EMPIRE_PURSUIT_SURVEY_SHADOW_1` gives a ×4 raid and warning delay to maps on
  `surveyShadowBiomes`. That list holds only **`AB_RockyCrags`** (the donor). The matcher is an
  exact `List<BiomeDef>.Contains(map.Biome)`. The world's tiles carry `RUT_ForsakenCrags`, and
  `AB_RockyCrags` holds 0 tiles on the canonical save (§2). **So the sheet's ⭐ "sensor shadow"
  most likely never fires on the campaign world.** `RM_ForsakenCrags` isn't listed either.
  This is a defect in a shipped mechanic, not a missing feature: the evidence is a defName
  mismatch, not a tile count. Live confirmation is **UNMEASURED** because the game is down.
- **Gods.** None. Lightfall exists as a named landmark on tile 9023 (campaign; `RUT_Lightfall`,
  authored 2026-09-12), and *"what waits at the bottom is unwritten"*. The Forsakens are a
  cryptid by ban 7, and the Nightbrother (Zabrak) whisper is campaign lore. No precept, ritual or
  relic touches the biome.

### Unbuilt sheet promises (⭐ or §-named)

the Dark as a substance with clear pockets · the Unveiling · Etchfall as grain chemistry · the
darkbeast halo · farmable light (unproven) · tholin harvest · gust power and the breakage
economy · ultima fibers · the gourmet line · fugitive holds · seep-works · rumor-sites · wind
farms, working and wrecked · the frostling admission (done) · the dusk-rat art redo.

## 2. Rename check: Forsaken Crags to Black Crags

The owner typed the rename on 2026-09-27 (program row 11) and ruled that it executes at this
sitting, gated by a live-tile check. **Nothing was renamed this pass.** This is the census and the
gate result, in the shape of the Cauldron rename (`CAULDRON_FULL_RENAME_1`).

### The tile gate: which BiomeDefNames does the world reference?

**The game is DOWN** (`./game`: *"NOT RUNNING"*, recorded DOWN), so the **live world is
UNMEASURED**. The gate was run the way the Cauldron rename ran it:
- **Save:** an offline shortHash decode of `CANONICAL_ASHKARR_START_2026-09-12.rws`'s
  `tileBiome` array.
- **Tool:** `worldmap.py`'s `WorldGrid`.
- **Def dump:** `DefDump/captures/2026-10-01T01-12-26Z`.
- **Sanity probe:** `RM_FloodedCanyon` reads **44**. That matches the live-bridge figure from
  `CRACKEDLANDS_FULL_RENAME_1` exactly.

These counts answer one question only: *would a defName rename leave the save pointing at a
deleted def?* They are **not** evidence about what is built (CLAUDE.md, zero tiles is not a
defect).

| defName | tiles on the canonical save | rename verdict |
|---|---:|---|
| `RM_ForsakenCrags` | **0** | free to rename (0 is the expected mid-migration state) |
| `RUT_ForsakenCrags` | **1,135** | **blocked in the same way as Cauldron's `RUT_PoisonForest`.** Renaming it leaves 1,135 tiles pointing at a dead hash until the repaint. Cauldron's precedent: the owner chose *"rename now; its 546 tiles ride to the paint-once-at-the-end repaint"* (question card, 2026-09-30). That is the default here unless he rules otherwise. |
| `AB_RockyCrags` (donor) | 0 | not ours, never a rename target. The pursuit shadow should stop naming it (§1). |

⚠ **The same decode shows two unresolved hashes, and they are live consequences of earlier
renames.**
- **`?65189` = 546 tiles.** That is exactly the `RUT_PoisonForest` count, which was renamed
  2026-09-30.
- **`?58457` = 222 tiles.** That matches the Pyrelands' recorded 222. The identity is inferred
  from the count, not decoded.

Both are owner-accepted under the ride-to-repaint ruling. They are recorded here because the
Black Crags rename would add a third (1,135 tiles). That is the cost the card asks him to
accept.

**Plain-text Scribe references in the save** (items, thoughts, terrain): the save names **no
`ForsakenCrags` string**. Its `Forsaken` hits all belong to donor defs we will never rename:
Alpha Genes' Forsaken faction gear (`AG_Forsaken*`, `AG_ForsakenForge`) and
`VCEF_ForsakenAnglerfish`. Probe: `<def>` returns 27,986 hits, so the instrument can see.

### What references the old name (MEASURED `git grep`, `origin/main`, `Transient/` excluded)

| target | count | notes |
|---|---|---|
| `RM_ForsakenCrags` | **75 / 30 files** | the def, the SWBestiary spawn-patch xpath, the worker, docs and items |
| `RUT_ForsakenCrags` | **1,215 / 30 files** | most of it is the `world/ASHKARR_WORLDMAP_tiles.csv` record (a NOT-target); the src hits are the twin, the rename patch's siblings, and the scatter of Utinni patches |
| packageId `mandrake.rm.forsakencrags` | 19 / 11 | About, compose manifest, items, ModsConfig snapshots |
| namespace/assembly `RimMandrake.ForsakenCrags` | 8 / 6 | **rebuild required.** The DLL and its `.srchash` must push together (`DLL_SOURCE_STAMP_GUARD_1`) |
| `RM_BiomeWorker_ForsakenCrags` | 10 / 7 | the `workerClass` string must move **in the same commit** as the C# type, or the def dies silently |
| mod folder `src/RimMandrake/ForsakenCrags/` | 6 files | folder rename plus the deploy-tool unique-name check |
| `ForsakenCrags` (all forms) | 1,368 / 77 | includes `ForsakenCrags_Rename.xml`, `ForsakenCrags_WildSpawns.xml`, the C# type names, and `ModsConfig.FORSAKENCRAGS_*` |
| `forsaken_crags` (files/strings) | 252 / 75 | the frozen sheet, the roster json, the fauna-sheet decisions, the artpipe jobs. The two canonical files rename with a one-line successor pointer, and the freeze header carries over |
| "Forsaken Crags" (label text, any case) | 247 / 124 | BiomeDef `<label>the Forsaken Crags</label>`, `BiomeNames_Ashkarr.xml` (which still targets the donor `AB_RockyCrags`), the cindermare/skarnix descriptions, the settings label |
| `AB_RockyCrags` | 55,414 / 285 | **donor, NOT a target.** The bulk is `world/**` records. The live src uses are the texture path, the pursuit shadow list, `AncientDangerGenSteps_AmbientDoctrine.xml`, `BiomeNames/Descriptions_Ashkarr.xml` and five `ashkarr_*.py` tools |
| ⛔ NOT targets | | `world/**`, `observed/`, closed items, handoffs, dated reviews. History stays history. Donor strings: `AB_*` terrain, weather and texture, and `AlphaBiomes.BiomeWorker_RockyCrags` |

### The word "Forsaken" survives elsewhere, and that is the real question

The sheet's **§8 "the Forsakens"** is a cryptid race (owner, 2026-09-06). The word has two
other live owners:
- **`VQEQuestText_AreForsaken.xml`** makes *Forsaken* **the exonym our people use for the
  Rakata ancients** (owner, 2026-08-20), with "The Forsaken Lab" and so on.
- **Alpha Genes ships a "Forsaken" faction and gear.**

So after the rename, *"the Forsakens who visit the Black Crags"* and *"the Forsaken ancients"*
would be two different peoples sharing one word. The rename frees the **biome** from the
collision. **Whether the cryptid keeps the name is a separate owner call**, put on the card
(§6 Q1). It is not assumed here.

## 3. Scorecard: the nine marks

**Free** is `RM_ForsakenCrags` plus its patch-added cast. **Campaign** adds the twin, the label
patch, Lightfall and the pursuit shadow. The program's verdict is the free column (Q11a).

| # | Mark | Free | Campaign | Evidence |
|---|---|---|---|---|
| 1 | Unique mechanic | **MISS** | **PARTIAL** | The free tier has none (its settings say *"no kit mechanics"*). In the campaign, the survey shadow ×4 is the only one, and it is keyed to the donor def (§1), so on this world it is effectively dead. |
| 2 | Discoverable technology | **MISS** | MISS | Nothing teaches. Gust power, tholin and the seep-works are all unbuilt. |
| 3 | Unique resources | **MISS** | MISS | Every row is donor. Ultima fibers, tholin and the gourmet line have no def. The donor glow-flora produce is not unique to this planet's crags. |
| 4 | Surprising creatures | **PARTIAL** | PARTIAL | The cast is strange: a quill-thrower, a beast that wears darkness and whose death eclipses the sky, a warmth-draining grip predator, a stalker that fears firelight. **All of it is donor or mis-tiered.** No owned invention exists. |
| 5 | GIANT beast | **MISS** | MISS | The ghorrumak (`AA_Behemoth`, a 16-square dragon) is **rostered and art-approved but wired into neither def**. The biggest live resident is the hulggarok (bs 2.8). |
| 6 | Gravship touch | **MISS** | MISS | Nothing. The sheet's own idea, *"the place to run to"*, is the natural one (§5 #6). |
| 7 | Soundscape | **MISS** | MISS | No SoundDef. The register in §9 is unbuilt. |
| 8 | Interesting weather | **PARTIAL** | PARTIAL | A permanent-night sky (`Clear` 0) is genuinely unusual. But it is donor, and the owner's own ⭐, the Unveiling, does not exist. |
| 9 | Relationship to the gods | **MISS** | PARTIAL | The campaign has the cryptid and the Nightbrother whisper (lore only), and Lightfall as a named place with nothing written at its bottom. |

**Free: 0 HIT / 2 PARTIAL / 7 MISS. Campaign: 0 HIT / 4 PARTIAL / 5 MISS.** This is the lowest
of the eleven. **What sets the Crags apart: the best single idea on the planet, light as a thing
the air eats, has never been touched by code.** Every image in the sheet sits on donor content:
the Dark that folds up in warm air, the clear pockets only a thermometer can find, a lamp as a
crop, the darkbeast as a hole in the glow, the Unveiling. The sheet is the asset. The body is a
borrowed mod.

⇒ Movement 3 aims at **the Dark itself first**. That is the one mechanic no other biome can
have, and four marks hang off it (1, 2, 8, 6). After it come the giant that already exists, the
owned cast, and the sound. **The admission test for this biome**, from its own image: *every new
thing must either live by the Dark, or trade in light.* Nothing sun-fed (ban 6), no steady wind
(ban 2), no geothermal (ban 1), no on-screen Forsaken (ban 7).

## 4. Roster fill

### The gaps, read from the sheet only

The stillsand rule applies: *if the roster looks healthy, it is wrong*. The roster shows 16 live
rows, and none of them is ours.

| gap | source | fill? |
|---|---|---|
| **No colossus** (mark 5) | bar; sheet §4 donor roster | **WIRE, don't invent.** The ghorrumak (`AA_Behemoth`) is already rostered here, and its art is approved and redrawn (`crags_ghorrumak_*`). A new giant would duplicate one the owner already placed. |
| **The base of the web has no body.** §4: *"chemotrophy on the mixing boundary… frantic in the blast, dormant in the still… a gust is a meal"*. Every donor row is a grazer or a predator of grazers. Nothing eats the **gust**. | §3, §4 | **YES, #1** |
| **The "suspiciously placed" creature.** §4: *"adapted to this terrain… too well, as though set here"*. §8 rumor-sites: *"a creature den too well provisioned, a stone circle nobody admits to"*. The Forsaken evidence has no animal to make it. | §4, §8 | **YES, #2.** This is how ban 7 is honoured: the evidence is an animal's work, deniable. |
| **Nothing trades in light.** §5: *"Light is the currency."* No creature takes it. | §5, §7 | **YES, #3.** A light-thief, which flies, so it gets real flight. |
| **The gourmet line has no plant.** §7: *"crag-fungus delicacies… lavish-meal multipliers, trade goods"* (owner, 2026-09-06). | §7 | **YES, flora #1** |
| A cave fish | `fish` ruling | **NO.** It was ruled out (36 water tiles under acid etchfall, and ban 6). |
| A second giant / more predators | — | **NO.** The vrakk, shekkur, vosska, zhurrakor, cindermare and skarnix already crowd the predator band. |
| The dusk-rat body | §4 | **NO new def.** Its art redo is owed (no job in `done/`). That goes on the art queue, not into a fill. |

### The sweep

Accent, from the batch-3a names doc rule 5: *"Crags: hard voiced stops, k/g/r clusters… said in
a gust."* No candidate shares a four-letter opening with the 14 drafted crag names (vrakk,
dhukk, hulggarok, zekkra, kessik, brekkugar, korrag, bhoruk, gruzz, shekkur, ulkhorr, thrizzik,
ghorrumak, zhurrakor) or with `korrum`.

**Instruments, run this pass:**
1. `git grep -il <name> origin/main -- src design infrastructure skills`. Probes: `mynock`
   **242** files, `korrum` **96**.
2. The Wookieepedia search API (`list=search&srsearch=`). Probe: `mynock` → *Mynock,
   Mynock/Legends, Ord Mynock*.

| candidate | repo | wiki | verdict |
|---|---:|---:|---|
| **gharrek** | 0 | 0 | ✓ #1 |
| krovvak | 0 | 0 | ✓ alt #1 |
| **durrgak** | 0 | 0 | ✓ #2 |
| dhagga | 0 | 0 | ✓ alt #2 (but *dh-* sits near dhukk; prefer durrgak) |
| **krizzak** | 0 | 0 | ✓ #3 |
| drekkis | 0 | 0 | ✓ alt #3 |
| drokkat, khaggar, skorrag, goddrak, rukkadh, grokkath, kerrog, tukkrag, gekkor | 0 | 0 | ✓ spares |
| **etchcap** (`RM_Etchcap`), `RM_EtchHollow` | 0 | 0 | ✓ flora #1 |

### Proposed fills: 3 creatures + 1 plant, all `RM_` tier, one home each

| # | name (alt) | band | bs | the creature |
|---|---|---|---:|---|
| 1 | **gharrek** (*krovvak*) · `RM_Gharrek` | the gust-feeder, the base of the web | ~0.6 | A flat, many-gilled crawler that clings in the lee of the crags. It lies **dormant in the still**: plates shut, cold, nearly invisible on obsidian. When a gust hits, every gharrek on the map **opens at once** and feeds on the stirred reactant mix: a sudden carpet of fluttering gill-fans and a faint chemical glow (flameless combustion, §4). Then they shut again. Harmless. It is the prey that makes the vrakk and the shekkur hunt *in the gusts*. **Ranching:** penned gharreks fatten only in gusts, and they give a little **gill-ash** that is the crags' chemfuel feedstock (it pairs with tholin, §5 #4). A visible map-wide pulse when the wind arrives is the biome's rhythm, turned into a creature. |
| 2 | **durrgak** (*dhagga*) · `RM_Durrgak` | the placer, the rumor-maker | ~1.2 | A slow, long-fingered digger that **arranges things**. It drags obsidian shards into **rings and rows**, caches glow-berries in neat piles, and lines its den with what it finds, including dropped steel and components. Rings and caches spawn on the map as a **sign** (a few `RM_DurrgakCairn` things and a stocked den), and the cairns go up whether or not a durrgak is in sight. Pawns who find one get a small "someone was here" thought. The description never says *who*. It describes only what it does, and that the Jawa *"say it learned it from someone"*. **Ban 7 holds:** there is no Forsaken. This is the sheet's own *"too neatly arranged… deniable"*, made into an animal. It is shy. Tamed, it **tidies**: it hauls small items into stockpiles at a crawl. That is the joke and the use. |
| 3 | **krizzak** (*drekkis*) · `RM_Krizzak` | the light-thief (a flier) | ~0.3 | A soft, dark moth-thing with a mouth like a lamp-glass. It **eats light**. Swarms settle on glow plants and dim them (a growth/glow debuff while perched), and they are drawn to **powered lamps**, which they cluster on and smother, cutting the lit radius. They take no power, only the glow. A colony's perimeter lights going dark one by one is the warning that a swarm has arrived. They scatter from heat (fires, heaters), the same rule as the skarnix. The *"currency"* has a thief. **It flies** (`MaxFlightTime`, vanilla flip-book frames when art lands; flight rule). ⚠ Its lamp-smothering needs a small C# comp (a glower radius debuff on the perched thing). |
| F1 | **etchcap** · `RM_Etchcap` | the gourmet fungus | — | A dense black-and-violet cap that grows **only in etch-hollows**, the low cells where the Dark's collapse-grain settles (§3). It is not sun-fed (ban 6 holds): it lives on the grain chemistry. Slow, low yield, and a **delicacy**: a lavish-meal ingredient with a mood multiplier, and a trade good off-world. It is the sheet's gourmet line, finally given a body, and it gives the etchfall a reason to be welcome. Placement: a wild plant with a terrain or low-elevation preference, or sown only on a new `RM_EtchHollow` soil (engine call at turn 3). |

All four are invented (Q11a → `RM_`) and single-homed. None reuses a neighbour's signature. The
gharrek's gust-pulse is not the Leaning Scrub's Stall-and-Gale: that is a **calendar**, and this
is a **feeding reflex**. The durrgak is the only creature on the planet whose sign is
*arrangement*. The krizzak attacks **light**, not power or hull (the mynock's lane).

**Wire-only, owed whatever the volley rules:** add the ghorrumak and the zhurrakor to the def
(rostered, art redrawn). Cindermare and skarnix move inline to `RM_` (card). The 12 done
`crags_*` facings and 7 `*_v1` flora textures ride `DONOR_DEFS_PORT_TO_OURS_1`.

## 5. Volley turn 1: the slate

**Kept clear of** the ruled and offered packages of the other ten rows. These were read from
every `*_bedazzle_review`, `*_cast` and `warscar_turn3_development` on origin/main, plus the Warscar
prompt's own list:

- **Warscar:** the Settling (calm → fallout film that keeps tracks), the aerosol screen, the
  totchak, the Geiger choir, the hospice, the old tongue, the rainbow pools.
- **Stillsand:** the Listening, the dunes take the ship, the Stillstorm, the Return.
- **Long Shade:** shade currency, the golden hour.
- **Leaning Scrub:** the Stall-and-Gale wind calendar, the vaporator.
- **Blue Desert:** silence-then-boom.
- **Cracked Lands:** read-the-land survey.
- **Cauldron:** fluid conversion, the four-stroke weather.
- **Forge:** giant-on-the-clock, the four voices.
- **Wasteland:** named storms.
- **Contagion:** draftprints, the Dive.
- **The grandfathered dark neighbours:** the **Twilight Deep's light economy** (skylight wells,
  the sun-sphere, mobile lamp constellations), the **Lantern Deeps' living light** (shard-minds
  in the dark), and the Nightside Ice's distillation column.

🔴 **Two echo risks are named, not hidden:**
- **Etchfall** is a fall that leaves residue, and the Warscar's Settling is too.
- **Gust power** is wind-shaped play, and the Leaning Scrub's calendar is too.

Each candidate below says how it stays its own.

**The Crags' family is LIGHT AND ITS ABSENCE.** The Stillsand is what is under you, the Long
Shade is where you stand, and the Warscar is what already happened. **The Black Crags is what
you can see, and what you can't.** Every candidate either changes what is visible, or trades
in light.

| rank | candidate | marks | size | tier |
|---:|---|---|---|---|
| 1 | The Dark is a substance: heat folds it | 1, 2, 8 | L | RM |
| 2 | The Unveiling | 8, 9 (+4) | M | RM |
| 3 | Wake the ghorrumak: the thunder is its voice | 5, 7 | S | RM (wire) |
| 4 | Etchfall: the grain that eats stone, and the tholin you sweep | 3, 8 | M | RM |
| 5 | The sensor shadow, made true, and the ship that hides | 6, 1 | S–M | RM + RUT |
| 6 | The ulkhorr's halo: a moving hole in the glow | 4 | M | RM |
| 7 | Grown light: the lamp is a crop | 3, 2 | S–M | RM |
| 8 | Sound comes in gusts | 7 | S–M | RM |
| 9 | The rumor-sites: the durrgak's rings | 9, 4 | S | RM body / RUT lore |
| 10 | Gust turbines: a watt is a wound | 2, 3 | M | RM |
| 11 | Lightfall: the bottom, written | 9 | M–L | RUT |
| 12 | Movement-4 pre-ticket: the free-tier body wave | — | M | RM |

1. **The Dark is a substance: heat folds it** *(marks 1, 2 and 8).* This is the sheet's central
   mechanism (§3, owner-ratified): *"the Dark does not leave — it folds up… nothing but a
   thermometer can tell the clear pocket from the wall of Dark beside it."*
   - **The field.** A `MapComponent` keeps a coarse **Dark-density field** over the map. It is
     thick by default. **Clear pockets** open and close where the cell is warm: a sharp-edged
     circle of clear air drifts, holds, then closes.
   - **Inside the Dark:** sight and ranged accuracy drop hard, glow radii shrink (light is
     eaten in transit), and the overlay is a dark haze with knife-edge holes.
   - **The discovery** is the sheet's own. 🔑 **Heat folds the Dark.** A campfire, a heater,
     a warm room carve a clear pocket around them. Players who learn it (a research unlock
     after the first "clear pocket around your heater" event) can build a **fold-lamp**: a
     heater-lamp that keeps a lane of clear air open. A warm base is a seeing base, and a cold
     one is blind. In a −10 °C biome that ties vision to fuel.
   - *Engine:* a MapComponent grid + a SectionLayer overlay + Harmony on `ShotReport` and on
     `GlowGrid` attenuation (read the sky-glow path first). **Large C#**, and the spine.
   - *Distinct:* the Warscar's Settling is a residue after calm. The Twilight Deep's light is
     something you carry and place. This is **air you can see through only where it is warm**.
   - *Trade-off:* the biggest build on the slate. A global accuracy and vision cut is harsh, so
     it needs a Mod Settings strength slider and a cap.
2. **The Unveiling** *(marks 8 and 9, plus 4).* The owner authored this one (§4b ⭐) and it does
   not exist. Rarely (a GameCondition of a few hours, single digits per year), **the Dark folds
   away wholesale**:
   - full light floods the map, the whole country shows itself, and a soft chord plays;
   - every pawn who is awake and outdoors gets a strong **"I saw the crags"** memory;
   - everything the Dark was hiding is revealed **for its duration**: durrgak rings, an
     ulkhorr, a fugitive hold's door, the shape of the land;
   - then it **folds back**, and the field returns.

   *God-touch:* the Unveiling is the biome's holy moment. An Ideology precept can ask for it
   ("the Dark is a veil"), and it can be the trigger for a ritual or a vigil. *Engine:*
   GameConditionDef + a field override on #1 + thoughts. **Medium.** *Distinct:* every other
   biome's rare weather is a hazard. This one is a **gift**. *Trade-off:* it leans on #1 to
   matter. Without the field it is just a bright day.
3. **Wake the ghorrumak: the thunder is its voice** *(marks 5 and 7).* The giant already exists:
   rostered, art redrawn (`crags_ghorrumak_*`), described as *"fire breath, regeneration, the
   thunder is their voice"*. Wire it into `RM_ForsakenCrags` at trace commonality. Then give it
   its sheet line: **during a Witchfire storm, the thunder you hear is sometimes the ghorrumak
   calling** (a distinct roll, a few seconds before a strike-flash that has no lightning). One
   may come down out of the crags and cross the map in the storm. *Engine:* a roster row, a
   SoundDef, and an incident gated on the storm weather. **Small.** *Distinct:* the totchak
   wakes to demolition, the Forge's giant runs on a clock, and the Stillsand's oommok walks as
   shade. The ghorrumak **is the storm's voice**. *Trade-off:* it is donor-bodied until the port
   lands (`DONOR_DEFS_PORT_TO_OURS_1`). Fire breath must not start fires on obsidian, which it
   naturally won't.
4. **Etchfall: the grain that eats stone, and the tholin you sweep** *(marks 3 and 8).* The sheet
   §3 says *the collapse is the erosion*. The donor's "rainy night" becomes a real weather:
   - the collapsed grain falls, and **unroofed stone and steel slowly lose HP** (the land being
     eaten);
   - it leaves a sweepable `RM_Tholin` drift (a filth that cleans into an item);
   - tholin refines to **chemfuel** (§7: *"chemfuel-adjacent industry from air"*), so the
     etchfall pays for its damage.

   *Distinct from the Warscar's Settling,* explicitly: the Settling falls **when the wind stops**
   and keeps **tracks**. Etchfall falls **where the Dark dies** (it follows #1's clear pockets,
   so heat brings it down on you), and it **eats**. Its residue is a fuel, not a record.
   *Engine:* a WeatherDef + a damage tick on exposed buildings + a filth and recipe. **Medium.**
   *Trade-off:* wall decay annoys. It should be slow, and roofs stop it.
5. **The sensor shadow, made true, and the ship that hides** *(marks 6 and 1).* The ×4 pursuit
   delay is **already built** and keyed to the wrong def (§1). First fix the list
   (`RUT_ForsakenCrags` + the RM def, which is an XML line). Then make it the biome's **ship
   touch**: **a gravship landed in the Crags is hidden**. Orbital trade and pursuit scans fail,
   and while the ship sits under the Dark its grav-signature fades (a hediff-like "masked" state
   on the ship). The Crags becomes the place every player brings the ship **to lie low**. It is
   the sheet's ⭐ *"the place to run to when the Empire is close"*, now with the ship in it.
   *Free tier:* a franchise-free version, "raids take longer to find you here" (the same ScenPart
   shape as an RM storyteller tweak). *Engine:* the fix is XML. The ship-mask is a small C#
   `MapComponent` checking for a `GravEngine` on the map. **Small–Medium.** *Trade-off:* safety is
   strong. Hiding must cost something: cold, the Dark, and breakage (#10).
6. **The ulkhorr's halo: a moving hole in the glow** *(mark 4).* The owner ruled this
   (§4: *"it wears it… a moving knot of blindness"*), and it is unbuilt. The ulkhorr **carries
   a radius of Dark** (it writes into #1's field, or into a local glow debuff if #1 is not
   built), even where the Dark cannot form: inside your warm base, under your lamps. Its death
   already **summons an eclipse** (the donor's `DeathActionWorker_SummonEclipse`), which keeps the
   lore: kill it and the sky goes out. *Engine:* a ThingComp writing a moving glow-negative
   radius. **Medium C#.** *Trade-off:* at 0.005 it is rare. It is surprising when it comes, but
   few players will ever see one, so it could be raised slightly or tied to the Unveiling (#2).
7. **Grown light: the lamp is a crop** *(marks 3 and 2).* §7 ⭐ *"the only biome where a lamp
   is a crop"*. Prove the donor's glow first (`AB_GiantGamma` radius against the crop light
   threshold: **UNMEASURED**). Then make it real:
   - **transplant** a gamma or giant gamma (a minified plant, the same shape as a tree
     transplant) to light a grow-room with no power;
   - **radagast berries feed gamma growth** (§4: *"glow-berries double as the gammas' growth
     medium"*) as a fertilizer item.

   *Distinct from the Twilight Deep:* there light is caged, chained and placed (lamps and
   spheres). Here it is **grown in the ground and eaten by the air**. *Trade-off:* it is
   the closest echo on the slate, so it should stay small.
8. **Sound comes in gusts** *(mark 7).* The Crags heard with eyes closed (§9):
   - **silence** is the bed, deliberately near-empty;
   - **the gust arrives like an impact**: a hard whump, then the wind howling through rock
     teeth, and the **gharrek fans opening** in a map-wide rustle (fill #1);
   - **the tick of etch-fall on stone** during #4;
   - **the ghorrumak's thunder** inside Witchfire storms (#3);
   - the **krizzak's soft clatter** on a lamp-glass as the lights go out (fill #3).

   *Engine:* the shipped `RM_MapComponent_ProximitySoundscape` + an extension with a
   gust-event trigger. **Small–Medium.** *Distinct:* the Warscar is a counter and a wind-harp,
   and its silence is the alarm. Here silence is **normal**, and the *sound* is the event.
9. **The rumor-sites: the durrgak's rings** *(marks 9 and 4).* The free tier is fill #2 (rings,
   caches, the "someone was here" thought). On the campaign tier, a few rings are **wrong**:
   too big and too old for a durrgak, aligned to something. Reading one advances a staged-lore
   ladder (the engine is built; Warscar's rung #9 precedent) toward the Nightbrother whisper.
   Ban 7 holds: it **never** confirms. *Engine:* prefab/scatter + one `AdvanceStage` call. The
   texts need the owner's pen. **Small.**
10. **Gust turbines: a watt is a wound** *(marks 2 and 3).* §5: *"wind-grasping technology
    breaks often… repair is a way of life"*. A crags turbine (a tech unlock from studying a
    **wrecked wind-farm**, a map scatter, the sheet's §8) makes **big power only during a gust**
    and nothing in the still. It needs a battery, and every gust carries a **breakdown roll**.
    *"A working turbine is tended like an animal."* *Distinct from the Leaning Scrub,* explicitly:
    the Scrub's wind keeps a **calendar** you can plan around. The Crags' wind has **no
    pattern**. It is a lottery you buffer against. *Engine:* a CompPowerPlant subclass reading
    a gust signal from the gust driver (which also feeds #8 and the gharrek). **Medium.**
    *Trade-off:* the closest echo on the slate after #7. It could be cut if the Scrub's wind
    already satisfies the owner.
11. **Lightfall: the bottom, written** *(mark 9, campaign).* The owner left *"what waits at the
    bottom"* unwritten, and this asks him to write it. One shape: a descent site (a pocket map
    under tile 9023) that holds the **one place the Dark always dies**, where the deepest etch
    has made a permanently clear, lit chamber, and in it whatever generations of the desperate
    lowered down. This needs his pen, not an agent's. **Medium–Large.** It is offered as a
    question, not a design.
12. **Movement-4 pre-ticket, not a mechanic: the free-tier body wave.** This is owed whatever the
    volley rules:
    - wire the ghorrumak and the zhurrakor;
    - move the cindermare and the skarnix inline to `RM_` (card);
    - fix `surveyShadowBiomes` (correctness, any seat);
    - build fills #1–#3 + `RM_Etchcap` if admitted;
    - queue the dusk-rat art redo;
    - give the free tier its own labels (the label patch is Utinni-only today, so free players see
      "nightling", "darkbeast");
    - add `MayRequire` to the 8 flora rows or own them;
    - execute the rename (§2).

**Recommended volley opener:** **#1 + #2 + #3** as the spine: *"the Dark is a thing in the air
that heat folds away, once in a long while it lifts entirely, and the thunder in the storm is a
dragon."* #1 and #2 are one system (the veil, and its lifting), and #3 is nearly free. Then #5
for the ship (it starts as a one-line fix), #8 for the ear, #6 for the surprise, and #4 as the
resource. #7 and #10 are the two echo risks to rank or cut. #11 is his to write or leave
unwritten. #1–#5 + #8 turn every free-tier MISS except mark 9 into a HIT, and #2 is a partial
on 9.

### What GPT added (`Transient/bedazzle_gpt_enrich_2026-09-30/blackcrags.md`, gpt-5.6-sol)

**Its top three are the same as ours:** the Folded Dark, the Unveiling, and the ghorrumak.

**It sharpened five things, which turn 3 should adopt:**
- **Line-integrated** accuracy penalties, and light-radius attenuation registered **beside**
  `GlowGrid` rather than edited into it.
- The fold-lamp is *"explicitly a heater that clears air, not a magical sensor"* (ban 5).
- The Unveiling reveals things **through normal sight**, not by exposing every secret.
- Etchfall collects in **rings at the edges of warm clearings**, so the heat-fold and the
  resource are one system.
- Starting the grav engine **tears the ship's mask away**, so leaving costs you the hiding.

**It added two things:**
- one shared `RM_GustController`, so the gharrek, the sound and any later system read the
  same pulses;
- the **Veil Vigil** at a durrgak cairn, best performed during an Unveiling. That is the
  gods mark, with no Forsaken on screen.

**It recommended three cuts:**
- **cut gust turbines** (*"mechanically thin and too close to the Leaning Scrub"*);
- **defer grown light** (an echo of the Twilight Deep and Lantern Deeps until the glow is
  measured);
- **do not invent Lightfall's bottom.**

Those three agree with the echo flags above.

## 6. The owner's first volley card

Seven picks, in order. Plain words. Each one says what it costs.

1. **The rename. How deep?**
   - **(a) All the way down,** like the Cauldron: the biome, the mod, the code and both biome
     records become "Black Crags". The old campaign record is still on 1,135 world squares,
     and those ride to the final repaint, as you ruled for the Cauldron.
   - **(b) The free mod and every label now,** with the campaign record renamed when the world
     is remade.
   - **(c) Labels only.**

   **And the cryptid:** do the whispered visitors stay "the Forsakens"? "Forsaken" is already
   your word for the ancient Rakata, and a donor mod has a "Forsaken" faction. Or do they get a
   new name?
2. **The spine.** Should the Black Crags open on these three?
   - **The Dark as a real thing in the air.** It blinds and swallows lamplight, and **heat
     opens clear pockets in it**, so a warm base can see and a cold one is blind.
   - **The Unveiling.** Once in a long while the Dark lifts entirely for a few hours, a holy
     moment.
   - **The ghorrumak.** The thunder in the storms is sometimes a dragon calling.

   *Cost:* the Dark is the largest build on the slate, and it makes fighting here much harder.
   It ships with a strength slider.
3. **The hidden ship.** Should a gravship landed in the Crags slowly **vanish from pursuit and
   orbit**? Raids are slow to find you, trade ships can't reach you, and starting the engine
   breaks the cover. *First, a fix that is owed anyway:* the "pursuers slow down here" rule is
   already built, but it points at the wrong biome record, so it does nothing on your world
   today.
4. **New creatures** (all ours, all living only here). Admit any or all:
   - **gharrek:** gill-fans that burst open across the map at every gust and feed on the air;
   - **durrgak:** a shy digger that lays obsidian rings and neat caches. Someone was here, and
     it never says who. Tamed, it tidies;
   - **krizzak:** a flying moth that **eats light**, so your perimeter lamps go dark one by one;
   - **etchcap:** a gourmet fungus that grows only where the Dark's grain has eaten the rock.

   *Alternates:* krovvak, dhagga, drekkis.
5. **Etchfall that eats walls.** Should the Dark's falling grain **slowly wear down unroofed
   stone and steel**, but leave a sweepable dust (tholin) that refines into fuel? *Cost:*
   decaying walls annoy, and roofs stop it.
6. **Cut or keep the two echoes.** Both GPT and BENCH lean cut or defer on these:
   - **gust turbines** (big power only in gusts, and they break often), which is close to the
     Leaning Scrub's wind;
   - **lamps as crops** (transplanting glowing trees to light a farm), which is close to the
     Twilight Deep's light.
7. **Housekeeping, plus one thing that is yours to write:**
   - May the cindermare and the skarnix (our inventions, not Star Wars canon) move into the
     free mod?
   - May the ghorrumak and the nighthrumbo (zhurrakor), which you already placed here, actually
     be switched on?
   - **Lightfall's bottom:** do you want to write what waits down there now, or leave it
     unwritten for this pass?

---

## 7. Turn 1 rulings (owner, 2026-09-30 23:25 PDT)

Paths and names in §§1-6 predate the rename: `ForsakenCrags` is now `Abyss` (`src/RimMandrake/Abyss/`, `RM_Abyss`, `RUT_Abyss`).

| Card item | Ruling | How recorded |
|---|---|---|
| 1. Rename | **The Abyss**, full rename now. His words, typed: *"Actually I want to call it the Abyss. And do the full rename in content, code, def, mod, and put it all in the consolidated biome mod now."* Not "Black Crags". | Done: `ABYSS_FULL_RENAME_1`. The 1,135 `RUT_ForsakenCrags` tiles in the start save are dead references until the repaint (accepted). The cryptid "Forsakens" naming stays an open question; every "Forsaken" hit for the Rakata, the cryptid and the vaults was left alone. |
| 2. Spine | **The Dark, full**: real air that heat clears, the rare Unveiling, the ghorrumak storm call, strength slider. | Decision taken by question card. `ABYSS_DARK_BUILD_1`. |
| 3. Hidden ship | Yes. His words, typed: *"Yes but probe droids will still come that must be avoided."* | `ABYSS_HIDDEN_SHIP_PROBES_1`. The "pursuers slow down here" rule now lists `RUT_Abyss` and `RM_Abyss` beside the donor (`ScenParts_EmpirePursuit.xml`). |
| 4. New creatures | gharrek, durrgak, krizzak, etchcap, **all admitted**. | Decision taken by question card. One build item each: `ABYSS_GHARREK_BUILD_1`, `ABYSS_DURRGAK_BUILD_1`, `ABYSS_KRIZZAK_BUILD_1` (flier, real flight), `ABYSS_ETCHCAP_BUILD_1`. No art exists for any of them. |

Card items 5-7 (Etchfall walls, the two echoes, housekeeping) were not answered at turn 1 and remain open for turn 2.
