# RELENTLESS_WIRE_MARKER_VERDICT_AND_REPAIR

## spec

WP-09a left two gaps. (1) The Marker-verdict append has no call site: add one in the relentless.py tick calling evidence.harvest (today only the manual 'evidence.py harvest' CLI exists). (2) One corrupt line in the evidence index stops new receipts: add an evidence-index repair command (dry-run by default, backs up, removes only unparseable lines, cap like repair_torn_ledger).

Done when: a tick appends the Marker verdict with no manual harvest (selftest with a planted tick), a planted corrupt index line is repaired by the command and receipts resume, both red under planted breaks.

Source: /mnt/d/ClaudeWork/rimmandrake/conductor/redesign_2026-11-06/stage4_log.md WP-09a and FOLLOWUPS (cont.); /mnt/d/ClaudeWork/rimmandrake/conductor/redesign_2026-11-06/redesign_final.md row 09a
