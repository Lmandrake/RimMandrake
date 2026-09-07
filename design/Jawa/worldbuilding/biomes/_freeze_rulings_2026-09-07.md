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

---

## R5 — FUEL: THE FINDING IS REJECTED. TWELVE SOURCES ARE EVIDENCE OF SCARCITY

**Ruled: there is no oversupply.** The review over-estimated **access and
availability**, not count. Owner, 2026-09-07: *"the fact that people have found
SO MANY ways to get fuel is still evidence of its scarcity."* A scarce resource
is exactly the one a population invents twelve marginal routes to.

🔑 **The gate is ACCESSIBILITY, and it is ruled per source.** No sheet loses its
economy; none of these is a major source save the Propane Lakes:

| source | why it is not a supply |
|---|---|
| **Propane Lakes** | the one real source — and **inaccessible until very late game**: terminator shock passage, extreme-cold safety |
| **Tar** | not fuel — must be **processed**, on machinery found only in some tar-containing squares (injected by *inhabited*), and it is **slow**; the player cannot stay long |
| **Sap-chemfuel** | not player-tappable — a **settlement-level investment** |
| **Seep oils** | slow seeps, hard to gather |
| **Tree liquors** | **fermentation-scale** production; not ship-friendly |
| **Blastpods** | wild; a minor input at best |
| **Tholins** | atmospheric **nanoparticles, unharvestable** — a similar keyword, not a fuel; contributes nothing to this story |
| **Venomvine** | becomes wood only over **timescales beyond the game** |
| **Glower / hydrocarbon flora** | harvestable, but slow and **very late game** |
| **Wick-plants** | sited in **one of the nastiest places on the map** |

⚠️ **And by the time the Propane Lakes are reachable, fuel scarcity SHOULD NOT be
the driving limiter** — the player is getting ready to win.

**Amends:** nothing is cut. Each sheet gains (or keeps) its accessibility clause;
`the_propane_lakes.md` keeps its premium, now explicitly a LATE-GAME premium.
**Doctrine this establishes:** before filing an oversupply finding, count
*reachable* supply, not sources. Twelve hard routes is scarcity.

---

## R6 — THE WATER TRUCE HOLDS WHERE THERE ARE OPEN SIGHTLINES

**Ruled:** the truce's mechanism is **distance you can see coming**. It holds on
open water where animals can watch each other and keep their spacing. In
enclosed water — slot canyons, walled cracks, roofed pools — there is no
distance to keep, so the truce **cannot** hold.

Derives `the_cracked_lands.md`'s 27 water tiles automatically, rules every
future enclosed water without a list, and makes the Cracked Lands the planet's
**one lethal water**.

**Amends:** the truce's statement in the world-def (add the sightline
mechanism); `the_cracked_lands.md` cites the rule instead of asserting a bare
exception.
**Owed at the roster pass:** which other biomes have enclosed water (the Sump,
the Lantern Deeps, canyon reaches of any river).

---

## R7 — THE PYRELANDS: THE FIRE IS THE SETTLEMENT BAN

**Ruled:** periodic burns destroy anything that cannot move — **no permanent
structures, no stored harvest, no walls.** Only **nomadic fire-followers** work
the Pyrelands, timing their circuit to the burn cycle. The richness stands
exactly as written; the scarcity premise is protected; the Pyrelands is a place
you **visit**, not settle.

**Amends:** `the_pyrelands.md` (state the ban and its mechanism), and the
settlement pass — **no permanent settlement may be sited in the Pyrelands.**

---

## R8 — DAYSIDE VAPOUR: "NEVER CONDENSES AS RAIN"

**Ruled:** the minimal amendment. `terminator_sea.md`'s sentence becomes
*"never condenses **as rain**"* — dew and fog are unaffected, and the Weeping
Stones / arid shrubland condensate economies stand.

**Amends:** `terminator_sea.md`, one sentence.
⚠️ **Deliberately left open:** WHERE dayside dew forms (open sand? stone? shade?)
is not ruled. The roster pass will have to answer it to site condensate flora.

---

## R9 — ⭐ WE DO NOT CROWN THINGS. DESCRIBE THE MECHANISM INSTEAD

