# MIASMA_MECHANICS_1 — C# mechanics kit spec (engine mapping)

Drafted 2026-09-11 against the FROZEN lore sheet
`design/Jawa/worldbuilding/biomes/the_miasma.md` (§0, §3, §4, §4b, §5, §6 hard
bans, §7, Owed) and the RULED comp kit in
`design/Jawa/worldbuilding/alpha_family_source_review.md` §4 (owner, 2026-09-11:
all six RM_ comps IN; build item `ALPHA_MECHANICS_KIT_1`). This spec maps the
sheet's mechanics onto the engine — it invents no lore. Anything marked
**INVENTED** is a tuning parameter this spec had to pick a starting value for;
anything marked ❓ is an engine claim not verified against source and must be
checked before build.

**Source verification basis**: claims below marked *(verified)* were read from
the RimSage source index this session (`mcp__rimsage__search_source` /
`read_csharp_symbol`). ⚠️ Same caveat as `greentide_kit_spec.md`: the index is
consistent with a 1.5-era decompile, so every "vanilla has no X" claim is "no X
**in the indexed source**" with an implicit ❓ against the live 1.6 assembly —
in particular, ❓ **check whether Odyssey added any tide/water-level machinery
before building M2's surge from scratch** (searched `Tide|WaterLevel|Salinity`:
only a worldgen noise constant surfaced). Anchors marked *(verified,
greentide)* were verified at that spec's drafting against the same index:
`BiomeDef.biomeMapConditions` (`Source/RimWorld/BiomeDef.cs:131`),
`GameCondition.ForcedWeather()` and the density/temperature virtuals
(`Source/RimWorld/GameCondition.cs`), WeatherDef `accuracyMultiplier` /
`moveSpeedMultiplier` (`Source/Verse/WeatherDef.cs:47–49`),
`WeatherOverlay_Fog : WeatherOverlayDualPanner`.

**Naming**: generic mechanisms are `RM_` (`RimMandrake.*` namespaces); Miasma
content defs exposing them are `RUT_` (`RimMandrake.Utinni.*`). Per the ruled
§4 resolution, one C# implementation per mechanic, tuned per-biome by XML only.
RM_ classes live in the ruled kit's home (`src/RimMandrake/EnvironmentalHazards/`,
packageId `mandrake.rm.environmentalhazards`) or a sibling RM_ mod if FOUNDRY
splits by weight.

**Hard-ban compliance (sheet §6, linter-checkable)** — how each ban binds this kit:

