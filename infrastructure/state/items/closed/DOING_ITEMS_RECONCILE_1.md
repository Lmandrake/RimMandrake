
## spec
Owner (2026-09-13, before going AFK): "What about examining the stuck queue
items marked doing?" Ledger projection at 09:20Z found **102 items in
`doing`**: 20 on the retired DECIDE/CHECK/BUILD seats (415–550h, orphaned by
redesign #4 — nothing will ever close them), 5 DIRTY_CODE_REVIEW_LOOP_RESTART
markers, ~50 FOUNDRY starts aged 24–330h, 12 BENCH + 3 OWNER-seat holds.
Three read-only classification passes (legacy / stale-FOUNDRY / BENCH+OWNER)
are fanned out; reconcile on their returns: close what's provably done (real
sha), drop what's dead (reason recorded), leave needs-owner sittings and the
live FOUNDRY window's <24h starts alone, and list the residue — items
started and then abandoned with work genuinely remaining — for re-queueing.
Seat guard note: BENCH cannot close/drop FOUNDRY-owned items; those
reconciliations get filed for FOUNDRY with the classified list as spec.

## verify
Re-run the doing projection: every remaining `doing` item is either <24h old,
a needs-owner sitting, or on the residue list with a stated reason.

## criteria
`doing` means someone is doing it. The state is a signal again, not sediment.
