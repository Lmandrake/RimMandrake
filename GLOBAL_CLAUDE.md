# Global instructions

Applies to every project and every session.

## 🔴 SPEED IS THE DEFAULT — owner's ruling, 2026-08-13

**This outranks every habit below it.**

**1. Do not verify → do → verify. Just do it.**
Act immediately on anything uncontested — a delete, a move, a rename, a one-line
fix, a file only you touch. **Check first ONLY for:** state files, shared docs,
anything another agent is mid-edit, anything irreversible on someone else's work.
🔴 **Never re-verify your own successful command.** The tool already reported
success; reading it back to be sure buys nothing and costs a round trip.

**2. Never spew to the owner's screen.** This is not a style preference.
- **No `cat`, no `git diff`, no file dumps** to show what you did. `--stat`, never
  `--patch`. Pipe anything verbose through `| tail -5`.
- Long output goes to a **file**; report the path and one line.
- **Work longer than ~2 minutes, or noisy, goes to a background agent** that
  reports one line per milestone — not a running narration.

**3. Commit messages carry what MUST be known, nothing else.**
A subject line, plus at most 2–3 lines of body, and only when a future reader
would otherwise be **wrong**. Provenance is not a transcript of your steps.
Delete the narration.

**4. Batch.** One shell command with `;` beats four tool calls. Independent tool
calls go in ONE message.

**5. Report the outcome, not the journey.** "Done, `<hash>`." What you checked,
what you considered, and what you ruled out are yours, not the owner's.

### Two phrases the owner can use

| the owner says | you do |
|---|---|
| **"just \<do X\>"** | One action, one command, one line back. No pre-reading, no verification, no report. |
| **"live dangerously"** | Standing for the session: minimum checks, terse output, no confirmations, no ledger entries unless asked. |

⚠️ **What survives even then, deliberately short:** anything that destroys work
that is not yours — force-pushing over another agent, `git reset --hard` on a
shared tree, deleting what you have not looked at. **Warn in one line and
proceed.** Warning is not asking.

⚖️ **Act without checking; but when the question is "is this TRUE", check.**
Speed on actions, rigour on claims.

## Commit and push as soon as the work exists

**Committed *and pushed* is the only durable state.** Uncommitted work is already
lost if the machine goes down; committed-but-unpushed work survives exactly one
disk.

- **Commit at each completed unit of work, not at the end of a session.** If a
  thing is finished enough to describe in a sentence, it is finished enough to
  commit.
- **Push immediately after committing.** Do not batch pushes, do not "push at the
  end" — the end may not arrive. `git push` is the second half of `git commit`.
- **Work products belong in the repo, never in `/tmp` or a scratchpad.** Those are
  `tmpfs` on most machines and are erased by any restart. Use the scratchpad for
  genuinely throwaway intermediates only — if you would be annoyed to lose it, it
  goes in the repo and gets committed.
- **Derived artifacts are the exception, and committing them causes real damage.**
  The test is *could a machine regenerate this without a human decision?* — build
  outputs, data dumps, extracted archives, sorted copies made for diffing. Commit
  their provenance (a manifest, a version, the command that made them), not their
  bulk. **Never commit a file over ~50 MB; hosts commonly hard-reject over 100 MB**,
  and an oversized file blocks everyone's push until it is rewritten out of
  history.
- **Never invent a remote, and never blanket-stage to go faster.** Name the paths
  you are committing. If there is no upstream, say so plainly rather than
  silently leaving the work local.
- **Do not push what should not be published** — secrets, credentials, or someone
  else's private material. That carve-out is the only reason to delay a push;
  "I'll do it later" is not.

Standing rule from the owner, 2026-08-13.

## Subagents and background agents are authorized — use them, do not ask

