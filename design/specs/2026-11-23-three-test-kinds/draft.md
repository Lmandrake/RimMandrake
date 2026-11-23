# Three kinds of live test: draft 1 (working text, not yet a rule)

Item `RIMMANDRAKE_ENACT_THREE_TEST_KINDS_FORCED_COUNTED_HUNTED_NOT_STARS_ALIGNED`. Written 2026-11-23 by the Conductor with
the owner. Next steps, in his order: his corrections, a deep GPT review, then the final short rule text. Nothing here
binds a run yet.

## The problem
A live scene can fail while the mod is correct. Two cases from 2026-11-23:
- Explosive Knockback visit 4: the "spared carrier" scene failed once because the carrier walked out of the blast, then
  passed six times. The one failure still blocked the visit's exit.
- FlowWorks: a raider was lifted out of a pit by a comrade on the rim once in 18 free runs. When the rescue was ordered
  directly, it happened 2 of 2 times, and the bug was fixed the same morning.
A visit exit that needs every scene to pass in one visit, or a scene to pass several times in a row, makes a correct mod
wait for luck. Each wait costs a full game load and a full suite.

## 1. Every live test declares its kind
- **Kind A, deterministic.** The default. The capability is reliable and the test can show it on demand. One run decides.
  A failure is a real failure. A count such as "4 of 5" is never used for kind A.
- **Kind B, stochastic.** The capability is reliable, or random by design, but the outcome of a run depends on things the
  test cannot control. The test looks for **evidence of success**. A clean, traced success is strong evidence. A failure
  is evidence only after it is read.
- **Kind C, intermittent hunt.** The test itself is deterministic. The test hunts a bug that shows only sometimes. The
  test looks for **evidence of failure** among apparent successes. Kind C is a temporary mode of a hunt, never a
  permanent member of a mod's acceptance suite.

A test with no tag is kind A.

## 2. What a tag costs
- A tag B or C is a claim, and the claim carries its evidence on the test.
- **Tag B** names: the environment variables that confound the run; what was done to control each one (a smaller mod
  list, the calm test environment, an existing or new bridge capability); and why control was not enough.
- **Tag C** names: the bug, how many times it was seen in how many runs, and where its trace is.
- The tester gives the tag. The Conductor, the owner, or a Fable rescue run may also give it, and will give it when a
  tester fails to see that it is needed. The diagnosis of a failed visit is the usual moment.
- A program refuses a B or C tag whose evidence is empty. Nothing else gates the tag.

## 3. How each kind is run and judged
**Kind A.** One run. PASS or FAIL. A failure sends the mod back or is fixed in the sitting, as today.

**Kind B.**
- Each run of the scene ends in one of five outcomes, kept apart: SUCCESS (traced), MOD FAILURE, ENVIRONMENT FAULT,
  APPARATUS FAULT, COULD NOT LOOK.
- The scene checks its own preconditions at the deciding moment (the carrier is inside the blast when it fires). A run
  whose preconditions did not hold is an ENVIRONMENT FAULT. It is not a FAIL, and it never needs a later PASS to "replace"
  it.
- The test passes on evidence of success: at least one traced success, and no run classed MOD FAILURE.
- Every non-success run is read and classed. The count "X of Y" is a resource choice for that test, set before the first
  run and written on the test with its reason. The count is tuned by experience.
- A failure that nobody can class after one read is not bad luck. If it is seen a second time, it opens a kind C hunt.
- Where the capability is random by design (a yield, a drop chance), the test states the expected rate and the count
  that would show it, before the first run.

**Kind C.**
- Opened after a bug is seen once or twice. Run mostly by a test pilot. A cheap tripwire (a check that goes red with a
  trace if the bug shows) may ride inside the mod's other runs while the hunt is open.
- The hunt ends in one of three ways:
  1. The trigger is found. It becomes a forced scene, kind A where possible, and the bug is fixed.
  2. The bug is fixed, and its forced scene stays in the live suite only if there is evidence that the bug is likely to
     come back. Otherwise its "once wrong" check goes to the offline tests, which are cheap to keep, or is retired.
  3. The bug cannot be reproduced, or shows too rarely to force. The hunt and its tripwire are removed from the mod's
     acceptance tests. One line records what was seen.
