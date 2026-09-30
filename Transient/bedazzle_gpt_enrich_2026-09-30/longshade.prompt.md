You are a senior game designer consulting on a RimWorld mod campaign. The owner wants recommendations to ENRICH one biome that has already been through a design sitting. Be concrete, vivid and buildable in RimWorld 1.6 (XML defs, C# comps, Harmony, incidents, map components, weather, sounds).

BIOME: The Long Shade

Standing rules of this project (binding on every recommendation):
- RimWorld 1.6 with ALL five DLCs assumed present; a Star Wars (old Tatooine / Jawa scavenger clan) campaign on one hand-made fixed planet. No worldgen, no alternative planets.
- Each animal lives in ONE biome unless there is an in-game reason (migration, life stage).
- Invented exotic names are fine; genuine Star Wars canon goes in a separate Star Wars layer.
- Heat is ONE planet-wide kind riding vanilla heatstroke; biomes differ by heat kind (overhead sun, low sun, ambient steam/volcanic).
- Animals or pawns must never vanish without a readable sign of what happened.
- If it flies in the fiction, it flies in the game.
- Every mod ships real Mod Settings.
- A biome's ideas must NOT echo another biome's signature; each biome has its own voice.
- The "bedazzle" bar is nine marks: unique mechanic, discoverable technology, unique resources, surprising creatures, a GIANT beast, a gravship touch, an interesting soundscape, interesting weather, a relationship to the gods.

WHAT THE OWNER HAS ALREADY RULED for this biome (ledger, verbatim; do NOT contradict or re-propose anything cut here):
- 2026-09-29: Movements 1-2 DONE (a05572659): longshade_bedazzle_review_2026-09-29.md. Scorecard 4 HIT / 2 PARTIAL / 3 MISS (misses: 6 gravship, 7 soundscape, 9 gods). Fills proposed: skarrok, vrekka, sippra, tazzok + shadespire, middenbloom, pavecrust. Side finding: 10 of 16 free-tier creatures + vorrel family have finished renders unwired (7 RM_ defs magenta). Volley turn 1 presented.
- 2026-09-30: VOLLEY TURN 2, owner typed this session (guard cannot see the turn; recording under BENCH). Rulings: (1) slate 2 Sh'kaar/ideoligion PARKED - owner: "Ignore ideoligion concept for now." (2) plant fill middenbloom RENAMED maidenbloom - owner: "Middenbloom sounds disgusting. Maidenbloom is better." (3) slate 1 shade awning: owner: "If it's easier than I think let's do it. Assess." - assessment given in-window (grid already counts roofed cells as full shade + 2-cell halo off walls, so a landed ship is already a harbour at zero cost). Owner asked for a full description of the biome as it stands before continuing.
- 2026-09-30: VOLLEY TURN 2 cont., owner typed (recorded under BENCH): verdict "It's ok... but a tad boring unless we get really strict about the dashing animal behavior. If we can do that it's quite interesting." Direction: "the shade should be more interesting. That's where everything's hanging out." Ideation asked on shade pockets: what to discover or fear there other than the animals; young sarlacc raids (one at a time) or juvenile sarlacc emergences; "Maybe some of those shady spots aren't so natural after all?"; Inhabited material: broken-down sand crawlers and other vehicles, desperate moisture farmers. GOLDEN HOUR IN: "I like the golden hour concept. A perpetual beautiful sunset." Asked for many more ideas very different from other biomes. Awning: no build ruled yet. Opus ideation agent launched.
- 2026-09-30: VOLLEY TURN 3 (BENCH develops) DONE: longshade_shade_ideation_2026-09-29.md (0cb1176c1). Strict dash FEASIBLE ~470 lines C# (heat-load body-size term, shade patch graph, sun-cost pathing via Harmony, rest/dash job givers) + directional shade pinned to golden-hour sun angle. Shortlist: Law of the Light (dash+golden hour+dash-radius ring), mirrak false-shadow predator, swimmer's road (one young sarlacc -> your dew ring -> well), crawler road, long carry, farm on the horizon + heliograph, gnomon line. Presented for turn 4 ruling.
- 2026-09-30: VOLLEY TURN 4 rulings, owner typed (recorded under BENCH). CROSS-BIOME LAW: "If we implement the heat load, then places like the Deep Desert and volcanic biomes should absolutely roast you similarly. It can't be a new "kind" of heat." => heat load rides vanilla heat (Heatstroke/temperature), not a new hediff, and applies on every extreme-heat biome. (1) Law of the Light: "yes". (2) mirrak: "yes". (3) swimmer's road: "yes but we can't have animals "disappear spontaneously." There needs to be SOME kind of indication of what happened to them." (4) crawler road: "Cool inhabited vision" - IN. (5) long carry: "Interesting! Actual shadow-casting gear doubles down on the idea of heat building up. I like it. Parisols, shade tents, simple shields you can stand behind. But again, this MUST be applied on other biomes where heat is extreme too... and there shade won't help you (in steam) or sideways shade (deep desert)." Items 6 gnomon, 7 farm/heliograph, 8 smaller ideas: not yet ruled.
- 2026-09-30: VOLLEY TURN 4 final, owner typed: "No on 6 7. Will consider the rest later. Rule them and build it, ticket it out." => gnomon line CUT, farm on the horizon/heliograph CUT, smaller ideas (item 8) DEFERRED to LONGSHADE_SHADE_EXTRAS_1. Volley complete; ticket-out proceeds.
- 2026-09-30: Movement 4 commission DONE: cast bible longshade_bedazzle_cast_2026-09-29.md + art CSV + 47 jobs for 23 subjects (owed art prio 70: mirrak, gloomcast own art, great devourer/groundrunner/fleshbeast/truffle mole, dewfringe sprig, parasol/shade tent/sun shield, 3 crawler-road wrecks, 2 sarlacc kill-sign filths; review-gated prio 60: skarrok, vrekka, sippra, tazzok, maidenbloom, shadespire, pavecrust). Skipped as existing: wrecked landspeeder, dead crawler structure, all wire-only renders. Not commissioned: mirrak hide icon, take-message (code).

THE BIOME'S DESIGN DOCS:
===== design/Jawa/worldbuilding/biomes/longshade_bedazzle_review_2026-09-29.md =====
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
  `RUT_HolyFlamePrecepts.xml` worships **Sh'kaar the All-Searing, the evil sun god**
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
| 9 | Relationship to the gods | **MISS** | No ideoligion/lore content. The hook is already in the campaign canon and nobody has used it: **Sh'kaar the All-Searing** (the evil sun, `divine_satiation_engine.md` §8) — and this is the one biome where the sun never sets. `DeepDesertTribes.xml` is a faction reskin, not a relationship. |

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
   condition)*. The campaign already has an evil sun god, Sh'kaar the All-Searing, whose
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


===== design/Jawa/worldbuilding/biomes/longshade_shade_ideation_2026-09-29.md =====
# The Long Shade — what's in the shade (volley turn 3 ideation, 2026-09-29)

Item: `LONGSHADE_BEDAZZLE_SITTING_1`, volley turn 3. Status: ideation for the owner; nothing
here is ruled.

Builds on: `desert.md` (frozen sheet — §1, §4 "the sprint economy", "the shelter is the trap",
"the patch is a commons", §8 "middens / dew line / wide gaps", §9 "permanent golden hour",
§10 engine facts), `long_shade_bedazzle_2026-09-27.md` (thesis + Rulings Q1–Q12),
`longshade_bedazzle_review_2026-09-29.md` (census, scorecard, slate). Nothing below reopens a
ruling. Invented names follow the ruled Desert register (doubled consonant, 5–7 letters,
-a/-ik/-ok); descriptive English for flora.

## 0. The owner's words this turn

Verbatim, typed (2026-09-29):

> *"It's ok… but a tad boring unless we get really strict about the dashing animal behavior.
> If we can do that it's quite interesting. But the shade should be more interesting. That's
> where everything's hanging out. Read the original sheet again about those shaded regions
> and let's do some ideation around them what's in there to discover or fear other than "all
> the animals?" Might this tie into young sarlacc raids? (One at a time) or juvenile sarlacc
> emergences? Maybe some of those shady spots aren't so natural after all? Inhabited
> definitely could have some great material here. Broken down sand crawlers and other
> vehicles. Desperate moisture farmers. I like the golden hour concept. A perpetual beautiful
> sunset. … Now generate many more possible ideas that are very different than our other
> biomes. Let's spice this baby up!"*

