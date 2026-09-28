# The Contagion — grotesque cast bible (full RM_ development)

_DESIGN, 2026-09-27, recorded on `CONTAGION_BEDAZZLE_SITTING_1`. Companion art
commission: `infrastructure/artpipe/art_lists/contagion_grotesque_cast.csv`._

## 0. The ruling this executes

Owner, 2026-09-27 (typed, on `CONTAGION_BEDAZZLE_SITTING_1`): the Contagion's whole
donor cast gets **full RM_-tier development — new defs, new names, new art, no
patches.** Naming register, verbatim: *"bizarre one or two-word descriptions of the
strangeness of the thing. Eyegore. Fleshsop. Bloody Mess."* — English grotesque
description, never invented-exotic words, never Star Wars names. The batch-3c exotic
drafts (ghaaz, zhool, bulloo, vezzok, …) are **superseded for this biome**; the
superseded table in `noncanon_beast_names_crags_nightside_contagion_slime.md`
carries the banner. Mandatory addition, verbatim: *"really gross fleshy flapping
skin things that fly."*

**Same-sitting owner name corrections (typed, ledger on the sitting item):**
1. Staticleech → **Sparkleech** (the grub follows: Sparkleech grub).
2. The eyeling keeps its already-ruled name **ikee** (owner, 2026-08-15) — Eyegore
   is dropped entirely, assigned to nothing.
3. Razorjack → **Doublemaw** stands: "razorjack" MEASURED non-canon (0 Wookieepedia
   search hits, sanity probe dianoga=10) — an Alpha Animals coinage, so the rename
   proceeds.
4. Blood bouquet → **Bloody Fist** (owner's own coinage; replaces keeping the donor
   label).

Everything rides the frozen sheet `the_contagion.md` — §4 gives every port its job,
§6 the hard bans, §9 the palette — and the ruled roster
`rosters/the_contagion.json` (commonalities cited below are its rulings). The
sheet amendment recording this sitting's new natives is **BENCH's to write**, not
this doc's; this doc is the design input to it.

**Collision sweep (MEASURED this pass):** every RM_ defName below returned 0 hits
across `src/` `*.xml`+`*.cs`; sanity probe `RM_Fessk` = 4 files. Near-miss noted:
a stray never-finished art job id `pyre_scorchpod_v1` exists in
`infrastructure/artpipe/registry.jsonl` (4 rows, nothing in `done/`, no def, no
design doc) — not a collision; cited so nobody rediscovers it.

**Existing art (searched before queuing, per the standing rule):** 14 of the 16
donor rows already have finished 3-facing art in `infrastructure/artpipe/done/` +
`_artsrc/` under the superseded exotic ids (`contagion_ghaaz_*`, `contagion_zhool_*`,
`contagion_blisteredbulloo_*`, `contagion_greaterbulloo_*`, `contagion_vezzok_*`,
`contagion_zhirrik_*`, `contagion_vulloth_*`, `contagion_fezzira_*` + larva,
`contagion_brossak_*`, `contagion_ghuvv_*`, `contagion_gollivra_*`,
`contagion_pellorax_*`, `contagion_pibbo_*`), plus `bloodbouquet_v1` and
`halfalientree_v1`. **All of it is in the retired "painterly vanilla + heavy black
outline" style** (read off the manifests) — the style the owner ruled reads
cartoonish — and the halfalientree render is the very "half oak" the sheet's Owed
list orders redone. The owner's "new art" ruling covers all of it; nothing is
reused, everything below is queued fresh. No eyeling/ikee art exists anywhere in
the pipe (MEASURED).

## 1. The name map

