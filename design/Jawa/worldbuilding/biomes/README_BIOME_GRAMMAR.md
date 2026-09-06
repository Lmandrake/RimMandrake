# Biome definition sheets — the grammar

_Owner + BENCH, 2026-09-05. Owner: "Pick principles that drive the local reasoning
and then populate to them... make biomes that radiate a powerful artistic theme and
pseudo alien biological reasoning."_

## The generative rule: **energy regime × local anomaly**

Two measured facts about Ash'karr drive everything (`the_one_map.md`):
1. The tidal lock is a **POINT**, not a latitude band — θ=0° substellar, θ=180°
   antistellar, the torn seas around **θ 63-117°**.
2. 🔴 **Concentric biome rings about the substellar point are FORBIDDEN.** A
   bullseye planet is explicitly ruled out.

Those two are in tension: the physics wants rings, the aesthetics forbid them. That
tension IS the design engine:

> **θ sets the ENERGY BUDGET. TEMPERATURE sets what METABOLISM is possible.
> A local ANOMALY sets the IDENTITY.**
> Rings never form because the anomalies are scattered.

**Three axes, not two (owner, 2026-09-05):** temperature is *similar to θ but
independent of it* — altitude, wind, water and venting all decouple the two. It is
its own axis because it decides two things θ cannot:
1. **Which metabolisms are chemically available at all** (a reaction that runs at
   40 °C may simply not run at −40 °C, whatever the energy budget says), and
2. **Which non-biological processes are at work** — frost shatter, evaporation,
   sublimation, clathrate stability, what the wind can carry.

A biome is a *reasoned intersection* of a regime, a temperature, and an anomaly.

**Energy regimes** — deep dayside (eternal noon, no diurnal cycle at all) · mid
dayside · **terminator band** (permanent low-angle light, the water, and the
day→night convection winds) · deep nightside (eternal dark, geothermal only).

**Anomalies that break the ring** — water · volcanism/vents · altitude · impact
scars · chemistry · wind corridors · and, uniquely to this world, **ancient wreck
fields**: on a scavenger planet, crashed tech is a legitimate ecological substrate.

A biome is a *reasoned intersection* of one regime and one anomaly. If you cannot
name both, the biome has no driving force and its art will drift ordinary — which
is exactly what went wrong with the poison forest.

## The sheet template (nine fields)

1. **What it is** — one paragraph, the place as a person would describe it.
2. **Planetary position** — the θ band + the anomaly. *(Added: this is what makes
   the reasoning derivable rather than decorative.)*
