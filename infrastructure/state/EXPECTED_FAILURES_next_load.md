# Expected-failure signatures — Armoury deploy batch #2, written 2026-09-04 BEFORE launch (FOUNDRY)

Supersedes the prior (2026-09-04, FOUNDRY) entry — that batch (4 assemblies)
already deployed, restarted, and verified clean earlier this session.

This batch: 6 fixes, all in ONE assembly (`JawaArmoury.dll`, mod
`mandrake.rsw.armoury`) — lower attribution risk than the last batch since
there's only one DLL to blame, but each fix still gets its own named
signature so a real regression can be told apart from the others.

| fix | file | expected signature |
|---|---|---|
| Fixed a Harmony transpiler injection point (already deployed+verified last restart) | Patch_JobGiver_AIFightEnemy.cs | N/A — not part of this batch, already live |
| Double-integrated mote movement + orphaned mote leak fixed | Spinning_Projectile/MoteWeaponReturn.cs | ABSENT: no behavior to watch for without spawning a returning weapon and observing mote speed in-game (not log-visible) — build success is the only automatic signal here |
| Dangling `Mote_LightSaberReturn` ThingDef reference documented (comment only, not fixed — unreachable code path, no live `SpinningWeaponProjectile` user) | Spinning_Projectile/SpinningWeaponProjectile.cs | ABSENT: no behavior change, comment-only |
| Missing null-guard on `VSH_inDangerField` reflection get | InstantHealingDrug/TCED_TryGiveJob_Patch.cs | ABSENT: no `NullReferenceException` naming `TCED_TryGiveJob_Patch` or `VSH_inDangerField` — this guard only fires on an already-rare version-mismatch path, so silence is expected either way; the fix just prevents a crash IF that path is hit, not a currently-observed crash |
| `CompProperties_KoltoTank.multiplier` (2.5) was declared but never read — healing ran at the hardcoded 2500-tick (1hr) cadence instead of the intended 6250-tick (2.5hr) cadence per the def's own description | KoltoTank/Building_KoltoTank.cs, KoltoTank/CompKoltoTank.cs | ABSENT: no exception. RESIDUAL: this is a gameplay-balance change (healing gets ~2.5x SLOWER, correctly matching the def's text) — not verifiable from the log, needs an in-game observation eventually, not blocking this restart |
| `FloatMenuOptionProvider_CarryToKoltoTank.Drafted` was `false`, blocking the option during combat — the exact situation the tank exists for | KoltoTank/FloatMenuOptionProvider_CarryToKoltoTank.cs | ABSENT: no exception. Not log-verifiable either — needs an in-game right-click check eventually (drafted pawn standing over a downed ally near a Kolto Tank should now offer "Carry ... to Kolto Tank") |

General: watch for any `InvalidProgramException`, `TypeLoadException`, or
Harmony patch-failure line naming `JawaArmoury` — that would mean a build
succeeded locally but something about the deployed DLL doesn't match
(should not happen, deterministic build, but check anyway). Run the usual
`harvest_log.py` full sweep afterward, same as any restart.
