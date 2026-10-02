# HUTT_LOTTERY_CHUTE_BUILD_1 — the Hutt chance chute

## spec
Authority: `design/RimMandrake/ship_cargo_hoist_design_2026-10-01.md` §4 and §5 row 4 (RULED). A fixed chute at the Hutt test site. Stake goods, **slaves or beasts**
and pay the house. After an hours-long timer, a crate comes up built with
`ThingSetMakerParams.totalMarketValueRange` around a rolled multiplier (mostly 0.7–1.1×, rare 3×, rare 0.3×).
**The house always takes a cut.** Odds and the cut are Mod Settings sliders. Staked pawns go in the manifest.

## criteria
- Many rolls average below the stake's value. A staked slave or beast is recorded, never silently vanished.

## Watch out
- Depends on HUTT_SLAVE_PIT_TEST_SITE_1 (and through it on GRAVSHIP_PEACEFUL_SETTLEMENT_LANDING_1).
- 🔑 **Animation is optional polish, and it comes LAST.** Ship with a drawn cable line (`GenDraw.DrawLineBetween`) and static sprites; transit is a hidden timer (vanish, wait, appear). Art is the final step and may be skipped. A descent animation is never in scope (owner: *"careful we don't get caught in endless animation development"*).
