# PIPE_ADAPTER_FIX_DEBT_NEVER_PAID

FlowWorks: adapter Send leaves negative carry unpaid (liquid created on partial accepts)

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C1-F8** CONFIRMED MEDIUM — Adapter Send mode: partial foreign accept leaves negative carry never charged (liquid created). SettleSend (RM_LiquidTransfer.cs:195-201) refunds the whole unit and records -fraction in carry; the Send path (CompLiquidPipeAdapter.cs:151-170) never consults negative carry, only Take does (Mathf.Max(0,carry)).

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
