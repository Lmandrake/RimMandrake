# ship_designs.md — Gravship topology: chosen hull + candidate menu (expanded limits)

_Design pass, 2026-08-06. Regenerated after **Bigger Gravships** was approved (WS 3522759531,
see `required_mods.md`). The mod is used here as a **design-time allowance** to loosen the
substructure limits so the ship can be a genuinely large, cool Star Wars silhouette — **not** to
enable in-game expansion. The anti-exponential pillar is still enforced by the repair-gate /
feedstock progression in `ship_deck_plan.md`, never by the tile cap. This doc owns the TOPOLOGY
choice; `ship_deck_plan.md` owns the repair-progression / heat doctrine the chosen hull inherits._

> ## ✅ CHOSEN HULL (LOCKED 2026-08-06): **#15 Falcon Halo (hollow)**
> A clean cargo **wheel** — thin cargo rim, a **hollow shrine-heart** at dead centre (grav-engine
> core + scrap-totem shrine, single rear causeway), **seven function-pods sunk into the outer rim**,
> and one long forward **Millennium-Falcon mandible arm** that forks into two prongs with the
> **shuttle bays capping the prong tips** and the **command cockpit** offset to starboard.
> Verified liftable: **4,057 / 4,800 tiles** (743 headroom), 7 extenders, single connected piece,
> all 14 mandatory regions; **largest cargo of the whole set (1,443)**.
> **Large panel:** `src/RimMandrake/mapsynth/runs/design_15_falcon_halo_hollow_large.png`.
> **Concept renders (start/end pair, alongside this file in `design/Jawa/worldbuilding/`):** `ship_damaged_image.png` = the stripped
> structural wreck the campaign begins from (the crashed Factory ship); `ship_image.png` = the
> fully-repaired ship the 7-phase repair progression climbs toward. Same silhouette (ring, seven
> rim pods, mandible arm with the two prong-tip shuttle bays, offset cockpit) confirms both are #15.
> The other fourteen silhouettes are retained below as the record of the exploration that led here.

> **Verifier:** `src/RimMandrake/mapsynth/ship_designs.py` + `build_designs.py` (regenerates + re-checks all
> fifteen). **Renderers:** `src/RimMandrake/mapsynth/render_designs.py` (8-panel grid of the early set) +
> `render_single.py <name>` (any one design on its own large panel).

---

## Change log (so a restart makes sense)

- **2026-08-06 (initial expanded pass):** eight designs generated under expanded limits.
- **2026-08-06 (region audit):** caught several designs missing regions; added textile/ammo (**D**)
  to the palette and enforced the full mandatory set programmatically.
- **2026-08-06 (colour pass):** recoloured to the user's scheme — system/"caps" regions at full
  saturation with fixed hues, factory wings as pastels, black background (see palette below).
- **2026-08-06 (this pass):**
  1. Added **Shuttle Bay (H)** as a **14th mandatory region** (white). Fitted into every hull.
  2. **Removed the two triangular Imperial-military designs** (Star Destroyer wedge, Manta delta) —
     those silhouettes are reserved for Imperial ships, not this Jawa hulk.
  3. Added **#7 Nodal Station** — twin central nuclei (cargo + carbonite) radiating asymmetric
     spoke-corridors to exterior octagon "cells", shuttle dock on the longest spoke.
  - Net: **seven designs**, all carrying **14 mandatory regions**, all verified liftable.
- **2026-08-06 (ring/nodal hybrid pass):** Added **#8 Ring-and-Spur** — a Ring × Nodal hybrid: a
  thinner main ring holding the core systems, with eight **circular pods** bursting outward on
  5-wide spokes at deliberately irregular ("semi-random") angles, one enlarged pod = the shuttle
  bay, thrown furthest out. Net: **eight designs**, all 14 regions, all verified liftable.
- **2026-08-06 (derelict-halo pass):** Added **#9 Derelict Halo** — the eerie variant. Same ring +
  irregular circular pods; "strange" **curved walkways** (never straight), two **overshooting past
  everything into empty space** for reasons long forgotten; **hollow void** interior except a **single
  spiral causeway** curving inward to the ship's heart: the **grav-engine core** ringed by a small
  consecrated floor of the Jawa's **worshipful scrap totems** (carbonite/sacred-scrap). Needed a new
  curved-corridor primitive (`arc()`) + a large-panel renderer (`render_single.py`, ~3× fonts) after
  "text too small" feedback.
- **2026-08-06 (contiguity guardrail + fix pass):** ⚠️ Added a **CONTIGUITY CHECK** to the verifier
  (`_count_components` in `ship_designs.py`): a real gravship is **one physically connected structure**
  — all parts must touch — so `liftable` now also requires `n_components == 1`. This caught that the
  first #9 had the pods *genuinely floating* (8 parts) **and** that **#3 (corvette, 5 parts — engine
  fins detached)** and **#4 (catamaran, 2 parts — bow command block detached)** had latent one-row gaps
  the old coverage-only check silently passed. **All three fixed** (pods now hang on **curved spiral
  tethers** that overlap the ring; corvette fins tied in by a stern deck; catamaran bow extended to the
  hull). Re-verified: all nine report `parts=1`. Net: **nine designs**, all 14 regions, all genuinely
  contiguous and liftable. New stats: #3 3849(951)/cargo616, #4 4113(687), #9 4228(572)/cargo1092.
