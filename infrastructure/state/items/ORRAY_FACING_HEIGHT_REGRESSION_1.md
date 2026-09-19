## spec

The approved Pyrelands render wave (`9e7e773a0`, 2026-09-17, "Wire approved
Pyrelands creature render wave into art-override mods") replaced Orray's three
facings and broke facing-height coherence badly.

**MEASURED 2026-09-18** with `art_checks.py` (`facing_height_consistency`,
instrument: max/min of visible-alpha bbox HEIGHT over the facing set, alpha>16;
height only, never area):

| | ratio | verdict |
|---|---|---|
| pre-wave blob `9e7e773a0^` | below 1.35, **no finding** | known-good |
| on disk now | **2.488** (south is 2.49x taller than east) | high |

Context for how bad 2.488 is: it is the **second-worst row in the whole
Pyrelands corpus** (only `AA_Razorjack` at 3.143 is worse), and worse than
every row the owner named out loud as broken — Anooba, which he described as
"North is HUGE compared to east", measures 1.458/1.560.

Orray was one of only four creatures pinned in `art_checks.py`'s
`HEIGHT_MUST_PASS` as a known-good control for the 1.35 threshold. So this
regression did not merely add a finding: it broke the selftest, which is how it
was found (`SELFTEST_FAILURE_TRIAGE_1`).

## verify

Orray's three facings agree on visible height within the 1.35 threshold, and
`Orray` is returned to `HEIGHT_MUST_PASS` in
`src/RimMandrake/Utils/art_checks.py` with `HEIGHT_REGRESSION` emptied of it.

⛔ **Do not close this by loosening `FACING_HEIGHT_MAX_RATIO`.** The threshold is
calibrated against seven owner- or measurement-confirmed breaks; raising it past
2.488 would unflag most of them.

## open

- **Needs the owner**, `needs: owner`. Two routes and the choice is his, not
  ours: regenerate Orray's south (or east) so the facings agree, or rule the new
  art acceptable as-is — in which case `Orray` moves from `HEIGHT_REGRESSION`
  to `HEIGHT_MUST_FLAG` with his words recorded, and the pin becomes a permanent
  documented exception like `FurnaceBeast`.
- Pinned meanwhile at `HEIGHT_REGRESSION = {"Orray": 2.488}` in `art_checks.py`,
  so the selftest fails loudly if the number moves in EITHER direction rather
  than the regression going quiet.
- Not yet looked at by eye. The instrument says the silhouettes disagree on
  height; it does not say which facing is the wrong one.
