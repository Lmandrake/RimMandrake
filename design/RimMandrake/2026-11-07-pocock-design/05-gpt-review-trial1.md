**The tests are deterministic and token-free to execute; keeping them useful is recurring engineering work.** The overnight break directly weakens the claim that this particular approach is cheap.

1. **The central finding holds, within its scope.** Projects that compile only kernels cannot execute caller behavior. The static checks offer limited exceptions, so “structurally blind” should mean *behaviorally blind*, not incapable of detecting any caller edit.

   The reported **16/20** supports a narrower claim: these scenarios detect many argument-negation faults in this frozen worker under this fake. The batch was frozen **after scenarios were planned**, so it is not an independent holdout. Its mutants are correlated: one positive case can kill several negations of an activation gate. Thus 80% is not an estimate of real-bug detection. Also, the kernel score includes `K_THOUGHT_DROP_SPAWNED`, acknowledged to be equivalent at the actual caller; that overstates meaningful kernel coverage.

   None overturns the caller-coverage gap. They do undermine “replacement works and is cheap” as a general conclusion.

2. **There are three separate costs.**

   - **Authoring:** scenarios, fixtures, fake semantics, runner integration and validation. The minute of file creation excludes planning; the approximately $10/hour trial includes mutation research. Neither measures production adoption cost.
   - **Execution:** compile and run a small executable containing 15 assertions. No model inference or tokens are inherently required. Compilation/startup likely dominate; standalone timing was not measured. Agents reading logs or repairing failures consume tokens. Repeating the entire mutation campaign is unnecessary.
   - **Upkeep:** every new dependency can require fixture and fake changes. Today’s CS0246/CS1061 errors reveal harness incompatibility, not a gameplay regression. Loud drift prevents silent execution against an obsolete interface, but provides no behavioral coverage until repaired.

   With daily caller rewrites, **upkeep is likely to dominate**. This test is already an offline deterministic test; there is no generation step that permanently removes maintenance. Freezing its old executable would stop testing current callers.

3. **I would adopt selective scenarios, primarily led by actual failures, with proactive coverage for high-consequence rules.**

   Prefer real game **and mod types** where practical: replacing `Filth_Mark`, settings and extensions duplicates interfaces you control. Referencing `Assembly-CSharp.dll` removes some duplication, but does not establish that minimal fixtures run outside the game. Unity dependencies also require appropriate references ([Unity documentation](https://docs.unity.com/en-us/engine/6000.6/manual/scripting/compilation-and-code-reload/plug-ins/managed)); map initialization and runtime dependencies remain feasibility questions. Try one bounded pilot before migration.

   Generating fakes from usage can automate signatures, **not faithful behavior**. Radial ordering, room semantics and component initialization still need implementation and validation; blindly regenerating can merely make compilation green.

   Keep small scenarios where consequences justify maintenance. Failure-led additions have demonstrated relevance, although they necessarily miss first occurrences. Retain useful kernel tests: this scenario set demonstrably does not replace their priority coverage.

4. **Policy—four lines:**

   Add a caller scenario for each confirmed caller bug, plus selected high-consequence rules.  
   Compile current production code; prefer real dependencies and keep remaining fakes minimal.  
   Run deterministically on relevant changes; repair harness drift without weakening expectations.  
   Expand coverage only when observed benefit justifies authoring and upkeep.

   **Two-week measurement:** maintenance-inclusive engineer/agent minutes per genuine regression caught before live testing, including initial authoring and all drift repairs. Report zero catches explicitly; exclude planted mutants and harness build failures. Compare that cost with the recorded cost of diagnosing those regressions live.