- **2026-08-06 (rectilinear Spine × Halo hybrids):** Added **#10–13** — four ways to blend the
  **Spinal Freighter** (#1, straight keel) with the **Derelict Halo** (#9, hung pods + hollow void +
  heart-shrine + overshoot walks), all in **right-angles** instead of curves. New squared-off idioms
  in `build_designs.py`: `_hang` / `_hang_v` (pod hung across a gap on a 1-tile catwalk), `_overshoot`
  (L-shaped walk-to-nowhere anchored to structure), `_bridge` (dog-leg segment link). **#10 Spinal
  Reliquary** (keel + hung wings + shrine amidships), **#11 Ladder Halo** (twin rails + hollow void +
  outboard pods), **#12 Cross-Nave Cathedral** (cruciform + shrine at the crossing), **#13 Broken Keel
  Halo** (keel snapped in three, dog-leg bridges). All verified `parts=1`, 100 % coverage, 14 regions.
  Net: **thirteen designs**. Each new one rendered on its own large panel via `render_single.py`.
- **2026-08-06 (Falcon Halo):** Added **#14 Falcon Halo** — the Large Halo (#9's ring) rebuilt **at
  full health**: a solid cargo **wheel** (thin rim band + central shuttle-hangar **hub** joined to the
  rim by four clean 5-wide spokes — NOT hollow), with **eight circular function-pods sunk half-into the
  OUTER rim** (each disk overlaps the band so it's structurally continuous, no tether), and **one long
  forward arm in the Millennium Falcon idiom**: a solid neck off the rim forking into **two mandible
  prongs** around an empty front notch, with the **command cockpit** jutting off to **starboard** on a
  short tube. New idiom in `build_designs.py`: `_embed_pod` (a circle centred just inside the rim so its
  inner half merges with the band). Verified `parts=1`, 100 % coverage, 14 regions, 4410/4800 tiles
  (headroom 390), 7 extenders, cargo 1319. Rendered on its own large panel. Net: **fourteen designs**.
- **2026-08-06 (Falcon Halo hollow):** Added **#15 Falcon Halo (hollow)** — user revision of #14:
  "keep it, but move the shuttle bay out to the end of those strange arms and leave the centre empty
  as before." Same clean cargo wheel + rim-embedded pods + Falcon mandible arm, but the **central
  hangar hub and its four spokes are removed** → the interior is a **hollow void** (the #9 treatment)
  holding only the grav-engine core + scrap-totem shrine (T) at dead centre, reached by a single rear
  causeway. The **shuttle bay (H) moves forward to cap the two mandible-prong tips** (a hangar pad off
  each arm end; the front notch stays open). Command stays at the offset starboard cockpit; the
  carbonite shrine moved from a rim pod to the centre, so the rim now carries **seven** embedded pods.
  Verified `parts=1`, 100 % coverage, 14 regions, 4057/4800 tiles (headroom 743), 7 extenders — and
  hollowing actually **raised cargo to 1,443** (the freed rim). Rendered on its own large panel. Net:
  **fifteen designs**.

---

## Limits used (and an honest caveat)

| | grav-engine radius | extender radius | max extenders | tile cap |
|---|---|---|---|---|
| **Vanilla (verified)** | 19 | 16 | 6 | 2,000 |
| **Expanded (used here)** | **34** | **30** | **12** | **4,800** |

**Provenance of the expanded numbers — now CORROBORATED (Fetcher `2026-08-06_bigger_gravships_ranges`,
delivered 2026-08-06).** These were originally *generous assumed* values; the Fetcher pull confirms
they are all **reachable** via the mod's sliders:

- **Bigger Gravships is a pure config mod** — RedMattis states it *"edits properties… doesn't modify
  the game's logic,"* exposing sliders for support (tile cap), support range, support count, thruster
  range/counts, chemfuel tank size, etc. There is **no hard published ceiling**; players report 2,600+
  tile ships and a 160×170 hull built without issue.
- A **sibling "Bigger Gravships" clone (WS 3527183506)** documents one concrete doubled preset: engine
  range 18.9→**37.9**, tile cap 500→**1000/engine**, extender range 16.9→**32.9**, extender cap
  250→**500 each**, extender limit 6→**10**. Our values (R_ENG 34, R_EXT 30, N_EXT 12, CAP 4,800) all
  sit within or just beyond that preset and are user-settable — **evidence-supported, no longer a bare
  assumption.**
- **One soft caveat (build-quality, not a hard limit):** RedMattis *and* Ludeon advise against long
  "train-shaped" hulls — the takeoff texture scales with the longest dimension, and very long ships
  have caused landing / quest-fit trouble. **#15 is a compact wheel (~square footprint + a short
  forward arm), i.e. exactly the "square-ish" shape the author calls safest — so this caveat validates
  #15's silhouette rather than threatening it.**

⏳ Still pending: a follow-up Fetcher request (`2026-08-06_bigger_gravships_SOURCE`) for the mod's
actual settings XML/C# to read the *exact* default and max slider values. The verifier is
parameterized (`ship_designs.py` top block), so if those differ it's a one-line change + re-run.

---

## The rules every design still had to pass

Two independent constraints, both verified per design (not assumed):

1. **Capacity** — total connected substructure ≤ the cap (4,800 here).
2. **Radius coverage + chain rule** — one grav engine reaches `R_ENG`; each of up to `N_EXT`
   field extenders reaches `R_EXT`; and every extender must itself sit inside the field already
   built by the engine + earlier extenders. A design that passes capacity can still fail to fly if
   a tile is out of radius. The verifier greedily seats the engine + extenders on each hull's
   backbone to maximize coverage, **stops as soon as the hull is fully covered** (so the reported
   extender count is how many are actually *needed*), then reports uncovered tiles and the
   farthest-tile distance.

**All eight below report: 0 uncovered tiles, chain rule satisfied, tiles ≤ 4,800, and every
required area present.** They are all genuinely liftable.

Every design carries the **full 14-region set**, checked programmatically — the build fails and
prints the shortfall if *any* region is missing. The 14 mandatory regions, from
`ship_deck_plan.md`'s wing map plus the shuttle bay added this pass:

- **Systems (5):** command/control **M**, thrusters + main power **S**, fuel tanks **U**,
  water tanks **W**, **shuttle bay H**
- **Factory — all six Factory_lore wings (6):** raw extraction **A**, bulk/dirty **B**, food **C**,
  textile/ammo **D**, advanced materials **E**, precision **F**
- **Storage (1):** cargo hold **G**  ·  **Living (1):** habitat **R**  ·  **Luxury (1):** carbonite bay **T**

---

## Colour scheme (for reading the sheet)

Set by the user so the sheet is legible at a glance:

- **System / "caps" regions — full saturation, fixed hues:** command = **blue**, habitat =
  **green**, water = **cyan**, cargo = **brown**, thrusters = **yellow**, carbonite = **black**,
  corridor = **grey**, fuel = **magenta**, shuttle bay = **white**. Keel/spine is a dark slate grey
  (deliberately darker than corridor grey so the backbone stays distinguishable).
- **Factory wings — pastels** (so they read as one family and recede behind the bright systems):
  precision = pastel violet, adv-materials = pastel coral, bulk = pastel orange, food = pastel
  yellow, textile/ammo = pastel mint, raw-extraction = pastel dusty-rose.
- **Background:** black. (Consequence: carbonite black tiles read only by their grey grid outline —
  fine, but a brighter border is available if you want the vaults to pop.)

The palette lives in `src/RimMandrake/mapsynth/ship_designs.py` (`COL` / `LABEL`), shared by verifier and renderer.

---

## The one geometric law that still shapes all of them

A spine-mounted extender covers a tile only if the tile is within `R_EXT` of *some* node on the
spine. With the wider radius the ships can be far bigger, but the law is unchanged:

> **You buy hull by adding LENGTH along a covered spine, never WIDTH past ~`R_EXT` tiles from it.**
> Every design is some arrangement of *spines* (straight, doubled, ring, or radiating spokes) with
> decks hung within reach of a spine. The wider radius just means the "spine tax" is cheaper.

Clearest illustrations in this set: the **Nebulon-B** only flies because the keel runs through
*both* end-hulls (not just the neck); the **Nodal Station** needs a node near each spoke tip, which
is why it burns the most extenders (9).

---

## The nine

Numbers below are from `designs_report.json` (regenerable via `build_designs.py`). "Factory" = all
six Factory_lore wings combined (A+B+C+D+E+F). Every design now carries all 14 regions (verified).

### 1 · Spinal Freighter — *the baseline topology, scaled up*
**4,499 tiles · 301 headroom · 5 extenders · cargo 702 · factory 1,404 · shuttle 234 · farthest 29.61**

One long keel, seven production wing-bands ribbing off both sides (all six factory wings, two cargo
bands, a shuttle bay), command bow, thruster/fuel/power stern, carbonite tail. The kept baseline,
now roughly 2.3× the vanilla footprint. Nearly saturates the cap → the "restoration runs out of
ship" feel is strongest here.

For: legible heat story (HOT wings E/B outboard vent to the desert); cleanest mapping to the repair
gate; longest usable exterior wall for defense and drills; matches the deck plan already written.
Against: long and thin = long internal hauls; the most wall to seal; no interior gathering space.
Best if: you want the deck plan in `ship_deck_plan.md` at a grander scale.

### 2 · Nebulon-B — *fore hull · thin neck · aft hull*
**3,741 tiles · 1,059 headroom · 4 extenders · cargo 562 · factory 1,754 · shuttle 126 · farthest 29.97**

The classic escort-frigate profile: a rounded command/habitat hull up front, a long skeletal neck
(carrying the shuttle dock, mess, textile, water and raw-extraction pods), and a boxy
engineering/engine hull aft. The **largest factory allocation** of the linear set (the aft
engineering block). Strongly asymmetric along its length.

For: extremely characterful; the neck is a natural firebreak and a deliberate "we never finished
rebuilding the middle" story beat; concentrates industry aft, living forward — clean separation;
lots of coverage headroom. Against: the neck is a logistics chokepoint (single narrow corridor
between the two halves) and a structural weak point in a hunted-nomad fight. Best if: the frigate
look and the fore/aft functional split appeal, and you like the neck as a chokepoint you defend.

### 3 · Corellian Corvette — *hammerhead bow, engine cluster aft*
**3,827 tiles · 973 headroom · 4 extenders · cargo 660 · factory 1,080 · shuttle 189 · farthest 29.15**

The Tantive IV blockade-runner: a wide rounded "hammerhead" command prow (bridge core + habitat
ring), a body that tapers aft carrying the six factory wings and tanks, a wide shuttle dock across
the aft body, and a radial cluster of five thruster stacks at the tail. Reads instantly as a
blockade runner. **Largest habitat allocation** (640).

For: gorgeous, recognizable, balanced (good cargo *and* habitat); the tapering body is efficient;
the tail engine cluster is a strong heat/thrust face. Against: the round hammerhead is fussier to
hand-author than a rectangle; the prow is mostly command/habitat, so industry is squeezed into the
mid-body; smallest carbonite vault (28). Best if: you want an elegant, iconic hull that's still
well-balanced across roles.

### 4 · Catamaran Courtyard — *twin hull + open courts (the double-spine idea)*
**4,068 tiles · 732 headroom · 4 extenders · cargo 970 · factory 1,174 · shuttle 122 · farthest 29.73**

Two parallel keels tied at bow (command) and stern (thrusters) by cross-decks, with a thin central
catwalk carrying backbone amidships. The open center is carved into a **fore court and an aft
court** — literal open-air courtyards inside the hull footprint. The port hull holds the four clean
factory wings + habitat + water + shuttle; the starboard hull holds the HOT wings + fuel +
carbonite. Largest cargo of the set.

For: directly realizes the double-spine / courtyard concept; the courts double as heat vents
(sealed-ship cooling as *space*, not tech), a solar/defense yard, and a firebreak between the two
industrial hulls; hull redundancy for a hunted nomad. Against: twin hulls = duplicated corridors.
Best if: the courtyard is a feature you want to play with, and redundancy appeals.

### 5 · Ring Station — *annulus around a central hangar*
**4,702 tiles · 98 headroom · 6 extenders · cargo 421 · factory 2,537 · shuttle 185 · farthest 29.02**

All decks live in a thick ring; the keel runs *around* the ring midline; six extenders space around
it. The center is a big **open hangar/courtyard** — the largest open space of any design. The
shuttle bay is an external docking blister off the NE outer hull. **By far the largest factory
allocation (2,537)**, and it essentially saturates the cap (98 headroom).

For: the most dramatic open core (shuttle pad, solar, water catchment, killbox, or trophy plaza);
both inner and outer ring walls are exterior → twice the vent/defense edge; enormous factory
capacity. Against: most complex to author and to path (circumferential hauls unless you bridge the
hangar); the inner edge is exposed hull to seal; almost no coverage slack. Best if: you want the
boldest silhouette and a large ceremonial/functional open core.

### 6 · Salvage Hulk — *asymmetric wreck (one grand wing, one broken stub)*
**4,604 tiles · 196 headroom · 4 extenders · cargo 622 · factory 1,700 · shuttle 288 · farthest 30.23**

Deliberately lopsided: a long, fully-built **port** hull (precision → cargo → food → textile →
habitat → water, bow to stern) and a short, **jagged starboard stub** — a working adv-materials
wing, a cargo stub, a bulk stub, a **rebuilt shuttle bay in the former derelict gap**, then a fuel
stub and carbonite vault near the stern. Asymmetric stern thrusters, and a small raw-extraction pod
broken off the port bow (tethered by a keel stub). Leans hard into the crashed-Factory-ship theme.

For: the most on-theme hull for a *salvaged wreck* — the missing/rebuilt starboard section *is* the
story, and gives a legible place to stage the repair gate; side-to-side asymmetric; the pod is a
great outlying objective; largest shuttle bay of the linear hulls (288). Against: the asymmetry
means uneven internal travel and a lopsided defense perimeter. Best if: you want the ship's shape
itself to tell the wreck story, with obvious room left to "finish."

### 7 · Nodal Station — *twin central nuclei radiating asymmetric spokes*
**4,607 tiles · 193 headroom · 9 extenders · cargo 357 · factory 1,107 · shuttle 357 · farthest 29.83**

Inspired by the reference station image. **Two central octagon nuclei sit side by side** — a
**Cargo** hub and a **Carbonite** hub — and each throws asymmetric **spoke-corridors** out to
exterior octagon **cells**, one per function (command, the six factory wings, water, habitat,
thrusters). Every spoke is **5 tiles wide = belt-in + belt-out + a central walking lane**, so
material rides inward to a nucleus and back out. The **white shuttle dock sits on the longest
spoke**, thrown well past the others, its octagon larger than the rest. Cargo feeds the upper/left
cells; carbonite feeds the lower/right cells plus the shuttle.

For: a genuinely different, modular silhouette that reads as a *station* not a *ship*; each cell is
a clean isolatable unit (maps 1:1 onto the wing-by-wing repair gate and per-cell power/heat plan);
the two nuclei make cargo and carbonite the literal heart of the hull. Against: burns the most
extenders (9 — each spoke tip needs a node in reach); spokes are long haul distances; the two
nuclei sit close, so which spokes belong to which hub isn't obvious at a glance (fixable by pushing
the hubs apart). Best if: the hub-and-spoke station aesthetic is what excites you and you like the
strict one-cell-per-function modularity.

