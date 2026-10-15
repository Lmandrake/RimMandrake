# HOSE_IMPORT_MEND_ONE_SHOT_MISS

FlowWorks: GSS hose-settings import marked done before reading

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C8a-F1** CONFIRMED LOW — GSS hose-settings import marks itself done before reading; an I/O failure never retries. Hose/RM_HoseLegacy.cs:109-110 sets hoseSettingsImported=true first. Affects players upgrading from a GSS build that had hoses.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