Standing from turn 2: Sh'kaar ideoligion **PARKED** (not developed here) · the dung plant is
**maidenbloom** · golden hour is **IN** · the artist-inspiration mod is
`ARTIST_BIOME_INSPIRATION_MOD_1` (one hook line in §3, nothing more).

**Name-sweep record (this pass).** New invented names used below — `mirrak`, `tollok`,
`harrok`, `skellok` — are **0 files** under `src/ design/ infrastructure/ skills/` and 0 lines
in `infrastructure/artpipe/registry.jsonl` (probe `korrum`: 37 files — the instrument sees).
Rejected as taken: *vellok* (20 files), *kessik* (46). ⚠️ The Wookieepedia search probe failed
for the control (`bantha`) too, so **canon-collision is UNMEASURED** for these four — re-sweep
before any def.

## 1. Strict dashing — can we enforce rest-dash-rest?

**Verdict: yes, and most of it is already on the bench.** Strict dashing is not one mechanic;
it is four, and three of them are extensions of shipped code. The owner's condition — *"really
strict about the dashing animal behavior"* — is met when (a) the open ground *costs*
something a creature can measure, (b) the cost is bounded by body size, (c) creatures plan
routes shade-to-shade instead of straight lines, and (d) resting is what the shade is for.
Build all four and "nothing pursues" stops being a ban we police and becomes physics the
animals obey.

### 1.1 What already ships (MEASURED from `src/RimMandrake/CreatureBehaviors/Source/`)

| piece | what it does today | what strict dashing needs from it |
|---|---|---|
| `RM_MapComponent_ShadeGrid` (151 lines) | `ShadeAt(cell)` 0..1; roofed = 1; else falloff from any building with fillPercent ≥ 0.8 or plant with visualSize ≥ 1.5 within **radius 2, isotropic**; full recompute every 2000 ticks | 🔴 **isotropic** — a ring round every caster, not a shadow. The sheet says *"a shadow four times its own height"* thrown one way forever. See 1.3 — this is the single most important upgrade in this document |
| `RM_HediffComp_ShadeDrivenSeverity` | severity/day lerped between `severityPerDayInSun` and `severityPerDayInShade` by `ShadeAt` | **is already the heat-load engine** — set sun rate positive, shade rate negative and it accumulates in the open and bleeds off in shade. XML only, except: it is gated on the `heatDrivenBurstEnabled` setting (needs its own toggle) and it has no body-size term (1.2) |
| `RM_CompHeatBurstPredator` + `RM_HeatDrivenBurst` | burst → decay → forced Goto to shade when fatigued; polling comp, no Harmony | the predator half of strict dashing is **done** (bearer: `RSW_WraidAlpha`; dakkra def owed) |
| `RM_JobGiver_WanderInShadeGrid` / `RM_ShadeSeekingWanderExtension` | wander prefers shaded cells | becomes the *rest* job (stay put, idle in shade) |
| `RM_JobGiver_SeekShade` / `RM_SeekShadeExtension` | Greentide kit: go under a **roof** past a temperature threshold | reads `roofGrid`, not the grid, and temperature is map-wide (§10) — **superseded for this biome** by 1.2's heat-load trigger |
| `RM_HediffComp_ShadeStagger` | vorrel victim staggers toward shade | the "collapse" end state already has a walker |
| `RM_Comp_ShadowCaster` + follower | gloomcast's shadow carries pirrik | the gloomcast is already a *moving* shade cell the grid must count |

### 1.2 What new work it takes

1. **Heat load — `RM_SunLoad` hediff (XML on the shipped comp + ~20 lines).** Stages:
   *warm* → *heat-laden* (MoveSpeed ×0.8) → *overheating* (Consciousness −, pain) →
   *sunstruck* (downed; lethal if it stays in sun). Positive in sun, negative in shade, so
   **rest time is set by distance run** — the sheet's "rest is thermal accounting" verbatim.
   Add one prop to `RM_HediffCompProperties_ShadeDrivenSeverity`: `bodySizeExponent`, rate
   in sun divided by `bodySize^k`. That single term **is** "dash range is a function of size":
   a bs-0.3 tebbra has seconds, a bs-16 gloomcast has a day. Applies to **colonists too** —
   the player dashes under the same law (the most important consequence; see §2 D1, §4 W1).
