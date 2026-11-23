# Live tests: three kinds, one contract (draft 3, the short rule text; not yet a rule)

After the GPT review (`gpt_review.md`). The reasons, the examples and the owner's words are in `draft.md`.

## The Principle of Impactful Evidence (owner's wording; goes at the top of the Charter)

> **Testing is spent where it is likely to change what we do with appropriate resource cost.** Our resources are fixed. A test earns its place by the future value of the evidence it is likely to give weighed against the cost to (re)generate that evidence. Coverage for its own sake should be reserved for essentially free testing (offline and computationally cheap). These values and costs change as the system and our knowledge of it change, so a test's place must be periodically reviewed, and a test that no longer earns is retired.

Two rules keep the Principle honest:
- Weigh a test by what its evidence could change: how bad the fault is for the player, how often play reaches it, and what
  a cheaper check could show. Rare is not the same as low value.
- To retire a test does not fix or accept a fault. A retired test leaves its record (below).

## 1. Every live scene has a contract
Before its first run, a scene states:
- **the claim**: one sentence about what the mod does (example: "an ordered rescue carries this pawn out of the pit");
- **the entry point**: where the scene steps in, and which decisions of the mod it leaves to the mod;
- **a valid opportunity**: the state that must hold for the run to test the claim;
- **success**: game state that a program reads (who is where, who holds what), never only a message that the mod wrote;
- **forbidden effects**: what must not happen (a pawn lost or doubled, an exception);
- **the end**: when the program stops looking.
A program decides each run from the contract. An agent reads only a run that the program cannot decide.

## 2. A run ends in one of seven outcomes, kept apart
SUCCESS · MOD FAILURE · RANDOM MISS (a valid opportunity, an allowed miss) · ENVIRONMENT FAULT · APPARATUS FAULT ·
UNRESOLVED (something went wrong and nobody knows why) · COULD NOT LOOK.
- A run is an ENVIRONMENT FAULT only when the record shows that something outside the tested behaviour spoiled the
  opportunity. If the mod could have spoiled it, the run is UNRESOLVED.
- A forbidden effect is a MOD FAILURE in any run, even a spoiled one.
- Only SUCCESS speaks for the mod. No other outcome needs a later pass to cancel it.

## 3. The kind says how a scene is judged
A scene with no tag is kind A.
- **Kind A, deterministic.** The scene can make a valid opportunity on demand, and the result is not random. One valid
  run decides: PASS or FAIL. A count such as "4 of 5" is never used.
- **Kind B, stochastic.** After a sincere attempt at control, the opportunity is still uncertain, or the result is random
  by design. The scene looks for evidence of success.
  - It passes on one SUCCESS, with no MOD FAILURE and no UNRESOLVED run on the same claim and build.
  - That pass says "this was seen to work". It does not say how often it works.
  - How many runs to spend is a budget, written on the scene before the first run. When the budget ends with no
    SUCCESS, the verdict is INCONCLUSIVE, never PASS and never FAIL.
  - Where the result is random by design (a yield, a drop chance), the scene passes on X successes in Y valid
    opportunities. X and Y come from the intended yield and from the testing budget, and are written before the first
    run. Check the rate itself offline where that is possible, because offline runs are free.
- **Kind C, intermittent hunt.** A temporary hunt for a fault that shows only sometimes. It looks for evidence of failure.
  It is never part of a mod's final acceptance tests. It may use kind A or B scenes to get exposure; their verdicts
  stay their own.

## 4. Tags B and C carry their evidence
- Tag B names the things that spoil the run, what was tried to control each, and why that was not enough.
- Tag C names the symptom, how often it was seen in how many opportunities, and where the trace is.
- The tester gives the tag. The Conductor, the owner or a Fable rescue run gives it when the tester does not see the need.
- A tag changes how a scene is judged. A tag never removes a recorded run.

## 5. An UNRESOLVED run, and the hunt
- One UNRESOLVED run is recorded and holds the scene's pass until someone classes it.
- A hunt opens when the fault is serious (one sighting is enough) or is seen again.
- **A hunt never opens silently.** The run that opens it tells the Conductor: what happened, why it matters, the next
  step that would tell two causes apart, and what that step costs. The Conductor may call a Fable rescue, add the hunt to
  a later rescue, or look itself.
- Each hunt step answers a named question. Before each step, state what the answer could change and what the step may
  spend. Count opportunities, not runs.
- A hunt ends as one of four: FIXED AND SHOWN · NOT A FAULT (the apparatus, or disproved) · STOPPED, UNRESOLVED ·
  HANDED ON.
- A trigger found is not a fix. A hunt stopped is not a fix.
- After a fix, the forced scene stays in the live tests only while the fault is likely to return. Otherwise its check
  goes to the offline tests, or is retired.
- A hunt that stops unresolved leaves a record: the symptom, how bad it is for the player, the trace and the save, the
  build and mod list, what was tried, and what would reopen it. A serious unresolved fault also needs a written decision
  at the mod's pass: the Conductor writes it, and the owner reads it in his digest.

## 6. A spoiled environment is repaired, in proportion
- When a run names a thing that spoiled it, the run tries to remove that thing: hold or place it inside the scene, use
  the calm test environment, use a smaller mod list, use a bridge tool, or build a bridge tool.
- Lean towards building the control. A control is rarely for one scene: it lowers the cost of this scene's later runs
  and of many later scenes. So weigh a control against the testing it makes possible, not against one proof.
- Trace a spoiled run to its source. Be inventive. What still cannot be controlled is the reason for tag B.
- The calm test environment is a named bridge profile. It reports which controls it switched on and which it could not.
  A scene checks that the controls it needs are on. A line in a list is not proof.

## 7. Minimum Force (goes in the live-testing skills)
> **Use the least force that makes a scene affordable and reliable, and that leaves to the mod every decision the scene
> claims to test.** Whatever the force steps past is outside that scene's evidence.

The ladder, from most force to least, for "a raider crosses a covered pit": teleport it onto the cover; give it a path
over the cover; a corridor with no other way and bait beyond; a ring of pits round a base and a natural raid. Say which
step the scene uses and, in one line, why not a lighter one. Trying every lighter step first is not required.

## 8. Verdicts keep, per scene
- A scene's verdict stands until a change touches what the scene reads or exercises. The record names the build that the
  game had loaded, not only the build on disk.
- No exit asks for every scene in one visit, or for one scene several times in a row.
- **The testing horizon.** State which claims are left to the owner's walk and to real play. That is accepted.
