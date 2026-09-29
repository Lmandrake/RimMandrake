<!-- status: cast bible — commissioned under CAULDRON_BEDAZZLE_SITTING_1 movement 4 -->
# The Cauldron — bedazzle cast bible (movement 4: commission)

**Item:** `CAULDRON_BEDAZZLE_SITTING_1` · **Program:** BAROQUE_BEDAZZLE_PROGRAM_1 (row 5)
**Date:** 2026-09-28 · **Author:** movement-4 commission agent (Fable)
**Feeds:** `CAULDRON_RULED_CONTENT_1` (defs) + `CAULDRON_MECHANICS_BUILD_1` (mechanics)
**Authorities:** `cauldron_bedazzle_review_2026-09-28.md` §Ruled-at-the-sitting (every
ruling below is fixed, owner-typed on the sitting item) · the review's art table and
proposed fills · rename is `CAULDRON_FULL_RENAME_1`'s scope — the mod is
`src/RimMandrake/PoisonForest/` today and **current defNames ship**; this document's
`RM_` names are the NEW defs' names (born post-ruling, so born Cauldron-voiced).

## 0. Shared law — every card obeys this without restating it

- **The ground is LOUD.** Owner ruling 1 REVERSED the frozen sheet's "quiet in a way
  that is wrong": the baseline is a slow steam engine underfoot — rushes, groans,
  sighs, rumbles, gurgles, hisses, dull slow roars. Silence survives only inverted, as
  the vent-bloom alarm (the engine falters). ⛔ No card, description or prompt below
  echoes the dead "silent biome" identity.