2. **The patch graph — `RM_MapComponent_ShadePatches` (~150 lines, medium).** On each grid
   recompute: flood-fill cells with `ShadeAt ≥ 0.6` into patches, record each patch's
   centre, rim cells and area, and link two patches when their nearest-edge gap is ≤ the
   longest dash any resident can make. Per body-size band, a patch's **reachable set** is
   precomputed. This is also what the harbour scorer (ruled marquee #1) and the named gaps
   (Q12) want — build it once.
3. **Sun-cost pathing — one Harmony postfix (~60 lines, small; the LongShade mod already
   carries Harmony for the dewfringe gate).** 🔑 MEASURED via RimSage (decompiled 1.6):
   `PathRequest` has a public `IPathGridCustomizer customizer` whose `GetOffsetGrid()` returns
   a `NativeArray<ushort>` of per-cell cost offsets — vanilla uses it for
   `UsedRectPathGridCustomizer` (roads avoid structures) and `BreachingGrid`. Normal pawn
   movement (`Pawn_PathFollower.GenerateNewPathRequest`) passes **none**. A postfix there
   attaches one shared per-map "sun cost" grid (cost ∝ 1 − ShadeAt, rebuilt with the grid)
   for any pawn whose race carries `RM_DashExtension`. Result: **every vanilla job** — eat,
   flee, hunt, herd-follow, go-to-mate — routes shade-to-shade automatically, with no job
   giver rewritten. This is what makes "strict" cover behaviour we did not write.
4. **The dash itself — `RM_JobGiver_Dash` + `RM_JobGiver_Rest` (~120 lines, small–medium),
   inserted at `Animal_PreMain`.** Rest: in shade with sun-load > 0 → idle/lie down in the
   deepest cell the hierarchy allows (strongest takes the centre — `bodySize` + predator
   flag rank; the weak take the rim). Dash: sun-load 0 and a need elsewhere → Goto the next
   patch on the graph with `LocomotionUrgency.Sprint`. Exposed with no reachable patch in
   range → **sprint to nearest shade regardless of who is in it** ("arriving overheated at a
   shelter already full" — the sheet's worst moment, now emergent). A pre-dash pause
   (60–180 ticks at the rim, facing the target) gives the §9 signature image: *an animal at
   the edge of a shadow, deciding.*
5. **Signalling before the run (optional, small).** A dashing animal checks the target
   patch's occupants first; a predator present there → pick another or wait. §4 "nobody
   commits without asking". A mote/call gives the player the read.

### 1.3 The directional grid — make the mechanical shade the rendered shade

🔑 **The engine CAN render a fixed, long shadow — MEASURED via RimSage.** `SkyManager` sets
the sun-shadow vector every tick from `GenCelestial.GetLightSourceInfo(…Shadow)`, **unless**
`GetOverridenShadowVector()` finds an override — which it takes from any live
`WeatherEvent.OverrideShadowVector` **or any thing carrying a `CompAffectsSky` whose
`OverrideShadowVector` is non-null**. Buildings, rocks and trees already print sun shadows
scaled by `ThingDef.staticSunShadowHeight`. So: one invisible map-anchored thing with a
`CompAffectsSky` subclass pins the shadow vector to a long low-sun angle, permanently — and
`RM_MapComponent_ShadeGrid` casts its mechanical shade **along the same vector**, length =
`staticSunShadowHeight × k` per caster. Rendered shadow and mechanical shade agree by
construction, which is exactly the §10 ⚠️ the sheet said was "cheap to decide now, expensive
to retrofit". (Needs one check: `Graphic_Shadow` skips roofed cells and
`Biome.disableShadows` must stay false.) ~80 lines on the grid + ~40 for the comp.

Consequence for play: patches become **long lee strips on one side of every caster** —
geometry the player can read off the screen and a wall they build throws a shadow they can
predict. That is the biome.

### 1.4 Honest size

| part | size | risk |
|---|---|---|
| `RM_SunLoad` + body-size term | XML + ~20 lines | low |
| directional grid + sky-pinning comp | ~120 lines | medium — must be tested for perf (full-map recompute already every 2000 ticks) |
| patch graph | ~150 lines | medium |
| sun-cost path customizer (Harmony) | ~60 lines | medium — NativeArray lifetime; the one Harmony patch |
| rest/dash job givers + hierarchy | ~120 lines | medium — tuning, not code |
| **total** | **~470 lines C#, one FOUNDRY item, 2–3 build sessions** | Tuning is the real cost: dash budgets per size band need a quicktest with a herd, a predator and a colonist, watched **by the owner** for "does this read as strict". |

Everything reads one grid, so a mod option turning the grid off degrades every animal to
vanilla, as the grid's own contract already promises.

## 2. What's in the shade

The sheet already says what a shadow here *is*: a staging post, a commons stratified
centre-to-rim, a trap, a midden, a dew ring. "All the animals" is the commons half. The other
half, which the sheet names and nobody built, is that **a shadow is the only place anything
on this ground can be kept** — so it is where everything that was ever lost, hidden, planted
or abandoned has ended up, and where anything that wants to be *found* waits. Every idea
below comes from that.

Format per idea: **pitch** · *what the player sees* · why only here · size · reuses · tier.
Sizes: XML · small C# (<150 lines) · big C#. Echo checks against the other ten bedazzle docs
are called out where they bite.

### 2A. Things to DISCOVER

**D1. The gap graves — salvage that lies in the sun.** *"Dying in the open is the only
privacy on this planet"* (§4) means nobody ever retrieves anything from a gap. So the open
between patches is strewn with the mummified, unlooted dead — pack animals still loaded,
travellers with their kit. *Seen:* a glint on the pavement 30 cells out, between two patches.
Getting it is a **colonist dash**: out, grab, back, before `RM_SunLoad` downs them — and the
farther graves are only reachable in a smoke-haze window or in the gloomcast's shadow.
*Only here:* the loot is guarded by geometry, not by a monster; the same strict-dash law that
governs the animals governs your salvager. **The player learns the sprint economy with their
own pawns' bodies.** Size: small (a GenStep scattering `Corpse`+gear on low-shade cells;
the rest is §1). Reuses: §1 sun-load, vanilla corpse/gear gen. Tier: RM (label "sun-dried
remains"). Distinct from the Stillsand's *buried* record — these lie on top, in the light.

**D2. The still gnomons — treasure at the tip of a shadow that never moves.** Somebody, long
ago, understood that the sun here never moves. They raised single standing stones where
nothing else stood, and buried something **exactly where the shadow ends** — because that
spot will be the same in a thousand years. *Seen:* a lone dressed monolith with a carved
line on the ground-face, and a long rendered shadow (§1.3) whose tip lands on a patch of
subtly wrong sand. Dig the tip: a cache. *Only here:* **the only biome on the planet where a
shadow is a coordinate.** The directional grid (§1.3) makes this readable on screen, and the
same fact explains why the builders came here. Some gnomons point at nothing any more —
someone got there first — and one chain points *to the next gnomon*. Size: small (a
`Building` monolith with `staticSunShadowHeight`, a GenStep burying a cache at
`pos + shadowVector × height`). Reuses: §1.3's pinned vector, vanilla `Mineable`/stash
content. Tier: RM (anonymous builders); Utinni can name them later.

**D3. Route cairns — the herders' patch-chain maps.** §7 "known viable routes… worth
mapping". Herder camps leave cairns in patches whose stones are stacked to point along a
viable chain. *Seen:* a small cairn at a patch rim. Study it (one colonist, an hour) and the
map overlays **the chain it marks, with the dash distance of each gap for a human** — which
patches your colonists can actually cross between. *Only here:* the discovery is a route
through light, not a place. Size: small C# (an overlay drawn from §1.2's patch graph, a
`CompUsable` to reveal it). Reuses: patch graph. Tier: RM.

**D4. The shade-cool cellars — someone dug down under a patch.** The coolest ground in the
biome is *under* the deep centre of an old patch. Abandoned root cellars and cisterns open
off the lee of big rocks: hatch → a pocket map one room deep holding stores that kept
(nothing rots in this heat either). *Only here:* the reason to dig is the shade above.
Size: medium (Odyssey pocket-map portal; the Twilight's skylight and the sarlacc throat use
portals too — this is a *cellar*, human-made and small, not a dungeon). Reuses:
`MapPortal` pattern already used by `RM_SeaDiveHatch`. Tier: RM. ⚠️ Echo risk with Stillsand
buried record — kept apart by being **built** rooms under shade, never sand-buried loot.

**D5. The dew wells that remember — dew-line condensers left running.** Ancient condenser
fins set along a patch's dew line, still beading water into stone basins. Drink here and the
basin is a real, small, renewable water source in a rainless biome. *Only here:* water that
exists only because the shadow's edge is cold. Size: XML + small (a building that yields
water only if its cells are rim cells — the dewfringe gate's boundary test). Reuses:
`RM_Patch_DewfringeWildSpawnGate` boundary test, FlowWorks. Tier: RM. Distinct from the
Leaning Scrub's buildable vaporator economy (slate #4 there): these are **relics on the
rim**, not an industry.

### 2B. Things to FEAR

**F1. The mirrak — the shadow that is an animal.** *(new, RM, mirrak)* A flat, broad,
dark-backed ambusher that lies on open pavement and **presents as a shade patch**. An
overheated animal (or colonist) dashing for the nearest shadow reaches it — and it closes.
*Seen:* a dark oblong on the pavement that the grid does not score as shade (and the route
cairns never mark). Tell: no dew halo, no tenants, and the shadow points the *wrong way* —
once §1.3 pins the sun, every real shadow is parallel, and a mirrak's is not. *Only here:*
it preys on the dash itself; it is only possible where every creature's life depends on
reaching shade fast. Ban 3 safe — it never moves to hunt. Size: small C# (an ambush comp —
`RM_CompAquaticAmbusher` is the shipped shape — plus a "counts as shade to the dash job
giver, not to the grid" flag). Reuses: ambusher comp, §1 dash job. **The strongest single
creature idea in this doc**, because it only works if the dash is strict.

