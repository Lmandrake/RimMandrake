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
| **armour absorption** | **integument TYPE dominates; size modulates weakly** — see below | corrected by the owner, 2026-09-05 |
| **health (`baseHealthScale`)** | `∝ mass` | this is what makes a whale not notice a dagger |

### 🔴 Armour is a material property, not a size property (owner correction)

> "I should have been less cavalier about armor absorption. Whale skin is way
> thicker with blubber than a cow but it's not that much thicker so that's an
> actual parameter that varies by beast depending on what they are. A rhino as
> large as a whale would scale just like that and be impervious."

So armour does NOT simply follow length. Each creature gets an **integument
class** carrying the dominant term, and size modulates it only weakly:

| integument | character | armour base |
|---|---|---|
| naked skin | human, worm | lowest |
| fur / hair | most mammals | low |
| thick hide | cow, muffalo | moderate |
| blubber | whale, seal | moderate-high but SOFT — thick, not impervious |
| scales | reptile, fish | moderate-high |
| chitin | insectoid | high vs cutting, brittle vs blunt |
| keratin plate / horn | rhino, thrumbo | very high |
| bone / bio-plate / metal | mech, armoured beast | highest |

⇒ **A rhino scaled to whale size IS effectively impervious** (keratin plate ×
huge). **A whale at whale size is merely very tough** (blubber is thick but
soft). Both fall out correctly once the TYPE carries the weight and size is a
weak modifier — the whale-never-notices-a-dagger result then comes mostly from
HEALTH (∝ mass), not from armour pretending to be armour plate.

The whale test is the acceptance test for ruling 3: a trivial weapon against a
huge creature must be *negligible*. 🔴 CORRECTED: it does NOT fall out of armour —
armour has no size term at all (below). It comes from **health ∝ mass**, plus the
integument class where the creature genuinely is armoured.

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


## Everything else that reacts to mass (owner, 2026-09-05)

> "We will want to renormalize a lot after this. Armor and pit trap activation
> mass and anything else that reacts to damage and mass. Also how much milk,
> meat, leather, etc comes from these creatures."

Renormalizing `bodySize` moves every consumer of Mass. Before applying anything,
AUDIT and then set deliberately — none of these may be left to fall out silently:

- **Yields:** MeatAmount, LeatherAmount (both carry `StatPart_BodySize`), plus
  milk, eggs, wool and their intervals. 🔴 A literal whale is `bodySize` ~1400,
  so auto-scaled meat is absurd — yields get **explicit per-creature values with
  a stated playability cap**, never a silent fudge of the size.
- **Traps & mechanisms:** pit-trap activation mass and anything else gated on
  Mass crossing a threshold.
- **Carrying & caravan:** CarryingCapacity, caravan mass capacity (`MassUtility`),
  pack-animal usefulness.
- **Husbandry:** pen space/load, bed fit, trainability gates, predation
  thresholds (who can hunt whom).
- **Combat:** ranged hit-chance vs the target (clamped 0.1-2.0, so it saturates),
  bullet-stagger immunity.
- **Needs:** Nutrition, MaxNutrition, food-tank size.

**Rule:** every one of these is either derived by a stated formula or set
explicitly per creature — and whichever it is gets recorded in the proposal, so
the owner reviews numbers, not surprises.


---

## 🔴 AUDIT CORRECTIONS (mass_consumer_audit.md, 2026-09-05) — read before executing

The audit read the engine and found **~45 consumers and 22 hard thresholds**. Three
things this doctrine asserted are FALSE, and one danger is disqualifying.

**Struck as non-existent / wrong:**
- ⛔ **"Pit-trap activation mass" DOES NOT EXIST.** `Building_Trap.SpringChance`
  (`Building_Trap.cs:116-141`) = knower factor × `TrapSpringChance` ×
  `PawnTrapSpringChance`, with *zero* StatParts. No mass or bodySize term in any
  trap class. Making traps mass-sensitive is a **feature request**, not a
  renormalization — it must be built, not tuned.
- ⛔ **Pen escape is not size-driven** — `RaceProperties.FenceBlocked => Roamer`,
  a bool. Only pen *density* is size-driven.
- ⛔ **Bleed rate is not size-driven** — that line scales blood *filth drop
  chance* (`Pawn_HealthTracker.cs:1221`), not bleeding.

**Armour — the doctrine's integument model is SAFE and fills a vacuum:** there is
zero size derivation anywhere; `ArmorRating_*` carries only `StatPart_Stuff`, and
animals get plain hand-authored `statBases` defaulting to 0 (vanilla Elephant 0,
Tortoise 0.50 — no size correlation at all). ⚠️ `maxValue` is hard-clamped at **2.0**.

**Yields:** meat + leather auto-scale (`140 × bodySize`, then a `postProcessCurve`
with kinks at bodySize **0.036** and **0.286** — piecewise, so naive ratio-rescaling
is wrong below 0.286). **Milk, wool and eggs are FLAT per-def integers** and do not
scale at all — every one must be set explicitly.

### 🔴 The disqualifying finding: literal real-mass bodySize breaks the engine

`bodySize` is not a free parameter — 22 hard thresholds are calibrated to vanilla's
~0.02-4.0 range. At literal real mass (rat 0.0046, whale ~1400):

| threshold | what breaks |
|---|---|
| **herd migration `ceil(4 / bodySize)`, UNCLAMPED** | a real-mass rat spawns **~870 animals** — **map hang**. Showstopper. |
| `maxPreyBodySize` (vanilla 0.25-3.0) | predators become eligible for nearly everything **including colonists** |
| bullet stagger `BodySize <= stoppingPower` (weapons 0.5-3.0) | everything under ~70 kg is **stun-locked by any rifle** — and it is INVISIBLE: no UI, no stat, no log. Surfaces as "combat feels weird" many sessions later. **Biggest silent risk.** |
| haul training **0.40** / rescue **0.65** | most trained haulers stop qualifying |
| ranged hit clamp **0.1-2.0** | nearly every animal pins to a rail; the mechanic loses all resolution |
| ideoligion animal-per-capita **1/2/4/6/8**; large-corpse 0.75; cell-share 1.5; bed 0.25/0.55; snow 0.9 | fail open or stop matching |