| donor def | job (sheet §4) | new name | RM_ defName |
|---|---|---|---|
| `AA_RedGoo` | the body | **Bloody Mess** | `RM_BloodyMess` |
| `AA_OcularJelly` | the eyes | **Gawpsack** | `RM_Gawpsack` |
| `AA_InfectedAerofleet` | the sower | **Blisterfloat** | `RM_Blisterfloat` |
| `AA_RedSpore` | the leaker | **Scorchpod** | `RM_Scorchpod` |
| `AA_BloodShrimp` | the drinker | **Bloodlurk** | `RM_Bloodlurk` |
| `AA_Helixien` | the undertaker | **Meltgut** | `RM_Meltgut` |
| `AA_Drainer` / `AA_DrainerLarva` | the thieves | **Sparkleech** / **Sparkleech grub** | `RM_Sparkleech` / `RM_SparkleechGrub` |
| `AA_RoughPlatedMonitor` | the basker | **Scaldhide** | `RM_Scaldhide` |
| `AA_Razorjack` | the pickers | **Doublemaw** | `RM_Doublemaw` |
| `AA_Swarmling` | the pickers | **Gnashling** | `RM_Gnashling` |
| `AA_Eyeling` | wretched-small | **ikee** (kept, owner 2026-08-15) | `RM_Ikee` |
| `AA_FungalHusk` | the walking dead | **the Shambles** | `RM_Shambles` |
| `AA_OcularNightling` | the watcher-kin | **Peeper** | `RM_Peeper` |
| `AG_OcularSlinger` | the tail | **Eyestinger** | `RM_Eyestinger` |
| `GR_Fleshling` | the pitiable | **Fleshsop** (owner's word) | `RM_Fleshsop` |
| *(authored, already built)* | the experiments | **the Unfinished** — stays as-is | `RM_TheUnfinished` (live: `src/RimMandrake/Contagion/Defs/ThingDefs/RM_TheUnfinished.xml`) |

| donor flora | new name | RM_ defName |
|---|---|---|
| `AB_AlienTree` | **Eyebark** | `RM_Eyebark` |
| `AB_AlienGrass` | **Lashgrass** | `RM_Lashgrass` |
| `AB_RedLeaves` | **Bleedleaf** | `RM_Bleedleaf` |
| `AB_RedPlantsTall` | **Gorestalk** | `RM_Gorestalk` |
| `AB_TentacularPlant` | **Rattlegrope** | `RM_Rattlegrope` |
| `AB_GlobularPlant` | **Sapblister** | `RM_Sapblister` |
| `AB_BloodBouquet` | **Bloody Fist** (owner's coinage) | `RM_BloodyFist` |
| `AB_HalfAlienTree` | **Halfmade Tree** (art redo folded in) | `RM_HalfmadeTree` |
| `AB_AlienTree_Polluted` | **blighted halfmade tree** (variant, plain modifier) | `RM_HalfmadeTreeBlighted` |

`RUT_RustPuff` (moved in from the Rot, 2026-09-20) is already ours and already
named; it stays a RUT_ campaign-layer row and is not part of this port.

New species are §3 and §5. Set pieces (the Coalescence, Cloud Repulsor, Sunbeam)
are §6.

## 2. Fauna — ports

Format: hook · cycle role · stats sketch · wiring. Commonalities are the ruled
roster's. All ports are UV-shy (dive at the Burn) except where the sheet's two
carve-outs already rule otherwise (Scorchpod walks the light and cooks; Scaldhide
is armored and hunts in it). Flight per the Flyer Law (CLAUDE.md): a flyer gets
real flight — `MaxFlightTime`/`FlightCooldown` statBases + the Locust-shape race
fields — and never waits on animation frames.

### Bloody Mess (`RM_BloodyMess`) — the body
A pool of somebody that never happened: raw red tissue creeping like spilled
viscera, budding half-organs that blink or clench once and are pulled back under.
- **Cycle:** the weapon's tissue itself. Eats everything dead, buds the Unfinished
  every Bloom (the live patch `RedGooSpawnsUnfinished.xml` already binds the donor;
  it retargets to this def), reabsorbs the failures. Dives — flattens into the
  ground and pools — at the Burn.
- **Stats:** bodySize 1.0 · commonality 0.75 · diet omnivorous scavenger
  (corpse-eater) · speed 1.6 · wildness 0.98, no trainability, melee blunt-acid.
- **Wiring:** `ThingDefs_Races/RM_ContagionFauna.xml` (new file, this mod);
  PawnKindDef beside it; `RedGooSpawnsUnfinished.xml` xpath moves off `AA_RedGoo`
  onto this def (the patch file then targets our own def and can fold into the def
  itself — no patches, per the ruling).

### Gawpsack (`RM_Gawpsack`) — the eyes
A drifting translucent bag stuffed with mismatched eyes, all of them open, all of
them looking up.
- **Cycle:** the Contagion's sensory organ, adrift at canopy height reading the
  cloud. **Sinks as one, seconds before a Burn** — the player's first tell.
- **Stats:** bodySize 0.7 · commonality 2.0 · diet none meaningful (aerial
  filter-feeder on spore fall) · speed 1.2 ground. **GROUNDED FLOATER — owner
  ruling by card 2026-09-27:** a drifting jelly is a floater, not a flapper; no
  flight stats. Drawn at canopy scale; the sink-before-Burn tell stays a
  cosmetic/behavioural beat, not a landing.
- **Wiring:** `RM_ContagionFauna.xml`. The sink-before-Burn behaviour is the
  sheet's Owed engine pass (jelly tell), not this def's XML.

### Blisterfloat (`RM_Blisterfloat`) — the sower
A hanging cluster of taut skin blisters under a gas bladder, dragging weeping
tendrils; it rises on the storm updraft to escape and bursts in the sunlight,
every time.
- **Cycle:** the escape attempt, failing a hundred times a day. Rides the updraft
  over the ridge, pops in UV, rains dead spores; the rim is littered with husks
  (the grey-white husk palette note, §9).
- **Stats:** bodySize 1.2 · commonality 0.5 · diet none (gas-bladder drifter) ·
  speed 1.0 ground. **Flyer:** `MaxFlightTime 15` / `FlightCooldown 8`,
  `flightSpeedFactor 1.8`, `canFlyIntoMap true`, `canLeaveMapFlying true` (leaving
  IS its story; the ones that leave are the ones that die off-map).
- **Wiring:** `RM_ContagionFauna.xml`.

### Scorchpod (`RM_Scorchpod`) — the leaker
A blistered walking seed-case on too few legs, shell sweating metal, smoking
faintly the moment the light touches it.
- **Cycle:** gallium-based, not carbon — the one native that can walk into the
  Burn (ban 2's ruled carve-out). Carries live tissue toward the valley mouth and
  almost always cooks first; drops **gallium** on butchery (§7 of the sheet).
- **Stats:** bodySize 0.55 · commonality 0.85 · diet detritus · speed 2.4 ·
  UV-tolerant flag rides the Owed Burn-weather engine pass.
- **Wiring:** `RM_ContagionFauna.xml`; butcherProducts gallium (item def exists in
  the stack; verify at build, never guess the defName).

### Bloodlurk (`RM_Bloodlurk`) — the drinker
A jointed shadow at the red waterline, all forelimb and siphon, that holds still
better than anything alive should.
- **Cycle:** water is everywhere, nutrients are not — it hunts warm blood at the
  pools. The ruled reason visitors die at the water's edge (commonality raised
  0.035→0.2 in the roster "so the pools actually kill").
- **Stats:** bodySize 0.8 · commonality 0.2 · carnivore ambush predator, hunts
  colonists at low body-size threshold · speed 3.8 in a lunge · manhunter-on-damage
  high.
- **Wiring:** `RM_ContagionFauna.xml`.

### Meltgut (`RM_Meltgut`) — the undertaker
A house-sized slug whose translucent belly shows the last three things it
swallowed, at three stages of not existing any more.
- **Cycle:** corrosive disposal of the Unfinished, faster than the goo reabsorbs —
  the valley's rendering vat. Where a Bloom's failures go.
- **Stats:** bodySize 4.0 (MEASURED donor) · commonality 0.1 · scavenger · speed
  0.6 (MEASURED donor) · acid melee, corpse-dissolving digestion.
- **Wiring:** `RM_ContagionFauna.xml`. **bs≥4 → 512 art canvas** (per the art
  rule this commission follows).

### Sparkleech (`RM_Sparkleech`) + Sparkleech grub (`RM_SparkleechGrub`) — the thieves
A wet-winged flap of tissue with a socket-mouth that clamps onto an Eyebark and
drinks its charge; the lights in its wings are stolen.
- **Cycle:** taps the ocular trees; ruinous to anything a visitor tries to grow.
  The grub is the same theft without the wings — and the donor's
  changes-into-another-creature special (MEASURED in the roster) is the biome's
  unfinishedness already built into a life-cycle: grub → adult.
- **Stats:** adult bodySize 0.45 · commonality 0.15 · plant-sap electrovore ·
  speed 3.2 · **Flyer:** `MaxFlightTime 10` / `FlightCooldown 5`,
  `flightSpeedFactor 2.2`, `flightStartChanceOnJobStart 0.15`. Grub bodySize
  0.2 · commonality 0.05 · speed 1.4 · not a flyer.
- **Wiring:** both in `RM_ContagionFauna.xml`; the grub's growth-into keeps the
  donor mechanism shape on our defs.

### Scaldhide (`RM_Scaldhide`) — the basker
A low armoured slab of scar tissue on legs, plates fused wrong, that walks out
into the killing light and eats what it finds already cooked.
- **Cycle:** UV-armored (donor acid-immunity MEASURED; the armor carve-out of ban
  2) — comes OUT in the Burn to eat scorched Unfinished in the open.
  Predator-of-the-window: the player moving in a Burn shares it with this.
- **Stats:** bodySize 1.8 · commonality 0.1 · carnivore-scavenger · speed 2.8 ·
  high blunt/heat armor.
- **Wiring:** `RM_ContagionFauna.xml`.

### Doublemaw (`RM_Doublemaw`) — the pickers
Two jaws on one skull, the second set where a throat should be, taking turns.
- **Cycle:** fast omnivore on the carcass economy; its infecting bite (donor
  special, MEASURED) is on-theme and kept.
- **Stats:** bodySize 0.6 · commonality 0.15 · omnivore · speed 4.6 · infection
  chance on bite wounds.
- **Wiring:** `RM_ContagionFauna.xml`.

### Gnashling (`RM_Gnashling`) — the pickers
A fist of teeth with legs — mostly mouth, the rest an afterthought.
- **Cycle:** swarm picker on the carcass economy; travels in numbers, strips what
  the Doublemaw opens.
- **Stats:** bodySize 0.25 · commonality 0.1 · omnivore · speed 4.2 · pack spawner
  (herd 4–8).
- **Wiring:** `RM_ContagionFauna.xml`.

### ikee (`RM_Ikee`) — the wretched-small
The owner's own creature name (2026-08-15), kept by his correction this sitting:
a shivering eye-cluster on legs that follows bigger things and watches.
- **Cycle:** wretched-small band of the roster (comm 0.6) — under-canopy skitterer
  living off the goo's leavings; dives into goo-pockets at the Burn.
- **Stats:** bodySize 0.3 · commonality 0.6 · scavenger · speed 4.0 · timid
  (flees, never fights).
- **Wiring:** `RM_ContagionFauna.xml`. ⚠️ Its DesertPort twin `RSW_Stareling`
  carries a second ruled name (*oxxa*) — that two-name flag is the names file's
  flag 2, not resolved here.

### the Shambles (`RM_Shambles`) — the walking dead
A dead thing still going somewhere, held up and steered by the fungus wearing it.
- **Cycle:** the weaponised fungus animating what the Burn and the pickers left —
  slow, virulent, treatable (donor behaviour kept on our def). Size ruled: 2 cells
  (drawSize 2, sitting ruling 2026-09-10, carried over).
- **Stats:** bodySize 1.6 · commonality 0.5 · none (fungal puppet) · speed 1.3 ·
  disease-vector melee.
- **Wiring:** `RM_ContagionFauna.xml`, drawSize 2 per the carried ruling.

### Peeper (`RM_Peeper`) — the watcher-kin
A once-predator gone soft and eye-studded — extra eyes opened in its hide until
watching replaced hunting.
- **Cycle:** the mutated nightling line: sturdier, docile, staring. Mid-tier
  browser of the goo margins; another sky-reader the player can learn from.
- **Stats:** bodySize 1.0 · commonality 0.5 · omnivore · speed 3.4 · docile
  (high wildness, low aggression).
- **Wiring:** `RM_ContagionFauna.xml`.

### Eyestinger (`RM_Eyestinger`) — the tail
A big segmented thing whose raised tail ends not in a sting but in an eye — and it
stings with it anyway.
- **Cycle:** heavy ambusher of the Eyebark groves; the donor's twitching-eye
  scorpion re-fleshed as ours.
- **Stats:** bodySize 2.5 (MEASURED donor) · commonality 0.5 · carnivore · speed
  3.0 · armored carapace, venom sting.
- **Wiring:** `RM_ContagionFauna.xml`.

### Fleshsop (`RM_Fleshsop`) — the pitiable
The owner's word: a wet rag of a creature, barely holding a shape, that leans on
things to stay standing and needs to be loved to live another day.
- **Cycle:** the failing chimera (donor bs 0.2 MEASURED) — what an Unfinished
  looks like when the goo forgets to take it back. The valley's one tug at the
  player's sleeve.
- **Stats:** bodySize 0.2 · commonality 0.5 · omnivore (fed by hand) · speed 2.0 ·
  the donor's needs-affection mechanic kept on our def.
- **Wiring:** `RM_ContagionFauna.xml`.

### the Unfinished (`RM_TheUnfinished`) — the experiments
**Already ours, already built, already in register — stays as-is.** Live set in
`src/RimMandrake/Contagion/`:
`Defs/ThingDefs/RM_TheUnfinished.xml`, `Defs/HediffDefs/RM_UnfinishedHediffs.xml`,
`CompRandomizeUnfinished.cs`/`CompSpawnerUnfinished.cs`. Not renamed, not re-arted
in this commission.

## 3. Fauna — new species (the enrichment)

All five are goo-bud lines, not independent evolutions: each dissolves back to
Bloody Mess at death (goo-corpse note on the def, the Unfinished's precedent), so
ban 3's "no finished natives" is satisfied the way the sheet itself satisfies it —
they are recurring drafts the goo keeps re-issuing, not settled species. The
mandatory owner addition (*"really gross fleshy flapping skin things that fly"*)
is the Skinflap and the Gorekite. **The sheet amendment admitting these five is
BENCH's to write; this section is its design input.**

### Skinflap (`RM_Skinflap`) — the mandatory horror, small
A sheet of loose wet skin that flies — no body to speak of, just the flap,
slapping itself through the air between canopy layers and draping over branches
to dry.
- **Cycle:** swarming, harmless, unforgettable — the Bloom's confetti. Feeds by
  soaking spore-rich rain through its underside; drapes flat and drips. Dives
  (drops and drapes) at the Burn.
- **Stats:** bodySize 0.15 · commonality 1.2 (numerous — the sky should move) ·
  filter-feeder · speed 2.0 ground, herd 6–12. **Flyer:** `MaxFlightTime 12` /
  `FlightCooldown 4`, `flightSpeedFactor 2.5`, `flightStartChanceOnJobStart 0.4`.
- **Wiring:** `RM_ContagionFauna.xml`; goo-corpse.

### Gorekite (`RM_Gorekite`) — the mandatory horror, large
A stretched hide the size of a tent riding the storm shear, trailing one long
wet grasper; its shadow crossing yours is the only warning before it drops and
smothers.
- **Cycle:** apex of the canopy air — preys on Skinflaps, Gawpsacks and anything
  man-sized caught in the open under the Bloom. Predator complement to the
  Scaldhide: one owns the Burn, this owns the storm.
- **Stats:** bodySize 1.6 · commonality 0.08 · carnivore, hunts colonists ·
  speed 2.2 ground. **Flyer:** `MaxFlightTime 20` / `FlightCooldown 10`,
  `flightSpeedFactor 2.8`, `canFlyIntoMap true` (arrives with weather fronts).
- **Wiring:** `RM_ContagionFauna.xml`; goo-corpse.

### Danglemaw (`RM_Danglemaw`) — the ambusher
A mouth on a tendon: a muscular cord anchored in the Eyebark canopy with a
free-hanging jaw at the end of it, slack until something walks underneath.
- **Cycle:** the canopy's toll — punishes the one shelter the Burn drives
  everything into. Under the trees is safe from the sky and not safe.
- **Stats:** bodySize 1.0 · commonality 0.12 · carnivore ambush (aggro radius
  small, damage high) · speed 1.0 (it barely relocates; the anchor drags).
- **Wiring:** `RM_ContagionFauna.xml`; goo-corpse. True ambush-from-canopy
  behaviour would be C#; v1 ships as a slow high-damage lurker spawned near
  Eyebark clusters — note for the def, not a blocker.

### Crispling (`RM_Crispling`) — the burn-line scavenger
A hunched picker crusted in its own char — it lets the Burn cook its back to a
shell, then walks the scorch line eating what didn't dive fast enough.
- **Cycle:** closes the Burn's loop: Burn kills → Crispling eats → Crispling's
  droppings feed the goo's edge. The third member of the Burn window with the
  Scaldhide and the player (armored carve-out of ban 2, char-crust flavor).
- **Stats:** bodySize 0.4 · commonality 0.3 · scavenger · speed 3.6 · heat/UV
  armor on the crust, soft underneath (flanking it works).
- **Wiring:** `RM_ContagionFauna.xml`; goo-corpse.

### Sloshbelly (`RM_Sloshbelly`) — the cistern (this pass's own addition)
A tick the size of a dog, swollen tight with red water, skin stretched to
translucency — it sloshes audibly when it walks, and the natives puncture it to
drink.
- **Cycle:** fills the naked niche in the water economy: everything needs the red
  water, only the Bloodlurk owns the pools — the Sloshbelly is the water that
  walks away from them. Burrows shallow at the Burn; punctured by predators (and
  butchering players) it yields red water, poison until sunned (§5/§7 of the
  sheet — the sun-sterilization loop gets a portable source).
- **Stats:** bodySize 0.6 · commonality 0.25 · red-water drinker (functionally
  herbivore-none) · speed 1.8, slower when full · butcher/harvest yields red
  water units (rides `WATER_KINDS_TAXONOMY_1`, not authored here).
- **Wiring:** `RM_ContagionFauna.xml`; goo-corpse.

## 4. Flora — ports

All in `src/RimMandrake/Contagion/Defs/PlantDefs/RM_ContagionFlora.xml` (new
file). None edible, none foragable (ban 4 — the biome def keeps forage 0.1 with
no foraged food def). The biome's `<wildPlants>` uses the shorthand element form
(`<RM_Eyebark>1.0</RM_Eyebark>`), **never `<li>`** — same law as `<wildAnimals>`.

- **Eyebark (`RM_Eyebark`)**, comm 1.0 — the canopy: a tree whose bark is studded
  with working eyes that track passers-by; the peaks' dominant organism, the thing
  the Sparkleech taps and the Danglemaw hangs from. Sketch: tree-class,
  harvestable wood-analog at poor yield, growDays long.
- **Lashgrass (`RM_Lashgrass`)**, comm 1.0 — ground cover of fine red filaments
  that flinch away from footsteps in a spreading wave; the ground telling
  everything where you are. Grass-class, no yield.
- **Bleedleaf (`RM_Bleedleaf`)**, comm 0.6 — a low shrub whose leaves wet through
  with red at the veins and drip; not carbon-clean ("not even 100% carbon based"
  kept in the description). Bush-class.
- **Gorestalk (`RM_Gorestalk`)**, comm 0.5 — tall red columns like stood-up
  entrails, faintly peristaltic. Tall-plant class, blocks sight lines (knife
  country's set dressing).
- **Rattlegrope (`RM_Rattlegrope`)**, comm 0.4 — a knot of tentacular limbs that
  gropes the air — and **rattles before a Burn**: the second tell, kept from the
  sheet. Sketch: plant with the donor's flailing read; the rattle behaviour rides
  the Owed engine pass with the Gawpsack sink.
- **Sapblister (`RM_Sapblister`)**, comm 0.4 — a swollen globular plant whose
  skin blisters weep red sap: the sheet's insect repellent and wound-sealant
  (§7). Harvest yields red sap units; the yield is an item, never food.
- **Bloody Fist (`RM_BloodyFist`)**, comm 0.3 — the owner's coinage this sitting:
  a clenched knuckle of dark red blooms on a spined stalk; its armored seed-fist
  breaks off, rolls to the burn line and dies there as fertilizer (sheet §4 kept
  verbatim).
- **Halfmade Tree (`RM_HalfmadeTree`)**, comm 0.5 — the infection front,
  advancing in Blooms, burned back in Burns. **Art redo folded into this
  commission (sheet Owed):** half PLANT, alien on BOTH halves — one half an alien
  plant being overwritten by a different alien wrongness, never a half oak, no
  Earth-tree read anywhere on it.
- **blighted halfmade tree (`RM_HalfmadeTreeBlighted`)**, comm 0.15 — the
  variant (plain-modifier form): the downslope front-line texture, further gone,
  barely a plant at all.

## 5. Flora — new species

Same file, same shorthand wiring, same bans. All three are infection-front
organisms (unfinished-flavored by construction).

- **Meatvine (`RM_Meatvine`)**, comm 0.35 — a vine of twitching muscle tissue,
  anchored at both ends and flexing slowly like something testing a limb it
  hasn't finished growing. Climbs Eyebark and Gorestalk; the goo trying out
  "reach". No yield; ugly-environment thought contributor.
- **Toothmoss (`RM_Toothmoss`)**, comm 0.3, burn-line band — a carpet of small
  grinding teeth at the scorch margin, wearing themselves down chewing the
  sterilized matter back into soil the goo can take. The Crispling's habitat.
  Walking it is slow and loud (movement cost up).
- **Wombpod (`RM_Wombpod`)**, comm 0.2 — translucent gestation pods the goo
  grows in sheltered hollows, each with something part-made floating in it.
  **The amoeba hosts of the built genome loop**: the Contagion mod's live
  gestation machinery (`RM_AmoebaGestation.xml`, `Hediff_AmoebaGestation.cs`,
  `AmoebaHostUtility.cs`, `RM_GenomeSample.xml`) gets its in-world organ —
  harvestable (a work-gated harvest yielding a gestation host / genome-loop
  input, exact item wiring at build), never food, and harvesting one is how the
  genome loop's host acquisition reads in the world instead of appearing from
  nowhere.

## 6. Set pieces and devices

- **the Coalescence** — three staged sprites (`coalescence_stage1/2/3`, 512, no
  facings): a growing crimson blob of eyes and part-limbs — the goo somewhere it
  has been left alone too long, gathering mass and parts toward something with a
  middle. Stage 1 a swelling in the goo with a few open eyes; stage 2 a heaped
  mass with limbs surfacing and submerging; stage 3 a tower of almost-anatomy,
  dozens of eyes, on the point of standing up. (Def/mechanism are the sitting's
  to rule; this commission delivers the staged art.)
- **Cloud Repulsor (`RM_CloudRepulsor`)** — a squat Helix field device emitting a
  brilliant vertical purple beam: Helix hardware that punches a hole in the cloud
  — a man-made local Burn. Single sprite, 256.
- **Sunbeam (`RM_Sunbeam`)** — a handheld Helix UV projector: the weapon that
  brings the clear sky indoors; the only ranged answer the Bloom respects.
  Single sprite, 256.

## 7. Ban compliance (sheet §6, checked row by row)

1. **No green squares** — no def here touches placement; roster binds per def.
2. **No life outside the storm shadow** — every native above is UV-shy (dives:
   Bloody Mess, Gawpsack, Blisterfloat, Bloodlurk, Meltgut, Sparkleech+grub,
   Doublemaw, Gnashling, ikee, the Shambles, Peeper, Eyestinger, Fleshsop,
   Skinflap, Gorekite, Danglemaw, Sloshbelly) or rides a ruled carve-out
   (Scorchpod the leaker; Scaldhide and Crispling armored).
3. **No finished natives beyond the ruled table + this sitting's additions** —
   the five new fauna are goo-bud lines with goo-corpses (re-absorbable by
   construction); the amendment recording them on the sheet is BENCH's.
4. **No edible forage** — nothing above is food: Sapblister yields sap (item),
   Sloshbelly yields red water (poison until sunned), Wombpod yields a genome-loop
   host, Scorchpod yields gallium. No nutrition on any plant, no
   human-consumable animal product.
5. **Red fog ×0.4 stands** — untouched.
6. **Contagion-touched never upgrades** — no def here grants a positive
   mutation; the genome loop's payoffs stay inside the already-built mod's
   mechanics.
7. **War-legacy split** — all content is Assailant-arsenal flavored; no
   Wasteland reads.
8. **Recognizability** — no Earth-animal or Earth-plant read anywhere in the
   briefs; the one deliberate Earth echo (a tick, a moss) is broken in each
   prompt (translucent water-swollen; teeth).

## 8. Def-wiring summary

- Mod: `src/RimMandrake/Contagion/` (exists, builds, ships `RM_Contagion` biome
  def). New files: `Defs/ThingDefs_Races/RM_ContagionFauna.xml` (+ PawnKindDefs),
  `Defs/PlantDefs/RM_ContagionFlora.xml`. **No patches** — full RM_ development
  per the ruling; the one existing donor-targeting patch
  (`Patches/RedGooSpawnsUnfinished.xml`) retargets to `RM_BloodyMess` and then
  folds into the def.
- Biome roster: `RM_Contagion.xml` `<wildAnimals>`/`<wildPlants>` in the
  **shorthand element form** (`<RM_Gawpsack>2.0</RM_Gawpsack>`), never `<li>` —
  the custom loader reads node name + text; a `<li>` silently discards.
- Flyers (Blisterfloat, Sparkleech, Skinflap, Gorekite — Gawpsack ruled a
  grounded floater by card 2026-09-27): statBases
  `MaxFlightTime`/`FlightCooldown` + race `flightStartChanceOnJobStart`/
  `flightSpeedFactor`/`canFlyIntoMap`(/`canLeaveMapFlying` Blisterfloat only),
  vanilla Locust shape. The switch is the STAT, not a bool; flight animation
  frames are separate and never block shipping.
- Commonalities: ports keep the ruled roster's numbers verbatim; new species'
  numbers above are design-sketch values for the sitting to ratify.
- C# already live and reused, not rebuilt: the Unfinished spawner comps, the
  genome loop (Wombpod is its flora face), `RM_ContagionBiome.cs`.
- defNames: every RM_ name in this doc swept against `src/` this pass — 0
  collisions (sanity probe `RM_Fessk` hit 4 files).