**F2. The tollok — the rent of resting.** *(new, RM, tollok)* Tick-like shade-dwellers
clustered in the deep centres of old wild patches; anything that rests there long picks up a
bleeding, itching infestation. *Seen:* animals leaving the best centre early, shaking.
*Only here:* rest is mandatory (§1) so rest has a price; and it is the reason the player's
**own, built** shade is worth more than a natural patch — yours is clean. Size: XML
(hediff + a HediffGiver keyed to resting in wild shade ≥ N hours; small C# for the "wild vs
built" test — roofed cells are built). Reuses: shade grid, vanilla hediff machinery. Tier: RM.

**F3. The overfull patch — the stampede for your roof.** §4's "worst moment available":
a herd arrives overheated at a patch already full, can't wait, and **bolts for the nearest
bigger shade — your base.** Not manhunter: panicked and sun-loaded, they go through
fences and into barns and they will not leave until they have cooled. *Only here:* an
incident whose cause is geometry and heat; it lands **on your doorstep because your roof is
the biggest patch**. Size: small (incident worker; the herd simply runs §1's "exposed, no
reachable patch" branch toward the player's roofed area). Reuses: §1 dash branch, the ruled
harbour ladder (marquee #1) — this is its violent rung. Tier: RM.

**F4. Sunstruck bodies in the rim.** Animals that arrive too late lie downed at the rims,
still alive, still dangerous if you approach (a downed predator bites). Scavengers work only
the patch edge (§4 "Scavengers here specialise exclusively in kills at a patch edge").
*Seen:* a rim littered with the half-dead — free meat, if you go get it past what is eating
it. Size: XML (falls out of §1's sunstruck stage). Reuses: §1. Tier: RM. Enrichment, not a
standalone.

**F5. The heat-shimmer false horizon.** In the open, a colonist with high `RM_SunLoad`
misreads distance: their destination drifts, their dash overshoots the patch. A mental
state, not a map effect. Size: small (a stage on the sun-load hediff that forces a random
offset on the next Goto). Tier: RM. Low priority.

### 2C. Shade that ISN'T natural — hidden, lying, planted

**N1. The empty patch.** 🔑 *(the owner's "maybe some of those shady spots aren't so natural
after all")* Every patch here is crowded — the commons law. So **a perfect, deep, dew-ringed
shadow with nothing in it** is the loudest warning on the map. What is under it is the
sarlacc (§2D S2), the mirrak (F1), a tollok nest, a minefield, or a buried vehicle. The
animals know; the player learns to watch the animals. Size: zero on its own — it is an
emergent read once §1 makes patches reliably full. Stated here because it should be
**designed for**: every "unnatural shade" idea below must empty its patch of wildlife
(`RM_JobGiver_Dash` treats a flagged patch as occupied-by-predator).

**N2. The wreck road — a patch-chain someone built out of dead vehicles.** A clan, long ago,
stripped and dragged wrecked landspeeders, skiffs, cart chassis and a crawler tread section
into a line across a wide gap, each one a shade-caster exactly one human dash from the next.
*Seen:* a dotted line of rusting hulks across the open, every one with animals in its lee.
*The choice:* it is **the richest salvage on the map and it is the only road across the
gap.** Every wreck you strip breaks a link — for the caravans, the herds, and your own
colonists. The Jawa instinct versus the route. *Only here:* salvage whose value is its
shadow. Size: small (GenStep placing wreck buildings with `staticSunShadowHeight` along a
line, chained by patch-graph distance; deconstruct yields). Reuses: `RSW_DeadCaravan` /
`RSW_PodracerWreck` wreck art, Alpha Vehicles-Neolithic carts (`DesertVehicleReskin`),
§1.2 patch graph. Tier: RM for the mechanic (generic "wreck"), RSW for canon hulls.

**N3. The crawler shade — a dead sandcrawler is the biggest harbour for miles.** The
`RSW_DeadCrawler` mutator (shipped, already whitelisted to `Desert`) drops a half-buried
three-deck hull with "sleeping hands" inside. In the Long Shade it is read differently: the
hull throws the **largest shadow on the map** — so its lee is a full stratified commons
(gloomcast in the centre, herds, a dakkra at the rim), and to reach the hatch you walk
through the whole hierarchy. *Only here:* the dungeon's outer defence is an ecosystem using
it as shade. Size: XML (give the hull a big `staticSunShadowHeight`; let §1 do the rest).
Reuses: `RSW_DeadCrawler`, `RSW_GenStep_DeadCrawler`. Tier: RSW (canon sandcrawler).

**N4. The lure awning — shade as bait.** Hunters' craft: a cheap stretched-hide awning on
poles that casts a patch where there was none, placed one dash from a herd's route. Game
comes to it. *Player-buildable* (after studying a herder's blind, D3-style): place it, and
the next dashing herd stages under your hunters' guns. *Only here:* the one biome where
**you can bait with geometry.** Cost: a dakkra may take tenancy first. Size: XML (a
building that casts shade and is not roofed — or is roofed; the grid counts either).
Reuses: shade grid. Tier: RM.

**N5. The dry vaporator stands — shade the farmers left behind.** The moisture farmers'
tall vaporators are the only man-made verticals out here, and each throws a long thin
shadow with its own dew line. Abandoned ones stand in lines across old fields — **a manmade
patch-chain nobody meant to build**, now colonised. Repair one and it works again (and the
wildlife in its lee is now your problem). Size: XML (reuse the KotOR vaporator art —
`Absorbed_KotorCore_Building_MoistureVaporators.xml`, ⚠️ that file is flagged
"do not deploy until it retires" — confirm the absorption state first). Tier: RSW (canon
vaporator). ⚠️ Echo: Leaning Scrub slate #4 owns *buildable moisture farming*; this is kept
distinct as **ruins that happen to be shade**, and its gameplay is the patch, not the water.

**N6. The mirror field.** *(bold)* An old array of sun-tracking mirrors that no longer
track — frozen, like the sun, at the angle they last held. They **throw light into shadows**:
certain patches are *unshaded* by a beam from half a map away. Turn a mirror (a repair job)
and a patch opens up, or another one dies. The only object on the planet that **edits the
shade map**. Size: big-ish (grid needs a "lit by mirror" subtraction; the mirror is a
rotatable building; ~150 lines). Tier: RM. See §4 W3.

### 2D. The SARLACC young — one at a time

What exists (MEASURED, `src/RimStarWars/Sarlacc/`): `RSW_SarlaccSwimmer` — Stage I, a mobile
sub-sand predator with a **fixed water reserve spent on every strike and metre**, that
"does not chase" and "does not strike anything that carries no water — droids pass over it
unnoticed"; `CompSarlaccSwimmer` roots it into `RSW_SarlaccAnchored` (Stage II, a pit that
strikes only at what stands beside its mouth) on a `RSW_DeepDesertSeep` or when it runs dry;
Stage III the cistern; the "changed return" hediffs for the swallowed. Home: the **deep
desert** (`sarlacc_native_habitat_draft.md`, ACCEPTED 2026-09-12). Owner, 2026-09-02:
*"there are smaller, more mobile ones."*

🔑 **Why a swimmer belongs here without breaking one-home:** the owner's own carve-out is
*"young versions that grow in [one place] then migrate"*. A swimmer is exactly a life stage
that moves — born at a deep-desert cistern, it swims **outward, toward water**, and the
nearest water in its world is the Long Shade's dew lines. So the Long Shade is where the
sarlacc's young **go to root**. That is one creature, one home, one migration.

**S1. The swimmer's crossing — one juvenile at a time.** *(the owner's "young sarlacc raids,
one at a time")* A single swimmer arrives at the soft-sand edge of the map, low on water. It
does not hunt the colony; it goes for **water** — anything wet that stands on soft sand near
a dew line. *Seen:* a sand-wake that moves patch to patch like everything else here (it
dashes too — it spends water per metre), a pause at each rim, then a strike at whatever is
standing on the rim. *The choice:* hunt it (hard — it is under sand, and only on
**hardpan** can it never reach you; ban 6's bargain gets its apex — ⚠️ no owned hardpan
terrain exists yet, review slate #6 `RM_Hardpan`), or **let it root.**
*Only here:* one monster, trackable, whose goal is not you but a place — and the player can
see where it is going. Size: small (IncidentDef + worker that spawns one swimmer at the map
edge; the swimmer's own comp does the rest). Reuses: `RSW_SarlaccSwimmer`,
`CompSarlaccSwimmer` in full. Tier: RSW (canon).
⚠️ Echo check vs the Stillsand's sand busters: the busters are an **infestation you
trigger**, many, erupting. S1 is **one named individual on a journey** — kept apart, and
must stay that way (never a swarm, never erupting from under your base).

**S2. The rooting — a juvenile emergence into a permanent mouth.** *(the owner's "juvenile
sarlacc emergences")* If S1's swimmer reaches a dew ring with enough water it roots: the
patch's tenants flee all at once, the dew line darkens wet, and the mouth opens in the
centre of the shade. **Your map now has an anchored sarlacc — forever**, a well with a
mouth, the deep centre of the best patch on the map owned by something that takes a tithe.
That is N1's empty patch, explained. *Keep or kill:* a rooted sarlacc is water (the anchored
stage "is filling"), pearls (ruled, "sarlacc pearls"), a disposal pit for the Rite of
Offering (ruled v1, *"a rite of offering and forgetting"*) — and a death at the rim now and
then. Size: small (one hook: dew-ring rim cells count as a seep for `CompSarlaccSwimmer`'s
root test). Reuses: `RSW_SarlaccAnchored`, `CompSarlaccAnchoredMouth`. Tier: RSW.

**S3. The droid runner.** The swimmer ignores droids. So in sarlacc country a clan's
droids are the only safe salvagers of a sarlacc-held patch — send a droid to strip the wreck
in the lee of the mouth. The Jawa fantasy, with the sarlacc's own shipped rule doing the
work. Size: zero (already true of the shipped comp). Tier: RSW. Worth stating to the player
in the swimmer's description — it already is.

**S4. The old rooting.** Map-gen variant: some Long Shade maps start with an anchored
sarlacc that rooted decades ago under the deepest patch — its apron of pressed residue ringing
the shade. Size: XML (GenStep placing `RSW_SarlaccAnchored` under the largest patch). Tier:
RSW. ⚠️ Keep rare; the cisterns are the deep desert's.

⛔ **Cut:** a sarlacc *egg clutch* in the middens — it echoes the Stillsand's eggs-as-water
and the deep desert's birth-trap eggs, and the swimmer's birth belongs to the cistern.

### 2E. INHABITED — broken crawlers, stranded people, desperate farmers

**I1. The desperate moisture farm — a homestead the ecosystem is besieging.** The ruled
harbour ladder (marquee #1) happening to **somebody else**. A moisture-farmer family's
roofed homestead is the biggest shade for a day's walk, so everything alive has moved into
their yard: a dakkra holds the barn shadow, a herd is packed against the south wall, the
vaporators are down because nobody can reach them alive. *Seen:* an Inhabited place with
the family indoors, rationing, and the whole biome's hierarchy standing outside. *Player:*
clear the yard (and get paid in water and a vaporator), trade them passage, or wait for them
to give up and inherit the stand. Size: small–medium (an `RM_InhabitedPlace` variant +
seeding the yard with §1 residents). Reuses: `Inhabited` (HOMESTEAD cast roster, 10 named
characters), `RSW_GenStep_MoistureFarm` template, the harbour ladder's incident rungs.
Tier: RM mechanic, RSW dressing (moisture farm is canon). **Distinct from Leaning Scrub**:
no farming economy — the farm is a siege.

**I2. The waiting camp — stranded at the last patch before the gap.** §8: "the last patch
before a wide gap is the most contested real estate in the biome". Travellers whose beast
died, who cannot cross: a camp of a dozen people sharing one shadow with the wildlife,
rationing. They pay for **shade on the move** — escort them across (your colonists carrying
a portable awning, W1, or walking in the gloomcast's shadow). *Only here:* a rescue whose
obstacle is 40 cells of sunlight. Size: small–medium (quest; `RM_Stranded` in
`StrandedQuest` is the in-house quest shape — a survivor who must be sheltered until
collected). Tier: RM.

**I3. The shade-rent men.** A Junkers-style crew has claimed a dead crawler's (N3) lee and
charges rent for shade — caravans pay in water to rest. Deal with them, displace them, or
become them. Size: XML-first (an Inhabited place on `RSW_DeadCrawler` with JUNKERS cast;
`CastRoster_JUNKERS.xml` exists). Tier: RSW/Utinni.

**I4. The broken caravan in the gap.** A caravan whose draught animals collapsed
mid-crossing (`DesertVehicleReskin`'s carts, `RM_DraughtFuelExtension` — carts that run on
animals): the carts are shade now, the crew is sheltering under them, and they have one
day's water. Rescue in the sun (D1's dash, with lives), or salvage later. Size: small (event
spawning the shipped `RSW_DeadCaravan` layout live, with living crew). Reuses:
`RSW_DeadCaravan`, `DesertVehicleReskin`. Tier: RSW.

**I5. The Jawa crawler that comes back.** The crawler in N3 was somebody's. Once a map's
dead crawler has been looted, a Jawa clan may arrive to reclaim it — trade, dispute, or a
salvage-rights fight, and on good terms they will **tow it**, and the map's biggest shadow
leaves with them (every tenant of the lee stampedes for the next — F3). Size: medium
(incident + a tow visual that despawns the hull). Tier: Utinni (Jawa clans). The most
Jawa idea here.

## 3. Golden hour

**IN (owner, turn 2): "A perpetual beautiful sunset."** The sheet's own §9 line: *"a sunset
that has been going on for a million years."*

### 3.1 How — one comp does sky, glow and shadow (MEASURED via RimSage)

Vanilla `CompAffectsSky` (Verse) exposes three virtuals that `SkyManager` reads every tick
from any spawned thing carrying it: `LerpFactor` (how strongly it overrides), `SkyTarget`
(glow + a full `SkyColorSet` — sky, **shadow colour**, overlay, saturation — + sun-shine
size/intensity), and `OverrideShadowVector`. Vanilla uses it for animated flashes; a
subclass with `LerpFactor => 1` forever is a **permanent sky**. So:

- **`RM_CompGoldenHour`** on one invisible, unselectable map-anchor thing that the biome's
  map-gen places (or the permanent condition spawns): `SkyTarget` = low amber glow (~0.55–0.65,
  enough to work and grow by — tune against plant growth), sky colour warm apricot → rose at
  the overlay, **shadow colour a cool violet-blue** (the sheet's warm/cool split: *"amber,
  ochre, rust against long cool blue shadows"*), and `OverrideShadowVector` = one long fixed
  vector. ~60 lines.
- **Why a comp, not only a GameCondition:** the ruled path (§10 / review slate #4) was a
  permanent `GameConditionDef` overriding `SkyTarget` (`RUT_MiasmaWeatherLock` shape). That
  gives colour and glow but **not the shadow vector** — `GetOverridenShadowVector` reads only
  WeatherEvents and `CompAffectsSky` things. The comp gives all three and is the piece §1.3
  needs anyway. Keep the condition as the *carrier* if it is convenient (it shows in the
  condition list as "Golden hour — the sun does not move here"), with the comp doing the work.
- **Shadow geometry becomes gameplay.** Every building, rock and tree with
  `staticSunShadowHeight` prints a long shadow along the pinned vector, and the directional
  grid (§1.3) scores mechanical shade along the same line. **What you see is what shelters
  you.** A player can read a patch off the screen, plan a wall to throw a strip of shade, and
  predict where the dew line will form. Tall thin structures out-shade squat ones — the
  sheet's "leggy" logic applied to architecture.
- **Per-map orientation.** The vector's *direction* is fixed per tile from its position on the
  planet (sunward is always one way on a tidally locked world) — so shadows on every Long
  Shade map point away from the substellar point. Consistent planet-wide, varied per map by
  terrain alone. Arc (60–88°) sets length: nearer the terminator, longer shadows.

### 3.2 Beautiful, not just orange

- **Two-tone world.** Lit faces warm, shadows cool violet; the shipped
  `RM_GlowMultiplierOverrideExtension`/`BiomeGlowPatches` handle glow variants; the colour
  work is the `SkyColorSet`.
- **Sun glare on the horizon edge.** `lightsourceShineSize/Intensity` in the SkyTarget draw
  the sun's shine; a low large soft value reads as a sun sitting on the horizon.
- **Dust-lit air.** A permanent low-alpha warm overlay (vanilla `SkyOverlay`, the shape
  weather uses) with slow drifting motes in the light and none in the shade — the air itself
  shows where the sun reaches. Small C# (overlay whose alpha keys to camera-cell `ShadeAt`).
- **Silhouettes at the rim.** Leggy animals standing at a patch edge read as silhouettes
  against the lit ground — nothing needed beyond §1's pre-dash pause and good art.
- **Terrain art.** Hardpan pale gold in light; deep sand ochre; dew-line fringe the only pale
  green (ban 8 ceiling, Q10).

### 3.3 What golden hour does to other systems

- **Smoke calendar (ruled #2):** haze lowers LerpFactor's glow and **lengthens the vector** —
  the sheet's "a smoke event is shade for everybody" becomes literal: every shadow on the map
  grows, patches merge, gaps close, the herds cross. One number drives it.
- **Never a night.** Ban 1 satisfied by construction; the clock still turns for needs and
  seasons, the light does not.
- **Colonist mood:** a small permanent "endless sunset" thought for newcomers that fades —
  beauty first, then the realisation it never ends. XML.
- **`ARTIST_BIOME_INSPIRATION_MOD_1` hook (one line, filed separately):** the Long Shade's
  subject is *the light itself* — an inspired artist here paints "the sunset that never
  ends", and the golden-hour anchor is the natural place for that mod's trigger to read.

## 4. Wild cards

Bold, and each checked against the other ten biomes' marquees.

**W1. Carry your own shade.** A colonist-worn parasol-frame / shade cape (apparel) and a
two-pawn **carried awning** that casts a moving 3×5 patch. Crossing parties dash under it;
hauling salvage from the gap graves (D1) becomes a formation. *Only here:* you become a
gloomcast. Small C# (a `CompShadowCaster` on apparel/pawn — **`RM_Comp_ShadowCaster` already
ships** for the gloomcast; this puts it on a colonist). Echo: pirrik follows the gloomcast's
shadow — here *you* are the caster. Tier: RM.

**W2. Shadow-shrinking predators — the harrok.** *(new, RM, harrok)* A lean, very tall,
stilt-legged thing that stands motionless in the open and **is its own shade** — it survives
in the sun by being a pole. Hunts by standing at a spot where its long shadow falls across a
rim, so anything resting in that sliver of shade is resting under it. Ban 3 safe (it never
moves to hunt). *Only here:* a predator whose ambush is its shadow. Small C# (it registers as
a shade-caster by height; ambush comp). ⚠️ Echo: mirrak (F1) is the *fake* shadow; harrok is
the *real* shadow with a mouth above it — pick one if the owner wants only one.

**W3. The mirror field (N6), as a puzzle map.** A large mirror array whose frozen angles
decide the local shade map; repairing/rotating mirrors re-lights and un-lights patches. The
herds re-route live. A whole map section is a solvable lock. Big. Tier: RM. No other biome
edits its own light.

**W4. Shade debt — the colony that becomes the harbour, sued for it.** Once the harbour
ladder peaks (ruled #1), herder clans whose route ran through the patch you built on arrive
to demand passage through your yard — a shade right-of-way, as old as the routes. Grant it
(goodwill, traffic, their dung and trade) or wall it (raids). Small–medium (incident + faction
logic). Tier: Utinni (herder clans). Distinct from the Twilight's permits (you *grant* here,
you are not granted).

**W5. The skellok — the shadow-ferrying swarm.** *(new, RM, skellok)* Tiny flat insects that
never enter the light — they **lay themselves down in a line** to make a strip of dark for
each other and roll forward like a carpet, a centimetre of shade on the move. A colony of
them is a slow-crawling dark streak across the pavement. Harmless; eaten by everything;
their dried carpets are a prized dye (the only black pigment on the dayside). Small (a
wandering filth-trail creature; dye item). *Only here:* shade built out of bodies at insect
scale — the sheet's "herd is infrastructure" at its smallest. Tier: RM.

**W6. The noon stone — the one place the sun is directly overhead.** Somewhere a sinkhole or
shaft lets light fall straight down into a deep canyon — the only place in the whole biome
with **no shadow at all**, a disc of white heat in a bowl of rock. Nothing goes there; so
what dies there is perfectly preserved, and the heat does odd things to materials left in it
(smelts, cures, bleaches). A kiln the planet built. Small–medium (a map feature + a
"sun-forge" recipe usable only on those cells). Tier: RM. ⚠️ Echo check vs the Forge — the
Forge's discoverable tech is heat-industry; keep this a **single natural curio** (bleaching
hides white — a cosmetic material — and curing the vorrel), not an industry.

**W7. The long listeners — signalling as gameplay.** §4 "nobody commits without asking":
animals challenge-and-answer across the gaps before running. Give it sound and a readout —
the calls travel far, and a colonist with Animals skill can **read the calls** to know which
patch holds a predator before crossing. A player can also *mimic* a call to hold a herd in
place or send it on. Small–medium. Tier: RM. Also answers mark 7 (soundscape) with the
biome's own voice.
## 5. Recommended shortlist

**The package: "the light is the law, and the shade is where everything is kept."** The dash
spine makes the open lethal and legible; golden hour makes the shade *visible and
directional*; everything else is a reason to cross the light or a lie about where the shade
is. Ranked — each depends on the ones above it.

| # | idea | one line | size | tier |
|---|---|---|---|---|
| **1** | **§1 Strict dash + directional shade** (sun-load, patch graph, sun-cost pathing, rest/dash jobs, grid cast along the pinned vector) | Every creature — colonists included — rests, dashes, rests, and the shadows it runs between are the ones on screen. | ~470 lines C#, one FOUNDRY item | RM |
| **2** | **§3 Golden hour** (`RM_CompGoldenHour`: sky, violet shadows, pinned vector) | A sunset that never ends, and the shadow it throws is the map. Shares its vector with #1, so build together. | ~60 lines + art tuning | RM |
| **3** | **F1 The mirrak** | The shadow that is an animal — it preys on the dash itself; tell by its shadow pointing the wrong way. | small C# + one creature | RM |
| **4** | **S1+S2 The swimmer's crossing and the rooting** | One juvenile sarlacc migrates in toward water; kill it on the way or let it root and own a well with a mouth, forever. | small (incident + one seep hook) | RSW |
| **5** | **N2 The wreck road** + **N3 crawler shade** | A patch-chain built of dead vehicles across a gap, and the biggest harbour a dead crawler — strip them and you break the road. | small / XML | RM + RSW |
| **6** | **D1 The gap graves** + **W1 carry your own shade** | Unlooted dead lie in the sun because nothing can go get them — except a colonist dashing, or a party under a carried awning. | small each | RM |
| **7** | **I1 The besieged moisture farm** | The harbour ladder happening to somebody else: a family pinned indoors while the whole biome occupies their yard. | small–medium | RM + RSW dressing |
| **8** | **D2 The still gnomons** | The only biome where a shadow is a coordinate — dig where it ends. | small | RM |

**Why this set.** #1–#2 answer the owner's condition and are the only large build; #3–#8 are
all small, all sit on #1's grid, and each is a *different reason the shade matters*: a lie
(#3), a migrating horror (#4), salvage-vs-route (#5), a reason to cross (#6), people (#7),
treasure (#8). None echoes another biome's marquee (checked: Stillsand busters/buried
record/eggs, Leaning Scrub vaporator economy, Twilight skylights/permits, Forge heat
industry, Cauldron, Blue Desert, Cracked Lands, Flooded Canyon).

**Runners-up worth a card row:** F3 the stampede for your roof (the harbour ladder's violent
rung — nearly free once #1 exists), F2 the tollok (makes built shade worth more than wild),
I5 the Jawa crawler that comes back, W2 the harrok (if the owner prefers a real-shadow
predator over the fake one), W3 the mirror field (the boldest).

**Interaction with the ruled marquees (not re-argued):** the harbour ladder (#1 ruled) gains
its violent rung (F3) and its NPC mirror (I1); the smoke calendar (#2 ruled) lengthens the
pinned vector and closes the gaps; the dew line (#3 ruled) becomes directional — dew forms
on the lee strip's edge, so walls placed across the vector make farmland.

**Owed before any build:** canon sweep of mirrak/tollok/harrok/skellok (Wookieepedia probe
failed this pass); `RM_Hardpan` (review slate #6) if S1's hard-ground refuge is to exist; a
perf check of a directional full-map recompute every 2000 ticks.

## 6. The shortlist, lived — expanded, combined, sharpened

Owner, typed, mid-pass: *"Ok, now your turn. Expand, beautify, and improve!"* Each shortlist
item below is developed as what the player **sees, hears and feels** in the shade at golden
hour, then improved — combined with its neighbours where they are stronger together, each
given one moment the player will tell someone about. Feasibility notes stay honest; nothing
here adds a build line that §1–§5 did not price, unless it says so.

### 6.1 The Law of the Light (§1 dash + §3 golden hour, one build)

**What you see.** You land and the sky does not change. It is the colour of the last ten
minutes before dusk — apricot at the horizon, rose overhead — and it stays. Every rock throws
a violet shadow four times its height, all parallel, all pointing the same way, like the map
was combed. In the lee of each one, something is lying down. At the edge of the nearest
shadow a sollak stands with its forelegs in the light and its body in the dark, head up,
facing the next rock thirty cells out. It stands there a long time. Then the whole herd goes
at once — a flat-out sprint across the gold, dust lit behind them — and lands in the next
shadow and drops, flanks heaving. The last calf is two strides behind. It makes it.

**What you hear.** In the open, the shimmer (review slate #3): a dry rising hiss that is not
insects and not wind — the sound of exposure — climbing the longer the camera sits on lit
ground. Pan into a shadow and it cuts to near-silence and one drip from the dew line. Across
the gaps, calls: challenge, answer, and then the run.

**What you feel.** Your first colonist sent to haul something from 40 cells out comes back
with a **heat-laden** icon, walking slowly, and spends an hour lying in the shade of the
cargo pod. You realise the rule applies to you. Every work order on this map is now a route.

**Improvements over §1.**
- 🔑 **Show the budget.** A pawn's inspect pane shows sun-load as a bar, and when a colonist
  is drafted, a faint arc on the ground marks **how far they can go and still get back to
  shade** — their dash radius, computed from the patch graph. The single UI element that
  makes the law legible. Small C# (a `DrawRadiusRing` on the selected pawn's reachable set).
- **Size classes the player can read.** Three named bands in descriptions: *close-country*
  (hill small life, never leaves the dense patches), *gap-runner* (herds and colonists),
  *open-walker* (gloomcast, dewback — can stand in the light for hours). The sheet's "the
  landscape is sorted by size" becomes vocabulary.
- **The memorable moment:** the herd at the rim, deciding — and the player's colonist
  standing beside it, also deciding.

**Honest feasibility.** Unchanged from §1.4 (~470 lines) + §3.1 (~60) + ~40 for the radius
ring. The ring and the sun-load bar are the cheapest parts and the most important for feel.

### 6.2 The mirrak — the shadow that points the wrong way

**What you see.** A dark oblong on the pavement, midway between two patches, about the size
of a shadow a boulder would throw. But there is no boulder. And it lies at an angle to every
other shadow on the map — because every real shadow here is combed by the pinned sun, and
this one was laid down by an animal. A tebbra, overheated and out of range of anything else,
veers for it, sprints the last ten cells, drops into the dark — and the dark closes over it
like a book.

**What you hear.** Nothing, which is wrong: every real patch has a drip, a rustle, a call.
The mirrak's patch is silent.

**What you feel.** Suspicion of every shadow, for the rest of the game. The player starts
checking angles.

**Improvements.**
- 🔑 **The haze unmasks them.** During the ruled smoke calendar's haze act (#2), every real
  shadow on the map **lengthens** with the pinned vector. A mirrak's does not — it is a back,
  not a shadow. So the haze, the biome's season of relief, is also the one time you can see
  every false shadow at once: short dark ovals among long violet strips. Hunting season for
  mirrak hide. Zero extra code — it falls out of §1.3 + ruled #2.
- **Mirrak hide** — a black, flat, matte leather that absorbs light: an item that, made into
  a roof-cloth or awning, casts *deeper* shade (higher `ShadeAt` under it). The predator
  that imitates shade becomes the best shade material. Small (a stuff with a shade-bonus stat
  the grid reads for stuffed casters).
- **It is the tell for N1.** A perfect-looking shadow with no dew halo, no tenants and no
  sound — the animals knew.
- **The memorable moment:** your own colonist, overheated, sprinting for "that shadow there",
  and you noticing the angle one second too late.

**Honest feasibility.** Small C#: ambush comp (the shipped `RM_CompAquaticAmbusher` shape),
a `RM_FalseShadeExtension` the dash job giver treats as shade and the grid does not, and art
for a flat creature (one sprite set; rotation must follow the creature, not the sun — which is
the point). ⚠️ The dash job must be willing to target it; otherwise it never eats.

### 6.3 The swimmer's road — one young sarlacc, one journey, one well

**What you see.** A letter from nobody: *"A sarlacc swimmer has come up out of the deep
desert, following water."* On the map edge, the soft sand is moving — a low wake, like
something just under the skin of the dune. It goes the way everything here goes: rim to rim.
It stops at the edge of every shadow (you can see the sand settle), and whatever is standing
on the dew line there stops standing. It is heading somewhere. You open the patch overlay and
trace its line — and it is heading for **the biggest dew ring on the map, which is the one
your walls make.**

**What you hear.** A low, dry grinding under the sand, audible only when the camera is near
the wake; the shimmer goes quiet around it, as if the light itself is holding its breath.

**What you feel.** A slow-motion siege by one individual. You have days. You can see the
route.

**Improvements.**
- 🔑 **It is going to your house.** The swimmer targets the **largest dew-ring on soft sand**
  (patch graph + rim cells). The harbour law (ruled #1) says your base is the biggest shade —
  so its dew line is the biggest ring. The player's choices are real and geographic: **lay
  hardpan** (the owed `RM_Hardpan` terrain, or paved floor — a swimmer cannot cross it) as a
  moat around your walls; **offer it a better ring** — build a shade wall out in the soft sand
  far from home and let it root there; or **meet it in the gap**, where it is at its weakest
  because every metre costs it water.
- **Its water shows.** The swimmer visibly slows as its reserve drops (the shipped comp
  already spends it per metre and strike); a player who reads it can let the gap wear it
  down — the biome fighting on your side.
- **The rooting.** If it reaches a ring, every tenant of that patch leaves in the same second —
  herds, the dakkra, the pirrik — a silent evacuation — and the dew line goes dark and wet.
  The mouth opens in the centre of the shade. It is yours now: a permanent well that takes a
  life at its rim once in a long while, the shipped Rite of Offering's altar, and a source of
  sarlacc pearls. **One per map, ever** — the incident will not fire while a swimmer or an
  anchored sarlacc of its making lives there (one at a time, as the owner said).
- **Droids walk past it** (S3) — a clan's droids become the only safe crew for work around the
  mouth. Already true of the shipped comp.
- **The memorable moment:** the silent evacuation of a whole patch, all at once, and then the
  sand in the middle of the shade starting to sink.

**Honest feasibility.** Small: one `IncidentDef` + worker (spawn one `RSW_SarlaccSwimmer` at
a soft-sand edge, gated one-per-map), one hook letting `CompSarlaccSwimmer`'s rooting test
accept a dew-ring rim cell as a seep, and a destination bias (target the largest ring). The
evacuation falls out of §1 (an anchored mouth flags its patch as predator-held). RSW tier —
canon creature, `RimStarWars/Sarlacc`. ⚠️ Sarlacc home is the deep desert; the carve-out
("young versions … migrate") must be stated in both biome docs, as the screecher precedent
does for multi-homing.

### 6.4 The Crawler Road — salvage that is also the only way across

*(N2 wreck road + N3 crawler shade, combined: the road leads to the crawler.)*

**What you see.** Across the widest gap on the map, a dotted line of dead machines: a
landspeeder on its side, a cart chassis, a skiff with its rail torn off, a length of crawler
tread — each exactly one human dash from the next, each throwing a long violet strip, each
with something lying in its lee. At the far end, half-buried and tilted, the hull of a
sandcrawler, three decks high, throwing the largest shadow for miles. In that shadow the
biome's whole hierarchy is arranged like a court: the gloomcast in the deep centre, a herd
packed round it, a dakkra at the rim, pirrik in the air. The hatch is at the back.

**What you hear.** Metal ticking as it takes the heat on its lit face; wind whistling through
the tread section; inside the crawler (up close), something mechanical cycling, very slowly.

**What you feel.** Greed and guilt, together. Every hulk is a haul of steel and components,
and every hulk you strip deletes a stepping stone — for the herds, for the caravans, for your
own colonists coming home.

**Improvements.**
- 🔑 **The road can be rebuilt — by you.** Haul a stripped hulk (or build a cheap shade frame)
  into a gap in the chain and the road re-links. The player can be the **road-maker** as well
  as the road-breaker, and extend a chain across a gap nothing has crossed — new traffic, new
  game, new trouble. Ties to W4: herder clans notice who keeps the road open.
- **Breaking a link has a visible consequence.** The next herd that arrives at the missing
  stepping stone stops at the rim, calls, waits — then turns back, or tries the long run and
  leaves its weakest dead on the pavement (which is new salvage — D1).
- **The crawler's sleepers.** The shipped `RSW_DeadCrawler` promises "sleeping hands" inside.
  Here, the sleeping hands are **Jawa-built droids that went dormant in the shade** because
  the shade is where they could keep cool — wake them and they are the crawler's last crew,
  and (I5) somebody will come back for them.
- **The memorable moment:** prying off the last panel of the landspeeder, then watching a
  herd arrive at the empty sand where it stood, and stand there calling.

**Honest feasibility.** Small: a GenStep laying wreck buildings (with `staticSunShadowHeight`)
along a chain whose spacing comes from the patch graph's human dash range; the crawler is the
shipped mutator with a big shadow height. Re-linking is vanilla hauling of a minified wreck
(make the wrecks minifiable — XML). The dormant-droid crew is the one addition, and is
RSW/Utinni content on the shipped crawler.

### 6.5 The Long Carry — the gap graves and the shade you bring with you

*(D1 gap graves + W1 carried awning, combined, and linked to 6.7.)*

**What you see.** Out on the gold, forty cells from any shadow, a pack animal lies where it
fell a hundred years ago, still loaded, dry as paper, its rider beside it. Nothing has ever
come for them — nothing can afford to. Then your party goes out: four colonists under a
stretched hide awning on poles, walking in step, a moving rectangle of violet shade crossing
the light. Halfway, two tebbra break from the nearest patch and run to join them under the
awning. Nobody shoos them.

**What you hear.** The shimmer rising as the party leaves the rocks; under the awning it
drops away to footsteps and breathing; the creak of the poles.

**What you feel.** That you have learned the biome — you are doing what the gloomcast does.

**Improvements.**
- 🔑 **The graves hold stories that point.** Some travellers carry a journal or a scratched
  slate: a page naming a **gnomon** (6.7) and which way its shadow falls, or the location of
  a dew well that no longer shows on any map. Salvage becomes the start of a trail.
- **Hitchhikers.** Small animals caught in the open will run to *any* moving shade, including
  yours. A party under an awning collects a little train of refugees — tameable, huntable,
  and occasionally a mirrak's prey follows them in. Falls out of §1 (the awning is a patch).
- **Mirrak-hide awnings** cast deeper shade (6.2) — the gear loop closes.
- **The memorable moment:** the small wild animals running in to stand under your awning.

**Honest feasibility.** Small each: a GenStep for the graves (corpse + gear + optional journal
item pointing at a real map feature — the item stores a target cell); the awning is a
two-pawn carried object — ⚠️ the cheapest honest version is **apparel** (a parasol frame per
pawn, each casting a small shade via the shipped `RM_Comp_ShadowCaster` logic), because a
true shared two-pawn carried building has no vanilla precedent. Price the shared awning as
medium and ship parasols first.

### 6.6 The farm on the horizon — the besieged homestead and its mirror

*(I1 besieged moisture farm, sharpened with a signalling mirror.)*

**What you see.** A flash on the horizon. Then another: short, long, short. A heliograph —
the one instrument that works forever here, because the sun never moves and never sets.
Somebody is signalling. Your colonist with the best eyes reads it: *water for help.* When you
get there: a roofed homestead with vaporator towers standing in a line across dead fields,
each tower throwing a long thin shadow with a pale dew line — and in every one of those
shadows, an animal. A herd is packed against the house's south wall. A dakkra lies in the
barn doorway. The family has been indoors for eleven days.

**What you hear.** The vaporators' slow hum from the ones still running; from the house, a
child; from the barn, nothing.

**What you feel.** The harbour ladder (ruled #1) from the outside — this is what your own base
will become.

**Improvements.**
- 🔑 **The heliograph is a building you get to keep.** A buildable `RM_Heliograph` (a mirror
  on a mast) lets the colony **talk to neighbours across the map** in this biome only: after
  the rescue, the farm flashes warnings to you — *swimmer seen on the east sand*, *haze
  coming*, *herd heading your way* — early-warning letters for incidents from 6.3 and F3.
  It is the Long Shade's radio, and it works because the light is permanent.
- **Three endings.** Clear the yard (reward: water, a working vaporator, a flashing ally);
  trade them passage out (they leave; you inherit the stand and its shade-chain); or wait —
  they give up and walk into the light, and the homestead becomes a ruin in a later visit,
  the harbour ladder having won.
- **The vaporator towers are the shade** (N5) — clearing the yard means clearing every tower's
  lee, one dash at a time.
- **The memorable moment:** the first flash on the horizon.

**Honest feasibility.** Small–medium: an `RM_InhabitedPlace` variant on the shipped Inhabited
framework (HOMESTEAD roster has 10 characters) + the `RSW_GenStep_MoistureFarm` template +
seeding the yard with §1 residents; the heliograph is a building + a letter-sender keyed to
incidents firing within its range (small). ⚠️ Leaning Scrub owns buildable moisture *farming*;
this is a siege and a signal, not a water economy — keep it that way.

### 6.7 The gnomon line — a treasure map that only the haze can finish

*(D2 still gnomons, improved with the smoke calendar.)*

**What you see.** A single dressed stone standing alone on the pavement where nothing else
stands, taller than anything natural near it, a line cut into its lit face. Its shadow runs
out across the gold, violet, dead straight, and ends on a patch of sand that is very slightly
the wrong colour. It has ended there for a thousand years. Dig: a cache — old, sealed, dry.

**What you hear.** Nothing special — and that is the charm; it is a quiet discovery in a loud
light.

**What you feel.** Kinship with whoever did this. They understood the sun was stopped, and
used it as a pen.

**Improvements.**
- 🔑 **Two tips, one of them hidden.** The builders knew about the haze too. Each gnomon
  marks **two** caches: one at the clear-sky tip, and one further out, **at the tip of the
  haze shadow** — the length the shadow reaches only while the smoke calendar's haze is on.
  The second cache cannot be found except during haze (the shadow must be seen to be read).
  The ruled season of relief becomes treasure season. Zero extra code beyond §1.3 + ruled #2:
  the haze lengthens the pinned vector; the GenStep places the second cache at the haze
  length.
- **Chains.** Some gnomons' shadows end at the foot of the next gnomon — a line across the
  map, ending at something worth the walk (a shade-cool cellar, D4; a sealed dew well, D5).
- **Emptied ones.** Some tips are already dug — someone got there first — and their grave is
  in the gap nearby (6.5).
- **The memorable moment:** the haze arriving, the gnomon's shadow creeping out across the
  sand past the old dig — and stopping somewhere new.

**Honest feasibility.** Small: a `Building` monolith with a tall `staticSunShadowHeight`
(renders the shadow); a GenStep burying cache(s) at `pos + unit(shadowVector) × length` for
clear and haze lengths; the cache is a vanilla buried/minable container. Depends on §1.3/§3.1
(pinned vector) — without it the gnomon is scenery.

### 6.8 How the package plays across a colony's first year

1. **Landing.** The unchanging sunset; combed violet shadows; herds at the rims, deciding.
   The first colonist comes home heat-laden. The dash ring appears when you draft someone.
   *(6.1)*
2. **First weeks.** You roof a shed and the harbour ladder begins: small life moves in. You
   find the Crawler Road and strip one wreck; a herd stops at the gap and calls. *(6.4, ruled
   #1)*
3. **First month.** A flash on the horizon. The farm. You clear the yard one tower-shadow at a
   time and come home with a heliograph. *(6.6)*
4. **The first haze.** Every shadow grows; the herds cross the uncrossable; mirrak show up as
   short dark ovals among long violet ones; a gnomon's shadow creeps out to its second cache.
   *(6.2, 6.7, ruled #2)*
5. **Mid-year.** The heliograph flashes: *swimmer on the east sand.* You have days. Hardpan
   moat, a decoy ring out in the sand, or a fight in the gap. *(6.3)*
6. **Late year.** A Long Carry out to the graves under a mirrak-hide awning, following a dead
   traveller's slate to a gnomon line. The wild things run in under your shade. *(6.5, 6.7)*
7. **And one day** the gloomcast alters its route to your walls (ruled #1), and the pirrik come
   with it, and the sunset has not moved at all.

Every beat above sits on the one build (§1 + §3). That is why it is ranked first: without the
strict dash and the pinned sh

TASK: Give 8 to 12 recommendations that would make The Long Shade richer, more memorable and more distinct, filling the weakest of the nine marks first. Improve and extend what is ruled rather than restarting it. For each recommendation:
- **Name** and a one-line pitch
- What the player sees, hears and feels
- Which of the nine marks it lifts
- How it could be built in RimWorld 1.6 and a rough size (XML only / small C# / large C#)
- Why it belongs to THIS biome and no other

Then list your TOP 3 in rank order with one line of why each. Reply in Markdown, at most about 1500 words. Do not ask questions; do not modify any files.