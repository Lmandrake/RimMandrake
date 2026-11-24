# BOUNDARY: the pager (`pager.py`), Design Version 0.1.0

Code: `src/RimMandrake/Utils/pager.py`, its class list `pager_classes.json`, and its digest readings
`ops_watch_pager.py` (the `pager` family of `ops_watch.py`). Design: `design.md` beside this page. Written Thu
2026-11-19, 7:20 PM PST, item `RIMMANDRAKE_DESIGN_PUSHOVER_ALERTS_CRITICAL_ONLY_TWO_SENDERS`. Each promise has a test of
its own name in `src/RimMandrake/Utils/selftest_pager.py`. The planted faults that the tests must catch are in
`src/RimMandrake/Utils/pager_plants.py` (21 of 21 caught, 2026-11-19).

## ACCEPTS (the only inputs the pager is built for)

- **send.** `pager.py send --class C --cause K --reading R --why W [--item ID] [--goal G] [--dry-run]`, from the
  Conductor window or an Operations role run. C is a class in `pager_classes.json`; K is a reading's key; R is the
  reading in letters, digits, spaces and `_.,:;=<>%+()#-`, at most 200 characters; W has at least four words; ID is an
  item id; G is a goal title, for `GOAL_SHOCK` only.
- **test.** `pager.py test --why W [--dry-run]` from the Conductor window: one emergency page of class `TEST`.
- **reads.** `check-credentials`, `ack [<receipt>]`, `status`, `classes`. They ring nothing.
- **credentials.** `PUSHOVER_USER_KEY` and `PUSHOVER_APP_TOKEN` in the environment, else as `NAME=value` lines in
  `<RM data root>/secrets/pushover.env` (`RM_PAGER_CREDENTIALS` overrides the path). Each is 30 letters and digits.
- **one-machine.** One user on Archmagi's WSL, the pager dir on the agent storage root (`RM_PAGER_DIR` overrides it),
  callers under that user's systemd.

## PROMISES

- **only-two-senders.** `caller` returns `conductor` only for seat BENCH, no `RM_ROLE_UNIT`, and a cgroup in a window
  scope `claude-seat-BENCH-<pid>.scope` with no `rm-*` unit on its path. It returns `operations` only for
  `RM_ROLE_UNIT=rm-role-operations-<epoch>`, seat BENCH, and that unit on the cgroup path. Every other caller (a
  detached helper, with or without `RM_ROLE_UNIT`; another role run; another seat; a plain shell; an unreadable cgroup)
  is refused, and its verdict line names why.
- **refusal-is-logged.** A refused send writes one `log.jsonl` line with the outcome `REFUSED` and its reason, calls no
  network, and writes no Conductor log line.
- **closed-class-list.** A class not in `pager_classes.json` is refused. A class refuses a sender it does not name
  (Operations cannot send `GOAL_SHOCK` or `TEST`). A class list that is malformed, or has an entry without its
  `added` record by CONDUCTOR, refuses every send.
- **fixed-template-text.** Pushover receives exactly the fields token, user, title, message, priority, retry and expire,
  and `sound` (`echo`) on every class but `TEST`.
  The title is `RimMandrake CRITICAL: <label>`; the message is the class template filled with the reading, goal and item.
  A reading that could carry a path, address, URL, quote or newline is refused before any send. The why is never sent.
- **emergency-priority.** Every page is priority 2, retry 120 s, expire 3600 s, to `api.pushover.net/1/messages.json`,
  inside Pushover's limits (retry at least 30 s, expire at most 10800 s, at most 50 retries).
- **goal-must-be-stated.** `GOAL_SHOCK` is refused unless `--goal` is a numbered goal title in the top block of
  `CONDUCTOR_GOALS.md`; it is refused when that file cannot be read; `--goal` on another class is refused.
- **one-fault-pages-once.** The key is class plus cause. A send for an open key inside its class's window is `REPEAT`:
  no network, the record's repeat count and last reading updated. After the window, the same key pages again. `TEST`
  never dedupes.
