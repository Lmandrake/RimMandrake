# STRUCTURE.md — where things live, and why

_The map of the repo. Read it once to know which tier a file belongs to; then read
that tier's own `README.md`, which is authoritative about what belongs inside it._

**This file names tiers and homes. It does not restate a tier's rules, and it
carries no counts** — a count copied out of `ls` drifts within hours and the copy
never announces that it is wrong. Name the thing, point at its authority.

---

## The seven tiers

Every path in the repo is in exactly one of these. The question each answers is
different, and that is the whole design: **intent, source, installed, measured,
theirs, studied, ourselves.**

| Tier | Answers | Its rule lives in |
|---|---|---|
| `design/` | What do we *intend* to exist? | `design/README.md` |
| `src/` | What did we *write* for a machine to consume? | `src/README.md` |
| `deployed/` | What is the game actually *configured* with? | `deployed/README.md` |
| `observed/` | What did a *running game* actually do? | `observed/README.md` |
| `vendor/` | What did *someone else* write that we run? | `vendor/README.md` |
| `research/` | What did *someone else* write that we studied? | `research/README.md` |
| `infrastructure/` | How does the *project* run itself? | `infrastructure/README.md` |

The four boundaries that get crossed by mistake:

- **`design/` vs `observed/`** — reasoning stays in design; a *conclusion* that only
  a running game could settle is an observation.
- **`src/` vs `deployed/`** — we wrote it vs it is installed. They drift, and the
  drift is the point of tracking both.
- **`vendor/` vs `research/`** — installed vs merely studied. A mod we run is
  vendor; a mod we read about and rejected is research.
- **`observed/` vs a script's own output** — map-synth PNGs and art-bench
  intermediates are *our* tool's artifacts, not a game's behaviour. They stay
  gitignored beside their generator in `src/`.

---

## The `Jawa/` vs `RimMandrake/` split

`design/`, `src/` and `research/` carry it. `deployed/`, `observed/` and
`infrastructure/` **do not**, deliberately — an installed config, a measurement and
a seat definition each belong to something other than our reuse category.

**The owner's promotion test:**

> *"Am I likely to want this in a totally unrelated playthrough, or will I have to
> fundamentally remake it — not just reconfigure it?"*

**Reconfigure → `RimMandrake/`. Remake → `Jawa/`.**

⚠️ **When unsure, `Jawa/`.** Promoting later is a `git mv`; discovering that a
"generic" doc silently assumed Star Wars is a debugging session.

---

## Pinned at the root — do not move these

| Path | Why it cannot move |
|---|---|
| `CLAUDE.md` | Claude Code auto-loads the **root** copy and only the root copy. |
| `GLOBAL_CLAUDE.md` | The tracked mirror of `~/.claude/CLAUDE.md`, kept beside it for the same reason. |
| `.claude/` | Fixed by the harness. Its hooks and `settings.json` resolve against this path. |
| `skills/` | Five entries in `.claude/skills/` are **relative symlinks** into it. |

🔴 **The `skills/` pin is the dangerous one.** Git stores a symlink as its literal
target string, so a `git mv` does **not** update it — the links break with **no
error at all** and the harness silently stops offering those skills. Moving
`skills/` is gated on the owner; if that gate opens, the `git mv` and the five
`ln -sfn` land in the same commit. Full statement: `infrastructure/README.md`.

---

## Where does X live

| Looking for | Go to |
|---|---|
| Standing operating rules | `CLAUDE.md` (root) |
| Which seats exist and what each owns | `infrastructure/agents/<SEAT>.md` |
| Shared seat rules, messaging residue | `infrastructure/agents_def.md` |
| Current work state — TODO, next reload, v1 scope, owner decisions, per-seat state and queues | `infrastructure/state/` (and `infrastructure/state/queue/<SEAT>.md`) |
| What to re-run after the mod list changes | `infrastructure/REFRESH.md` |
| Doc-count policy, and how a written instruction rots | `infrastructure/DOC_BUDGET.md` |
| A report still being read | `infrastructure/output/` |
| A report whose question is answered | `infrastructure/disposing/` — 7-day dwell, then deleted. Treat as absent; exclude from greps. |
| Superseded narrative kept only for *why* | `infrastructure/archive/` |
| Mod adoption, bans, cherry-pick lists, armoury | `design/Jawa/mods/` |
| The world, the ship, the xenotype, factions | `design/Jawa/worldbuilding/` |
| Art briefs and the art method | `design/Jawa/art/` |
| A *method* reusable in another playthrough | `design/RimMandrake/` |
| Our authored mods for this campaign | `src/Jawa/` |
| Our generic mods — art fixes, `RimDefDump`, `WreckedMachines` | `src/RimMandrake/` |
| Python tooling, deploy script, seat scripts | `src/RimMandrake/Utils/` |
| The RimBridge companion assembly | `src/RimMandrake/bridgetools/` |
| Copied game config — `ModsConfig.xml`, RimSort rules, per-mod settings | `deployed/config/` |
| A measurement from a live game | `observed/` — stamped per contact |
| Third-party mod source, salvaged assemblies | `vendor/mod_sources/`, `vendor/salvage/` |
| How to *operate* somebody else's mod; which of its log errors are benign | `vendor/wisdom/` |
| Study material we did not author | `research/Jawa/`, `research/RimMandrake/` |
| A skill | `skills/<name>/` — the directory is the source |

Skills are named in the listing above only as a location. **Which skill to load
when is `CLAUDE.md`'s job**, not this file's.

---

## Three cross-tier rules you will hit today

**Writing a file in `src/` is not deploying it.** The game reads
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\<ModName>` and nothing
syncs it from this tree. Plan first with
`src/RimMandrake/Utils/deploy_custom_mods.py`, then `--apply --mod <Name>`; a bare
`--apply` pushes every mod in the tree including another seat's half-finished work.
`src/DEPLOY_HOLD.txt` and the full procedure: `skills/rimworld-deploy/SKILL.md`.

**Track the manifest, never the payload.** Saves, def dumps, `Player.log`,
screenshots, downloaded `.rws` maps, `vendor/mod_sources/` — all gitignored, all
still on disk. **Git never forgets, so the rule is about refusing the *next*
payload**, not cleaning up the last. Never delete one "for size"; it buys nothing.
Ignore rules and their reasons: `.gitignore`.

**One working tree, several seats.** `git status` a shared doc before editing it.
Commit **explicit paths only** — never `git add -A`, `git add .`, or `git commit -a`
— and read `git diff --cached --stat` before committing. Enforced by
`.claude/hooks/block_blanket_git_stage.py`.

---

## Keeping this file true

**A manifest is the one document that cannot be maintained by reading documents.**
It has to be diffed against `ls`, which takes about a minute:

```bash
ls /mnt/d/Luke/dev/Rimworld                       # root: 7 tiers + skills + 2 md
ls /mnt/d/Luke/dev/Rimworld/*/README.md           # every tier states its own rule
```

**If a new top-level directory or a new root file appears, it belongs here in the
same commit.** Everything else in the repo announces itself; a missing entry on a
map does not. A tier's *internals* are its own README's problem — do not mirror
them here, or the copy will drift and this file will start lying about the tree it
exists to describe.
