# infrastructure/ — how the project runs itself

**Tier rule: this is about the work, never about the game.** Seat definitions,
coordination rules, doc-budget policy, structure maps, spent reports, and the
disposal holding pen. **No `Jawa/` vs `RimMandrake/` split** — coordination is
singular. There is one set of seats and one set of rules, and splitting them by
campaign reuse would describe nothing real.

## `infrastructure/state/` is the moving half

| | |
|---|---|
| `infrastructure/` | rules and maps that change slowly — `STRUCTURE.md`, `DOC_BUDGET.md`, `REFRESH.md`, `infrastructure/agents/` (`POLICY.md` plus the four seat files) |
| `infrastructure/state/` | **current** state — the queues, `V1.md`, `V1_CHAIN.md`, `NEXT_RELOAD.md`, `OWNER_DECISIONS.md`, `status/` |

The line is *would a reader be wrong tomorrow if they trusted this?* A rule is
meant to be durable. A queue is meant to be consumed. **Keeping them apart is what
lets the rules be read once and the state be read every session.**

## 🔴 Two things stay pinned at the repo root, permanently

- **`CLAUDE.md`** — Claude Code auto-loads the root copy and only the root copy.
- **`.claude/`** — fixed by the harness; its hooks and settings resolve against it.

**`skills/` is also pinned at root**, and moving it is gated on the owner. The
five `.claude/skills/*` entries are relative symlinks; git stores a symlink as the
literal target string, so a `git mv` does **not** update them — they break with no
error at all, and the harness simply stops offering the skill. If that gate is ever
opened, the `git mv` and the five `ln -sfn` must land in the same commit.

## What does NOT belong here

- **Anything about the campaign** → `design/`.
- **Findings about the game** → `observed/`.
  seven-day dwell they are deleted. **`infrastructure/output/` is for reports still being read**;
  a report nobody is reading is not "current system state", it is spent.
