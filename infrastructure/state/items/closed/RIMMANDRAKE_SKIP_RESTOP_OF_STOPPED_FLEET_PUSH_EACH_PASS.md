## spec
src/RimMandrake/Utils/switching_plan.py decide(): two branches return a fresh `stop` while the fleet is already stopped
on the live account (state["stopped"]["account"] == live): a pending switch marker under STALE_PENDING_S with live under
its line, and a spent live whose target cannot be confirmed after a poll. Each pass then calls fleet-stop again, and
record_stop() re-stamps state["stopped"] (dropping phone_notified, new `at` in the push key), so notify_stop sends a new
red "Claude stopped: all accounts are out" phone push every pass while it lasts. Found by Codex's full-file review of
switching_plan.py in RIMMANDRAKE_ATTRIBUTE_MANUAL_SWITCH_BY_LOG_NOT_OLD_MARKER (D:\ClaudeWork\rimmandrake\lane4\sp_codex_review.md
point 3); reproduced with decide() fixtures. The other stop branches already answer `stopped` (the no-target branch and
the failed-marker branch guard on it).

## verify
python3 src/RimMandrake/Utils/selftest_switching_plan.py   # exit 0
Watched failing on e219f1e872: 2 of 2 "...already stopped on live: stopped, not a new stop (got stop)"; the control
(no stop recorded: stop) passes on base. Expected: all passed.

## criteria
- A fleet already stopped on the live account is answered `stopped` by every stop branch; a spent live with no stop recorded still stops.
