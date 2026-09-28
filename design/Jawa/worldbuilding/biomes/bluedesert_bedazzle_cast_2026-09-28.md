<!-- status: cast bible — commissioned under BLUEDESERT_BEDAZZLE_SITTING_1 movement 4 -->
# Blue Desert bedazzle cast — the four new natives + art commission

**Item:** `BLUEDESERT_BEDAZZLE_SITTING_1` (movement 4: commission) · **Date:** 2026-09-28
**Feeds:** `BLUEDESERT_RULED_CONTENT_1` (defs) + `BLUEDESERT_MECHANICS_BUILD_1` (mechanics)
**Authorities:** the 2026-09-28 amendment block in `the_blue_desert.md` (ruled names and
facts) · `bluedesert_bedazzle_review_2026-09-28.md` §3/§4/§5 (developed pitches + turn-2
rulings) · `creatures/blue_desert_hydrocarbon_life.md` (the built cast's register, stats
laws, the charge family §2).

## 0. Shared law — every card below obeys this without restating it

- **Admission test** (sheet §4): hydrocarbon-metabolic, cold-stable, warm-reactive. Every
  card carries the charge family; a warm-safe native is a ban-3 violation.
- **The charge family, as built** (life brief §2; `Defs/HediffDefs/RM_BlueDesertCharges.xml`
  read this pass): one hediff **per species** — `RM_DorrakCharge`/`RM_KrissekCharge`/
  `RM_VekkitCharge` exist, so the new fauna get `RM_VhaulkCharge`, `RM_MurrekCharge`,
  `RM_OssivelCharge`, given by `PawnKindDef.startingHediffs`, each a
  `HediffCompProperties_ExplodeOnDeath` at the card's radius, **Flame 40** (the chain
  number, §2d), `destroyBody false` (corpses butcher to cold wax). Flora ride
  `RM_CompPlantCharge` (KillFinalize-only — cutting and swallowing are safe).
- **Shared fauna stats** (life brief conventions): `ComfyTemperatureMin/Max` **−100 / −11**
  (heatstroke above −1 °C IS the warm-reactivity, §1f), `ArmorRating_Heat 0` (a native in
  a neighbour's blast is a casualty), `Flammability 0.1` (flora 0.05), `MeatAmount 0`,
  `LeatherAmount 0`, `butcherProducts → RM_ColdWax`. Laws: 60 kg per bodySize, drawSize =
  body length in metres, health ∝ mass, melee best hit ≈ 12–15 × bodySize (Law 3).
- **Tameability is relaxed** (turn-2 ruling 4): the blanket `Wildness 1.0 / trainability
  None` stance is dead; each card sets its own. `BLUEDESERT_RULED_CONTENT_1` §6 carries
  the pass over the existing three.
- **Names are final** (ruled, styled for variance — one/one/two/three syllables): no
  restyling in defs; `vh-` stays the apex marker and only the vhaulk carries it.
- **Numbers are design choices**, calibrated against the built cast's anchors (dorrak
  bs 1.6 / krissek 0.9 / vekkit 0.45); FOUNDRY tunes in playtest, the *relationships*
  (who outruns whom, whose blast is biggest) are the ruled part.

## 1. RM_Vhaulk — the colossus

**Hook.** The biome's slow mountain: a house-sized sealed Swallower-lineage giant on six
pillar legs, a rolling cistern of pentane sludge that grazes whole floss fields in a
pass. It is neutral and it ignores you; every decision it creates is the mechanic. Kill
it near your base and you have detonated a district; lure it toward a siege camp and it
is a weapon; tap it alive and it is the mad-brave harvest. The quarry warnings include
*do not still the mountain* — and they mean the EMP trap.

**Class/role.** GIANT (mark 5). Apex herbivore, no predator, no threat until made one.
The read from a distance is terrain; the read up close is a mistake.

**Description (salvager register):**

> From the ridge it reads as a hill that was not there last season. Six legs like quarry
> pillars, a back like a buried tank, and it eats a floss field the way weather eats a
> footprint — whole, slowly, without noticing you. The crews call it the mountain and
> steer wide. The old warnings say do not still the mountain, and the crews who thought
> that was poetry are the reason the crews steer wide.

