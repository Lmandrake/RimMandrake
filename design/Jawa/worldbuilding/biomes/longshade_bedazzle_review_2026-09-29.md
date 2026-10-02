# Long Shade — bedazzle review (movements 1–2), 2026-09-29

Item: `LONGSHADE_BEDAZZLE_SITTING_1` · program row 8 of `BAROQUE_BEDAZZLE_PROGRAM_1`.
Builds on the ruled sitting `long_shade_bedazzle_2026-09-27.md` (12 questions ruled by the
owner, all executed at `3bf918d54` / `LONGSHADE_RULED_CONTENT_1`); **nothing ruled there is
re-litigated here** — this pass scores what those rulings delivered, finds what they left
open, and lays the slate for movement 3. Template: `leaningscrub_bedazzle_review_2026-09-29.md`.
Everything below is MEASURED from `src/`, the ledger shards, `rosters/desert.json`, the
frozen sheet `desert.md` and the artpipe stores this pass (2026-09-29) unless marked.

## Name mapping confirmation

The biome lives under **three** names, all one def-pair, and none of them is "desert" in
the program table's sense of the *Blue Desert*:

| where | name | evidence |
|---|---|---|
| program table row 8, ruled name (§7 Q2, 2026-09-21) | **Long Shade** | `src/RimMandrake/LongShade/About/About.xml`, packageId `mandrake.rm.longshade`, BiomeDef `RM_LongShade` label *"the Long Shade"* |
| frozen campaign twin | **`RUT_Desert`**, label *"the Desert"* | `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Desert.xml` (FROZEN, header 2026-09-24; still serves the saved world until the terminal paint) |
| sheet / roster / accent doc | **"desert"** — `desert.md` (🧊 FROZEN, `BIOME_FREEZE_FABLE_REVIEW_1`, + 2026-09-27 amendment), `rosters/desert.json` (`"defNames": ["RM_LongShade","RUT_Desert"]`), naming batch **4c** (*"The long shade."*) | the sheet's own thematic handle is "the long shade"; `arid_shrubland.md` is the Leaning Scrub, not this |

Not this biome: `RUT_ExtremeDesert`/`RM_Stillsand` (the Stillsand; the Dune Sea is a REGION
label, owner 2026-09-27), `RUT_BlueDesert`/`RM_BlueDesert` (row 3), `RUT_AridShrubland`/
`RM_LeaningScrub` (row 7). The Utinni cast patch is
`UtinniPatches/Patches/WildAnimals_LongShade.xml` (targets `RM_LongShade` by its own xpath).
Live packaging note: the owner's 612-mod list carries **`mandrake.rm.biomes`** (the Baroque
Biomes compose, `BAROQUE_BIOMES_WAVE2_FOLD_1`), not `mandrake.rm.longshade` as a separate
row — the source of truth for content is still `src/RimMandrake/LongShade/`. No pre-rename
residue: folder, packageId, BiomeDef and every owned def already carry the LongShade/`RM_`
spelling, so no rename census is owed.

## What's there

Sources read: all of `src/RimMandrake/LongShade/` (13 def files, 2 C# files, Textures), the
frozen twin, `WildAnimals_LongShade.xml` (both ops resolved from their own xpath),
`rosters/desert.json`, `desert.md` §4c–§10 + amendment, `long_shade_bedazzle_2026-09-27.md`
(esp. its Rulings), naming batch 4c, `LONGSHADE_RULED_CONTENT_1` (closed),
`DESERT_GLITTER_BIRDS_COMMENSALS_1` (closed 2026-09-28), `DEEP_SAND_WALKABLE_TERRAIN_1`
(closed), `DESERT_FAMILY_PORT_EXECUTION_1` (live), `BIOME_SHIP_CONTRIBUTIONS_1`, the
CreatureBehaviors/EnvironmentalHazards/OasisMaker sources the biome consumes, the Stillsand
sitting's rulings (to keep the two deserts' marquees apart), and the artpipe registry /
`done/` / `_artsrc/` / `pending/` / `active/`.

### BiomeDef(s)

Twin architecture, both live:

