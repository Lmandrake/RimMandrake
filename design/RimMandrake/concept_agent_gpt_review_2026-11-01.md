# Skeptical external review of the concept agent design (verbatim; not applied; the Conductor judges it)

The central weakness: this design can certify that agents agree about a summary while missing the experience that makes the owner reject the mod.

I checked only the two supplied texts. The binding `RELENTLESS_AGENT.md`, referenced policies, standing rulings, implementation, reported measurements, and historical examples are **unverified**.

1. **The Control result is manufactured by scenario selection.**

   **Flaw:** §5 selects at least six scenarios where Readers and Control disagree, then requires Readers to score at least 9/10. Those conditions already guarantee that Readers beat Control by **at least four points**: among the six disagreements, at most one can favor Control, while at least five favor Readers. The required three-point advantage adds no test whatsoever.

   **Concrete failure:** A sheet passes, and the system reports that it demonstrated information gain over the initial message. That gain was largely built into which questions survived selection. Conversely, an unusually clear initial message can make the exam impossible to assemble: there may be fewer than six disagreements, despite an excellent contract.

   Ten selected scenarios also do not justify the stated general miss-rate interpretation. The approximately 26% bound assumes ten independent, representative trials with zero misses; these are deliberately selected, correlated, model-generated cases. The actual passing score can include a miss.

   **Cheapest fix/test:** Remove the disagreement quota. Freeze the scored scenarios before seeing Reader and Control predictions; use disagreements separately as diagnostic questions. Treat a strong Control result as evidence that little elaboration was needed, rather than automatic invalidation.

2. **The exam tests the sheet’s world, including its omissions.**

   **Flaw:** The Examiner receives only the sheet. Readers receive the sheet and tree. If the debate omitted an important dimension, the exam generator has no independent obligation to discover it. Agreement demonstrates consistent interpretation of the supplied account; it does not demonstrate that the account captures the owner’s concept.

   Reader disagreement can indicate ambiguity, but Reader agreement cannot establish its absence. Shared assumptions can produce unanimous wrong answers.

   **Concrete failure:** Everyone agrees that the spill looks right, conserves litres, and gets cleaned. Nobody tests whether repeated spilling makes ordinary colony management intolerable, because that interaction never entered the sheet. The owner rejects the completed mod after playing it; the exam remains an immaculate 10/10.

   Storyboards worsen this limitation when timing, frequency, agency, or interruption is the experience. A three-frame strip can show a fall without establishing whether it feels like falling.

   **Cheapest fix/test:** Reserve a few challenges sourced independently from the summary: raw owner statements, comparable rejected behavior, or an adversary explicitly looking for missing dimensions. Use the already-permitted scratch spike for a core experience that pictures cannot settle. Predeclare which scenarios exercise core lines.

3. **Waivers create permanent immunity without resolving overlapping obligations.**

   **Flaw:** “The builder may do anything there” is stronger than “the owner does not care about this property.” The design makes a waiver absolute and permanent, while leaving its intersection with other requirements to informal interpretation.

   The prohibition on raising it again also blocks legitimate clarification when consequences change. Treating every such clarification as pestering confuses repeating a question with discovering a dependency.

   **Concrete failure:** The owner waives stain appearance on constructed floors. A floor stain becomes visually indistinguishable from standing water. The Marker now has an appearance waiver and a binding “must not read as standing water” criterion covering the same pixels. Either interpretation can be defended from the text.

   A second failure is cumulative: several individually irrelevant choices combine into a rejected experience, but their defects have been excluded from both escape accounting and future questioning.

   **Cheapest fix/test:** State explicitly that a waiver removes only its named obligation and never grants an exception to another leaf. Require a conflict check when recording it. Permit a narrowly framed dependency clarification when satisfying the remaining contract becomes impossible; keep the original preference settled.