### 8 · Ring-and-Spur — *ring core with semi-random circular pods*
**3,837 tiles · 963 headroom · 10 extenders · cargo 1,279 · factory 894 · shuttle 317 · farthest 29.97**

A **hybrid of #5 Ring and #7 Nodal.** A *thinner* main ring carries the core systems (the ring body
is one big cargo hold, with command / thrusters+power / water / fuel blocks and a carbonite vault
set into the band), and **eight circular pods burst outward** on 5-wide spokes at deliberately
**irregular angles** — the six factory wings + habitat + the shuttle — so the ring's symmetry is
broken into something that reads as an organically-grown station rather than a machined torus. One
pod (the **white shuttle bay**) is **larger and flung furthest out**. The angles and radial offsets
are fixed-but-jittered (deterministic, so the build reproduces), giving the "semi-random" look you
asked for. **Largest cargo of the whole set (1,279)** — the entire ring body is hold.

For: keeps the monumental ring silhouette *and* the modular-pod isolability of the Nodal station,
while the asymmetry makes it distinctive; each pod is a clean isolatable unit (maps onto the
wing-by-wing repair gate); the ring's inner *and* outer walls are exterior (double vent/defense
edge) and the pods add even more perimeter; enormous cargo; lots of coverage headroom (963). Against:
burns many extenders (10 — each pod tip needs a node in reach); the smallest factory allocation of
any design (894 — most floor went to the cargo ring and to corridors), so this is a *hauler/trader*
hull more than an industrial one; circumferential hauls around the ring unless you bridge the core;
the pods are single-purpose and a bit cramped (radius-7 balls ≈ a modest room each). Best if: you
love the ring look but found #5 too symmetric, and you want maximum storage with modular outlying
pods — accepting a lighter factory.

