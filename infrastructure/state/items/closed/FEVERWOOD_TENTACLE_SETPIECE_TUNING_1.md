# FEVERWOOD_TENTACLE_SETPIECE_TUNING_1 — the eye set-piece's frequency, and the poison/radioactive suppression route

## spec

Caused by `FEVERWOOD_TENTACLE_BESTIARY_1` (six tentacle types + the ordinary
drive-off ladder + the severed-limb harvest — built and closed). Authority:
`design/Jawa/worldbuilding/biomes/fever_wood_deep_and_mud_2026-09-23.md` §2b,
§6d, §6f.

That item built the ORDINARY two-tier ladder for five limbs
(`RM_CompTentacleLimb`: retreat / sever-and-harvest) and the eye's own
three-tier ladder for the sixth (`RM_CompTentacleEye` on `RM_Sekkulaath_Bloom`:
retreat / map-wide day-long drive-off / permanent kill on this map). Both
comps and all six defs are real, compiling, and wired into an ambient roll
(`RM_MapComponent_TentacleWatch`). **Two things that item explicitly declined
to guess remain unbuilt:**

### 1. The eye set-piece's real frequency/pressure model

The design sheet §6d rules FOUR inputs compose into one pressure number (base
roll weighted by pool size, player provocation, accumulating pressure per
pool, a deliberate summon) and calls the resulting frequency **"the single
most important tuning number in this whole design... unset — nobody has
chosen it."** §6i additionally rules the set-piece gets **no protection** (no
maturity gate, no wealth floor, no scaling clamp — all three explicitly
declined) and that legibility (pool size, `RM_Corvath`, the chorus falling
silent, the town's pool-list) must carry all of the fairness instead.

**What FOUNDRY actually shipped as a placeholder, not a tuned answer:**
`RM_MapComponent_TentacleWatch`'s ambient roll treats Bloom as one of six
uniformly-timed limb outcomes (weight 2 of ~105, INVENTED, flagged in that
class's own header) — a single Bloom sighting alone carries the eye's full
ladder. This is NOT the "large pool, many limbs, and the eye itself" grand
set-piece the table describes (§2b row 3) — that reads as a distinct,
bigger, multi-limb event, and no such distinct event exists in the codebase.
Owed:
- A real pressure/frequency model per §6d's four inputs (needs the owner's
  numbers — do not guess a curve).
- A decision on whether the "many limbs + eye" framing needs its own spawn
  event distinct from an ordinary Bloom sighting, or whether Bloom-solo (as
  shipped) is close enough. Ask, do not assume.
- §6i's own accepted risk (an unlucky early colony facing this before it can
  survive it) is real given the shipped placeholder's flat weight — worth
  raising alongside the frequency question.

### 2. Poison/radioactive suppression (§2b's last row, §6f)

**Entirely unbuilt.** The ladder's row "foul the water with specific poisons
or radioactive material → suppressed for several days" has no mechanism at
all in `FEVERWOOD_TENTACLE_BESTIARY_1`'s build — no detection of a
poison/radioactive substance entering a registered pool cell, no suppression
state on `RM_MapComponent_TentacleWatch` (which does have `blockedUntilTick`
already — reusable once the trigger exists).

§6f rules the SHAPE (campaign layer: genuinely dangerous radioactive salvage
only, rare/expensive; free tier: craftable from vanilla Uranium) but not:
- **Which items qualify**, campaign-side. The seep-oils (`RM_Seepril`) were
  offered and explicitly **declined** — do not reach for them.
- **How much, for how long**, and whether suppression harms the pool's other
  content (the treasure trickle, `RM_Corvath`) — §6f's own open question.

## watch out

- ⛔ Do not guess either number. Both are named "unset" by the owner across
  two separate rulings in the same design sitting — ask, do not invent a
  curve or a reagent list to make this item closeable solo.
- The reusable hooks already exist: `RM_MapComponent_TentacleWatch.blockedUntilTick`
  (a suppression trigger just needs to push it out further, same as a sever's
  respite) and `RM_CompTentacleEye`/`RM_CompTentacleLimb`'s thresholds are
  all field-tunable on the def, not hardcoded — a real frequency/reagent
  ruling should mostly be a def/tuning change plus one new detection comp for
  the poison route, not a rearchitecture.