4. **The finish line can acquire new owner requirements through “tightening.”**

   **Flaw:** Both designs allow findings to add clauses under existing leaves immediately, without asking him. Both also say new concepts must return upstream. Nothing operationally distinguishes those cases.

   A clause’s location in JSON does not establish that the owner already required it.

   **Concrete failure:** The owner explicitly accepts cleaning as the cost of careless hoses. Later, a Marker adds “thirty spilling hoses must not create a cleaning backlog” beneath `spill_gets_cleaned`, calling it a clarification. The worker must now redesign behavior the owner already chose, and previous PASSes are void.

   The reverse is equally dangerous: a real missing requirement can be called a “new concept” and bounced upstream indefinitely. This moves scope disputes into the build process.

   **Cheapest fix/test:** Require every tightening to cite the existing obligation it enforces and check for conflicts with rulings and waivers. An addition that changes the acceptable behavior set beyond that obligation returns upstream. Test this with deliberately disguised scope additions.

5. **The handoff contains actual contract mismatches.**

   **Flaw:** The supplied documents do not yet describe one consistent acceptance artifact.

   | Mismatch | Concrete failure | Cheapest correction |
   |---|---|---|
   | Concept §7 permits advisory `does` lines outside the tree; Gate A requires every `does` line to map to a leaf, floor line, or waiver. | A deliberately pruned, nonbinding intention either fails lint or gets falsely promoted to a requirement. | Give advisory intentions an explicit representation and lint rule. |
   | Relentless §4 requires a whole-mod **walk leaf**; the Concept tree specification and worked example omit it. | Individually passing leaves arrive without the required integrated finish test. | Make the walk leaf an explicit intake obligation. |
   | Concept §8 inherits a floor by hash; Relentless §3 requires mechanical constraints to be leaves with instruments, guards, and receipts. | A floor reference passes upstream but cannot satisfy downstream evidence checks. | Define how floor entries expand into versioned leaves and receipts. |
   | Concept assigns `budget` to a program; Relentless §10 assigns its proposal to Producer. | Each side expects the other to supply a required field. | Resolve the acknowledged ownership conflict in the shared schema. |
   | Setter discovers instrument needs but cannot add criteria; missing instruments require their own leaves. | An instrument requirement discovered during binding forces an upstream tree revision, possibly after root/hash approval. | Specify that return path and which approvals become stale. |

   There is also a shared timing ambiguity: intake requires all eight fields, including supervisor-supplied `red`, before a Build lease, while guard red is produced on a candidate later. Distinguish a required red specification from the later receipt.

   **Cheapest overall test:** Run the worked example through a schema-level handoff, including floor expansion, Setter refusal, instrument creation, walk leaf, and receipt lifecycle. The example currently demonstrates neither full contract completeness nor successful intake.

6. **The owner-time saving is asserted without a denominator.**

   **Flaw:** “The agent does the thinking and he does the ruling” does not make ruling cheap. The owner still has to reconstruct context, inspect pictures, understand tradeoffs, answer scenarios, validate the root, and inspect first GREEN.

   “No cost to him” during agent-only retries ignores elapsed delay and the cost of returning to a concept later.

   **Concrete failure:** A concept consumes several proposal rounds, image approvals, ten exam verdicts, another twenty verdicts across two retakes, root validation, and the first live look. The design calls these “minutes” without comparing them with current design time plus avoided rework. The phone-sized sheet may merely compress the decisions until they become unreliable.

   **Cheapest fix/test:** Measure active owner minutes, number of interruptions, elapsed time, retakes, and later correction time. Compare total cost through the owner’s first accepted build with the present process. Until then, “lower owner burden” is **unverified**, not a design property.

7. **The mechanical floor is an uncalibrated benchmark suite presented as a default contract.**

   **Flaw:** The numbers lack a stated workload distribution, sampling window, attribution method, noise policy, and aggregate resource budget. Naming a machine and reference scene does not supply those.

   At the proposed busy allowance, twenty mods each consuming 1 ms per tick would exceed the document’s entire 16.67 ms tick budget. Individually passing limits do not compose.

   **Concrete failures:**

   - A genuine intermittent 125 ms tick disappears on rerun and is discounted as noise.
   - A bounded but enormous allocation passes “no unbounded growth”; legitimate state growth fails “heap flat.”
   - A mod passes the minimal scene and becomes expensive under interacting colony behavior.
   - A save loads without errors while silently losing meaningful state.
   - Texture usage is counted in MB but has no limit.
   - “Click to visible response” passes because a cosmetic acknowledgment appears while the requested action remains delayed.

   Important missing candidates include save-time cost, preservation of existing save state, burst allocations/GC effects, scaling with feature count, and interaction workloads. Which belong as universal gates remains **unverified**.

   Naming, worldgen policy, visual quality, and resource consumption also need different enforcement semantics; a single “every constraint has number, unit, machine” rule cannot sensibly cover them all.

   **Cheapest fix/test:** Run the proposed five-mod calibration before making numerical defaults blocking. Specify workload size, observation window, noise treatment, and aggregate headroom. Keep applicable standing rulings binding independently of whether benchmark numbers have been calibrated.

