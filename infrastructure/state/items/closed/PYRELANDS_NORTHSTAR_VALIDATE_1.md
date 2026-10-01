# PYRELANDS_NORTHSTAR_VALIDATE_1 — owner re-validates the Pyrelands north star

**For:** BENCH (owner card). **Parent:** PYRELANDS_NORTHSTAR_TRIAL_1. **Plan:** `design/RimMandrake/northstar_trials/Pyrelands_trial_plan.md` §1.2, §2.4.
**Depends on:** BIOME_MOD_UNIFICATION_1 (packaging must be settled first; it is, as of wave 2).

MEASURED 2026-09-30 with `modcheck.northstar.parse()`:

- The walk declares `state: VALIDATED`, but its recorded hash is `90a286aa83f1` and the current
  hash is `15e3d4df4583`, so the walk is **effectively DRAFT**.
- `7690c96fb` validated 2 bars on the owner's word.
- `b3457a829` then added 8 more bars without re-validation.

## acceptance

- [ ] BENCH cards the owner on the 10 bars as written, plus plan §2.4's proposed additions (6
      must-show bars and 1 cannot-show), in plain language.
- [ ] Bar text he changes is edited into `## north star` in the same sitting.
- [ ] `modcheck/cli.py validate Pyrelands` is run on his typed word, with the quote flag. A card
      click is recorded as "decision taken by question card".
- [ ] `northstar.parse()` then reads VALIDATED with a matching hash.
- [ ] Nothing is edited inside the section after that without re-validating.
