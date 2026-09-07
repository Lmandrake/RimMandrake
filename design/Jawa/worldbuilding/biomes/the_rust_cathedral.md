# The Rust Cathedral — definition sheet

_Owner + BENCH, 2026-09-06, written in conversation over two rounds and ratified
("Write it up! So cool."). Defines `AB_MechanoidIntrusion` (Alpha Biomes) — the
biome, the region, and the mind all carry the name **THE RUST CATHEDRAL**. Unlike
every other sheet, this one is mostly an ASSEMBLY: the Cathedral's soul was
already ruled across `design/Jawa/reconciled_lore/03_deep_history.md` (the live
machine doctrine — this sheet defers to it rather than duplicating it), the
2026-08-19 sacrilege economics, the 2026-09-04 mind ruling, and the Scarlands
§GM. What this sitting added: the naming settlement, the wall ladder, the
coolant canals, the hum, the eels, and the living bolts._

🔴 **THE LORE IS PARTITIONED** (same law as `the_scarlands.md`): most of what
this sheet knows is unfolding plot the players must discover. §P is the whole
player-facing register; §GM carries the truth and its gates; §6 bans the leak.

🔑 **The naming settlement (owner, this sitting):** the **Forsakens = the
Rakatans = the Ancients** — one people — and they command the **Forgotten
Sentinels**, which is what the mechanoids ARE. The **Forgotten Arsenal and the
Forsaken Arsenal are the same thing** (the faction-13 label, hidden, no
settlements); "Sentinels" names the units in speech. All prior usages
harmonize; propagation rides the Wednesday canon sitting.

## 0. The measurements everything rests on

MEASURED off the live CSV: **236 tiles, one region, at the substellar
doorstep** — arc median 10.7 (sun **+79°**, the highest steady sun on the
planet), temp median 62.5 °C (58..66), rain ~zero (max 20 mm). **The flattest
ground anywhere: 211 of 236 tiles dead flat at a uniform ~615 m** — §2 gives
the flatness its reason. **Eight river tiles that cannot be water** — ruled:
they are not (§3). 29 species cast pre-sheet (mostly evictions owed — §4).
Donor (Alpha Biomes): not re-inventoried this sitting — the biome is authored
on ruled canon, and the donor def's mechanical remains reconcile at the roster
item.

## 1. What it is

A metal country. A flat plateau of deck plate and mathematical walls at the
foot of the eternal noon — **a complex, almost circuit-board maze of walls,
structures and designs that scream of meaningful complexity and intention**
(owner), rust-dust banked in drifts against them, heat shimmer as the standing
weather, and almost nothing alive. The mechanoids are at their densest here —
and sometimes **the really powerful ones can be seen, slowly on patrol,
terrifying in their destructive capacity against any biological they spot.**
Desiccated, cooked animals lie where they strayed in, mad with scaria to the
last. And under everything, always, a hum.

## 2. Planetary position

Arc 5–17, hand-sited (one patch in the world): the anomaly here is not water,
altitude, or chemistry — **it is ARTIFACT.** The uniform flatness is a built
surface: **the plateau IS the works.** You do not stand on ground that holds a
factory; you stand on the factory — halls the size of canyons under the plate,
the gantry forests and cooling stacks the only relief (the 19 hill tiles).

## 3. Driving forces

- **Time stopped here.** No rain, no frost, no tectonics, near-zero humidity —
  the one patch of Ash'karr with no erosion engine at all. The rust is a
  surface film and a blowing dust, not decay in progress; for machinery this
  old it has barely rusted at all, and that wrongness is the first thing an
  educated visitor notices.
- **The slumber.** The mind is deliberately dormant (ruled) — but not dead:
  the pumps still run, and rarely a production line somewhere under the plate
  **cycles once** — a mile of machinery turning over in its sleep — and every
  living thing on the plateau stops until it passes.
- **The coolant still moves** (owner, canon): the eight "river" tiles are
  **coolant canals**, circulating after all this time. Not that the machine
  cares — **the thing it was supposed to cool was never finished.** (Liquid
  properties ride `LIQUID_TYPES_MOD_1`.)

## 4. What lives here — almost nothing, and each exception is a story

"Remote from organics" is mechanically true: the standing 29-species cast is
mostly evictions. The residents:

- **Mynock flocks** — the one grazer that belongs, working the dead conduit;
  the Cathedral tolerates them, or grooms them, like a man brushing flies off
  a grave. (Shared with `the_scarlands.md`; one home, two ranges.)