**Ruled, and this is general doctrine, not an archive fix.** Owner, 2026-09-07:
*"We don't need any of these superlatives... We don't need to go around crowning
things for the planet."*

🔑 **The replacement is descriptive prose that states the MECHANISM and lets the
reader compare.** His own examples, as the pattern to write to:

- the cold preserver → *"acting like a deep record of all who fell here, so long
  as they survive the brutal dry freezing"*
- the tar → *"entombs all who fall into it, preserving their hard structures far
  into the future"*
- the Slime → **not "archive" at all**: *"living, flowing genetic database"* —
  which *"is more accurate than archive anyway."*

⛔ **This retires the whole SUPERLATIVE CROWNS card group** — the review's
finding #18 and its ten double/triple claims, #29's terminator "only"s, #13's
"the mod's fastest disease clock", #12's sickest-air trio, #15's wood monopoly,
#26's "only surface water", #20's "only seismically active province". **None of
them needs a crown ruling. Each needs its superlative rewritten as a
mechanism.** No sitting time is owed to deciding who wins; the work is prose.

**Amends:** every sheet carrying an "only / the planet's / the most / the
fastest" claim. The rule for the rewrite: say what the place DOES and why, and
never rank it against the rest of the planet.

---

## R10 — THE WILDSTEAM: THE GREENTIDE IS HOME, THE REST ARE HOLDINGS

**Ruled:** the Greentide is home ground and holds the **capital** — it already
carries two seats on the owner's own coordinates (Oilpalm and one more), the
strongest existing commitment. The others are demoted to holdings:

- **Sporefall** (Fever Wood) — the **beloved second city**, a stilt-built
  treetop town; a jewel, not the seat.
- **The Miasma seat** — the cool-weather retreat and first coastal foothold.
- **The Webwork seats** — the war front, ringing the Webwork's Scald side.

**Amends:** `the_greentide.md` (name the capital), `the_fever_wood.md` (Sporefall
is second city; its "home-canton preference" question for the Wednesday sitting
is now ANSWERED — remove it), `the_miasma.md`, `the_webwork.md`.
**Feeds:** the settlement pass, directly.

---

## R11 — THE WARDENS: ONE LIFECYCLE, A MIGRATION BETWEEN TWO BIOMES

**Ruled:** wardens **breed and are born in the Miasma's mangal nurseries**,
spend their **adult lives in the Grey Deep as the brine adults**, and **return to
the Miasma to die** — the elders too brine-broken to go back out become the
**warden mothers** guarding the next crèche.

Both sheets stand with one line each, and the planet gains a migration worth
more than either sheet alone.

**Amends:** `the_miasma.md` (the mothers are the END of the cycle, not the
species), `the_grey_deep.md` (its giant is paired against adults on their ocean
ground), and `sea_beasts_roster.md`.
**Owed:** a stated route between the Miasma delta and the Grey Deep.

---

## R12 — GEOTHERMAL: A DENSITY FIELD, NOT AN EXCLUSIVITY CLAIM

**Ruled: the question was never which province owns volcanism.** Owner,
2026-09-07: *"we should compute a density, a likelihood, of geothermal geysers
and other vents that decreases as you move away from mountain ranges on the
dayside and drops to zero on the terminator for sure. Just as a guide to prevent
the utterly random distribution currently observed... It's mostly about
preventing them from spawning on every map as they do now."*

**So the deliverable is a FIELD, not a sentence:**

- **likelihood is highest at/near dayside mountain ranges**, and **decays with
  distance** from them;
- **zero at the terminator**;
- it exists to stop geysers appearing on **every** map, which is the observed
  defect today.

⛔ **The Forge's "only seismically active province" is struck under [R9] anyway**
— it is a crown. The Forge is where the field is densest; it does not own the
mechanism.

**This is a BUILD item, not a prose amendment** — geysers are placed by RimWorld
mapgen per map, so honouring the field means constraining that placement.
**Amends:** `the_forge.md`, `the_scald.md`, and the Anvil seep lines, each to
cite the field rather than claim or deny exclusivity.
