## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FB_hose_gss_2.2). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. The repair is built. A1 and A2 still require L2 live acceptance on the current artifact. The executable M15f colonist-job/style proof is supplied by GSS_RESTRING_PROVE_ONE_STYLE_AFTER_JOIN.

### verification (FB_hose_gss_2.2)
Current source has `Patch_Restring_Bridge` in `Source/Aerial/ConduitStylePicker.cs`. Its successful power-span postfix queues `QueueLink(a.parent, b.parent)`, giving re-stringing the same conduit-run reconciliation path as TryLink. The finding below records the original defect. Live completion of the colonist job and one joined style remain owed.

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

## verify
- Written by the Producer, Producer weekly plan 2026-10-29 (run folder D:\ClaudeWork\rimmandrake\producer\2026-10-29T0045Z_weekly), goal 3. Unverified part: RM_RestringSpan.
- L2: cut the only span joining two runs, restyle the sides differently, re-string: the joined run carries one style.
- L2: a MOD-class proof row for RM_RestringSpan PASS on the current build.
- Stopping point: finish.

## criteria
<!-- Written by the Producer, event re-plan 2026-10-29 (run folder D:\ClaudeWork\rimmandrake\producer\2026-10-29T0701Z_event), from this item's `## verify`; level-tagged for `rimflow implemented`. -->
- A1 L2: cut the only span joining two runs, restyle the sides differently, re-string: the joined run carries one style
- A2 L2: a MOD-class proof row for RM_RestringSpan PASS on the current build
- A3 L0: `mod_completion.py GimmeSomeSlack` no longer lists RM_RestringSpan as unverified
