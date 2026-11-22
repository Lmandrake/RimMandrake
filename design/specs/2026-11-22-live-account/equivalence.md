# Equivalence: six old readers of the live account against the one home (account_live.py)

Run 2026-11-22 by `python3 design/specs/2026-11-22-live-account/equivalence.py` (old readers from base `9d0bc39906`,
taken verbatim with `git show`; cases from `src/RimMandrake/Utils/fixtures/account_live_cases.json`, built by
`build_fixtures.py` beside this file). Planted faults: `mutations.py` beside this file (8 planted, 8 caught).

Inputs: 43 cases. 24 are recorded: the real `claude-account --json status` output on Archmagi and on SteveDesktop
(over ssh, through a login shell), and the 22 `use` rows of `~/.claude-accounts/log.jsonl` (2026-10-28 to 2026-11-21),
each rendered as the Archmagi status with `live` set to the row's account. 19 are fixture shapes from the boundary page.
Emails in the fixtures are scrubbed.

Result: on all 24 recorded cases, every old reader and the new home give the same account. 23 differences, all on
fixture shapes, all classed "old was wrong"; 0 unexplained. Besides those, two old readers raised where the new home
answers: `account_usage.remote_live` (AttributeError on a JSON list) and `running_now.collect_inuse` (PermissionError,
uncaught). The bare `account_handover` expression raises on 12 of the 43 cases (a traceback ends its timer pass); the
harness counts that as UNMEASURED.

The classes:
- A warning line or banner before the JSON hid the account from `slot_allocator`, `running_now`, `account_handover`
  and `remote_live` (they `json.loads` the whole stdout). This is the planted case of acceptance line ACCOUNT.
- A non-zero exit with a `live` name in stdout was read as the account by `slot_allocator`, `account_handover` and
  `remote_live`. The switcher exits 0 on success; the new home reads it failed.
- `"ok": false` with a `live` field was read as the account by five readers. It is the switcher's refusal.
- `running_now` refused a status with no `ok` key; the test fakes and an older switcher print none.
- `running_now` printed `3` for a non-string `live`.

## The table