- **Name accent** (Batch 4a, ruled): glass and acid — thin front vowels, ts/sk/x/ss
  clusters, -ix/-iss/-eth endings. Invented exotic words, `RM_` tier (Q11a: "Star Wars
  style" naming is not Star Wars IP).
- **Art register (the Cauldron house style for every job below):** a poison forest of
  glass and acid under chemical fog — wet-lacquered darks (black-green, char-brown),
  the dark-crust film's black/purple/red sheen, pale crystal-fan accents, and the
  chemistry's sick green-amber ONLY where something pools, beads or stains; every
  surface carries condensate beading or mineral rings, because every wet surface is a
  dosed surface. Corrosion patina (acid-etch, verdigris, eaten metal) on anything
  industrial. Realistic painted natural-history illustration, grounded believable
  anatomy, matte natural surface texture with wet sheen, never cartoonish, never cute,
  no outlines, alien but biologically plausible. Faced jobs: north is a **true rear
  view from directly behind — no eyes, no face, no frontal features**.
- **One home.** All four natives are Cauldron-only; no multi-homing (owner law
  2026-09-21).
- **Numbers are design proposals** — FOUNDRY calibrates in the build tickets; the
  *relationships* (who is biggest, who is prey, what the shear is worth) are the ruled
  part.

## 1. Name sweep (MEASURED this pass, 2026-09-28)

Instrument: `git grep -il <name> -- src/ design/ infrastructure/state/`.
**Sanity probe: `korrum` → 65 files** (instrument proven able to see; the review's
own probe read 63 two commits earlier — same instrument, tree moved).

| name | files | verdict |
|---|---|---|
| `vexxith` | 4 | CLEAR — all 4 are this sitting's own commissioning prose (review doc, `CAULDRON_RULED_CONTENT_1`, BENCH ledger line, queue render). No def, no other subject. The owner's "collision sweep owed" is hereby paid: **`RM_Vexxith` stands.** |
| `GasTapScaffold` | 0 | CLEAR |
| `FilterWorks` | 0 | CLEAR |
| `FilterCartridge` | 0 | CLEAR |
| `Seismograph` | 2 | CLEAR — both hits are the review doc + mechanics ticket describing this very commission |
| `CauldronVent` | 0 | CLEAR |
| `CorrodedWellhead` | 0 | CLEAR |
| `CondenserStack` | 0 | CLEAR |
| `CorrodedShrine` | 0 | CLEAR |

(vexxiss / zisska / eskith / xithess were collision-swept clean at the review pass,
probe korrum 63; not re-litigated here.)

## 2. Art dedup (standing owner law — searched before queuing anything)

Instrument: filename search over `infrastructure/artpipe/` `done/` (3,873 files),
`pending/` (1), `active/` (1), `failed/` (62), `_artsrc/` (1,780) + content search of
`registry.jsonl` + all 16 `Transient/*.decisions.json`. **Sanity probes: suush → 6
files in done/, 24 registry hits; krissek → 10 files in done/** (the instrument sees).

**Empty everywhere — genuinely owed, queued below:** vexxiss, zisska, eskith,
xithess, vexxith, gas-tap scaffold, filter-works, filter cartridge, seismograph,
corroded ruin pieces (wellhead / condenser stack / shrine), and the Cauldron vent
(the only `vent` art anywhere is `scald2_ventbuilding_a/_b` — the **Scald sea's**
steam-vent building in that biome's register; not reusable here, different biome's
voice and chemistry).

**Found and NOT re-queued** — see §5 wired-by-FOUNDRY.

## 3. Cast entries — the four new natives

### RM_Vexxiss — the solid giant (mark 5)

**Ruled frame (fixed):** solid, **NO explosion anywhere on it** — alive, dying or
dead ("too many exploding giant beasts"). Inhales a vent deeply and that vent's
production pauses for days; pries at gas-tap scaffolds to drink. **Fire warden:**
ignition anywhere near it and it attacks the igniter and smothers the flames out.
Poisons water bodies on touch. Shearing plates off a LIVING vexxiss yields
`RM_Vexxith`; a kill wastes the lode.

**Description (in the biome's voice):**

> The ground here talks all day — rush and groan and gurgle, the slow engine of the
> forest's chemistry — and the vexxiss is the one thing that walks like it belongs in
> the machine. A hill of slag that moves: plates of smelter-scab and old bark grown
> together, crystal fans standing down the spine like vents on a boiler, no eyes
> anywhere on it because it has never needed to see anything. It drinks the ground's
> breath straight from the wellheads, it hates fire the way a lung hates smoke, and
> the crews that shear its plates say the trick is not the climbing. The trick is
> doing it without warming the shears.

**Silhouette/palette brief:** a walking hill — the read from distance is terrain.
Massive low-slung body on pillar limbs, armor of layered slag plates and bark-scab,
crystal spine-fans in a graded row down the back, a blunt eyeless prow of a head that
is more intake than face. Slag greys and char-browns, dark-crust purple-red film in
the plate seams, pale glass-crystal fans as the accent, condensate beading on the
lower plates. 🔴 **HARD BAN: nothing explosive-looking** — no glow-from-within, no
gas-bag translucence, no warning colours, no wick, no distended volatile-looking
volumes. It reads as stone and patience, never as ordnance. And NO eyes.

**Facings:** south, east, north (north = true rear: plated back, spine-fans from
behind, rear pillar limbs). **Canvas 512** — colossus precedent (Vhaulk/Muttavaq):
scale must carry in the pixels. **drawSize intent: ~7.0** (adult), bodySize ~6.0
class — the biggest thing in the forest; slow (the sheet's "nothing fast" law scales
up), rare (0.02-class commonality), neutral until fire or shears give it a reason.

**Def wiring pointers (build: `CAULDRON_RULED_CONTENT_1` §2; behaviors:
`CAULDRON_MECHANICS_BUILD_1` §5):** shear = work-giver operation on a plate body
part (dorrak-hump / vexxiss-plate lineage); no charge hediff of any kind.

### RM_Zisska — the plated crust-grazer

**Ruled frame (fixed):** the RM tier's own herbivore — mineral-rasper, the biome's
one legal herbivory (rasping crust off stone; there is nothing to graze). Butchers
to toxic prized meat + a trace of the metal it concentrated.

**Description:**

> Low and broad as a dropped shield, plated like the stones it eats. The zisska
> spends its life nose-down against rock and old trunks, rasping off the mineral
> rings the forest paints on everything that stands still — and everything it rasps
> stays in it. The Farmers of other countries would call it livestock. Here the
> butchers wear gloves to the elbow, and the meat is worth the gloves.

**Silhouette/palette brief:** tortoise-broad, low-slung, a dome of overlapping
plates with mineral-ring staining ground into them; a wide rasping under-slung mouth
barely visible below the shell rim; short digging limbs. Wet-lacquered dark plates,
purple-red crust film in the plate margins, pale mineral-ring stripes as the accent
— it wears the biome's paint because it eats the biome's paint. Small deep-set eye
band, nothing prominent.

**Facings:** south, east, north (north = plate dome and rear rim only). Canvas 256.
**drawSize intent: ~1.6**, bodySize ~1.0 class; slow, herd-adjacent, high wildness
but tamable at a price (a grazer that feeds on stone is a fence-proof pasture
animal — FOUNDRY prices it).

### RM_Eskith — the feather-footed ground-drummer

**Ruled frame (fixed):** the voice's fauna half. Talks by striking the ground —
heard as knocks through the substrate, through the engine's noise, not through air.
Goes silent ahead of a vent bloom: a living gas alarm, coupled to the falter tell
(`CAULDRON_MECHANICS_BUILD_1` §1).

**Description:**

> Knee-high, quick-footed, feet feathered out into wide soft pads that read the
> ground the way ears read air. Eskith talk in knocks — a drummed code sent through
> the rock, felt in your boot soles under the engine's rumble. The forest is never
> quiet, so nobody listens for sound here; they listen for the drumming. When the
> eskith stop answering each other, the old hands are already walking for the roof.

**Silhouette/palette brief:** a small upright ground-bird-adjacent body (no
Earth-nameable bird) on two strong drumming legs, the feet the signature — wide,
feather-fringed splayed pads, oversized for the body; a banked row of small eyes
(the biome's "many eyes" lane) across a blunt head; drab wet-forest darks with
crust-film iridescence at the feather-fringe, pale condensate beading on the
leg-feathering. The read is alert, harmless, tuned to the floor.

**Facings:** south, east, north (north = rear: back, folded fringe, drumming
haunches; the eye-bank invisible). Canvas 256. **drawSize intent: ~0.9**, bodySize
~0.35 class; common enough that the drumming is the biome's texture (0.4-class),
prey band, no manhunter.

### RM_Xithess — the filter-frond flora

**Ruled frame (fixed):** the sheet's missing signature silhouette, admitted as
pitched: a crown of fine chemical fronds held out like filters, **stirring
constantly**; harvest yields vent-chemistry stock, not wood.

**Description:**

> A pale trunk the height of a person, crowned with a fan of fine fronds that never
> stop moving — not in wind, in CHEMISTRY, combing the fog for what the vents
> exhale. Watch a xithess for a minute and you understand the whole forest: nothing
> here drinks water. It filters. Harvesters take the frond-crowns whole and sell
> them as they are — a xithess crown is a fistful of the forest's own refinery.

**Silhouette/palette brief:** single pale smooth trunk (bone-white going grey-green,
mineral-ringed at the base), no branches, all crown: a radial fan of many fine
graduated filter-fronds, caught mid-stir — visibly asymmetric, some fronds furled
and some spread, so the stillness of a sprite still reads as motion. Frond tips
carry the chemistry's green-amber bead-tips (the pooled-accent rule); condensate
strings between fronds. Transparent-edged fronds against the fog, never an opaque
mop.

**Facings:** single (plant; Graphic_Random variants derive from the master).
Canvas 256. **drawSize/visualSize intent: ~1.0–1.3 cells**; mid-tier field-former,
wild-clustered near vent ground.

## 4. Cast entries — material, industry and kit

### RM_Vexxith — the shear material (item + stuff)

**Ruled frame (fixed, owner-typed):** shearing a living vexxiss yields a **rare
material immune to powerful acids and temperature** — not metal. Only obtainable by
the shear; a corpse's plates crumble. Name sweep paid this pass (§1): `RM_Vexxith`
stands.

**Description:**

> A sheared vexxith plate, still holding the curve of the animal's flank. Acid beads
> off it. Fire cannot warm it. The forge-hands say working it is like arguing with
> something that has already decided — and everything made from it outlives the
> argument, the forge, and the smith.

**Silhouette/palette brief (item icon; the STUFF colour derives from it):** three or
four sheared plates stacked, curved like roof slates — layered slag-lamination
visible on the cut edge (the growth rings of a walking hill), surface a deep
matte iron-black with the purple-red crust sheen, cut edge pale and crystalline;
one plate showing acid-bead runoff standing on the surface, wetting nothing. Reads
as armor waiting to be asked.

**Facings:** single. Canvas 256. Item + StuffProps ride the def ticket
(`CAULDRON_RULED_CONTENT_1` §2); stuffable art tinting derives from this master.

### RM_GasTapScaffold — the gas-tap scaffold (building)

**Ruled frame (fixed):** the gas is highly flammable, burns with toxic smoke, and
**should be stopped**; capping a vent stops the leak AND banks flow for refining —
safety and industry as one act (`CAULDRON_MECHANICS_BUILD_1` §3). The vexxiss pries
at these to drink.

**Description:**

> A scavenger's answer to a hole in the world that breathes fire: a clamped scaffold
> of salvage steel stood over a wellhead, cap screwed down against the pressure,
> take-off line coiled to a banked tank. Every joint is doubled, because the ground
> pushes back. Every scaffold in the forest has pry-marks on it, because something
> out there prefers to drink from the tap.

**Silhouette/palette brief:** a squat 4-legged clamped frame over a capped vent
throat — Jawa salvage build language: mismatched steel, doubled clamps, a small
banked accumulator tank low on one leg, gauge with a cracked face. Corrosion patina
everywhere the fog touches; fresh bright metal only at the pry-marks. No flame, no
glow — a capped vent is a QUIET fixture; the danger reads as pressure, not fire.

**Facings:** single (building; def may rotate with Graphic_Single). Canvas 256.
**drawSize intent: ~1.5–2 cells** footprint.

### RM_FilterWorks — the filter-works (building) + RM_FilterCartridge (item)

**Ruled frame (fixed):** the discoverable tech is **conversion of one fluid to
another via filtering** (LiquidDef/FlowWorks lane): filter building + consumable
cartridges; launch recipes tapped-gas condensate → liquid reagents, toxic water →
potable water. Taught by studying the corroded ruin kit
(`CAULDRON_MECHANICS_BUILD_1` §4).

**Building description:**

> The forest's one lesson, learned from the ruins of the people who learned it
> first: everything here is something else wearing a solvent. The filter-works pulls
> them apart — one fluid in, a cartridge in the throat, a different fluid out. The
> Farmers call it doing by hand what the river god does by grace, and they say it
> quietly, because Oomo is known to grimace at this country.

**Building silhouette/palette:** a waist-high pressure vessel on a frame — intake
and outlet pipe stubs at opposite ends, a top-loading cartridge breech with one
cartridge seated half-visible, drip-tray beneath the outlet. Etched-metal patina,
mineral rings where drips dried, the green-amber accent ONLY as one bead at the
outlet. Facings: single. Canvas 256. Footprint ~2 cells.

**Cartridge (item) description:**

> A filter cartridge, packed the old way: crushed crust-mineral, frond-felt from the
> xithess crowns, a wax seal at each end. Spent ones turn the colour of what they
> caught. The ruins are full of spent ones.

**Cartridge silhouette/palette:** a hand-sized ribbed cylinder, wax-capped both
ends, pale frond-felt visible at a broken rib; one end stained the chemistry's
green-amber (a partly-spent read — provenance in one glance). Facings: single.
Canvas 256. *(Spent-cartridge ruin litter can ship as a retint of this master —
dressing, not a second commission.)*

### RM_Seismograph — the seismograph (building)

**Ruled frame (fixed):** research-gated; translates the falter tell into a real
alert for players who play muted — the engine's silence made into a letter
(`CAULDRON_MECHANICS_BUILD_1` §1).

**Description:**

> A drum, a stylus, a weighted needle sunk into bedrock — the Farmers' machine for
> listening to the machine. All day it writes the ground's talk in a fidgeting line:
> rush, groan, gurgle, roar. The one thing it is built for is the moment the line
> goes flat. A flat line here is not peace. It is the engine drawing breath.

**Silhouette/palette brief:** a knee-high instrument on a bedrock-bolted tripod — a
rotating paper drum with a scrawled trace line, a brass-dark stylus arm, a heavy
plumb mass below the frame. Scavenger-precise: this is the biome's one delicate
machine, kept oiled where everything else corrodes. The drum's white paper is the
lightest value in the whole cast — it should read across a dark room. Facings:
single. Canvas 256. Footprint 1 cell.

### RM_CauldronVent — the vent (ThingDef)

**Ruled frame (fixed):** vents are map-spawned ThingDefs that leak visible flammable
gas; ignition burns with toxic smoke; a gas-tap scaffold caps one; the vexxiss
inhales one and its production pauses for days (`CAULDRON_MECHANICS_BUILD_1` §3/§5).

**Description:**

> A throat in the ground, rimmed in mineral rings laid down one exhale at a time.
> This is where the engine's noise comes up loudest — the rush and the gurgle right
> under your feet — and where its breath comes up rawest. Unlit, it wavers the air
> and beads every surface downwind. Lit, it is a torch with poison for smoke. The
> Farmers cap them. The forest keeps making more.

**Silhouette/palette brief:** a natural surface feature (1×1 or 2×2 read): a dark
fissured throat in bare rock, concentric mineral-ring terracing (bone-white to
green-amber inner stain), condensate beading heavy on the downwind rim, faint
heat-shimmer distortion suggested at the mouth. ⛔ NO visible flame in the base
sprite — ignition is a state the mechanics own; the sprite is the UNLIT vent.
Facings: single. Canvas 256. **drawSize intent: ~1.5** over a 1-cell def.

### The corroded ruin kit — RM_CorrodedWellhead · RM_CorrodedCondenserStack · RM_CorrodedShrine

**Ruled frame (fixed):** the study-interactable ruin kit teaches the filter-works
(§4 of the mechanics ticket carries the set pieces); the shrine is Oomo's Grimace
made content — the owner ruled Oomo *"will dislike it but not refuse to go"*
(grudging shrine kit, sour flavor tint, no precept defs).

**RM_CorrodedWellhead:**

> A capped wellhead from before the collapse, the cap welded down by people who were
> not coming back for it. The mineral rings have climbed it like tree-bark. Study
> the welds and you learn the first thing the old crews knew: the ground's breath
> can be held.

Silhouette: a low industrial stub — flanged pipe collar, welded dome cap, chain-dog
clamps — half-swallowed by mineral-ring terracing; acid-etch patina, one seam
weeping the green-amber stain. Single facing, 256, ~1 cell.

**RM_CorrodedCondenserStack:**

> A condenser stack, tall as two people, its fins eaten to lace. It made water out
> of fog for somebody once — the one thing this country will not give away free.
> Study the fin spacing and the cartridge racks rotted into its base, and the
> filter-works stops being a mystery.

Silhouette: a slender vertical finned column on a square base, fins corroded
lace-thin at the top, an empty cartridge rack and two spent cartridges fused to the
base; streaked verdigris-and-rust patina, condensate still beading on the surviving
fins (it half-works, which is the poignant read). Single facing, 256, tall sprite —
**drawSize intent ~1×2.5** over a 1-cell def.

**RM_CorrodedShrine:**

> A river-god's shrine in a country with no river. The Farmers still build them here
> — smaller than they build them anywhere else, and facing away from the vents, the
> way you set a chair for a guest you know will not stay. The offering bowl is a
> filter cartridge. Nobody calls that disrespect. Oomo comes anyway, and grimaces,
> and keeps the water honest a little way around it.

Silhouette: a knee-high cairn-and-bowl shrine in the campaign's Oomo language (wave
motif carved shallow), the bowl holding a clean cartridge; the ONLY unstained clean
water bead in the whole cast sits in that bowl — the single point of grace. Stone
greys, shallow-carved motif, minimal green-amber anywhere near it. Single facing,
256, 1 cell.

## 5. Wired-by-FOUNDRY — validated art that exists; NOT re-queued (⛔ standing law)

From the review's art table, re-verified against `done/` this pass (all present):

| subject | art in `done/` | disposition |
|---|---|---|
| `AB_CrystalFlower` → owned divergence | `crystalflower_v1` | wire per `CAULDRON_RULED_CONTENT_1` §3 |
| `AB_BloodBouquet` | `bloodbouquet_v1` | wire |
| `AB_RavenNettle` | `ravennettle_v1` | wire |
| `AB_RedBugloss` | `redbugloss_v1` | wire |
| `AB_KeeningCordax` | `keeningcordax_v1` | wire |
| `AB_GiantAgariTox` | `giantagaritox_v1` | wire |
| `AB_GiantToxicFlower` | `gianttoxicflower_v1` | wire |
| `RM_Suush` | `cauldron_suush_south/east/north` | DONE + deployed; nothing owed |
| `RM_TwistingThornwood` | `twistingthornwood_v1` (+ shipped `_a`/`_b`) | nothing owed (description fix rides the def ticket) |
| `RM_TreeMartyr` | `martyr_v1` (+ shipped `_a`/`_b`) | nothing owed |
| `RM_DarkCrust` | `rutdarkcrust_v1` | nothing owed |
| `RSW_VentStalker` | rides `kinrath_v1`/`canon_kinrath_v1` retint | deliberate; nothing owed |
| the 7 wired-and-keep imports (Lylek, Plasmorph, LuciferBug, Radyak, RipperHound, Skalder, Silooth) | donor mods' own art | wiring is def work, no art owed |

## 6. Queued art — 13 subjects, 19 job files

**CSV:** `infrastructure/artpipe/art_lists/cauldron_bedazzle_cast.csv` —
`rimflow_item_id CAULDRON_BEDAZZLE_SITTING_1`, channel codex, transparent,
priority 70. Queued via `fill_queue.py`; per-facing jobs land in
`infrastructure/artpipe/pending/` with east as the derive-facings master
(ARTPIPE_FACING_COHERENCE_1 default).

| id | canvas | facings | kind |
|---|---|---|---|
| `RM_Vexxiss` | **512** | south,east,north | creature (colossus precedent: scale carries in pixels) |
| `RM_Zisska` | 256 | south,east,north | creature |
| `RM_Eskith` | 256 | south,east,north | creature |
| `RM_Xithess` | 256 | single | flora |
| `RM_Vexxith` | 256 | single | item/stuff master |
| `RM_GasTapScaffold` | 256 | single | building |
| `RM_FilterWorks` | 256 | single | building |
| `RM_FilterCartridge` | 256 | single | item |
| `RM_Seismograph` | 256 | single | building |
| `RM_CauldronVent` | 256 | single | map feature |
| `RM_CorrodedWellhead` | 256 | single | ruin kit |
| `RM_CorrodedCondenserStack` | 256 | single | ruin kit (tall) |
| `RM_CorrodedShrine` | 256 | single | ruin kit |

## 7. Handoff notes (defects/finds observed — nothing filed, per this brief)

- **`RM_CompResourceCondenser` / `RM_CompGatherableGas` already exist**
  (`src/RimMandrake/EnvironmentalHazards/Source/`, consumed by
  `RUT_SteamCatch.xml` in TerminalBiomes) — a comp family for a building that must
  sit on a vent/geyser ThingDef and bank a resource. `CAULDRON_MECHANICS_BUILD_1`
  §3's gas-tap scaffold looks like this exact shape; FOUNDRY should read those two
  files before writing new C# ("search src before designing" — this project keeps
  having already built it).
- The Scald sea owns `scald2_ventbuilding_a/_b` art — superficially similar subject,
  different biome register; nobody should "save a job" by reusing it here.
- Spent-cartridge ruin litter (mechanics §4's set dressing) can ship as a retint of
  the `RM_FilterCartridge` master — dressing, not a second art commission.
- Building sprites are commissioned single-facing per sitting precedent (Swale). If
  FOUNDRY defs any of them Graphic_Multi, file the extra facings as follow-on jobs
  rather than blocking the build.
- The review's roster-gap note stands: the 7 imports wire on the Utinni/donor layer
  per Q11/Q11a and two frozen-sheet ban lines need amending under ruling 7 — that is
  `CAULDRON_RULED_CONTENT_1` §1's work, restated here only so nobody reads this
  bible's silence as the sheet standing unamended.
