## spec
Asked by the owner, 2026-11-08 5:20 PM PST: "reminder: the ToDo's for our phone are NOT alarming our phone properly, we need some way for you to send real messages to our phone that alert, so please design that now in the background with options to consider as a subagent".

The design is written, and nothing is built. Read it here: `D:\ClaudeWork\rimmandrake\conductor\phone_alerts_design_20261108.md` (WSL: `/mnt/d/ClaudeWork/rimmandrake/conductor/phone_alerts_design_20261108.md`). GPT's second opinion, verbatim, is beside it: `phone_alerts_design_20261108.gpt.md`. A draft question card is at the end of the design (§9).

## Why the Todoist tasks never rang (measured 2026-11-08, read-only API reads)
- The account is on the free plan (`premium_status: not_premium`).
- A sync read of reminders returned **0**: no task ever had a reminder attached, and a due time alone never rings.
- `urgent_reminder_device: None`, so no phone is set to receive Todoist's urgent alarms.
- Todoist warns that a reminder made shortly before it fires may not reach an iPhone in time. Our tasks are created one minute before they fall due.
- Three senders post these tasks: `pulse/phone_push.py`, `deadman_check.py` and `windows/heartbeat.ps1`. As of 2026-11-08 20:05Z, 137 of their tasks were open in the Inbox the owner shares with Steve, and none was ever closed. One sweep on 2026-11-07 at 02:34Z posted about 50 tasks in 20 seconds.

## Recommendation
- **Primary: Pushover.** It costs $4.99 once. Its emergency priority (with Critical Alerts) sounds through silent and Do Not Disturb, repeats until he acknowledges it, and returns a receipt.
- **Backup rung: a Todoist urgent reminder.** It is free and also rings through silent and Do Not Disturb, on iOS 26 or later. If his iPhone is below iOS 26, the backup is ntfy.sh instead.
- **External watchdog: Healthchecks.io**, sending to Pushover, for the case where the whole house is down.
- **One CLI for every sender, `notify`:** dedup by key and level, burst coalescing, a budget that always keeps a slot for urgent, and fixed templates only.
- **Claude app push:** keep it as the in-session nudge only.
- **Our pick versus GPT's:** GPT agrees on Pushover first but prefers a Twilio voice call as the backup. That is card option 2.

## Done when
- The owner has answered the card.
- If he picks build: a build item is filed, carrying the T1–T6 test plan in design §6. Every test that sends to his phone runs only with him holding it.

## Watch out
- `phone_push.py`'s docstring says "no Remote Control push tool exists". That has been stale since the `PushNotification` tool shipped, but it is still the wrong route for the no-AI dead-man path.
- His iPhone's iOS version is UNMEASURED; the backup rung depends on it.
- Closing the 137 open Todoist tasks is a write to a shared account, so card question 2 asks first.
