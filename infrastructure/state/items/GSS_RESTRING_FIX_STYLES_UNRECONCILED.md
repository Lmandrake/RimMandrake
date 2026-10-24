## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FB_hose_gss_2.2). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FB_hose_gss_2.2)
Verdict: CONFIRMED MINOR. Run-merge rule hangs only on TryLink postfix (ConduitStylePicker.cs:470-481); Restring (CompAerialAnchor.cs:362-374, called by RestringJob.cs:73) reconnects without it

### GPT finding (verbatim)
### FB_hose_gss_2.2 — Re-stringing reconnects electrical runs without reconciling their styles
- severity: MAJOR
- where: `src/RimMandrake/GimmeSomeSlack/Source/Aerial/CompAerialAnchor.cs:362–373` (`Restring`); `src/RimMandrake/GimmeSomeSlack/Source/Aerial/ConduitStylePicker.cs:471–480` (`Patch_TryLink_Bridge`)
- evidence:
  ```csharp
  [HarmonyPatch(typeof(CompAerialAnchor), nameof(CompAerialAnchor.TryLink))]
  ```
  ```csharp
  a.parent.Map.GetComponent<RM_MapComponent_ConduitRuns>()?.QueueLink(a.parent, target);
  ```
- failure scenario: Cut the only span joining two runs, restyle the disconnected sides differently, then complete the re-string job. `Restring` restores power and redraws meshes, but only `TryLink` queues the run-merge rule. The repaired electrical run retains both styles indefinitely. Differing endpoint looks also keep triggering the two run flood fills used to choose the span material during drawing. That performance consequence depends on outside-part `AerialMaterials.cs`, which I opened to confirm.
- confidence: high
