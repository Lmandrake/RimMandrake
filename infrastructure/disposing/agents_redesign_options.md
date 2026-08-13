# Agent redesign — lineup options for the owner to evaluate

_PROJECT, 2026-08-13, at the owner's request. **Decision document — nothing here
is adopted.** Options first, my recommendation last, open questions at the end._

---

## What the owner asked for

1. Each seat **extremely clear and relatively independent** of the others.
2. Seats act as **requested reviewers** of each other's work — by invitation, not patrol.
3. **Project files adjusted so each seat touches as few shared files as possible.**
4. **Different voices** that encourage the kind of thinking that seat's work needs.
5. **Different metrics / care-abouts** each brings to evaluating the project, centred on its expertise.
6. Each file opens **"You are a … "** — expert role plus skill list. A fully specced agent.
7. **Terse, jargon-free communication** above all.
8. Voice register: **opinionated experts** — licensed to hold and defend technical opinions, and to say the owner is wrong.

Mechanism already chosen: **the SessionStart hook injects the seat's file automatically**, keyed to the role recorded by `Utils/set_agent_window.sh`. No more "become agent X", and a resumed session cannot drift identity.

---

## Two measurements that constrain every option

**1. The contention is in the queues, not the code.** Touch counts over the last 400 commits:

| File | Touches | Owner |
|---|---:|---|
| `TODO.md` | **64** | shared by all four |
| `NEXT_RELOAD.md` | **45** | shared by all four |
| `skills/**/traps*.md` | 68 combined | shared |
| `AGENT_*_state.md` | 70 combined | single-owner each ✅ |
| `CLAUDE.md` | 19 | shared |
| `agents_def.md`, `STRUCTURE.md` | 30 combined | PROJECT |

The two shared queues alone are **109 touches** — more than the next four files
combined. Rule 6 tells a seat to back off when a file is dirty, so every hour one
seat holds `TODO.md` is an hour the other three are instructed not to file
anything. **This is the independence problem, and it is mostly independent of the
lineup choice.**

**2. `worldbuilding/` holds 31 files and has no seat.** The 2026-08-12 completion
survey found zero queue entries naming any of them, and water — the declared
master-resource — had zero hits anywhere in any queue.

---

## The flaw in the current cut

The four seats are cut by **lifecycle stage of an artifact**:

> CREATE (does not exist yet) → WORLD (live, must work) → BRIDGE (drives the live game) → PROJECT (the repo)

Three consequences follow from that choice alone:

- **It is an assembly line, so work crosses seats constantly.** `agents_def.md`
  has a whole `Handoff: CREATE → WORLD` section because the cut guarantees handoffs.
- **The campaign has no home.** "The campaign as a played experience" is not a
  lifecycle stage of an artifact, so it fell outside all four.
- **PROJECT is cut by medium (documents), which makes it inherently
  cross-cutting.** It polices everyone's files. That is the direct cause of it
  raising two already-settled items at the owner today.

**A cut by expertise — by profession — gives each seat a domain it owns end to
end.** It also makes "You are a …" write itself, which is what the owner asked
for.

---

## Option A — Five seats: keep the four, add CAMPAIGN

Smallest possible change. BRIDGE / WORLD / CREATE / PROJECT unchanged; a fifth
seat takes `worldbuilding/`, the faction roster, water doctrine, the endgame
branch web.

| | |
|---|---|
| ✅ | Fixes the single biggest documented gap with minimal disruption. Nothing to re-learn. |
| ✅ | Every existing rule, handoff and state file stays valid. |
| ❌ | Leaves the assembly-line handoff traffic exactly as it is. |
| ❌ | Leaves PROJECT cross-cutting, so the patrol problem persists. |
| ❌ | Five windows, and the new seat is defined by *what is left over* rather than by an expertise. |

---

## Option B — Five seats, re-cut by profession ⭐ my recommendation

| Seat | You are a… | Owns | Its metric — the question it brings to any review |
|---|---|---|---|
| **BRIDGE** | live-systems engineer — RimBridge/GABP, C#/Harmony, IL reading, latency measurement, in-game instrumentation | `bridgetools/`, `Utils/rimbridge_*`, `skills/rimbridge/` | *Has it been seen working in the running game?* |
| **MODWRIGHT** | RimWorld mod author — XML PatchOperations, def schemas, xpath, load order, `About.xml`, assembly packaging | `custom_patches/`, `mods/dev/`, `skills/rimworld-modding/` | *Does it load clean, and does the patch actually bind?* |
| **SHOWRUNNER** | game designer — RimWorld systems, faction/economy/threat design, narrative pacing, player-experience reasoning | `worldbuilding/`, `V1_SCOPE.md`, the roster, water doctrine | *Does the player ever notice this, and does it change play?* |
| **DIAGNOSTICIAN** | reliability engineer — `Player.log` forensics, conflict isolation, mod-set health, regression triage | `mods/`, `benign_log_errors.md`, the live mod set, harvest | *What is the evidence it is broken, and what is the smallest test?* |
| **ARCHIVIST** | technical writer + information architect — doc structure, staleness, scope discipline, the MVP seat | `CLAUDE.md`, `agents_def.md`, `STRUCTURE.md`, queues | *Can the next session find this and trust it?* |

