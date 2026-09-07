# Freeze-review card rulings — owner, 2026-09-07

Rulings on the cards raised by `_freeze_review_2026-09-07.md`
(item `BIOME_FREEZE_FABLE_REVIEW_1`). **These are decisive canon.** Each ruling
below amends the docs named under it; amendments add detail, they never change
the ruling. Propagation status is tracked per ruling.

---

## R1 — THE SCALD IS A PERCHED OCEAN THAT SPILLS THE WORLD'S RIVERS

**Ruled:** the lore is the perched ocean. The Scald's surrounding mountains are
the water sources; the Scald is that water captured into a vast crater at
altitude; **its outflow makes the rivers that nourish the world.** Period.

🔑 **The map's −350 m is an ENGINE ARTIFACT, not a fact about the world.**
Owner, verbatim: *"Rimworld maps cannot handle the concept of an ocean that is
at altitude. They MUST be at 0 as defined. The map requires the scald be below
in order to be considered ocean, thus we draw it that way."* The world-def sea
table records how the Scald had to be **drawn**; it is not evidence of what the
Scald **is**.

⛔ **This reverses `the_scald.md`'s "terminal pan: eight rivers end in it, none
leave."** The eight rivers are inflow from the ringing mountains; the Scald
spills outward, and the dayside's great rivers are its outflow.

⚠️ **General principle this establishes, wider than the Scald:** a value read
off the painted map may be a *representation forced by the engine* rather than a
measurement of the world. `canon.yml` rule 1 ("a MEASUREMENT of the painted
world beats any prose about the painted world") does **not** apply where the
engine could not represent the truth — there the ruling stands and the map is
the compromise. Before citing a map-derived number against a lore claim, ask
whether RimWorld could have drawn the lore claim at all.

**Amends:** `the_scald.md` (§ sea table reading, terminal-pan framing),
`the_one_map.md` (its spill paragraph is CONFIRMED, not superseded), and the
water-source lines of every sheet that took its water from elsewhere because the
Scald was read as terminal.
**Opens:** the river-graph work — which rivers leave the Scald, their courses
and their fates (see the `RIVER_LEDGER_1` recommendation).

---

## R2 — RIVER ENDS: THE ABSOLUTE IS STRUCK, THE DIRECTION OF TRAVEL IS KEPT

**Ruled:** strike the absolute "EVERY river dies in a sealed salt plain."
Rivers end where they end. **Qualifier, ruled with it: even the Grey Sea has
begun the journey towards salt flat itself.** The salt end is the planet's
direction of travel, not a law that every river has already obeyed.

**Amends:** the world-def and `wasteland.md` (strike the absolute, write the
direction-of-travel qualifier), `the_grey_deep.md` (the Grey Sea is salting —
it is early on the same road, not exempt from it).
**Stands as written:** the Miasma's rivers-reach-the-Grey-Sea, the Greentide's
river graves, the Scald's inflow.

---

## R3 — GROWTH LAW: A PRINCIPLED EXEMPTION, NOT A LIST

**Ruled:** the freak-growth law (R-H3) applies only where **water AND light are
both present**. Where either is missing, growth is normal-to-dormant. This
derives all six contested sheets (terminator_sea, nightside_ice, wasteland,
arid_shrubland, dune_sea, deep_desert) automatically and rules every future
biome without a maintained list.

**Amends:** R-H2b — replace the terminator-seam sole-exemption wording with the
water-and-light test. Each of the six sheets cites the rule rather than
asserting slow growth bare.
**Owed:** a one-line call on the edge cases where "lit" is arguable (the Sump,
the Lantern Deeps, anything roofed or submerged).

---

## R4 — THE PLANETARY WIND: TWO OPPOSED HADLEY CELLS, MEETING IN THE STORMWALL

**Ruled, and this is the decisive statement of Ash'karr's atmospheric
circulation. Owner's words, 2026-09-07:**

- **Dayside:** the dominant signal is **inward radial at surface level toward
  the subsolar point, and outward radial at high altitude.** This closes at the
  terminator in the Stormwall turbulence.
- **Nightside:** it is **reversed** — the wind **sinks at the antisolar point**,
  blows **along the surface toward the terminator**, **rises in the Stormwall
  turbulence**, and **returns radially towards the antisolar point at high
  altitude.**
- These are the **planetary-scale Hadley cells, colliding violently against each
  other in the Stormwall** — producing the atmospheric volatile precipitates,
  the lightning, the ship damage and the rest of the terminator's weather.
- **The superrotating wind is a PERIODIC ADDITION to this overall flow, at
  altitude.** It is *"one of the reasons it's not just a bullseye world: it is a
  perturbation to the overall radial story."* It is not the planetary wind and
  never was.
- **At surface level, local variation in elevation, hydration and other factors
  can dominate with local weather patterns — the most extreme of which are the
  high mountain ranges.**

**Settles, in one ruling:**
- The two-wind-field conflict — `dune_sea.md`'s radial inflow is the surface
  law; `deep_desert.md` / `fall_line.md`'s superrotation is real but is an
  aloft, periodic perturbation, not the grain-cutting wind.
- **Circulation closure**, previously written three different ways: the dayside
  cell closes **at the Stormwall**; the nightside cell sinks **at the antisolar
  point** and also rises at the Stormwall. Both "stormwall" and "antistellar
  point" sheets were half-right; "ends at the crags" is wrong.
- **Pyrelands ash reaching the desert against the surface wind** — it rides the
  outward-radial high-altitude return, and the superrotation perturbation
  redistributes it off the bullseye.
- **The anti-bullseye question** — superrotation is the named mechanism that
  keeps the planet from being a clean radial bullseye. `deep_desert.md`'s "far
  ring" wording is legal in substance under this ruling.

**Amends:** `dune_sea.md`, `deep_desert.md`, `fall_line.md`,
`arid_shrubland.md` (stormwall sink), `terminator_sea.md` + `nightside_ice.md`
(antistellar sink), `desert.md` (ash route), and the world-def's weather
section, which should carry this model in full as the single cited source.
