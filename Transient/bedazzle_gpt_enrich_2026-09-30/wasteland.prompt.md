You are a senior game designer consulting on a RimWorld mod campaign. The owner wants recommendations to ENRICH one biome that has already been through a design sitting. Be concrete, vivid and buildable in RimWorld 1.6 (XML defs, C# comps, Harmony, incidents, map components, weather, sounds).

BIOME: The Wasteland

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
- 2026-09-28: Volley turn 2 rulings, owner typed this session (recorded under BENCH after a guard quote-match refusal; his message is in the session transcript verbatim): FULL DONOR REPLACEMENT yes; register = 'ugly warty life that was already tough enough to survive the waste products and survive if not thrive... creatures that already ate the waste of other beings, survived extreme environments' (survivors, not sufferers - reshapes the sheet's pathos read). The Throat's true name = THE PIT. Cask bay approved. Warcaskets REDEFINED cross-cutting: very resistant to extreme temps + vacuum + toxins, an alternative to space suits and ocean access, but very slow, bulky, prone to failure under compound threats - 'a primitive tank around a person'. Living furnace approved + extended to pollution emission/consumption/usage creatures; interdependent cargo-bay waste-ecology allowed emergently. Excretor ranching absolutely. Bezoar Colossus loved, hardened shell of waste/scavenge debris/bezoars, TWENTY CELLS WIDE. Ash exhumation reuses the MovingDunes mechanism. Dose layer: radiation AND pollution, mostly the pollution mechanism.
- 2026-09-28: Volley turn 4, owner typed: 'Full accept. Bedazzled!' - the whole turn-3 package stands: Middenshell name, brine label-only renames (defNames frozen for the canonical save), full name map, warcasket suit class as its own cross-cutting ticket with the ocean-access-vs-ship-only reconciliation as stated, processor family, MovingDunes-mechanism exhumation, pollution-first dose. Commission fires now.
- 2026-09-28: DURABLE RECORD of the owner-accepted name map (Full accept, 2026-09-28), in case the commission agent's in-flight work needs re-running: PORTS ParagonRat->Scumrat, Molebear->Slagmole, Spidercat->Scabspinner, Toxalope->Boilhide, Beetlefleet->Middenbeetle, Swarmling->Gristleswarm (+Soot variant), Terramorph->Gravelgut; FLORA ToxiGrass->Scumgrass (+Tall), WeepingToxberry->Pusberry, ToxiBulb->Boilbulb, PoluxBush->Wartshrub, vanilla rows stay; NEW Sloghog (ranchable excretor->bezoars), Sootgrazer (ash->fuel bricks), Smolderback (living furnace), the Middenshell (20-cell giant on TitanicCreatures, corpse=bezoar quarry), Cinderfelt (fresh-ash marker plant); brine trio defNames FROZEN, labels only: drazz->brineleech, tekk->sparkcrab. Commission agent spawned 2026-09-28 writing wasteland_survivor_cast_2026-09-28.md + wasteland_survivor_cast.csv. Dredgewing flyer OFFERED to owner, UNANSWERED.
- 2026-09-28: Close-out ticketed 2026-09-28: sheet amendment landed on wasteland.md (register revision, new natives incl the 20-cell Middenshell, THE PIT name, MovingDunes exhumation + pollution-first dose, warcasket cross-ref); WASTELAND_RULED_CONTENT_1 (cast defs) + WASTELAND_MECHANICS_BUILD_1 (comps/titanic/storms) filed for FOUNDRY; WASTELAND_STORM_WEATHER_DEFS_1 closed as answered. Sitting stays open for the art review (21 jobs in flight).
- 2026-09-28: Grimewing RULED IN - decision taken by question card 2026-09-28 (option: add the carrion-glider flyer). RM_Grimewing joins the cast: wretched half-bald scavenger bird riding storm-thermals, circles fresh post-storm exhumations, real flyer (MaxFlightTime stat form). One def + roster row added to WASTELAND_RULED_CONTENT_1, 3 faced art jobs queued.
- 2026-09-29: Art review DONE by owner (export: Transient/bedazzle_art_sheets_2026-09-28/wasteland/sheet.decisions.json): 14 keep, 6 improve (Boilhide violet/yellow boils; Grimewing darker+pinker+forward knees; Gristleswarm east-facing leg count + sickly-white flesh; Middenbeetle; Slagmole shovel face + ribbed back; Sloghog more alien), 1 regen (Middenshell as huge mineral-shelled tubeworm), plus Scumrat->Scumslider redesign in note. Owner typed: "Lots of removal of terran animals, palette needs more diversity."

THE BIOME'S DESIGN DOCS:
===== design/Jawa/worldbuilding/biomes/wasteland.md =====
# The Wasteland — definition sheet

> 🧊 **FROZEN — `BIOME_FREEZE_FABLE_REVIEW_1`, 2026-09-07.** The rulings in this
> sheet are frozen: **amendments add detail; they never change a ruling.** The
> unfreeze path is an owner ruling at a sitting, recorded on the item that
> changes it; contradiction cards from the freeze review amend under this rule.


_Owner + BENCH, 2026-09-05, written in conversation over three passes. The ladder's zero:
the first truly dead ground. Thematic handle: **no outlet** — and its image: **a just-lost
sunset, flickering with wrathful lightning.**_

🔑 **Read against `forsaken_crags.md` where the regions overlap** (Gray Crags, Sunreach,
Nightspill): the interleave ruling (owner, 2026-09-06) is crag = the standing relief that
shatters the wind, wasteland = the drained flat between — no border drawn, no tile churn,
and never regularized into bullseye rings.

🔑 **Read against `arid_shrubland.md`.** The shrubland is where the land goes mild and life
becomes the danger; the Wasteland is the opposite inversion — **the land itself is the only
danger, and there is almost nothing alive to fear.** You can sleep here without a watch. The
ground will still be killing you while you do.

⭐ **AMENDMENT 2026-09-28 (owner, `WASTELAND_BEDAZZLE_SITTING_1` — the bedazzle
sitting; rulings owner-typed on its ledger, cast details in
`wasteland_survivor_cast_2026-09-28.md`, the cast bible):**
(1) **Register REVISED — survivors, not sufferers.** Verbatim: *"ugly warty life
that was already tough enough to survive the waste products… creatures that
already ate the waste of other beings, survived extreme environments."* Names
are English ugly-tough (Scumrat, Boilhide, Sloghog…), never invented-exotic,
never Star Wars; §4's and §9's old pathos read is corrected in place below.
(2) **Full RM_ development ruled** — the whole donor cast replaced outright
(defs, names, art), not patched; the accepted name map is in the cast bible.
(3) **New natives admitted to §4**: the **Sloghog** (ranchable excretor —
bezoars), the **Sootgrazer** (ash-eater — fuel bricks), the **Smolderback**
(the radiothermal solitary made flesh), and **the Middenshell** — the biome's
giant, owner-ruled **twenty cells wide** on the TitanicCreatures engine, never
hostile, proximity-dosed, its corpse a permanent bezoar-quarry landmark. Flora
adds the **Cinderfelt**, the fresh-ash-fall marker mat. Brine trio: label-only
renames (drazz→**brineleech**, tekk→**sparkcrab**; defNames frozen for the
canonical save).
(4) **The Throat's true name RULED: THE PIT** (§8 corrected).
(5) **Storm mechanics ruled**: ash exhumation **reuses the MovingDunes
mechanism** (this resolves the mutator-churn scope question the Owed section
carried); the dose layer is **radiation AND pollution, ridden mostly on the
Biotech pollution mechanism**.
(6) **Warcaskets redefined as a cross-cutting suit class**
(`WARCASKET_SUIT_CLASS_1`): extreme-temp/vacuum/toxin-resistant, an alternative
to space suits and ocean access as TERRAIN survival (sea floors stay
ship-only) — slow, bulky, failure-prone under compound threats, *"a primitive
tank around a person."* Cask bay approved; interdependent cargo-bay
waste-ecology allowed emergently.

⭐ **AMENDMENT 2026-09-29 (owner, `PIT_RENAME_STENCHLANDS_1`):** **The Pit's name
further ruled: THE STENCHLANDS.** The rename request predated confirmation of which
site it meant; the owner confirmed in conversation that it is this sitting's Pit (the
former Glowing Throat, §8) he meant. Full chain: the Glowing Throat (working name) →
The Pit (ruled 2026-09-28) → **The Stenchlands** (ruled 2026-09-29). §8/§9/§10 below
corrected in place to the current name.

## 0. The measurements everything rests on

MEASURED via `src/RimMandrake/Utils/biome_sheet_stats.py` (canon CSV + the 8 overlay
plans): **1,126 tiles**, arc 37→118 (p10/median/p90 73/**90**/108) — the def now sits
**exactly on the terminator at the median** (sun elevation 0°), not 10° past it. The
low tail is the already-flagged mislabeled 19 tiles (§Owed, `WORLDMAP_DESERT_BAND_REPAIR_1`).
The per-region stats split into three families:

| family | regions | arc | temp | elev |
|---|---|---|---|---|
| **Dayside basins** | Salt, Pan, Glass Reach, Blight, Cinders, Scour | 73–92 | +10…+27 °C | low (5–32 m) |
| **The margin** | Ashen Wastes, Nightspill | ~101–108 | −9…−1 °C | mid |
| **The dark scour** | Sunreach, Cinderdark, Sootreach, Gray Crags | 110–129 | −13…−35 °C | high (200–544 m) |

⚠️ **Amendment (measurement refresh, not a ruling change):** re-measured against the
current world, **Cinderdark and Sootreach now carry zero `Wasteland` tiles** — both
regions have moved off this def since the table above was written (Cinderdark 102 and
Sootreach 159 tiles now register under `BiomeGRimond` instead). The dark-scour row's
region list is stale on that point; its arc/temp/elev columns are not re-derivable from
the per-def instrument (no per-region climate breakdown) and are left as measured, not
recomputed. Also newly present in the current tile set: **~130 tiles now sit in regions
outside all three named families** (Grey Sea, Thornbelt, Ashfall Range, Long Sand,
Twilight Sea, Glare, Pale Flats, Damp, Wither, Kiln, Dew Horn, Dune Sea, The Verge,
Twilight Crags — full region list and counts in `biome_sheet_stats.py`'s output). Flagged
for the freeze review / a `WASTELAND_FAMILY_REFRESH` follow-up, not resolved here.

🔴 **One def, by ruling.** The different wastelands vary **only by the mutators and
Inhabited injections** assigned to each family (owner, 2026-09-05) — the `fall_line.md`
no-new-BiomeDef precedent, extended.

Founding doctrine already in force and honored here:
- **The salt plains are dead river ends** (`ASHKARR_WORLD_DEFINITION.md` hydrology): every
  river branch ends in a dead salt plain — 235 termini, ~1,120 tiles, three hypersaline
  pools, basins sealed from the seas.
- 🔴 **The war-legacy split** (owner, verbatim, in the world definition): the planet carries
  TWO legacies of the old war and they must never merge. `Wasteland` is the **poisoned**
  one — *"contaminated by radiation and more conventional poisoning."* The danger is **the
  ground, the air, the water** — never the wildlife — and ⛔ **anomaly entities may NOT be
  cast here.** The bioweapon class is a different meaning — and since
  2026-09-06 not a biome at all: the Horrors raiding faction, injected nightside dungeons
  and the Overdrive site (`assailant_weapon_remnants.md`); `HorrorWastes` is dissolved.

## 1. What it is

Where the Rakatans used nuclear, radiation and chemical weaponry to devastate the Assailants
(and, later, more modern forces): conventionally toxified, ruined, and left. Where rivers
die, everything they carried is concentrated into salt and brine. Where the sky's exhaust
falls and nothing ever washes. Nothing recycles here — water doesn't leave, fallout doesn't
wash, history doesn't decay — and for all the ages since the war it has also been the
place you throw what nobody wants, because it was already ruined.

Creatures exist and may be dangerous — but **it is not they who did this**. They merely
adapt, struggle, and mostly fail.

## 2. Planetary position

**Multiple regimes × ONE anomaly: concentration with no outlet.** A wasteland is anywhere
the planet drains to and nothing drains from — and there are three drains, which is why the
def scatters instead of ringing:

- **The hydrological drain** — endorheic basins where dying rivers evaporate to salt,
  toxins and brine.
- **The atmospheric drain** — the Hadley cell's high branch carries the dayside's exhaust
  (Pyreland ash, dust, the dry fraction of the stormwall's chemistry) over the top, and it
  falls in the downdraft on the wall's dark shoulder, where no fog or rain will ever wash
  it. The Ashen Wastes and Cinderdark are the planet's chimney soot.
- **The historical drain** — the war's poisons, used and left; plus everything hurled here
  since. The stormwall's odd chemistry brews its own variant in the terminator pockets, and
  nuclear enrichment from the long-dead terminator battles is still trapped there.

## 3. Driving forces

**Concentration without circulation.** Cold, dark (past arc ~95), bone-dry, and chemically
loaded. 🔑 Canon 2026-09-06 (`forsaken_crags.md` §3): the crag country kills the wind's
coherence — laminar flow shatters to turbulence in the crags, so what escapes nightward
over the dark scour carries nothing. Rot runs slow to nothing — without desiccation needing to occur (owner's ruling).
The Hadley downdraft keeps the dark scour under hard, dry, cold outflow; the basins bake
under low sun; the terminator pockets sit in the wall's own fallout and glow.

## 4. How the biology adapted

### The wretched many

Most life is **bizarre, mutated, small — and completely at home** (register ruled
2026-09-28: survivors, not sufferers). Ordinary lineages that were already tough enough:
vermin that ate the waste of other beings, warty, short-lived, visibly marked by the
ground — and doing fine. Dangerous the way a cornered thing is dangerous, never the way a
predator is. They are the biome's moving proof that this ground marks everything it
touches, and that something tougher than the ground got here first.

### The leveraging few — extremophile life at its edge

The few that grow and thrive here are **ODD** — unusual powers and metabolisms that leverage
the radiation and toxicity itself:

- **Radiotrophs.** They feed on what kills everything else — so 🔑 **the vegetation is the
  dosimeter**: growth clusters over buried cores, blast glass and enrichment pockets, and
  the "lushest" ground in a Wasteland is the deadliest. Prospecting inverts — locals camp
  where nothing grows.
- 🔴 **Plants clean; animals only refine** (owner's ruling). The flora heals by
  **sequestration**: pulling mobile contamination out of dust and brine and locking it
  downward into deep root-masses and vitrified nodules. The Wasteland heals **top-down** —
  a walkable crust over a deep that grows hotter. Cleaning means making the poison stop
  moving. An old "recovered" wasteland is a clean crust over a lethal root-vault, and
  digging where the land looks healed is precisely the mistake.
- **The excretors.** Creatures that metabolize contamination concentrate it — and shed what
  they can't use as dense pellets, metal-salt bezoars, plated casts. ⭐ **A kept herd is a
  slow refinery**: graze them on ruined ground and they hand the poison back as a compact,
  handleable object. They extract; they never heal — that is the plants' monopoly.
- **The radiothermal solitaries** — so hot with their own decay they must dump heat to
  live: they haunt the cold dark scour and keep distance from their own kind or cook each
  other (the spacing law returns, driven by heat). A warm boulder in the black country
  means one passed; ⭐ a tamed one is a living furnace that heats a shelter all winter and
  irradiates it the entire time.
- **The brine batteries.** Hypersaline pools over mineral beds are half a voltaic cell;
  what lives in them runs on ion gradients and discharges them as defense. The pool you
  want to mine has an owner, and the owner is a capacitor.

### The unadapted dead

The bones of creatures that did not understand what they wandered into are the monuments —
giant desert megafauna, unaccustomed to danger itself, dead slowly and preserved forever:
**rib-vaults on the horizon**, the only architecture for miles, the traditional ash-storm
shelter (with the traditional price: the bones lie where the dust settles thickest). And a
few **dead sarlaccs** — each one a pre-dug descending throat, foolish enough to have come up
under this ground and grown too close.

## 4b. Weather — the three storms

- **Ash storms (everywhere; ratified, with terrible consequences).** Centuries of
  deposition picked up and re-dealt: blinding, abrasive, conductive — and radiologically
  live. 🔑 **The storm redraws the danger map**: hot dust scoured off one field and laid on
  another; re-survey after every storm, trust no old reading. And storms **exhume** — every
  blow reveals a trench line, a hull, a cache, a crime somewhere, and buries something
  else.
- **Radiation-halo storms (everywhere else the plasma doesn't reach).** An auroral-like
  halo and glow — less violent, ambient radiation raised for the duration.
- 🔴 **Plasma storms (TERMINATOR FAMILIES ONLY** — owner's ruling): charged fallout whipped
  past threshold until the wind itself is radioactive, electric and strong enough to throw
  wreckage. EMP, burn, dose and burial in one weather event.

🔑 **Doctrine-grade note:** on a planet frozen by ruling — one hand-made world, forever —
the Wasteland is the single place the map is **allowed to regenerate**. Storm-exhumation
means "what's out there" is a live question twice a season. The frozen world keeps one
shuffling deck, and this is it.

## 5. Always true

- Nothing recycles: water, fallout and history all terminate here.
- Rot runs slow to nothing, no desiccation required. What you leave, you find again —
  though ⚠️ *you may not want what you left here too long*: caches soak up the ground they
  sit in, radiotrophs colonize them, storms move them.
- The danger is environmental first — ground, air, water — and priced in dose.
- The vegetation maps the danger (radiotroph growth = hot ground), and the flora is the
  planet's only healing process: sequestration, glacially slow, protected by no one.
- Wildlife is marked by the ground: wretched and mutated as the rule, extremophile-odd as
  the exception.
- Junker corpses are more common than anyone else's.
- Past arc ~100 the only light is the stormwall's glow on one horizon — a permanent
  just-lost sunset with lightning in it. Navigation trivial; morale not.

## 6. Never true — 🔴 HARD BANS (linter-checkable)

1. 🔴 **No anomaly entities** (owner's standing war-legacy ruling — they belong to the
   bioweapon biomes, never here).
2. 🔴 **No bioweapon-class lifeforms, and no extension of that class by analogy.** The
   creatures here did not do this; a def framed as an engineered weapon-organism is a
   violation.
3. 🔴 **The wildlife is never the biome's headline threat.** Creatures may be dangerous,
   but any content making fauna the primary danger has misread the ruling: the ground, the
   air and the water come first.
4. 🔴 **No unmarked wildlife.** Everything living here is visibly shaped by the
   contamination — wretched, mutated, or extremophile-odd. A clean, healthy, ordinary
   animal def resident here is a violation.
5. 🔴 **No rain** (R-H1: rain falls only at the greatest altitudes; the Wasteland is
   not one — an earlier "planet-wide" paraphrase here was loose and is corrected).
6. 🔴 **No spoilage-dependent content** — rot is near-zero here; a mechanic that assumes
   normal decay is a violation.
7. 🔴 **Plasma storms never occur outside the terminator families** (elsewhere: ash storms
   and radiation halos only).
8. 🔴 **The recognizability rule applies**; the Star Wars icon carve-out protects icons.

## 7. Uniquely available

- **Preservation** — cold, sterile, salted: nothing here rots, so whatever is buried
  stays exactly as it fell. With the caveat in §5.
- **Salt, glass, brine minerals** — the basins' concentrate.
- 🔑 **War salvage priced in dose** — ground nobody can live on is ground nobody has
  stripped. The dive structure: vac suits, radiation-scrubbing drugs, the dose budget as
  the timer, and medicine that *may or may not* cleanse what you catch. **The prize
  compounds**: every failed expedition adds itself to the hoard — ruined vehicles of past
  attempts, crashed ships that should have chosen differently.
- ⭐ **Warcasket sarcophagi** — a dead Junker in an adjusted warcasket is a sealed
  salvage-within-salvage: suit, tools, and the half-extracted core still in its grips.
- **Excretor refining** — kept herds that hand back concentrated material as bezoars.
- **Radiothermal heating** — the living furnace, at the living furnace's price.
- 🔴 **Plant-vault ore — the cursed prize.** The sequestration flora manufactures
  densely concentrated fuel deposits. Mining them is exactly what the Junkers
  do and exactly what reopens the wound.
- **The tipping fee** — the one biome with an income stream attached to its awfulness.
- **The exhumation lottery** — post-storm prospecting, the map re-dealt.

## 8. Inhabited objects

### The Junkers — crude sovereigns of the dump (owner's ruling)

It is usually the Junkers who are foolish enough to venture in, extracting usable nuclear
(or worse) fuel in specially adjusted warcaskets — and dying at it more often than anyone.
They **claim ownership of the dump** and charge for the *rite* of dropping
waste here, making meager credit off a claim that is legally absurd and universally honored,
because nobody else wants to enforce anything in a Wasteland.

🔴 **They are digging up the very plants that are crusting over the poison** — ripping the
sequestration vaults for their dirty reactors and weaponry, reintroducing buried
contamination into circulation. And **their denial about the Stenchlands is institutional, not
stupid**: their entire economy is the tipping fee; admitting the hazard ends the dump.

### The mutator/injection palette (the one-def ruling, made concrete)

| family | mutators & Inhabited injections |
|---|---|
| **Salt basins** | hypersaline pools, salt crust, brine-battery fauna, dead-river termini, drowned cargo |
| **War ground** | vitrified craters, trench systems, buried arsenals, crashed hulls, buried crimes |
| **Fallout scour** | ash dunes, storm-exhumation sites, radiothermal dens, rib-vaults, the stormwall glow |
| **Terminator pockets** | trapped enrichment, plasma storms, the oldest battle ruins, dead sarlacc throats |

### ⭐ THE STENCHLANDS (true name ruled 2026-09-29, superseding "The Pit," ruled 2026-09-28; "the Glowing Throat" was the working name before that)

One dead sarlacc has had so much hideousness thrown down it that **an unholy glow now rises
from it**, and the ground sometimes trembles as though it were moving or groaning. 🔴 **It
is not alive and not undead, despite the rumors** (owner's ruling — the trembling is gas
pockets and settling mass; the Junkers' "it's just settling" is technically true and
completely beside the point). Ages of the worst casks are **mingling, changing,
reacting** into a serious regional hazard: potentially explosive, and potentially able to
vent toxins high enough into the atmosphere to **poison a sizeable part of the world**. The
Junkers refuse and refute all of it.

### Everything else

- **Roads-of-shame** — the waste caravans, the only regular traffic, converging on the
  Junker toll gates.
- **Rib-vaults** and the other dead sarlacc throats (bunker, vault, dungeon, the dump's
  dump).
- **The buried crimes** — ages of things hidden here *because* nothing rots and
  nobody looks, all perfectly preserved.

## 9. Artistic theme

**"A just-lost sunset, flickering with wrathful lightning."**

- **Light:** the dark families are lit by the stormwall's permanent glow on one horizon —
  sunset afterimage, aurora-halo storms, lightning flicker. The basins are the opposite:
  blinding salt-white under a low sun. Point-sources of *wrong* light punctuate both: the
  radiotroph groves, the warm dens, the Stenchlands.
- **Palette:** salt white, ash grey, vitrified black-green, brine-pool mineral color — and
  the sickly radiances against it.
- **Silhouette language:** horizons of nothing, then one enormous thing — a rib-vault, a
  dead hull, a throat mound. Architecture exists here only as remains.
- **Fauna reads as tough ugly survivors** (register ruled 2026-09-28, replacing the old
  pathos read): warts, plating and mineral crust worn as armor and adaptation — content,
  never pitiable, and never menace either.
- **Sound:** wind over crust; Geiger-analog clicks as the biome's heartbeat where the
  player has the instrument; the rumor-tremor near the Stenchlands.

## 10. Campaign hooks (owner-authored 2026-09-05 — candidate arcs, none built)

- 🔑 **The Stenchlands as the environmental doomsday clock**, and the faction triangle around
  it: the **Junkers** cannot admit it; **Wildsteam** (the wild's partisans, preaching to
  deaf ears) and **Deepwater** both sincerely care about the planet's future habitability
  and have no leverage — ⇒ **the players are the only hands all three can use.** Survey
  dives, venting and stabilization ops, sealing attempts, Junker-brokered access. The one
  questline where alignment runs by conscience instead of tribe.
- 🔴 **The waste run — the gravship disposal dilemma.** The players can haul the terrifying
  waste elsewhere, but can never leave the planet. Every destination is a moral verdict:
  1. **Drop it on the Empire** — an act of war dressed as sanitation. Does the planet
     really want to declare WAR on the Empire?
  2. **Freeze it on the cold side** — the honest coward's option.
  3. **Entomb it on the remaining Assailants** discovered there — *the Rakatan solution*,
     re-enacted by the players with better intentions.
  4. **The volatiles** — the nightside holds `AB_PropaneLakes` (2,531 tiles, MEASURED). A
     bleeding reactor core dropped into cryogenic propane ignites — and a sustained melt
     could be **how the players breach `ANCIENT_WAR_LAB_1`, the sealed research station
     holding live, trapped, studied Assailants** (owner-reconciled 2026-09-07: this is
     the same site as the propane-lakes war lab, `the_propane_lakes.md` §8 — not a
     second station). The dark tower at the Scald (`SCALD_DARK_TOWER_1`) is a different
     dungeon with a similar theme; do not conflate the two.
  5. **The Slime experiment** (owner, 2026-09-06 — `the_slime.md` §7): scoop tons of the
     living genetic database onto the gravship and pour it down the Stenchlands — likely killing what
     you poured, maybe neutralizing the pit, with genuinely unknown results below. The
     only option that is an experiment rather than a verdict.

---

## Owed

- **Names, owner's pick:** the halo-storm and plasma-storm player-facing names. (The
  Stenchlands (Throat → Pit → Stenchlands), the excretors, the radiothermal solitary and
  the brine-battery creatures were all named at the 2026-09-28/2026-09-29 sittings — see
  the amendment blocks and the cast bible.)
- **Engine feasibility pass:** RULED 2026-09-28 — the dose layer rides Biotech's
  pollution mechanism (radiation AND pollution, pollution-first), and the storm
  map-reshuffle reuses the MovingDunes mechanism. Build: `WASTELAND_MECHANICS_BUILD_1`
  (the three storm WeatherDefs ride it too).
- **Def tails:** 19 tiles at arc < 60 (min 37.1, up to 54 °C) look mislabeled — same
  instrument as the shrubland mend; fold into `WORLDMAP_DESERT_BAND_REPAIR_1`'s session.
- The tipping-fee economy and the waste-caravan traffic want faction-spec wiring
  (`FACTION_SPEC.md`: Junkers, Wildsteam, Deepwater).


===== design/Jawa/worldbuilding/biomes/wasteland_survivor_cast_2026-09-28.md =====
# The Wasteland survivor cast — full RM_ replacement bible

_DESIGN subagent under `WASTELAND_BEDAZZLE_SITTING_1`, 2026-09-28. Owner rulings
(recorded on that item's ledger, 2026-09-27/28): the Wasteland's donor cast gets FULL
RM_ replacement — new defs, names, art, no patches. Register: **"ugly warty life that
was already tough enough to survive the waste products… creatures that already ate
the waste of other beings, survived extreme environments."** SURVIVORS, not
sufferers — English ugly-tough names, never invented-exotic, never Star Wars. The
name map below is OWNER-ACCEPTED VERBATIM ("Full accept"); no defName collisions
found (repo-wide grep, sanity-probed), so every name ships unchanged._

_Read with `wasteland.md` (frozen sheet). §9's "fauna reads as pathos" is REVISED by
the register ruling: these read as tough ugly survivors, not suffering victims. All
§6 hard bans honored per entry below._

## 0. Contents

- §1 Scope, sources, what stays untouched
- §2 The wretched many — ported fauna (8 rows)
- §3 The new species — processors and the radiothermal solitary
- §4 The Middenshell — the giant (own section)
- §5 The brine trio — label-only renames (defNames frozen)
- §6 Flora — ports, keepers, and the new Cinderfelt
- §7 Roster wiring summary (wildAnimals / wildPlants, donor rows out)
- §8 Art commission — what is queued, what was found finished
- §9 Proposals tail (flyer niche note)

## 1. Scope, sources, what stays untouched

**Source roster** — `src/RimMandrake/Wasteland/Defs/BiomeDefs/RM_Wasteland_Biome.xml`
(the RM_ standalone mod, `WASTELAND_RM_MOD_BUILD_1`). Every donor `wildAnimals` row in
it is replaced by an owned RM_ species below; every donor `wildPlants` row that is a
mod's (not vanilla's) gets an owned port. **Vanilla rows stay untouched:**

- `Toxalope` — vanilla **Biotech** animal (already noted in the biome file). Owner map
  says Toxalope → Boilhide, so it IS ported despite being vanilla: the register ruling
  wants an owned, visibly-marked survivor, and a vanilla animal resident here would
  violate §6 ban 4 (no unmarked wildlife) anyway. The vanilla def is simply dropped
  from the roster; nothing patches it.
- `Plant_GrayGrass`, `Plant_TreePolux` — vanilla, stay.
- `Plant_Toxipotato` — **MEASURED vanilla Biotech** (`Data/Biotech/Defs/
  ThingDefs_Plants/Plants_Cultivated_Farm.xml`; no workshop mod defines it). Stays.

**Already-owned content that stays as-is** (no redesign, no rename):
`RM_DosimeterLawn`, `RM_VaultRoot`, `RM_WastelandScorchedStars`, the brine trio
(§5), `RM_BrineDeposit_*`, the brine terrains/hediff. Art status for these: §8.

**Ban compliance frame (§6 of the sheet), asserted once and honored per entry:** no
anomaly entities; nothing framed as an engineered weapon-organism; the wildlife is
never the headline threat — every dangerous entry below is dangerous only by dose,
proximity or defense, never by predation on the colony; everything is visibly marked
by contamination (warts, plating, mineral crusts, boils — never clean); nothing
depends on rain or on spoilage.

**Register:** every description is written as a creature that WON — it eats what
poisons everything else, it is content, its ugliness is armor and adaptation. No
pity language in labels or descriptions.

## 2. The wretched many — ported fauna

All eight are the biome's "wretched many" (sheet §4) re-read through the register
ruling: small, warty, short-lived — and completely at home. Commonalities carry the
donor row's value so the biome's texture doesn't shift. Diets are design targets;
FOUNDRY cribs the donor's statBases as the starting numbers when porting, then
applies the deltas noted. Def files live in
`src/RimMandrake/Wasteland/Defs/ThingDefs_Races/` (one file per species,
`RM_<Name>.xml`, ThingDef + PawnKindDef together), textures under
`Textures/Things/Pawn/<Name>/` at the artpipe's facing names.

### Scumrat (port of GR_ParagonRat, commonality 0.7)

- **Hook:** the rat that made the dump its estate — fat on what nothing else will
  touch, bald in patches, wart-knuckled, and doing fine.
- **Class:** wretched many. **Stats sketch:** bodySize ~0.35, omnivore/carrion
  (OmnivoreRoughAnimal-family food type — an everything-eater), speed brisk
  (~4.4). Breeds fast; the biome's baseline meat animal.
- **Marked by:** hairless wart-clustered hide over the shoulders, salt-stained
  muzzle, mineral staining down the flanks.
- **Danger frame:** none beyond a cornered bite. Never a threat headline.

### Slagmole (port of GR_Molebear, commonality 0.4)

- **Hook:** a barrel of muscle that digs through vitrified crust like frost — its
  claws are worn glassy and its hide is set with embedded grit it never sheds.
- **Class:** wretched many (heavy end). **Stats sketch:** bodySize ~1.6, herbivore/
  root-feeder (digs vault-root and buried growth), slow (~3.0), high armor-blunt
  from the grit hide. Tameable pack-digger flavor text, no mechanic owed.
- **Marked by:** slag-grit embedded along the back like a cobbled road; one milky
  eye is common.
- **Danger frame:** defensive only; revenge-prone if dug out.

### Scabspinner (port of GR_Spidercat, commonality 0.4)

- **Hook:** a patchy-furred ambusher whose webs are half silk, half scab — it
  spins over its own sores and over its burrow mouth alike, and both hold.
- **Class:** wretched many (the closest thing to a predator, kept small).
  **Stats sketch:** bodySize ~0.75, carnivore of scumrats and middenbeetles only
  (predator of the small cast, never man-hunting), speed ~4.0.
- **Marked by:** crusted spinnerets, fur missing in mange-map patches, scabbed
  joints it re-silks daily.
- **Danger frame:** hunts the small cast; flees pawns. Never the biome's threat.

### Boilhide (port of Toxalope — vanilla Biotech row dropped, commonality 0.4)

- **Hook:** the grazing herd animal whose hide is a landscape of sealed boils —
  each one a pocket where its body walled poison off and moved on.
- **Class:** wretched many (herd). **Stats sketch:** bodySize ~0.7, herbivore
  (grazes the toxic flora rows freely — scumgrass, boilbulb), speed quick (~4.6,
  it is still an antelope-shape under the warts). Leather: "boilhide" — ugly,
  cheap, tox-resistant flavor.
- **Marked by:** the boil-field hide, antlers fused into a single mineral-crusted
  club.
- **Danger frame:** none; it runs.

### Middenbeetle (port of GR_Beetlefleet, commonality 0.7)

- **Hook:** a fist-sized beetle that files across the flats in caravan lines,
  hauling scraps of everything back to middens it defends from nobody.
- **Class:** wretched many (detritivore). **Stats sketch:** bodySize ~0.2,
  detritivore/carrion, speed ~3.8, travels in loose lines (herd animal flag).
- **Marked by:** carapace pitted like struck flint, salt rime at every seam.
- **Danger frame:** none. Swarms a carcass, never a colonist.

### Gristleswarm (port of VFEI2_Swarmling, commonality 0.6)

- **Hook:** a knee-high scuttler of gristle and plate that lives in rot-slow
  country by eating what cannot rot — sinew, hide, bone-rind — and thriving on it.
- **Class:** wretched many (pack detritivore). **Stats sketch:** bodySize ~0.3,
  carrion/detritivore, speed ~4.2, spawns in small packs (3–6).
- **Marked by:** exposed gristle at the joints gone leathery and grey, back plates
  crazed like dried mud.
- **Danger frame:** pack defense only; a pack fights back as one when one is hurt.

### Soot Gristleswarm (port of VFEI2_BlackSwarmling, commonality 0.6)

- **Hook:** the gristleswarm of the ash country — the same animal run through the
  chimney: soot-black, grease-sheened, ember-eyed.
- **Class:** wretched many; **plain-modifier variant of Gristleswarm** (owner's
  accepted form: "Soot Gristleswarm", never an invented second name). Same body,
  same behavior; ash-country color and a slightly better cold tolerance.
- **Stats sketch:** as Gristleswarm; ComfyTemperatureMin ~ −30.
- **Def note:** its own ThingDef/PawnKindDef (`RM_SootGristleswarm`) — a variant
  def, not a color channel — because the donor pair were two defs and the roster
  weights them separately.

### Gravelgut (port of AA_Terramorph, commonality 0.2)

- **Hook:** a low armored slab that eats the ground itself — gravel, glass-crumb,
  mineral crust — and passes it as smooth sorted pebbles the locals kick apart to
  read what is buried underneath.
- **Class:** extremophile-odd (the roster's resident oddity; a lesser excretor,
  kept distinct from the Sloghog: it sorts minerals, it does not concentrate
  contamination). **Stats sketch:** bodySize ~2.0, mineral-feeder (dendrovore-style
  diet flag off; custom "eats rock chunk" flavor is text only, mechanically a
  slow-grazing herbivore so no new needs system is owed), speed ~2.2.
- **Marked by:** mouthparts worn to polished stone, hide set with a mosaic of
  swallowed-and-rejected glass.
- **Danger frame:** ignores everything; hits like a wall if attacked.

**Donor removal (per port, same change):** the donor row comes OUT of
`RM_Wasteland_Biome.xml`'s `<wildAnimals>` in the very commit that adds the RM_
row — shorthand element form both directions (`<RM_Scumrat>0.7</RM_Scumrat>`,
never `<li>`). No patches, no `MayRequire` residue: the RM_ mod's roster ends the
change with zero donor references.

## 3. The new species

Owner-ruled, developed fully here. These are the sheet §4 "leveraging few" made
concrete: two excretor/processors and the radiothermal solitary. All three are
economic animals — the biome's uniquely-available §7 columns (excretor refining,
radiothermal heating) given bodies.

### Sloghog — the ranchable excretor (commonality 0.3)

- **Hook:** a warty, barrel-bodied hog that grazes poisoned ground with total
  contentment and periodically coughs up the poison as a stone you can sell.
- **Class:** processor (excretor — sheet §4: "they extract; they never heal —
  that is the plants' monopoly").
- **Behavior/product:** grazes polluted/toxic terrain and the toxic flora rows;
  every ~4–6 days a fed adult produces one **bezoar** — a dense metal-salt lump of
  refined contamination (new ThingDef `RM_ContaminantBezoar`: heavy, valuable to
  the right buyer, mildly dangerous to stockpile in quantity — flavor + a small
  beauty/toxic-environment footnote, not a new hazard system). **A kept herd is a
  slow refinery** — the ranching loop is the point: pen them on ruined ground,
  collect the poison as a handleable object.
- **Mechanic shape:** `CompHasGatherableBodyResource` subclass (the milk/wool
  shape — well-trodden engine ground; FOUNDRY: crib `CompMilkable`, gate the
  fill rate on standing on polluted terrain when Biotech pollution is present,
  else on time). Pollution-CONSUMPTION per the owner's processor ruling: where
  the engine allows, grazing a polluted cell occasionally un-pollutes it — the
  herd genuinely processes, one mouthful at a time. If the un-pollute call proves
  awkward, the bezoar output alone satisfies the ruling's economy half; note it
  and ship.
- **Stats sketch:** bodySize ~1.2, speed ~3.4, herd 2–5, tameness high (it was
  bred-adjacent once, or acts like it). Meat: edible, faintly awful. Leather:
  wart-hog hide, cheap and tough.
- **Marked by:** wart fields down both flanks, tusks capped in mineral crust,
  content half-shut eyes.
- **Danger frame:** none. It is the closest this biome comes to livestock.

### Sootgrazer (commonality 0.25)

- **Hook:** a slab-shouldered grazer that works the ash-fall like pasture — it
  eats deposition itself and presses what it can't burn into brick.
- **Class:** processor. **Behavior/product:** eats ash/pollution deposition
  (mechanically: grazes on ash-family and polluted terrain; same terrain-gated
  gatherable comp as the Sloghog); a fed adult yields **fuel-grade soot bricks**
  (`RM_SootBrick` — chemfuel-adjacent burnable, stackable, sells low but the
  supply is endless where the sky keeps falling).
- **Stats sketch:** bodySize ~1.0, speed ~3.6, small herds, cold-tolerant (the
  ash country is the margin and the dark scour's edge).
- **Marked by:** hide the exact grey of settled ash with darker rain-shadow
  streaks it never had rain to earn — the streaks are grease; nostrils fringed
  with filter-bristle combs.
- **Danger frame:** none.

### Smolderback — the radiothermal solitary (commonality 0.05, rare)

- **Hook:** so hot with its own decay it must dump heat to live — a living
  furnace that haunts the cold dark scour and cannot stand its own company.
- **Class:** radiothermal solitary (sheet §4 verbatim: "a warm boulder in the
  black country means one passed; a tamed one is a living furnace that heats a
  shelter all winter and irradiates it the entire time").
- **Behavior/product:** constant heat output (a `CompHeatPusher` on the pawn —
  the vanilla comp, cheap and proven); constant low toxic/radiation dose to its
  room (Biotech tox-buildup on nearby pawns, small hediff-per-rare-tick comp —
  the DOSE is ambient, never an attack). **Solitary spacing:** its own kind cook
  each other — spawns alone, wanders alone; a mental-map spacing mechanic is NOT
  owed (spawn-alone + lone-wanderer flags read as the behavior; note in def).
- **The trade:** tame one and winter is solved and dosed at once. Heats a shelter
  all winter, doses it the whole time. That sentence goes in the description.
- **Stats sketch:** bodySize ~1.8, speed ~2.6, carnivore/scavenger (eats the
  frozen dead of the scour; hunts nothing bigger than a gristleswarm), ComfyTemp
  min ~ −60 (it brings its own weather).
- **Marked by:** back plates split by glowing seams — the sickly-radiance §9
  accent made flesh; snow never lies on it; the ground steams where it beds.
- **Danger frame:** proximity dose + heat only. It never attacks unprovoked; the
  ban on wildlife-as-headline-threat holds because avoiding it is trivial — it
  is the *keeping* of it that costs.

## 4. The Middenshell — the giant

**THE giant, owner-ruled TWENTY CELLS WIDE.** A colossal, ancient excretor — the
Sloghog's deep-time cousin grown into geography. Its hardened shell is a rampart of
fused waste, scavenge debris and its own vitrified bezoars: centuries of what it
processed, worn as architecture. It is the sheet's silhouette law made animal —
"horizons of nothing, then one enormous thing."

- **Hook:** the oldest survivor on the planet's worst ground, wearing everything it
  ever ate.
- **Class:** giant (excretor lineage). **Never hostile** — it does not fight, it
  does not hunt, it barely notices. **Proximity is the dose:** a radius aura of
  toxic/radiation buildup around the body (same ambient-dose comp family as the
  Smolderback, larger radius, stronger near the shell). **Its walk is the danger:**
  a destruction wake — crushed terrain, flattened structures, snapped flora along
  its path. Getting near it is a choice you pay for; being in front of it is a
  mistake the ground remembers.
- **Engine wiring:** rides the **TitanicCreatures engine** — `RM_TitanicExtension`,
  multi-cell body via Large Pawns, wander-route AI, destruction wake, and
  **corpse-becomes-harvestable-landmark**: a dead Middenshell hardens into a
  permanent map feature, and that feature is a **bezoar quarry** — the shell mined
  like a resource rock for vitrified bezoars (`RM_ContaminantBezoar` + a rarer
  `RM_VitrifiedBezoar` grade), the single richest excretor-refining prize in the
  biome, priced in the dose you take digging it.
- 🔴 **FOUNDRY verification bar (goes in the wiring item):** verify the
  TitanicCreatures engine's maximum footprint tier actually handles a **20-cell**
  body, and REPORT if it does not — the width is an owner ruling, so an engine
  ceiling below 20 is an escalation, never a silent shrink.
- **Spawn shape:** never in `<wildAnimals>` (it is not weather, it is an event) —
  one-per-map-at-most via mutator/incident wiring in the titanic engine's own
  spawn machinery; the dark scour and war-ground families are its range.
- **Stats sketch:** bodySize maximal for the engine tier (target: the 20-cell
  tier's own number), speed glacial (~0.8), diet: everything and nothing — it
  grazes terrain like the processors, at landscape scale.
- **Marked by:** the shell IS the marking — fused slag, hull-plate scraps, ribs of
  something that lost, all grouted in vitrified black-green bezoar glass with
  sickly-radiance seams deep in the crevices.
- **Ban compliance:** never hostile, so never the headline threat (the ground
  still is — the Middenshell just concentrates it); visibly nothing BUT
  contamination; no anomaly flavor — it is an animal, old, not wrong; no
  weapon-organism framing — nobody made it, it simply refused to die.

### Art note

The Middenshell's job renders at **512** so the scale carries in the pixels (the
contagion cast's Meltgut precedent); the read must be "landscape that turns out to
be an animal", walking, all four limbs load-bearing under visible mass.

## 5. The brine trio — label-only renames

`RM_BrinePlate`, `RM_Drazz`, `RM_Tekk` (`Defs/ThingDefs_Items/
RM_WastelandBrine_Items.xml` + the three `RM_BrineDeposit_*` beds). **defNames
FROZEN** — the canonical save may reference them — and the register ruling lands as
**label-only renames** (labels + descriptions' first noun; deposit-bed labels
follow):

| defName (frozen) | old label | new label |
|---|---|---|
| `RM_Drazz` | drazz | **brineleech** |
| `RM_Tekk` | tekk | **sparkcrab** |
| `RM_BrinePlate` | brine plate | brine plate (stays) |

Deposit beds re-label to match: "brineleech bed", "sparkcrab bed"; descriptions
swap the old nouns in place. Mechanics, stats, hediff, terrains: untouched.

**Art finding (checked, per brief):** `RM_Tekk`'s PNG is a byte-copy of
`RUT_Hardwood.png` — a wood resource icon, not sparkcrab art; `RM_Drazz` and
`RM_BrinePlate` still point at an Alpha Biomes donor texture
(`Things/Plants/AB_CrystalHorn/AB_CrystalHornA`) that does not resolve on a
standalone load (the file's own REMAINS note calls for an art-lane decision).
This commission IS that decision: all three get real item-icon jobs (§8).

## 6. Flora

Def file for the ports + Cinderfelt: `Defs/ThingDefs_Plants/RM_WastelandFlora.xml`
(alongside the existing three). Vanilla rows (`Plant_GrayGrass`, `Plant_TreePolux`,
`Plant_Toxipotato` — vanilla Biotech, MEASURED §1) stay untouched.

### Scumgrass (port of RG_Plant_ToxiGrass, commonality 1.2)

The biome's default green — a wiry, grease-slicked grass that grows on ground that
kills cleaner plants, salt-crusted at the blade tips. Stats: ground-cover grass
family (crib donor statBases), fertilityMin low, fertilitySensitivity 0. Grazing
animals eat it without complaint; that is what half the cast lives on.

### Tall Scumgrass (port of RG_Plant_TallToxiGrass, commonality 0.8)

The same grass where the ground is richest — which here means worst. Waist-high,
sight-blocking, its plain-modifier name per the accepted map. Own def
(`RM_TallScumgrass`), donor pair kept as two rows at donor weights.

### Pusberry (port of AB_WeepingToxberry, commonality 0.2 — tree)

A small tree whose pale berries sit in weeping, wax-sealed sockets — the tree
walls its fruit off from its own sap the way the boilhide walls off poison.
Berries edible processed; raw is a lesson. Tree family stats off the donor.

### Boilbulb (port of AB_ToxiBulb, commonality 0.1)

A ground bulb swollen into a blistered dome, mineral-crusted at the base, faintly
warm to the hand. A forage staple for the cast and a processed-food input for
colonists.

### Wartshrub (port of VRE_PoluxBush, commonality 0.08)

A knee-high shrub whose bark is one continuous wart-field — sequestration in
miniature (it locks what it drinks into its galls; the polux lineage's little
cousin). Galls harvestable as a low-grade chemfuel/chemical input.

### Cinderfelt — NEW (commonality: not a standing row — see wiring)

**A felt-grey mat that grows ONLY on fresh ash fall; the post-storm marker.** The
sheet's exhumation-lottery doctrine given a visible face: after every ash storm
the flats grow a grey pelt, and where the felt is thickest, the fall was — which
is where the survey (and the dose) is. Fast-growing, short-lived, dies as the
fall compacts.

- **Wiring:** not a standing `<wildPlants>` weight — it germinates from the ash
  storm's own aftermath (the storm weather def's post-effect scatters it, or a
  MapComponent seeds it on ash-deposition terrain after the weather ends; FOUNDRY
  picks the cheaper). A token 0.02 wildPlants row is acceptable as a fallback so
  the def is never dead content while the storm wiring lands.
- **Stats sketch:** growDays ~1.5, lifespan short (dies in ~8 days),
  fertilitySensitivity 0, purple-grey felt texture, maxMeshCount 4 mat form like
  the dosimeter lawn.
- **Ban compliance:** depends on ash fall, not rain (§6 ban 5 clean); marks the
  storm the way the dosimeter lawn marks the ground.

## 7. Roster wiring summary

Target roster in `RM_Wasteland_Biome.xml` after the build (shorthand element form
throughout — `BiomeAnimalRecord`/`BiomePlantRecord` custom loaders read node NAME
as the def and node TEXT as commonality; a `<li>` silently discards the def):

```xml
<wildAnimals>
  <RM_Scumrat>0.7</RM_Scumrat>
  <RM_Middenbeetle>0.7</RM_Middenbeetle>
  <RM_Gristleswarm>0.6</RM_Gristleswarm>
  <RM_SootGristleswarm>0.6</RM_SootGristleswarm>
  <RM_Boilhide>0.4</RM_Boilhide>
  <RM_Slagmole>0.4</RM_Slagmole>
  <RM_Scabspinner>0.4</RM_Scabspinner>
  <RM_Sloghog>0.3</RM_Sloghog>
  <RM_Sootgrazer>0.25</RM_Sootgrazer>
  <RM_Gravelgut>0.2</RM_Gravelgut>
  <RM_Grimewing>0.15</RM_Grimewing>
  <RM_Smolderback>0.05</RM_Smolderback>
</wildAnimals>
```

`wildPlants`: donor rows (`RG_Plant_ToxiGrass`, `RG_Plant_TallToxiGrass`,
`AB_WeepingToxberry`, `AB_ToxiBulb`, `VRE_PoluxBush`) replaced at the same weights
by `RM_Scumgrass` 1.2 / `RM_TallScumgrass` 0.8 / `RM_Pusberry` 0.2 /
`RM_Boilbulb` 0.1 / `RM_Wartshrub` 0.08; vanilla rows and the existing RM_ rows
unchanged; `RM_Cinderfelt` 0.02 fallback row (§6). Middenshell: never a roster
row (§4). **Every donor row removal lands in the same change as its RM_
replacement** — the mod ends the build with zero donor `MayRequire` references in
its roster. The `RUT_` twin's patch-added campaign roster
(`UtinniPatches/Patches/WildAnimals_Wasteland.xml`) is NOT this pass's scope; its
donor rows are the absorption campaign's (`MLIE_ABSORPTION_BIOME_WIRING_1`
family), noted here so nobody re-discovers them as this cast's leftovers.

New item defs owed alongside: `RM_ContaminantBezoar`, `RM_VitrifiedBezoar`,
`RM_SootBrick` (§3–§4). C# owed: the terrain-gated gatherable comp (Sloghog/
Sootgrazer), the ambient-dose comp (Smolderback/Middenshell aura), Middenshell
titanic wiring — all FOUNDRY items; **`RM_CreatureBehaviors.csproj`-style
explicit-Compile listing applies if any of it lands in an existing assembly: a
new .cs without a `<Compile Include>` line compiles into nothing, silently.**

## 8. Art commission

CSV: `infrastructure/artpipe/art_lists/wasteland_survivor_cast.csv`, format per
`contagion_grotesque_cast.csv`, `rimflow_item_id=WASTELAND_BEDAZZLE_SITTING_1`,
channel codex, transparent, priority 70. Fauna faced `south,east,north` at 256;
**Middenshell at 512**; flora and item icons single at 256. Style register:
realistic natural-history illustration + grime/wart/mineral-crust texture
language, sheet §9 palette (salt white, ash grey, vitrified black-green, sickly
radiance accents), the true-rear-view north line on every faced job, no camera
words anywhere. Register line on every job: tough content survivor, never
pitiable.

**Pre-queue check (done 2026-09-28, per the owner's existing-art ruling):**
`done/`, `_artsrc/`, `registry.jsonl` searched per subject —

- `rutdosimeterlawn_v1`, `rutvaultroot_v1` — **finished art exists** in `done/` +
  `_artsrc/` (generated for the RUT_ twins, `COMMISSION_LEDGER_CLEANUP_1`).
  **Skipped from this commission.** Owed instead (FOUNDRY): copy the finished
  PNGs into this mod's `Textures/` at the defs' texPaths (`Things/Plant/
  DosimeterLawn`, `Things/Plant/VaultRoot`) — both texPaths currently resolve to
  no PNG in the repo.
- `scorchedstars_v1` — finished (`ART_REGEN_FLORA_WAVE1_QUEUE_1`) and the mod
  already ships `ScorchedStars_a/b.png`. Skipped. (Its Q13 divergent-identity
  regen remains owed on the build item, separately — not silently re-queued
  here.)
- All new cast subjects (Scumrat…Middenshell, Scumgrass…Cinderfelt, the three
  brine icons): **no existing art anywhere** — queued.

Queued: **21 jobs** — 12 faced fauna, 6 single flora, 3 single item icons
(brineleech, sparkcrab, brine plate — §5's art finding).

## 9. The Grimewing — ruled in (decision taken by question card, 2026-09-28)

**The flyer niche is FILLED.** The **Grimewing** — a carrion-finder that rides the
storm-thermals: the biome's exhumation lottery means fresh finds after every storm,
and this wretched, half-bald scavenger bird circling a fresh exhumation is the
visible "the map re-dealt here" marker, the way the cinderfelt marks the fall.

- **Class:** wretched many (aerial scavenger). Per the standing flyer rule it is a
  **real flyer**: `MaxFlightTime`/`FlightCooldown` statBases + race flight fields,
  Locust shape, `canLeaveMapFlying` true (it is a bird; it lairs nowhere).
- **Stats sketch:** bodySize ~0.5, carrion diet, speed ~4.0 ground / flightSpeedFactor
  ~2.5. Commonality **0.15** (`<RM_Grimewing>0.15</RM_Grimewing>` joins the §7
  roster block).
- **Marked by:** patchy moth-eaten feathers over bare warty grey skin, salt-stained
  hooked beak, wing gaps where feathers never grew back.
- **Danger frame:** none — it eats what the storm digs up, never what walks.
- **Art:** 3 faced jobs queued 2026-09-28 (`RM_Grimewing_*` in pending/; row
  appended to the cast CSV). Build lands with `WASTELAND_RULED_CONTENT_1`.


TASK: Give 8 to 12 recommendations that would make The Wasteland richer, more memorable and more distinct, filling the weakest of the nine marks first. Improve and extend what is ruled rather than restarting it. For each recommendation:
- **Name** and a one-line pitch
- What the player sees, hears and feels
- Which of the nine marks it lifts
- How it could be built in RimWorld 1.6 and a rough size (XML only / small C# / large C#)
- Why it belongs to THIS biome and no other

Then list your TOP 3 in rank order with one line of why each. Reply in Markdown, at most about 1500 words. Do not ask questions; do not modify any files.