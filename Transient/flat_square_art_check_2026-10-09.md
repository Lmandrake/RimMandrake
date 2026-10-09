# Flat square art check 2026-10-09

Finding: neither Murrelith nor Thavrik carries a KEEP ruling. Nothing was overwritten; both files are the original placeholders
(395/394 bytes, git history is the single birth commit ba560a36c, never touched since; `make_placeholders.py` sits beside them).

Source: infrastructure/state/art_rulings/2026-10-07_feverwood_sheet_2026-10-05.decisions.json (RM_FeverWood sheet, owner rulings 2026-10-08)
- RM_Murrelith: decision `redo` - "Very close. Please regenerate but make those streamers beautifully translucent rainbow colors, regally." (prefill A). Regen owed, not a keep.
- RM_Thavrik: decision `hold` - "no longer needed".
- RM_Chellow: decision B; N/S are real renders (Oct 8), but RM_Chellow_east.png is still a 394-byte placeholder.

Real renders: Murrelith has finished artpipe jobs (feverwood_murrelith_*, regen_fw_murrelith_flying_{1,2}_v1_* in _artpipe/done); Thavrik only feverwood_thavrik_{n,s,e} done jobs. Not installed; no ledger-kept sha differs from live.

Sweep (src/**/Textures, Pawn/Plant, excluding *m.png; flat = >95% opaque px within distance 12 of mean): 2427 scanned.
Probes: RM_Skellick_east 6.7% flat (not flagged); Murrelith_east and Thavrik_east 100% (flagged).
Hits: RM_Murrelith x3, RM_Thavrik x3, RM_Chellow_east (ruling B, east owed), RM_Drommath, RM_Ollareth (FeverWood), RM_Sorruth (TerminalBiomes), RM_TrackPrint_Animal (CreatureBehaviors, likely a deliberate icon); the last four have no sheet ruling found.
Action taken: none (no restore).
