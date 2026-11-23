<!-- status: live -->
# What this repository is

**RimMandrake is an agentic experimental software factory, and the thing it is building is a
game.** Both halves of that sentence are the point. If you read only one page of this repo, read this page. Nothing else
in the repo makes sense without it.

The repo has two intentions. The repo holds both intentions at the same time, on purpose:

1. **To build the most comprehensive remake of RimWorld ever attempted.** The remake is not a mod list. The remake is a
   coherent, hand-authored world with its own biomes, creatures, physics, factions, lore and
   fiction. We judge the remake on whether a player's experience is right.
2. **To be an experiment in whether agentic factory pipelines can expand a *creative* project**, not merely execute a
   requirements document.
   - Almost every agent pipeline in the world works where the answer is known in advance. There, the only question is
     whether the code matches the spec.
   - This pipeline works where the spec itself is the hard part. Taste is the acceptance criterion. Someone must
     *look at* the result to judge whether it is "correct".

This repo is Lukas Mandrake's passion project and his laboratory. Here he tries new ideas for agents, factories,
orchestration strategies, workflows, delegation boundaries, judging, refusal, memory and measurement. The ideas that
survive here inform his research elsewhere. Work here is play in the serious sense: intellectual play, done on
purpose. He chose this place because its failures are cheap.

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

The choice of domain is the experimental design. The game is not a hobby that happened to need tooling. A colony sim on a
desert world has three properties at once. That combination is extraordinarily hard to buy anywhere else.

**It is low-consequence.**
- An agent here cannot hurt a person or lose money that matters.
- An agent here cannot leak anything or break a system that someone depends on.
- So agents can get real autonomy here: the authority to decide, deploy, restart, judge each other and refuse.
- To discover a wrongly drawn autonomy boundary costs a bad afternoon, not an incident.
- We try dangerous ideas here *because* they are safe here.

**It is deeply, intuitively understandable at every step.**
- A human can look at a screen and know instantly whether something is wrong:
  - whether a creature moves wrong;
  - whether the light is wrong;
  - whether a biome feels dead;
  - whether an explosion threw the right things.
- No expert gap lies between the work and the judgment of the work.
- So a person can catch an agent that is subtly, confidently wrong. That failure mode matters most. In a domain where
  only a specialist can tell, that failure is nearly invisible.
- The game is the instrument: the game renders agent behaviour into something that a person can see.

**It is unbounded and creative.**
- No one outside hands down a finish line.
- So the pipeline must generate its own intent and argue the intent out.
- The pipeline must write down what "good" means before it builds. Then we hold the pipeline to that text.
- Whether a pipeline can work this way is the actual research question.

Together, these three properties make an environment where agentic behaviour becomes more:
- **understandable**: you can follow every step;
- **interpretable**: you can see what the agent believed, and where the agent went wrong;
- **trustable**: you earn trust by watching, not by assertion.

## What is actually being experimented on

A visitor who expects "a mod repo plus some scripts" will misread almost everything here. The machinery is the subject
of study. Much of the machinery exists to make agent work legible and checkable, not to produce defs faster.
Here are the recurring experiments:

- **Seats and roles instead of one assistant.** Named roles have different jobs, authorities and context:
  - the Conductor: the window that the owner talks to, which decides and launches work;
  - the Designer: argues a mod's design out before any code;
  - Operations: watches the health of the system;
  - Dispatch: the clock, with no AI in it;
  - the Test Pilot: one live debugging sitting.

  `LEXICON.md` is the protected vocabulary. `src/RimMandrake/rimflow/roles/` holds the role files.
  `infrastructure/agents/` holds the charter, the model policy and the Conductor's file.
- **An append-only ledger as the memory of record.** Every claim, close, finding, refusal and delegated decision is an
  event on disk (`rimflow`). The ledger is not a thing that an agent remembers. Sessions die; the ledger does not.
- **Blind judging and separation of maker from marker.** The agent that judges the work is a fresh agent. That agent
  did not do the work and did not see the attempt. The judge gets the exam, not the answer.
- **Written-down intent before the build.** A mod states its *north star* and its **bars** before the work. A bar is
  a plain sentence about what a player must see. We set the bars before the work; we do not fit them to the work
  afterwards. A bar is an experience, never a tuning number.
- **Design Versions.** Each mod names the version of its *design* that it is building towards (Semantic Versioning).
  - The version separates "this got closer to the vision" (Convergent) from "this changed the vision" (Divergent).
    - So the versions keep a pipeline from quietly redefining success.
- **Refusal as a first-class artifact.** A gate or judge that refuses must say three things: what evidence it
  rejected, what would pass, and the smallest fix. A "No" without a path forward is itself a defect.
- **Delegation boundaries, explicitly.**
  - Agents decide nearly everything, art included.
  - A short list of acts stays with the owner.
    - Every delegated call is logged as a delegation, not as his approval.
  - One of the experiments is to find out where that line actually belongs.
- **Instrument distrust.** We treat a measurement tool that returns a confident wrong number as the primary hazard.
  - We write down the known traps (`infrastructure/state/facts/instrument_traps.md`).
  - Guards exist to refuse a guess dressed as a measurement.
- **Live proof over assertion.** We prove a change in the running game, through a single-driver bridge and scripted
  sittings, on two machines. The proof includes screenshots that a human can stare at.
- **Pipelines that fix themselves.** The pipeline can find a defect in its own machinery. If the fix is known, the
  pipeline fixes the defect in the same run. In that case the pipeline does not file the defect for someone else.

We built, measured, found wanting and retired several of these experiments. We keep that history
(`design/RimMandrake/retired_loops_2026-11-13.md`), because a failed orchestration strategy is a result, not an
embarrassment. The current successor is the **Maturation Pipeline**. Its work unit is a whole versioned mod, not a
ticket (`design/specs/2026-11-13-maturation-pipeline.md`).

## What this is not

- **Not merely "a game."**
  - If you judge this repo as a game project, you miss the experiment.
  - If you judge the repo as pure agent research, you miss that the game must genuinely be good.
  - An experiment whose output nobody cares about cannot test taste.
- **Not a requirements-driven software shop.** There is no external customer, no deadline and no scope document from
  outside. We generate and argue the intent here.
- **Not a product, and not commercial.** The repo is a private passion project built on RimWorld (© Ludeon Studios),
  played with all its expansions.
- **Not a worldgen toolkit.** Players never generate anything. We author one hand-made world, freeze it, and ship it as
  a savegame. (Owner ruling; see `CLAUDE.md`.)
- **Not a demonstration that agents are trustworthy.** The repo is an attempt to find out *when* agents are
  trustworthy. The attempt runs in the one environment where being wrong is affordable and being wrong is
  visible.

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

**The tier rule, which governs every document here:**
- `design/` is intent.
- `observed/` is measurement.
- `deployed/` is what a game can actually load.
- `research/` and `vendor/` are material that we did not write.

A sentence in the wrong tier is how a repo starts to lie to itself. Keeping the tiers apart is part of the experiment too.