3. **Driving forces** — the physical/chemical engine, in one sentence.
4. **How the biology adapted** — the consequence. Mechanism, not adjectives.
5. **Always true** — invariants.
6. **Never true** — 🔴 HARD BANS, written checkable (owner's ruling): a linter must
   be able to flag a def that violates one.
7. **Uniquely available** — what only this biome gives the player.
8. **Inhabited objects** — what structures, ruins and wrecks occur, and why here.
9. **Artistic theme** — palette, silhouette language, quality of light. The thing
   that makes it *radiate*.

## The sheet drives the roster (owner's ruling)

The definition is the **admission test**. Nothing lives in a biome that its
reasoning does not justify — flora and fauna are populated TO the principles, not
inherited from whatever mod shipped them. Two standing bans apply everywhere:

- 🔴 **The recognizability rule** (`creature_recognizability_rule.md`): if a player
  can instantly name what it is meant to be, it does not belong on this planet.
- 🔴 **THE LUSH RULE, three-part** (owner, 2026-09-05 — corrected; an earlier
  "lush = water-high biomes" phrasing was WRONG and is struck):
  1. **Dayside: lush exists ONLY along rivers and coasts.** It is a THIN LINE on
     the map, never a region — a green edge against the vast empty dune. Away from
     water there is nothing.
  2. **The terminator is NOT lush. It is SOLITARY.** Its character is sparse,
     lonely and singular; never write it as an abundant green belt.
  3. **The nightside has a DIFFERENT definition of lush** — dense, but built of
     very alien life forms rather than green plants. A future nightside-lush biome
     is the owner's stated intent.


## 🔴 The Star Wars icon carve-out (owner, 2026-09-05)

> "Iconic Star Wars status protects completely."

The recognizability rule disqualifies **terrestrial** referents, never in-universe
ones. A bantha, a dewback, an astromech reading as exactly what it is *is the
campaign working*, not a violation. Iconic Star Wars creatures and droids are
exempt from the cut rule outright — and their recognizability is an asset to be
sought, not a defect to be corrected.

---

## Progress — which biomes are defined (updated 2026-09-05)

The owner works these **one at a time, in conversation**: BENCH opens with where the biome
stands and a proposed driving mechanism, the owner rules and adds, one more pass, done.
Order is by **similarity — slowly vary** (owner, 2026-09-05).

| sheet | biome def | status |
|---|---|---|
| `poison_forest.md` | `PoisonForest` | ✅ done |
| `dune_sea.md` | `ExtremeDesert` (Dune Sea) | ✅ done |
| `terminator_sea.md` | the three seas | ✅ done |
| `nightside_ice.md` | nightside | ✅ done |
| `fall_line.md` | **injection layer** over `ExtremeDesert` | ✅ done — no new BiomeDef |
| `deep_desert.md` | `ExtremeDesert`, far ring | ✅ done |
| `desert.md` | `Desert` | ✅ done |
| **arid shrubland** | `AridShrubland` | 🔵 **NEXT — opened, awaiting the owner** |
| `wreck_fields.md` | — | ⛔ superseded by `fall_line.md` |

### 🔑 The dryland ladder is ONE number: the sun's angle

Sun elevation is `90 − arc`; insolation scales as its sine. This is the instrument that
generated the deep desert and desert sheets and it should generate the rest.

| biome | sun above horizon | insolation vs overhead | shadow length | hilliness | temp |
|---|---|---|---|---|---|
| `ExtremeDesert` | 47.4° | 74% | 0.9× height | 1.0 | 48.3 °C |
| `Desert` | 14.4° | 25% | 3.9× height | **2.0** | 24.5 °C |
| `AridShrubland` | 9.2° | 16% | 6.2× height | 1.0 | 20.9 °C |
| `Wasteland` | −9.9° | 0% | — | 1.0 | 0.5 °C |

**Deep desert** = absence (distance from water). **Desert** = the shade economy, because the
terrain is hilly enough to cast shadows and the sun is high enough to make them matter.
**Arid shrubland** = where the shade economy *ends* — the terrain flattens again and the sun
drops to 16% of overhead, so nothing has to hide any more. That is the proposed hinge, put to
the owner 2026-09-05 and **not yet ruled**.

### Where arid shrubland was left

Opened with the owner; his answer is owed. Proposed:
- **The first ground on the dayside where you don't have to hide** — which is why vegetation
  is continuous and why it is a shrubland rather than another desert.
- **The inversion:** both deserts have total visibility and threats at known fixed positions.
  This is the first biome with **cover**, so the danger stops being the ground and becomes
  **concealment** — something can be near you without your knowing.
- It is **low and flat at the terminator's edge** (median arc 80.8, median elevation 21.5 m,
  largest region literally named **Damp** at arc 90.0), so R-H2b's condensation — the second
  water source — begins to reach it.
- ❓ **Open question put to the owner:** the poison forest is toxic because condensation
  deposits the dayside's airborne filth and nothing washes it away. Arid shrubland is upwind,
  on the approach. **Does the taint start here in a mild early form, or is this the last clean
  ground before it?**
- ⚠️ The def is scattered worse than `Desert` was — arc 15.6→112.5, −14.7→59.6 °C, with 45
  tiles at 57 °C in the Dune Sea. Same class of defect as `WORLDMAP_DESERT_BAND_REPAIR_1` and
  probably folds into that same bridge session.
