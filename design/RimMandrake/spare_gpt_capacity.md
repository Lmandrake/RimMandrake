# Spare GPT capacity before its refresh

A standing brainstorm: what to point GPT (Codex) at when its weekly allowance will reset unspent and Claude's is
tight. General ideas first; each gets refined into a concrete runner or item later.

Started 2026-11-09 8:40 PM PST. Measured then (from Codex's own session logs, `ops_watch.c_codex`): 50% of the
weekly Codex quota used, reset in 26.1 h (Tue 2026-11-10 ~10:40 PM PST). Claude: nearly out. Owner, verbatim:
*"Please switch to as much of the work as possible done by GPT. We are nearly out."* and *"what can we use all that
CODEX capacity for? Any build items we could have it knock out? Art reviews?"*

## The constraint that shapes everything

Every GPT job today still has a Claude agent around it: a thin Sonnet helper that applies GPT's SEARCH/REPLACE,
builds, runs the selftests and lands the work (tonight's GSS cleanup: 9 GPT rounds, 10 items closed, about 70k Claude
tokens). So "spare GPT" is only spare while the Claude wrapper stays thin. The biggest win is whatever lets Codex
run **without** a Claude wrapper.

## Ideas (Conductor's seed list)

1. **A Codex-only runner.** `codex exec` in a pooled scratch clone, given one item and its acceptance check. A plain
   script (not an agent) runs the build and selftests and lands only on green. Claude is not involved at all. This is
   the enabler for most of what follows.
2. **Burn down the offline backlog.** About 1,100 open items need only offline work. Start with the well-specified
   ones: those with a named selftest, validator or compiler outcome.
3. **Clear the code-review debt.** Every file is DIRTY until a full-file review says CLEAN. Run Codex reviews across
   the DIRTY set, starting with the most-used mods, and mark files clean on Codex receipts. Findings become items.
4. **Settle reconcile items.** The top of the Conductor's queue is RECONCILE items: commits already exist, and someone
   has to rule whether they complete the item. GPT can judge commit against item text and return the verdict line.
5. **Art pre-review.** GPT reviews art sheets well (owner, 2026-10-23). Use it for art-eval second looks,
   `prereview.json` for pending sheets, and facing/scale checks, so nothing reaches the owner unread.
6. **Draft the designer first-touch passes.** About 60 items need the owner to sign off a mod's expanded spec. GPT
   can draft the spec expansions and validation strategies, so his sittings are spent judging, not waiting.
7. **Audit the checkers.** Mutate selftests to prove they can fail (mutate-your-checker). Tonight two GSS fixes landed
   without that proof.
8. **The log junk.** Work the fixes in `D:\ClaudeWork\rimmandrake\logspam\REPORT.md`
   (`RIMMASTER_TRACE_FULL_LIST_LOG_CRUD_SIX_OFFENDERS`): silencing patches, the Beer guard, the unattributed
   "non-compressible thing" line.
9. **Doc truth sweep.** Find statements in design docs and skills that the code now contradicts, and propose
   deletions (wrong material is deleted, never superseded).
10. **Prep for Wednesday.** Pre-chew the four items set for Wednesday (phone alerts, Artisan part B, Pyrelands
    footprints, the Pocock skills trial), so each arrives as a one-page brief with the decision isolated.

## Guard rails

- No owner-only decisions (delegation_policy section 2) and no live game: Codex cannot drive the bridge.
- A close needs a test that was shown failing without the fix. A "GPT reread it and found no defect" close is weak,
  and is marked so on the item (five such closes on 2026-11-09).
- If Codex reports exhausted, stop; never move the work to Claude.

## GPT's own answer

(Appended below from `gpt_consult.py`; see that section's header for the round and the date.)
