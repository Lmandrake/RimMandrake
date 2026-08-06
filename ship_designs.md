# ship_designs.md — Candidate gravship topologies (expanded limits)

_Design pass, 2026-08-06. Regenerated after **Bigger Gravships** was approved (WS 3522759531,
see `required_mods.md`). The mod is used here as a **design-time allowance** to loosen the
substructure limits so the ship can be a genuinely large, cool Star Wars silhouette — **not** to
enable in-game expansion. The anti-exponential pillar is still enforced by the repair-gate /
feedstock progression in `ship_deck_plan.md`, never by the tile cap. This doc owns the TOPOLOGY
MENU; `ship_deck_plan.md` still owns the repair-progression / heat doctrine that any chosen hull
inherits._

> **Deliverable images:** `player_maps/ship_designs_comparison.png` (the 8-panel comparison grid) +
> `player_maps/design_9_derelict_halo_large.png` (#9 rendered large & readable on its own panel).
> **Verifier:** `player_maps/ship_designs.py` + `build_designs.py` (regenerates + re-checks all nine).
> **Renderers:** `player_maps/render_designs.py` (grid) + `render_single.py <name>` (one large panel).

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
  irregular circular pods, but the pods are **free-floating** (NO radial spokes joining them to the
  ring); instead "strange" **curved perimeter walkways** arc around the *outside* of the hull, two of
  them **overshooting a little past everything into empty space** for reasons long forgotten. Nothing
  is straight. The interior is a **hollow void** except a **single spiral causeway** curving inward to
  the ship's heart: the **grav-engine core**, ringed by a small consecrated floor bearing the Jawa's
  **worshipful scrap totems** (the carbonite/sacred-scrap block). Needed a new curved-corridor
  primitive (`arc()` in `ship_designs.py`). Rendered as its own **large standalone panel**
  (`render_single.py`, ~3× fonts) after feedback that the grid text was too small. Net: **nine
  designs**, all 14 regions, all verified liftable.

---

## Limits used (and an honest caveat)

| | grav-engine radius | extender radius | max extenders | tile cap |
|---|---|---|---|---|
| **Vanilla (verified)** | 19 | 16 | 6 | 2,000 |
| **Expanded (used here)** | **34** | **30** | **12** | **4,800** |

**Caveat — provenance of the expanded numbers.** These are *generous assumed* values, chosen to
open up the authoring space, **not** yet read from the mod. The mod's real slider ranges were
requested via Fetcher (`2026-08-06_bigger_gravships_ranges`); when that lands I'll re-validate all
eight against the true min/max. The verifier is parameterized (`ship_designs.py` top block), so
re-checking against real numbers is a one-line change and a re-run. This is an **assumption**, not
established evidence — flagged so you can weight it accordingly.

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

The palette lives in `player_maps/ship_designs.py` (`COL` / `LABEL`), shared by verifier and renderer.

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

### 9 · Derelict Halo — *floating pods, curved perimeter walks, a shrine at the dead centre*
**4,186 tiles · 614 headroom · 10 extenders · cargo 1,165 · shuttle ~317 · farthest 29.83**

The **eerie sibling of #8.** Same monumental cargo ring with the core systems set into its band
(command / thrusters+power / water / fuel), and the same **eight irregular circular pods** for the
six factory wings + habitat + the enlarged white shuttle bay. But here the pods are **free-floating**
— **no radial spokes connect them to the ring at all.** They simply hang in the black, held to the
ship only by the grav field (the pale connection halos), never by a walkway. Instead, **"strange"
curved perimeter catwalks** arc around the *outside* of the hull — never straight, always arc-like —
and **two of them overshoot a little past everything, dangling off into empty space** for reasons
long forgotten. The whole interior is a **hollow void** save one thing: a **single spiral causeway**
that curves inward from the ring to the ship's heart at the dead centre — the **grav-engine core**,
ringed by a small consecrated floor bearing the Jawa's **worshipful scrap totems** (the black
carbonite / sacred-scrap block). That lone sacred path is the only thing that reaches the middle.

