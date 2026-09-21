# EXTREME_DESERT_GIANT_COMMENSALS_1 — shade-commensal micro-fauna under giants

## what is wrong

dune_sea.md §4 ("the giants carry the only moving shadows on the planet, and
there is an ecology living in them") describes two mechanics with no def and
no item:

1. **The mirror-plated sun-axis giant** — the walking mountain whose moving
   shadow the commensals live in. `RUT_ExtremeDesert` already carries three
   giants (`RSW_KraytDragon`, `RSW_GreaterKraytDragon`, `RSW_WarWyrm`), but
   none is confirmed sun-axis-polarised (mirror/ceramic sun-face, all soft
   parts on the shade-face — dune_sea.md §4's hard ban 4, "no radially
   symmetric organisms") — that needs checking against each one's actual art
   before deciding whether an existing giant qualifies or a new one is owed.
2. **The shade-commensal micro-fauna** — grain-scale life that shelters
   under, rides, and follows a giant's shadow. Design-only per the item's own
   original scope: this needs a **shade-FOLLOW** behavior (track a specific
   moving shade source, not just seek the nearest shaded cell), which is a
   different, harder C# problem than `DESERT_SHADE_GRID_KEYSTONE_1`'s static
   `ShadeAt(IntVec3)` query.

## now unblocked

`DESERT_SHADE_GRID_KEYSTONE_1` closed 2026-09-20 this session
(`50c022770`): `RM_MapComponent_ShadeGrid.ShadeAt(IntVec3)` exists,
feature-gated, with two consumers (shade-seeking wander, a shade-driven
hediff decay rate). This item's hard dependency is satisfied — the commensal
mechanic can now be *designed* against a real API instead of a hoped-for one.

**⚠️ `ShadeAt` alone is not enough to build the commensal mechanic.** It
answers "how shaded is this cell right now", a static per-tick query. "Follow
this specific giant's moving shadow" needs either (a) a per-giant tracked
shadow-caster component the commensal's AI queries directly (bypass the
map-wide grid, cheaper and more precise for a 1:1 follow relationship), or
(b) `ShadeAt` plus a proximity/most-recently-darkened heuristic (cheaper to
build, less precise — a commensal could "follow" the wrong giant's shadow
if two cross paths). This decision belongs to whoever builds the mechanic,
not this design item, but both routes are cheap now that the grid exists at
all.

## the design question this item leaves open

- Which giant is the sun-axis host: an existing RUT_ExtremeDesert giant
  (reskin/verify) or a new mirror-plated chassis authored to the letter of
  §4's sun-face/shade-face split? A reskin is cheaper; a new chassis is more
  faithful if none of the three existing giants was built sun-axis-polarised.
- What are the commensals themselves — reuse an existing grain-scale desert
  species (e.g. from the already-ported roster) given a shade-follow
  behavior, or author new ones? The sheet doesn't name specific creatures,
  only the ecological role.
- Gameplay hook: §4 states "a caravan that stays in the shade of a walking
  mountain travels; a caravan that does not, does not" — this implies a
  player-facing mechanic (a buff/speed effect for staying in a giant's
  shadow), not just cosmetic commensal fauna. Confirming whether that
  player-facing half is in this item's scope or a separate one is itself an
  open question, not decided here.

## verify

This item exists, is `## needs: offline` (design, not owner — no card is
required to keep designing this; a card may be needed later once a specific
creature/mechanic choice is proposed), and names `DESERT_SHADE_GRID_KEYSTONE_1`
as a satisfied hard dependency plus the open design questions above.

## criteria

The giant-commensal mechanic is a filed, correctly-sequenced item with a
real, unblocked C# foundation to build against — not an unfiled note waiting
on infrastructure that no longer needs building.

## second consumer, added 2026-09-20 (COMMISSION_LEDGER_CLEANUP_1)

`DESERT_GLITTER_BIRDS_COMMENSALS_1` wants the identical shade-FOLLOW
mechanism for the desert's own megafauna (`RSW_ShadeWhale`, landed same
pass) rather than the extreme-desert giants this item covers. Whoever builds
the shade-follow route here (tracked shadow-caster vs. `ShadeAt`+proximity
heuristic) should build it as a shared mechanism with that item as the
second consumer, not have it re-derived independently.
