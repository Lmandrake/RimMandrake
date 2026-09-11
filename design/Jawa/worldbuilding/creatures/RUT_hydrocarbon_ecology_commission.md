<!-- status: design brief — nothing here is built -->
# The hydrocarbon ecology — HYDROCARBON_ECOLOGY_COMMISSION_1

_Design brief, 2026-09-10, Fable pass (backgrounded from BENCH per
`infrastructure/agents/Agent_Policy.md`). This doc **specifies**: no XML, no C#, no
art generation (art HELD until the Codex channel is fixed). Format precedent:
`creatures/goo_boom_commission.md` (the vhessk). Every rule INVENTED here rather than
derived from a ruling, sheet law, or measurement is flagged **[INVENTED]**._

**The commission, verbatim (owner, live at the bench, 2026-09-10):** *"What kinds of
small, innocuous little creatures might be swimming around in the propane lakes (and
the big propane lake)? Totally alien life that uses hydrocarbon for blood. A stationary
animal that stings/attacks at the bottom of the propane lake. Weird plant-like growths
underwater. Keep going like this and make interesting things growing in the blue desert
and propane lake biomes and propane lakebed. Do this in the background and commission
them."* Eight live addenda followed, each with a reference image (§0).

**Reference images (all committed under `creatures/references/`):**

| file | seeds |
|---|---|
| `propane_lakebed_stinger_hydra_ref.png` | the lakebed stinger (§4): bulbous anchored stalk, tentacle crown, budding juvenile |
| `propane_underwater_growth_microbial_ref.png` | the underwater growths (§5): sphere colonies + hair-fine filaments |
| `propane_crystal_lifeform_ref.png` | crystal form A (§3): faceted shard body, helix-braided tentacles, drifting motes |
| `propane_crystal_lifeform_B_ref.png` | crystal form B (§3): crystal crown on a single helix stem, frost-fern fronds, rooted |
| `twilight_ocean_bottom_rosette_ref.png` | the twilight bottom rosette (§8): concentric tubular-cell rings, teal rim → gold core, self-lit |
| `twilight_venom_worm_ref.png` | the twilight venom worm (§9): iridescent segmented worm, stalked bulb-tipped appendages, feathery gill-fans |
| `scald_bladderboil_ref.png` | the bladderboil (§10): golden wrinkled sac body with crater openings — the deflated state |
| `grey_deep_bacterial_mat_ref.png` | the Grey Deep mat (§11a): pink-ochre spiky-cusped carpet in total darkness |
| `grey_deep_brine_pool_ref.png` | the brine pool (§11b): a sharp-rimmed milky-turquoise lake-within-the-sea |
| `grey_deep_brine_rim_mussels_ref.png` | the rim beds (§11c): dense yellow-green shell beds crowding a brine pool's precipitate rim |

---

## 0. The owner-seeded commissions, at a glance

| # | seed (owner's words) | name | biome | engine shape | section |
|---|---|---|---|---|---|
| 1 | "stationary animal that stings/attacks at the bottom of the propane lake" | **vhaal** (`RUT_Vhaal`) | propane lakebed | hostile Building with a short-range verb (not Plant, not pawn — §4b) | §4 |
| 2 | "something interesting as a plant to grow on the bottom of the Twilight Ocean" | **hearthwheel** (`RUT_Hearthwheel`) | the_twilight_deep | Plant def (interaction test: harvested) — build deferred to diving mods | §8 |
| 3 | "a bladderboil… puffing up in the boiling water… can be fished for" | **bladderboil** (`RUT_Bladderboil`) | the_scald | wildAnimals aquatic pawn + fishTypes catch item (both — §10c) | §10 |
| 4 | "Twilight deep-sea worm, venomous, slow but nasty" | **sissal** (`RUT_Sissal`) | the_twilight_deep | pawn, slow, venom melee (toxic buildup route) | §9 |
| 5 | "Propane crystal life form" (drifter) | **aviir** (`RUT_Aviir`) | the_propane_lakes | pawn, aquatic drifter — one of the swimmer set | §2, §3 |
| 6 | "Different propane crystal life form" (rooted) | **aviir crown** (`RUT_AviirCrown`) | propane lakebed | Plant def (interaction test: anchored + harvestable — §3c) | §3 |
| 7 | "Bacterial mats at the bottom of the Grey Sea" | **mason-felt** | the_grey_deep | TERRAIN (interaction test: condition of the seafloor) | §11a |
| 8 | "Deep sea Grey Sea brine pools… extremely toxic" | **stillpool** | the_grey_deep | TERRAIN + toxicity mechanic (hazard tier of the ruled ambient brine) | §11b |
| 9 | "Underwater yellow mussels growing around brine pool" | **rimshell** (`RUT_Rimshell`) | the_grey_deep | harvestable Plant-def bed at the pool shore (interaction test: harvested) | §11c |

Everything else in this brief is the "keep going like this" extension: the biochemistry
page (§1), two more swimmers (§2), the underwater growth flora (§5), the Blue Desert
detonation-register flora and its eater (§6), and the lakebed as a layer (§7).

---

## 1. Waxblood — the hydrocarbon biochemistry through-line

One shared mechanism, so every species below cites it instead of re-inventing its own
chemistry. The ruled base is `the_blue_desert.md` §3 "Hydrocarbon biology
(owner-ratified, in full)": *no glucose; metal-organic compounds trapped in cell
membranes, a hydrocarbon soup for blood; butane and pentane as the power-storage
molecules; methane exchange as the basis of metabolism, with some fast creatures toying
with the extreme energy of oxidation. Catastrophically reactive in a warm oxygen
environment — the extreme cold keeps them stable.* And `the_propane_lakes.md` §4's
admission test: *hydrocarbon- or ammonia-metabolic, cold-loving (R-H10), not an icy
dayside analog.*

**The blood.** "Waxblood": a hydrocarbon soup (ruled, verbatim) carrying dissolved
butane/pentane fuel and suspended **metal-organic granules** (ruled: "metal-organic
compounds trapped in cell membranes") that serve as the oxidizer-carriers — the
hemoglobin analog, except what they ferry is bound oxidizing radicals scavenged from
aurora-processed tholins, never free oxygen. **[INVENTED: the granules-as-carrier
reading; the metal-organics themselves are ruled.]**

**The energy source.** The nightside has no sun. The feed is what falls: **fuel snow**
(`the_propane_lakes.md` §4b — hydrocarbon and ammonia precipitation) and **aurora-ash**
(§3: "Umbra is the crags' tholin factory" — auroral particle chemistry manufacturing
fractal organics). The base of every food web below is fallout grazing: eat what the sky
makes. Metabolism is the ruled methane exchange — fuel + bound oxidizer → energy +
methane, exhaled as gas (which is why the lake fizzes faintly over a shoal —
**[INVENTED, the fizz]**).

**Why the life doesn't ignite the lake** (this must pass `the_propane_lakes.md` §6 ban
4: *no ignition without a hot source or spark — a trigger must be thermal or
electrical*). Ignition needs fuel + free oxidizer + heat. The lake is fuel; the life
never provides the other two: its oxidizer is **bound**, released only inside a cell,
molecule by molecule, and its body temperature is the lake's (−79 °C). Waxblood
metabolism is a slow fire in a locked box, run at cryogenic rates. The **Burners**
(ruled, both sheets) are the exception that proves the rule: they are the one lineage
that stores free oxidizer ("toying with the extreme energy of oxidation," ruled), which
is why they alone burn — and why they alone explode. Everything in THIS commission sits
on the safe side of that line: innocuous means oxidizer-bound. **[INVENTED: the
bound-oxidizer mechanism; its two ruled anchors are the metal-organics and the Burner
exception.]**

**Wounds.** Waxblood congeals on contact with the cold instantly — a wounded waxblood
creature self-seals in seconds, bleeding a bead of colorless wax that freezes where it
falls. Consequence for play: these creatures rarely bleed out; you kill them or they
recover. **[INVENTED]**

