1. **Each proposed principle has a failure mode.**

   **1 — Physics/place:** “Same on every tile” confuses consistent rules with identical outcomes; “never asks which biome” mistakes syntax for architecture. Relevant inputs include history, populations and player settings. Counter-example: rot survives in two equally dark rooms differently because one has exhausted its nutrients. Conversely, replacing a biome check with an `isRotTerrain` check can preserve exactly the same arbitrary restriction.

   **2 — Depends/showcases/source:** Useful descriptions, poor admission criteria. They overlap, and association does not establish good gameplay. “Must be carried elsewhere” also excludes migration and deliberate cultivation. Counter-example: a venomous animal showcases venom, but that does not justify giving every colony another mandatory antidote chore; its eggs might naturally disperse beyond its native biome.

   **3 — World limits only:** Taken literally, this prohibits settings, simulation budgets and practical abstractions. It also demands ecology accomplish something players may reasonably defeat. Counter-example: roofs defeat sunlight mortality, and farming pays the Rot’s food cost. A thriving transplanted colony is then successful play, not failed containment. Decide whether you mean *prevent unaided spread* or *prohibit expansion*.

   **4 — Data/laws:** Data can encode laws, and distributions have behavior. The distinction does not establish modularity or ownership. Counter-example: a terrain definition can quietly grant biome-exclusive fire immunity; weather probabilities can prevent rain forever. Meanwhile, several biome mods independently implementing “universal” combustion produce conflicting laws.

   **5 — Every visible effect actionable:** This would remove atmosphere, ornamental variation and useful confirmation of earlier actions. Counter-example: distant dust gives the desert scale without requiring a dust-management system. The geyser halo’s defect may be that it falsely suggests a mechanical boundary; removal, visual redesign and adding mechanics are separate options. Do not invent chores to justify decoration.

2. **The missing principle is that universal mechanics must justify their combined burden.** Local consistency does not guarantee a playable or tractable planet.

   Require predictable interactions through shared concepts—heat, fuel, exposure—with explicit precedence where systems conflict. Counter-example: sunlight kills the floor while its heating loop continually regenerates it, creating oscillation or unlimited heat.

   Require discoverable causes and responses; player control over disruptive systems; a simulation budget at a stated colony scale; and ecological containment that explains unaided distribution while permitting intentional transplantation. A dozen individually attractive mechanics can collectively become unreadable, compulsory maintenance or an unacceptable tick cost. Universality alone earns none of those costs.

3. **No: “never reads `BiomeDef`” is the wrong enforcement boundary.** Honest biome checks include native spawning, map generation, weather selection, biome-specific presentation, migration of old saves, and regional environmental conditions represented by a biome because their underlying ecology is not simulated.

   That last case should be a declared, inspectable approximation. “The predator receives a magical damage bonus here” remains an arbitrary rule unless explicitly justified.

   Better test: **hold declared causal inputs constant, change biome identity, and compare behavior.** Then transplant the entity into a real foreign map to catch initialization and registration failures. Review whether every difference has a defensible cause. A lint can flag code for review; it cannot establish universality.

4. **Separate intended semantics from demonstrated support.** The draft’s binary choice is false: avoiding biome checks proves little, while validating every combination is unnecessary.

   The cheapest credible policy is:

   - For each mechanic, declare prerequisites, causal inputs, installation requirements and expected inactive behavior.
   - Test its core behavior independently of biome identity.
   - Run one repeatable foreign-biome transplant scenario, covering activation, ordinary operation and ecological failure or dormancy.
   - Exercise representative environmental boundaries and specifically identified dangerous interactions; expand coverage after defects.
   - Check performance on a representative demanding colony, with an agreed budget.

   Maintain a small support ledger: tested environments, known limitations, unresolved failures. Vanilla and third-party integration can remain best effort.

   “Universal” need not mean continuously active: exposure needs sunlight; a floor needs installation and food. Nor does it determine defaults. Optional systems and their dependencies need explicit activation policy. Universal design without **any** foreign-map validation remains an aspiration, not an evidenced compatibility claim.

5. **The file needs decision authority and a consumption mechanism.** Merely existing at the root will not steer agents.

   Use **3–7 active entries**, with twelve an exceptional ceiling. At birth, record confirmed commitments and unresolved questions; allow no confirmed entries rather than manufacturing convictions. Retroactive interviews should test historical rulings against counter-examples, distinguish quotation from inference, and obtain confirmation.

   Each entry should contain: **stable ID; decision rule and preferred tradeoff; scope and exceptions; one honoring and one violating example; verification method; authority/provenance; review trigger.** Prefer “When X conflicts with Y, prefer X unless Z” over “We value X.” Checks may be editorial review or player observation, not necessarily automation.

   The owner approves additions, semantic changes and retirement; agents propose them. Conflicting principles require an explicit priority or owner decision. An approved exception must remain visible, with its scope and reconsideration trigger.

   Put the instruction to consult this file in the agent rules. For consequential work, agents identify applicable entries and explain exceptions in the proposal or review. Detect drift through changed behavior, repeated exceptions, counter-examples and contradicted tests—not only Design Version changes. Update examples as the project develops.

   Its distinct job is **current, cross-cutting decisions about the intended result**:

   - A **constitution** establishes authority and amendment rules.
   - A **north star** describes the desired destination.
   - A **lexicon** defines vocabulary.
   - **CLAUDE.md** directs agent conduct and workflow.
   - **ADRs** preserve particular decisions and their rationale.

   Link these documents; avoid copying their content into competing authorities.

   The strongest argument against the file is that it becomes a second, stale specification whose confident language makes agents enforce yesterday’s preferences against today’s evidence. Mandatory files also encourage fabricated principles. Where existing documentation already performs this function, the root file should point to that canonical material instead of duplicating it.

6. **Three replacement sentences:**

   **For principle 1:** “Given the same relevant conditions and state, an installed mechanic behaves consistently across biomes; biome identity alone does not change its rules.”

   **For principle 3:** “Native distribution and unaided spread should follow discoverable ecological constraints that remain valid after transplantation and that players may deliberately overcome.”

   **For principle 5:** “Visuals that imply gameplay consequences must communicate them truthfully and legibly; decorative atmosphere need not create a mechanic.”
