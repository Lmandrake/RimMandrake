# CAULDRON_TRUNK_DEPOSITS_BUILD_SWEAT_SHOWS

## What
Build the trunk-deposit coat (grey metallic scabs + bruised-blue crystal fans) on RM_TwistingThornwood exactly as
`design/Jawa/worldbuilding/biomes/cauldron_trunk_deposits_design_2026-11-02.md` §2-§4 specify: RM_TrunkDepositsExtension, DepositTier kernel fn beside RM_YieldKernel.FleckBand (+ Python
mirror swept over the grid), one Plant.Print postfix drawing coat then flecks, a CompTickLong re-print on crossing
the old-age threshold, setting trunkDepositsEnabled (default on). Art: Deposits_Scab/Deposits_Slag 256x256 made by
editing TwistingThornwood_a.png and subtracting it, judged by the art-eval pipeline, installed via the art ledger.

## Acceptance
- `python3 src/RimMandrake/Cauldron/selftest_cauldron_trunk_deposits.py` green with both deposit PNGs on disk
  (registration >= 95 %, coverage bands).
- L2 quicktest: a mature and an old thornwood show their coats; off after toggling trunkDepositsEnabled.
- First read: the design's UNMEASURED line (how wild mapgen seeds Age on full-grown trees).
