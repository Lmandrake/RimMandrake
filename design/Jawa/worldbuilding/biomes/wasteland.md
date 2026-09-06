# The Wasteland — definition sheet

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

## 0. The measurements everything rests on

MEASURED 2026-09-05 off `world/ASHKARR_WORLDMAP_tiles.csv`: **1,699 tiles**, and the def
straddles the terminator (arc 75→130, median 100 — the sun 10° *below* the horizon). The
per-region stats split into three families:

| family | regions | arc | temp | elev |
|---|---|---|---|---|
| **Dayside basins** | Salt, Pan, Glass Reach, Blight, Cinders, Scour | 73–92 | +10…+27 °C | low (5–32 m) |
| **The margin** | Ashen Wastes, Nightspill | ~101–108 | −9…−1 °C | mid |
| **The dark scour** | Sunreach, Cinderdark, South Crags, Gray Crags | 110–129 | −13…−35 °C | high (200–544 m) |

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
wash, history doesn't decay — and for a thousand years since the war it has also been the
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

Most life is **bizarre, mutated, small, and pathetic** — ordinary lineages being slowly
ruined: vermin at the contamination edge, born wrong, short-lived, visibly suffering.
Dangerous the way a cornered sick thing is dangerous, never the way a predator is. They are
the biome's moving proof that this ground damages everything it touches.

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
5. 🔴 **No rain** (planet-wide, R-H1).
6. 🔴 **No spoilage-dependent content** — rot is near-zero here; a mechanic that assumes
   normal decay is a violation.
7. 🔴 **Plasma storms never occur outside the terminator families** (elsewhere: ash storms
   and radiation halos only).
8. 🔴 **The recognizability rule applies**; the Star Wars icon carve-out protects icons.

## 7. Uniquely available

- **Preservation** — the planet's larder and archive: cold, sterile, salted; nothing rots.
  With the caveat in §5.
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
- 🔴 **Plant-vault ore — the cursed prize.** The sequestration flora manufactures the
  richest concentrated fuel deposits on the planet. Mining them is exactly what the Junkers
  do and exactly what reopens the wound.
- **The tipping fee** — the one biome with an income stream attached to its awfulness.
- **The exhumation lottery** — post-storm prospecting, the map re-dealt.

## 8. Inhabited objects

### The Junkers — crude sovereigns of the dump (owner's ruling)

It is usually the Junkers who are foolish enough to venture in, extracting usable nuclear
(or worse) fuel in specially adjusted warcaskets — and dying at it more often than anyone.
They **claim ownership of the planet's largest dump** and charge for the *rite* of dropping
waste here, making meager credit off a claim that is legally absurd and universally honored,
because nobody else wants to enforce anything in a Wasteland.

🔴 **They are digging up the very plants that are crusting over the poison** — ripping the
sequestration vaults for their dirty reactors and weaponry, reintroducing buried
contamination into circulation. And **their denial about the Throat is institutional, not
stupid**: their entire economy is the tipping fee; admitting the hazard ends the dump.

### The mutator/injection palette (the one-def ruling, made concrete)

| family | mutators & Inhabited injections |
|---|---|
| **Salt basins** | hypersaline pools, salt crust, brine-battery fauna, dead-river termini, drowned cargo |
| **War ground** | vitrified craters, trench systems, buried arsenals, crashed hulls, buried crimes |
| **Fallout scour** | ash dunes, storm-exhumation sites, radiothermal dens, rib-vaults, the stormwall glow |
| **Terminator pockets** | trapped enrichment, plasma storms, the oldest battle ruins, dead sarlacc throats |

### ⭐ The Glowing Throat (working name — owner's pick owed)

One dead sarlacc has had so much hideousness thrown down it that **an unholy glow now rises
from it**, and the ground sometimes trembles as though it were moving or groaning. 🔴 **It
is not alive and not undead, despite the rumors** (owner's ruling — the trembling is gas
pockets and settling mass; the Junkers' "it's just settling" is technically true and
completely beside the point). A thousand years of the worst casks are **mingling, changing,
reacting** into a serious regional hazard: potentially explosive, and potentially able to
vent toxins high enough into the atmosphere to **poison a sizeable part of the world**. The
Junkers refuse and refute all of it.

### Everything else

- **Roads-of-shame** — the waste caravans, the only regular traffic, converging on the
  Junker toll gates.
- **Rib-vaults** and the other dead sarlacc throats (bunker, vault, dungeon, the dump's
  dump).
- **The buried crimes** — a thousand years of things hidden here *because* nothing rots and
  nobody looks, all perfectly preserved.

## 9. Artistic theme

**"A just-lost sunset, flickering with wrathful lightning."**

- **Light:** the dark families are lit by the stormwall's permanent glow on one horizon —
  sunset afterimage, aurora-halo storms, lightning flicker. The basins are the opposite:
  blinding salt-white under a low sun. Point-sources of *wrong* light punctuate both: the
  radiotroph groves, the warm dens, the Throat.
- **Palette:** salt white, ash grey, vitrified black-green, brine-pool mineral color — and
  the sickly radiances against it.
- **Silhouette language:** horizons of nothing, then one enormous thing — a rib-vault, a
  dead hull, a throat mound. Architecture exists here only as remains.
- **Fauna reads as pathos**: the wildlife should look like suffering, not menace.
- **Sound:** wind over crust; Geiger-analog clicks as the biome's heartbeat where the
  player has the instrument; the rumor-tremor near the Throat.

## 10. Campaign hooks (owner-authored 2026-09-05 — candidate arcs, none built)

- 🔑 **The Throat as the environmental doomsday clock**, and the faction triangle around
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
  4. **The volatiles** — the nightside holds `AB_PropaneLakes` (554 tiles, MEASURED). A
     bleeding reactor core dropped into cryogenic propane ignites — and a sustained melt
     could be **how the players breach the sealed research station holding active
     Assailants.**
  5. **The Slime experiment** (owner, 2026-09-06 — `the_slime.md` §7): scoop tons of the
     living archive onto the gravship and pour it down the Throat — likely killing what
     you poured, maybe neutralizing the pit, with genuinely unknown results below. The
     only option that is an experiment rather than a verdict.

---

## Owed

- **Names, owner's pick:** the Throat's true name; the radiotroph flora, the excretors, the
  radiothermal solitaries, the brine-battery creatures; the halo-storm and plasma-storm
  player-facing names.
- **Engine feasibility pass:** RimWorld has no native radiation — Biotech's pollution
  system (wastepacks, polluted terrain, tox resistance) is the obvious spine and is nearly
  this biome verbatim; needs a dose/geiger layer, the three storm weather defs, and the
  storm map-reshuffle (mutator churn on a frozen world needs its own tooling and its own
  ruling on scope).
- **Def tails:** 19 tiles at arc < 60 (min 37.1, up to 54 °C) look mislabeled — same
  instrument as the shrubland mend; fold into `WORLDMAP_DESERT_BAND_REPAIR_1`'s session.
- The tipping-fee economy and the waste-caravan traffic want faction-spec wiring
  (`FACTION_SPEC.md`: Junkers, Wildsteam, Deepwater).
