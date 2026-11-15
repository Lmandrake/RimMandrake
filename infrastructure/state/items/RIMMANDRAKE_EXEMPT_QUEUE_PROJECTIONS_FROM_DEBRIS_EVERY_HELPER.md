# RIMMANDRAKE_EXEMPT_QUEUE_PROJECTIONS_FROM_DEBRIS_EVERY_HELPER

## spec

`src/RimMandrake/rimflow/wrapup.py` `check_clone` files a finished helper clone as debris when it holds untracked
`infrastructure/state/queue/<SEAT>.md` files. Those are rimflow queue projections, regenerated on every rimflow call;
only `queue/HUMAN.md` is tracked on main, so every helper clone carries a dozen of them and `wrapup.debris_standing`
reads 1+ with no work in it (incident `wrapup-20261113102602`, measured 2026-11-15 07:30 PST: the one standing row,
unit `...harden-bridge-lock-owner-hol-1794751190`, inactive, 0 unpushed, 15 untracked paths = 14 projections + one
conversations/ export).

Fix: exempt untracked `?? infrastructure/state/queue/<name>.md` lines (a direct child `.md` file only) the same way
the `?? conversations/` lines are exempted. A nested path under `queue/`, or any other untracked or modified path,
stays debris.

## verify

Acceptance test: `python3 src/RimMandrake/Utils/acceptance_wrapup_queue_projections.py` must print `PASS 6/6` and
exit 0. Watched FAIL on base 5b43546145 (`PASS 3/6`: one_projection, many_projections and
projections_and_conversation filed as debris). Also run `run_selftests.py --only selftest_wrapup.py`.
