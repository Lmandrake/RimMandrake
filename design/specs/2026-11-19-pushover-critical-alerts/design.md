# Pushover critical alerts: two senders, a closed list of classes, Design Version 0.1.0

Item: `RIMMANDRAKE_DESIGN_PUSHOVER_ALERTS_CRITICAL_ONLY_TWO_SENDERS`. Written Thu 2026-11-19, 7:20 PM PST. Promises:
`boundary.md` beside this file. Code: `src/RimMandrake/Utils/pager.py`.

The owner, 2026-11-19 about 7:00 PM PST, word for word: *"I already have Pushover. On trial for now. We should design
emergency alert system for that now, only for CRITICAL needs like hardware failure, inability to switch accounts, or
shocking inability to achieve a stated goal. Conductor or Operations only."*

## 1. What this is, and what it is not

- **One program, `pager.py`, rings his phone through Pushover.** Nothing else in the estate sends to Pushover.
- **It is narrower than the 2026-11-08 design** (`D:\ClaudeWork\rimmandrake\conductor\phone_alerts_design_20261108.md`).
  That design had three levels, a budget, burst coalescing, a Windows heartbeat sender and an outside watchdog. He now
  asks for critical pages only, from two senders. So this design keeps one level (emergency), a closed list of classes
  and a dedupe. The rest stays in the 2026-11-08 file as candidate next-version work. Todoist stays retired as an alert
  route (`design/RimMandrake/standing_rulings.md` §Todoist is for to-do lists only).
- **Every trigger is OFF until the Conductor switches it on.** §8 lists the triggers. The test page of 2026-11-23, 11:08
  AM PST reached his phone.

## 2. Who may send, and how the caller is proved

Only two callers may page him. `pager.py` proves each caller with two facts: the environment, and the process's own
cgroup. A launched run cannot leave its systemd unit by a change to its environment.

| caller | environment | cgroup |
|---|---|---|
| the Conductor window | seat BENCH (`AGENT_SEAT`, else `RIMFLOW_SEAT`), no `RM_ROLE_UNIT` | a window scope `claude-seat-BENCH-<pid>.scope` (the scope `claude_bounded.sh` gives each window), with no `rm-*` unit on the path |
| an Operations role run | `RM_ROLE_UNIT=rm-role-operations-<epoch>`, seat BENCH | that unit on the path: `rm-role-operations-<epoch>.service`, or its scope `claude-seat-BENCH-rm-role-operations-<epoch>.scope` |