- **failed-send-stays-pending.** A `COULD_NOT_SEND` does not open the key; the next send for it calls Pushover again; a
  `SENT` clears the failing streak.
- **four-outcomes-apart.** SENT 0, REFUSED 1, REPEAT 2, COULD_NOT_SEND 3, DRY_RUN 4. `SENT` only for HTTP 200 with
  status 1 and a receipt. A 200 without a receipt, any 4xx or 5xx, no answer, and missing credentials are each
  `COULD_NOT_SEND` with the cause named; missing credentials call no network. A dry run calls no network and writes no
  state, and says what it would send, that credentials are missing, or that it would be a repeat.
- **could-not-send-is-visible.** A failing streak writes one Conductor log line when it starts, a `log.jsonl` line for
  every attempt, and its attempt count in state; the send that finally leaves says how many failed first.
  `ops_watch_pager.points` reads the streak as `pager.could_not_send` (MEASURED); no state file reads a measured 0; a
  torn state reads UNMEASURED.
- **secrets-never-printed.** Neither credential value appears in a verdict line, `log.jsonl`, `state.json` or the
  Conductor log; a misshapen value is named by its variable, never shown.
- **torn-state-not-read-as-empty.** `read_state` raises on a torn or wrong-shaped `state.json`; `status` exits 3 on it;
  a send still pages (a critical page is not lost to a bad file) and moves the torn file aside, never overwriting it
  unread.
- **page-survives-a-bad-pager-dir.** When the pager dir cannot be written (no lock, no state, no log), a send still
  pages, reports `SENT`, names the lock and state errors in its record, and writes its Conductor log line. A crash of
  the tool prints `PAGER ERROR` and exits 5; it claims no outcome.
- **check-credentials-rings-nothing.** `check-credentials` calls only `users/validate.json`: 0 valid, 1 Pushover says
  invalid, 3 could not look (no file, no answer).

## DOES NOT SURVIVE (not promised)

- **deliberate-bypass.** A helper that starts its own scope (`systemd-run --user --scope`) named like a window's, sets
  seat BENCH and unsets `RM_ROLE_UNIT`; or any process that posts to Pushover itself with the credentials. The gate is
  not a security wall; the credentials file is readable by the user.
- **a-hand-edited-class-list.** A class added to `pager_classes.json` without the Conductor's ledger note. The loader
  checks the `added` record's shape, not that the act was logged.
- **pushover-accepts-then-loses.** Pushover returns a receipt and then fails to deliver. `ack` shows it as not
  acknowledged; nothing re-sends.
- **phone-settings.** Critical Alerts off on his iPhone, or Pushover's app removed. The page is `SENT` and rings
  quietly or not at all.
- **a-receipt-poll-without-a-page.** `ack` with no page ever sent says it could not look; it does not wait.
- **two-machines.** A second machine with its own pager dir dedupes separately.
- **state-written-after-a-sent-page-fails.** Pushover accepted the page and then `state.json` could not be written:
  the next call rings again.

## LIFE CYCLES

- A fault key: absent → SENT (open, paged at T) → REPEAT … (inside the window) → SENT again after the window.
- A failing streak: absent → COULD_NOT_SEND (streak starts: one Conductor line) → COULD_NOT_SEND … → SENT (streak
  cleared, the Conductor line names the failed attempts).

## LIMITS (each with the danger it guards)

- **window_h per class** (24 h, 6 h, 168 h, 0): an alert that rings again for a fault he already knows trains him to
  ignore the pager (design §4).
- **RETRY_S 120, EXPIRE_S 3600**: a page that rings once is missed; one that rings every 30 s for 3 h is muted (design
  §5). Pushover's own bounds: retry ≥ 30, expire ≤ 10800.
- **HTTP_TIMEOUT_S 20**: urllib waits forever without a timeout (default None), and the lock is held across the send,
  so one hung connection would block every later page.
- **reading at most 200 characters, cause at most 80**: the text goes to Pushover's servers; a longer field is not a
  reading, and Pushover refuses a message over 1024.
- **why at least 4 words**: a page with no stated reason cannot be judged afterwards.
