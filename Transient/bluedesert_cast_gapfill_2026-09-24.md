# The Blue Desert — cast gap-fill draft

_Drafted by a Fable design subagent, 2026-09-24, for `BLUEDESERT_DESIGN_SITTING_1`.
Rows for the owner to react to — strike or keep. Nothing here is authored; no roster,
sheet or XML is edited by this file._

Frozen sheet: `design/Jawa/worldbuilding/biomes/the_blue_desert.md` (§3 hydrocarbon
biology, §4 roles, §6 bans, §9 theme). Existing cast:
`design/Jawa/worldbuilding/creatures/blue_desert_hydrocarbon_life.md`
(`BLUE_DESERT_LIFE_AUTHORING_1`, closed — and the mechanisms are BUILT:
`src/RimUtinni/UtinniPatches/Source/BlueDesertLife.cs` carries `CompPlantCharge`
(warm-detonation), `RM_HediffComp_ExplodeOnPartDestroyed`, `RM_CompRuinedDetonator`,
`RM_CompEffecter_Halo`, `RM_IngestionOutcomeDoer_ButaneGut`; fauna detonation rides
Core's `HediffCompProperties_ExplodeOnDeath` via `RM_BlueDesertCharges.xml`).

## 1. Coverage map (sheet §4 roles vs existing cast)

| sheet role | status |
|---|---|
| **Swallowers** (sealed herbivore, whole-root swallow, wrong-place wound detonates) | **COVERED-BY `RM_Dorrak`** — hump-gut part-destroyed trigger + `RM_HydrocarbonCharge` r3.9, built |
| **Burners** (blue-fire halo at speed/fight + detonation-on-death) | **COVERED-BY `RM_Krissek`** — `RM_CompEffecter_Halo` + `RM_KrissekHalo` effecter + charge r2.9, built |
| **Pickers** (ablation-line scavengers) | **COVERED-BY `RM_Vekkit`** — corpse-eater herd, charge r1.1, built |
| **Transparent fractal flora** (fern / dandelion-head / fuzzball, warm-detonation) | **COVERED-BY `RM_Glassfern` / `RM_Chimeglobe` / `RM_Palefloss`** — `CompPlantCharge`, wild-only, built (`RM_BlueDesertFlora.xml`) |

**No sheet-owed role is uncovered.** All rows below are DEPTH candidates only —
the roster today is 3 fauna + 3 flora on the planet's sparsest biome (density 0.5 /
0.33, sparse is doctrine). Precedent for depth rows at a sitting: the Weeping Stones
sitting added an RM_ pilgrim herd and a ridge-flier by card.

⚠️ One flag for the sitting, not a row: the three flora labels (glassfern,
chimeglobe, palefloss) are English compounds, kept by the owner's 2026-09-10 card —
they predate the 2026-09-24 coined-name law. Reaffirm or rename; this draft does
not presume either.

## 2. Fauna gap-fill rows (depth candidates — strike freely)

All names pass `check_pseudo_sw_name.py` (advisories only) and are repo-collision
clean. Existing cast is a wall of two-syllable names (dorrak/krissek/vekkit); these
mix 1/1/2/3 per the syllable law.

### 2a. `RM_Zhaaz` — the phase boundary made flesh (slime; long-vowel monosyllable per planet law)

- **Concept:** a slow translucent lobe of living propane slush that creeps the cold
  hollows two degrees from pooling — the biome's own §3 sentence as a creature. It
  digests fallen organics by engulfing; it is the ONLY native that eats a native
  corpse without butchery risk.
- **Mechanism:** `RM_HydrocarbonCharge` (r1.9); §1f heatstroke closes the warm case;
  body/behaviour patterns from `src/RimMandrake/GelatinousSlime`. No new comp.
- **bodySize** 0.7 · **commonality** 0.25 · moveSpeed ~1.2, manhunter 0.
- **Art seed:** a glassy grey-blue puddle-lobe, ice visible through it, faint internal
  shimmer; no face, no limbs; reads wet at −60.

### 2b. `RM_Vrisk` — the haze-skimmer (flier; sky presence)

- **Concept:** a kite-thin flier that rises only when the Haze descends, sieving
  condensing hydrocarbon droplets from the air with fractal gill-fronds — the sky
  niche the biome has none of (mynock/neebray were trimmed away).
- **Mechanism:** real flight per the standing rule — Core `MaxFlightTime` /
  `FlightCooldown` + race flight flags (Locust shape); no flip-book frames needed to
  ship (plainer look is correct). `RM_HydrocarbonCharge` r1.1. Haze-gated activity
  is a nice-to-have (weather check in a JobGiver), not blocking.
- **bodySize** 0.3 · **commonality** 0.3 · wildGroupSize 2~5.
- **Art seed:** a translucent tri-vaned kite with trailing fractal filaments, edge-lit
  blue-white; membrane refracts starfield, never feathers.

### 2c. `RM_Dovvik` — the defuser (EXISTING design, unrostered — ruling owed)

- **Concept:** proboscis siphoner that drains a plant's butane charge without killing
  it — already carded in `RUT_hydrocarbon_ecology_commission.md` §6 (owner did not
  strike it); the life brief's §10 left rostering it as the owner's call. This row IS
  that call.
- **Mechanism:** siphon = a small ThingComp job draining plant HP/charge props; charge
  r1.1. Name stands from the prior card (2-syllable, already swept).
- **bodySize** 0.5 · **commonality** 0.4.
- **Art seed:** low four-legged tick-shape with one long coiled proboscis, matte grey;
  the coil is the silhouette.

### 2d. `RM_Utikka` — the lawn-grazer (prey depth)

- **Concept:** a fist-sized palefloss-cropper that nips filament tips (never the
  root), the krissek's staple prey — today the predator's only prey is the vekkit,
  which mostly stands at carcasses.
- **Mechanism:** all existing — grazing via §2f `ButaneGut` exemption
  (`RM_HydrocarbonNativeExtension`), charge r1.1. Zero new C#.
- **bodySize** 0.15 · **commonality** 0.8 · wildGroupSize 4~8, flees everything.
- **Art seed:** a hopping knuckle of plated grey with no visible head; reads as a
  pebble until it moves.

## 3. Flora gap-fill rows

**GAP: none.** The sheet's silhouette language (§9) names exactly ferns,
dandelion-heads and fuzzballs — all three shipped — and §3's "plants stay small"
plus the ≤1.1-cell cap argue against a fourth form. No row drafted; if the sitting
wants a fourth, the open slot is a rare "seed-lattice drift" ground scatter
(chimeglobe's shed heads as a harvestable ThingDef, not a plant), which is an item,
not flora.