- ⭐ **The coolant eels** (owner: "why not?") — blind, pale things circling
  the closed loop for ten thousand generations, eating the microfouling: dead
  micromachines, scale, silt. The filters were reconfigured, once, to let
  them pass — **"not that the machine cares" has exactly one exception.** The
  Cathedral keeps them: living maintenance for a cooling system whose purpose
  died unfinished, tended anyway. Grief with a biology (§GM rung). Fishing
  the canals is possible and deeply inadvisable — the hum changes the moment
  a line goes in.
- ⭐ **The living bolts** (owner) — component-looking creatures the player
  tries to pick up and simply move out of the way; they move in **complex,
  strange, dance-like patterns for no reason**, baffling everyone — and
  **their little dances resonate with the mood of the greater mind**, a nod
  toward how great it actually is. (§GM: they are teeny-tiny droid
  mechanisms left from the auto-growing technology the Cathedral once owned
  to build itself — now left simply to drift in its thoughts, endlessly.)
  Implementation: mechanical "wildlife" — not organic, not tameable, not
  butcherable into meat; the roster item owns the def shape.
- **Scaria-mad strays** — they wander in off the Scarlands and the Scorch,
  and the sun and the Sentinels finish them; the desiccated dead are map
  dressing, not spawns.
- **Roster candidate flagged by the owner**: the cockroaches from the
  cockroach mod ("might work here after all") — verify the mod and grade at
  the roster item.

## 5. Always true

- The hum is everywhere on Cathedral ground, felt in the teeth — and it
  **changes**: slow shifts of tone that are the mind's pleasure and
  annoyance made audible (§7b).
- The flatness is built; the walls are treasure; the maze is intentional.
- The Sentinels garrison at their densest, guard perimeters, and do not hunt.
- **Even the droids don't know why they are spared here.** Everywhere else
  they are targeted; here, arriving with reverence, they are passed over —
  **the first of many sacred moments.** No text explains it (§6).
- Eight of the twelve Free Droid enclaves stand on Cathedral ground; it is
  their holy city, and "remote from organics" is what its remoteness means.
- The sacrilege economics stand as ruled (2026-08-19): ~10 sacred
  faction-owned buildings at −15 goodwill each; hysteresis hostile at −75,
  un-hostile only at 0 — desecration survivable, repentance expensive;
  mineable bulk free.
- Dig deep enough and **very bad things happen. No one's quite sure what.**
  (Massive mechanoid movement — and that is all anything will ever say.)

## 6. Never true — 🔴 HARD BANS (linter-checkable)

1. 🔴 **No §GM truth in player-facing text** — the mind's nature, the smart
   metal, the plasma fountain, the bolts' origin, the eels' meaning: plot
   only, gate-kept.
2. 🔴 **No explanation of the droids' mercy, anywhere, in any register** —
   not even the droids know; a def or dialog that explains it violates the
   sheet.
3. 🔴 **No hunting Sentinels** — perimeter defense only; a Sentinel raid or
   pursuit story is a violation (faction 13 stays in the raid roster as
   ruled — vault and perimeter emphasis, not manhunts).
4. 🔴 **No organic settlement or faction presence but road traffic** — the
   droids alone dwell here.
5. 🔴 **No true acid terrain** — sulfuric dressing only (2026-08-19 ruling);
   pool hazards are stationary and legible.
6. 🔴 **No deep-drill explanation** — the response event stays undescribed in
   every text, forever.
7. 🔴 **No ordinary wildlife** — nothing organic spawns here that isn't §4's
   short list; green flora count: zero.

## §P — what the players are told

A metal wasteland at the foot of the eternal noon: the densest mechanoid
ground on the planet, a maze of intentional walls that are themselves
salvageable metal, coolant that still runs to cool nothing anyone can find,
strange component-creatures dancing patterns nobody can read, and a hum that
everyone — everyone — eventually notices is *reacting to them*. The droids
make pilgrimage here and are inexplicably spared, and their only counsel is
the line the sheet keeps verbatim: **"Why have you angered this place? We
know what it feels. So will you if you just listen."**

## §GM — the truth (gates per the Scarlands ladder; deep detail lives in `reconciled_lore/03_deep_history.md`)

- **It is a kyber-crystal engineered mind** (owner, this sitting) — the same
  nature as the mechanoids' minds, but vastly more powerful. It was going to
  manage and coordinate **the entire planetary factory and surrounding
  area**. Now it has nearly nothing to do — **and not even all of its own
  intelligence to do it with.** So depressing.
- **The metal was smart metal** — self-assembling through flowing
  micromachines, the technology long defunct. The whole Cathedral was a
  **self-assembling factory built to manufacture a massive mind — itself
  merely part of something bigger still**: drawing the mass of asteroids,
  channeling the star's power in a profound plasma fountain across
  interstellar distances, massive magnetic dynamos working toward some
  greater purpose — **all of it gone before it was ever even half complete.**
  (The Propane Lakes' collapsing megastructures are this program's far end —
  `TERRAMANUFACTURE_CANON_1`.)