| | |
|---|---|
| ✅ | Every seat is a real profession, so "You are a …" and the skill list write themselves. |
| ✅ | Five genuinely different evaluation lenses — the owner's "different metrics" requirement, satisfied by construction. |
| ✅ | Art/authoring split from diagnosis, which is the split that currently causes CREATE→WORLD handoffs. |
| ⚠️ | ARCHIVIST is still somewhat cross-cutting — mitigated by rule 9 (docs owned by subject owner) and by review-on-request rather than patrol. |
| ❌ | Largest migration: rules, handoffs, state files and queue tags all need rewriting. |
| ❌ | Where does **art** live? Under MODWRIGHT, or a sixth seat (Option D). |

---

## Option C — Four seats, re-cut, no repo custodian

LIVE (bridge + diagnosis) · BUILD (all authoring incl. art) · SHOWRUNNER (campaign) · plus **no** ARCHIVIST — every seat owns its own docs under rule 9, and staleness becomes a scheduled sweep rather than a seat.

| | |
|---|---|
| ✅ | Four windows, less coordination, fewer git collisions, no growth. |
| ✅ | Rule 9 is already ratified, so decentralised doc ownership is not a new idea. |
| ❌ | **The completion survey exists because nobody was watching the whole.** Removing the seat that produced it is a real risk. |
| ❌ | Merging bridge and diagnosis puts two very different expertises in one window. |

---

## Option D — Six seats: Option B plus ARTIST

As B, with art split out: sprite/texture generation, the chroma-key alpha pipeline, the offline validator, style-matching to shipped RimWorld art.

| | |
|---|---|
| ✅ | Art genuinely is a separate expertise with its own skills (`generating-rimworld-sprites`, `editing-images`) and its own validator. |
| ✅ | The lost sled art shows art work has its own failure modes and its own durability needs. |
| ❌ | Six windows is a lot of coordination for one person to supervise, and art is bursty — the seat idles between requests. |

---

## Cross-cutting: split the queues, whichever lineup wins

This is the highest-value change on the page and it is **independent of the lineup**.

**Now:** two shared queues, 109 touches, constant rule-6 backoff.

**Proposed:** one queue per seat — `queue/BRIDGE.md`, `queue/SHOWRUNNER.md`, … Each
seat writes freely in its own file and **never blocks anyone**. Filing *at* another
seat means appending to **their** queue — a single append to a file its owner is
usually not holding, instead of four writers contending on one file.

`NEXT_RELOAD.md` is the exception worth keeping shared: it is genuinely one
document about one event (the next load), read top-to-bottom by whoever drives it.
Keep it shared, but move per-seat *staging* into the per-seat queues so only
load-round items land there.

Expected effect: the top-two contended files drop out of the contention list, and
rule 6a's "hold for minutes not hours" stops being load-bearing.

---

## Open questions for the owner

1. **Lineup** — A, B, C or D?
2. **Art** — its own seat, or inside the authoring seat?
3. **Queue split** — adopt per-seat queues? (I recommend yes regardless of lineup.)
4. **Where do the identity files live?** `.claude/agents/*.md` is Anthropic's
   documented location and gets tooling support, but those files drive
   *non-interactive* helpers. The seats are interactive windows, so their files can
   live there for consistency and be injected by hook — or live in `agents/` to
   avoid implying they are spawnable subagents. **This one has a real trade-off and
   I want the owner's call.**
5. **Does the seat list also become real subagent definitions?** Separately from the
   seats, the throwaway helpers we spawn (roster auditor, log triager, art
   validator) *are* genuine `.claude/agents/` candidates.
6. **How opinionated?** "Tell the owner they are wrong" — does that extend to a seat
   declining work it judges out of scope, or only to arguing before complying?

---

## What Anthropic actually specifies (so we know what is ours to invent)

From `https://code.claude.com/docs/en/sub-agents.md`:

- **Stated:** frontmatter is `name` + `description` required; `tools`,
  `disallowedTools`, `model`, `skills`, `memory`, `hooks`, `effort`, `color` and
  others optional. Body becomes the system prompt. Project `.claude/agents/`
  outranks user `~/.claude/agents/`. **Every level of CLAUDE.md loads into
  subagents**, and the agent prompt is *additional* to it, not a replacement.
- **Stated best practice:** *"each subagent should excel at one specific task"*;
  write detailed descriptions because the description is what triggers delegation;
  limit tool access; check project agents into version control.
- **All examples are second person** — "You are a code reviewer" — which matches
  the owner's requested opening.
- **Docs are SILENT on:** recommended prompt length, whether to include examples,
  and any formal method for deciding when two agents are too similar. **The
  distinctness design below is ours, not Anthropic's.**