- **`RM_LongShade`** — `Defs/BiomeDefs/RM_LongShade.xml`, `mandrake.rm.longshade`
  ("RimMandrake: Long Shade"; hard dep FlowWorks, loadAfter creaturebehaviors +
  environmentalhazards). animalDensity **0.4**, plantDensity **0.05**, forageability 0.25 with
  **`foragedFood = RM_UltracactusPad`** (Q3, built), `BiomeWorker_Desert`, vanilla
  `World/Biomes/Desert` worldmap texture. Weather: stock defs only — Clear 90 /
  DryThunderstorm 4 / **Sandstorm 4 (Odyssey's def)** / GrayPall 1 / rain+snow 0.
  Terrain: Sand below fertility 0.8, Soil above, plus one `terrainPatchMakers` entry laying
  **`RM_DeepSand`** patches (perlin 0.045, minSize 60, threshold 0.65) — the walkable-but-slow
  deep sand of the 2026-09-27 ruling (`DEEP_SAND_WALKABLE_TERRAIN_1`, closed `eb5a35214`;
  FlowWorks' `RM_DeepSand.xml`, Standable, pathCost 300, fishable as Freshwater by tag).
- **`RUT_Desert`** — the frozen twin: same numbers, 53 inline fauna rows (all
  `MayRequire`-gated), 8 flora rows, no patch makers (deep sand was ruled after the freeze).

Mod Settings (`RM_LongShadeMod.cs`, 106 lines): master toggle + "Dewfringe confined to the
shade line"; the shade-seeking and contact-venom toggles are pointed at the two kit mods'
own screens. Meets the every-mod-ships-settings rule.

### Flora

**Free tier, inline on `RM_LongShade` (5 rows, shorthand form parsed as elements):**
`RM_Leachmoss` 1.5 · `RM_Ultracactus` 0.8 (OURS, Q2) · `RM_Dewfringe` 0.4 (new, Q6/Q10) ·
`RM_Venomvine` 0.25 · `RM_Vorrel` 0.1. Every one is owned; leachmoss/venomvine are
EnvironmentalHazards kit plants (loadAfter, not hard-dep — the twin gates them
`MayRequire="mandrake.rm.biomes"`, the RM def does not).

**Campaign tier, patch-added (`WildAnimals_LongShade.xml`, second op, `PatchOperationAdd`
onto `RM_LongShade/wildPlants`, 5 rows):** `RSW_SurraGrass` 0.6 · `RSW_Plant_Chakroot_Wild`
0.3 · `RSW_Plant_HubbaGourd_Wild` 0.2 · `RSW_VellaraBloom` 0.12 · `RSW_DommoTree` 0.06.
Chak-root and hubba gourd are genuine canon (Q11). **Surra grass, vellara bloom and dommo
tree are UNRULED** — Q2's recommendation asked for the same canon-or-ours verdict on all
three; the ruling covered the ultracactus only. Two of the three (dommo 0 Wookieepedia hits,
vellara donor coinage) are `RM_` candidates by the same logic that freed the ultracactus,
and they are the free tier's only tree and only bloom.

The vorrel family is BUILT IN FULL and native here: `RM_Vorrel` → `RM_VorrelFruit` →
`RM_Cook_VorrelSeedDish` (Cooking 8, three vanilla stoves, 900 work) → `RM_VorrelSeedDish`;
`RM_VorrelBrood` (SeverityPerDay + `RM_HediffCompProperties_ShadeStagger`) and
`RM_VorrelEuphoria`. Dewfringe carries its own Harmony spawn gate
(`RM_Patch_DewfringeWildSpawnGate.cs`, 144 lines, reads `RM_MapComponent_ShadeGrid`
boundary adjacency, toggleable). Ultracactus + pad + pulp all have art in this mod.

### Fauna (def + patch-added, merged)

**Free tier, inline on `RM_LongShade` — 16 rows:** `JOE_Landopus` 0.5 and `JOE_Cephalope`
0.5 (both `MayRequire="mandrake.rut.patches"` — see the qorrax note), then 14 owned `RM_`
defs in `Defs/ThingDefs_Races/`: `RM_Jellypot` 0.7 · `RM_Bokka` 0.5 · `RM_TruffleMole` 0.5 ·
`RM_GreatDevourer` 0.5 · `RM_Groundrunner` 0.5 · `RM_MatureFleshbeast` 0.5 (bs 6, predator) ·
`RM_Ossik` 0.4 (pack, spd 7.0 — a mount, not a predator, so ban 3 does not bite) · `RM_Kudda`
0.2 · `RM_Thurra` 0.05 (pack, milkable) · `RM_Vosska` 0.05 (predator, sand-swimmer, spd 4) ·
`RM_Khorrak` 0.035 · `RM_Ommok` 0.025 · `RM_Ulgga` 0.015 · **`RM_Gloomcast` 0.015 (bs 16.0)**.
Labels are still the frozen batch-4c working labels (jellypot, great devourer, groundrunner,
mature fleshbeast, truffle mole) except gloomcast, which was ruled.

**Campaign tier, patch-added (first op, `PatchOperationAdd` onto `RM_LongShade/wildAnimals`,
all `MayRequire="mandrake.rsw.swbestiary"`, 37 rows read from the op's own value):**
35 canon rows (Bantha 0.8, Sketto 0.8, Shyrack 0.6, Gorg/Gutkurr/Jamel/LongtailGorg/Ronto/
Wraid 0.4, WraidAlpha 0.15, Eopie/Hrumph/IridonianReek/Jimvu/Kwi/Skalder/Uvak/Varactyl/
Zeer 0.3, Falumpaset/FrilledGorg/Jakobeast/Nerf/Nuna/Shaak/TeeMuss/Worrt 0.2, Bolotaur/
Clodhopper/FeralGrazer/Iriaz/Krykna/Runyip 0.1, Voorpak 0.05, Horax 0.01) plus
**`RSW_Dewback` 0.3** (Q8, IN; slowed 4.7 → 4.4 by
`BiomeFaunaStatAdjustments_Generated.xml`, predator flag: the def carries none) and
**`RSW_GlitterBird` 0.2** (built 2026-09-28, `DESERT_GLITTER_BIRDS_COMMENSALS_1` closed
`04242cb8f`: a Whisperbird reskin carrying `RM_ShadowFollowerExtension`, real flyer,
`MaxFlightTime` 30). Kreetle and gizka are gone as ruled (Q6); no Blurrg (Q8, TAMED-ONLY into
the Leaning Scrub 2026-09-29); the sand-lion import row is dead (Q9).

**Campaign cast: 53 wired species; free-tier cast: 16, of which 14 are owned `RM_` defs.**
The one-home law: kudda and truffle mole now have their ONE home here (cut from the
Stillsand at its sitting the same day); the cephalope/qorrax is deliberately terrain-bound
across both deserts (owner's deep-sand ruling) — annotated, not a leak.

Mechanism bearers, by tier (this is what mark 1 rests on):

| mechanism (all `mandrake.rm.creaturebehaviors`, live C#) | free-tier bearer | campaign bearer |
|---|---|---|
| `RM_ShadeSeekingWanderExtension` + `RM_MapComponent_ShadeGrid` + `RM_JobGiver_WanderInShadeGrid` | `RM_Gloomcast` | (RSW_ShadeWhale source, superseded) |
| `RM_FilterFeedExtension` + `RM_JobGiver/JobDriver_FilterFeedTerrain` | `RM_Gloomcast` | — |
| `RM_CompDungSeeder` (fertilise + seed young plants + chance young creature, shade-gated) | `RM_Gloomcast` → `RM_Filth_Gloomcast` | — |
| `RM_Comp_ShadowCaster` + `RM_ShadowFollowerExtension` + `RM_JobGiver_FollowShadowCaster` | `RM_Gloomcast` (caster) | `RSW_GlitterBird` (follower) |
| `RM_CompHeatBurstPredator` + `RM_HeatDrivenBurst` hediffs (burst-grab-retreat) | **none** — dakkra is the intended bearer, def unbuilt | `RSW_WraidAlpha` |
| `RM_HediffComp_SeedPassage` + `RM_HediffComp_ShadeStagger` (the vorrel corpse-loop) | `RM_VorrelBrood` on any eater | same |
| dewfringe shade-line spawn gate (this mod's own Harmony patch) | `RM_Dewfringe` | same |

⚠️ Three things the 2026-09-27 rulings commissioned are **ruled but not built**, and no item
carries them: (1) the five fillers **sollak / gennok / tebbra / dakkra / pirrik** — art
generated, owner-ruled on the sheet (4 IMPROVE → redo landed as the `_b` sets, 4 KEEP), and
`LONGSHADE_RULED_CONTENT_1` explicitly excluded their defs "gated on the owner's review
sheet"; that gate has opened and **no def item exists** (`git grep -l Sollak|Dakkra|Qorrax|
Pirrik infrastructure/state/items/` → none). (2) The **qorrax** rename — `JOE_Cephalope` is
still wired under its donor name, MayRequire-gated to `mandrake.rut.patches`, with its own
recreated art (`RM_Qorrax`, 6 renders, KEEP) sitting unused. (3) 🔴 **The glitter-bird
exists TWICE**: `RSW_GlitterBird` (built 09-28 as a Whisperbird reskin, zero own PNGs, wired
0.2 in the Utinni patch) and **pirrik** (the sheet's own name for the same creature, 12 KEEP/
IMPROVE renders, no def). "Glitter-bird" is the sheet's invention, not canon, so Q11a says it
belongs in the `RM_` tier as `RM_Pirrik` with the built follow-wiring and the pirrik art —
one creature, one def. A card row, not a finding to act on here.

### Terrain / weather / mechanics / C#

- **Terrain:** Sand/Soil by fertility + owned `RM_DeepSand` patches (built, ruled). No
  pavement/hardpan terrain of our own despite §9's "soft sand sheets vs cracked hardpan
  pavement" and §7's "desert pavement stone" — the hard-ground half of the sheet's
  soft/hard bargain (§4, ban 6) has no def.
- **Weather:** no owned WeatherDef, GameCondition or lock. Sandstorm is Odyssey's stock def.
  The smoke calendar (haze + ash-pulse + sand-lock) is **ruled marquee #2 (Q11)** and unbuilt.
  The "permanent golden hour" render (§10: sky-glow override, the `RUT_MiasmaWeatherLock`
  shape) is feasibility-listed and unbuilt.
- **Mechanics live:** the whole shade kit above; contact venom (`RM_Venomvine` +
  `CompContactVenom`/`MapComponent_ContactVenom`, EnvironmentalHazards); the vorrel
  corpse-loop; dewfringe rim gate; deep sand. The Oasis Maker (`mandrake.rm.oasismaker`,
  `RM_OasisPlacementScorer` carries a copy of `ShadeAt`) is the biome-adjacent water machine.
- **Mechanics ruled, unbuilt:** shade-harbour escalation ladder (marquee #1), smoke calendar
  (#2), dew line as *farmable* real estate (#3 — the plant exists; the fertility/FlowWorks
  condenser half does not), middens (the cheap swap), the wide gaps (Q12: named at the
  repaint window, with the owner).
- **C# in this mod:** 250 lines total (settings + dewfringe gate). Everything else is kit.
- **Lore/ideology layer:** none for this biome. The Utinni tier has `DeepDesertTribes.xml`
  (a `TribeCivil` reskin — the §8 "Deep Desert Tribe holdings", canon no-roads) and the Sump's
  `RUT_HolyFlamePrecepts.xml` worships **Sh'kaar the All-Searing, the searing sun god**
  (`divine_satiation_engine.md` §8) — the dayside's own deity, with no Long Shade content
  touching it.
- **Sound:** none — and the `RM_` move deliberately DROPPED the donor Wounded/Death/Call/
  Angry SoundDefs on all 14 owned creatures (fauna file header), so the free tier's cast is
  silent by def.

### Art status per cast member

Resolved every `<texPath>` in the mod (ThingDef + PawnKindDef lifeStages, folder-aware)
against every `src/*/*/Textures` tree, then searched artpipe registry/done/_artsrc under
BOTH the current and the old port/donor spellings (probes: `imperialtoad` 12 registry lines,
`whisperbird` 78, `korrum` 6 done — the instrument sees):

| cast member | texPath state | artpipe |
|---|---|---|
| `RM_Gloomcast` | **Horax art copy** (`Textures/swanimals/Gloomcast/`, PNGs copied from HoraxArtOverride — header says so) | **0 jobs** under gloomcast/shadewhale/shade_whale; `horax_v1` exists for the Horax itself. The colossus has no face of its own. |
| `RM_Ossik` `RM_Kudda` `RM_Thurra` `RM_Vosska` `RM_Khorrak` `RM_Ommok` `RM_Ulgga` | `Things/Pawn/Animal/RM_<X>/RM_<X>` — **resolves NOWHERE** (magenta in game) | **DONE under the old port names** `rsw_sandstrider` / `rsw_spineroller` / `rsw_sandhorn` / `rsw_dunestalker` / `rsw_ferroclaw` / `rsw_sandmaw` / `rsw_tuskcoil`, 6 files each in `done/` + `_artsrc/` (plus `aa_terramorph_v1` for the khorrak — two jobs, reconcile per `DESERT_FAMILY_PORT_EXECUTION_1`). **Wire-only.** |
| `RM_Bokka` | Stoneback donor path (resolves via SWBestiary's copied BMT art) | `rsw_stoneback` done 6 — wire-only |
| `RM_Jellypot`, `RM_TruffleMole` | BMT donor paths, resolve via SWBestiary copies | `desertportb_jellypot` done — wire-only; truffle mole: 0 under trufflemole/pikkut — owed |
| `JOE_Landopus` / `JOE_Cephalope` | donor | `desertportb_landopus` done — wire-only; **`RM_Qorrax` done 6, KEEP** — wire with the rename |
| `RM_GreatDevourer` `RM_Groundrunner` `RM_MatureFleshbeast` | **Alpha Animals donor paths** (`Things/Pawn/Animal/AA_*`) — resolve only because `sarg.alphaanimals` is active; magenta in the free mod standalone | 0 under greatdevourer/hakkro, groundrunner/dobbak, fleshbeast/vukkoroth — **owed** (three of the 14 owned defs still hard-depend on a donor's textures) |
| `RM_Vorrel`, `RM_VorrelFruit`, `RM_VorrelSeedDish` | **resolve NOWHERE** — magenta today (`Things/Plant/RM_Vorrel` etc. exist in no Textures tree) | `rutstaggerseed` + `rutstaggerseeddish` done 4 in `_artsrc/` (the ledger note of 2026-09-25 said exactly this: rendered, never deployed to any Textures path) — **wire-only** |
| `RM_DewfringeSprig` | item texture resolves nowhere | plant art done (`RM_Dewfringe`, KEEP); sprig icon owed (small) |
| `RM_Ultracactus`, pad, pulp, `RM_Dewfringe`, `RM_Filth_Gloomcast` | own art in this mod | done, KEEP |
| `RM_GloomcastHide`/`Meat`, egg items, `RM_CactusMeat`, `RM_BlackChitin` | donor item icons (`swresource/…`, `AA_EggBeetle`, `AA_Chitin`) | not queued; low priority, but the free mod's own hide references SWAC's texture |
| fillers sollak / gennok / tebbra / pirrik | no def | 12 each (`RM_<X>` + `RM_<X>_b` redo sets), owner-ruled |
| dakkra, qorrax, dewfringe, ultracactus pad | — | 6 / 6 / 2 / 6, all KEEP |
| campaign canon rows (35 + Dewback) | SWBestiary | `desert_swaca_*` (Wraid, Gutkurr, Shyrack, Bantha…) and `desertportb_*` waves done; Dewback 14 files across `canon_dewback_v1`/`dewback_v1` — ride `DESERT_FAMILY_PORT_EXECUTION_1`, not this sitting |

## Nine-mark scorecard

| # | Mark | Verdict | Evidence |
|---|---|---|---|
| 1 | Unique mechanic | **HIT** | A whole *shade economy* in live C#, consumed by this biome's own free-tier defs: the shade grid, shade-seeking wander, sand filter-feeding, dung seeding, shadow-caster/follower, the vorrel corpse-loop (`SeedPassage` + `ShadeStagger`), the dewfringe rim gate. No other biome runs a shade economy (the Stillsand borrows only the caster/follower pair for its mirror giant). Caveat: the burst-grab-retreat predator, the sheet's flagship, has **no free-tier bearer** until the dakkra def lands. |
| 2 | Discoverable technology | **PARTIAL** | The prepared vorrel is a keepable craft (Cooking 8 on any vanilla stove) — but nothing is *discovered*: no research, no study target, no teaching moment; and the khorrak's description promises iron-to-asteroid-alloy transmutation with **no comp, no product def** behind it. The vaporator/dew-condenser and the harbour scorer (ruled marquee) would be the discoveries; unbuilt. |
| 3 | Unique resources | **HIT** | `RM_VorrelSeedDish` (only grows at shaded water pockets, 0.1), `RM_UltracactusPad`/pulp (forage off open sand), `RM_DewfringeSprig`, `RM_GloomcastHide`/`Meat`, `RM_CactusHide`, `RM_Filth_Gloomcast` — all defs live. Art caveat: three of them are magenta today (vorrel family). |
| 4 | Surprising creatures | **HIT** | A plant that kills you from the inside and walks you to shade to die (vorrel, built); a bs-16 grazer that eats the ground (gloomcast, built); birds that live in one animal's shadow (glitter-bird, built 09-28); a deer-sized sand-swimmer bound to deep sand (qorrax, ruled). |
| 5 | GIANT beast | **HIT (art caveat)** | `RM_Gloomcast` bs 16.0, wired 0.015, every mechanic on it live (`ShadeSeeking`, `FilterFeed`, `DungSeeder`, `ShadowCaster`). Its art is a copied Horax; **0 artpipe jobs ever** under any of its names. Sollak (bs ~4, the herd giant) is art-done, def-unbuilt. |
| 6 | Gravship touch | **MISS** | Nothing anywhere references the ship in this biome's voice. `long_shade_bedazzle_2026-09-27.md` §6 proposed the **shade awning** (a landed ship becomes the best harbour on purpose), pavement-stone flooring and the vorrel galley — none was on the 12-question agenda, so **unruled**; `BIOME_SHIP_CONTRIBUTIONS_1`'s running list has no Long Shade row. |
| 7 | Soundscape | **MISS** | No SoundDef, no ambient, no register in the frozen sheet (§9 is light/palette/silhouette/motion only), and the free-tier cast was stripped of even its donor call/wound sounds at the move. The kit precedent exists (`RM_MapComponent_ProximitySoundscape`, Greentide's hum layers; `RM_DeepCalm`) and is unused here. |
| 8 | Interesting weather | **PARTIAL** | Stock weather only (Clear 90; Odyssey's Sandstorm 4). But the **smoke calendar is RULED marquee #2** (Q11, 2026-09-27) — haze weather + ash-pulse condition + sand-lock — and `RUT_MiasmaWeatherLock`/Pyrelands `AshFall` are shipped shapes. Ruled, unbuilt. |
| 9 | Relationship to the gods | **MISS** | No ideoligion/lore content. The hook is already in the campaign canon and nobody has used it: **Sh'kaar the All-Searing** (the searing sun, `divine_satiation_engine.md` §8) — and this is the one biome where the sun never sets. `DeepDesertTribes.xml` is a faction reskin, not a relationship. |

Score as built: **4 HIT / 2 PARTIAL / 3 MISS** — up from the program table's "content
today: 1", because the 09-27 sitting's builds landed (`3bf918d54`, deep sand `eb5a35214`,
glitter-bird `04242cb8f`). The distinctive fact of this biome: **the mechanics bench is the
deepest of the eleven** (seven live C# systems) while the *presentation* half — its own art
for the colossus, seven magenta creatures with finished renders sitting unwired, no sound,
no weather, no gods — is where the misses are. Movement 3 here is less invention than
**making the built biome visible and audible**, plus the two ruled marquees.

## Roster gaps + Proposed fills

### What the rulings already fill, and what they left open

The 2026-09-27 sitting filled the free tier's four livelihood bands (sollak huge-herd,
gennok herd/pack, tebbra herd-small, dakkra burst predator) and the sheet's own owed
glitter-birds (pirrik). With those five landed the free tier fields **21 fauna**. What is
still open, each one a niche the frozen sheet names and no wired species incarnates:

| gap | sheet source | state |
|---|---|---|
| **ambush-flier band** — Shyrack (canon) is the only bearer; the free tier has none | §4 "predator and prey solve positional problems"; Q4's sub-question ("does the band need a free-tier bearer?") was **never carded** — Q4 was answered by "fill gaps creatively" | open |
| **the middens' living face** — nothing works the shadows-as-collection-points, nothing scavenges the open where "dying in the open is the only privacy" | §8 middens, §4 "dying in the open" | open |
| **the dew line's living face** — dewfringe grows on the rim; nothing *lives* on it, though "everything that values the line stands on it" | §8 dew line, §4.3 | open |
| **the smoke calendar's living face** — ash-pulse harvests are "uniquely available" (§7), but no creature answers the ash | §4 "the smoke is a gift, and the ash changes the rules" | open |
| hardpan/pavement specialist — the hard-ground bargain (ban 6: no burrow-ambush on pavement) has no surface-only resident | §4 soft/hard bargain, §9 pavement | open; held back (see below) |
| **flora: only one tree, one bloom, one grass — all campaign-tier and UNRULED** (surra grass, vellara bloom, dommo tree; Q2's same-verdict request went unanswered) | §4b | card row |
| **flora: no vertical shade-caster of our own** — the grid's `CastsShade` already treats any plant with `visualSizeRange.max ≥ ShadeCastingPlantVisualSize` as a shade source, so a tall owned plant IS a shade patch; the free tier has none (dommo is campaign-tier and unruled) | §9 "every vertical is a shade-maker and therefore a landmark" | open |
| flora: nothing grows *on* the middens or the dung — `RM_CompDungSeeder` boosts whatever is nearby; the biome has no plant that belongs to the fertilised ground | §4c dung-seeded growth, §8 middens | open |
| flora: no hardpan crust — pavement is bare | §9 | open |

Other sitting rows found this pass (adjudicate there; nothing done here):
- **The glitter-bird double** (above): `RSW_GlitterBird` vs pirrik — one creature, propose
  `RM_Pirrik` carries the built follow-wiring and the pirrik art, the RSW def retires.
- **The five fillers + qorrax have no build item** though their art is ruled — a movement-4
  ticket regardless of what else this sitting rules.
- **The khorrak's promise**: its description sells iron-to-alloy transmutation; the def has no
  comp and no product. Either build it (slate #5) or rewrite the description.
- **Three owned creatures wear Alpha Animals' textures** (great devourer, groundrunner, mature
  fleshbeast) — the "free" mod goes magenta without `sarg.alphaanimals`. Art owed.
- Accent: the Desert register is RULED (batch 2 + 4c: doubled consonant, 5–7 letters,
  -a/-ik/-ok; rule 7 keeps it); flora runs descriptive-English (leachmoss, venomvine,
  dewfringe) with the vorrel as the one coined exception. Fills below follow both.

### Proposed fills — 4 NEW invented creatures + 3 NEW plants, `RM_` tier, one home each

All collision-swept this pass: `git grep -il` over `src/ design/ infrastructure/ skills/`
(probe `korrum` 82 files, `vosska` 15), artpipe registry + `done/` + `_artsrc/` by both
spellings (probe `sillik` 45 registry lines — which is how *sillik* was CAUGHT: it is a live
Weeping Stones creature, 29 files, and is dropped), and a live Wookieepedia search probe
(`bantha` → 3 hits proves the instrument). Every primary below is **0 files / 0 art / 0
hits**; near-misses are flagged on the alternate, never the primary.

| # | name (alt) | band | the creature |
|---|---|---|---|
| 1 | **skarrok** (*hollik*) | medium ~0.9, TRUE FLYER | The scarp-drop ambusher: roosts on the shaded face of standing rock and *falls* onto whatever surfaces at the rim below — one strike, one glide back into the shadow. No pursuit (ban 3): its whole hunt is a vertical, and the trip back is the bound. The ambush-flier band's free-tier bearer, and the biome's first creature that makes a scarp's height gameplay. Real core-1.6 flight (`MaxFlightTime`/`FlightCooldown`, flip-book owed per the flyer law). |
| 2 | **vrekka** (*brokka* — ⚠ Wookieepedia fuzzy near-miss *Boorka*) | small ~0.5 | The midden-worker: a squat bone-crusher that never sprints because it never has to — it lives where everything ends up, the lee of every rock, and eats what the wind and the dying deliver. Follows corpses into the open (the one thing here that will), drags what it can back into shadow; its heaps ARE the middens' visible surface. Keys to corpses, never to the clock (ban 1). |
| 3 | **sippra** (*lorrik* — ⚠ fuzzy near-miss *Sannus Lorrick*) | small ~0.25 | The rim-walker: a long-legged dew-drinker that lives on the one-cell shade line and nowhere else — walks the halo of every patch, drinks the dewfringe's beads, and is the first thing a player sees standing exactly where the shade ends. Steady, small, edible: the reliable game §7 promises, on the exact ground §8 calls the most valuable. Spawn/wander gated to the same boundary test the dewfringe already uses. |
| 4 | **tazzok** (*mullok*) | small ~0.3, subsurface | The ash-answerer: dormant under the sand for seasons, it surfaces only when ash falls — a grain-scale grazer that eats the ash-fertilised flush and is gone when the wind unpacks the sand. Not a boom (ban 4): a fixed population that *appears*, the way the smoke calendar's whole point is that the rules change for a while. Gives the ruled marquee #2 a creature to be about; dormancy shape = the Stillsand's dust-husk wake pattern, ash-keyed instead of damage-keyed. |

Held back, not proposed: a hardpan runner (*kreppa*, swept clean) — until an owned hardpan
terrain exists (slate #6) there is no ground for it to be the specialist of.

| # | name (alt) | the plant |
|---|---|---|
| A | **shadespire** (*torrak*) | The only vertical that grows: a slow, hard, column-stemmed succulent 3–4 m tall, one every few hundred cells, that the grid reads as a shade-caster — so a shadespire IS a small patch, with its own dew ring, its own tenants and its own midden on the lee side. Fellable for dense pale wood (a real unique material); felling one erases a harbour. The single most useful plant the free tier can own, because it makes the shade economy *grow*. |
| B | **middenbloom** | The dung-and-midden plant: germinates only on fertilised ground (`RM_Filth_Gloomcast` / midden cells / dung-boosted cells), a fat low rosette that is the visible proof a giant stopped here. Harvest = a rich plant-food yield, the ash-and-dung "fertility arrives" law (§5) made pickable. Ban 8: dun and rust, never green. |
| C | **pavecrust** | The hardpan lichen: a thin grey-amber crust on pavement cells, harvestable in scraps for a slow-burn fuel/dye, walkable, unburnable. Gives the bare half of the map a texture and the hard-ground bargain a payoff; pure XML once hardpan terrain exists. |

Each is invented (free to live in `RM_` per Q11a), single-homed here, and none reuses a
neighbour's cast or a neighbour's mechanism (the Stillsand's giants, busters and buried
record are untouched). With the four creatures the free tier fields ambush-flier + scavenger
+ rim-grazer + ash-grazer under and over the ruled five: a food web with a top, a bottom and
a calendar.

### Art already generated — never re-queue (searched by BOTH spellings)

**Finished, owner-ruled, waiting on DEFS:** `RM_Sollak`/`_b`, `RM_Gennok`/`_b`,
`RM_Tebbra`/`_b`, `RM_Pirrik`/`_b` (IMPROVE → redo landed), `RM_Dakkra`, `RM_Qorrax` (KEEP)
— 12/12/12/12/6/6 files in `done/` + `_artsrc/`, `pending/` and `active/` both 0.

**Finished, waiting on WIRING (the def exists, the texPath resolves nowhere or to a donor):**
`rsw_sandstrider` (→ `RM_Ossik`), `rsw_spineroller` (→ `RM_Kudda`), `rsw_sandhorn` (→
`RM_Thurra`), `rsw_dunestalker` (→ `RM_Vosska`), `rsw_ferroclaw` + `aa_terramorph_v1` (→
`RM_Khorrak`, two jobs — reconcile), `rsw_sandmaw` (→ `RM_Ommok`), `rsw_tuskcoil` (→
`RM_Ulgga`), `rsw_stoneback` (→ `RM_Bokka`), `desertportb_jellypot` (→ `RM_Jellypot`),
`desertportb_landopus` (→ `JOE_Landopus`), `rutstaggerseed` + `rutstaggerseeddish` (→
`RM_Vorrel` family, 4 files). **Ten of the sixteen free-tier creatures and the biome's
signature plant have finished art that is not on their defs.** The owed work is a wiring
pass, not a job file.

**Nothing exists for (the only legitimate new jobs):** the gloomcast's own art (0 under
gloomcast / shadewhale / shade_whale; the colossus deserves the 512 treatment sollak got),
great devourer / groundrunner / mature fleshbeast (0 under current and drafted names),
truffle mole (0 under trufflemole / pikkut), the dewfringe sprig icon, and the seven fills
above. Campaign-tier canon rows ride `DESERT_FAMILY_PORT_EXECUTION_1`'s waves
(`desert_swaca_*`, `desertportb_*`, `dewback_v1`/`canon_dewback_v1`) and are not this
sitting's to queue.

## Candidate mechanics slate — ranked, aimed at the MISSes

**Already ruled and riding (Q11, not re-argued):** shade-harbour escalation ladder →
smoke calendar → dew line, middens as the cheap swap; the wide gaps at the repaint window
(Q12). They score as PARTIAL until built and appear below only where a new candidate
*enriches* them. Boundary with the Stillsand (ruled the same day, marquee order sand busters
→ crossing with the giant → the buried record): **world-scale walking-with-the-giant and
dune-burial archaeology are the Stillsand's**; the Long Shade keeps the map-scale gloomcast
shadow and the *surface* middens — aeolian heaps in the lee of casters, not buried caches.

**The name is the hint taken seriously: everything here is a SHADOW, and the sun is a
character.** The biome's fixed sun is the one thing on the planet that never changes, so its
signature family is *exposure* — position as the whole game (the ruled thesis), extended
to the ship, the gods and the ear.

1. **The shade awning — the ship is the harbour on purpose** *(mark 6; §6's own proposal,
   unruled)*. Two facts already shipped make this nearly free: the grid reads every
   ROOFED cell as full shade, and roofs are what a gravship is — so a landed ship is
   already the largest harbour for miles by the grid's own logic; the harbour ladder
   (ruled #1) just has to *count* it. The awning is the deliberate version: an extendable
   ship module (a Building carrying a small `RM_ShadeCasterExtension` the grid's
   `CastsShade` learns to read — ~20 lines) that throws a real shade wake off the hull.
   Payoffs in the biome's voice: sippra and tebbra move into the wake (free hunting at the
   ramp), a dakkra takes tenancy under the landing struts, the pirrik flock roosts on the
   hull, and one day the gloomcast alters its route to the biggest harbour it has ever
   seen — dung-seeding your landing field (`RM_CompDungSeeder`, shipped) and standing
   bs-16 where you wanted to park. **Pavement-stone flooring** (§7, pure XML) and the
   **vorrel galley** (the live-prep cabinet, `RUT_RotSporeKit_LivePrepRecipes` shape) ride
   along as the register row for `BIOME_SHIP_CONTRIBUTIONS_1`. *Uniqueness:* every other
   biome threatens the ship; this one is *hospitable to it*, and hospitality is the threat.
   *Trade-off:* a bs-16 visitor must delay and damage, never hard-block a launch.
2. **Sh'kaar's country — the sun as the god** *(mark 9; Utinni-tier precepts, RM-tier
   condition)*. The campaign already has a searing sun god, Sh'kaar the All-Searing, whose
   own rule (`divine_satiation_engine.md` §8) is that light "does Sh'kaar's work" and
   staying dark and hidden is pious — and this is the one biome where he never looks
   away. Content: (a) a precept pair *Shade-piety* (working under roof is devout; work in
   the open is a small profanity, hunting in the open is a sacrifice) / *Sun-defiance*
   (the inverse cult that goes out at the worst moment on purpose); (b) one ritual, **the
   Shade Tithe** — cutting a new roofed patch as liturgy, the sheet's "building a roof is
   the most powerful act" made sacred, with the harbour ladder as its reward; (c) one
   event, **the Searing** — a rare condition where the golden hour goes white: glow
   multiplier spikes, the grid's falloff radius shrinks (a one-line hook), and every
   creature freezes in whatever shade it has. Devout colonies get a day's warning; the
   defiant get none. (d) The gloomcast as the god's opposite — the thing that *carries*
   shade; killing one is sacrilege to a shade cult and a feast to a sun cult.
   *Uniqueness:* no other biome's god is its weather. *Engine:* `RUT_HolyFlamePrecepts`
   is the precept precedent (reachability: a MemeDef must `requireOne` it), the sky-lock
   shape from §10 for the Searing. *Trade-off:* Ideology content is campaign-tier; the
   Searing condition itself ships RM-tier so the free biome gets the weather without the
   theology.
3. **Heard as heat — the soundscape** *(mark 7; register proposed here, the sheet has
   none)*. The Long Shade is the biome you hear with your skin: in the open, a dry rising
   shimmer that is not an insect and not wind — the sound of exposure — climbing the
   longer the camera sits on lit ground; step into shade and it cuts to near-silence with
   one drip (the dew line). Layers: the gloomcast's tread as a sustainer within its
   `ShadowCaster` radius (you hear it through the ground before you see it); the vorrel
   victim's stagger has a sound; the smoke calendar muffles the shimmer to a hush (relief,
   §9). *Engine:* `RM_MapComponent_ProximitySoundscape` + `RM_ProximitySoundscapeExtension`
   (shipped, Greentide) for the tread; a new ~40-line camera sustainer keyed to
   `ShadeAt(camera cell)` for the shimmer; SoundDefs on the placeholder-clip convention
   (no audio pipeline exists — reuse shipped grains, as every owned SoundDef does).
   *Trade-off:* silence-as-signal needs the shimmer to be genuinely quiet in shade or it
   reads as a bug; the tread must not fire off-map.
4. **The golden-hour sky lock** *(mark 8 — the cheap, unique half)*. §10's own answer to
   "the engine cannot render directional shadow": a permanent `GameConditionDef`
   overriding `SkyTarget` colour/glow to a fixed low amber (vanilla `GameCondition_Aurora`
   is the override shape; `RUT_MiasmaWeatherLock` our shipped permanent lock), so the
   biome's sky belongs to nowhere else on the planet the moment you land. Pairs with the
   smoke calendar (haze dims it), the Searing (whites it) and the shade grid (which stays
   the mechanical truth — the divergence is accepted and stated). *Engine:* XML + small
   C#. *Trade-off:* none worth naming; it is the sheet's own §9 sentence rendered.
5. **The khorrak works — the discoverable alloy** *(marks 2 + 3)*. The def already promises
   it: a khorrak parked among mined iron slowly transmutes it into an alloy "otherwise
   found only in asteroids". Build it: a tamed khorrak penned with steel/ore stacks
   converts them over days into `RM_KhorrakAlloy` (a plasteel-adjacent stuff), and the
   first taming *teaches* it — the knowledge you keep is a working animal, not a research
   node. Steady, slow, un-boomable (ban 4). *Engine:* one comp on the pawn scanning
   adjacent stacks on a long interval (~80 lines), one item def, one recipe-free
   conversion. *Trade-off:* rate must be tuned so it is a livelihood, not a plasteel mine.
6. **Hardpan — the hard ground gets a def** *(marks 1 + 6; the sheet's soft/hard bargain)*.
   An owned `RM_Hardpan` terrain laid by the same patch makers as deep sand: fast, exposed,
   unburrowable — the legal ground for nothing to ambush from (ban 6) and the only place a
   sprint is safe from below. Deep sand = slow and ambushed; hardpan = fast and watched
   from the scarps (skarrok). Pavecrust grows on it; **pavement stone** (§7) is cut from
   it for the ship floor. *Engine:* pure XML + patch makers + a `mineable`/cut recipe.
   *Trade-off:* two owned terrains must read apart at a glance — art-led.
7. **The smoke calendar, enriched** *(mark 8; ruled #2 — enrichment only)*. What the
   ruled three-act weather gains from this slate: tazzok surfaces on the ash act; the
   shimmer (#3) hushes on the haze act; the sky lock (#4) dims; and a rare fourth act, the
   Searing (#2), is the calendar's cruel exception. The ash-pulse growth virtual is still
   UNMEASURED (read Volcanic Winter's decompile before pricing). Nothing here changes the
   ruling.
8. **The dew condenser — the dew line as discovered technology** *(mark 2; ruled #3's
   build half)*. Studying a dewfringe stand (or the ultracactus) teaches a FlowWorks
   condenser that harvests water only on shade-boundary cells — the rim becomes
   plumbing, base *shape* becomes a water decision, and the Oasis Maker's placement scorer
   (shipped, already carries `ShadeAt`) is the placement precedent. *Trade-off:* ban 8
   ceiling on any visible growth it causes.
9. **The surface middens, kept distinct** *(mark 3; the ruled cheap swap)*. Mapgen heaps
   on the shaded lee of every caster (shadespire and rock alike): bone, scrap, organic
   matter, rarely a find; vrekka works them, middenbloom grows on them. `GenStep` on the
   `RM_GenStep_RootCauseways` pattern; mineable-thing tables per the greatbole heartwood.
   Boundary: surface heaps sorted by wind, never the Stillsand's buried record.
10. **Movement-4 pre-ticket, not a mechanic — the presentation wave.** Wire the ten
    finished render sets onto their defs, retire the three Alpha Animals texture
    dependencies, give the gloomcast a face, land the five filler defs + qorrax rename +
    the pirrik/glitter-bird merge. This is the single largest visible delta available to
    this biome and it needs no ruling beyond "yes".

**Recommended volley opener (movement 3):** 1 + 2 + 3 as the spine ("the ship is the
harbour, the sun is the god, the heat is the sound"), 4 riding 2, 5 + 6 as the economy
pair, 7–9 as enrichments of what is already ruled, 10 ticketed regardless. Slates 1–4 turn
all three MISSes and the weather PARTIAL; 5 turns the technology PARTIAL.
