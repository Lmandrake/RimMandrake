# CLAUDE.md — standing operating rules for this project

_Auto-loaded by Claude Code from the project root. Keep it short; it is read every
session. Detail belongs in the docs it points to._

Project: a heavily modded RimWorld 1.6 campaign — Jawa scavenger clan aboard a
salvaged gravship on a desert world. ~561 active mods.

**Read at the start of any RimWorld task:**
`mods/benign_log_errors.md` §0 (triage method) and
`skills/rimworld-modding/references/traps.md` (earned lessons, short by design).

---

## Standing authorizations — do not ask again

**Background agents and subagents are fully authorized.** Spawn them freely and in
parallel for searches, censuses, file sweeps and any read-only investigation. Do
not ask permission, do not propose it and wait — just do it and report the result.
The mount is slow (~210 files/sec) and `device_bash` calls time out at 45 seconds,
so fanning work out is usually the *correct* approach, not an indulgence.

Granted 2026-08-11 by the project owner, standing until revoked here.

## How to work here

**The game restart is the scarce resource — a cold load is ~23–30 minutes.** Never
say "restart and see". Arrive at a restart already confident, batch everything that
can ride along, and write down in advance the exact log strings that will decide
each item. Then harvest the *whole* log, not just the thing you changed.

**Verify offline first — but know which files are authoritative when.** Defs,
`About.xml`, `ModsConfig.xml`, the Workshop tree and the live def dump are all
ordinary files, and reading them beats trusting a manager's UI.

⚠️ **While RimWorld is running, mod-list state on disk is NOT authoritative.**
The running game holds its mod list in memory and rewrites `ModsConfig.xml` on
exit, and Steam does not remove an unsubscribed mod's folder while the game has
it open. So during a live session:

- a mod still listed in `ModsConfig.xml` may already be unsubscribed
- a folder still present under `294100/` proves nothing
- a manager's changes may be overwritten when the game closes

**Never tell the user "your removal didn't land" while the game is up.** Ask
whether the game is running, or check `Player.log`'s mtime against
`ModsConfig.xml`'s, and say what each timestamp implies instead of asserting a
state. Mod-list claims are only safe after a clean exit.

**Batch by ambiguity, not by count.** Config changes (load order, settings,
un/subscribes) carry no attribution risk and always ride along. A validated XML
patch with named log strings is safe to include. New C# assemblies and
broad-patching mods stay solo.

**Writing a file is not deploying it.** The game reads
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\<ModName>`, never this
repo. Run `python Utils/deploy_custom_mods.py` (plan-only) then `--apply`. Treat
"the file is written" and "the game can see it" as two separate claims. A whole
test cycle was lost to this on 2026-08-11.

**Commit explicit paths only. Never `git add -A`, `git add .`, or `git commit -a`.**
Four threads share ONE working tree, so at any moment most of what `git status`
shows belongs to someone else, mid-edit. A blanket add sweeps their unfinished
work — and their *staged* work — into your commit, under your message.

```bash
git add path/one.md path/two.xml     # name every file
git diff --cached --stat             # read it before committing
git commit -F - <<'EOF'              # ...
```

If `--stat` lists a file you did not touch, unstage it (`git restore --staged
<path>`) rather than explaining it away in the message. Likewise `git status` a
doc before editing it: if it is already modified, someone is in it — pick another
file or coordinate.

This is not hypothetical. On 2026-08-11 commit `76d7f64` swept three staged
`git mv` renames out of another thread's in-flight audit and committed them under
an unrelated message about load order. Nothing was lost that time. The failure
mode that costs you is a half-written patch committed as though it were finished.

**Validate every patch before it goes near the Mods folder:**
`python skills/rimworld-modding/scripts/validate_patch.py <file> --live`.
Note it reads `Patches/` only — never `Defs/`.

**Run `python Utils/refresh.py` after any mod-list change.** It reports what is
stale and whether a game load is required. See `REFRESH.md`.

**Never guess a defName, a field, or a namespace.** Read the actual def, the actual
`About.xml`, or `strings` the actual assembly. Quote the file path and a dated
snippet in a comment at the top of any patch.

**Two error phrasings, two different systems:**
`Could not **resolve** cross-reference` = def loader, a live mod-set problem.
`Could not **load** reference to` = Scribe/deserializer, a *saved file* holds a
dead name. The second is where "errors from mods I deleted months ago" come from.

## Communication

**Always connect an observation to a recommended action.** "X is true" is half an
answer; the owner wants "X is true, so do Y". State the recommendation even when
it is "leave it alone".

Be concise and direct when the owner is mid-task. Own mistakes plainly and say
what changed as a result.

## Keep the skill learning

After any RimWorld task, ask what surprised you. If something did, append it to
`skills/rimworld-modding/references/traps.md` — symptom, cause, fix, and above all
**"generalises to"**. When an entry would change default behaviour, promote it into
`SKILL.md` and delete it from the log. Every entry there cost a real debug cycle.

## Environment notes

- Four+ threads work in this repo, sharing one working tree and one game install.
  Both shared-state hazards follow from that: commit explicit paths only (above),
  and remember `deploy_custom_mods.py --apply` overwrites the game copy with
  whatever is in the repo *right now*, including another thread's half-finished
  work. Always read the plan first; `-` lines mean someone hand-edited the
  deployed copy, so `--pull` before overwriting.
- In cloud (Cowork) sessions the G: project is **not** mounted for `device_bash`
  and files there cannot be deleted or committed by the assistant — only written.
  Deletions and `git` operations must be done locally.
