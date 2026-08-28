# Redesign #4 — Two hands, one ledger

The first three redesigns each removed a coordination channel (peer chat, queue
hand-edits, the CHECK re-read loop) and each helped. This one removes the remaining
fixed costs: resident seats that don't earn residency, ceremony priced by fear instead
of reversibility, and prose as an enforcement substrate. It is deliberately aligned
with the conclusions already reached in `research/agentic_workflows.md` (control
plane, typed interfaces, human reserved for judgment) — this is that document applied,
not a new philosophy.

## §1 Design principles

1. **Rigor is priced by cost-to-undo, nowhere else.** One table, six entries, replaces
   ~50 verification rules.
2. **A rule lives as a hook, a charter line, or nothing.** Prose does not enforce.
3. **Decisions are data.** One dated line, replacement-on-reversal, git as archive.
4. **Context is the scarcest resource.** Every resident window must earn its doctrine
   tax; everything that can be a script or a subagent is one.
5. **BENCH generalizes.** The posture that worked — "you're with me, do what I say,
   minimal checking" — becomes the default posture toward the owner everywhere, with
   the expensive list as the only exception.

## §2 Topology: two resident windows + subagents + scripts

| role | what it is | model |
|---|---|---|
| **OWNER** | The decider. All rulings are his; DECIDE ceases to exist as a window. | — |
| **PAIR** | The window at his side. Permanently BENCH. Does what he says, asks questions immediately, drafts decision one-liners for him to accept, spawns subagents for anything long. | Fable/Opus |
| **FACTORY** | The autonomous window. Pulls the queue oldest-first by lane, ships, closes by commit trailer, never asks. Runs AFK batches. | Sonnet (escalates per item, see MODELS_AND_TOKENS.md) |
| **subagents** | Fan-out: censuses, sweeps, audits, art batches, verification passes. Always with `model` set. | Haiku/Sonnet |
| **scripts/cron** | Board render, queue views, roster generators, sweeps. No model. | — |

What happens to the four seats:

- **BUILD → FACTORY.** Same work, same ownership of `src/`, one-line charter.
- **DECIDE → the owner**, with PAIR drafting. The design/ tree keeps its owner rule.
- **CHECK → a lane, not a window.** The 08-27 ruling already did this: verification is
  owed only to things never once observed running, and whoever proves it closes it.
  A `lane: check` item is picked up by FACTORY (or PAIR at the bench) like any other.
- **REP → a cron job plus a PAIR duty.** Board render and queue views are scripts.
  The one human-facing duty (triage what needs the owner) is PAIR's, because PAIR is
  where the owner is.

Two windows also halves worktree collisions by construction: FACTORY is the only
autonomous writer; PAIR writes only what the owner just asked for. If a third window
is ever warranted (a long AFK art batch), it is a temporary FACTORY-2 with an explicit
directory lease, not a new identity.

**Seat identity prose (pronouns, spinner verbs, registers, "what this seat declines")
is retired.** It costs tokens every wake and grants no capability.

## §3 The reversibility table — the whole verification doctrine

| tier | definition | ceremony |
|---|---|---|
| **T1** | `git revert` undoes it completely (edits, deletes, renames, repo files, queue items, docs) | **None.** Act, commit, push, one line. No claim/start/verify, no report. |
| **T2** | Undoable with effort (deploys to the Mods folder, ModsConfig writes, board/tool changes other windows consume) | One pre-check named by the tool itself (deploy plan read, porcelain check). Close normally. |
| **T3** | Expensive or irreversible: a cold-load slot · savegame writes to the frozen world or ship saves · force-push/history rewrite · deleting work not yours · anything the owner must LOOK at to judge | Spec/verify/criteria earn their keep **here only**. Batch into load rounds. Evidence in the closing commit. |

"Remove this file" is T1: the correct total response is `git rm`, commit, push,
"Done, `<hash>`." Anything more is the defect.

## §4 Item lifecycle v2

- **An item is one line** — `NAME · lane · the ask` — plus an optional pointer.
  spec/verify/criteria sections exist only on T3 items. `rimflow file` stops prompting
  for them otherwise.
- **The commit trailer is the close.** `claim`/`start` survive only as advisory locks
  when two writers might collide; T1 items skip them entirely.