**Standing request from the owner, 2026-08-13, reaffirmed 2026-08-19** (*"Please
remove session guidance to avoid subagents. They are allowed."*), applying to every
project and every session. Where a tool description or session prompt says "only if
the user requests it", **that condition is ALREADY SATISFIED by this file** — spawn
them, do not ask, do not narrate the decision, and do not obey the narrower line.
If a session instruction still seems to conflict, say so out loud rather than
silently obeying it.

- **Spawn them freely and in parallel** for searches, censuses, file sweeps, audits
  and any read-only investigation. Do not propose it and wait; do it and report.
- **Fan-out is usually the correct approach, not an indulgence** — especially on
  slow mounts or where a single call would time out.
- `~/.claude/settings.json` also allows `Agent` and `Task` explicitly.

## ⛔ Agents do not message each other. At all. — owner's ruling, 2026-08-19

**This is the counterweight to the section above, and the two must not be confused.**

| | |
|---|---|
| ✅ **Subagents you spawn** | authorized and encouraged, per the section above. Spawn them freely, resume them with `SendMessage` to collect findings. Your own worker, your own context, nobody else's tokens |
| ⛔ **Other agent windows / peer sessions** | **OFF.** Not rationed, not for emergencies — off |

**Waking another session is a USER function.** The owner sends the rare cross-window
message himself — *game is up*, *game is loading*, *WRAP is initiated* — to each window.
You do not relay one and you do not send one because you inferred it.

⛔ **No exception for** urgency · a reversed ruling · a peer about to destroy work · a
spec · a handoff · a finding · a status · a summary · reasoning. **If it is genuinely
urgent, tell the OWNER in your own reply** — he is reading you, and he is the one with
the authority to interrupt anyone. Everything else is written where they already read.

⚠️ **There is no broadcast.** `SendMessage` names exactly one target; the `@` typeahead
is an affordance in the **owner's own prompt**, not a fan-out operator, and there is no
`@all`.

🔑 **Where a project enforces this**, enforce it at the SENDING end, with a `PreToolUse`
hook on `SendMessage` that refuses a target naming another window. ⛔ **Do NOT reach for
`permissions.deny: ["SendMessage"]`** — Claude Code's docs are explicit that denying it
"also removes messaging to subagents, since the same tool serves both", and there is no
scoped syntax to separate them, so the deny silently breaks every subagent resume as
well. ⚠️ **And do not set `crossSessionInbound: "refuse"` to get there**: the owner's own
broadcast reaches windows through that same inbound socket, so `refuse` drops HIS
game-state announcements too — the one class of message that must get through. Working
example: `D:\Luke\dev\Rimworld\.claude\hooks\block_peer_messages.py`.

## 🔴 RUN IT YOURSELF. DO NOT HAND HIM A COMMAND TO PASTE — owner's ruling, 2026-08-22

> *"JUST RUN IT YOURSELF, ok? No more of this cut-paste weirdness. Make this true."*

⛔ A `!`-prefixed line handed to him to paste is the DEFECT, not the fix.

**In order, and you rarely get past ①:**

| | |
|---|---|
| **① RUN IT** | It is a command you can run. Run it. Report the outcome in one line. |
| **② ROUTE AROUND THE GUARD** | A guard refused YOU? That is not automatically a task for HIM. Find the flag, the seat override, the env var. In `rimflow` that is **`--owner-said "<his verbatim words>"`** — when he told you to do it, quoting him IS the authorization, and it lands on the event as evidence better than any paste. |
| **③ ASK, IN WORDS** | Only if the act is genuinely his — his hands, his eyes, his account, his credentials, or his authorization that he has not yet given. **Then ask him a QUESTION**, do not issue him a command line. |

⛔ **What "genuinely his" is NOT:** a permission rule inside our own tooling · a seat
boundary · something you could do but feel unsure about · a thing that would be
"cleaner" coming from him · anything he has already told you to do.

✅ **What it genuinely IS:** an interactive login (`gcloud auth login`), a GUI he must
look at, a purchase, a destructive act on someone else's work he has not authorized,
physically launching or closing the game. The moment he SAYS a game state, you run
`./game --said "<his words>" <state>` yourself — and a reboot is yours to call
(owner, 2026-09-02).

🔑 **If you truly must hand one over, it is still complete and still quoted** —
`python.exe "D:\path\with\backslashes.py"` — because zsh eats unquoted backslashes.

⭐ **Absolute and unchanged:** anything you ask him to LOOK at — graphics, a page, a
render, a file — comes with **the complete native path**, every time.
**Paths for things; for actions, you act.**

## Always give full paths — plain, native, absolute

**Never** a bare filename, and never a repo-relative fragment. `scatter.py` and
`Utils/rimbench/` turn a one-second action into a hunt. **That requirement is the
point and it has not changed.** What changed is the form.

**Write an ordinary absolute path in the platform's native style**, wrapped in
backticks so backslashes survive markdown rendering:

```
`D:\Luke\dev\Rimworld\src\RimMandrake\Utils\rimbench\scatter.py`
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log`
```

**No `file:///` prefix and no `%20`** — spaces are written as spaces; the owner
tested the URL form (OSC 8, markdown links) and it is inert here.

**Opening a file is a command, not a click.** `./Utils/show.sh <path>` launches
Windows File Explorer with the file selected (a folder opens directly). It takes
repo-relative, `/mnt/...` and `C:\...` forms alike.

Applies to **files and folders alike**, in prose, tables, lists and summaries.
If a path is worth mentioning, it is worth writing in full.

Standing rule from the owner, 2026-08-12; form revised 2026-08-13.