```
cases 43 (24 recorded, 19 fixture); old readers 6; base 9d0bc39906
case                                        source    new         account_failover | switching_plan | slot_allocator | running_now | account_handover check | account_usage
archmagi-real                               recorded  lukas       lukas | lukas | lukas | lukas | lukas | lukas
stevedesktop-real-over-ssh                  recorded  system      system | system | system | system | system | system
switch-to-lukas-2026-10-28T12:45:15-07:00   recorded  lukas       lukas | lukas | lukas | lukas | lukas | lukas
switch-to-system-2026-10-28T14:10:27-07:00  recorded  system      system | system | system | system | system | system
switch-to-steven-2026-10-28T18:36:17-07:00  recorded  steven      steven | steven | steven | steven | steven | steven
switch-to-system-2026-10-30T15:31:43-07:00  recorded  system      system | system | system | system | system | system
switch-to-lukas-2026-11-01T17:37:52-08:00   recorded  lukas       lukas | lukas | lukas | lukas | lukas | lukas
switch-to-steven-2026-11-03T18:54:23-08:00  recorded  steven      steven | steven | steven | steven | steven | steven
switch-to-system-2026-11-04T01:26:38-08:00  recorded  system      system | system | system | system | system | system
switch-to-steven-2026-11-06T00:30:28-08:00  recorded  steven      steven | steven | steven | steven | steven | steven
switch-to-lukas-2026-11-06T11:26:26-08:00   recorded  lukas       lukas | lukas | lukas | lukas | lukas | lukas
switch-to-steven-2026-11-06T11:30:11-08:00  recorded  steven      steven | steven | steven | steven | steven | steven
switch-to-lukas-2026-11-06T12:27:44-08:00   recorded  lukas       lukas | lukas | lukas | lukas | lukas | lukas
switch-to-system-2026-11-11T11:57:07-08:00  recorded  system      system | system | system | system | system | system
switch-to-steven-2026-11-11T16:52:53-08:00  recorded  steven      steven | steven | steven | steven | steven | steven
switch-to-system-2026-11-12T13:50:50-08:00  recorded  system      system | system | system | system | system | system
switch-to-lukas-2026-11-15T12:05:20-08:00   recorded  lukas       lukas | lukas | lukas | lukas | lukas | lukas
switch-to-steven-2026-11-17T05:46:13-08:00  recorded  steven      steven | steven | steven | steven | steven | steven
switch-to-lukas-2026-11-17T05:54:00-08:00   recorded  lukas       lukas | lukas | lukas | lukas | lukas | lukas
switch-to-system-2026-11-17T05:58:49-08:00  recorded  system      system | system | system | system | system | system
switch-to-steven-2026-11-17T21:33:12-08:00  recorded  steven      steven | steven | steven | steven | steven | steven
switch-to-system-2026-11-18T18:59:06-08:00  recorded  system      system | system | system | system | system | system
switch-to-steven-2026-11-20T18:40:21-08:00  recorded  steven      steven | steven | steven | steven | steven | steven
switch-to-lukas-2026-11-21T17:45:13-08:00   recorded  lukas       lukas | lukas | lukas | lukas | lukas | lukas
warning-line-before                         fixture   lukas       lukas | lukas | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED
login-banner-before-and-note-after          fixture   lukas       lukas | lukas | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED
acceptance-fake                             fixture   lukas       lukas | lukas | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED
long-padding-before                         fixture   system      system | system | system | UNMEASURED | system | system
no-ok-key                                   fixture   system      system | system | system | UNMEASURED | system | system
cut-at-1000-chars                           fixture   UNMEASURED  UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED
cut-at-2000-chars-of-a-long-status          fixture   UNMEASURED  UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED
live-empty-string                           fixture   UNMEASURED  UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED
live-null                                   fixture   UNMEASURED  UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED
live-not-a-string                           fixture   UNMEASURED  UNMEASURED | UNMEASURED | UNMEASURED | 3 | UNMEASURED | UNMEASURED
refused-rc1                                 fixture   UNMEASURED  UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED
not-ok-rc0                                  fixture   UNMEASURED  beta | beta | beta | UNMEASURED | beta | beta
rc3-with-a-live-name                        fixture   UNMEASURED  UNMEASURED | UNMEASURED | lukas | UNMEASURED | lukas | lukas
empty-stdout                                fixture   UNMEASURED  UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED
garbage                                     fixture   UNMEASURED  UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED
json-list                                   fixture   UNMEASURED  UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED (raised AttributeError)
timeout                                     fixture   UNMEASURED  UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED
not-found                                   fixture   UNMEASURED  UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED
permission-denied                           fixture   UNMEASURED  UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED (raised PermissionError) | UNMEASURED | UNMEASURED
differences old vs new: 23; classed 23; unexplained 0
  classed  account_failover.live_account / not-ok-rc0: old was wrong: "ok": false is the switcher's refusal; its live field is not a reading
  classed  account_handover check / acceptance-fake: old was wrong: a warning line before the JSON hid the account (json.loads of the whole stdout)
  classed  account_handover check / login-banner-before-and-note-after: old was wrong: a warning line before the JSON hid the account (json.loads of the whole stdout)
  classed  account_handover check / not-ok-rc0: old was wrong: "ok": false is the switcher's refusal; its live field is not a reading
  classed  account_handover check / rc3-with-a-live-name: old was wrong: a non-zero exit is a failed status run, not an answer (the switcher exits 0 on success)
  classed  account_handover check / warning-line-before: old was wrong: a warning line before the JSON hid the account (json.loads of the whole stdout)
  classed  account_usage.remote_live / acceptance-fake: old was wrong: a warning line before the JSON hid the account (json.loads of the whole stdout)
  classed  account_usage.remote_live / login-banner-before-and-note-after: old was wrong: a warning line before the JSON hid the account (json.loads of the whole stdout)
  classed  account_usage.remote_live / not-ok-rc0: old was wrong: "ok": false is the switcher's refusal; its live field is not a reading
  classed  account_usage.remote_live / rc3-with-a-live-name: old was wrong: a non-zero exit is a failed status run, not an answer (the switcher exits 0 on success)
  classed  account_usage.remote_live / warning-line-before: old was wrong: a warning line before the JSON hid the account (json.loads of the whole stdout)
  classed  running_now.collect_inuse / acceptance-fake: old was wrong: a warning line before the JSON hid the account (json.loads of the whole stdout)
  classed  running_now.collect_inuse / live-not-a-string: old was wrong: a non-string live is not an account name
  classed  running_now.collect_inuse / login-banner-before-and-note-after: old was wrong: a warning line before the JSON hid the account (json.loads of the whole stdout)
  classed  running_now.collect_inuse / long-padding-before: old was wrong: a status with no ok key (an older switcher, the test fakes) names its account; only ok=false is a refusal
  classed  running_now.collect_inuse / no-ok-key: old was wrong: a status with no ok key (an older switcher, the test fakes) names its account; only ok=false is a refusal
  classed  running_now.collect_inuse / warning-line-before: old was wrong: a warning line before the JSON hid the account (json.loads of the whole stdout)
  classed  slot_allocator.live_login_name / acceptance-fake: old was wrong: a warning line before the JSON hid the account (json.loads of the whole stdout)
  classed  slot_allocator.live_login_name / login-banner-before-and-note-after: old was wrong: a warning line before the JSON hid the account (json.loads of the whole stdout)
  classed  slot_allocator.live_login_name / not-ok-rc0: old was wrong: "ok": false is the switcher's refusal; its live field is not a reading
  classed  slot_allocator.live_login_name / rc3-with-a-live-name: old was wrong: a non-zero exit is a failed status run, not an answer (the switcher exits 0 on success)
  classed  slot_allocator.live_login_name / warning-line-before: old was wrong: a warning line before the JSON hid the account (json.loads of the whole stdout)
  classed  switching_plan.switcher_status / not-ok-rc0: old was wrong: "ok": false is the switcher's refusal; its live field is not a reading
  raised   account_usage.remote_live on 1 cases: json-list
  raised   running_now.collect_inuse on 1 cases: permission-denied
EQUIVALENCE PASS
```
