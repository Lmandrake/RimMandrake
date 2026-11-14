# RIMMANDRAKE_SHORT_DROWNED_ELECTRONICS_LIKE_RAIN_DOES

## spec

Owner, live look 2026-11-14 about 11:30 AM to 12:10 PM PST (finding 8, `D:\ClaudeWork\rimmandrake\conductor\sitting_20261114\OWNER_LOOK_WORDS.md`):

> "Next version comment: adding conductive liquid over electronics is the same as putting them out in the rain in terms of causing them to short and explode (borrow same game code)."

The game code to borrow is `RimWorld.ShortCircuitUtility.TryShortCircuitInRain(Thing)` (decompile ShortCircuitUtility.cs:90). `SteadyEnvironmentEffects` calls it for things under rain.
- It fires when a `CompPowerTrader` is PowerOn with `Props.shortCircuitInRain`, or when a `CompPowerBattery` holds more than 100 Wd.
- It then sends the "ShortCircuitRain" letter and runs `GenExplosion.DoExplosion` with radius 1.9 and Flame damage.

The work:
- Call it, at the rain cadence, for each such building whose live part is under a conductive liquid (water and brine yes; oil and tar no; the list is a design choice).
- Prior notes on rain shorts: `design/RimMandrake/fulgurite_lightning_design_pass_2026-10-15.md` lines 39-46.

Design Version class: Divergent (next version), in his own words.

Build effort: medium.

Acceptance test (offline, a local model could run it): a FlowWorks selftest of the selection rule asserts:
- a powered `shortCircuitInRain` building, and a battery over 100 Wd, under 1 m of water are chosen to short;
- the same building under tar, or dry, is not chosen;
- the call target is `ShortCircuitUtility.TryShortCircuitInRain`.
