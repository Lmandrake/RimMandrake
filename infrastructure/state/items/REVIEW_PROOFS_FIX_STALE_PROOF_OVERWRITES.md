## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FF_validation_suite_1.2). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FF_validation_suite_1.2)
Verdict: CONFIRMED MAJOR. human_review.py:1110-1131 later Proof_*.json overwrites newest validation rows; freshness only from validation hash

### GPT finding (verbatim)
### FF_validation_suite_1.2 — An old proof PASS can overwrite a current FAIL and inherit its freshness
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/human_review.py:1110–1131` (`latest_result`)
- evidence:
  ```python
      files += sorted(glob.glob(os.path.join(NSDIR, "proof_*.json"))) if not path else []
              hashes.append(d.get("mod_hash"))
                  rows[r["id"]] = (str(r.get("status", "")), str(r.get("detail", "")))
  ```
- failure scenario: The newest validation result has the current hash and reports a mechanism FAIL. An older `proof_*.json` reports PASS for that ID. Proof files are processed afterward and overwrite the FAIL; only the validation file contributes freshness. The sheet can therefore display “Works in game” with a current-hash label using an obsolete PASS. Proof files also receive no live/mock or assembly-identity filtering.
- confidence: high