- The live acceptance suite is never a list of everything that was once wrong.

## 4. Verdicts are per scene, and they keep
- A scene's verdict on a build stands until a change touches what that scene reads or exercises (already a rule).
- No exit asks for all scenes in one visit, or for a scene several times in a row, unless that scene's tag says why.

## 5. An environment fault is removed, not rerun
- An ENVIRONMENT FAULT is not a mod failure. It may be an apparatus failure: that depends on how much control we had.
- Each time a confounding variable is named, the run that named it tries to remove it, in this order of cost:
  1. pin or place the thing inside the scene;
  2. use the calm test environment (below);
  3. use a smaller mod list;
  4. use an existing bridge capability;
  5. build a new bridge capability.
- A removed variable is written once in a shared list, with its removal, so that the next scene starts from it.
- **The calm test environment** is one named, standard state that a scene asks for. Proposed content, to be checked
  against the game: no storyteller incidents, no raids or visitors that the scene did not place, no wild animals, fixed
  weather, hour and season, pawn needs and mental breaks frozen, a fixed random seed where the engine allows it.
  Which of these the bridge can already do is UNMEASURED.
- Some influence will always remain. The aim is that a correct mod almost never fails a live suite.

## 6. Minimum force
- Forcing is a tool with a cost. A forced scene shows the elemental capability, and hides the configurations that real
  play makes.
- **Use the least force that makes the test affordable and reliable.** The ladder, from most force to least, for
  "a raider walks over a covered pit":
  1. teleport the raider onto the cover;
  2. give the raider a path over the cover;
  3. build a corridor with no other route and place bait beyond the pit;
  4. ring a natural base with covered pits and let a natural raid find its way.
- Step 4 is almost never affordable. Each scene says which step it uses and why a lower-force step was not used.
- Force the environment. Do not force past a decision that our own mod's code makes: that decision is under test, and
  it gets its own scene.
- **The testing horizon.** Some configurations are found only at the owner's walk, and some only in real play. That is
  accepted. The horizon is what we can afford, and it is stated, not hidden.

## 7. The Principle of Impactful Evidence (proposed wording, for his correction)
> **Testing is spent where it is likely to change what we do.** Our resources are fixed. A test earns its place by the
> future value of the evidence it is likely to give, never by coverage for its own sake. That value changes as the
> system and our knowledge of it change, so a test's place is reviewed, and a test that no longer earns it is retired.

Corollaries that this draft already uses: a hunt that cannot reproduce its bug is dropped; a fixed bug keeps a live
check only when it is likely to return; cheap offline checks may hold many "once wrong" cases, because their cost is low.

## 8. Open points for him and for the GPT review
- How a scene proves "traced success" without an agent reading every trace (cost).
- Whether "seen a second time" is the right door from kind B into kind C.
- Who retires a test under the Principle, and how often the review happens.
- What the calm test environment can really hold still in RimWorld, and what each missing bridge capability costs.
- How the existing scenes of the four running mods sort into A, B and C, and what that does to their open exits.
- Whether a fixed random seed is possible with a full mod list.

## His words, verbatim (2026-11-23)
The order (about 11:35 AM PST):

> YES! Stochastic event testing requires the changes you pose. 0) We need to define three things to make this work. A: deterministic test (should always be reliably testable, the standard default, what we assume today). B: Stochastic test (testing a reliable capability with many input variables that make the test's outcome unreliable, thus requiring looking for evidence-of-success rather than guaranteed reproducable success on demand. Only justified due to large numbers of unreliable environmental variables or a capability that itself stochastic in yield/production by intention) C: Intermittent test (the test itself is deterministic, but it's seeking an intermittent bug that only occasionally manifests due to complex environments or unknown nature, thus requiring looking for evidence-of-failure amidst repeated apparent successes). We need to explicitly tag tests for their intention, so they can be repeated and judged appropriately. Approved explicitly: 1) Force the situation ALWAYS if possible, there are too many variables to control otherwise. 2) Broaden this definition of detection/success/failure to handle A, B, and C cases explicitly. 3) Required to handle case B. 4) Correct, a detected failed environment is not a mod failure and may or may not indicate a testing apparatus failure, depending on the level of our own control. Each time a failed environmental variable is identified, the testing environment (number of loaded mods, calm testing environment definition, use of or creation of new BRIDGE capabilities to remove the influences) should be explored and exercised if possible. There will likely always be some residual testing influences, but let's get VERY creative in trying to remove them to preserve sanity and not burn all our tokens on repeating large expensive test suites with low yields even if the mod is 100% correct. Push back and question card me, expand this prompt to make it excellent. This is a VITAL upgrade, immediate priority, work with me Fable right now! Then we send it to GPT afterwards for deep review, skeptical breakdown, and fix improvements, and finally work together on the final token-efficient simple bearing language version.

