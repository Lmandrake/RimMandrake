# PIT_COVER_DIAGNOSE_GIVES_WAY_TOO_SOON

Class: MOD (presumed, untraced). BENCH live 2026-10-19, flowworks tier (11 mods), FlowWorks DLL ccf36a9af7.
live_session B4 cover rows, run `Transient/live_session/20261018T233414/session.json` (B4_cover_*):
a deck of six covers in a row over 2 m (4-notch) dug cells, owned by a non-player faction (the cover spares its own
faction), one drafted colonist spawned on the deck's first cover; 70 ticks (two 30-tick scans).

- WovenScrap (40 kg): 60.7 kg colonist fell - correct.
- PlankLattice (120 kg): ONE 60.9 kg colonist fell (depth 4.0).
- ReinforcedFrame (220 kg): ONE 54.6 kg colonist fell (depth 4.0).

The previous run (single cover per tier, `20261018T232207`) held 60.8 kg on PlankLattice, so the difference is the
six-cover DECK: suspect the deck sum (RM_SpanUtility.LoadOn over every deck cell) or the weakest-cover rule
(CompPitCoverTrigger, GPT C4-F5) reading a cover of the wrong tier, or adjacency to the 40 kg deck 2 cells away.
Rule out first: a pawn spawned onto a cover counted twice, the 2-cell gap counting as one deck.

Bar: a 120 kg deck holds 1 colonist and gives way at the 2nd (>=120 kg summed); 220 kg holds 3 and gives way at the 4th.