**Butchery and product.** Waxblood tissue is not food — no water-based gut digests it,
and warmed to habitable temperature it becomes what `the_blue_desert.md` §3 says it is:
*catastrophically reactive in a warm oxygen environment.* Butchery yields **cold wax**
— the fauna's storage chemistry as harvestable fuel, exactly the already-ruled pattern
(`the_blue_desert.md` §7: "Burner fuel glands / Swallower gut-oil — the fauna's own
storage chemistry as harvestable fuel, at the fauna's own risk"). Every wax product
carries the warm-detonation behavior or it violates §6 ban 3 ("no warm-safe hydrocarbon
organics… you never bring one indoors"). Zero meat, zero leather, no kitchen path —
mirror the vhessk's explicit-zero convention. **[INVENTED: the "cold wax" item name;
the yield-is-fuel pattern is ruled.]**

**Scope.** Waxblood covers the Blue Desert and Propane Lakes hydrocarbon casts in this
brief. The Ammonia Flats' cast (Frostbound Behemoth, Terramorph) is the OTHER ruled
chemistry (`the_propane_lakes.md` §3 "Two solvents") and is not touched here —
FrostboundBehemoth's OPEN alien redesign is left where it is, un-folded-in: it is
ammonia-register work and belongs with an Ammonia Flats pass, not a hydrocarbon one.

---

## 2. The lake swimmers — small, innocuous, and the fish of a lake you cannot swim in

**Set of 3** (flora-template ruling §8.5: default 3 per set — applied to this fauna set
as well **[INVENTED: extending the flora set-default to a fauna set]**). The design
anchor is the review finding (`review/round2/biome_findings.md`, the_propane_lakes):
*"admission test is strict (solvent-tolerant, ignition-safe) — commission 2-3 natives
around AuroraSylph's aurora register rather than importing."* This set is those
natives. AA_AuroraSylph (the ruled "perfect Propane Lake creature") holds the AIR — the
aurora dancer above the ice. These three hold the LIQUID, in the same register:
translucent, aurora-lit, quiet.

**Fishing ruled out, wildAnimals ruled in — for all three.** The roster carries the
ruling already (`rosters/the_propane_lakes.json`, FISH_BY_BIOME_1): *"no fish — the
lake is liquid propane at ~−79 °C, not water… CREATURES owed as new defs, not
fishTypes."* So unlike the Megakrill (a fishing result, never a spawn —
`review/round2/move_mapping_v2.md`), the lake swimmers are the inverse: **spawned
aquatic wildAnimals on `RUT_PropaneLake` water, never a fishing table.** There is
nothing to eat in the catch anyway (§1 butchery), and the point of them is to be SEEN —
ambient life making the black mirror alive. The V-wake exotic (ruled v1,
`proposals/propane_gas_deep_design.md` row `lake-creature`) stays a separate, later,
hostile def; these three are what it eats. **[INVENTED: the V-wake-eats-them link.]**

All three: `RUT_` tier (`design/NAMING_SCHEME_PLAN.md` — endemic campaign content),
names per `Alien_Bestiary.md` §1 with the fish commission's refinement (soft vowel-led
names for drifting water-life; clade roots for chitin). Collision-swept against
`fish_bestiary_commission_2026-09-10.md`, `creature_names_ashkarr.md`, and the biome
sheets. Untransportable dayside, all three (R-H10, restated as `the_propane_lakes.md`
§5: "nothing native survives the crossing dayside").

### 2a. The aviir — the crystal drifter (owner seed #5; full treatment §3)

Listed here as a member of the set; specified in §3 as half of the crystal pair.
Innocuous, drifting, the set's beauty. Small bin.

### 2b. The ophal — the fallout grazer

