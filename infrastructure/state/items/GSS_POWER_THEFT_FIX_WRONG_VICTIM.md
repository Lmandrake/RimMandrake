## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FB_hose_gss_2.5). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FB_hose_gss_2.5)
Verdict: CONFIRMED MINOR. CompPowerTap accumulates sinceEventWd across victims and raises it against the current vt (CompPowerTap.cs:148-158) -> goodwill charged to the wrong faction

### GPT finding (verbatim)
### FB_hose_gss_2.5 — Theft windows are attributed entirely to the current victim
- severity: MINOR
- where: `src/RimMandrake/GimmeSomeSlack/Source/Aerial/CompPowerTap.cs:148–158` (`CompTick`); `src/RimMandrake/GimmeSomeSlack/Source/Aerial/PowerTheftConsequences.cs:47,67` (`OnDrained`)
- evidence:
  ```csharp
  sinceEventWd += stolenWd;
  ```
  ```csharp
  if (AerialSettings.tapEvents) TapEvents.Raise(parent, vt, sinceEventWd);
  ```
- failure scenario: A clamp can bite either of two adjacent foreign transmitters. It drains faction A for most of an event window; A’s transmitter is then removed, making it select faction B before the 250-tick event. The event sends all accumulated energy and draining ticks with B’s current transmitter. B receives A’s draining time if already caught, or a discovery event based partly on theft from A. The per-faction saved accumulators cannot correct this because the window never records which faction supplied each tick.
- confidence: high