⇒ **`drawSize` can be literal — it is only art.** `bodySize` cannot be literal
real-mass without either a mass-compression mapping or editing all 22 thresholds.
This needs an owner ruling; it is recorded here as OPEN, not silently resolved.

---

## OWNER RULING on bodySize (2026-09-05): **literal + targeted mitigations**

Go literal real-mass, and patch the specific consumers that would break. The
mitigation list, in priority order:

| # | threshold | mitigation |
|---|---|---|
| 1 | **herd migration `ceil(4 / bodySize)`, unclamped** | 🔴 MUST clamp (patch). Untouched, a real-mass rat spawns ~870 animals and hangs the map. Nothing ships before this. |
| 2 | **bullet stagger `BodySize <= stoppingPower`** | set `RaceProperties.bulletStaggerIgnoreBodySize` per race — the engine ALREADY offers this opt-out. Highest silent risk if skipped. |
| 3 | `maxPreyBodySize` (vanilla 0.25-3.0) | retune per predator so colonists (1.0) are not casually eligible prey |
| 4 | haul **0.40** / rescue **0.65** training gates | retune so intended work animals still qualify |
| 5 | meat/leather `postProcessCurve` (kinks at 0.036 / 0.286) | set yields EXPLICITLY per creature with a stated cap; never ratio-rescale across a kink |
| 6 | milk / wool / eggs | flat per-def integers — set explicitly, nothing falls out |
| 7 | ranged hit clamp 0.1-2.0 | ACCEPT saturation (no fix without an engine patch); record that the mechanic loses resolution at the extremes |
| 8 | ideoligion per-capita, bed 0.25/0.55, large-corpse 0.75, cell-share 1.5, snow 0.9 | audit after the pass; accept or patch case by case |

## ⭐ The Pits mod is not a problem — renormalization FIXES it

The owner's "pit trap activation mass" meant **our own `src/RimMandrake/Pits`**, not
vanilla traps. It already sums real `StatDefOf.Mass` in KILOGRAMS against cover
tiers: **WovenScrap 40 kg · PlankLattice 120 kg · ReinforcedFrame 220 kg**.

Those thresholds are honest; **the creature masses are what's wrong**. `PitCoverTier.cs`
already records the tell: the quicktest matrix found **240 kg was the ceiling of any
single vanilla creature** — an elephant/megasloth/thrumbo maxing at 240 kg is absurd
(a real elephant is 4,000-6,000 kg), and the owner filed **`BEAST_MASS_REALISM_AUDIT_1`**
on 2026-08-30 precisely because "the 240kg ceiling itself looked suspiciously low."

⇒ **This renormalization is the fix for the item he filed in August.** After it, the
pit tiers finally mean what they say — a real elephant smashes any cover, a rat never
springs one — with **no change to the Pits mod at all**. Re-verify the tiers against
the new mass distribution once the pass lands, and close that item.

---

## 🔴 WORKLIST CORRECTED (visual portfolio, 2026-09-05) — the earlier list was measured wrong

The "TOP MISMATCHES" list carried up from the size model was computed over the
**full register, cut and live mixed**. That is the wrong population:

- **65 of the 232 out-of-band creatures are ALREADY CUT** by Cherry Picker.
- Only **28 of Jurassic's 131 dinos are live** — the "whole dino block runs
  2.5-2.9x" finding was mostly measuring creatures nobody will ever see.

⇒ Any ranking that includes cut creatures is a different and **wrong** worklist.
Fix only the **live** population. Corrected figures (n=892 live):

**81% (725/892) already obey the engine's own law** — the defect is a MINORITY,
and it runs in BOTH directions (too big AND too small). 167 are out of band.

**Systematic (one per-mod multiplier fixes most) — do these first, cheap:**
| mod | median | out | block-fixable |
|---|---|---|---|
| Vanilla Vehicles Expanded | 1.71x | 17 | **88%** |
| Biotech | 0.75x | 6 | **100%** |
| Caravan Adventures | 2.10x | 5 | 80% |
| Alpha Animals | 1.16x | 25 | 68% |
| Biomes! Polluted Lands | 0.94x | 5 | 60% |

**Scattered (per-creature work) — the real cost:**
🔴 **Biomes! Caverns is the heaviest target and was NOT in the old list**: 27 out
of band, only **7% block-fixable**, because its defect is **bimodal, not shifted** —
seven pupae pinned at `bodySize 1.0 -> drawSize 1.0` (0.50x) against `chem snail`
at 2.83x. ⭐ Those 7 pupae share ONE life-stage drawSize, so they are a **sub-block**
and cheap to fix as a group even though the mod as a whole is not.
Then: Vanilla Genetics Expanded 38% · Jurassic 27% · Alpha Mechs 22% · SW Animal
Collection 14%.

**Overall:** of 160 out-of-band creatures in characterisable blocks, one per-mod
multiplier clears **67 (42%)**; **93 need hand edits**.

⚠️ A per-mod multiplier applied to `bodySize` moves mass, yields, haul capacity and
shootability; applied to `drawSize` it moves only the sprite. The 42% holds either
way, but WHICH field the multiplier lands on is a separate ruling.

Figures + method: `design/Jawa/worldbuilding/review/viz/` (portfolio scored 90/100,
all three members carry a `visual-critic` SHIP verdict).
