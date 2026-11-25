# Polish: the account drain (`switching_plan.py`), beside `boundary.md`

- `_check`'s pre-poll brake writes `{**pre, "do": "soft"}` for any decision in `ACTS`, `stopped` included: during the poll a stopped fleet's notice reads `soft` with `switch_pending` true, and `notice_refusal` (no drain) refuses nothing by the notice; the published decision still refuses, and the pass writes `stop` again after its poll.
