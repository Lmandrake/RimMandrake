# skills/ — procedure you load, not prose you read

**Tier rule: a skill is a METHOD YOU FOLLOW.** It answers *how do I do this class
of thing without paying for the mistakes again* — a sequence, a decision table, a
validator to run. If it does not change what you *do* next, it is not a skill.

The directory **is** the skill. `skills/<name>/` is the source of truth; the
`<name>.skill` zip beside it is a build output, and an installed copy is a
read-only cache. Editing an installed copy changes nothing durable.

## Skill versus trap — the line that decides where text goes

| | |
|---|---|
| **skill** | a method you follow: *"before testing any patch, deploy it, then validate with both `--live` and `--defs`"* |
| **trap** | a specific failure you avoid: *"`PatchOperationRemove` deletes every match, not the first"* |

Traps go to `skills/rimworld-modding/references/traps.md` — the **index**, which
routes to five topic files and carries the five-part admission test (specific,
non-obvious, actionable, domain-bound, still true). Most candidate lessons fail
it. **A trap that would change default behaviour gets promoted into a `SKILL.md`
body and deleted from the log**; the log is a staging area, not an archive.

## Anatomy

```
skills/<name>/
  SKILL.md        required. YAML frontmatter + body.
  references/     topic files the SKILL.md indexes and links to.
  scripts/        runnable tools the SKILL.md tells you to invoke.
```

**Frontmatter is exactly two fields in every skill here: `name` and
`description`.** `name` must equal the folder name — lowercase letters, digits
and hyphens, ≤64 chars, and must not contain `claude` or `anthropic`.
`description` is not a summary; it is the **trigger**, written as *what it does*
plus *"Use when/whenever …"*, because that sentence is all the agent sees when
deciding whether to load it.

**`SKILL.md` is the index; `references/` is the detail.** When the body nears the
cap, split a topic out — `rimworld-modding` (11 files) and `generating-images`
(7) both did. A link to a file that does not exist is a validation failure: the
agent goes looking and finds nothing.

## The enforced constraints — `src/RimMandrake/Utils/package_skill.py`

| Constraint | Limit |
|---|---|
| `SKILL.md` body | **≤ 500 lines** (frontmatter excluded) |
| `description` | **≤ 1024 characters** |
| `name` | ≤ 64 chars, `[a-z0-9-]+`, equals folder name, no reserved word |
| relative links in `SKILL.md` | must resolve on disk |

🔴 **A failing skill leaves its OWN archive stale — the others are still written.**
`--all` packages every skill that validates and exits 1 naming the ones that did
not. **That is how five archives drifted from their sources unnoticed**: the run
exited 1, two skills breached the 500-line cap, and their stale zips sat beside
twelve fresh ones looking identical.

*(The message used to read "Nothing was installed", which was false and sent people
hunting for a fleet-wide failure that never happened. Corrected 2026-08-14; it now
names the failures and says the rest were written.)*
**Read the exit code and the named list, not the directory listing.**

Validate without writing: `python3 src/RimMandrake/Utils/package_skill.py --all --check`.

## Delivery — writing the folder is not shipping the skill

- **`skills/*.skill` is gitignored** (`.gitignore:149`). Zero archives are
  tracked, and that is correct: they are derived, they are bulk, and git never
  forgets.
- **Rebuild at hand-off:** `python3 src/RimMandrake/Utils/package_skill.py --all`.
- **Committing a stale zip is the worst of the three options** — worse than no
  zip, because a stale archive is indistinguishable from a current one and gets
  installed as if it were the work.
- **Five skills are also symlinked into `.claude/skills/`** and are therefore
  invocable in-session by name. Those symlinks **are tracked**; moving or
  renaming `skills/` breaks them and the harness silently stops offering those
  skills (`infrastructure/STRUCTURE.md` line 24).

⚠️ **Co-developed with the owner, so they round-trip out of this repo:** the five
symlinked skills — `editing-images`, `generating-images`,
`generating-rimworld-sprites`, `rimbridge`, `rimworld-modding`. Edit the copy
**here**, re-package, and say it has been **delivered**, not saved. Installing it
is the owner's action, not ours. The other eight are repo-only and are read by
path.

## The thirteen

| Skill | Read it when |
|---|---|
| `agent-messaging` | Before any cross-session send — send vs file vs commit, the ten-line ceiling, live-bridge announcements, what a peer cannot authorise. |
| `agent-reporting` | Reporting to the owner — glyph-led format, 72-char cap, terse by default, numbers over adjectives. |
| `editing-images` | Altering an image that already exists; holding invariants steady and detecting silhouette drift. |
| `generating-images` | Creating an image from nothing via Codex `$imagegen`, including the chroma-key route to alpha. |
| `generating-rimworld-sprites` | Any PNG destined for a mod's `Textures/` — canvas, real alpha, footprint, offline validator. |
| `gravship-layout` | Authoring, exporting or inspecting a `ShipLayoutDefV2` — no map, no build, no game running. |
| `rimbridge` | Driving a live RimWorld from outside: spawn, build, control time, screenshot, measure. |
| `rimworld-debug-testing` | Testing without a cold load — throwaway quicktest colonies, and what one can and cannot prove. |
| `rimworld-deploy` | Before testing anything in game, and whenever a change "didn't take". Writing a file is not deploying it. |
| `rimworld-load-round` | Before calling or queueing a restart — how to spend the ~23–30 minute cold load. |
| `rimworld-modding` | Any mod authoring, patching, def, load-order problem or `Player.log` triage. |
| `rimworld-savegame` | Reading, grepping or editing a `.rws` — grid codec, `fogGrid`, the two error phrasings. |
| `rimworld-start-prep` | Mods added, removed, reordered or re-sorted — the three uncoordinated writers of the mod list. |

## What does NOT belong here

- **A single failure you hit once.** That is a trap entry, not a skill.
- **Findings, measurements, state.** A skill says how; `observed/` says what
  happened and `infrastructure/state/` says where we are.
- **Campaign fiction or specs** → `design/`. A skill must survive a different
  playthrough.
- **How to operate somebody else's mod** → `vendor/wisdom/`.
- **Which skill to load when** → that is `CLAUDE.md`'s job, deliberately, so the
  routing lives in the file every session already reads.
- **Build outputs.** `<name>.skill` and `__pycache__/` are never committed.