- The relations, the slumber's reasons, the Utinni's vouching, the hatred of
  the Helix, the pet-droids: **all per `03_deep_history.md` §The Rust
  Cathedral** — that doc owns them; this sheet points.
- The living bolts drift in its thoughts; the eels are kept; the hum is its
  voice leaking. The Scarlands next door are its builders' graves and its
  last stand's cost (`the_scarlands.md` §GM).

## 7. Uniquely available

- ⭐ **The wall ladder** (owner): the map is MADE of treasure, in tiers —
  common deck plate (free bulk, mine at will) → **dead smartsteel** (the
  defunct micromachine alloy, distinctly valuable) → rarer, stranger wall
  types worth "mining out" — really destroying and claiming → and below it
  all, the deep live-pattern metal that comes with §5's last bullet.
- **The salvage-vs-sacrilege loop**: every wall is money, every sacred
  building is blasphemy, and the hum grades you continuously in between.
- **Hum-literacy** — learnable, tradeable knowledge: reading the tones (and
  the bolts' dances) tells you what no instrument can.
- **Gravtech boons** — plot-tier, through the mind, at its own risk (per
  `03_deep_history.md`).
- **Bolt-shed curiosities and eel-catch** — both salable, both watched.

## 7b. Playing the Cathedral

The donor advice pattern inverts here: the Cathedral is not survived by walls
but by **manners**. Mine the bulk freely; touch nothing sacred; when the hum
drops, stop moving (the bolts freeze first — watch them); when a great
Sentinel crosses your line of sight, be small and biological and boring. The
hum-mood system (`RUST_CATHEDRAL_MECHANICS_1`) is the biome's core mechanic:
a slow-moving attitude value voiced as layered tones, displayed by the bolts'
dances, commented on by droid NPCs, and wired into the ruled hysteresis — the
long ladder of warnings before −75 is the Cathedral being, by its own lights,
patient.

## 8. Inhabited objects

- **The sacred core** — the ~10 faction-owned buildings of the ruled
  economics; the droids' shrines in the old machinery, where the whispered
  voices are real attention.
- **The enclave holy city** — eight of twelve seats (*Cell Seven, No Master,
  Vent Forty, Vent Twelve, The Cracking Yard, No Owner, Second Speaker* and
  kin); only *No Master* kept a road out.
- **The works** — gantry forests, cooling stacks, feedstock fields, the
  coolant canals, the circuit-board maze itself.
- **Sentinel grounds** — patrol routes (including the great ones', slow and
  visible from far off), vault perimeters at their densest.
- **The dressing** — rust drifts against the walls; the desiccated strays;
  the pools with their sulfuric look.

## 9. Artistic theme

**"A circuit board the size of a country, humming to itself in its sleep."**

- **Light:** the whitest, emptiest sky on the planet over the fullest ground;
  hard geometric shadows that never move; shimmer.
- **Palette:** rust film over dark metal, verdigris at the coolant, the dust's
  ochre drifts, hazard-sulfur at the pools — and no green anywhere.
- **Silhouette language:** intention — right angles, repeats, alignments that
  resolve into meaning from altitude; the great Sentinels' slow skyline
  crossings.
- **Motion:** shimmer, dust, the bolts' inexplicable dances, one patrol.
- **Sound:** THE feature — the ever-present hum in slow emotional weather,
  the once-in-a-great-while line-cycle rolling under the plate, and beneath
  the canals, if you listen long enough, something like circulation.

---

## Owed

- `RUST_CATHEDRAL_MECHANICS_1` (to file) — the hum-mood system (attitude
  value, layered tones, bolt-dance display, droid commentary, hysteresis
  wiring), the deep-drill response event (undescribed), wall-tier defs, the
  living bolts as mechanical wildlife, eel-fishing consequences.
- **Roster item** — evict the bulk of the 29 cast; mynocks (shared with the
  Scarlands), eels, bolts; the cockroach-mod candidate (owner) verified and
  graded.
- `LIQUID_TYPES_MOD_1` — coolant as a first-class liquid.
- **Canon sitting (Wednesday)** — propagate: the naming settlement
  (Forsakens=Rakatans=Ancients; Sentinels=the mechanoids; Arsenal=the
  faction, both epithets); the kyber-mind fact into `03_deep_history.md`
  (which also touches the Lantern Deeps' kyber canon and the mechanoid-mind
  nature); this sheet's §GM cross-links.
- **Donor def reconciliation** — read `AB_MechanoidIntrusion`'s actual XML at
  the roster/patch item (not indexed in RimSage this sitting) and strip
  whatever contradicts the sheet.
