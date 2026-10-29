## spec
found-by: proof_restore_check.py (BENCH, 2026-10-26, systemic sweep from lesson infrastructure/state/lessons/20261026T161651Z-BENCH-proof-scene-restore-leak.md).
Tool: src/RimMandrake/Utils/proof_restore_check.py (selftest selftest_proof_restore_check.py; each hit below is counted under a BASELINE key there: lower or remove the count when fixed).

A live proof that changes a def or a Mod Settings field must undo it on EVERY exit path (finally / registered restore run on
INVALID, ERROR and throw), putting back the value it READ before the poke, never a hard-coded default. The hits below either
poke outside any try/finally that restores (unrestored-on-throw), restore a fixed literal/DEFAULTS value (restores-fixed-value),
or call Settings("reset") with nothing remembered (reset-loses-player-values). A leaked poke poisons every later test in the
running game and can overwrite the player's settings.

Filed, not fixed: bridgetools/JawaBench was excluded from this sweep's edits (another batch owns it). Fix pattern: see 0a6567cce8 (C# restore delegate before the
poke, RunRestore on re-stage/INVALID/ERROR/Verdict finally) and this sweep's knockback_runner.py snapshot_settings/restore_settings.
A deliberate exception gets  on the hit line or the line above.

### hits (file:line kind target :: text), measured 2026-10-26 (1 hits)
- src/RimMandrake/bridgetools/prove_sea_dive_floor.py:85 unrestored-on-throw raw :: `call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=_f, value=_v)`