---

### 9 · Derelict Halo — *pods on curved tethers, dangling perimeter walks, a shrine at the dead centre*
**4,228 tiles · 572 headroom · 10 extenders · cargo 1,092 · shuttle ~317 · farthest 29.83**

The **eerie sibling of #8.** Same monumental cargo ring with the core systems set into its band
(command / thrusters+power / water / fuel), and the same **eight irregular circular pods** for the
six factory wings + habitat + the enlarged white shuttle bay. The twist is *how* the pods attach:
instead of #8's clean straight radial spokes, each pod hangs off a **curved spiral tether** that eases
out from the ring band and sweeps as it goes — so the connectors read as **strange curved walkways,
never straight lines**. A few of those tethers **overshoot past their pod and dangle off into empty
space** for reasons long forgotten (each such stub is *anchored to a pod*, so it's real ship, not
debris). The interior is otherwise a **hollow void** save one thing: a **single spiral causeway** that
curves inward from the ring to the ship's heart at the dead centre — the **grav-engine core**, ringed
by a small consecrated floor bearing the Jawa's **worshipful scrap totems** (the black carbonite /
sacred-scrap block). That lone sacred path is the only thing that reaches the middle.

**Correction (2026-08-06):** the first cut of this design had the pods *genuinely floating* (no
connector at all), which is **not a valid gravship** — a gravship is one physically contiguous
structure; every part must touch. That version failed the new contiguity guardrail (8 disconnected
parts). This entry describes the fixed, **single-piece** design (verified `parts=1`).

