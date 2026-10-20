# RELOAD_POCKETS_DIAGNOSE_KEPT_NO_RECEIPTS

Class: UNTRACED (MOD or transient). live_session B7 (`B7_reload_A2/A3/save_reload_pockets_iden`) FAILed twice on
`pocket_covers` alone (runs `Transient/live_session/20261018T232207` and `20261018T233414`; access/digdepth zones agreed).
The run kept no before/after strings, so the cause cannot be read offline.

What is known (offline, 2026-10-19 BENCH):
- `RM_PocketGrid.Build` is a full deterministic relabel from `EffectiveDepth` (dug depth + intact `Building_SpanDeck`s),
  so the same map gives the same `comp`/`size`; a difference means the INPUT differed when one side was read.
- The covers zone is the only B7 zone holding decks (hostile-owned pit covers from B4 `g_cover_tiers`).
- Deck spawn/despawn bumps `ClimbGeneration`, but the rebuild is throttled to `RebuildMinTicks` = 60 unpaused
  (`RM_PocketGrid.RebuildIfStale`), and `RM_MapComponent_Excavation.FinalizeInit` notes the grid "may have been built by
  region building" during the load. Leading hypothesis: the after-load read hit a grid built before the decks were
  counted (a transient up to 60 ticks), not a save/load loss. Unproven.

Harness change (this item): B7 now records `pairs` {before, after, settled} for every differing key and `settledSame`
(keys that agree again after `RELOAD_SETTLE_TICKS` = 120). Bar: one run with the strings. settledSame = all ->
transient (decide whether a 60-tick stale grid after load matters; likely a one-line rebuild-on-FinalizeInit fix);
still differing -> a real reload difference, trace which input (deck Decked/Read, depth) changed.
Re-run: `live_session.py --only B0,B4,B7` (pass 2 F1).