| Ban | Where it binds |
|---|---|
| 1. No gene machine | M5's boons are **HediffDefs only — never genes, never a directed pick**. The player cannot choose a boon; the Working stays undirected. |
| 2. Rainbow flora never lies | No mechanic in this kit touches the rainbow flora (roster/art owns it); nothing here may attach damage, toxicity, or ambush to those defs. |
| 3. No medicine economy | M5's boons are outcomes, not items; no cure-good, pharmacopoeia, or medical trade def ships from this kit. |
| 4. No clockwork tide | M2's surge is MTB/incident-driven, **never scheduled** — no fixed period field may exist on the def. |
| 5. No rain | `RUT_MiasmaWeather` and every weather this biome can roll carry zero rain/snow rates; the standing lock (M4) makes vanilla rain unreachable. |
| 6. No virus authorship | M4/M5 player-facing strings name engineered plagues at most as "the war's leavings" — no author, ever (the war's §GM gates own it). |

Scoreboard: **6 mechanics** · **2 ruled-comp reuses** (EnvironmentalWeather,
BiomeGlowMultiplier) · **6 new RM_ classes** (1 L, 3 M, 2 S) · XML-only content
on top (biome figures, gear, boon hediffs, set-piece kinds).

---

## M1. The fresh→brine axis (§3 "the gradient as geography")

**Player experience.** Every Miasma map has a direction: one side drinks river,
the other tastes of the dying sea. Trees, muck color, fauna and disease load
sort along it. You site your base by it — and M2 redraws it under you.

**Engine route.** `RM_MapComponent_GradientAxis : MapComponent` — a generic
per-map scalar field (0.0 fresh → 1.0 brine), stored as a coarse per-cell grid,
Scribe-saved. Defined at map-gen by `RM_GenStep_GradientAxis : GenStep` (ordered
after `GenStep_Terrain`): axis direction derived from the tile's river entry vs
coast edge (both live on the map's TileInfo; ❓ exact 1.6 field names for river
links and coastal direction — read `TileInfo`/map-gen source at build), then a
signed-distance gradient with noise so the salt line is a wandering front, not a
ruler. Public API: `SalinityAt(IntVec3)`, `SaltLineCells()`, and
`ShiftAxis(float delta, int durationTicks)` (M2's entry point).

Terrain painting at gen time: the GenStep assigns the water/muck TerrainDefs by
salinity band — fresh channel / brackish / brine / salt-crust (`RUT_` TerrainDef
per band; grades coordinate with `LIQUID_TYPES_MOD_1`, which owns what the
liquids ARE — this kit only consumes the defs). Flora sorting is free: plant
defs restrict by terrain, so the roster pass gets the gradient without code.
Disease-load sorting: M4's exposure severity multiplies by `SalinityAt` band
(**INVENTED**: brine-side ×0.6, mid ×1.0, fresh ×0.8 — the Working ferments
hardest where everything settles, mid-gradient).

Generic on purpose: extension-driven (`RM_GradientAxisExtension` on the
BiomeDef names the bands and terrain mapping) — the Webwork/Scald never need
it, but any future two-water biome does, and M2/M3 are strictly its clients.

**Effort**: **M** (component + GenStep + band painting). **v1: ships** — §5
says the salt line is "the most important line in the biome"; nothing else in
this kit stands without it.

## M2. The breath-tide surge (§3, ban #4)

**Player experience.** Days apart, never on schedule, the sea shoves miles up
the channels: brine terrain crawls inland over hours, brackish pools turn
lethal-salt, the shore side of your map is redrawn. Then the rivers shove back.
No map state is permanent (§5).

**Engine route.** `RUT_Surge` IncidentDef (category ThreatSmall-adjacent
weighted only into this biome) firing `RM_GameCondition_GradientSurge :
GameCondition` (generic — parameterized on direction, magnitude, ramp):

- **Trigger is storm-driven, never clockwork**: base MTB (**INVENTED**: 5 days)
  multiplied down hard while a storm-class weather/condition is active
  (**INVENTED**: ×0.25) — the terminator storms piling the Grey Sea against the
  Salt Gate, priced as weighting, not schedule. 🔴 The def carries no period
  field; the linter can check that.
- **The shove**: over the condition's ramp-in (**INVENTED**: 4–8 in-game
  hours), calls M1's `ShiftAxis` (+delta toward fresh, **INVENTED**: 15–35
  cells of front movement) and repaints crossed cells band-by-band via
  `TerrainGrid.SetTerrain` *(verified, `Source/Verse/TerrainGrid.cs:193`)*.
  Player-placed floors/bridges are **not** repainted (❓ verify the under-floor
  natural terrain layer — `TerrainGrid` holds an under-grid; confirm the
  API and that reflow on floor removal reads the new band).
- **The shove back**: condition end reverses the delta over days
  (**INVENTED**: 2–4), never quite to the old line (small residual drift, so
  no two maps age alike). Recede is what arms M3.
- **Presentation**: forced `RUT_SurgeWeather` during ramp-in (seaward exhale:
  wind sound, thick air; `ForcedWeather()` *(verified, greentide)*), letter on
  arrival, and the salt line drawn as a subtle ground fleck line while the
  condition runs so the player can watch it move.

*Why not a ruled comp*: `RM_GameCondition_EnvironmentalWeather` locks weather
and damages; it has no concept of a moving spatial front. New class, honest.

