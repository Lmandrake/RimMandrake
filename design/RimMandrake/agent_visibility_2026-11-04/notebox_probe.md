# Note-delivery probe and the note box (report steps 3-4), 2026-11-05

Item `STATION_NOTEBOX_BUILD_WHISPER_AT_NEXT_TURN`. Owner, 2026-11-05: *"1 yes, 2 send a note is fine for now. 3 no 4 yes."*
Take-over (step 5, option F) is not built.

## Step 3: delivery ways, tested in a throwaway dir (`D:\ClaudeWork\rimmandrake\scratch\notebox_probe`), `claude -p --model sonnet`

| way | test | result |
|---|---|---|
| A. PostToolUse hook, `additionalContext` | note file written 8 s into a `sleep 15` Bash call | delivered once, attached to that tool's result; the next call saw nothing. Launch shape unchanged |
| B. `--input-format stream-json`, second user message on stdin mid-run | written during the same `sleep 15` | delivered at the same boundary (attached to the tool result, not a new turn). Needs the supervisor to hold a stdin pipe for the unit's whole life: a different launch shape |
| C. Stop hook, `decision: block` | note pending when a one-turn run tried to end | the stop was blocked once and the run continued with the note (2 turns; the final result reflects it); the `stop_hook_active` Stop then ended normally |
| A+C with the real hook, end to end | `notebox.py send` 6 s into a subagent's `sleep 15`, throwaway `RELENTLESS_ROOT` and clone marker | the subagent's Bash call (event carries `agent_id`) delivered nothing; the main thread's Agent result carried the note; record shows `delivered ... at PostToolUse` |

Not probed: `claude --bg` / `attach` (E2) and tmux (B*). Both are interactive hosting and belong to take-over, which is not wanted now.

**Winner: A + C.** They need no change to how workers launch (systemd unit, `-p`, json result, kill and time walls all stay). They deliver at the next tool boundary, and at the end of the run when no tool call is left. B is just as timely but would move stdin ownership into the supervisor for the unit's whole life.

Honest latency: a note waits for the current tool call to return. A long Bash call or a subagent delays it by that call's length; in the end-to-end test the delay was 26 s, the subagent's run time.

## Step 4: the note box as built

- `src/RimMandrake/rimflow/notebox.py`: `send ITEM "text" [--gen G] [--by NAME]` · `show ITEM [--json]` · `deliver --event PostToolUse|Stop` (the hook body).
- `.claude/hooks/notebox_deliver.py`, registered for PostToolUse (all tools) and Stop in `.claude/settings.json`. Outside a Relentless worker (no `RELENTLESS_GEN`, or no `.git/relentless.json`) it exits at once.
- **Binding:** a note is bound at send time to the item and the gen running then. Send refuses an item that is not running unless `--gen` is passed. Only a worker session receives it: the marker in its project clone (`CLAUDE_PROJECT_DIR/.git/relentless.json`) must name that item, and its `RELENTLESS_GEN`, set only at a worker's launch, must be that gen. Any other session in the clone (a helper, the owner's own `claude`) has no `RELENTLESS_GEN` and receives nothing. A note never follows a station to other work or to a later gen. One left pending when its run ends stays pending in `show`, and the owner re-sends it on purpose.
- **At most once:** delivery runs under a per-item flock, which the hook waits on for at most 2 s, and appends a `delivered` record before the hook prints. A hook killed in between loses that one delivery and never doubles it. The text is still in the record and in learned.md.
- **Record:** `<relentless root>/store/items/<ITEM>/notes.jsonl` (sent and delivered rows), a `note_sent` / `note_delivered` line in `store/journal.jsonl`, and the delivered note appended to the item's `learned.md`, so the next worker's brief carries it.
- **Known edge:** a child `claude -p` started by a worker inside its own clone would inherit `RELENTLESS_GEN` and could take the note. Workers start no such children today; Agent-tool subagents are excluded by `agent_id`.
- **Judges and checkers** receive nothing: relentless.py sets `RELENTLESS_GEN` only on a worker's launch (the build/pilot launch), never on a check, consult or help run. A note meant to change a judgment goes to the item, not the judge.
- Proof: `python3 src/RimMandrake/Utils/selftest_notebox.py` runs the registered command strings through `sh -c`. A mutation test showed it catches a removed gen check and a removed subagent guard.

Owed to step 2 (the Pipeline window): a note field per station tab that calls `notebox.py send` with the item that station is running.
