# RIMMANDRAKE_RENEW_SAFE_ADVANCE_AUTO_ARM_HOURLY

## spec
`jawa/safe_advance` (JawaBenchVitalsTools.cs:229) auto-arms the vitals monitor with a 60 min TTL when it is not armed,
and never renews it or disarms it. A later advance sees `Armed` true and does not re-arm. So 60 wall minutes after the
first auto-arm, `FrameArmed` disarms on "ttl" in the middle of whatever advance runs then, and that advance ends
"aborted: monitor disarmed mid-advance (coverage lost)".
Failure seen: Pyrelands visit 2, 2026-11-21 00:08 PST. In `embergrass_regrow`, `regrow_dry_watered_vanilla` stopped
after 660 of 2000 ticks, 24.6 min into the chain, with no other driver on game a. Its row parts went UNMEASURED, and
25 minutes of chain time were lost. Any chain series longer than an hour on one game session meets this.
A second case in the same visit: `burn_line_burned_share` went UNMEASURED when the monitor was disarmed (SUMMARY.md, visit 2, "the governor's monitor disarmed").
Cause [guess ~75%]: the auto-arm TTL ran out. The arm time of that session's monitor was not read.
Fix: when safe_advance auto-armed the monitor (autoArmed), renew `_until` at each advance start, or disarm it at the
advance end; an explicit arm by a governor row keeps its own TTL.
## verify
Live, game a or b, no explicit `jawa/vitals arm`: safe_advance 100 ticks; read `jawa/vitals` ttlLeftS; let the wall clock
pass the TTL (or arm with ttlMin 1 through the same auto path in a test build); safe_advance 2000 ticks completes with
state done, not "monitor disarmed".
## criteria
Acceptance test: none offline; the TTL lives in the bridge DLL's main-thread frame. Live command above, red on the
current DLL (the abort reproduces after the TTL), green on the fix.

## refs
file: src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchVitalsTools.cs
file: src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchVitals.cs

Measured 2026-11-21 02:02 PST on game a (full list, mid walk_season): jawa/vitals status read armed true, row null, by "jawa/safe_advance", why "auto-armed by safe_advance", ttlLeftS 2903. The visit renewed it by hand (jawa/vitals arm ttlMin 240) to keep the walk from aborting; that is not the fix.
