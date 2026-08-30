# Ash'karr — The Sundered

A tidally locked desert world: one face forever under twin suns, one forever
dark, life in the band between. **The axis of everything is ARC from the
substellar point, never latitude** — this world does not spin, so there is no
day, season, or latitude gradient. Every number about the painted planet lives
in `infrastructure/state/canon.yml > planet` (tiles, water %, temperature
curves, biome censuses, settlements); this file carries the physics and the
rulings. Status: the map is **adopted and being authored in place**; the freeze
is a savegame not yet taken (`canon.yml planet.status`).

The name reads three true ways at once: the world split by the lock; the world
broken by the Forsakens' failed terraforming; the people sundered by the war.

## The three condensers — the whole of the planet's chemistry [owner 2026-08-15]

| where | what condenses | what it makes |
|---|---|---|
| **the high peaks** | water, violently | flash floods, brief fierce green, rivers, the hypersaline seas — and gigantism |
| **the terminator seam** | water, as a trace | the stunted, toxin-hoarding poison forest |
| **the deep night** | hydrocarbons | the propane lakes — a fuel field that kills the unprepared by cold alone |

- **It rains ONLY on the unlandable peaks.** Ordinary rain is stripped from
  every other biome's weather table. Every drop of fresh water is stolen from a
  mountain.
- **The mountains are VOLCANIC, and there are many ranges** — a tectonically
  dead world with stationary hotspots builds Olympus-class peaks, keeps its
  condensers, and (flash floods off raw rock) delivers the nutrient load that
  makes the seas violently alive. Gigantism is a nutrient budget, not a conceit.
- **The seas are impossibly salty** — not the Dead Sea; what the Dead Sea
  becomes. Food and mass, not drink. Exactly three: **The Scald** (painted
  `Lake` — a named sea, the def stays), **The Twilight Sea**, **The Gray Sea**.
- **The ocular forests** drink the high rain and excrete red spore-toxin
  streams that detoxify in transit — the rivers everyone drinks begin as
  poison. One organism's tissue that forgot where to stop. Rare and horrible.

## Fire ecology — the Pyrelands

Freakish plant growth (a planetary fact: vegetation reads aggressive, *wrong*)
+ no rain + dry thunderstorms = **a standing burn that migrates across the
savanna forever**. The fire lights the storm and the storm lights the fire —
built from shipped weather mechanics, not simulated. The Pyrelands are the
high-risk/high-reward tile: the planet's best soil (ash), on a schedule you do
not control. The **tar pits** are the receipt — eons of ash-and-flood churned
into biologically rich tar at the margin, preserving what they catch
(including things that are not bones). Four survival strategies characterize
factions: burrow (Geonosians) · move (Tuskens — camps in the scar behind the
front) · burn-it-first (unclaimed — see GAPS) · wall-it-out (the Empire's
sterile scars visible from orbit).

## The nightside — a decay gradient, not a biome [owner 2026-08-15]

Sequence, fading spatially: poison forest (the seam) → mycotic jungle →
gelatinous superorganism (**patches only, never a band**) → propane lakes,
crystalline caverns, self-glowing landscapes (the last light) → **the forsaken
crags** — total darkness, an alien chemistry that is oddly FULL of life and
deeply hostile: most creatures manhunt on arrival, **nothing is edible**. The
crags are the exact conjugate of the deep desert: absence kills you there,
presence kills you here. The one biome where the scavenging loop itself fails.

**The nightside is as cold as the dayside is hot** (R-H10): nightside biomes'
temperatures are forced down; nightside creatures ENJOY frigid cold and die
crossing the terminator, as dayside life dies going out. The terminator is a
hard biological barrier both ways — the ship must be excellently heated to
reach the propane that keeps it warm, and nightside biology is untransportable,
which makes it valuable.

Unifying idea: dayside assembles matter obscenely fast; the darkside takes it
apart just as fast. Same metabolism, opposite sign. **Growth stalls in exactly
one place** — the terminator seam — and that exception is what makes the poison
forest legible.

## Water doctrine [owner 2026-08-13]

1. **Thirst is DIFFERENTIAL**: Jawa and desert-natives need much less; offworld
   xenotypes normal; aquatics/heavy-bodied ELEVATED (a leash, not a penalty);
   **droids none — that is the Jawa advantage stated mechanically.** Every
   restraining bolt is an act of water economics.
2. **Natural potable water is always DEFENDED** — the defenders' presence is
   explained by the water. Manufactured/stored water (vaporator farms, the
   player's stills) is exempt — W4.
3. **Most desert water is saline or contaminated**; purification is expensive
   v2 tech *for the player* — the Deepwater monopoly and Jawa salvage stills
   already exist and stand (W5).
4. **v2: water bottles become the currency and silver goes rare.** The most
   transformative and highest-risk item; wants its own build slot.

Layer discipline: in fiction water is the master resource; in the v1 engine it
is DBH-Lite Thirst-only (real need, no plumbing, no free-water generator; the
ship carries storage, never generation). Do not let fiction confidence leak
into build talk.

## Terrain design — the four axes

Every terrain answers, by construction: ① **Abundant** (why you come),
② **Scarce** (what it denies — your next need), ③ **Exotic** (located covetable
wealth), ④ **Threat** (the qualitative timer that evicts you). Closed loop; no
tile is a terminus. **Terrain treasures** (quarry/well/deep-drill/wreck/derrick)
are operable but never player-buildable — wealth bound to place. An
infinite-rate generator is pillar-safe iff discoverable-only AND on a tile
whose threat bounds the dwell. The world is REGIONALIZED, not noise: a volcanic
"fire coast," vast unbroken desert seas, one Shipyards-like cluster (now the
Rust Cathedral, `03_deep_history.md`), ocular forests on mountains bleeding
rivers.

## Standing guards

- Do not reopen geometry, water fraction, sea count, or the temperature curve —
  accepted, not merely current [owner 2026-08-20/22/23].
- `ZBiome_Grasslands` IS the Stormy Savanna (the defName lies) and carries the
  Pyrelands; vanilla Savanna/Grasslands stay cut.
- The painter beat the cut list once and for all: `AB_GelatinousSuperorganism`
  and `ZBiome_Grasslands` stay as painted [owner 2026-08-20].
- The `Alien Worlds – Tidally Locked` mod's curve is worldgen-only and can
  never touch the painted save; its "+14" is arc 45°, its terminator is −37 °C.
  Ours is +14 at the terminator. Two curves, two planets, only ours ships
  (`canon.yml > temperature_curves`).
- **There is no canon start colony** — The Setdown was struck
  [owner 2026-08-24]; nothing on the map is the player's home until the owner
  sites it.