| field | value |
|---|---|
| defName / label | `RUT_Ophal` / `ophal` |
| nickname | "snowmoth" — for the way a shoal rises to meet the fuel snow |
| body plan | a flattened translucent ribbon, 30–40 cm, edged with a continuous undulating fin; no eyes, a dorsal line of faint aurora-green photophore dots (it navigates by the sky's light through the surface — **[INVENTED]**) |
| behavior | shoals just under the surface on fuel-snow nights, grazing the fresh fall as it dissolves; sinks to mid-water when the sky is quiet. Wholly non-combat: `herdAnimal`, flees, never fights |
| admission | `the_propane_lakes.md` §4 (hydrocarbon-metabolic, cold-loving, no dayside analog) + §1 waxblood; its feed is the ruled fuel snow (§4b) |
| size | small bin; bodySize well under 0.5 — vermin-class, spawned in groups |
| product | butchery: a little cold wax (§1); no meat, no leather |
| art | palette inside the propane family (`palettes/biome_palette_anchors.json`: `#0b0d12`→`#ccd4dc`), body glass-grey, the photophore line the only color — aurora green, LOW saturation so it defers to the flora accent (§5 header). The signature image: a shoal of ophal under falling fuel snow, dots of green under a black mirror |

### 2c. The skerrik — the bed-skater

| field | value |
|---|---|
| defName / label | `RUT_Skerrik` / `skerrik` |
| nickname | "tapper" — divers hear its walking as fingernail taps on the hull |
| body plan | a palm-sized chitin-analog disc on eight stilt legs (the `karr-`/`-rrik` chitin clade root, per `Alien_Bestiary.md` §1 — armour takes the land roots), skating on the lakebed sediment; wax-white shell, no glow (the bed is dark; ban-safe) |
| behavior | works the lakebed growth fields (§5), rasping pearlfield beads and carrion wax; the vhaal's (§4) staple prey and the reason the stinger gardens exist where the fields are thickest. Timid, scatters from light |
| admission | `the_propane_lakes.md` §4 + §1 waxblood; closes the lakebed loop: fallout → growths → skerrik → vhaal |
| size | small bin, bodySize ~0.3 |
| product | butchery: cold wax + a chitin-analog scrap **[INVENTED: the scrap; whether it is stony or counts as a stuff is an economy call, left open §12]** |
| art | wax-white and bone-grey inside the family's light steps; it reads by silhouette (stilt-legged disc), not color |

---

## 3. The crystal pair — aviir and aviir crown (owner seeds #5 and #6)

Two reference images, one deliberate pair: **A** (`propane_crystal_lifeform_ref.png`) a
faceted crystal-shard body on the jellyfish plan, trailing helix-braided translucent
tentacles, attended by drifting motes; **B** (`propane_crystal_lifeform_B_ref.png`) a
crystal cluster crown rooted on a single helix stem, radiating frost-fern fronds with
spark-tipped ends. The two share the helix — the pair reads as designed.

### 3a. RECOMMENDED reading: one organism, two stages

**The rooted crown is the polyp; the drifter is what it buds.** Real cnidarian logic
(polyp → medusa), and the shared helix-stem makes it visually legible without a codex
entry. The aviir crown sits anchored on the lakebed growing its crystal crown from
dissolved minerals; at maturity the crown's terminal shard **calves** — detaches and
drifts free as an aviir, trailing the helix that was its stem. Old lakebeds are
crown-gardens; the water above them glitters.

- This gives the propane lakes the same lifecycle-hook distinction the Scarlands got
  with MegaphoridLarva — a biome whose wildlife teaches its own biology by being
  watched.
- Engine shape: **two defs regardless** (RimWorld has no metamorphosis mechanic to
  lean on): `RUT_AviirCrown` and `RUT_Aviir`, the lifecycle carried in descriptions
  and spawn placement (crowns on the bed, drifters in the water). A real calving
  mechanic (crown spawns a drifter on a timer) is a small C# comp — flagged as
  optional, not v1. **[INVENTED: the lifecycle; the alternative below is offered.]**

**Alternative reading (offered, not recommended): two sibling species** — same crystal
lineage, one sessile and one free. Cheaper lore, no calving question, but it spends two
species slots saying less than one lifecycle says.

### 3b. The aviir (drifter, stage 2 — the set's third swimmer)

| field | value |
|---|---|
| defName / label | `RUT_Aviir` / `aviir` |
| nickname | "lakestar" — from shore it is a point of violet light moving under the mirror |
| body plan | a hand-to-forearm-sized faceted shard — translucent crystal, violet-blue self-lit core — trailing two to four helix-braided tentacle skeins. Drifts; swims only to right itself and to rise |
| the niche split vs AA_AuroraSylph (required reconciliation) | the sylph is the ruled perfect creature of the AIR — the aurora register above the ice. The aviir is the same register taken INTO the liquid: it rises to just under the surface on reconnection nights and its core brightens with the sky (it metabolizes induced charge — see below). Sylph above the mirror, aviir below it, the reflection made literal. No niche overlap: one flies, one drifts; they meet only in the player's screenshot |
| why crystal life is lawful here | the biome already rules partially-inorganic life: `the_propane_lakes.md` §4 "Crystal flora: partially inorganic, regrowing daily from the fuel snow." The aviir is that ruling's faunal step. And it passes the Lantern Deeps' principle (`the_lantern_deeps.md` §6 ban 3: "resident crystal life is crystal, not an animal wearing crystals") — the aviir IS crystal: the shard is the body, not armor on flesh |
| one lineage with the Lantern Deeps' cast, or unrelated? | **PROPOSED AS AN OPTION, flagged for the owner:** the deep-lore thread — the caverns' crystal cast (Gembug/CrystalCrab/Glowtail) and the lake's crystal pair share an origin in the planet's mineral-organic chemistry, two expressions of one very old trick (deep warm caverns vs cold surface pooling). It would make crystal life a planet-level fact rather than two coincidences. The alternative is deliberate unrelatedness (convergence). Nothing below depends on the answer; no sheet currently rules it either way |
| energy | waxblood §1 plus a second income no other native has: **piezo-charge** — the crystal body harvests the auroral ground currents the biome already rules (§3 "the electrojet"; §7 the tap harvests the same sky). It is the electrojet tap, evolved first. **[INVENTED, anchored on the ruled GIC physics]** |
| ignition safety | ban 4 pass: it carries charge, not heat, and micro-currents at −79 °C in a body with no free oxidizer spark nothing. The TAP is the dangerous electrode, not the aviir **[INVENTED]** |
| behavior | innocuous drifter; congregates under aurora; `manhunterOnDamageChance` 0 — it cannot meaningfully fight and doesn't |
| size | small bin, bodySize ~0.4 |
| product | butchery/shatter: crystal shards (ties to the biome's ruled crystal-wood economy, §7) — never kyber (§6 ban 2, restated: crystal content carrying kyber properties is a violation) |
| **the motes** (in ref A) | **RULED-CHEAP CALL: pure art.** Drawn into the sprite and description ("attended by a dust of seed-crystals"), NOT a companion critter — an ambient mote-flock def would spend a def and a sprite to say what one sprite already says, and every added kind must pass the strict admission test. If the owner wants living motes later, the cheap route is a `wildGroupSize` flock on the aviir itself (several aviir spawn together), zero new defs — noted as the fallback |
| art | violet-blue self-lit crystal against the black mirror — sits inside the family's accent space (`#4fa8f0` running-flame blue is the biome accent). ⚠️ fauna, so the flora accent slot (§5) is not spent — but at LOW commonality so points of violet light stay rare and precious, per §9 "aurora green/violet" |

### 3c. The aviir crown (rooted, stage 1) — and the interaction test

Anchored and harvestable — so the flora template's RULED interaction test
(`flora_commission_template.md` §8.3: *"If a colonist ever interacts with ONE of it
(harvest, cut, study) it is a Plant def"*) applies even though the fiction codes it as
fauna: **the aviir crown is a Plant def.** A colonist (or the submerged-adventure crew)
harvests A crown for its shards; nothing about it needs a verb, movement, or AI —
engine-wise it is exactly what the crystal flora already is. It takes a **plant card**
in the lakebed register (§5, card 4) and is listed there; its description carries the
lifecycle ("a young lakestar, still on its stem").

---

## 4. The vhaal — the lakebed stinger (owner seed #1)

The full brief, vhessk-level. Reference: `propane_lakebed_stinger_hydra_ref.png` — the
bulbous stalk anchored at the base, the radiating tentacle crown, the budding juvenile
on the flank. That is the body plan, taken whole.

### 4a. Name and flavor

| field | value |
|---|---|
| defName (ThingDef) | `RUT_Vhaal` |
| label | `vhaal` |
| nickname (description only) | "bottlearm" — the bulbous stalk and the reaching arms; salvager slang carries the warning per `Alien_Bestiary.md` §1 rule 4 |
| tier | RimUtinni (`RUT_`, packageId `mandrake.rut.*`, per `design/NAMING_SCHEME_PLAN.md`) |

**Why this name:** one syllable, hard stop, `vh-` initial — the bestiary's whisper
register for the things with names people say from a distance. Opaque; the nickname
does the describing. Collision-swept (no vhessa/vhessk/vhaggan overlap in morpheme
position — distinct final consonant).

**Description (in-fiction, player-facing, salvager register):**

> A pale green bottle-shaped stalk the height of a standing man, rooted to the lakebed,
> crowned with a spread of slow-curling arms that do not move until something does. The
> divers who work the fuel call it a bottlearm and give each one two arm-lengths of
> respect, because the arms are longer than they look and what they touch stops
> swimming. Smaller stalks bud from the flanks of old ones, so where there is one there
> is a garden. It has never been seen to let go of the bottom, and nobody has asked it
> to.

### 4b. The engine decision — building, not plant, not pawn

The commission's own question: *building-like plant with a damage mechanic, or a
non-moving pawn?* Ruling proposed: **a map-spawned hostile BUILDING carrying a
short-range attack verb.**

- **Not a Plant def.** Two independent reasons. (1) The interaction test
  (`flora_commission_template.md` §8.3, RULED) sorts by interaction: colonists never
  harvest, cut, or study a vhaal — they fight it or route around it; its interaction
  is combat, which is exactly what the test's Plant category has no room for. (2) The
  engine fact under the test: the Plant class carries no attack verbs at all
  (confirmed in the template's own §1 engine survey of `Plant.cs` — growth, graphics,
  wind; no combat). A stinging plant is not a plant in RimWorld.
- **Not a non-moving pawn.** Vanilla has no stationary-pawn precedent; the pawn
  machinery (jobs, pathing, mental states, manhunter wandering) assumes movement, and
  a MoveSpeed-0 pawn fights that machinery everywhere. The vhessk brief could lean on
  a moving pawn's mechanics; the vhaal cannot.
- **The precedent that fits:** vanilla mechanoid clusters spawn hostile, attackable,
  verb-carrying BUILDINGS on a permanently hostile faction on wild maps. The vhaal is
  that pattern reskinned organic: full health bar, targetable, attacks what enters
  range, never moves. ⚠️ Build-seat verification owed (never guess a field): confirm
  the turret-building def shape and its verb/faction wiring against RimSage before
  writing XML; nothing in this table is a guessed field name, and the exact
  building-class choice is the builder's to verify.

### 4c. Behavior and numbers (design-level)

| aspect | spec |
|---|---|
| attack | short reach — melee-radius sting, 2–3 cells **[INVENTED range]**; venom register: the sting delivers concentrated waxblood oxidizer — a burning cold. Damage direction: moderate per hit with a slowing after-effect (frostbite/hypothermia-adjacent hediff family — exact hediff verified at build), not one-shot lethality. The threat model is "the garden costs you," not "the garden kills you" |
| threat shape | stationary hazard: it punishes route mistakes during the ruled submerged adventure and guards loot placed in its gardens (§7). It is the lakebed's answer to a trap, with a health bar |
| aggression | attacks pawns in reach; ignores everything out of reach. It cannot pursue — that is the counterplay, and it is honest: LOOK where you swim |
| durability | tough for its size (anchored, no flight response) but killable from range; killing one from outside its reach is safe and slow — the intended clearing method |
| the garden | spawns in clusters (the budding juvenile in the reference, made mechanical): placement scatters 2–5 stalks of mixed sizes **[INVENTED counts]** in the lakebed growth fields where the skerrik graze (§2c — its prey; the reason it anchors there) |
| products | killed: cold wax + sting-sacs — a venom-harvest reagent option, flagged open (§12) rather than designed as economy |
| admission | `the_propane_lakes.md` §4 admission test (hydrocarbon-metabolic, cold-loving, no dayside analog — nothing on the dayside looks like this); §1 waxblood; ban 4 pass: sting is chemical cold, no heat, no spark; ban 6/R-H10: anchored is the extreme case of untransportable |
| what it is NOT | not the V-wake creature (ruled separately, `propane_gas_deep_design.md` v1 rows: that one moves, hunts pipe and pawns, hates pumping). The vhaal is its stationary counterpart; the two never merge |

### 4d. Art direction

Reference plan taken whole: bulbous anchored stalk (widest at the lower third),
tentacle crown of 6–9 arms of unequal length, one budding juvenile on a mature flank.
Palette: the reference's green is retuned to the biome family
(`biome_palette_anchors.json` the_propane_lakes: `#0b0d12`→`#ccd4dc`) — a pale
grey-green within the family's mid values, arms tipped faintly darker; **no self-glow**
(the lakebed is dark; the vhaal is the thing you DON'T see, and every glowing species
here defers to the flora accent discipline in §5). Canvas per
`skills/generating-rimworld-sprites/SKILL.md` at build; a building gets one facing plus
damage states if the builder wants them. At review distance the read must be: a bottle
with arms, rooted, and a small one budding — "where there is one there is a garden."

---

## 5. The underwater growths — the propane lakebed flora register (owner seed: the SEM image)

Reference: `propane_underwater_growth_microbial_ref.png` — clustered spheres +
radiating hair-fine filaments. That is the shape language: **colonies of beads, and
threads.**

Per `flora_commission_template.md` §2, flora ships as a REGISTER HEADER + PLANT CARDS.
The template proposes the header live as a `flora_register` block in
`rosters/the_propane_lakes.json`; that block schema is itself still PROPOSAL, so the
cards live HERE as the authoring source and are transcribed into the roster JSON at
ratification/build — one home now, no half-installed schema. **[Process call, flagged.]**

### Register header — the propane LAKEBED (a habitat layer of the_propane_lakes)

```
flora_register (the propane lakebed):
  sheet:            biomes/the_propane_lakes.md (laws cited by §, never restated)
  palette_family:   #0b0d12 #232833 #454d5c #7d8794 #ccd4dc (palettes/biome_palette_anchors.json)
  accent (the ONE): claimed by the palespire (card 3) — running-flame blue #4fa8f0 family.
                    No other lakebed flora may carry saturated color (template §8.4, RATIFIED)
  light_regime:     none — the lakebed is dark; prompt clause "unlit, cold grey-on-black,
                    no light source, no directional shadow." Self-glow is the accent
                    species' monopoly
  silhouette_register: beads and threads (the reference): clustered spheres, hair-fine
                    radiating filaments; nothing leafed, nothing branched-woody
  hard_bans:        the_propane_lakes.md §6: #2 (no kyber), #4 (no ignition without
                    hot source/spark — nothing here is a heat or spark source), #6
                    (no transportable natives), #9 (recognizability)
  ladder:           ground cover → pearlfield · films & mats → streamer-felt (TERRAIN)
                    · vertical landmark → palespire · (aviir crown rides as a 4th card,
                    mid flora, from §3c)
  interaction test: applied per card below (template §8.3, RULED)
```

### Card 1 — pearlfield (`RUT_Pearlfield`) · ground cover · Plant def

| field | value |
|---|---|
| slot / bin | ground cover · small |
| the read | fields of frost-grey bead-clusters carpeting the lakebed — the SEM image at world scale. Each "plant" is one colony fist of spheres |
| function | the lakebed's primary producer: the beads accrete sinking fuel-snow wax and aurora-ash into storage spheres (§1 waxblood, fallout-fed). The skerrik (§2c) rasp them; the whole bed economy stands on this card |
| interaction test | **Plant def** — harvested (divers cut bead-clusters for cold wax), so the RULED test says Plant |
| ecology | high commonality, no cluster radius (lawn); grows only on lakebed terrain. Wild only — cultivation unruled here and not requested; card ships unsowable **[flagged: mirror of the Blue Desert's ban 2, applied by choice not law]** |
| graphics | Graphic_Random, 3 variants (template default), high maxMeshCount (tiling element per template §4); near-symmetric texture element, no distinctive blotch (template §5.4, the 200-instances rule) |
| palette | family mid-greys, beads a half-step LIGHTER than the bed terrain (value separation, template §8.4); zero saturation, zero glow |

### Card 2 — streamer-felt · films & mats · TERRAIN

| field | value |
|---|---|
| the read | the reference's hair-fine filaments as a ground condition: a grey felt of threads binding the lakebed sediment, combed flat by the bottom currents |
| interaction test | **terrain** — nobody harvests ONE thread; it is a condition of the seafloor (the RULED test's terrain branch, verbatim case). Ships as a lakebed terrain variant ("felted bed"), not a def with health |
| function | the bed's binder and its map-reader: felt lies combed in the current direction — free art-level navigation for the submerged adventure. Gameplay delta, if any, is a minor move-speed difference between felted and bare bed **[INVENTED, optional]** |
| palette | terrain-tone, darkest family steps; visually the "grain" of the lakebed |

### Card 3 — palespire (`RUT_Palespire`) · vertical landmark · Plant def · THE ACCENT

| field | value |
|---|---|
| slot / bin | vertical landmark · large |
| the read | where bead colonies pile for centuries they fuse and climb: a spire of fused spheres, narrowing as it rises, its top course faintly alight — running-flame blue (#4fa8f0 family), the lakebed's ONE accent (template §8.4: at most one accent species per biome — claimed here, so no other lakebed flora and neither the vhaal nor the growths may glow) |
| function | landmark navigation for the submerged adventure — the lakebed's equivalent of the Grey Deep's pillars: divers steer spire to spire. Old spires mark old fields; the vhaal gardens ring their bases (loot-and-hazard staging, §7) |
| why the glow is lawful | ban 4 needs a thermal or electrical trigger for ignition — the spire's light is cold chemiluminescence off the waxblood cycle **[INVENTED]**, no heat, no spark; nothing about it can fire the lake |
| interaction test | **Plant def** — fellable/harvestable (crystal-wood-adjacent yield, §7's ruled "crystal wood" economy) |
| ecology | rare, solitary (lone landmark per template ladder); hand-placeable for the adventure map |
| graphics | Graphic_Random 2 variants; growth-floor check per template (a young spire is a taller pearlfield — the sprite must read at 40%) |

### Card 4 — aviir crown (`RUT_AviirCrown`) · mid flora · Plant def

From §3c. Mid bin; clustered ("crown-gardens"); crystal-violet BODY but its light sits
below the palespire's accent in saturation and area — the crown is a glint, the spire
is a lamp **[the discipline that keeps §8.4 to one accent]**. Harvest: crystal shards.
Description carries the lifecycle.

---

## 6. The Blue Desert — the detonation register

What "grows" where warmth detonates: the sheet already answers — the ruled transparent
fractal flora (`the_blue_desert.md` §3: *transparent, needing no light, growing fractal
branches for gas exchange in place of leaves — ferns, dandelions, fuzzballs… when they
go, it is not a fire, it is an explosive chain reaction*). The roster's `new_defs` has
carried "transparent fractal flora set" undesigned; these are the cards.

### Register header — the_blue_desert

```
flora_register (the_blue_desert):
  sheet:            biomes/the_blue_desert.md
  palette_family:   #1c2430 #35455a #5a7086 #8fa4b8 #d2dde6 (anchors file; its own note
                    warns transparent flora anchors what refraction TINTS — expect overrule)
  accent (the ONE): NOT claimed by flora. The anchors file assigns the biome accent
                    (#55c0f0) to the Burners' blue-fire halo — fauna. Under the ratified
                    one-accent law this register leaves the flora accent slot EMPTY
                    (zero is allowed, template §3) so the only warm light for a hundred
                    kilometers stays the Burners' (§9, verbatim)
  light_regime:     starlit clear — "lit dimly in cold blue-grey ambient starlight,
                    no light source, no directional shadow"
  silhouette_register: sheet §9 verbatim: "fractal — ferns, dandelion-heads, fuzzballs,
                    transparent and small"
  hard_bans:        §6 #1 (no water metabolism), #2 (NO cultivation — every card
                    unsowable, wild-only), #3 (no warm-safe organics — every card and
                    every product carries warm-detonation), #7 (no rain), #8 (recognizability)
  ladder:           ground cover → palefloss · mid flora → glassfern · mid flora →
                    chimeglobe · (no vertical landmark: §3 "plants stay small", ruled)
  mechanic_load:    shared warm-detonation comp (roster new_defs already owes it; C#)
```

### Card 5 — glassfern (`RUT_Glassfern`) · mid flora

The fern of the ruled trio. A hand-high fractal frond, fully transparent — the art is
edges and refraction, not surface (family tints only). Every frond a charge of liquid
butane (§3, ruled). Size small; Graphic_Random 3 variants; near-symmetric (repetition
rule); harvest: wild-cut chemfuel-analog that detonates warm (§7 "hydrocarbon flora as
fuel — wild-harvest only, cold-handled only," ruled).

### Card 6 — chimeglobe (`RUT_Chimeglobe`) · mid flora

The dandelion-head: a clear stalk carrying one spherical lattice head that sheds
glittering seed-lattices to the wind (ice-sand drift as its disperser — §3b's wind,
used). Named for the sound a field makes in wind **[INVENTED detail]**. Slightly
taller than glassfern, one value-step lighter (template §8.4 value separation).
Unsowable, detonating, transparent, as above.

### Card 7 — palefloss (`RUT_Palefloss`) · ground cover

The fuzzball: a fist of transparent filaments hugging the ground — the biome's sparse
"grass" (plant density 0.33, §0). High mesh count tiling element, 3 variants, strictly
symmetric. The starter charge of every chain reaction: when a Burner detonates, it is
the palefloss field that carries the boom **[INVENTED: the chain-carrier reading;
consistent with §3's "explosive chain reaction"]**.

### Card 8 — the dovvik (`RUT_Dovvik`) · fauna · the thing that finally eats the flora

The commissioned novel niche: the Blue Desert's ruled cast eats plants only through
the Swallower's sealed macro-gut. Nothing small eats the flora, and nothing at all
decomposes it — dead glassfern just lies there, a live charge forever. The dovvik is
the answer at the small end:

| field | value |
|---|---|
| defName / label / nickname | `RUT_Dovvik` / `dovvik` / "defuser" — homesteader slang: a dovvik-cleared field is safe to walk warm |
| name grammar | `-ik` small-quick clade (`Alien_Bestiary.md` §1); collision-swept |
| body plan | a rabbit-sized low scurrier, frost-grey, with a long insulated proboscis — no jaws for plant matter at all |
| the trick | it never bites the charge; it **taps** it: the proboscis pierces a frond and siphons the butane load out cold, leaving the fractal skeleton standing — drained glass, inert. It defuses the flora plant by plant and burns the fuel over days in its own slow waxblood cycle (§1) |
| the warm-detonation ban, passed | §6 ban 3 audit: the dovvik's storage bladder is itself a hydrocarbon charge — kill one warm, or carry a carcass indoors, and it detonates like the flora it drank. Its harvested bladder is a fuel item with the standard warm-detonation behavior. Nothing about it is warm-safe |
| innocuous? | fully — flees everything, herd-less, tiny. Its danger is entirely the player's handling error, which is the biome's whole register (§1: "the beauty has a price tag on it") |
| ecology effect | grazes flora density down locally (the mechanical expression of "eats the flora" — plant destruction on feed, vanilla herbivore behavior); its drained-skeleton leavings are flavor/filth, optional |
| admission | §4 admission test: hydrocarbon-metabolic (waxblood), cold-stable, warm-reactive (the bladder). No Earth silhouette (proboscis scurrier, no ears, no tail) |
| size / product | small bin, bodySize ~0.25; butchery: the fuel bladder (cold-handled, detonates warm), no meat |
| art | family greys, one value-step darker than the ice so it reads as a moving shadow; zero color (the accent is the Burners') |

---

## 7. The propane lakebed — the bottom as its own layer (the owner's word: "propane lakebed")

What the bottom holds, assembled from the pieces above plus the ruled substrate — the
staging ground for the ruled submerged adventure (`propane_gas_deep_design.md` row
`lake`, v1: "a wild underwater adventure WITHIN a propane lake… the ship must carefully
lower itself into FUEL"):

1. **The growth fields** (§5): pearlfield lawns on streamer-felt ground, palespires as
   the landmarks — pillar-to-pillar navigation in fuel, the Grey Deep's lane-travel
   pattern arriving at the antipode.
2. **The stinger gardens** (§4): vhaal clusters rooted where the fields are thickest,
   because that is where the skerrik graze. Loot placed in a garden costs something.
3. **The crown-gardens** (§3): aviir crowns glinting violet in the dark — beauty as
   waypoint.
4. **The preserved** — the layer's own treasure logic, and it is already ruled from
   three directions: the lake is anoxic, −79 °C, and dark, and `the_propane_lakes.md`
   §5 rules "the dead of the Blue Desert arrive here"; §8 rules the fallen, the prior
   taps' wire-loop ruins, the collapsing machine's conduits, and the war lab beneath
   the surface. Everything that ever sank is still there, perfect. The lakebed is the
   planet's cold archive, and the submerged adventure is a museum robbery where some
   exhibits sting. **[Assembly of ruled parts; nothing new invented here.]**
5. **The one thing the bed never holds:** heat or spark (§6 ban 4). Every species
   above was audited against it individually; the layer as a whole contains no
   ignition source — the first one ever to arrive is the player's thruster (§3,
   ruled).

---

## 8. The hearthwheel — the Twilight Deep bottom rosette (owner seed #2)

Reference: `twilight_ocean_bottom_rosette_ref.png` — concentric rings of tubular
cells, teal rim → green → gold core, reading self-lit against blackness.

**Biome and laws** (`the_twilight_deep.md` — different world, different chemistry:
ordinary carbon-and-water life, ruled): implementation deferred by standing ruling to
the diving mods (sheet header) — this card is design-now, build-deferred, exactly like
the census's kelp-forest set.

| field | value |
|---|---|
| defName / label | `RUT_Hearthwheel` / `hearthwheel` — English flora register (flora names are descriptive here: sweetline, quickgrass precedent); named for what it is on the banks: a hearth |
| where it lawfully sits | **the lamplit banks.** §3: "the underwater rivers… their banks are the richest ground in the sea"; §7: "River-bank harvest — the mud channels' banks: the richest gathering ground, nutrient-fed forever." Self-lit, it needs no skylight — so not the light columns; and the dark between is the predator's (§4). The banks are also where the Compact tends (§8) — see the fishery line below |
| the "only true marine flora" reconciliation | §4 rules the kelp "the planet's only true marine flora" — and the sheet is FROZEN (amendments add detail, never change a ruling). So the hearthwheel is written as the sheet's OTHER register: §4's ceiling gardens are "an inverted reef of filter-feeders and grazers" — colonial animal life read as garden. The hearthwheel is that register on the floor: **a colonial filter-feeding organism in a rosette, plant-LIKE, not a plant** — each "petal ring" a ring of feeding tubes straining the detritus rain. The kelp's title stands untouched; the owner's "as a plant to grow" is honored in the engine, where it IS a Plant def. **[Reconciliation flagged for the owner: if he'd rather it be true flora, that is a one-line frozen-sheet amendment at a sitting]** |
| interaction test | **Plant def** (RULED test: harvested — the Compact and players crop its outer rings). Engine-plant, lore-colonial: the test sorts by interaction, not taxonomy |
| the fishery pairing | StoneCrab is the Compact's tended-fishery animal on the banks; the hearthwheel is the flora-counterpart: **tended rosette plots** — cropped in rings, the regrown rim harvested like a leaf vegetable of the sea **[INVENTED: the tending; anchored on §8's "kelp plots in tended rows" precedent]**. Its glow doubles as the banks' lamplight motif (§9: "lamplight on the riverbanks below") — some of the lamps are alive |
| palette vs the contrast law | family: `#142016`→`#b0ab7d`; accent `#e2b048` "well-light / lamp gold." The reference's teal→green→gold gradient reconciles as: core = **the biome accent, lamp gold `#e2b048`** — the hearthwheel claims the twilight flora accent slot (currently unclaimed; the kelp set, unauthored, is hereby NOT the accent); middle rings = family greens (`#2c4028`/`#52603a`); **the reference's teal rim is dropped to a family green-grey** — teal would be a second saturated hue and the ratified law says one family + one accent. ⚠️ Flagged: the owner's reference shows teal; if he wants it, the law needs his overrule for this species |
| ecology / scale | medium bin (a rosette ~1.5–2 cells visual); solitary-to-sparse on banks, denser in Compact plots (hand-placed rows, sweetline precedent); Graphic_Random 3 variants, radially symmetric (repetition-safe by construction) |
| glow note | a literal engine glow (CompGlower on a plant) is mod-pattern territory — same open question the template logged for twinkling flora (TWINKLE_FLORA_SPIKE_1). v1 ships the glow painted in the sprite; a real light rides the spike's verdict |

---

## 9. The sissal — the Twilight venom worm (owner seed #4)

Reference: `twilight_venom_worm_ref.png` — iridescent segmented worm, translucent
pink/green/gold, branching stalked appendages tipped with bulbs, feathery blue
gill-fans at the head. Beautiful-and-wrong.

| field | value |
|---|---|
| defName / label / nickname | `RUT_Sissal` / `sissal` / "jewelworm" — the nickname is the warning: the pretty one |
| name grammar | `ss-` sibilant — the bestiary's venom clade root, soft-bodied vowel ending per the fish commission's water register. Collision-swept (saal, vhessa distinct) |
| the register | "don't touch the pretty thing": low flee-threat, severe if touched. It never chases; it barely moves; every casualty walked into it |
| placement | **the lamplit banks' shallows and margins** — where divers and fishers actually reach and the Compact works (§7 river-bank harvest, §8 tended plots): the hazard lives exactly in the biome's richest gathering ground, which is what makes it matter. Not the dark between: that is ruled the true predator's hunting ground (§4 "one true predator… hunting the shoals in the dark between columns") and the sissal is prey-adjacent clutter there, not a resident. Cited call |
| the predator-stack finding | `review/round2/biome_findings.md` (the_twilight_deep): "five mega-predators over prey of Laa, Yobshrimp, StoneCrab; chain is inverted." The sissal deliberately adds NO apex weight: **small-to-medium band** (bodySize ~0.6, drawSize ~1.2), mid-tier menace by chemistry not mass — a hazard, not a hunter. It slightly thickens the prey side too (the true predator eats sissal; the venom is for the slow world of the banks, useless against a strike from the dark **[INVENTED]**) |
| movement / combat | very slow (crawler, MoveSpeed near the bottom of the animal range); does not flee, does not hunt; retaliates only in reach. `manhunterOnDamageChance` low-not-zero — poke it and it is briefly, locally, nasty |
| the venom mechanic | melee tools deliver **toxic buildup**: the Core hediff `ToxicBuildup` exists and is the vanilla venom currency (toxic fallout applies it). The known vanilla wiring shape is a DamageDef that applies an additional hediff on hit; Biotech's ToxGas is the OTHER route and is rejected here (gas is area denial — wrong register for a touch-hazard, and Biotech-gated per the vhessk brief's ToxCloud finding). 🔴 Build-seat verification owed per house rule: confirm the exact damage-def/hediff wiring against RimSage before XML — the design commitment is only "melee applies ToxicBuildup, scaling to severe with repeated contact"; a small custom DamageDef is acceptable if Core has no clean reusable one |
| severity curve | one touch: sick and slowed. Standing in melee with it: collapse-grade buildup. Kill it from one cell away with a stick: free. The counterplay is written in its own slowness |
| palette vs the contrast law — the accent conflict, resolved | the contrast law (template §8.4, RATIFIED) governs FLORA: one family, one flora accent — and §8 already spends the twilight flora accent on the hearthwheel. The sissal is FAUNA, so the flora slot is not double-booked — but two glowing jewels on one bank would still fight, so the sissal is **value-tamed**: body translucent in family greens/bronze, the iridescence confined to SMALL areas — the bulb tips and gill-fans only, a shifting pink/gold shimmer that reads at one cell and vanishes at zoom (value, not hue, carries its silhouette). The hearthwheel keeps the lamp; the sissal is the glint beside it. ⚠️ Flagged for the owner regardless: if he wants the worm as the biome's showpiece instead, swap the two — but not both |
| product | none worth designing now; a venom-gland harvest is the same open economy call as the vhaal's sting-sacs (§12) |
| art | the reference plan: segmented translucent body, stalked bulb-tipped appendages breaking the silhouette, feathery head-fans. Ban 6 audit: no Earth-nameable read (it is no leech/centipede silhouette — the stalked bulbs see to that) |

---

## 10. The bladderboil — the Scald floater (owner seed #3)

Reference: `scald_bladderboil_ref.png` — a golden, wrinkled, crater-pocked sac: the
DEFLATED state. Inflated, the same body taut and near-spherical.

### 10a. Name and flavor

| field | value |
|---|---|
| defName / label | `RUT_Bladderboil` / `bladderboil` — **the owner's own coinage, kept verbatim.** ⚠️ Noted, not changed: `Alien_Bestiary.md` §1 steers away from English compounds as species names — but the owner named this one at the bench, and his word is the ruling. The bestiary rule survives as the default for names WE coin |
| nickname | "pilgrim's kettle" — it whistles faintly when it vents **[INVENTED detail]** |

**Description (player-facing):**

> A leathery golden sac the size of a head, riding the Scald's boil. When the water
> around it roars it gulps itself full and swells taut, floating high and hard where
> nothing else can live; when it drifts into a quiet margin pool it sighs out through
> its crater-mouths and slumps to a wrinkled bag, half-sunk, resting. Pilgrims call
> them kettles for the whistle they make letting go. They are entirely harmless, and
> the shore-folk net the resting ones.

### 10b. The sheet reconciliation — ruled exception not needed

`the_scald.md` §6 ban 4: *"No macro-life in the boil itself — the walkers live at depth
where it is merely hot; **nothing swims the roiling surface layer but bubbles and
sails.**"* The ban carves its own exception — bubbles and sails — for the ruled
bubble-sailors (§4: jellyfish-analogs riding boiling bubble-lines). **The bladderboil
is written INTO that clause, not as a new exception:** it is the sail register's second
member — where the bubble-sailor rides bubble columns, the bladderboil IS its own
bubble. It doesn't swim the boil; it floats it, inflated. No frozen-sheet amendment
required; the choice "depth-dweller that rises" is rejected as needless — the surface
reading is lawful as-is and matches the owner's words ("floating around the Scald").
Cited call.

The puff/deflate cycle maps onto the biome's real gradient: the boil proper (always
roiling — §5 "the boil never stops") keeps it inflated; the MARGINS (§8: "the margins
hurt and heal" — the gentler shore waters) are where it deflates and rests. Inflation
is its boil-survival trick: taut and gas-filled, it rides above the worst of it,
insulated by its own vapor jacket **[INVENTED mechanism; the admission test it passes
is §4's "thrives in heat that kills everything else"]**. It joins the dung-and-mat
economy (the admission test's second clause) as a surface skimmer of the boil's froth
and floating mat-fragments.

### 10c. Fished AND seen — both routes, argued

The Megakrill precedent is fishing-ONLY (a catch item, never a spawn —
`review/round2/biome_findings.md`: "still a fishing result, never a spawn"). The
bladderboil is the opposite case: the owner's sentence puts it visibly on the water
("floating around the Scald") AND in the net ("can be fished for"). So: **both.**

- **wildAnimals**: an aquatic pawn on Scald water, ambient, innocuous, fully
  non-combat — the visible bobbing population is the point (the Scald's §9 art theme
  lists the sailors' traffic as the readable sky; kettles join that traffic).
- **fishTypes**: a catch item `RUT_BladderboilCatch` in the Scald's fishing table
  (the fish commission §1 already gives the Scald a table: eesh/karrash/saal/muddal —
  this is its fifth line, uncommon bucket). Engine fact from that commission's §0: a
  fish is an ordinary ThingDef in `thingCategories: Fish`; the catch item and the pawn
  are two defs and the engine never links them — the fiction does (you net the
  resting, deflated ones at the margins, which is also why fishing yields them while
  the boil keeps the inflated ones out of reach). Stats per that commission's floater
  register (nutrition 0.10, market 3 — thin food, common filler): anti-exponential
  law kept. ⚠️ One deliberate delta: the Scald is never potable (§6 ban 1, "fouled
  not toxic") — the catch is edible cooked, mirroring the fouled-not-toxic line |

### 10d. The puff/deflate cycle — the honest engine answer

What is NOT engine-supported: a graphic tied to a map/water condition. Life-stage
graphics are AGE-driven (the template's §1 engine survey: sprites scale/swap by growth
and life stage, nothing environmental), so no vanilla route swaps sprites by "is the
water boiling."

- **v1 (recommended, zero C#):** ONE sprite, mid-inflation — taut upper dome, wrinkled
  skirt — so both states read in one body; the description (§10a) carries the cycle.
  Cost: nothing. Loss: the cycle is fictional, not visible.
- **v2 (needs a C# spike):** a small comp swapping two graphics on a timer or on
  water-cell state — the same shape as the already-ruled TWINKLE_FLORA_SPIKE_1
  question (prove the pattern on ONE def, measure tick cost, report). If that spike
  succeeds for flora, this rides its pattern; it is NOT promised here.

### 10e. Numbers and art

Small bin, bodySize ~0.3, spawns in loose groups (kettle-fleets); MoveSpeed minimal
(it drifts; the boil moves it). Palette: the reference's gold kept — it lands inside
the Scald's thermophile-orange accent family (`#e8763a`, anchors file) against the
scald-cyan water family: a fauna echo of the mat-band rainbow, high contrast by the
biome's own scheme. Art plan: the golden crater-pocked sac of the reference, drawn
mid-taut; craters (its vent-mouths) are the identity marks — at review distance the
read is "a gold buoy with mouths."

---

## 11. The Grey Deep floor — one set-piece in three cards (owner seeds #7, #8, #9)

Three references, one image: **the toxic pool, its precipitate rim, and the life
crowding the edge of the poison.** The three cards below are cross-cited as ONE
set-piece — a stillpool is never placed without its rim, and the rim is where the
rimshell beds and the mason-felt meet. The whole risk-reward of the Grey Deep floor
is readable in one glance at it.

### 11a. The mason-felt — the bacterial mats (owner seed #7)

Reference: `grey_deep_bacterial_mat_ref.png` — a pink-ochre, spiky-cusped microbial
carpet on a lightless seafloor.

| field | value |
|---|---|
| name | **mason-felt** (a terrain label, not a species defName — see next row) |
| engine shape | **TERRAIN** — the textbook case of the RULED interaction test (`flora_commission_template.md` §8.3): nobody harvests ONE of it; it is a condition of the seafloor. A Grey Deep floor terrain variant ("mason-felt bed"), cusped texture per the reference. No def, no health bar, no plant |
| one organism, not two (recommended) | `the_grey_deep.md` §4: the pillar-mason is "a crystal-binding film that builds — mineral columns rising from the floor." **The mat IS the pillar-mason's ground phase**: the film at rest is a carpet; where it concentrates, it builds. Mat = the organism resting, pillars = the organism working. One monoculture, zero new lore, and the sheet's word "film" already contains it. This also makes the mat lawful under EITHER cap reading: the sheet's §4 header releases the cap (owner ruling 2026-09-10) but even the old "three residents" text is satisfied — the mat adds no fourth resident, it is the first resident seen whole. And schools/swarms stay banned (§4 note): a mat is neither. ⚠️ The alternative (a second, independent film species) is flagged for the owner but recommended against: it spends a species slot to say less |
| navigation dividend | travel below is pillar-to-pillar (§4, ruled); the mat adds the ground-level read: felt thickness grades toward where the mason builds — thicker carpet means pillars near **[INVENTED, cheap, art-level]** |
| palette — the mate-mark protected | the reference's pink-ochre is **value-tamed into the grey family** (`#171b19`→`#c2c6c0`): a warm-cast mid-grey (ochre hue at very low chroma) so the floor reads organic-warm against the mineral-cold pillars WITHOUT becoming a color. It is argued as an environmental sub-accent at most — because the biome's one saturated color is spoken for and load-bearing: the accent (`#d81f6e`, the giant's mate-mark) is "one point of impossible color approaching through the grey" (§4) and nothing on the floor may dilute that shock. Also audited: §6 ban 4 (no bioluminescent dressing) — the mat does NOT glow, ever |
| build cost | one terrain def + texture when the Grey Deep builds (itself diving-mod deferred, same as §8); this card is design-complete now |

### 11b. The stillpool — the brine pools (owner seed #8)

Reference: `grey_deep_brine_pool_ref.png` — a sharply-rimmed lake-within-the-sea,
milky turquoise, sitting in the seafloor. The real ones kill most of what enters.

| field | value |
|---|---|
| name | **stillpool** — from the sheet's own line (§5: "the pools have shores, and their stillness is the deadliest thing in the biome"); a terrain label, not a species |
| already ruled — this card escalates, it does not add | the sheet HAS brine pools: §6 ban 1 ("No survivable brine-pool entry — no def, gear, or story makes the pools swimmable; harvest happens at their shores") and the §5 line above. This card gives them their body. And the two-tier brine gradient is written explicitly so the pools extend an existing law rather than invent one: **tier 1, ambient** — the biome's water, "brine that hurts, worn as a life condition" (§4, the crusted giant's whole biography): chronic, survivable, the cost of being here. **tier 2, the stillpool** — the same chemistry concentrated past the line: heavier-than-water hypersaline brine pooled in floor basins, a lake under the sea, extremely toxic, unsurvivable (ban 1 restated as physics: denser brine does not mix — you sink INTO it and it does not let the chemistry dilute) |
| engine shape | **TERRAIN** (interaction test: a condition of the ground — nobody harvests a pool) **+ a toxicity mechanic.** What exists vs what needs a spike, honestly: (a) the project has already BUILT damaging water — the Scald's burn-on-crossing values are live (`the_scald.md` §6 ban 3: "the built burn values stand"), so per-cell cost-to-enter terrain is proven in-house; (b) vanilla Biotech's pollution is the closest presence-toxicity precedent (polluted ground applying toxic buildup to unprotected pawns) — the pattern exists, its reuse on a custom terrain is 🔴 build-seat verification against RimSage, not assumed here; (c) the honest v1 given ban 1: entry is not a damage event to tank but a KILL — impassable-to-pawns terrain (deep-water pattern) whose fiction is lethality, with the toxicity mechanic reserved for the SHORE ring (standing on rim cells applies slow ToxicBuildup — the tier-1 brine, concentrated near its source). v1 ships (c); (a)/(b) patterns upgrade it if a spike wants pools you can wade into and die |
| the preservation register — the loot anchor | ban 5 rules "no decay of the encased… preserved forever"; §5 rules "the dead stand where they sank." The stillpool is where that register is DENSEST: real brine pools pickle what dies in them, and this one has been doing it since the sea began. **Proposed as the diver-loot set-piece anchor:** what sank into a stillpool never rotted, never got jacketed by the mason (the brine kills the film too — why the pool floor is bare while the rim crusts **[INVENTED]**), and never got picked — because the two things that work the dead here cannot follow: the ossuary shrimp (§4) has watched every pool's shore and never entered, and the TetnissCrab — the review's "preserved-in-tar scavenger" that "fits the preservation register perfectly" (`biome_findings.md`) — works the tar line, not the brine. So the pools hold the only unworked dead in the biome: the richest, most legible salvage on the floor, visible through the milk, reachable by exactly nobody — until a player brings tooling the biome never evolved. The set-piece writes itself: the shrimp watching from two pillars away as you fish a corpse it has wanted for a century |
| rim halo | the real pools grow white/ochre precipitate rims — kept, and unified with 11a: **the rim IS the mason-felt's edge state**: the film feeding richest at the brine boundary, crusting itself in precipitate as it dies into the overspill **[one organism, same recommendation as 11a — the rim is the mat at its limit; flagged with 11a's identity question]**. Palette: rim bone-white/pale-ochre (family light steps), pool milky turquoise — the ONE place the floor departs the grey family, argued as an environmental sub-accent like the mat: large, still, desaturated-milky, and incapable of moving — so the mate-mark (`#d81f6e`, "one point of impossible color, MOVING") keeps its shock monopoly: the pool is a pale held breath, the mark is a moving scream |

### 11c. The rimshell — the yellow beds at the edge of the poison (owner seed #9)

Reference: `grey_deep_brine_rim_mussels_ref.png` — dense yellow-green shell beds
packed exactly at the pool's lethal edge (the owner's word: "underwater yellow
mussels growing around brine pool").

| field | value |
|---|---|
| defName / label | `RUT_Rimshell` / `rimshell` — ⚠️ NOT labeled "mussel": §6 ban 6 is a frozen hard ban ("no vanilla-Earth organisms by name or read; the shrimp is skeletal-*seeming*, never an Earth shrimp by name"). The owner's bench sentence named the reference image, and the same sheet already shows the pattern for honoring both (shrimp-seeming, not shrimp): the rimshell is mussel-SEEMING. Flagged in §12 in case he wants the Earth name anyway |
| the set-piece line (§7/§8 material for the sheet, offered) | *"Life packed shell-to-shell at the edge of the poison: divers harvest the rim, and the pool keeps the greedy."* A harvestable protein source at the most dangerous spot on the seafloor — the reach-over-the-edge loop: the beds grow densest on the innermost rim cells, where the shore-ring toxicity (11b) ticks while you work. Ban 1 is satisfied to the letter: "harvest happens at their shores" — this is the thing the shore grows to harvest |
| why life crowds the lethal edge | the rimshell farms the boundary: rooted in the rim crust, siphoning the chemical gradient where brine overspill meets sea — the richest chemosynthetic seam in the biome, feeding on the mason-felt's edge bloom (11b's rim) **[INVENTED mechanism; the real-world pattern is exactly this]** |
| engine shape — the route decision | **harvestable Plant-def bed.** Interaction test (RULED): individuals are HARVESTED — a colonist crops A bed → Plant def, the test's verbatim branch. The alternatives, rejected with cites: fishTypes (FISH_BESTIARY_COMMISSION_1 route) fails twice — the Grey carries no fishing table in that commission's seven waters, and a rooted bed is not a catch; the StoneCrab tended-fishery pattern (Twilight banks) is an ANIMAL husbandry loop and the Compact's — the Grey has no tenders and its register is untended. So: wild Plant-def beds, cluster-spawned on stillpool rim cells only (hand-in-glove with 11b's placement), harvest yield a shellfood item |
| economy note | the yield is real food from a lethal place — priced by risk, not scarcity mechanics; anti-exponential discipline from the fish commission carried (yield modest, nutrition ordinary). Whether shellfood is its own item or reuses an existing food class: build call |
| palette | yellow-green kept — the owner's word and the reference — but at mat discipline: ochre-yellow at restrained chroma (a warm smolder against the grey family, brightest thing on the floor BUT static and low-saturation next to `#d81f6e`); the mate-mark keeps the shock slot. Value: beds one step darker than the bone-white rim so the three-part set-piece separates by value — pale rim, dark gold beds, milky pool |
| art | clustered asymmetric shells, mineral-crusted, trap-door seam (de-Earth'd silhouette per ban 6: crusted and lopsided enough that "mussel" is a resemblance, not an identification); Graphic_Random 3 variants, tiling-safe (template §5.4) |

---

## 12. Open questions — the owner's, not ours

1. **The crystal deep-lore thread (§3b):** are the propane crystal pair and the
   Lantern Deeps' crystal cast (Gembug/CrystalCrab/Glowtail) one ancient lineage, or
   unrelated convergence? Proposed as an option; nothing built depends on it.
2. **Crystal pair reading (§3a):** one organism with a lifecycle (recommended) or two
   sibling species?
3. **The twilight accent (§8/§9):** hearthwheel holds the lamp-gold flora accent and
   the sissal is value-tamed — confirm, or swap. And: does the hearthwheel keep the
   reference's teal rim (needs a one-species overrule of the ratified one-accent law)?
4. **The hearthwheel's taxonomy (§8):** colonial-animal-read-as-plant (keeps the
   kelp's frozen "only true marine flora" line untouched — recommended) or true flora
   (needs a frozen-sheet amendment at a sitting).
5. **Grey mat identity (§11a/§11b):** the pillar-mason's own ground phase, with the
   pool rims as its edge state (recommended) — or a second film species?
5b. **The rimshell's name (§11c):** "rimshell" honors frozen ban 6 (no Earth organisms
   by name); if the owner wants "mussel" as the label anyway, that is a frozen-sheet
   overrule at a sitting.
5c. **Stillpool entry (§11b):** v1 impassable-lethal (honors ban 1 exactly) — or a
   spike for wade-in-and-die toxic terrain on the Scald burn / Biotech pollution
   patterns?
6. **Venom-harvest economy:** do vhaal sting-sacs / sissal glands / dovvik bladders /
   skerrik chitin become items with recipes, or stay flavor? All four are parked as
   flavor-only defaults.
7. **Bladderboil v2 visible inflation (§10d):** ride the TWINKLE spike's pattern if it
   succeeds, or stay v1 forever?
8. **Lakebed flora cultivation (§5 card 1):** pearlfield ships unsowable by choice
   (mirroring the Blue Desert's ruled ban); is that the owner's intent for the lake
   too?

---

## 13. Sources read for this brief

- Biome sheets: `biomes/the_propane_lakes.md` (§0–§9, bans, admission test),
  `biomes/the_blue_desert.md` (§3 ruled biochemistry, §6 bans),
  `biomes/the_twilight_deep.md` (habitats, frozen rulings, §6 bans),
  `biomes/the_scald.md` (§4 cast, §6 bans, §8 margins), `biomes/the_grey_deep.md`
  (§4 cast, §6 bans), `biomes/the_lantern_deeps.md` (§6 ban 3, crystal-life principle)
- `flora_commission_template.md` (register/card structure; §8 RULED calls: interaction
  test, contrast law, set default 3, size bins)
- `palettes/biome_palette_anchors.json` (the five biomes' families and accents)
- Rosters: `biomes/rosters/the_propane_lakes.json` (fauna, FISH_BY_BIOME_1 no-fish
  ruling, new_defs), `rosters/the_blue_desert.json` (new_defs owed)
- `proposals/propane_gas_deep_design.md` (the six ruled v1 rows; the V-wake creature)
- `review/round2/biome_findings.md` (AuroraSylph arrival + "commission 2-3 natives"
  finding; the twilight predator-stack finding; the Grey cap release; Megakrill
  fishing-result precedent), `review/round2/move_mapping_v2.md`
- `fish_bestiary_commission_2026-09-10.md` (engine facts on fishTypes; register stat
  table; naming registers; the Scald's existing table)
- `creatures/goo_boom_commission.md` (format precedent; the never-guess-a-field house
  rule; ToxCloud Biotech-gating finding)
- `Alien_Bestiary.md` §1 (naming grammar), `design/NAMING_SCHEME_PLAN.md` (RUT_ tier)
- The ten reference images under `creatures/references/` (each viewed)


---

## §13 — Owner card rulings, 2026-09-10 (closes §12)

1. **Crystal lineage: YES, one lineage.** The aviir and the Lantern Deeps crystal cast
   (Gembug, CrystalCrab, Glowtail) share one crystal-life origin expressed in two
   extreme places. Canon thread; codex text may reference it.
2. **Twilight accent: hearthwheel wins, WITH the teal rim** — a ruled one-species
   exception to the ratified one-accent law (§8.4 of the flora template). Sissal's
   iridescence stays confined to bulb-tips as drafted.
3. **Name stands: rimshell.** "Mussel" stays out per frozen ban 6; mussel-seeming
   silhouette is the recognizability channel.
4. **Harvest economy: COMMISSION THE ITEMS NOW** (owner overrode the flavor-only
   recommendation). Real item defs + recipes designed in this wave — sissal venom,
   vhaal stingers, bladderboil bladders, and natural extensions. Addendum §14 owed.

---

## 14. The harvest-item economy — commissioned per §13.4 (discharges §12.6)

Design briefs, no XML. Every item: what it is · how obtained · ONE primary use ·
market posture · the existing item it must NOT duplicate. 🔑 **Downstream
reconciliation point: `ECONOMY_TRADE_SWEEP_1`** (BENCH queue: the full
what-is-sold-where sweep at the end of the world sweeps) — every market posture below
is a proposal that sweep ratifies or reprices; nothing here pre-empts it.

**Duplication survey done first** (the campaign's existing adjacent economy, read
before inventing): the Armoury carries an ABSORBED KOTOR poison system —
`guy762_Poison_saber` hediff (`src/RimStarWars/Armoury/Defs/Absorbed_KotorCore/HediffDefs/Absorbed_KotorCore_Hediff_Poison.xml`)
plus ModularWeapons2 melee poison-upgrade parts (`Absorbed_Kotorcore_ModularWeapons2_*`)
— so a new venom-coating SYSTEM would be a duplicate. The crystal economy is ruled and
Deeps-gated: pyrinth (orange lighting family), kyber (crafting-only, `KYBER_TRADE_PLOT_1`
illegality owed), lanternstone (`BMT_ResourceBlueCrystal` — volatile, blasting-grade)
(`design/Jawa/mods/crystal_mods_inventory.md`, CRYSTAL_INGEST_EXECUTION_1 closed).
ManyWaters ships water-bottle items (`RM_ColoredWaterBottles`). Chemfuel is vanilla's
fuel currency, and the Blue Desert §7 already rules wild flora/fauna fuel as
"a chemfuel windfall."

### 14a. Sissal venom sac — `RUT_SissalVenom`

- **What/how:** a translucent gland taken by butchering a sissal corpse (small yield,
  1–2 **[INVENTED counts]**).
- **Primary use — feed the existing system, don't fork it:** the reagent for the
  Armoury's ALREADY-ABSORBED KOTOR poison melee-upgrade path, which currently has no
  in-world material provenance — its upgrade recipes gain a sissal-venom ingredient
  cost at build. One recipe edit, zero new mechanics, and the Twilight banks become
  the named source of every poisoned blade on the planet.
- **Market:** tradeable, modest — spacer/Compact demand; the sweep prices it.
- **Must NOT duplicate:** `guy762_Poison_saber` and the ModularWeapons2 poison parts —
  this item is their INPUT, never a second coating/hediff system. A medicine-precursor
  use was considered and dropped: kolto (`KoltoTank`, same absorbed pack) already owns
  the exotic-healing slot.

### 14b. Vhaal stinger — `RUT_VhaalStinger`

- **What/how:** the hollow arm-tip barb, recovered from a killed vhaal (building
  leavings; 1–3 per stalk **[INVENTED]**).
- **Primary use — COMPONENT, not trophy:** the tip material for the ruled
  ignition-safe weapon register — `propane_gas_deep_design.md` row `saturation-heist`
  (v1, owner verbatim): *"primitive javelains and catapults. Strictly non-flammable,
  non-temperature-based… Vibro-weaponry."* A stinger-tipped javelin/spear recipe: a
  cold-chemistry weapon usable inside saturation zones where everything thermal is
  suicide. Trophy value rides for free in MarketValue; no separate trophy def.
- **Market:** tradeable (a curiosity off-world, a tool on the nightside).
- **Must NOT duplicate:** the sissal path (14a) — the stinger's sting chemistry does
  NOT become a second poison reagent; its weapon carries the burn-cold flavor as
  description, damage stays ordinary Sharp **[INVENTED restraint, keeps one venom
  system on the planet]**.

### 14c. Bladderboil bladder — `RUT_BladderboilBladder`

- **What/how:** butchery of the bladderboil PAWN (the fishTypes catch item stays a
  thin-food floater per §10c; the bladder comes only from real corpses — fishing
  yields food, hunting yields the organ **[INVENTED split, keeps the catch item
  anti-exponential]**).
- **Correction on the waxblood tie, honestly:** the bladderboil is SCALD fauna —
  water-chemistry thermophile under §4's dung-and-mat admission test, NOT waxblood
  (§1's scope is the hydrocarbon nightside). Its bladder holds gas and heat, not
  fuel; it has no chemfuel path and claiming one would be wrong-biome chemistry.
- **Primary use:** a heat-proof organic vessel — the **kettle-skin**: a primitive
  insulated container/canteen that carries boiling water safely; component for the
  pilgrim still fiction (§3's ruled distillation chain — the Scald boils fouled, the
  breath is clean).
- **Market:** campaign-local trade (pilgrim economy); the sweep decides if it travels.
- **Must NOT duplicate:** ManyWaters' `RM_ColoredWaterBottles` family — the
  kettle-skin is the heatproof/primitive tier or an INGREDIENT for still/canteen
  recipes, never a parallel bottle line. Flagged by name for ECONOMY_TRADE_SWEEP_1.

### 14d. Aviir shard — `RUT_AviirShard`

- **What/how:** shatter-butchery of an aviir; harvest of an aviir crown (§3c).
- **Primary use — the tap component:** tap-grade piezo crystal, riding §13.1's
  one-lineage ruling: the same crystal life the Deeps grows, expressed cold — and the
  lake's expression harvests CHARGE (§3b piezo income). It is the component the
  **electrojet tap** (`the_propane_lakes.md` §7, ruled building) wants: tap recipes
  and surge-protection upgrades take aviir shards at build.
- **Market:** **campaign-only for now** — NOT trader stock until ECONOMY_TRADE_SWEEP_1
  rules, because that sweep already owns "Deeps-gated crystals as expensive trader
  stock" and a second crystal entering trade must be priced beside them, not around
  them.
- **Must NOT duplicate:** lanternstone (`BMT_ResourceBlueCrystal` — ALSO a blue
  glowing crystal: the collision risk found). Differentiation ruled into the def:
  aviir shard is inert-stable and non-volatile (no blasting use, no glow-furniture
  family — pyrinth owns lighting, lanternstone owns volatility) and carries nothing
  of kyber (no Force content, `FORCE_POWERS_ARE_V2_1` untouched).

### 14e. Rimshell — `RUT_RimshellMeat` + `RUT_RimshellShell`

- **What/how:** harvesting a rimshell bed (§11c Plant-def harvest) yields both.
- **Meat — primary use: food.** Raw shellfood, ordinary nutrition per the fish
  commission's anti-exponential law; the risk-priced protein of the pool rims. NOT in
  `thingCategories: Fish` (it is harvested, not fished — no fishing table exists in
  the Grey) **[engine-posture call for the build]**.
- **Shell — primary use: craft material,** small: inlay/ornament recipes (the
  Compact's trade-jewelry register **[INVENTED]**); one use, not a stuff.
- **Market:** meat campaign-local (it rots); shell tradeable as a minor luxury.
- **Must NOT duplicate:** the FishBase catch items (32 species already commissioned —
  the meat must not read as catch #33) and StoneCrab's tended-fishery yield.

### 14f. Hearthwheel rim — `RUT_HearthwheelRim`

- **What/how:** cropping the rosette's regrown outer ring (§8 tended plots; the plant
  survives harvest — leaf-vegetable pattern).
- **Primary use: food** — the banks' vegetable delicacy, the flora counterpart of the
  StoneCrab fishery; cooked-meal ingredient, mild mood bonus as the "lamplit meal"
  register **[INVENTED]**.
- **Market:** Compact trade good (they sell water; this is the thing they DON'T sell
  cheaply); build deferred with the biome (diving mods).
- **Must NOT duplicate:** the kelp economy — kelp is ruled "food, fiber, and the wet
  lattice-timber" (`the_twilight_deep.md` §4): staple vs delicacy; the hearthwheel
  ships food-only, no fiber, no timber.

### 14g. Natural extensions (per §13.4 "and natural extensions")

- **Cold wax** (§1's generic waxblood butchery yield, all nightside species):
  commissioned as ONE shared item, `RUT_ColdWax` — refines to chemfuel at a
  cold-handled recipe (the Blue Desert §7 "chemfuel windfall," made mechanical). It
  CONVERTS to chemfuel, never competes with it; warm storage detonates it (§6 ban 3
  behavior carried on the item).
- **Dovvik bladder** folds into cold wax (a dovvik butchers into more of the same
  item, no bespoke def). **Skerrik chitin scrap is CUT** — §2c's open question closed
  by this pass: it yields cold wax only; a fourth micro-material earns nothing.
- **Sting-sacs** (§4c's vhaal option) fold into 14b's stinger — one drop, not two.
