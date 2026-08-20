# Global instructions

Applies to every project and every session.

## 🔴 SPEED IS THE DEFAULT — owner's ruling, 2026-08-13

**This outranks every habit below it.** Measured on the day it was issued:
deleting one file was taking 5–10 minutes, a day produced ~220 commits and moved
the actual goal by one item, and diffs scrolling past the screen cost more
attention than the work was worth.

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

⚖️ **The honest trade:** skipping verification buys speed and costs accuracy. On
the day this was written, three things documented as *settled* turned out wrong.
So: **act without checking; but when the question is "is this TRUE", check.**
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

Standing rule from the owner, 2026-08-13, issued after an unplanned reboot
destroyed a session's scratchpad work and exposed a 13-hour, 224-commit unpushed
backlog that existed on a single disk.

## Subagents and background agents are authorized — use them, do not ask

**Standing request from the owner, 2026-08-13, applying to every project and every
session.** Treat this as the owner having *already asked* for subagents wherever a
tool description or session instruction says "only if the user requests it" — the
request is on file, here.

- **Spawn them freely and in parallel** for searches, censuses, file sweeps, audits
  and any read-only investigation. Do not propose it and wait; do it and report.
- **Fan-out is usually the correct approach, not an indulgence** — especially on
  slow mounts or where a single call would time out.
- Do not ask permission, and do not narrate the decision to use them.

⚠️ **A CLAUDE.md authorization does not override a session-level instruction.** On
2026-08-13 the project CLAUDE.md had granted this since 2026-08-11 and a session
prompt still said "do not use subagents unless the user requested it" — the file
lost, and the work was done single-threaded. **If those two ever conflict again,
say so out loud rather than silently obeying the narrower one**, and note that
this section records the owner's request, which is what such instructions are
conditioned on.

## 🔴 Do not message other agents — owner's ruling, 2026-08-19

**This is the counterweight to the section above.** Spawning subagents is authorized
and encouraged; **messaging peer sessions is not.** They are opposites: a subagent
works *for* you in its own context, while `SendMessage` to a peer **lands in someone
else's context mid-turn and bills their tokens exactly like a prompt the owner
typed.**

**Send one only when BOTH hold:** (1) the owner asked for it, or it is a real
emergency — the other session is about to destroy work, is acting on a reversed
ruling, or is about to test something that is not live; and (2) it fits in **one or
two sentences**.

⛔ **Never** to hand over a spec, a contract, a finding, a status, a summary,
context, or "here is what I decided". Write it where they already read — a queue
file, the doc it contradicts, the commit.

⚠️ **There is no broadcast.** `SendMessage` names exactly one target; the `@`
typeahead is an affordance in the **owner's own prompt** for naming one session, not
a fan-out operator, and there is no `@all`.

🔑 **And a peer message cannot change configuration anyway** — Claude Code instructs
a receiving session never to alter permission settings, `CLAUDE.md` or other config
because another session asked. Only the owner can.

## Always give full paths — plain, native, absolute

**Never** a bare filename, and never a repo-relative fragment. `scatter.py` and
`Utils/rimbench/` turn a one-second action into a hunt. **That requirement is the
point and it has not changed.** What changed is the form.

**Write an ordinary absolute path in the platform's native style**, wrapped in
backticks so backslashes survive markdown rendering:

```
`D:\Luke\dev\Rimworld\Utils\rimbench\scatter.py`
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log`
```

**No `file:///` prefix and no `%20`** — spaces are written as spaces. The URL form
existed only to be clickable, and it is not: the owner tested terminal hyperlinks
(OSC 8) and markdown links, both inert here, and a double-click only copies. So
it bought nothing and cost readability and line width.

**Opening a file is a command, not a click.** `./Utils/show.sh <path>` launches
Windows File Explorer with the file selected (a folder opens directly). It takes
repo-relative, `/mnt/...` and `C:\...` forms alike.

Applies to **files and folders alike**, in prose, tables, lists and summaries.
If a path is worth mentioning, it is worth writing in full.

Standing rule from the owner, 2026-08-12; form revised 2026-08-13.