**Stats sketch.**

| field | proposed | grounding |
|---|---|---|
| `baseBodySize` | **6.0** (≈ 360 kg frame + cistern mass in lore) | above Thrumbo (4.0); the biggest thing on the nightside |
| `drawSize` (adult) | **7.0** | 7 m long; canvas **512** (Middenshell/Meltgut colossus precedent — scale must carry in the pixels) |
| `baseHealthScale` | **6.0** | ∝ mass, no discount — killing one is a campaign, which is the point |
| `ArmorRating_Sharp / Blunt / Heat` | 0.7 / 0.5 / **0** | a step past the dorrak's boiler plate; Heat 0 per shared law |
| `MoveSpeed` | **1.2** | below the dorrak (1.8); it never chases and never flees |
| `foodType` / `baseHungerRate` | `VegetarianRoughAnimal` / 2.5 | grazes flora fields whole — Vanish ingestion, so its own grazing never chains (§1g of the life brief) |
| `Wildness` / `trainability` | 0.98 / `None` | tameability relaxed elsewhere, not here: you do not tame a district-bomb, you learn to live near one |
| `manhunterOnDamageChance` | **1.0** | neutral until wounded; then the mountain notices you, slowly |
| `wildGroupSize` | 1 | there is never a second one on the map |
| commonality | **0.02** | the ruled 0.02-class rare — most maps never see one |
| `combatPower` | 450 | Thrumbo-class raid-point weight |
| `lifeExpectancy` | 200 | older than the quarry epochs' later attempts |
| `lifeStageAges` | Baby 0 / Juvenile 8 / Adult 25 | three stages; blast radius is life-stage-independent (§1d) |
| melee | slam Blunt 30, cooldown 4.0 | deliberately **below** Law 3's curve (bs 6 → 72–90): it is not a fighter, and the danger must never be its teeth |
| `butcherProducts` | `RM_ColdWax` × 80 | the cistern; a kinetic kill's prize |

**Marked by / visual identity.** Six pillar legs; a sealed, seamed back with no visible
head worth the name — intake at the front like a dorrak's lid scaled to a garage door;
frost rime standing on the flanks because the cistern is colder than the animal. Grey on
grey with glacial blue-white only where light passes a translucent sludge-window along
the lower flank — the one hint of what it is full of.

**Danger frame.** The largest detonation on the planet's surface (~radius 15 Flame),
**trigger-gated** (ruled, sheet amendment (2)): it explodes ONLY when it dies of
heat-family damage (Flame/Burn — lightning's strike damage is Flame, so lightning comes
free). A kinetic or cold kill leaves the cistern intact: the richest harvest, earned the
hard way. **And the ion trap: any EMP hit against a LIVING vhaulk detonates it
immediately** — checked on hit, not on death. Stunning it is one of the worst things you
can do. The description carries that obliquely (*do not still the mountain*), never as a
tooltip spoiler.

**Def wiring notes** (build: `BLUEDESERT_RULED_CONTENT_1` §2; gating mechanics:
`BLUEDESERT_MECHANICS_BUILD_1` §1).

- `RM_VhaulkCharge` (HediffDef, per-species pattern): `ExplodeOnDeath` radius ~15,
  Flame 40, `destroyBody false` — **plus the two gates**, which need a custom
  HediffComp pair in `BlueDesertLife.cs`: (a) death-cause filter — detonate only when
  the killing `DamageInfo.Def` is heat-family; (b) EMP-on-hit —
  `Notify_PawnPostApplyDamage` fires the kill+detonation on any EMP damage while alive.
  New `.cs` content in the existing assembly: check the csproj — a file without its
  `<Compile Include>` line compiles into nothing, silently.
- **Valve tap body part**: the dorrak Hump pattern scaled up — a `Valve` part
  (coverage ~0.06, height Top) on a bespoke BodyDef (six legs rules out reusing
  `QuadrupedAnimalWithHoovesAndHump` cleanly; the dorrak's cosmetic-label compromise
  does not stretch to a colossus). The tap-alive harvest is a work-giver operation at
  that part → cold-wax windfall at manhunter risk (mechanics item §1).