**Effort**: **L** (the repaint/reflow correctness and its save state are the
kit's hard part). **v1: ships** — it is the biome's signature event and the
sheet's physics ("nothing here ever reaches equilibrium").

## M3. Stranding pools and the stranded (§4 "the stranded")

**Player experience.** The surge recedes and leaves pools behind your base —
cut-off water holding things that should not be ashore: gills going leathery,
fins splaying into feet. Evolution auditioning in your back yard. The pools
shrink over days; what's in them either makes it back to the channels or
doesn't.

**Engine route.** `RM_MapComponent_StrandingPools`, armed by M2's recede:

- **Pool detection**: after each recede step, flood-fill water-band cells; any
  water region no longer connected to the main channel network registers as a
  pool (id, cells, birth tick — Scribe-saved).
- **Stranding spawns**: per pool, weighted roll (**INVENTED**: 40% empty, 50%
  1–2 stranded, 10% something bigger) spawning from a `RUT_StrandedSpawnList`
  def-list the roster pass owns — the transitional endemics are roster
  content; this kit ships only the spawner and the pool lifecycle.
- **Pool decay**: pools shrink cell-by-cell (**INVENTED**: fully dry in 3–8
  days), stranded creatures path toward the nearest channel when their pool
  drops below a size threshold — a simple JobGiver (return-to-water) on the
  stranded kinds, same ~30-line shape as the review's `JobGiver_Mine` note.
- **The next surge erases the ledger**: pools re-covered by M2 deregister;
  their occupants rejoin the wild population.

*Why not a ruled comp*: nothing ruled owns spatial regions or spawn-on-recede.

**Effort**: **M**. **v1: ships in minimal form** (detect, spawn, decay;
return-to-water job may land as "despawn at pool death" first — ❓ flag at
build if the job slips, so the sheet's tragedy isn't silently a despawn
forever).

## M4. Miasma weather — the biome breathing (Owed: "exposure + the mangals' visible thriving")

**Player experience.** The green-gold haze is the default sky: sound muted and
thickened, light softened, sickness in every breath — while the mangals around
you visibly thrive on it. Its absence is the strange day, and it never, ever
rains.

**Engine route.** Reuse-heavy, per the ruled kit:

- `RUT_MiasmaWeather` WeatherDef — native fields for accuracy/movement
  *(verified, greentide)* (**INVENTED**: accuracy 0.85, move 1.0 — the muck,
  not the air, is the movement story; `movementDifficulty 4` already prices
  that in biome XML). Overlay: green-gold haze via a
  `WeatherOverlayDualPanner` subclass or the greentide's
  `RM_WeatherOverlay_GroundFog` with warm textures — share the class, ship new
  art. Ambient sound set muted/thick (`soundsAmbient`, biome XML).
- **The lock**: ruled **`RM_GameCondition_EnvironmentalWeather`** as a
  permanent `biomeMapConditions` entry *(both hooks verified, greentide)* —
  forced `RUT_MiasmaWeather`, no damage fields. Rare clear spells ride the
  condition's config, not vanilla's rain-capable rotation (ban #5 holds
  structurally).
- **The light**: ruled **`RM_HarmonyPatch_BiomeGlowMultiplier`** with
  `RM_BiomeGlowMultiplierExtension` on the Miasma BiomeDef (**INVENTED**:
  multiplier 0.85 — softened, "seen through breath", not the Lantern's dark).
  The review §4.3 already names `the_miasma.md` as this patch's customer.
- **Exposure**: `RM_HediffComp_EnvironmentalExposure` (generic, XML-tuned) on a
  standing map-wide carrier — crib shape:
  `HediffComp_GiveHediffLungRot` *(verified,
  `Source/Verse/HediffComp_GiveHediffLungRot.cs` — MTB-curve gas-exposure check
  with a gene-immunity gate already stock)*. Ours: unroofed pawns during
  miasma weather accumulate `RUT_MiasmaExposure` (mild: breath/consciousness
  shading), severity rate × M1's salinity-band multiplier, native fauna and
  listed races immune (XML). It is the ambient tax; the real diseases stay
  vanilla's, priced by `diseaseMtbDays 15` in biome XML — **no new disease
  system**. Exposure feeding disease chance is deliberately NOT wired (vanilla
  MTB already owns it; two systems would double-charge).
- **The mangals' visible thriving**: `PlantDensityFactor`/growth read of the
  standing condition *(virtual verified, greentide)* — plant growth bonus
  while miasma runs (**INVENTED**: ×1.15), so a clear spell visibly stalls the
  green. Zero rain is biome XML (no rain-capable WeatherDef in commonalities)
  — the trees drink river and sea; §3's plumbing is flavor text, not code.

**Effort**: **S** (one exposure comp + XML; heavy pieces are ruled kit).
**v1: ships.**

## M5. Fever-forged — the boon tables (§4b)

**Player experience.** Surviving a disease in the Miasma sometimes leaves
something behind: a hardened immunity, a small permanent toughness, once in a
great while something genuinely strange. Getting sick here is still terrible —
it is just no longer only terrible. Players learn the arithmetic the pilgrims
know.

**Engine route.** `RM_HediffComp_ForgeOnSurvival : HediffComp` (generic —
attached to disease HediffDefs by XML patch, active only where its props say):

- **Seam**: `CompPostPostRemoved()` *(virtual verified,
  `Source/Verse/HediffComp.cs:48`)*, exactly the crib of
  `HediffComp_RecoveryThought` *(verified — fires on removal, gated on
  `!Pawn.Dead`)*. Additional gates: severity high-water mark ≥ threshold
  (**INVENTED**: 0.6 — a brush with it doesn't forge; track max severity in
  the comp, Scribe-saved) and removal-by-recovery, not by amputation/death of
  part (❓ verify how removal reason is distinguishable at the comp seam —
  worst case, gate on the pawn's `ImmunityHandler` record for the def
  *(class verified, `Source/Verse/ImmunityHandler.cs`)* being ≥ immune
  threshold at removal).
- **Biome gate**: props flag `onlyInBiomes` — fires only when the pawn's map
  biome matches (the Miasma, uniquely, per the sheet). The comp is patched
  onto vanilla + campaign disease hediffs globally; elsewhere it is inert.
- **The table**: props carry a weighted list of boon **HediffDefs** (ban #1:
  never genes, never a player pick) + a `noBoonWeight`. Starting shape
  (**INVENTED** weights; the roster/content pass tunes per sheet §4b's own
  note "the boon tables are the roster/mechanics item's to tune"): 55%
  nothing · 30% `RUT_HardenedImmunity_<disease>` (immunity-gain-speed /
  disease-resist stat offsets, per-disease flavor) · 14% small permanent
  resilience (`RUT_FeverForged_Toughskin` / `_Painworn` / `_Saltblood` — minor
  stat hediffs) · 1% the genuinely strange tier (**content deliberately
  unspecified here — owner card 1**).
- **Presentation**: letter on a boon ("the fever broke, and left something"),
  nothing on no-boon — the table stays illegible, wild-nature, undirected.

*Why not a ruled comp*: `RM_Ability_TargetedHediffAffliction` afflicts;
nothing ruled listens to recovery.

**Effort**: **M** (comp is S; the removal-reason gate and the global patch
hygiene are the work). **v1: ships** with the 1% tier stubbed empty until
card 1 is ruled.

## M6. Warden mothers and the crèches (§4 "the warden mothers", Owed)

**Player experience.** Enormous brine-broken elders lie half-sunk at the
nursery shallows — stationary, lethal within reach, tragic. The juveniles boil
around them. Every map's crèches are placed, mapped and named at generation;
they are never a random spawn, and everything living remembers what you do
there.

**Engine route.**

- **Placement**: `RM_GenStep_PlacedSetPieces : GenStep_Scatterer` subclass
  *(base verified, `Source/Verse/GenStep_Scatterer.cs`;
  `GenStep_ScatterThings` shows the concrete shape)* — generic "set-piece"
  scatterer driven by a def-list: per map, N sites (**INVENTED**: 2–4) chosen
  on brine-side shallow water (validator reads M1's axis — strict ordering
  after `RM_GenStep_GradientAxis`), each spawning one warden-mother pawn + a
  juvenile cluster + a named area marker (`RUT_CrecheMarker` invisible
  building holding the site identity; gives the "mapped and named" ground).
  The warden/juvenile PawnKindDefs are roster content
  (`sea_beasts_roster.md`'s nursery↔adult pairing) — this kit ships the
  scatterer and the marker.
- **Never random**: warden kinds carry zero biome wild-spawn commonality;
  the GenStep is their only entry. Juveniles DO wild-spawn (the shallows
  swarm) — the crèche clusters are on top.
- **Stationary + lethal in reach**: `RM_CompTerritorialAnchor : ThingComp` —
  pawn never paths beyond its anchor radius (**INVENTED**: 12 cells of the
  marker), attacks anything hostile-or-harvesting inside it, ignores
  everything outside. ❓ cleanest seam: a ThinkTree subtree vs a
  wander-radius override (`pawn.mindState` anchor fields exist for hives — verify
  the insect defend-and-return-to-hive nodes at build and crib whichever is
  smaller). Melee stats/size are XML.
- **"Everything living remembers it"** (§8, sacred-adjacent): killing a
  warden or clearing a crèche flips the site's marker to despoiled and
  applies a standing map-wide wild-fauna aggression factor for days
  (**INVENTED**: manhunter-chance factor ×1.5 for 10 days — a factor, not an
  event). Small map component state on the marker. NOT a mood/ideo system —
  the sheet says "not sacrilege in the oasis sense".

**Effort**: **M** (scatterer S + anchor comp M; memory state S). **v1: ships**
placement + anchor; the despoiled-memory factor may land one build later —
flag, not silent.

---

## XML-only ledger (no C#, listed so nothing gets re-invented)

- Biome figures: `animalDensity 6.5`, `movementDifficulty 4`,
  `diseaseMtbDays 15`, forageability 1.0 — BiomeDef XML per sheet §0.
- The attar, delta loam, arthropod foods, flotsam tables — §7 economy, rides
  the **items pass** (sheet Owed), not this kit. Ban #3 patrols it.
- Rainbow flora, mangal trees, all creature kinds — roster/art passes
  (`TREE_GRAPHICS_OWNERSHIP_1`, `sea_beasts_roster.md`).
- Brackish/brine liquid grades — `LIQUID_TYPES_MOD_1` owns the defs; M1
  consumes them.

## New-C# roster (beyond the two ruled-comp reuses)

| Class | For | Effort |
|---|---|---|
| `RM_MapComponent_GradientAxis` + `RM_GenStep_GradientAxis` | M1 | M |
| `RM_GameCondition_GradientSurge` | M2 | L |
| `RM_MapComponent_StrandingPools` (+ return-to-water JobGiver) | M3 | M |
| `RM_HediffComp_EnvironmentalExposure` | M4 | S |
| `RM_HediffComp_ForgeOnSurvival` | M5 | M |
| `RM_GenStep_PlacedSetPieces` + `RM_CompTerritorialAnchor` | M6 | M |

Total: 1 L, 3 M (M1, M5, M6 counting their pairs), 2 S-adjacent (M3 minimal,
M4); two ruled-comp reuses ride `ALPHA_MECHANICS_KIT_1`'s build.

## Build order

1. **`ALPHA_MECHANICS_KIT_1` lands first** (external dependency):
   `RM_GameCondition_EnvironmentalWeather` + `RM_HarmonyPatch_BiomeGlowMultiplier`
   finished shapes (M4).
2. **M4 weather + light + exposure** — near-pure reuse; the biome instantly
   feels right and every later live test happens under the haze.
3. **M1 gradient axis** — the spine; terrain bands need
   `LIQUID_TYPES_MOD_1`'s grades named (defs can stub as recolors first).
4. **M2 surge** — the L item, strictly after M1.
5. **M3 stranding pools** — strictly after M2 (armed by its recede).
6. **M6 warden placement** — after M1 (site validator); anchor comp is
   independent, can land early against a placeholder kind.
7. **M5 fever-forged** — independent of all of the above; slot anywhere;
   boon-table tuning waits on the roster/content pass and card 1.

Cross-item dependencies restated: `ALPHA_MECHANICS_KIT_1` (M4),
`LIQUID_TYPES_MOD_1` (M1's terrain grades), roster pass (M3's stranded list,
M6's warden/juvenile kinds, M5's table tuning), items pass (§7 economy —
deliberately NOT in this kit), `sea_beasts_roster.md` (nursery pairing).

## Owner cards — RULED, sitting 2026-09-12

1. **Strange tier: rule 2–3 strange hediffs NOW** — the tier ships real, not
   empty. ⇒ OWED: draft the 2–3 strange hediffs (design register, boons stay
   hediffs per ban #1, nothing Slime-miracle-shaped) and put them to the owner
   for ratification before def work.
2. **Surge vs player ground: unfloored crops in the band DIE.** Physics, not
   mercy — floors/bridges are the engineering answer, as churnmud in the
   Greentide.
3. **Crèche despoiling: marked sites only.** Open-water juvenile hunting is
   not remembered; the fear stays player-learned, not a mechanical fence.
