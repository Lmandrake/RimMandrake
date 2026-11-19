## spec
Codex full-file review of src/RimMandrake/rimflow/maturation.py (2026-11-18, `D:\ClaudeWork\rimmandrake\evidence\finish_rollback\rb_codex.txt`, its second P1, pre-existing): `seed_mod` promises "an existing record is returned untouched", but `load()` returns None both when the stage record is absent and when it is unreadable or not JSON, so `maturation.py seed` on a mod whose record is corrupt writes a fresh seeded record over it and the old state is lost. (maturation_autonomy's seed step checks `isfile` first, so only the CLI seed path is exposed.) Watched failing on e2aa419fe1 (red: seed_mod returned, no error). Fix: seed only when the record is measured absent; an existing record that cannot be read raises ValueError (the CLI prints NOT SEEDED and exits 1) and is left as it is.

## verify
Acceptance test: in selftest_maturation's seeding section, a corrupt ExplosiveKnockback record: seed_mod raises ValueError and the file is byte-identical after. `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation` (1/1 GREEN after; red on base e2aa419fe1, watched failing).

## criteria
- seed_mod never writes over an existing stage record it cannot read.

## refs
file: src/RimMandrake/rimflow/maturation.py
file: src/RimMandrake/rimflow/selftest_maturation.py