- **Staleness inverts.** Current default: prove an item stale before dropping (the
  10-minute burn). New default: **one grep/probe; if it doesn't prove the item still
  live, drop it with `stale-drop` and move on.** Real work re-files itself in one
  line; a wrongly dropped item costs 30 seconds to restore from git. The asymmetry is
  overwhelming and it currently points the wrong way.
- **The owner's word closes anything.** "That's already validated — remove it" is a
  T1 act plus a ledger line `closed at owner's word`. No complaint, no re-derivation,
  no "let me just confirm." (BENCH already says this; it becomes global.)
- **Queue hygiene is a cron script**, not a seat behavior: anything closed >48h ago
  still rendering, any `needs:` pointing at a dead gate, gets listed for the owner in
  one screen. Nobody "verifies completeness" by hand again.

## §5 Decision hygiene (the anti-flip-flop mechanism)

- A ruling is **one dated line in `canon.yml`** (numbers/rosters) **or on the item**
  (scope/process). PAIR drafts it; the owner says yes; it lands.
- **Reversal replaces.** The old line is deleted in the same commit; git holds it.
  Supersession chains in prose are retired — `deciding-and-superseding`'s propagation
  step gets cheaper because there is one canonical location to propagate *from* and
  far fewer places that restate rules to propagate *to*.
- **A ruling under 24h old is a draft** — reversible without ceremony or apology.
  This gives the model (and the owner) explicit permission to be provisional, which
  removes the incentive to over-specify on first contact — the root of the
  flip-then-archive pattern.

## §6 Instruments, in order

For any question about game mechanics: **① RimSage** (`mcp__rimsage__*` — defs and
C# source, no load, no byte-scan) → **② the def dump via `measure`** (post-patch
truth) → **③ quicktest via bridge** (90 s, runtime truth) → **④ a cold-load slot**
(T3, batched). Most of the "read the mechanism first" memories exist because ① wasn't
available or wasn't reached for; it now short-circuits the majority of live checks.

## §7 What this does NOT change

Hooks (all kept, several rules migrate *into* hooks). `canon.yml`. `facts/`
(unbudgeted). The minimal-modlist regime, quicktest, bridge, deploy tooling, measure.
The design-doc supersession banners. BENCH/BELT/AFK vocabulary (PAIR is permanent
BENCH; FACTORY is permanent BELT). The no-peer-messaging ruling — with two windows
there is nothing to message.

## §8 Migration path (about half a day, reversible at every step)

1. **Adopt the charter.** `rewrites/CHARTER.md` → `infrastructure/agents/CHARTER.md`.
   POLICY.md and the four seat files are reduced to a three-line pointer at the top
   ("superseded by CHARTER.md, <date>, git holds the old text") — honoring the
   "supersede into the superseded doc" rule once, on the way out.
2. **Disposition every current rule**: hook-covered → delete the prose; genuinely
   needed default → already a charter line or it isn't needed; everything else →
   delete. The doc-budget system retires with the mass it policed (`doc_budget.py`
   and `warn_doc_budget.py` removed; `facts/` never needed it; the charter cannot
   grow by construction).
3. **Patch rimflow**: add `--tier`, stop prompting spec/verify on T1/T2, add
   `stale-drop`, accept trailer-only closes for T1. (Half of this is deleting guards.)
4. **Stand down REP and CHECK windows.** Cron the board render. Fold their open items
   into lanes.
5. **Run one week, measure two numbers** already free in the ledger: median
   file→close wall time, and process-share of commits. If the process share doesn't
   fall below ~35% and simple requests aren't near-instant, revisit — with data, not
   a fifth redesign from intuition.

## §9 Risks, stated honestly

- **Sonnet-run FACTORY will make more small mistakes than Opus.** Accepted by design:
  T1 mistakes are `git revert` cheap, T3 items escalate models per item. The review's
  bet is that ceremony was compensating for a cost asymmetry that mostly doesn't
  exist.
- **Dropping stale items will occasionally drop a live one.** Restoring is 30 s from
  git; the current alternative burns 10 min per *already-done* item, and done items
  outnumber wrongly-dropped ones by the ledger's own arithmetic (F6).
- **A one-page charter will feel underspecified.** It is — deliberately. The 15k-word
  version was tried and produced this review. When a gap appears, the answer is a
  hook or a charter line that *replaces* one, never an appendix.