- Balance care: a 15-radius Flame blast inside flora chains can glass a quarter map —
  that is the point, but verify the cascade cost near map edges (mechanics item §1).

## 2. RM_Murrek — the drift ambusher

**Hook.** A flat, wide predator that buries itself under ice-sand drifts and erupts
under prey — the ruled drift weather made into a predator's tool. After every drift
storm the landscape is re-armed: yesterday's safe path is today's ambush field, and a
drift leaning against your wall might be a drift.

**Class/role.** Mid predator (marks 4+8 coupling); the krissek's clade cousin, slower
and meaner. In the open it is unimpressive; the drift IS the animal.

**Description (salvager register):**

> Flat as a dropped tarp and about as easy to see, once the sand has settled over it.
> It does not chase and it does not need to: it lies where the wind builds the drifts,
> and the drifts are everywhere the wind was. The crews walk the swept ice after a
> storm and probe the leaning sand with poles, and the poles are not long enough.

**Stats sketch.**

| field | proposed | grounding |
|---|---|---|
| `baseBodySize` | **1.2** (≈ 72 kg) | between krissek (0.9) and dorrak (1.6) |
| `drawSize` | **1.9** | wide and flat — length carries the flatness read; canvas 256 |
| `baseHealthScale` | 1.2 | ∝ mass |
| `MoveSpeed` | **3.5** | slow for a predator in the open — its speed is the ambush |
| `foodType` / `predator` / `maxPreyBodySize` | `CarnivoreAnimal` / true / **1.0** | takes utikka, vekkit, ossivel — never a dorrak |
| `manhunterOnDamageChance` | 0.8 | meaner than its cousin's grace |
| `Wildness` / `trainability` | 0.97 / `None` | relaxed law noted; a buried pet is not a pet |
| `wildGroupSize` | 1 | ambushers do not share drifts |
| commonality | **0.25** | rarer than the krissek (0.35) |
| `combatPower` | 110 | one hard hit and position, not a sustained fighter |
| `lifeExpectancy` | 12 | |
| `lifeStageAges` | Baby 0 / Juvenile 0.3 / Adult 0.6 | |
| melee | strike Stab **17**, cooldown 2.8; jaws Bite 10, cooldown 2.0 | Law 3 (bs 1.2 → 14–18); the eruption's first hit is the fight |
| `butcherProducts` | `RM_ColdWax` × 8 | |

**Marked by / visual identity.** A low wide wedge — all margin, like a ray that learned
to walk: fringed skirt-edges that vibrate sand over its own back, dorsal hide textured
as wind-rippled drift sand, paired hooked forelimbs folded under the leading edge.
Grey-white over grey, the drift-camouflage colourway; the underside (never shown in
sprites) is the dark side.

**Danger frame.** `RM_MurrekCharge` at **radius 2.9**, Flame 40 — krissek-class blast,
ungated (any death detonates, heatstroke included). The ambush is the mechanic; the
charge means flushing one with fire re-arms the field a different way.

**Def wiring notes** (defs: `BLUEDESERT_RULED_CONTENT_1` §2; burrow AI:
`BLUEDESERT_MECHANICS_BUILD_1` §6 — build order: weathers first).

- The def ships walk-and-hunt viable WITHOUT the burrow AI — a slow flat predator —
  so the content item does not wait on the mechanics item.
