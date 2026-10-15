# Test-environment hardening (BENCH builder, 2026-10-15)

Items: `TESTENV_SITE_HEAT_HARDEN_COOKS_BY_ROW3`, `TESTENV_FOGGED_MECH_HARDEN_WOKE_ON_REVEAL`. The full write-ups and proof
commands are in `infrastructure/state/items/<ID>.md`.

## Where the harnesses live
- Pyrelands suite: `src/RimMandrake/Pyrelands/validation.py` (its `_comp` / `_wait` are the per-row and wait hooks), run by
  `Utils/northstar_driver/cli.py` with `northstar_plan.py`.
- GSS: `src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py` P3 (site prep). The fog reveal is
  `Utils/validation_core.py` `reveal()`, called by `prepare_site` (aerial, style and FlowWorks sites).
- Shared quiet profile: `Utils/modcheck/quiet_site.py`. It was not changed; it is still DIRTY and was never reviewed.
- The new shared module is `Utils/modcheck/testenv_guards.py`, with its selftest `selftest_testenv_guards.py`.

## Heat: what changed
- The Heatstroke guard removes only the vanilla Heatstroke hediff from the colonists. It runs at the start of each row and
  every 6000 ticks of waiting. The site's heat is never touched.
- It is exempt in rows that read Food or felt temperature (`scorchfruit_produces`, `furnacebeast_warmth`).
- The vanilla formula gives at most 0.18 per chunk at 65 C. An unguarded half day at 56.7 C gives 0.67, which matches r5's
  measured 0.65.

## Fogged mech: what changed
- The root mechanism, from rimsage:
  - TriggerUnfogged and RectTrigger fire SignalAction_Ambush / DormancyWakeUp.
  - FloodUnfog wakes every pawn it uncovers and sends the "Area revealed" ThreatBig letter when a mechanoid is among them.
- `disarm_fog_triggers()` vanishes every trigger and signal action (Ethereal) and reads them back.
- `proof_all` P3 now runs: disarm, then hostile buildings, then non-colonists, then the pin. After that it disarms again and
  reads back hostile pawns, and FAILs SITE if any is left.
- `reveal()` disarms before any colonist's sight.

## Offline checks
- `selftest_testenv_guards.py`
- `selftest_pyrelands_site.py` (`test_heat_guard_2026_10_15`)
- `selftest_proof_all.py` (5b)

The `run_selftests --only` run of those, plus `selftest_proof_hose`, `selftest_quiet_site` and `selftest_theforge`, is GREEN.

## Proof commands (next live round)
They are written into each item file. In short:
- Pyrelands: `cli.py run --mod Pyrelands --chains scorchfruit_fire_born,scorchfruit_produces,scorchfruit_spoils,firehawk` on
  the reloaded r6 site.
- GSS: `proof_all.py --live --no-shots` on 2-3 fresh maps.

## Commits / CLEAN status
See the commit log. All 7 changed files are marked CLEAN after a full-file review.
