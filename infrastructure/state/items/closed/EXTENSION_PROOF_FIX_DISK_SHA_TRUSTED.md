## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FF_validation_suite_1.3). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FF_validation_suite_1.3)
Verdict: CONFIRMED MAJOR. extension_proof.py:183-190 trusts on-disk sha; driver_stamp.py:31,36 says only mvidMatchesFile proves the loaded DLL

### GPT finding (verbatim)
### FF_validation_suite_1.3 — Extension evidence can identify the replacement DLL instead of the loaded DLL
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/northstar/extension_proof.py:183–190` (`main`, environment capture)
- evidence:
  ```python
              ms = (rm.get("assembly") or {}).get("matches") or []
              env["assembly_matches"] = len(ms)
              env["assembly_sha256"] = ms[0].get("sha256") if len(ms) == 1 else None
  ```
- failure scenario: Start the game with DLL A, then deploy DLL B without restarting. This runner records B’s on-disk hash while exercising A. Its result can consequently claim the newer assembly, and dry/river halves can merge under that false identity. The in-part `driver_stamp.py` explicitly documents this trap and requires `type_probe.mvidMatchesFile`; this runner bypasses that safeguard.
- confidence: high