- Burrow hookup (mechanics §6): buried/unburied states via a burrow/unburrow job
  driver (the biome's first genuinely new one) + a MapComponent listening for the
  drift weather's end that re-seeds buried murrek at fresh drift cells. Dig the
  drift, flush the thing. Buried state wants a near-invisible drift graphic swap,
  not a new sprite sheet — the drift itself is the art.
- New `.cs` needs its `<Compile Include>` line (same trap as §1).

## 3. RM_Ossivel — the choir

**Hook.** The biome's voice (mark 7 in fauna form). A knee-high vent-throated thing
whose gas-exchange spiracles sound organ tones; packs sing at the ablation line at
"dusk" (activity-cycle, not sky — there is no dusk on the nightside). Harmless,
beautiful — and a working alarm: **they go silent when something big moves.** A colony
that learns the choir learns to hear the silence.

**Class/role.** Small herd herbivore-adjacent (spiracle-feeder on airborne
hydrocarbons + palefloss); prey for krissek and murrek; the alarm the player earns by
paying attention.

**Description (salvager register):**

> Knee-high, round-bodied, throat like a rank of organ pipes. At the line they stand
> in dozens and sing — long cold chords you can hear through a sealed helmet, the only
> proof for a hundred kilometres that anything is glad to be here. The crews like
> them. The crews also count on them: when the singing stops all at once, you have
> until the echo dies to be somewhere else.

**Stats sketch.**

| field | proposed | grounding |
|---|---|---|
| `baseBodySize` | **0.35** (≈ 21 kg) | below the vekkit; krissek/murrek prey |
| `drawSize` | **0.9** | canvas 256 (the floor) |
| `baseHealthScale` | 0.35 | ∝ mass |
| `MoveSpeed` | 4.0 | quick enough that the choir scatters |
| `foodType` | `VegetarianRoughAnimal` | crops palefloss beside the utikka |
| `manhunterOnDamageChance` | 0 | it has never fought anything |
| `herdAnimal` / `wildGroupSize` | true / **5~12** | the choir is the point |
| `Wildness` / `trainability` | **0.55** / `None` | the relaxed-tameability ruling lands here: a tamed choir is a living perimeter alarm — deliberate, and priced by taming work, not forbidden |
| commonality | **0.5** | common; the soundscape needs them |
| `combatPower` | 25 | |
| `lifeExpectancy` | 9 | |
| `lifeStageAges` | Baby 0 / Juvenile 0.2 / Adult 0.4 | |
| melee | nip Bite 4, cooldown 1.8 | not a fighter |
| `butcherProducts` | `RM_ColdWax` × 2 | and butchering the choir is a choice the colony hears |

**Marked by / visual identity.** A rounded, upright-postured little body whose throat
and chest are a fan of graded vent-pipes — spiracle tubes of visibly different lengths,
frost-rimmed at the openings; small folded limbs, no true face beyond a sensory band
above the pipes. Glacial blue-white grading to grey; the pipes' interiors the darkest
value on the body.

**Danger frame.** `RM_OssivelCharge` at **radius 1.1** (vekkit-class pop), Flame 40 —
the one you can survive standing next to, but a startled choir dying together in a
floss field is its own cautionary tale.

**Def wiring notes** (defs: `BLUEDESERT_RULED_CONTENT_1` §2; choir/silence:
`BLUEDESERT_MECHANICS_BUILD_1` §5).

- The def ships silent-capable: no hard dependency on the sound work. Choir hookup
  (mechanics §5): a sustainer ambient keyed to pack presence at the ablation line /
  activity cycle, using vanilla SFX reuse/retint first (audio is a new pipeline ask —
  scope small).
- **Silence-alarm**: the choir's sustainer stops when a pawn above a bodySize
  threshold (design: ≥ 1.0 — murrek, dorrak, vhaulk, and yes, a colonist in armour
  does not qualify; predators and the mountain do) moves within hearing range —
  MapComponent or comp proximity check on the pack's sustainer, per mechanics §5's
  "choir stops when a big pawn nears", verified by state read.
- Tameability: `Wildness 0.55` is this bible's proposal under ruling 4; the tamed
  choir-as-alarm reading follows the approved tamed-dovvik precedent (a utility pet
  whose utility is its biology).

## 4. RM_Virr — the whistle-reed (flora)

**Hook.** The soundscape's floor (mark 7). A fractal tube whose branches sound in wind
— fields of virr ARE the biome's music between storms. **The pitch rises as the plant's
charge ripens**, so a keen-eared colonist hears which field is about to be dangerous to
warm. The only plant on Ash'karr that tells you its own state.

**Class/role.** Fourth native flora card, joining the life brief §6b table (palefloss /
glassfern / chimeglobe). Mid-tier, field-forming.

**Card (extends the §6b table; shares every §6a field — `completelyIgnoreFertility`,
the −90…−1 °C band, glow-0 growth, no `sowTags` (ban 2), `Flammability 0.05`, the
ButaneGut outcome doer, `harvestedThingDef RM_ColdWax`):**

| field | `RM_Virr` · whistle-reed · mid |
|---|---|
| the read | a hollow fractal tube, hand-high, branching into graded open-ended pipes — an organ the wind plays |
| `MaxHitPoints` | **35** (≤ the chain number 40) |
| `Nutrition` | 0.25 |
| `growDays` | 10 |
| `harvestYield` (cold wax) | 3 |
| `harvestWork` | 130 |
| `visualSizeRange` | **0.65~1.0** — the smallness law: nothing above 1.1 cells |
| `maxMeshCount` | 1 |
| `wildClusterRadius` / weight | 4 / 4 — fields, because fields are the instrument |
| `wildOrder` | 2 |
| `charge.radius` (`RM_CompPlantCharge`) | **1.9** (glassfern-class) |
| `graphicClass` | Graphic_Random, 3 variants |
| `selectable` | true |
| `BeautyOutdoors` | 4 |

**Marked by / visual identity.** Transparent like all the native flora — but where the
glassfern is edge and the chimeglobe is lattice, the virr is *bore*: open pipe-ends of
visibly different diameters, thin translucent walls with refraction highlights, the ice
readable through the body. A card that reads as an opaque reed on ice fails (life brief
§8's rule).

**The rising-pitch note (wiring, mechanics §5).** Two inputs map to one audible
parameter: (a) ambient — a wind-keyed sustainer on virr fields (WeatherDef wind →
sustainer volume), the between-storms music; (b) **the ripeness pitch** — the
sustainer's pitch parameter driven by the field's charge state: growth fraction as the
slow season-scale rise, and `RM_CompPlantCharge`'s existing two-longtick warm countdown
as the sharp final climb — the same countdown the pre-detonation crack cue (mechanics
§5) already listens to, so the virr's scream and the crack cue are one system heard
two ways. Zero new mechanism class: the comp already holds the state; the sound layer
reads it.

## 5. RM_BlueIce — visual note (mineable + item icon)

The ⭐ golden mineable (`BLUEDESERT_RULED_CONTENT_1` §3: RockBase-family mineable +
stockpilable item; thaw-roll comp is the mechanics item's §3). Visual identity, both
forms:

- **The one true blue up close.** The sheet's law is "nothing here is blue up close" —
  scattering only. Blue ice is the earned exception, and it is real physics: ancient
  compressed ice IS blue in the body, the long optical path through dense bubble-free
  ice. The player who mines it holds the only locally-blue thing in the biome — which
  is exactly why it reads as treasure ("golden," owner).
- **Mineable (in-wall)**: deep glacial blue-into-teal translucent mass, glassy
  conchoidal fracture faces, fine white crack-veils deep in the body, frost bloom at
  cut edges. Follows the RockBase atlas convention (the greatbole-heartwood precedent:
  a natural-rock blob with its own colour identity); FOUNDRY derives the atlas tile
  from the item art's material language if no separate wall texture is commissioned.
- **Item icon (this commission)**: a cut block — clean quarried facets, deep
  saturated glacial blue with internal light, white crack-veils, distilled-water
  clarity at the thinnest corner. Reads as gem-grade water: valuable, cold, pure.

## 6. Roster wiring summary

Shorthand element form ONLY (`<DefName>commonality</DefName>` — a `<li>` in
`wildAnimals`/`wildPlants` silently discards the def). Target state of
`RM_BlueDesert.xml` after `BLUEDESERT_RULED_CONTENT_1` lands (existing three + the
2026-09-24 depth cast + the bedazzle four; depth-cast commonalities are that item's
to settle, shown here as this bible's proposal for one source):

```xml
<wildAnimals>
  <RM_Vekkit>0.8</RM_Vekkit>
  <RM_Utikka>0.7</RM_Utikka>
  <RM_Dorrak>0.5</RM_Dorrak>
  <RM_Ossivel>0.5</RM_Ossivel>
  <RM_Krissek>0.35</RM_Krissek>
  <RM_Vrisk>0.3</RM_Vrisk>
  <RM_Murrek>0.25</RM_Murrek>
  <RM_Dovvik>0.2</RM_Dovvik>
  <RM_Zhaaz>0.1</RM_Zhaaz>
  <RM_Vhaulk>0.02</RM_Vhaulk>
</wildAnimals>
<wildPlants>
  <RM_Palefloss>1.0</RM_Palefloss>
  <RM_Glassfern>0.5</RM_Glassfern>
  <RM_Virr>0.4</RM_Virr>
  <RM_Chimeglobe>0.25</RM_Chimeglobe>
</wildPlants>
```

- `animalDensity 0.5` / `plantDensity 0.33` stay explicitly set (sparse by doctrine;
  never zeroed).
- The three donor water-plants (`AB_ToxiGrass`, `AB_CrystalHorn`,
  `PoisonPlantTallGrass`) come OFF in the same change (turn-2 ruling 1; CrystalHorn
  keeps its Propane Lakes home).
- The campaign-tier Star Wars rows (`Vapaad`, `AA_Thunderbeast`) ride the Utinni
  patch, not this mod.

## 7. Art commission

**Pre-queue check (standing owner rule), run 2026-09-28.** Instrument: filename search
over `infrastructure/artpipe/done/` (3,778 files), `pending/` (14), `_artsrc/` (3,541
entries) + content search of `registry.jsonl`. Sanity probe: **krissek → 10 hits in
`done/` and 10 in `_artsrc/`** (the instrument sees). Findings: **vhaulk, murrek,
ossivel, virr, blueice/blue_ice — 0 hits everywhere.** Nothing to reuse; all five
subjects genuinely owed. (Side note: `registry.jsonl` returned 0 even for krissek —
it does not index this cast; the filename search over `done/`/`_artsrc/` is the
working instrument for Blue Desert subjects.) The 20 existing-cast jobs
(chimeglobe/glassfern/palefloss/dorrak/krissek/vekkit) are already queued/done and are
NOT re-queued.

**CSV:** `infrastructure/artpipe/art_lists/bluedesert_bedazzle_cast.csv` — 5 jobs,
`rimflow_item_id BLUEDESERT_BEDAZZLE_SITTING_1`, channel codex, transparent,
priority 70:

| id | canvas | facings | note |
|---|---|---|---|
| `RM_Vhaulk` | **512** | south,east,north | colossus precedent (Middenshell/Meltgut): scale must carry in the pixels; the read is "terrain feature that turns out to be an animal" |
| `RM_Murrek` | 256 | south,east,north | |
| `RM_Ossivel` | 256 | south,east,north | |
| `RM_Virr` | 256 | single | plant, Graphic_Random variants derive from the master |
| `RM_BlueIce` | 256 | single | item icon (cut block); mineable atlas derives from it |

**Style register (sheet §9 — "extremely blue from far away; colorless up close"):**
cold glacial blue-white and glass-grey palette, grey-on-grey bodies with blue-white
only in translucence, frost rime and rim light; starlit cold light; the saturated
blue-fire accent `#55c0f0` stays the krissek halo's — none of the new cast borrows it;
rust/char accents only where the fallen lie (not on these subjects). Realistic painted
natural-history illustration, grounded believable anatomy, matte natural surface
texture, never cartoonish, no outlines, no camera words. Recognizability rule: no
Earth-nameable silhouette. Every faced job's north line: **true rear view seen from
directly behind — no eyes, no face, no frontal features.** Flora/ice must show
transparency and refraction (an opaque card fails).

Queued via `python3 src/RimMandrake/Utils/artpipe/fill_queue.py --input
infrastructure/artpipe/art_lists/bluedesert_bedazzle_cast.csv` — counts recorded on
the ledger at queue time.
