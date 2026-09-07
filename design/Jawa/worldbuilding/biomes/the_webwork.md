# The Webwork — definition sheet

_Owner + BENCH, 2026-09-06, written in conversation over two rounds and ratified
("Go for it, write it up!"). Defines `AB_FeraliskInfestedJungle` (Alpha Biomes).
**The biome's name is THE WEBWORK** (owner's pick). The species keeps both its names
by standing ruling: **Wyyyschokk** to the galaxy, **Feralisk** on this world
(`Livestock_Trade_Utility_Pets_v1.md` — "leave the name and let the terrain carry
the story"). Thematic handle: **the loom** — and its image: **a green and white
hellscape, silent, owned, and growing.**_

🔑 **Read against `the_greentide.md`** — the sibling green square, answered by
inversion: the Greentide is loud, lawless plenty where *water makes the jungle*;
the Webwork is silent, owned territory where *the jungle steals its water* — first
through parasitic roots, then through the spiders' irrigation. The dayside's three
water-laws (oasis peace / canyon ambush / river war) get a fourth register here:
**occupied.** The truce concept does not even parse in the Webwork; you are not a
fellow drinker, you are prey in someone's ledger.

## 0. The measurements everything rests on

MEASURED 2026-09-06 off `world/ASHKARR_WORLDMAP_tiles.csv` (live re-measure — an
older 534-tile figure in `ASHKARR_WORLD_DEFINITION.md` decayed with the map's
reshaping): **172 tiles, 0 river tiles, 0 water tiles.** Sun median **+50°** (arc
21→54) — more raw energy than the Greentide. Temp median 47.4 °C (36.2..63.5).
Mountainous-heavy: 62 mountainous + 7 impassable of 172; elevation to 1,255 m.
Regions: **Dune Sea 73, Scald Spine 50**, Dew Belt 19, Hollow Verge 16, Anvil 14.

🔴 **The rain is bimodal and it is the biome's skeleton: 99 tiles get ZERO rain;
the other 73 climb to 1,529 mm** — near the heaviest on the planet, on green
mountain shoulders the Contagion could not take (its own sheet: no green squares).
Half this jungle drinks storms. Half drinks nothing — and is jungle anyway. §3
explains how.

Donor inventory (Alpha Biomes, workshop 1841354677): **kept** — movementDifficulty
2 (the worst walking on the dayside), diseaseMtbDays 35 (the sickest air on the
planet), forageability 1.0, and the donor's own gameplay advice, canonized in §7b
("build a walled compound, leave it seldom, and USE the spiders"). **Corrected** —
animalDensity 5.4 inverts to low-but-lethal: this jungle's ordinary wildlife has
been *eaten* (§4b). **Evicted** — the vanilla-Earth zoo (elephant, rhino,
capybara, cobra…). Donor lore adopted: infested jungles expand across a biosphere
when conditions are right, and such worlds get bombarded from orbit with atomics —
which is exactly how the Wyyyschokk homeworld died.

## 1. What it is

The place where the plants grew so dense and thick that **they drank their entire
river** — soaked it up into a thicket of terrible, nightmare plants ever churning
against itself. That is why the map shows a jungle with no water: the water is
*inside*. Above, the high green shoulders drink directly from the edge of the
boiling rain at the mountaintops; below, vast silk irrigation networks drip and
channel the stolen water as far as it can be made to reach. It is eerily silent —
most of the animals have been eaten, and few will enter. Those who do frequently
discover a shadow, seconds before it lands upon them, and know nothing more.

## 2. Planetary position

Mid-dayside, arc 21–54, lobed across the Scald Spine's wet highs and down into the
Dune Sea's edge. The reasoned intersection: **maximum solar energy × a stolen
river × an engineer species.** It can even compete with the Contagion in ferocity
— though in truth it is mostly **UV exposure that keeps the highest peaks clear**.

## 3. Driving forces — a biome-sized creature of shade

One law unifies everything here: **the entire biome is a single organism of
shadow.** The plants churn but cannot stretch far from their stolen source; the
water moves through a dense mat of parasitic roots — shared, or stolen rather —
and then through the spiders' silk gutters; the Wyyyschokk itself is **helpless in
direct sunlight** though strongly heat-resistant. UV caps the biome above (the
bare peaks), and the dry sun cages it on every side (the desert). The Webwork
lives pressed against a wall of light, in the humid dark between — hence the two
halves the rain-measure found: the storm-fed highs are the reservoir, the
irrigated lowlands are the reach, and the silk is the plumbing that connects them.

**Why the jungle exists beyond its water: the Wyyyschokk built the rest.** The
irrigation network is theirs — significantly increasing the range of the terrible
terrain they love. This is not an infested jungle. It is a *plantation*, and every
living thing in it is stock in the owner's ledger.

## 4. The Wyyyschokk (locally: the Feralisk)

Not native. No one knows how they arrived. Their homeworld was sterilized by
atomic fire to stop exactly this. **This is one world they cannot consume** — and
worryingly, their territory is growing.

- **Frame**: as large as an elephant, as massive as a horse — mostly nimble,
  sharp legs. (Implementation: big drawSize over modest bodySize, melee authored
  explicitly — body size never scales damage.)
- **The mouth-loom**: adhesive web-like *enzymes* shot at significant range —
  from the mouth, never an abdomen — spun into extremely durable lines. The
  adhesive is **commandable**: virtually impossible to release, or slick as ice,
  and strong as steel or more. The ranged spit applies **Shokk-bound**: a
  semi-permanent near-immobilization hediff that does not wear off for days
  unless attended medically. Not damage — helplessness. The spider comes back.
- **The mandibles**: crush a human head in a single bite. This is not a spider
  that delicately drinks a husk — it DESTROYS its enemy with terrible strength
  and devours the victim in ripped-off portions. Bones snap; armor breaks; it is
  far stronger than an ordinary human.
- **The legs**: stabbing and cutting weapons — known to cut through a
  Stormtrooper's leg armor in a single slash (the armor-penetration benchmark).
- **The venom** (large prey): injected through the mandibles, attacking the
  nervous system — paralysis and heart attack. It kills thrumbo-class prey by
  cardiac arrest and everything smaller by dismemberment.
- **The web-sense**: they do not dwell in trees but in elaborate webwork laid
  through the *entire ecosystem*. Borderline sentient, they feel an intruder long
  before the intruder suspects the webbing exists, communicate through
  vibrations, summon ambush support, and run coordinated assaults after tracking
  prey for over a kilometer. Ambushers burst from underbrush, underground, or
  above.
- **Fecund and self-limiting**: 1,000 eggs a year — and they are **their own main
  predator** as well as everything else's. An erratic, psychotic intelligence:
  turning on each other as swiftly as they cooperate, honoring no family or
  tribe, wielding only the technology they were born with *(for now)*. Legends of
  them learning to talk exist; none has survived scrutiny (flavor only — never a
  mechanic).
- **The weaknesses**: helpless in direct sunlight and away from high humidity
  (implementation anchor: **the existing high-UV-sensitivity gene** — owner's
  pointer; verify the exact def at build, never guess it). Nothing they do
  overcomes the dry heat of the desert.
- 🔴 **They HATE droids** and preferentially destroy them. The *why* stays
  unexplained — it is scarier as a fact of the place. Consequence: the one
  terrain where a droid force is a liability, and the Free Droid Enclaves know it.
- **Untameable.** Enemy of all, ally to none — seeking slowly to convert all the
  green of the world into their green and white hellscape.

## 4b. The three wars — why the Webwork has not won

- **The anchor-beetles**: great insects of the jungle that hate them
  instinctively, rising up to chew through web anchors and slowly undo the
  networks. Neutral, unbothered — and *herdable*: lure beetles along a route and
  they cut a safe corridor (the living-tool pattern, like the Greentide's
  grazers).
- **The egg-mites**: fist-sized, running the silk to seek out and devour eggs.
  Harmless to a pawn — which makes a mite trail a **living treasure map** to a
  nest.
- **Themselves**: the infighting is why 1,000 eggs a year has not eaten the
  planet.

## 4c. The plants, and the pale flowers

The thicket churns against itself — the explosive-growth engine
(`EXPLOSIVE_PLANT_GROWTH_1`) run in self-consuming mode: gaps open and close,
paths are temporary. And beneath the spiders a strange agriculture has arisen:
frequently coated in sticky pollen and seeds, they sow as they hunt, and colonies
of **great, strangely pale flowers follow their architecture** — the white traces
the web. Fresh blooms mean an active line; withered lines mean abandoned web and
the safe path. The biome's palette is also its map, for anyone brave enough to
read it.

## 5. Always true

- The water is inside: no surface water, no river — a drunk river in a living
  thicket, moved by roots and silk.
- The web is a nervous system; touching it anywhere is being *felt* everywhere
  nearby.
- The jungle is eerily silent — the quiet is not peace, it is ownership.
- Direct sunlight is lethal to the owners; clearings are the only safe ground.
- Only fire provides the kind of protection and offense needed to drive them
  back.
- The Wildsteam are at war here, and pay for mandibles.
- The territory is growing at its margins.

## 6. Never true — 🔴 HARD BANS (linter-checkable)

1. 🔴 **No tamed, traded, or negotiated Wyyyschokk** — no def, quest, or story
   makes one an ally; the talking legends never bear out.
2. 🔴 **No truce language** — nothing here imports the oasis register.
3. 🔴 **No vanilla-Earth fauna or flora** in the rosters (standard eviction).
4. 🔴 **No hyperweave from any source but the Webwork** — a trader stock entry or
   recipe yielding Shokkweave outside this biome's routes violates §7.
5. 🔴 **No web projection from an abdomen** — art and text always use the mouth.
6. 🔴 **No safe dense-canopy cell** — map logic never generates covered ground
   guaranteed free of web-sense; safety exists only in light.

## 7. Uniquely available

- 🔴 **SHOKKWEAVE — the silk IS hyperweave, renamed, and the ONLY way to obtain
  it in the game** (owner's ruling). Superb armor material. Routes in: cutting
  harvestable web (which rings the line you cut), butchering a kill (small
  yield), raiding a nest. Implementation: game-wide rename patch + hyperweave
  stripped from every trader stock table, proven against live trader generation,
  not the XML (`SHOKKWEAVE_SOLE_SOURCE_1`).
- **The eggs** — extremely valuable smuggled offworld; carrying stolen eggs marks
  you to every web you pass. The smuggler's jackpot, priced in risk.
- **The mandible bounty** — the Wildsteam's standing reward for fresh pairs; a
  recurring quest faucet at their seats.
- **The still-burners** — the Wildsteam's belching flame weapons, fueled by
  liquors and oils tapped from the trees and fermented in their stills: one fuel
  item that is also a drink and a trade good. Tap the jungle's trees to burn the
  jungle's owner.
- **The light-moat** (§7b) — the only base-defense of its kind on the planet.

## 7b. Playing the Webwork — the light-moat

The donor's advice, canonized: *build a walled compound, leave it as seldom as
possible, and USE the spiders to your advantage.* But the wall here is inverted:
**a clearing is the fortress.** Cut the canopy, burn a ring, keep it burned — the
owners physically cannot cross open sunlit ground. Fire is architecture, not just
weaponry. The threats to a light-moat are the jungle's own mechanics: regrowth
(the growth engine working against you), overcast skies, and an untrimmed margin.
Implementation: the existing high-UV-sensitivity mechanism plus lit-ground
aversion in pathing; the moat maintains itself only as long as you do.

## 8. Inhabited objects

- **The web networks** — anchor lines, sheet webs, and the silk irrigation
  gutters, laid through the entire ecosystem; flower-traced (§4c).
- **The nests** — woven from great masses of young trees and the rotting hides of
  victims; eggs inside, Shokkweave in the walls, the mother above; the mites can
  lead you there.
- **The Wildsteam war front** — their seats ring the Webwork's Scald side;
  still-burner patrols, mandible bounty boards, scorched fallbacks. Devastating
  at home, per doctrine — and this is next door to home.
- **No droids** — the enclaves site far from the web line, always; a droid convoy
  routed near the margin is a story that ends badly and is told often.
- **The margins** — where the Webwork meets desert or Greentide: burned strips,
  beetle grounds, and the creep. On border maps the web line visibly advances
  between visits (the encroachment engine, re-aimed); at world scale the growth
  is plot and flavor — the frozen map does not repaint, the dread does not need
  it to.

## 9. Artistic theme

**"A green and white hellscape, silent, owned."**

- **Light:** dim green gloom under total canopy; hard white blades of sun at
  clearings and margins — safety rendered as glare; the pale flowers glowing in
  the dark like route-lights.
- **Palette:** every dark green, dead white silk, bone-white blooms, the
  red-brown of hide-woven nests.
- **Silhouette language:** the web's geometry over organic chaos — catenary
  lines, sheet planes, gutter-runs; and the Wyyyschokk itself: too many sharp
  legs under too large a shadow.
- **Motion:** almost none — churn in the thicket, a mite-stream on a line, then
  the burst.
- **Sound:** the quietest green place on the planet. No calls, no crashes; drip,
  silk-creak, and the listener's own steps. The Greentide's silence-before-the-
  predator is the Webwork's *permanent state*.

---

## Owed

- `WEBWORK_MECHANICS_1` — the C# kit: web-sense MapComponent (felt-marks, pack
  convergence, kilometer tracking), concealed-burst ambush, Shokk-bound hediff,
  the light-moat (existing UV-sensitivity mechanism — verify the def, never
  guess), commandable-adhesion, beetle anchor-chewing, margin creep on border
  maps, droid-priority targeting.
- `SHOKKWEAVE_SOLE_SOURCE_1` — the economy ruling: rename, strip every trader
  table, add the three harvest routes; prove against live trader generation.
- **Roster** — rides the full assignment pass: the Wyyyschokk kinds (bestiary FJ
  clade names `nettik`/`chirrik`/`rothrik` available for the guilds), beetles,
  mites, the churning flora, the pale flowers; donor density correction.
- **Wildsteam kit** — still-burner weapon + liquor fuel item + mandible bounty
  quest (lands with their template/faction work).
- **Egg economy** — item, offworld sale route, the carried-eggs mark.
- **Cross-flow ledger**: the Contagion's UV cage (shared physics, one
  instrument); the Greentide margin (two expansionist greens meeting — the
  Webwork converts, the Greentide churns); `VAPOR_EMITTER_PLACEMENT_1` owes
  nothing here (no steam sources — the Webwork's wet is silent).
