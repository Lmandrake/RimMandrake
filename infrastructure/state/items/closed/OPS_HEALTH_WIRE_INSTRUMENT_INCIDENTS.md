# OPS_HEALTH_WIRE_INSTRUMENT_INCIDENTS

## spec

WP-06 leftovers. (a) Utils/ops_health.py does not read instrument_incidents.json (callers pass ids): make it read the file itself. (b) PROOFLESS_WIRE_ENROL_487_BUILT_STRANDED is still classed content, so under a pipeline-only pause it is not treated as a system item: class it system (is_system/system_items) so the reserved repair slot can enrol it.

Done when: ops_health reads instrument_incidents.json without caller-supplied ids (selftest, red when the file is ignored) and PROOFLESS_WIRE_ENROL_487_BUILT_STRANDED is classed system under a pipeline-only pause.

Source: /mnt/d/ClaudeWork/rimmandrake/conductor/redesign_2026-11-06/stage4_log.md FOLLOWUPS line 3; /mnt/d/ClaudeWork/rimmandrake/conductor/redesign_2026-11-06/redesign_final.md row 06
