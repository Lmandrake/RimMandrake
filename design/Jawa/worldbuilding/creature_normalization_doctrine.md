# Creature & race physical normalization — doctrine

_Owner rulings 2026-09-05, recorded verbatim. This is the rulebook the
renormalization pass and every review sheet answer to. Supersedes the
"preserve vanilla's curve" option considered in `creature_size_model.md`
(that doc remains correct about what the ENGINE does; this one says what WE
choose to do with it)._

## The four rulings

1. **Target is LITERAL 1:1.** Not vanilla's clickability curve.
   > "We have unusually powerful game zoom so I'm not afraid of tiny creatures."
2. **Concept is the anchor; nothing else is preserved.**
   > "We need not preserve anything. The animals concept is all we keep.
   > Creatures whose concept clearly need to be huge should be. Ones that
   > conceptually be tiny should be made that way... Clearly a tiny thing that
   > looks like Stegosaurus makes no sense. Nor a 10 cell rat. I am not afraid
   > to regenerate anything... Let's not be afraid and do what's right at least
   > once. Then we will fix problem cases after."
3. **Damage/armour/health DO follow mass — intelligently.**
   > "An acid attack from a huge creature might not scale with body size but
   > area of effect might. But physical bites and scratches and stomps would
   > absolutely. Same with their armor absorption and health. A whale sincerely
   > never notices a human with a dagger. Never."
4. **Races normalize as the XENOTYPE AS PLAYED** — race base + its gene stack,
   the thing the player actually meets. Genes that change size AND stats must be
   resolved as a stack, never double-applied.

## The scale anchor (1 cell = 1 metre)

A RimWorld cell is ~1 m, and vanilla already draws a humanlike at ~1.5 cells —
which is a real human's ~1.5-1.7 m body length seen from above. So the anchor is
honest and we adopt it:

- **`drawSize` (cells) = the creature's real body LENGTH in metres.**
- **`bodySize` = real mass in kg / 70** (human 70 kg -> 1.0).

Both come from the creature's CONCEPT (what the thing actually is), assigned from
real-world or clearly-analogous biology — not from its current def values.

**Self-check:** these two are independent readings of the same animal, so their
consistency is a free error-detector. For a roughly human-proportioned body,
`bodySize ≈ (cells / 1.5)³`. A 0.25 m rat -> 0.0046 -> 0.32 kg: a real rat.
Where the cube check disagrees, the SHAPE explains it and must be stated:
spindly/legs (light for length), flat/serpentine, gas-filled, armoured/dense,
blubbered. **A disagreement with no stated shape reason is an error, not a style.**

## Derived stats (ruling 3)

| stat | scales as | why |
|---|---|---|
| **physical melee** (bite, scratch, stomp, slam) | `∝ mass^(2/3)` | force follows muscle cross-section (length²), i.e. mass^(2/3) — not linear |
| **acid / venom / toxic / ranged** | **damage does NOT scale** | chemistry is chemistry |
| **acid / blast AREA of effect** | `∝ length` (cells) | a bigger animal sprays/covers more ground |
| **armour absorption** | `∝ length ∝ mass^(1/3)` | hide/plate thickness scales with linear size |
| **health (`baseHealthScale`)** | `∝ mass` | this is what makes a whale not notice a dagger |

The whale test is the acceptance test for ruling 3: a trivial weapon against a
huge creature must be *negligible*, and it falls out of armour ∝ length together
with health ∝ mass without any special case.

## ⚠️ Engine consequences to watch (flagged, not blocking)

Extreme `bodySize` has real ripples: `MeatAmount`/`LeatherAmount` carry
`StatPart_BodySize` (`val *= bodySize`), as do `CarryingCapacity`, `Mass`,
`Nutrition` and caravan capacity. Ranged hit-chance against a target is clamped
0.1-2.0, so it saturates rather than exploding. A literal 100-tonne whale is
`bodySize` ~1400 and would yield absurd meat; such cases get a stated yield cap
rather than a silent fudge of the size. Record the cap; never hide it.

## Scope

Vanilla is NOT protected — ruling 2 says concept wins. But vanilla creatures are
also the least likely to be conceptually wrong, so expect most edits in the
modded population. Humanlikes use ruling 4, not the animal law.

## What "problem cases after" means

The pass proposes; the owner reviews. Every changed creature carries: old vs new
`drawSize`/`bodySize`, the concept and real-world length/mass it came from, the
shape reason for any cube-check disagreement, and the derived stat deltas.
Nothing is applied silently.
