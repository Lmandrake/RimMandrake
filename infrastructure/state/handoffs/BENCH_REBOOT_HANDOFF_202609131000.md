
## BENCH handoff — 2026-09-13 ~10:00Z

### Finished this sitting (all committed and pushed)
1. **CATHEDRAL_ARC_OPEN_CARDS_1 ruled and closed** (`3f6f98cd2`): warzone flip
   = GM surfaces + faction-hostility flips + storyteller swap + all-out-hostile
   mechanoids; pass scope = narrowest. Propagated into both build items.
2. **Hub rebuilt at a NEW artifact URL** — the old one was deleted, link dead:
   https://claude.ai/code/artifact/ec893765-f01c-4cd8-a0b2-58e5b0bf2257 (pinned
   on the owner's yes). Pointers updated; FOUNDRY's copy already fixed
   (HUB_URL_POINTER_FIX_1, closed by FOUNDRY at 9f4c06b9).
3. **`infrastructure/dashboards/hub/regen_hub.py`** (owner request): one-command,
   no-LLM hub regeneration + publish validation, 0.5s; `--check`, `--full`;
   emits `data/publish_ready.json` for a single-call publish. Reviewed full-file,
   marked CLEAN (`79d452398`). 51/51 selftests.
4. **Doing-items audit** (owner request; DOING_ITEMS_RECONCILE_1 closed at
   `d07d585cd`): 61 real doing items, not 102; verdicts in
   `Transient/doing_audit_2026-09-13.md`. BENCH-side fixed in place;
   **21 zombie FOUNDRY starts filed as DOING_SEDIMENT_RECLAIM_1** for FOUNDRY;
   TECHPRINT_FACTION_GATING_1 reassigned FOUNDRY-ready.
5. ARTPIPE_FAILED_REQUEUE_1 filed for FOUNDRY (46 failed jobs triaged: 27
   gemini-banned, 16 codex transients, 3 canvas-size bug); evidence
   `Transient/artpipe_failed_triage_2026-09-13.tsv`.
6. ~9 days of untracked Transient evidence committed (`9d100d37c`); derived art
   piles (sea_raw 150MB, triposr 78MB, art_gen 59MB) and 24MB BMPs deliberately
   left untracked.

### Half-done / holds
- Nothing mid-edit. All subagents reported and were acted on.
- BENCH queue: CANON_DRAIN_1 gated (fauna 336/828 + flora 130/288 undecided —
  gate closed); MODLIST_DEFERRED_CARDS_1 waits for an owner-called sitting.

### Owner should look at first
- Four sittings wait on him (now correctly `needs owner`):
  WORLDMAP_FINAL_REVIEW_1, DUNGEON_SETPIECE_TEXT_1, CAMPAIGN_STORY_SITTING_1,
  ASSIGNMENT_SHEETS_VERDICT_SITTING_1.
- The rebuilt hub URL above (old pinned link is dead everywhere).

### Traps for whoever resumes
- Ledger projections: use FILE ORDER, never ts-sort (same-second start+close
  inverts — this is how 102 "stuck" items were really 61). In LESSONS_INBOX.
- `--owner-said` refuses questions — an owner question authorizes an
  examination, not a state change. Route cross-seat changes to the owning seat.
- FOUNDRY window is live (Cathedral/GM lane) and the artpipe daemon is
  rendering; don't double-drive either.