For: it is by far the most *atmospheric* and unsettling silhouette — a hollow derelict wheel with
organs floating around it and a shrine at its core, which is exactly the crashed-Factory-ship /
Jawa-salvage mood; huge cargo (1,165, second only to #8); the floating pods are the ultimate
isolatable units (each is a self-contained sealed room, maps perfectly onto the wing-by-wing repair
gate); the perimeter walks give a *lot* of exterior/defensible edge; comfortable coverage slack
(614). Against: it is **not physically sensible as a working ship** — pods you can only reach by the
grav field, not on foot, plus walkways that lead nowhere — so it is the **hardest to actually play**
(hauling, pathing, defence between disconnected pods) and the **hardest to hand-author**; light on
walkable connective floor; the "mysterious dangling" catwalks are pure flavour tiles. Best if: you
want a *set-piece / GM-mood* hull — a haunted salvaged wheel — and you're willing to trade practical
playability for the strongest possible atmosphere. (This one is more art object than optimised base;
if you love the look but want it playable, we can re-connect the pods with short curved skyways and
keep the shrine-at-centre motif.)

*Rendered on its own large panel:* `player_maps/design_9_derelict_halo_large.png` (built by
`render_single.py`, ~3× the comparison-grid font size for legibility).

---

## Decision translation

**The decision this serves:** which hull silhouette to commit to before the tile-level blueprint
and the (still-blocking) start-save authoring work. `ship_deck_plan.md`'s repair gate, heat
doctrine, and campaign hooks apply to *whichever* you pick.

**Comparison at a glance** (verified from `designs_report.json`):

| # | Form | Tiles (head) | Ext | Cargo | Factory | Shuttle | Asymmetric? | Open space | Authoring difficulty |
|---|------|-------------|-----|-------|---------|---------|-------------|-----------|----------------------|
| 1 | Spinal freighter | 4499 (301) | 5 | 702 | 1404 | 234 | no | none | easiest (rectangular) |
| 2 | Nebulon-B | 3741 (1059) | 4 | 562 | 1754 | 126 | fore/aft | none | medium |
| 3 | Corellian corvette | 3827 (973) | 4 | 660 | 1080 | 189 | mild (bow) | none | hard (round bow) |
| 4 | Catamaran | 4068 (732) | 4 | **970** | 1174 | 122 | no | **2 courts** | medium |
| 5 | Ring station | 4702 (98) | 6 | 421 | **2537** | 185 | no | **hangar** | hardest (ring) |
| 6 | Salvage hulk | 4604 (196) | 4 | 622 | 1700 | 288 | **yes (L/R)** | derelict gap | medium |
| 7 | Nodal station | 4607 (193) | 9 | 357 | 1107 | **357** | **yes (spokes)** | **inter-spoke** | hard (spokes) |
| 8 | Ring-and-spur | 3837 (963) | 10 | **1279** | 894 | 317 | **yes (pods)** | **ring core + gaps** | hard (ring+pods) |
| 9 | Derelict halo | 4186 (614) | 10 | 1165 | ~360 | 317 | **yes (floating)** | **hollow core + void** | **hardest (floating pods)** |

**Tradeoffs, distilled:** *most cargo* → **8** (Ring-and-Spur, 1,279), then **4** (Catamaran, 970);
*most factory* → **5** (Ring), then **2** (Nebulon-B); *most shuttle capacity* → **7** and **6**;
*asymmetry* → **6** (side-to-side wreck), **7** (radial spokes), **8** (irregular ring pods), **2**
(fore/aft); *courtyard / open space* → **4** (twin courts), **5** (hangar), **7** (inter-spoke
voids); *most on-theme wreck* → **6**; *most iconic Star Wars reading* → **3** (corvette); *ring
silhouette* → **5** (symmetric), **8** (broken-symmetry), or **9** (hollow derelict wheel);
*most atmospheric / set-piece* → **9** (floating pods + shrine core); *easiest to hand-author* →
**1**; *hardest* → **9** (disconnected floating pods). Coverage slack (room to tweak later) is best
on **2** (1,059), **8** (963), **3** (973) and **9** (614), tightest on **5** (98).

**Dependencies:** all nine inherit the substructure math, the `ship_deck_plan.md` repair gate +
heat doctrine, and the desert / VGE / faction layers. All nine require **Bigger Gravships**
(approved) configured to at least the assumed sliders; **the real slider ceilings are not yet
confirmed** (Fetcher pending) — if the mod can't reach r34/r30/12/4800, the near-cap designs
(5, 6, 7) shrink first. (#8 and #9 have more slack, so they survive a tighter cap; but their 10
extenders would be the first thing to bite if the mod caps `N_EXT` below 12.)

**Principal risks:** (a) the expanded limits are *assumed*, not verified — the Fetcher result could
force a re-tune (most likely affecting the near-cap designs 5, 6, 7, and the high-extender designs
7/8/9 if `N_EXT` is capped low); (b) start-save authoring of a large pre-broken hull is still the one
true blocker regardless of shape — the ring (5), the spoked station (7), the ring-and-spur (8), and
especially the **floating-pod halo (9)** are hardest to hand-place; (c) designs 5–7 have little
coverage slack, so any later deck-widening needs a re-verify; (d) **#9 is not physically playable as
drawn** — its pods are field-connected but foot-disconnected — so it's a mood/set-piece candidate
unless the pods are re-linked with skyways.

**Missing info that would help:** the real Bigger Gravships slider ranges (pending Fetcher); and
your priority weighting — *maximum cargo* (→8, then 4/9), *maximum factory* (→5/2), *the asymmetry you
called out* (→6 for side-to-side, 7 for radial, 8 for broken-ring, 9 for floating), *maximum
atmosphere* (→9), *a playable open courtyard* (→4/5), *the modular station look* (→7/8), or *the most
iconic silhouette* (→3).

**Recommendation:** for the crashed-Factory-ship / Jawa-salvage theme, **6 (Salvage Hulk)** remains
the strongest single pick — its missing/rebuilt section literally *is* the repair story. **7 (Nodal
Station)** and **8 (Ring-and-Spur)** are the boldest station-style options and map cleanly onto the
wing-by-wing repair gate (each pod/cell is an isolatable unit); pick 8 over 7 if you want a ring
silhouette and maximum cargo, 7 if you want the twin-nucleus industrial heart. If you want the most
balanced conventional ship, **3 (Corvette)** or **4 (Catamaran)**. If you want a pure *set-piece /
GM-mood* hull, **9 (Derelict Halo)** is the most evocative — a hollow salvaged wheel with organs
floating around it and a scrap-shrine at its core — but treat it as art unless the pods get re-linked
for playability. All nine are proven to fly; none is wrong — and I can **hybridize** further (e.g. a
salvage-hulk asymmetry with nodal cells on the rebuilt side, or a playable #9 with curved skyways).

**Recommended next step:** pick one (or ask for a hybrid), and I'll draw the tile-level interior
blueprint for it against the cap, then fold the choice back into `ship_deck_plan.md` [DECIDE B].
When the Fetcher ranges land I'll re-validate the chosen hull against the real numbers before any
authoring.

---

## File map (for a clean restart)

- `player_maps/ship_designs.py` — Canvas + coverage verifier + shared palette (`COL`/`LABEL`) +
  limit constants (VANILLA vs EXPANDED). Helpers: `octagon()`, `spoke()` (straight), and — new for
  #9 — `arc()` (curved corridor: walks an angular span at a radius, lays backbone on the centerline)
  and `line_backbone()`.
- `player_maps/build_designs.py` — the 9 design functions, the 14-region `REQUIRED` check, runs
  verify + tally, writes grids (`design_*.npy`), placements (`design_*_place.json`), and
  `designs_report.json`.
- `player_maps/render_designs.py` — composites the black 8-panel comparison sheet with legend +
  per-panel coverage halos and stats. Outputs `ship_designs_comparison.png`.
- `player_maps/render_single.py <name>` — renders ONE design as a large standalone sheet with ~3×
  fonts + bigger tiles (built after "text too small" feedback). Outputs `design_<name>_large.png`.
- `player_maps/designs_report.json` — verified numbers per design (source of every stat above).
- `player_maps/ship_designs_comparison.png` — the 8-panel deliverable image.
- `player_maps/design_9_derelict_halo_large.png` — #9 rendered large & readable.

To regenerate everything: `cd player_maps && python3 build_designs.py && python3 render_designs.py &&
python3 render_single.py 9_derelict_halo`.
