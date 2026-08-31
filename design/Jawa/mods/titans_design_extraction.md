<!-- status: live — design reference extracted from titans.fl before its retirement (MOD_LIST_OUTGROWN_AUDIT_2, owner ruling 2026-08-31). Not Star Wars canon; keep only the mechanism, not the mod. -->
# Titans mod — what made it scary, extracted before retirement

Owner's ruling, 2026-08-31: *"titans were actually scary unlike most rimworld
creatures. Read their stats and how they achieved this, record it, and
incorporate it into our own Star Wars creatures. Then retire. It's not Star
Wars canon."*

Source: `titans.fl` ("Titans" by FlatronWS), workshop id `3572242808`,
`Defs/ThingDefs_Races/Races_Animal_Titan.xml` — the mod's ENTIRE content.
**No C#, no Harmony, no Assemblies/ folder at all.** Every mechanism below is
plain XML fields, fully portable with zero engine-compatibility risk.

## The stat block (one race, `Titan`)

| field | Titan | Thrumbo (vanilla tank benchmark) |
|---|---|---|
| `baseBodySize` | 5 | 4 |
| `baseHealthScale` | **20** | 8 |
| `MoveSpeed` | **6.5** | 5.5 |
| `PainShockThreshold` | **0.95** | ~0.8 (vanilla default) |
| Natural armor (Sharp/Blunt/Heat) | **none** | 0.6 / 0.4 / 0.3 |
| `predator` / `maxPreyBodySize` | **true / 10** | false (herbivore) |
| `wildGroupSize` | **1-8 (pack)** | 1 (solitary) |
| `combatPower` | 300 | 500 |
| naive summed melee DPS (all tools, own cooldowns) | ≈42.9 | ≈49.8 |

**The load-bearing finding: per-hit numbers are NOT where the scariness
lives.** A single Titan is not mechanically scarier than a Thrumbo 1v1 — its
raw tool damage/DPS is lower. `combatPower` (the AI's own balance knob) rates
it BELOW Thrumbo. Whoever designed this did not "buff the numbers"; they
picked a different combination of ordinary knobs.

## The actual mechanism: five mundane multipliers stacked, not one big number

1. **Zero armor, pure-HP tanking** — a genuinely different survivability
   *shape* than Thrumbo's armor-deflection, not just a bigger version of it.
   2.5x HP with nothing to reduce incoming damage means every hit connects at
   full force but the creature absorbs far more of them before going down —
   reads as "grinding," not "impenetrable."
2. **Near-total pain immunity (0.95)** — removes the standard RimWorld
   tactic of wounding a target into submission before it dies. Most fights
   end at ~0.8 pain (unconscious); this one barely slows down until it is
   nearly dead outright.
3. **An opening hard-CC** — both fist tools carry a `surpriseAttack` bonus
   (`Stun 20`) alongside their normal damage. The FIRST hit a colonist takes
   can lock them down before they get a second action — a threat that is
   "over" for the victim on contact, not a war of attrition.
4. **Unprovoked active predation, upward** — `predator:true`,
   `maxPreyBodySize:10` (double its own size). It hunts, it does not merely
   retaliate — the danger exists before the player does anything wrong.
5. **Pack spawning (1-8)** — every mechanism above compounds across multiple
   bodies simultaneously. This is very likely the single biggest multiplier:
   a swarm of things that each stun-lock and shrug off wounding is a
   different fight than one big monster.
6. **Faster than a fleeing colonist** (6.5 vs ~4.6 sprint) — the counter-play
   "just run" is closed off, which is what makes 1-5 actually matter instead
   of being avoidable.

No unique ability, no armor penetration, no knockback, no terrain
destruction, no dread/fear aura, no bespoke sound design (it reuses vanilla
`Pawn_Bear_*` clips). The "scary" read is entirely emergent from stacking
ordinary fields differently than vanilla ever does at once.

## Portability to our Star Wars creatures — what to actually take

Every mechanism above is a plain field, safe to reuse without inventing new
C#:

- **Zero-armor/pure-HP as a SECOND tank archetype**, distinct from armored
  apex predators. Gives Law 3/Law 4's beast-normalization pass
  (`beast_normalization_spec.md`) a real second design lane: an apex beast
  can read as "hard to put down" via raw HP instead of always via armor —
  useful specifically because Law 4's thick-hide/armor register already
  covers the armored lane; a bare-HP apex avoids every SW beast converging
  on the same "shrugs off blasters" trick.
- **`PainShockThreshold` override** on a named apex tier — cheap, and a real
  point of difference from ordinary wildlife that never touches this field.
- **`surpriseAttack`/opening-hit stun** on a beast's best tool — matches Law
  3's own "burst lethality, not shredding" framing (the beast_normalization
  spec's own language) almost exactly; this is likely the single most
  reusable trick here.
- **`predator`/`maxPreyBodySize` tuned upward** for a named apex creature
  that should read as actively dangerous rather than merely defensive.
- **Pack-spawning apex tiers** (`wildGroupSize` > 1) as a deliberate design
  lever for a specific "swarm of dangerous things" encounter, used
  sparingly — this is the multiplier that does the most work and should not
  be the default for every apex beast.
- **Move speed above player sprint** as the gate that makes the rest matter
  — without it, the correct counter-play is always "disengage."

## What NOT to copy

- Nothing here — there is no C#/Harmony dependency to avoid, no
  Anomaly/Biotech-gated mechanic (the only `MayRequire="Ludeon.RimWorld.
  Odyssey"` tags are an optional biome entry and a trainable, both droppable
  with no loss of the mechanism).
- Do not copy the flavor (bear sounds, generic "Titan" naming, its own
  texture) — reuse the MECHANISM, author fresh SW-flavored content per this
  project's own naming/art pipeline.

## Status

Extraction complete. Per the owner's ruling, `titans.fl` retires from the
active mod list once this doc is committed — see `MOD_LIST_OUTGROWN_AUDIT_2`
and the packageId removal from `ModsConfig.xml`.
