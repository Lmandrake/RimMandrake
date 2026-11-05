## spec
Class unknown (HARNESS or SITE most likely), from test pilot gen 19 of GRAFFITI_NORTHSTAR_GREEN_FULL_1 (live A2 2026-11-05,
fresh 250x250 TemperateForest quicktest, small list). Gen 11 saw the same family (a Toughspike arrival, a "Crush" death).
- Expected: the suite's colonists do not die; a fleshbeast does not appear on a fresh quicktest.
- Observed (`jawa/vitals action=events`, `jawa/damage_log`): colonist Alekey (Human22132) died at tick 601 at cell 125,125, and
  Stonejaw (Human22158, in RM_GraffitiPaintingSpreeState since 601) died at tick 1501 at cell 123,129. Both are damage_log kind
  `kill`, amount 0.0: a direct Kill with no damage, vitals "died: unknown cause". At tick 1501, two Fingerspikes (ids 8592,
  8593) "arrived" and "departed" in the same sample. Every functional row still PASSED.
- RULED OUT: `suite._clear_pawns` vanish as the killer (each vanished pawn reads `departed`, never a death).
- Next: find the Kill(null) caller around the chain boundaries (`_prep_site` -> `clear_area` -> destroy_batch / spawn_batch
  walls over a standing pawn?). Find where the Fingerspikes came from (world pawns spawned by what?).
- Evidence: `D:\ClaudeWork\rimmandrake\testpilot_GRAFFITI_NORTHSTAR_GREEN_FULL_1\g19\latched.txt`, `D:\ClaudeWork\rimmandrake\testpilot_GRAFFITI_NORTHSTAR_GREEN_FULL_1\g19\dmg.txt`.
