## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FE_cs_selftests_4.1). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FE_cs_selftests_4.1)
Verdict: CONFIRMED MAJOR. GSS DeterminismChecks.cs:79-90 Compare walks fresh keys only and drops EndA==null pieces; a stale incremental-only cord reads as zero differences

### GPT finding (verbatim)
### FE_cs_selftests_4.1 — Determinism comparison ignores surplus incremental pieces
- severity: MAJOR
- where: `src/RimMandrake/GimmeSomeSlack/Source/SelfTest/DeterminismChecks.cs:79–90` (`Compare`)
- evidence:
  ```csharp
  foreach (LaidPiece p in fresh.Where(p => p.EndA != null))
  {
      if (!cur.TryGetValue(p.Key, out ulong h)) { missing++; keys.Add("missing " + p.EndA + "|" + p.EndB); }
  ```
- failure scenario: An incremental rebuild retains an obsolete cord after a topology change. Every cord in the fresh build still matches, but the incremental result contains an additional stale piece. `Compare` reports zero differences and zero missing pieces because it never checks incremental-only keys. With one matching piece, `Run` declares the scene successful. The comparison also excludes all pieces with `EndA == null`, so pile/node differences alone cannot fail this check. This finding uses only the supplied files.
- confidence: high
