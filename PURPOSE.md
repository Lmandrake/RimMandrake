<!-- status: live -->
# What this repository is

**RimMandrake is an agentic experimental software factory, and the thing it is building is a
game.** Both halves of that sentence are the point. If you only read one page of this repo,
read this one: nothing else here makes sense without it.

It has two intentions, held at the same time and on purpose:

1. **To build the most comprehensive remake of RimWorld ever attempted** — not a mod list, but
   a coherent, hand-authored world with its own biomes, creatures, physics, factions, lore and
   fiction, judged on whether a player's experience is right.
2. **To be an experiment in whether agentic factory pipelines can expand a *creative* project**
   — not merely execute a requirements document. Almost every agent pipeline in the world is
   pointed at work where the answer is known in advance and the only question is whether the
   code matches the spec. This one is pointed at work where the spec itself is the hard part,
   taste is the acceptance criterion, and "correct" is a thing someone has to *look at* to
   judge.

This is Lukas Mandrake's passion project and his laboratory. It is where he tries new ideas for
agents, factories, orchestration strategies, workflows, delegation boundaries, judging,
refusal, memory and measurement — and the ones that survive here inform his research
elsewhere. Work here is play in the serious sense: intellectual play, done deliberately, in a
place chosen because its failures are cheap.

## The declaration

> *"This repo needs to become aware of its overall purpose. It is an agentic experimental
> software factory pipeline. It is indeed intended to create the most comprehensive remake of
> Rimworld ever seen. It is also an experiment in using agentic experimental factory pipelines
> to expand creative projects, rather than merely requirements-driven software production. It is
> where Lukas Mandrake tries new ideas for agents, factories, orchestration strategies,
> workflows, and many other aspects that inform the rest of his research elsewhere. ... this is
> not merely "a game." It is a passion project where Lukas Mandrake intellectually plays and
> performs deep experimentation in an environment that is low-consequence as well as deeply,
> intuitively understandable at every step such that agentic behavior becomes more
> understandable, more interpretable, and more trustable overall."*
>
> — Lukas Mandrake, 2026-11-17, instructing that this be made formal repo documentation

## Why a game, and why this game

The choice of domain is the experimental design, not a hobby that happened to need tooling. A
colony sim on a desert world has three properties that are extraordinarily hard to buy
anywhere else at once:

**It is low-consequence.** Nothing an agent does here can hurt a person, lose money that
matters, leak anything, or break a system someone depends on. That means agents can be given
real autonomy — the authority to decide, to deploy, to restart, to judge each other, to refuse
— and the cost of discovering that an autonomy boundary was drawn wrong is a bad afternoon, not
an incident. Dangerous ideas get tried here *because* they are safe here.

**It is deeply, intuitively understandable at every step.** A human can look at a screen and
know instantly whether a creature moves wrong, whether the light is wrong, whether a biome
feels dead, whether an explosion threw the right things. There is no expert gap between the
work and the judgment of the work. That makes it possible to catch an agent being subtly,
confidently wrong — the failure mode that matters most and that is nearly invisible in domains
where only a specialist can tell. The game is the instrument: it renders agent behaviour into
something a person can see.

**It is unbounded and creative.** There is no finish line handed down from outside, so the
pipeline has to generate its own intent, argue it out, write down what "good" means before it
builds, and then be held to it. That is the actual research question.

Put together: this is an environment where agentic behaviour becomes more **understandable**
(you can follow every step), more **interpretable** (you can see what the agent believed and
where it went wrong), and more **trustable** (trust earned by watching, not asserted).

## What is actually being experimented on

A visitor who expects "a mod repo plus some scripts" will misread almost everything here. The
machinery is the subject of study, and much of it exists to make agent work legible and
checkable rather than to produce defs faster. The recurring experiments:

- **Seats and roles instead of one assistant.** Named roles with different jobs, authorities and
  context: the Conductor (the window the owner talks to, which decides and launches work), the
  Designer (argues a mod's design out before any code), Operations (watches the system's
  health), Dispatch (the clock, with no AI in it), the Test Pilot (one live debugging sitting).
  `LEXICON.md` is the protected vocabulary; `infrastructure/agents/` holds the role files.
