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
- 🔴 **Lush flora only in the water-high biomes** (owner, 2026-09-05).
