# Root causes

Five mechanisms generate the pain. None of them is a discipline failure — each is a
rational response, by the model or the owner, to a real incident. That is why adding
rules never fixed them: the rules *are* the mechanism.

## RC1 — Rigor is priced by the incident that created it, not by the cost to undo

Nearly every verification rule was born from a genuine disaster: seven confident wrong
counts in one session, a 13-day silent sampler, a 224-commit unpushed backlog, defs
silently discarded by an `<li>`. Those incidents share one property: they involve the
**expensive artifact** — the 25-minute load, the deploy target, the frozen savegame,
the def dump that lies. The rules they produced were then applied *uniformly*, so
deleting a file inherits the same posture as rewriting the worldmap. "It validates what
the human is asking for too much, as though the user is mistrusted" is this mechanism
seen from the outside: the system cannot tell a cheap mistake from an expensive one,
so it treats every request as potentially the expensive kind.

**Fix shape:** price rigor by reversibility, once, in one table (see REDESIGN §3).
Anything `git revert` can undo gets zero ceremony. The expensive list is short — about
six entries — and it already exists in fragments (BENCH's "three verify-first acts").

## RC2 — Prose is the enforcement substrate, and prose dilutes

The owner already learned this ("adding rules to prevent bad behavior just dilutes
existing rules") and the repo proves it twice over:

- `block_paste_handoff.py` exists because the same rule, written twice in prose, was
  violated anyway. Every hook in the repo enforces; almost no paragraph does.
- The SPEED ruling sits at the very top of CLAUDE.md, outranking everything — and
  still loses in practice, because salience is divided across 200+ imperatives. A
  priority system where everything is 🔴 has no priorities.

There is a second-order effect specific to LLM agents: **the model's cheapest
available "fix" for any incident is to write a rule**, because writing prose is what it
is best at and costs one tool call. So every retrospective produces doctrine, doctrine
produces conflicts, conflicts produce meta-doctrine (`POLICY.md:100-106` is a rule
about rule growth). The memory `owner-rules-must-be-data-not-prose.md` states the
lesson; it has not yet been applied to the constitution itself.

**Fix shape:** a rule may live in exactly three places — a hook (enforced), the
one-page charter (a default, one line, fixed budget), or git history (deleted). There
is no fourth place. See rewrites/CHARTER.md.

## RC3 — The write-a-rule reflex turned model indecision into permanent process noise

To the owner's direct question — *is Opus flip-flopping?* — the honest answer is yes,
and the evidence is unusually clean because the flips were archived:

- A ruling corrected "~20 minutes" after being issued, after the seat had already
  propagated the first version into three files (`DECIDE.md:106-115`).
- A verification rule superseded on 08-27 whose 08-23 form was itself a correction of
  the original (`CHECK.md:57-64`).
- `REP.md` disagreeing with itself about MODE vocabulary within one file.

Under-specified decisions plus an eager codifier produce oscillation; that is a known
failure mode of any strong model asked to legislate on the fly. But the damage here
was not the flip — flips are cheap. The damage was that **every position in the
oscillation was written down and kept**, so the doctrine now contains its own history
of indecision, and every future reader (agent or human) pays to re-litigate it. The
supersession chains in the seat files are fossilized flip-flops.

**Fix shape:** decisions land as one dated line in data (`canon.yml` or the item), and
a reversal **replaces** its predecessor — git is the archive of what was believed
before. A decision under 24 hours old may be reversed freely without ceremony; the
prose essay form of rulings is retired. (The propagation discipline in
`deciding-and-superseding` stays — it is the *number of places to propagate to* that
shrinks.)

## RC4 — Four resident maximal-context peers is the wrong topology

The peer-messaging ban was correct and measurably improved things. What remains is the
residual cost of the topology itself:

- **The doctrine tax is paid four times.** Each window re-reads 30–50k tokens of
  constitution+skills per wake (F1). Two of the four windows (REP, CHECK) no longer
  produce enough closed work to justify a resident context at all (F7).
- **Coordination moved from messages into files, but did not shrink.** 74 reassign
  events, queue renders committed 150+ times per seat, and the shared single worktree
  produces the stale-measurement collisions the memories document
  (`shared-worktree-remeasure-before-acting.md`).
- **Seats are personalities, and personalities accrete identity prose** (spinner
  verbs, pronouns, registers, "what this seat declines") that costs tokens and grants
  no capability. Your own `research/agentic_workflows.md` reached the same conclusion:
  strongly-typed interfaces, not personalities.

**Fix shape:** two resident windows (PAIR with you, FACTORY on the queue), lanes
instead of seats, subagents for fan-out, scripts/cron for rendering. See REDESIGN §2.

## RC5 — Skill curation happens at the worst possible moment

The 75%-context reboot ritual — "consider moving some lessons to skill" — hands the
most delicate editorial task (merge new knowledge into a long document without
duplicating it) to a model at its **highest context pressure**, mid-flight, with the
least room to read the skill it is editing. The triplicated block in
`generating-rimworld-sprites` (F5) is exactly what that produces: three sessions each
appended their lesson because none had room to read the whole file first. `traps.md`
at 10k words is the same dynamic with a designed journal that made appending
legitimate and pruning optional.

**Fix shape:** end-of-session writes go to a one-line-per-lesson inbox file; skills
are edited only by a fresh-context curation session on a schedule. See
WORKING_PATTERNS.md for the cadence.

## The meta-cause — deletion was expensive, so accretion won

Until `files-must-shrink-git-is-provenance` (late in the project), nothing made
deleting prose safe-feeling, while every incident made adding prose feel responsible.
Doc budgets tried to cap the symptom and became a shrink-treadmill (F4). The single
most important cultural change in this review is: **git history is the archive;
deletion is the default disposition for any rule that is not a hook or a charter
line.** Once deleting is cheap and normal, every other mechanism above loses its fuel.