Every other caller is refused: a detached helper, a Producer or Conductor role run, another seat, a plain shell, a
process whose cgroup cannot be read. The refusal goes to `<pager dir>/log.jsonl` (class, cause, the refusal's reason)
and into the ops digest as `pager.refused_24h`. It writes no Conductor log line, so a helper in a loop cannot flood
that log.

What a refused helper sees, measured from this helper's own run (Thu 2026-11-19, 7:15 PM PST), exit 1:

    PAGER REFUSED class=HARDWARE_FAILURE cause=disk.whea_severe_24h refused: a launched run
    (RM_ROLE_UNIT=rm-detached-bench-rimmandrake-design-pushover-alerts-criti-1795143674) is neither the Conductor
    window nor an Operations run

A helper that finds a critical fault writes it on its item (or in the Conductor log), and the Conductor decides whether
to page.

## 3. The closed list of critical classes

The list is `src/RimMandrake/Utils/pager_classes.json`. A class that is not on the list cannot page him. To add or
change a class is the Conductor's logged act: a commit from the Conductor window, and a ledger note with `--per-ruling
RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS --why "<the class and why it is critical>"`. Each entry carries an
`added` record (by CONDUCTOR, the date, the words it rests on). `load_classes` refuses an entry without one.

| class | who may send | window | what fires it (the measured signal) |
|---|---|---|---|
| `HARDWARE_FAILURE` | Conductor, Operations | 24 h | a fatal disk or PCIe error on Archmagi's D: NVMe; SteveDesktop's CPU fault that a reboot does not clear; a disk close to full (§8) |
| `ACCOUNT_SWITCH_FAILURE` | Conductor, Operations | 6 h | the switching plan tried a switch and it failed; the fleet went dark with no account to run on (§8) |
| `GOAL_SHOCK` | Conductor only | 7 days | the Conductor's own judgment, never a program (below) |
| `TEST` | Conductor only | none | the Conductor's drill (`pager.py test`) |

**A shocking failure of a stated goal (`GOAL_SHOCK`).** The Conductor may send it only when all three are true:

1. The goal is one of the numbered goals in the top (newest) block of `infrastructure/state/CONDUCTOR_GOALS.md`.
   `pager.py` refuses any other `--goal` text, and it refuses a goal page when it cannot read that file.
2. The evidence shows that the goal cannot be reached by the means it states. Examples: work that the goal needs is
   lost; a mechanism that the goal rests on is proved unworkable; the goal's own measure went backward over days of
   work that was aimed at it.
3. To wait for his next sitting would cost something real: work lost, spend on a dead path, or a decision that only he
   can take.

An ordinary miss never qualifies: a late date, a failed run, a bounced ticket, a red test, a slow week. A program never
sends `GOAL_SHOCK`. The Conductor's `--why` states the evidence. The Conductor also writes a ledger note with the same
ruling and why, so the act reaches his daily digest.

## 4. One fault pages once

- **The key is the class plus the cause** (`HARDWARE_FAILURE:disk.whea_severe_24h`). The cause is the key of the
  reading that fired it.
- **A repeat of the same key inside its window updates the record and does not ring.** The record keeps the repeat
  count and the last reading. The verdict is `REPEAT` (exit 2). After the window ends, a fault that is still there
  pages again once.
- **The danger that each window guards is an alert he learns to ignore** (his words: "only for CRITICAL needs").
  - 24 h for hardware: a disk or CPU fault does not mend itself in hours. A second ring the same day tells him nothing
    new. The next day's ring tells him that it is still broken.
  - 6 h for accounts: a switch failure can clear at the next reset, or come back on the next account. 6 h is a little
    more than one 5-hour Claude window, so a failure that is still there after the next window reset rings again.
  - 7 days for a goal: a goal failure is decided once. The next week's sitting reads the rest.
  - The test class never dedupes, because each drill must ring.
- **A page that could not leave is not recorded as paged.** The next call tries again (§6).
- **Two callers at the same moment do not both ring.** A file lock covers the read, the send and the write.

## 5. How Pushover is used

- **Emergency priority (2) for every class.** It rings again until he acknowledges it, and each page returns a receipt.
  Pushover's limits (pushover.net, read 2026-11-19): retry 30 s or more, expire 3 h or less, at most 50 retries.
- **Retry 120 s, expire 3600 s: 30 rings in an hour.** The danger of a longer or faster ring: noise that he learns to
  mute. The danger of a shorter one: a page that he misses while he is away from the phone. After the hour, the next
  window brings the fault back if it is still there.
- **No quiet hours.** The closed list is the filter: each class is something he would want to know at 3 AM. A quiet
  hour would hold a disk failure until morning, which is the failure that this design exists to prevent.
- **Through silent and Do Not Disturb:** only when Critical Alerts is switched on in the Pushover app on his iPhone.
  Whether Critical Alerts covers emergency priority is NOT CONFIRMED on Pushover's site (note of 18:27Z on
  `RIMMANDRAKE_CARD_PHONE_ALERT_ROUTE_AFTER_PUSHOVER_FACTS_CHECKED`). The first test page settles it (§9).
- **The text is a fixed template.** It is the class label, the reading, and an item id, and nothing else. Pushover's
  servers see the text. A reading may hold letters, digits, spaces and `_.,:;=<>%+()#-` only, up to 200 characters. So
  no path, address, URL, quote or newline fits. The `--why` is logged here and never sent.

## 6. Four outcomes, never confused

Each call prints one verdict line `PAGER <OUTCOME> ...`, after the outcome is known, and exits with its own code.

| outcome | exit | means | what it leaves |
|---|---|---|---|
| `SENT` | 0 | Pushover answered HTTP 200, status 1, and a receipt | state (the fault is open), a Conductor log line with the receipt, a log.jsonl line |
| `REFUSED` | 1 | the caller, class, cause, reading, goal or why is not allowed; nothing was sent | a log.jsonl line |
| `REPEAT` | 2 | the same fault paged inside its window: recorded, not rung | the updated record, a log.jsonl line |
| `COULD_NOT_SEND` | 3 | allowed, but the page did not leave: no credentials, network down, Pushover said no, or a 200 without a receipt | the failing streak in state; one Conductor log line when the streak starts; `pager.could_not_send` in the ops digest; a log.jsonl line for every attempt |
| `DRY_RUN` | 4 | `--dry-run`: says what it would send, or that it would be a repeat; no network, no state change | a log.jsonl line |

When Pushover cannot be reached, the outcome is `COULD_NOT_SEND` with the cause named ("Pushover unreachable:
URLError ..."). It is never `SENT` and never `REFUSED`. The ops digest shows it in the `pager` family
(`ops_watch.py`, collector `c_pager`, readings in `ops_watch_pager.py`): `pager.could_not_send` (faults whose page has
not left), `pager.refused_24h`, `pager.sent_7d`. A torn state file reads UNMEASURED there, never 0. Operations reads
`digest.md`. The first measured reading, 2026-11-20T03:18Z: could_not_send 0, refused_24h 1 (this helper's smoke test
in §2), sent_7d 0.

## 7. Credentials: what he must do once

`pager.py` reads two values at call time: the environment (`PUSHOVER_USER_KEY`, `PUSHOVER_APP_TOKEN`) first, else
**one file: `D:\ClaudeWork\rimmandrake\secrets\pushover.env`** (WSL: `/mnt/d/ClaudeWork/rimmandrake/secrets/pushover.env`,
under the agent storage root; `RM_PAGER_CREDENTIALS` overrides it). The file is outside every repo and is never
committed. A missing or misshapen value is named by its variable and the file path. The value itself is never printed,
logged or sent anywhere but Pushover.

His steps (Pushover's dashboard as we know it; the labels are not re-read today):

1. Log in at `https://pushover.net`. **Your User Key** is on the dashboard, at the top right.
2. On the same page, under **Your Applications**, click **Create an Application/API Token**
   (`https://pushover.net/apps/build`). Name: `RimMandrake`. Type: Application. Tick the terms box. Click **Create
   Application**. The next page shows its **API Token/Key**.
3. Save both values, as these two lines, to `D:\ClaudeWork\rimmandrake\secrets\pushover.env`:

        PUSHOVER_USER_KEY=<your user key>
        PUSHOVER_APP_TOKEN=<the RimMandrake app token>

4. On the iPhone, in the Pushover app's settings, switch on **Critical Alerts** (iOS asks once to allow it).

Then `pager.py check-credentials` proves both values with Pushover's `users/validate` call. That call rings nothing.
An alternative to steps 1 to 3: the Conductor can drive his logged-in browser (the `wsl-windows-plumbing` skill) to
create the application and write the file.

**The trial.** Pushover's site gives a 30-day free trial per platform, then 4.99 USD once (note of 18:27Z, 2026-11-19).
The trial's end date is UNMEASURED: it counts from the day he installed the app, which is not on Pushover's public
pages. He had it on 2026-11-19, so the trial ends on 2026-12-19 or earlier. **The purchase is his act (money). Nothing
here buys it.**

## 8. The triggers

`src/RimMandrake/Utils/pager_triggers.py` reads each trigger and pages through `pager.py send`. Its promises are in
`triggers_boundary.md`. Every Operations run calls `pager_triggers.py run` (`roles/operations.md` §Run hygiene); the
Conductor window may call it too. Every trigger is OFF until the Conductor window switches it on, one at a time:

    python3 src/RimMandrake/Utils/pager_triggers.py status
    python3 src/RimMandrake/Utils/pager_triggers.py on <name> --why "<why>"

Two triggers cannot ring as designed (measured 2026-11-24):

- **`steve_stuck`**: the fault monitor is PASSIVE (advisory), and a passive monitor never sets STUCK. The trigger reads
  COULD_NOT_LOOK.
- **`fleet_stop`**: while the fleet is stopped, no Operations run and no Conductor window runs, so nobody calls the
  pager. It needs a sender with no AI, which §2 refuses; that is the Conductor's choice. The log holds 4 stops from
  2026-11-11 to 2026-11-20; a switch ended the last one after 5 min.

The names are `whea_severe`, `steve_stuck`, `disk_root`, `disk_c`, `disk_d`, `switch_failed` and `fleet_stop`.
`GOAL_SHOCK` has no trigger. Last readings are from the ops watch pass of 2026-11-20T03:01Z unless stated.

| class | cause (the reading) | fires when | last reading | why this line |
|---|---|---|---|---|
| HARDWARE_FAILURE | `disk.whea_severe_24h` (WHEA-Logger 18 or 20, Critical or Error, on the D: NVMe) | > 0, MEASURED | 0; 0 of 793 readings since 2026-11-06 were above 0 | a fatal hardware error is data at risk now |
| HARDWARE_FAILURE | `steve.fault_stuck` (`D:\ClaudeWork\rimmandrake\testq\fault_state.json`, phase `STUCK`) | phase is STUCK | PASSIVE (2026-11-20T03:16Z) | SteveDesktop's SIMD fault is back after a reboot, or the reboot cap is spent: a reboot no longer clears it |
| HARDWARE_FAILURE | `disk.root_free_gb`, `disk.c_free_gb`, `disk.d_free_gb` | < 50, MEASURED | 564.8, 2228.0, 1625.3 | the worst measured day grew scratch by 207 GB (2026-10-26); 50 GB is about 6 h at that rate, so a write fails soon. The 210/200 GB lines stay Operations' ordinary alarm |
| ACCOUNT_SWITCH_FAILURE | `switching_plan:<marker>` (`D:\ClaudeWork\rimmandrake\switching_plan\markers\*.json`) | a marker in phase `failed`, under 6 h old, with no later `done` marker of any transition (the plan writes the time again at each retry) | 4 markers, all `done`, 0 `failed` | the plan tried to switch and could not: every window on the spent account stops |
| ACCOUNT_SWITCH_FAILURE | `switching_plan:fleet_stop` (`switching_plan\state.json`) | `stopped` is set (a `do: stop` log line stays after the stop ends) | none seen | the fleet is dark: no account is left to run on |
| GOAL_SHOCK | `goal:<short name>` | the Conductor's judgment (§3) | none | never a program |

Two readings are named and deliberately not triggers:

- **`disk.whea_corrected_24h`** (the D: NVMe corrected-error count): corrected errors lost no data. The existing alarm
  at more than 30 a day (`OPS_WHEA_DIAGNOSE_THIRTY_A_DAY`) reaches Operations. The highest reading in 793 is 19. No
  measured link from this count to a failure exists, so it does not page him. If the count is ever seen to come before
  a fatal error, the Conductor adds a line with that evidence.
- **`disk.whea_blind`** (the event log query failed): that is "could not look", not a failure. It stays Operations'.

## 9. The live send

The test page went out at 2026-11-23, 11:08:08 AM PST and was acknowledged at 11:08:20 (`pager.py ack`, receipt
`rxfuj2jk91jt2aurw15z6zzziop7s9`). The owner: *"I received it successfully, the phone made a custom noise and was loud.
It was a very brief sound though, so a real alert should use one of the louder noises I had indicated previously."* A
real page now sends the sound `echo`; a `TEST` page keeps the default. Whether the phone was on silent and Do Not
Disturb for that page is UNMEASURED.

## 10. When the item closes

The item is operational: it closes only when it is running (`CLAUDE.md` §An operational item is done only when it is
running). The close needs a real page that reached his phone (the `ack` line above), at least one trigger switched on,
and a promise for `rm-deadman`: `--live "reading=<pager dir>/state.json ..."` on the trigger's own reading. Until then
the item stays open with a `LEFT OPEN:` note.

## 11. Next version (not built)

From the 2026-11-08 design, for him to weigh later: a Windows-side sender for "WSL is dead" (`heartbeat.ps1`), an
outside watchdog for "the house is dark" (Healthchecks.io), a backup rung when Pushover is down (ntfy or a Twilio call),
and `--close` to cancel a ringing page when its fault clears (Pushover's receipt cancel).