8. **B is plausible, but the comparison does not establish that a new role is necessary.**

   **Flaw:** The design conflates three choices: who talks to the owner, which workflow runs, and whether its executor may later build the item.

   A named role does not enforce separation. A skill can enforce it through item-level permissions. “It never builds” also does not remove the incentive to finish its own debate and pass its own exit test.

   **Concrete failure:** The new Concept role is optimized for producing lockable sheets, shares the same assumptions as its reviewers, and rushes ambiguous choices into delegated decisions. The claimed conflict is still present, merely attached to a different deliverable.

   **Cheapest fix/test:** Keep the on-demand workflow, but enforce non-builder identity per item rather than relying on role prose. Measure whether Conductor actually suffers context or time costs before maintaining a separate role indefinitely.

   Giving the job to Producer **as described here** is a bad fit because of its communication and launch rules. Whether those rules exist and are immutable is **unverified**. Token blindness is not a decisive argument once budget calculation is assigned to a program.

9. **The pruning question mistakes individual necessity for collective sufficiency.**

   **Flaw:** “Would you reject it if only this were false?” discards properties that matter in combination. It also assumes every important experience can be decomposed into independently decisive leaves.

   **Concrete failure:** One extra click, one delayed response, one distracting effect, and one awkward recovery action are each tolerable alone. Together they make the feature irritating enough to disable. All four get pruned because none individually warrants rejection.

   The suggested 5–12-leaf target then pressures the agent to split a coherent concept—or hide obligations inside broad leaves—rather than represent its actual acceptance conditions.

   **Cheapest fix/test:** Apply the pruning question to coherent bundles as well as individual details. Make the required walk leaf test accumulated friction and interactions. Treat leaf count as a workload observation, not evidence that the concept is defective.

10. **The back-test is contaminated, and the rule-retirement logic mistakes silence for evidence.**

   **Flaw:** The named historical test is the failure that inspired the design, and the expected answer is supplied explicitly: reach `pit_reads_as_hole`. An agent playing the owner from historical fragments cannot recreate the owner’s unrecorded preferences.

   **Concrete failure:** The back-test discovers exactly the advertised missing criterion and “earns” a live sitting without showing that it can discover a different omission.

   Separately, removing floor lines after ten mods with no catches rewards preventive rules for disappearing. Zero catches can mean the rule prevented defects, the instruments missed them, or those mods never exercised it.

   **Cheapest fix/test:** Treat the Pit as a regression fixture, not validation. Use another historical rejection with the decisive later evidence withheld. Retire rules based on applicability and removal evidence, not a raw count of uneventful mods.

I would cut the Control score gap and disagreement quota; mandatory storyboards for every exam scenario; the absolute ban on waiver clarification; the 5–12-leaf pressure; and automatic rule retirement after ten quiet mods. I would postpone the exam script and separate-role machinery until one manually run concept demonstrates a consistent downstream handoff and measured value for the owner’s time.

**Strongest attack 1:** The Control comparison is rigged by construction: six selected disagreements plus a 9/10 Reader score guarantee a larger advantage than the required threshold. It adds ceremony and a claim of validation without adding an independent test.

**Strongest attack 2:** The exam asks agents to invent and answer questions inside the same summary whose omissions it supposedly detects. A completely missing experience can survive every gate, leaving the owner to discover the wrong mod at first GREEN—the exact failure this agent exists to prevent.