- **An append-only ledger as the memory of record.** Every claim, close, finding, refusal and
  delegated decision is an event on disk (`rimflow`), not a thing an agent remembers. Sessions
  die; the ledger does not.
- **Blind judging and separation of maker from marker.** The agent that judges work is a fresh
  one that did not do it, did not see the attempt, and is given the exam rather than the answer.
- **Written-down intent before the build.** A mod states its *north star* and its **bars** —
  plain sentences about what a player must see — and those are set before the work, not fitted
  to it afterwards. A bar is an experience, never a tuning number.
- **Design Versions.** Each mod names the version of its *design* it is building towards
  (Semantic Versioning), which separates "this got closer to the vision" from "this changed the
  vision" — Convergent versus Divergent — and keeps a pipeline from quietly redefining success.
- **Refusal as a first-class artifact.** A gate or judge that refuses must say what evidence it
  rejected, what would pass, and the smallest fix. "No" without a path forward is itself a
  defect.
- **Delegation boundaries, explicitly.** Agents decide nearly everything, art included; a short
  list stays with the owner; every delegated call is logged as a delegation and not as his
  approval. Finding out where that line actually belongs is one of the experiments.
- **Instrument distrust.** A measurement tool that returns a confident wrong number is treated
  as the primary hazard; known traps are written down
  (`infrastructure/state/facts/instrument_traps.md`) and guards exist to refuse a guess
  dressed as a measurement.
- **Live proof over assertion.** Change is proven in the running game through a single-driver
  bridge and scripted sittings, on two machines, with screenshots a human can stare at.
- **Pipelines that fix themselves.** When the pipeline finds a defect in its own machinery and
  the fix is known, it fixes it in the same run rather than filing it for someone else.

Several of these were built, measured, found wanting and retired — that history is kept
(`design/RimMandrake/retired_loops_2026-11-13.md`), because a failed orchestration strategy is
a result, not an embarrassment. The current successor is the **Maturation Pipeline**, whose
work unit is a whole versioned mod rather than a ticket
(`design/specs/2026-11-13-maturation-pipeline.md`).

## What this is not

- **Not merely "a game."** Judging this repo as a game project misses the experiment; judging
  it as pure agent research misses that the game must genuinely be good, because an experiment
  whose output nobody cares about cannot test taste.
- **Not a requirements-driven software shop.** There is no external customer, no deadline, no
  scope document handed down. Intent is generated and argued here.
- **Not a product, and not commercial.** It is a private passion project built on RimWorld
  (© Ludeon Studios), played with all its expansions.
- **Not a worldgen toolkit.** Players never generate anything; one hand-made world is authored,
  frozen, and shipped as a savegame. (Owner ruling; see `CLAUDE.md`.)
- **Not a demonstration that agents are trustworthy.** It is an attempt to find out *when* they
  are, in the one environment where being wrong is affordable and being wrong is visible.

## Where to go next

| You want | Read |
|---|---|
| the rules every agent here obeys | `CLAUDE.md`, then `infrastructure/agents/CHARTER.md` |
| the words this project protects | `LEXICON.md` |
| the current pipeline design | `design/specs/2026-11-13-maturation-pipeline.md` |
| what we intend to exist | `design/README.md` and `design/INDEX.md` |
| what has been measured in a running game | `observed/` |
| the owner's standing rulings | `design/RimMandrake/standing_rulings.md` |
| how the live game is driven | `infrastructure/GAME_STATE_WORKFLOW.md` |
| how debugging is done here | `design/RimMandrake/debug_process.md` |
| the ledger | `rimflow` (`src/RimMandrake/rimflow/`) |

**The tier rule, which governs every document here:** `design/` is intent, `observed/` is
measurement, `deployed/` is what a game can actually load, `research/` and `vendor/` are
material we did not write. A sentence in the wrong tier is how a repo starts lying to itself,
and keeping those apart is part of the experiment too.
