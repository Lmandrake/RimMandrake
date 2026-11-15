# RIMMANDRAKE_STOP_RETRYING_A_PRE_PUSH_REFUSAL

## Defect
`./publish` retried a pre-push hook's `REFUSED` (orphan item prose: an item spec pushed without its ledger row) as if it
were a network blip: three sleeps, each printing only git's last line "failed to push some refs", exit 2. The hook's
reason showed only with a hand `git push --dry-run` (2026-11-15 ~1:40 PM PST, this run).

## Fix
`publish.py` push loop: a non-non-fast-forward error whose stderr holds a line starting `pre-push REFUSED` raises at once
with the whole hook output ("nothing pushed"). The DLL/source-stamp guard keeps its own rebuild-and-retry branch above it.

## Acceptance test
`python3 src/RimMandrake/Utils/selftest_publish.py` -> `50/50 passed`; `t_hook_refusal_stops_at_once_with_its_reason`
failed on base 7d5ca1bf71 ("the refusing hook ran 3 times", watched) and fails again with the detection disabled (watched).
