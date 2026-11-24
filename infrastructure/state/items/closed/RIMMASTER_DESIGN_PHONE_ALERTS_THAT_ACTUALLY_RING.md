## spec
Asked by the owner, 2026-11-08 5:20 PM PST: "reminder: the ToDo's for our phone are NOT alarming our phone properly, we need some way for you to send real messages to our phone that alert, so please design that now in the background with options to consider as a subagent".

The design is written, and nothing is built. Read it here: `D:\ClaudeWork\rimmandrake\conductor\phone_alerts_design_20261108.md` (WSL: `/mnt/d/ClaudeWork/rimmandrake/conductor/phone_alerts_design_20261108.md`). GPT's second opinion, verbatim, is beside it: `phone_alerts_design_20261108.gpt.md`. A draft question card is at the end of the design (§9).

## Why the Todoist tasks never rang (measured 2026-11-08, read-only API reads)
- The account is on the free plan (`premium_status: not_premium`).
- A sync read of reminders returned **0**: no task ever had a reminder attached, and a due time alone never rings.
- `urgent_reminder_device: None`, so no phone is set to receive Todoist's urgent alarms.
- Todoist warns that a reminder made shortly before it fires may not reach an iPhone in time. Our tasks are created one minute before they fall due.
- Three senders post these tasks: `ops_core/phone_push.py` (`pulse/phone_push.py` until 2026-11-18), `deadman_check.py` and `windows/heartbeat.ps1`. As of 2026-11-08 20:05Z, 137 of their tasks were open in the Inbox the owner shares with Steve, and none was ever closed. One sweep on 2026-11-07 at 02:34Z posted about 50 tasks in 20 seconds.

## Todoist retired, 2026-11-19 (owner)
- His words, typed into a card: "So Todoist is officially retired as any kind of alert: it just doesn't work in a timely manner. It's really only to maintain to do lists, as it says." Full text: `design/RimMandrake/standing_rulings.md` §Todoist is for to-do lists only.
- **The Todoist backup rung is struck from every option** (A, the backup in the recommendation, and card options 1 and 3). The alert route itself is still his open choice; nothing (Pushover or anything else) is built.
- The senders' Todoist posts are off (`RM_TODOIST_ALARM_POSTS`, default off; heartbeat `-TodoistAlarmPosts`), and the 173 alarm tasks open in the shared Inbox were completed (RIMMANDRAKE_RETIRE_TODOIST_AS_ALERT_ROUTE_IT_NEVER_RANG). Until a route is built, no alarm reaches the phone.

## Recommendation
- **Primary: Pushover.** It costs $4.99 once. Its emergency priority (with Critical Alerts) sounds through silent and Do Not Disturb, repeats until he acknowledges it, and returns a receipt.
- **Backup rung:** struck as Todoist (retired 2026-11-19, above); ntfy.sh or GPT's Twilio call are the remaining candidates.
- **External watchdog: Healthchecks.io**, sending to Pushover, for the case where the whole house is down.
- **One CLI for every sender, `notify`:** dedup by key and level, burst coalescing, a budget that always keeps a slot for urgent, and fixed templates only.
- **Claude app push:** keep it as the in-session nudge only.
- **Our pick versus GPT's:** GPT agrees on Pushover first but prefers a Twilio voice call as the backup. That is card option 2.

## Done when
- The owner has answered the card.
- If he picks build: a build item is filed, carrying the T1–T6 test plan in design §6. Every test that sends to his phone runs only with him holding it.

## Watch out
- `PushNotification` exists but needs an AI in the loop, so it is the wrong route for the no-AI dead-man path (`phone_push.py`'s stale docstring was corrected 2026-11-19).
- His iPhone's iOS version is UNMEASURED; with Todoist struck it only matters if ntfy is weighed.
