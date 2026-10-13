# C# review — night 2026-10-13 (BENCH helper, offline)

Scope: C# files touched by 4f015f41a2, 28efd07e01, 040556e9c3, 9421288110, dbdfef28f7, dbe92f0c92 that `code_review_status.py check` reported DIRTY. (e167f49523 / f3aaa39a56 touched Python only.)
Checklist: main-thread-only API off-thread · Harmony re-entry / swallowed exceptions · null map/pawn after reload · per-tick cost · settings defaults = shipped · refusal paths that silently succeed.

| file | findings | outcome |
|---|---|---|
| bridgetools/JawaBench.BridgeTools/JawaBenchVitals.cs | **F1** stepper wedge (below). Minor: Specimens hold Thing refs across a game swap (the epoch coverage trigger already stops a governed run). | F1 fixed; stays DIRTY (a fix does not clean) |
| bridgetools/JawaBench.BridgeTools/JawaBenchVitalsTools.cs | **F2** `timeoutMs < 0` returned a null result instead of a refusal | fixed; DIRTY |
| bridgetools/JawaBench.BridgeTools/JawaBenchVitalsCore.cs | none (added the pure `AdvanceFrameStop` gate for F1) | CLEAN |
| bridgetools/JawaBench.BridgeTools/JawaBenchQuietSiteTools.cs | **F3** `action=apply` with neither flag returned success having done nothing | fixed; DIRTY |
| bridgetools/JawaBench.BridgeTools/JawaBenchSafetyCore.cs | none | CLEAN |
| bridgetools/JawaBench.BridgeTools/JawaBenchMapInfoTools.cs | **F6** (systemic) `set_current_map`'s refusal uses a non-capturing lambda (shared `<>c`); map_info `season` reads TicksAbs without the GameReady guard (ErrorOnce during an in-game load) | not fixed (filed F6); DIRTY |
| bridgetools/JawaBench.BridgeTools/JawaBenchResearchTimeTools.cs | **F4** time_set_ticks declared the clock BEFORE the negative-ticks refusal and on no-op calls (a stale pending declaration could later whitewash an undeclared jump to that tick); `success` was hard-coded true, not read back. Also F6 lambdas (`d => d.IsFinished`, `f => f.defName`) | F4 fixed; DIRTY |
| FlowWorks/Source/RM_NorthstarProofs.cs | **F5** ProofTank: `Enum.TryParse` accepted `"7"`/`"Store,Fill"` (undefined mode set under success); the empty-out's TryRemoveLiquid result ignored. ProofPump: any verb but `pour` silently set draw. ProofLip: null excavation engine -> NRE | fixed; DIRTY |
| FlowWorks/Source/SelfTest/TransferChecks.cs | none (test code; allow-list entry for ProofTank is correct) | CLEAN |
| bridgetools/AwarenessSelfTest/UnitsVitals.cs | none; 4 new gate units added | CLEAN |
| AwarenessSelfTest/Program.cs, JawaBenchSituationalTools.cs (1176 l), JawaBenchTpsWriter.cs (529 l) | 2-line touches inside never-clean large files; NOT reviewed in full tonight | DIRTY, unreviewed |

## Findings detail

**F1 — safe_advance wedges after a disarm, TTL or unready game (real).** `JawaBenchSafeAdvance.Frame` was pumped only from inside `JawaBenchVitals.Frame` *after* `if (!Armed) return;` and `if (!GameReady()) return;`. So its own "monitor disarmed mid-advance", wall-timeout and cancel checks were unreachable exactly when they mattered: a `jawa/vitals disarm`, the TTL, a return to menu or a load mid-advance left `SA.Cur.State == "running"` forever, and every later `jawa/safe_advance start` refused ("an advance is already running") while `cancel` could never land. Fix: `Frame()` now pumps the stepper armed or not; the stepper checks cancel / wall / armed FIRST (pure `V.AdvanceFrameStop`, unit-tested: 4 units, red by compile failure before the function existed), then the readiness gate (now including `GameReady()`, which the old call path supplied implicitly). Live proof owed: `SAFE_ADVANCE_PROVE_DISARM_ENDS_THE_RUN`.

**F2** — `timeoutMs < 0` skipped the wait and the read-back lambda returned `null`: a call with no `success` at all. Now refused up front.

**F3** — `jawa/quiet_site action=apply` with `clearThreats=false, proximityLetters=false` reported `success=true`. Now refused.

**F4** — see table. Declaration now happens only for a write that moves the clock; `success = TicksGame == ticks`.

**F5** — see table; each now returns `REFUSED: ...`.

**F6 (systemic, filed `COMPANION_LAMBDA_HARDEN_NO_GSS_NO_SERVICE`)** — JawaBenchVitalsTools.cs records (measured live 2026-10-13) that a NON-capturing lambda anywhere in the `JawaBenchTerrainTools` partial class lands in one shared `<>c` that fails to load without GimmeSomeSlack, killing every tool that uses one. MapInfoTools and ResearchTimeTools both still have them; the class has many more. A per-file fix is whack-a-mole; it needs a decision (move GSS-typed lambdas into their own class, or lint) and a non-GSS live check.

Checked and fine: every game read in the reviewed tools is inside `ctx.MainThread.InvokeAsync`; the vitals Harmony prefix/postfix contain observer faults (counted) and never swallow the game's own exceptions; disarmed hooks return at the first volatile read; per-tick cost is one counter + a T60 census (hediff walk only for colonists/critical); `vitals_settings.json` absent = all channels on (= shipped); campaign profile denies `quiet_site` and `safe_advance`.

Builds: companion `build.py --gm` (plan only, NOT deployed) OK; `winbuild.py FlowWorks` OK. Awareness core selftest 141/141.