For: the most *atmospheric* and unsettling silhouette in the set — a salvaged wheel with organs slung
around it on curling gangways and a shrine at its core, exactly the crashed-Factory-ship / Jawa mood;
big cargo (1,092, third behind #8 and #4); each pod is a clean isolatable unit (maps onto the
wing-by-wing repair gate); the curved perimeter walks give a lot of exterior/defensible edge; decent
coverage slack (572). Against: it is the **hardest to hand-author** (curved tethers + a spiral core
path placed tile-by-tile); the tethers are long and thin, so foot-hauling between pods is slow and the
ship is corridor-heavy; the "mysterious dangling" stubs are deliberate flavour tiles that cost a
little wealth for no function. Best if: you want a *set-piece / GM-mood* hull — a haunted salvaged
wheel — and you accept a corridor-heavy, hauling-slow layout for the strongest atmosphere.

*Rendered on its own large panel:* `src/RimMandrake/mapsynth/runs/design_9_derelict_halo_large.png` (built by
`render_single.py`, ~3× the comparison-grid font size for legibility).

---

## The four rectilinear Spine × Halo hybrids (#10–13)

*Added 2026-08-06 at user request: "make a new ship version that's LIKE the central spine one, but
that is more like a rectilinear version of this Derelict Halo … merge those two in a few different
ways."* Each of these takes the **Spinal Freighter's** DNA (one straight keel, right-angles, dense)
and re-expresses the **Derelict Halo's** four signatures **in squared-off geometry**: (a) modules
**hung across a visible gap on a thin catwalk** instead of fused into a hull; (b) a **hollow-void**
interior; (c) a **shrine at the heart** — grav-engine core + worshipful scrap totems (the black
carbonite block) on a consecrated floor; (d) "**strange" catwalks that overshoot into empty space**
(here L-shaped dog-legs, each anchored to real structure so it's ship, not debris). All four are
verified `parts=1`, 100 % coverage, all 14 regions, comfortably under cap. They're rendered on their
own large panels via `render_single.py`. The blends differ in *how* the spine is treated:

### 10 · Spinal Reliquary — *one straight keel, wings hung on catwalks, grav-shrine amidships*
**4,012 tiles · 788 headroom · 7 extenders · cargo 722 · farthest 30.0**

The **most literal merge.** It *is* the Spinal Freighter — one straight cargo keel, command bow,
thruster tail — but every production wing has been detached and **hung off the spine across a gap on a
1-tile catwalk** (the squared-off cousin of the Halo's tethers), and the belly amidships has been
**hollowed into a reliquary chamber** enshrining the grav-engine + scrap totems. Overshoot catwalks
dangle off the bow, the shuttle pod, and the stern. For: keeps the freighter's legibility and easy
hauling (short straight spine) while gaining the Halo's hung-pod modularity and central shrine; each
pod is a clean isolatable repair unit; lots of slack (788). Against: the least *eerie* of the four —
it still reads as a tidy freighter with detached wings rather than a haunted wreck.

### 11 · Ladder Halo — *twin rails, hollow void between, pods hung outboard, shrine in the void*
**4,313 tiles · 487 headroom · 9 extenders · cargo 400 · farthest 30.0**

Splits the single keel into **two parallel rails** with a **hollow dark void** running the length
between them, crossed by a few cargo **rungs** (the only things spanning the gap besides bow, stern,
and shrine). All ten pods hang **outboard**; the **shrine floats in the central void** with its totem
core; most inter-rail bays are deliberately left empty and eerie. For: the strongest *hollow-frame /
derelict monkey-bars* reading; the void is a natural heat-vent and firebreak; very symmetrical and
easy to reason about. Against: lowest cargo of the four (400 — the rails carry little bulk); the long
void means more walking; 9 extenders.

### 12 · Cross-Nave Cathedral — *cruciform hull, shrine at the crossing, pods off all four arms*
**4,475 tiles · 325 headroom · 8 extenders · cargo 752 · farthest 29.73**

A true **cruciform**: a long nave crossed by one transept, with the **shrine at the crossing** (the
sacred heart, dead-centre) and pods hung off **all four arms**. The transept tips are **end-chapels**
— habitat on one side, the enlarged white shuttle bay on the other. Overshoot catwalks dangle off all
four arm tips. For: the **boldest, most architectural silhouette** of the four and the most on-theme
for a Jawa relic-ship (an actual cathedral in the void); good cargo (752); the four arms give four
natural fire-compartments around the shrine. Against: the widest footprint (two axes), so it's the
least compact; tightest slack of the four (325); the transept makes it read less like "a spine ship"
and more like its own thing (which may be exactly what you want).

### 13 · Broken Keel Halo — *keel snapped in three, dog-leg catwalk bridges, shrine in the middle*
**3,999 tiles · 801 headroom · 7 extenders · cargo 698 · farthest 29.83**

The **most derelict reading.** The keel is **snapped into three segments** separated by real gaps,
each gap re-joined *only* by a **strange offset dog-leg catwalk** (kink right, then kink left — never
a clean straight rung), so the ship looks like it broke apart and was lashed back together. The
**shrine sits in the middle segment**; pods hang off all three; overshoots dangle off the bow, the
shuttle, and the stern. For: the closest in *spirit* to the Derelict Halo — the "why is it in pieces"
mystery, now rectilinear; each segment is a self-contained module (superb repair-gate mapping — a
segment can be isolated wholesale); the most coverage slack of the four (801). Against: the segment
gaps mean the longest internal travel (cross the dog-legs to move fore-aft); the bridges are thin
single-tile chokepoints (a risk if raiders breach one).

*Rendered on their own large panels:* `src/RimMandrake/mapsynth/runs/design_10_spinal_reliquary_large.png`,
`design_11_ladder_halo_large.png`, `design_12_cross_nave_large.png`,
`design_13_broken_keel_halo_large.png`.

---

## The Falcon Halo (#14)

*Added 2026-08-06 at user request: "start again with the **Large Halo (non-derelict)** and
intelligently add some circles **semi-embedded in the outside of the ring** … with **one primary long
arm coming out and forward similar to the Millennium Falcon's design.**"* This is the Halo ring at
**full health** — the working sibling of #9, not the haunted wreck.

### 14 · Falcon Halo — *a clean cargo wheel, pods sunk into the rim, one long forward mandible arm*
**4,410 tiles · 390 headroom · 7 extenders · cargo 1,319 · factory 1,182 · shuttle 441 · farthest 30.89**

A solid cargo **wheel**: a thin rim band of cargo, a **central shuttle-hangar hub**, and four clean
5-wide **spokes** joining hub to rim (so the interior is a working cross, *not* the Derelict Halo's
hollow void). Eight circular **function-pods are sunk half-into the OUTER edge of the rim** — each
disk is centred just inside the rim so its inner half merges with the band (structurally continuous,
no tethers or spokes) while its outer half bulges past the hull. The eight pods are placed **with
purpose**: the hot/dirty wings (adv-materials, bulk) and the raw-extraction/food/textile wings ring
the rear and sides near the thrusters, while **habitat** and the **carbonite scrap-shrine** sit on the
forward flanks. The three remaining cardinal system blocks (thrusters aft, fuel port, water starboard)
are set into the band. The forward arc of the rim is left clear for the **Falcon arm**: a solid neck
off the rim **forks into two mandible prongs** around an empty front notch, and the **command cockpit**
juts off to **starboard** on a short tube — the Falcon's signature offset cockpit. For: **by far the
largest cargo of the whole set (1,319)** with strong factory too (1,182) — a genuine
hauler-industrial; the most immediately recognizable *Star Wars* profile; the embedded pods are clean
isolatable repair units without the fragility of long tethers; the central hangar is a natural muster
point. Against: tightest-but-one slack (390 headroom) — the solid wheel is tile-hungry, so it shrank
from the first cut; the offset cockpit is a slightly exposed command node at the end of a thin tube;
the forward notch is cosmetic (empty space) rather than functional.

*Rendered on its own large panel:* `src/RimMandrake/mapsynth/runs/design_14_falcon_halo_large.png`.

### 15 · Falcon Halo (hollow) — *hollow shrine-heart, shuttle bays out on the mandible tips*
**4,057 tiles · 743 headroom · 7 extenders · cargo 1,443 · factory 1,182 · shuttle 420 · farthest 29.83**

*User revision of #14, 2026-08-06: "keep it, but move the shuttle bay out to the end of those strange
arms and leave the centre empty as before."* Identical clean cargo wheel, rim-embedded pods, and
Falcon mandible arm — but the **central hangar hub and its four spokes are gone**, so the interior is
a **hollow void** (the Derelict Halo treatment) holding only the **grav-engine core + the worshipful
scrap-totem shrine** at dead centre, reached by a **single rear causeway**. The **shuttle bay flares
off the tips of the two mandible prongs** (a hangar pad capping each arm; the front notch between them
stays open), putting the ship's dock at the very prow. Command stays on the offset starboard cockpit.
The carbonite shrine moved from a rim pod to the centre, so the **rim now carries seven** embedded
pods instead of eight. For: keeps the iconic Falcon profile while restoring the eerie hollow heart you
liked in #9; **the most cargo of the entire set (1,443)** — hollowing the hub and dropping to seven
pods actually *freed* rim volume; the most coverage slack of any near-complete design (743); the
forward shuttle pads are a dramatic, thematic prow. Against: the void means longer internal travel and
a single causeway to the shrine (a chokepoint by design); the shuttle bays and cockpit are all clustered
at the exposed forward arms — a lot of critical function far from the hull's mass.

*Rendered on its own large panel:* `src/RimMandrake/mapsynth/runs/design_15_falcon_halo_hollow_large.png`.

---

## Decision — RESOLVED

**The decision this served:** which hull silhouette to commit to before the tile-level blueprint and
the (still-blocking) start-save authoring work. **Resolved 2026-08-06 → #15 Falcon Halo (hollow).**
`ship_deck_plan.md`'s repair gate, heat doctrine, and campaign hooks now apply to that hull; the
remaining designs are kept below only as the exploration record. Everything after this table is the
comparison as it stood at decision time.

**Comparison at a glance** (verified from `designs_report.json`):

| # | Form | Tiles (head) | Ext | Cargo | Factory | Shuttle | Asymmetric? | Open space | Authoring difficulty |
|---|------|-------------|-----|-------|---------|---------|-------------|-----------|----------------------|
| 1 | Spinal freighter | 4499 (301) | 5 | 702 | 1404 | 234 | no | none | easiest (rectangular) |
| 2 | Nebulon-B | 3741 (1059) | 4 | 562 | 1754 | 126 | fore/aft | none | medium |
| 3 | Corellian corvette | 3849 (951) | 4 | 616 | 1080 | 189 | mild (bow) | none | hard (round bow) |
| 4 | Catamaran | 4113 (687) | 4 | **970** | 1174 | 122 | no | **2 courts** | medium |
| 5 | Ring station | 4702 (98) | 6 | 421 | **2537** | 185 | no | **hangar** | hardest (ring) |
| 6 | Salvage hulk | 4604 (196) | 4 | 622 | 1700 | 288 | **yes (L/R)** | derelict gap | medium |
| 7 | Nodal station | 4607 (193) | 9 | 357 | 1107 | **357** | **yes (spokes)** | **inter-spoke** | hard (spokes) |
| 8 | Ring-and-spur | 3837 (963) | 10 | **1279** | 894 | 317 | **yes (pods)** | **ring core + gaps** | hard (ring+pods) |
| 9 | Derelict halo | 4228 (572) | 10 | 1092 | ~330 | 317 | **yes (tethered pods)** | **hollow core + void** | **hardest (curved-tether pods)** |
| 10 | Spinal reliquary | 4012 (788) | 7 | 722 | ~1100 | 317 | no | shrine + gaps | medium (straight keel) |
| 11 | Ladder halo | 4313 (487) | 9 | 400 | ~1100 | 317 | no | **central void** | medium (twin rails) |
| 12 | Cross-nave | 4475 (325) | 8 | 752 | ~1100 | 317 | no (cruciform) | **crossing + arms** | hard (two axes) |
| 13 | Broken keel | 3999 (801) | 7 | 698 | ~1100 | 317 | **yes (segments)** | **segment gaps** | medium (dog-legs) |
| 14 | Falcon halo | 4410 (390) | 7 | 1319 | 1182 | 441 | **yes (Falcon arm)** | **hangar hub** | hard (wheel + arm) |
| 15 | Falcon halo (hollow) | 4057 (743) | 7 | **1443** | 1182 | 420 | **yes (Falcon arm)** | **hollow shrine-heart** | hard (wheel + arm) |

**Tradeoffs, distilled:** *most cargo* → **15** (Falcon Halo hollow, 1,443), then **14** (Falcon
Halo, 1,319) and **8** (Ring-and-Spur, 1,279); *most factory* → **5** (Ring), then **2** (Nebulon-B); *most
shuttle capacity* → **14** (441, central hangar), then **7** and **6**; *asymmetry* → **6**
(side-to-side wreck), **7** (radial spokes), **8** (irregular ring pods), **14** (the Falcon arm),
**2** (fore/aft); *courtyard / open space* → **4** (twin courts), **5** / **14** (central hangar),
**7** (inter-spoke voids); *most on-theme wreck* → **6**; *most iconic Star Wars reading* → **14**
(Falcon profile) and **3** (corvette); *ring silhouette* → **5** (symmetric), **8** (broken-symmetry),
**9** (hollow derelict wheel), or **14** (clean working wheel + forward arm); *most atmospheric /
set-piece* → **9** (floating pods + shrine core); *easiest to hand-author* → **1**; *hardest* → **9**
(disconnected floating pods). Coverage slack (room to tweak later) is best
on **2** (1,059), **8** (963), **3** (973) and **9** (614), tightest on **5** (98).

**Dependencies:** the chosen hull inherits the substructure math, the `ship_deck_plan.md` repair gate
+ heat doctrine, and the desert / VGE / faction layers. It requires **Bigger Gravships** (approved)
configured to at least the assumed sliders; **the real slider ceilings are not yet confirmed**
(Fetcher pending). #15 is comfortable here — 4,057 tiles (743 headroom) and only **7 extenders** — so
it survives a moderately tighter cap; the first thing that would bite is `N_EXT` if the mod caps it
below 7, or `R_EXT` if the pods/arm tips fall out of reach. **Re-validate #15 against the real numbers
when the Fetcher result lands, before any authoring.**

**Principal risks (for the chosen #15):** (a) the expanded limits are *assumed*, not verified — the
Fetcher result could force a re-tune, though #15's 743-tile slack and 7 extenders give it a good
buffer; (b) start-save authoring of a large pre-broken hull is still the one true blocker regardless
of shape, and the wheel + rim-embedded pods + forked arm make #15 a genuinely fiddly hand-place (the
Falcon arm tips and the seven rim discs each need care); (c) #15 clusters critical forward function
(both shuttle pads + the offset cockpit) out on exposed arms, and the shrine sits behind a single-
causeway chokepoint — deliberate, thematic, but worth remembering when the deck plan places defenses.

**Missing info that would help:** the real Bigger Gravships slider ranges (pending Fetcher) — the last
open input before #15 can be authored with confidence.

**Why #15 (decision rationale):** it lands the crashed-Factory-ship / Jawa-salvage theme *and* the
most iconic Star Wars silhouette in one hull — a clean working wheel with a Millennium-Falcon mandible
arm — while restoring the eerie hollow shrine-heart the user liked in #9. It also carries the **most
cargo of the entire set (1,443)** with strong factory (1,182), and its rim-embedded pods are clean,
isolatable repair units that map neatly onto the wing-by-wing repair gate. The earlier front-runners
(#6 Salvage Hulk for pure theme, #8 Ring-and-Spur for cargo, #9 Derelict Halo for mood) are all folded
into #15's strengths.

**Next step:** draw the tile-level interior blueprint for **#15** against the cap (the coastal_mesa
treatment), and it is now folded into `ship_deck_plan.md` [DECIDE B]. When the Fetcher slider ranges
land, re-validate #15 against the real numbers before any authoring.

---

## File map (for a clean restart)

- `src/RimMandrake/mapsynth/ship_designs.py` — Canvas + coverage verifier + shared palette (`COL`/`LABEL`) +
  limit constants (VANILLA vs EXPANDED). Helpers: `octagon()`, `spoke()` (straight), and — new for
  #9 — `arc()` (curved corridor: walks an angular span at a radius, lays backbone on the centerline)
  and `line_backbone()`.
- `src/RimMandrake/mapsynth/build_designs.py` — the 15 design functions (incl. `d_falcon_halo` #14 and the CHOSEN
  `d_falcon_halo_hollow` #15, plus the `_embed_pod` rim-sinking helper), the 14-region `REQUIRED`
  check, runs verify + tally, writes grids (`design_*.npy`), placements (`design_*_place.json`), and
  `designs_report.json`.
- `src/RimMandrake/mapsynth/render_designs.py` — composites the black 8-panel comparison sheet with legend +
  per-panel coverage halos and stats. Outputs `ship_designs_comparison.png`.
- `src/RimMandrake/mapsynth/render_single.py <name>` — renders ONE design as a large standalone sheet with ~3×
  fonts + bigger tiles (built after "text too small" feedback). Outputs `design_<name>_large.png`.
  The chosen hull renders via `render_single.py 15_falcon_halo_hollow`.
- `src/RimMandrake/mapsynth/runs/designs_report.json` — verified numbers per design (source of every stat above).
- `src/RimMandrake/mapsynth/runs/ship_designs_comparison.png` — the 8-panel deliverable image (designs #1–8).
- `src/RimMandrake/mapsynth/runs/design_15_falcon_halo_hollow_large.png` — the **CHOSEN** hull rendered large & readable.
  (`design_9_derelict_halo_large.png` and `design_14_falcon_halo_large.png` are kept for reference.)

To regenerate everything: `cd player_maps && python3 build_designs.py && python3 render_designs.py &&
python3 render_single.py 15_falcon_halo_hollow`.