Card answer 1, how kind B is judged:

> For Tests of Type A (intended for capabilities that should be reliable and reliably testable) you would not use "4 of 5" form of success. That would be inappropriate. If there are environmental variables that frequently confound an otherwise reliable capability (such as requiring certain pawns present in specific onfigurations), it becomes test type B where traced success & failures is important evidence but ANY demonstration of success may be as good as we're going to get. Then tuning the X out of Y numbers becomes art and resource balancing. Please push back if this doesn't seem appropriate or make sense or address your concern.

Card answer 2, kind C and the pass:

> Intermittent bugs will be a transient hunt mode, usually by a test pilot, but possibly temporarily inserted into passing pipeline tests while they are still being hunted during the development (after having been seen once or twice). They are never intended to be left on for the final testing suite. As you say, once their source is detected, they may be converted into specific forced configurations (hopefully even deterministic at that point) to ensure it does not reoccur, but after the fix that requires proof of likely re-emergence (you don't want your basic acceptance suite turning into a littany of everything that was once wrong, it's too expensive for live game testing). Offline tests may be more receptive to holding a large number of "once wrong" recursion testing. If the bug is never or exceptionally rarely reproducable and cannot be transformed into a forced test, it is dropped from any mod acceptance testing to preserve efficiency. This should become a broad principle in our game: the Principle of Impactful Evidence: due to fixed resources, we must allocate testing only to what is likely to provide future value, never comprehensive coverage for its own sake, and that equation will change over time given evolving knowledge of an evolving system. [Please help me restate this answer before you record it verbatim, we want this to be superbly stated for the best impact on the game. That principle should be placed at the highest level within this project, I believe you made a place for that guidance recently?]

Card answer 3, who tags:

> It's not as hard as you say. Of course the User or the Conductor have authority to do this. If environmental variables beyond our control can be identified that preclude a Kind A test, even after sincere attempts to control them, it is reasonable to proceed to kind B testing. There is evidence for it, not a lazy tester. The tester should have to provide evidence that type B testing is required, after a sincere attempt to control the environment otherwise fails. The Conductor or a Fable Rescue would be ideal sources for this if the tester fails to recognize it. Debugging/diagnosing a failed pass is a perfect time to recognize this in an ordinary environment. PLEASE do try to control environment and/or upgrade the BRIDGE with skills to help provide a more stable testing environment first whenever possible. That too is evidence that type B testing is required.

Card answer 4, forcing and natural runs:

> Agreed, forcing is dangerous, not simply preferred. It tests the basic, elemental capability but does not explore important configurations. Here is another Principle, this time for Debugging/testing skills in rimworld: the minimum force required for testing is optimal. Example: We are testing a raider walking over a large covered pit, but they rarely choose to walk over it in a real game. From least desirable/most elemental to most desirable/most complete: teleport raider onto middle of covered pit; pre-set raider walk path over the pit; place pit in narrow hallway without alternative route and place desired object/combatant as bait to draw them over it; place an array of covered pits entirely surrounding a natural base and allow naturally spawned raiders to find their own path across in their own time. [We will almost never be able to afford that final, natural test type due to the time and token cost of each test plus a potentially low yield due to environmental factors and other mod interactions] [Agreed that the player walkthrough can cover the most complex situations, but even still some will simply have to wait for real gameplay to discover, and that's ok. that is the "testing horizon" we can afford.]
