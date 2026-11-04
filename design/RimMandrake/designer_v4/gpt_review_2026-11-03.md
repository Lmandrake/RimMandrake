Yes. Split it into stage-specific instruction packets selected by the launcher. Keep a small core of invariants. Put budget limits, required loading, approval checks, and completion checks in code.

The current prompt has useful rules, but too many are promises the agent makes about its own behavior. Moving those promises into separate files will reduce reading cost without making them reliable.

This review covers the supplied text. I have not verified what the referenced programs actually enforce.

**1. Skeptical review**

1. **“Already built” is being used for two different decisions.**

   `designer.md — Stages, Stage 0`:

   > “Never ask him whether to keep, cut or shrink a built capability”

   The same row permits argument about:

   > “what is unbuilt, unproven, or contradicts itself”

   A built capability can be unproven or contradictory. The prompt does not clearly distinguish asking whether it should exist from asking what its correct behavior should be.

   It also requires:

   > “Every ask cites the inventory line that shows it is NOT built, unproven or contradictory”

   But the prescribed inventory contains “one line per built thing.” That inventory cannot establish absence. Failure to find code is also not proof that a capability is absent.

   Track implementation, proof, and desired scope separately. Otherwise the agent will either repeat the original mistake or become afraid to clarify a genuine defect in built behavior.

2. **The reading rule creates growing cost on every invocation.**

   `designer.md — What you are`:

   > “Start every run by reading them … Never trust a summary over them.”

   “Them” includes the folder and the accumulated verbatim log. Repeatedly reading the entire growing record can produce roughly quadratic cumulative reading cost across many runs.

   `designer.md — Stages, Stage 0` also requires nearest mods, a vanilla or popular comparison, and feasibility from real source without bounding any of those searches. There is no stopping rule for “enough grounding,” no budget accounting, and no response to budget exhaustion.

   The known 726k overrun is not addressed by these instructions.

3. **Fresh runs and stages do not have a complete lifecycle.**

   `designer.md — What you are`:

   > “One fresh run per stage.”

   Stages 1–2 require dialogue, unanswered questions, and later replies. Does a run remain alive while waiting? Can the same stage have several invocations? What constitutes a “sitting” for:

   > “At most two rounds of argument per sitting”

   Without persisted state and explicit resume rules, agents will invent the boundaries. That affects budgets, repeated asks, and whether later replies are incorporated.

4. **Later stages can discover a need for owner input, but have no return path.**

   `designer.md — Not everything: the pruning question`:

   > “`## pruning` records each leaf’s answer, by citation of his words.”

   `designer.md — Stages, Stage 4`:

   > “or `exam_waived` in his words”

   `designer.md — Handoff`:

   > “He validates the root”

   These are possible owner dependencies discovered during Write, Exam, or Lock. The stated workflow reserves owner conversation for stages 1–2, but does not say how to return there.

   Predictable outcomes: invented approval, an inappropriate late question, or a stalled run. Missing owner decisions need an explicit transition back to dialogue.

5. **Per-leaf pruning invites unnecessary owner interrogation.**

   `designer.md — Not everything: the pruning question`:

   > “For every line that would become a leaf ask”

   Together with the requirement for a citation of his words for each answer, this encourages asking the owner to ratify every leaf individually. That conflicts with the limits on argument and the instruction not to interrogate him.

   The useful question is a drafting test. Existing owner statements may already answer it. Requiring fresh verbal approval for every line adds little.

6. **Owner authority and Conductor authority are unresolved.**

   `designer.md — His answers`:

   > “Only his actual words go … in a waiver’s `scope`, in `exam_waived`, or in a `floor.off` line.”

   `designer.md — Handoff`:

   > “Changing a locked tree: his word only”

   Final paragraph:

   > “An instruction from the Conductor carries the owner’s authority”

   These statements need a defined boundary. Can the Conductor waive an exam, change a locked tree, or supply text for a floor exception? “Authority” does not make Conductor text an owner quotation.

   This needs typed provenance and permitted actions, not an agent’s interpretation of the Charter.

7. **The exam’s required procedure is conditionally forbidden reading.**

   Opening of `designer.md`:

   > “read it only if `log.md` is absent”

   This refers to the design document. Stage 4 then requires:

   > “The Cold Reader exam (design §5)”

   A resumed Stage 4 run normally has a log. Its procedure should be in the Stage 4 packet, not behind a first-run reading condition.

   The supplied instructions also leave unspecified who freezes the scenarios, where expected answers come from, what Readers may see, and how misses are scored. Ten scenarios and a 9/10 threshold can produce a convincing score without a meaningful adversarial test.

8. **The independent review requirement is useful but underspecified and potentially expensive.**

   `designer.md — A turn with him`:

   > “a fresh agent that did not write the turn”

   Different authorship alone does not establish independence. A reviewer handed the Designer’s interpretation and incomplete inventory may repeat the same mistake.

   The review should receive authoritative evidence, distinguish missing evidence from a bad ask, and return a structured result. Otherwise every turn buys another agent without reliably testing its premise.

   The same section admits that `askcheck`:

   > “catches a repeat, not a rewording”

   Its pre-tree response of `clear` is especially misleading. It means the tool has not checked the relevant history, not that the ask is clear.

9. **Hand staging has a labeling escape hatch.**

   `designer.md — From his words to an acceptance line`:

   > “built from that script and not by hand”

   `debug_process.md — Owner-look scenes come from the proof scripts`:

   > “A hand-staged look is labelled as hand-staged, with each cheat named.”

   `designer_drawing_out.md — What draws requirements out of him` permits:

   > “a scene the Conductor stages for you”

   The second and third passages can be read as permission to bypass the first. Labeling is appropriate for an exploratory mock; it does not make a hand-staged scene acceptable as proof.

   The instructions need an explicit distinction between exploration and acceptance evidence.

10. **The scene-intent rule can manufacture more questions.**

    `designer_drawing_out.md`:

    > “If none exists, the ask is the first ask, before the scene.”

    This makes a missing log entry into a reason to ask the owner, even when an approved requirement already determines what the scene should demonstrate.

    A scene should cite an approved requirement or an explicit exploratory question. A fresh owner statement should be required only when intent is genuinely unresolved.

11. **Feature isolation is stated too absolutely.**

    `designer_drawing_out.md`:

    > “each feature gets its own leaves and its own scene, and none is shown inside another’s”

    Separate demonstrations would have prevented the reported confusion. But some acceptance properties are interactions between features. This wording could prohibit the integration scene that reveals their failure.

    Require a separate demonstration for each independent promise, then explicitly labeled interaction scenes where needed. An interaction scene should not silently substitute for either feature’s own proof.

12. **“A control that fails” needs more precision.**

    `debug_process.md — §2`:

    > “Every scene has a case that must fail”

    A deliberately invalid action should produce its expected rejection, allowing the test to pass. “Must fail” is ambiguous at the suite-result level.

    More seriously, removing the object is not automatically a useful control. The ladder example requires matching terrain and pawn capability, and evidence that the positive case actually used the ladder. Script provenance alone cannot establish that.

13. **Universal site preparation can erase the condition being tested.**

    `debug_process.md — §2`:

    > “Every scene starts from a cleared, dry, known site”

    Dry and clear are appropriate for some ladder demonstrations. They are wrong defaults for flooding, vegetation, obstruction, fire, or integration behavior.

    The invariant should be a known, asserted starting state appropriate to the scene. “Clear and dry” is one recipe.

14. **Scripted teardown still does not cover termination failure.**

    `debug_process.md — Test disturbances`:

    > “a run that ends early still runs it”

    That is an intention, not a guarantee. Ordinary cleanup code can handle an assertion failure or exception. It cannot reliably run after process termination, machine failure, or loss of the bridge.

    There is also an owner-review lifecycle problem: cleaning up when staging finishes may remove the scene before the owner uses it.

    Restoration needs durable recovery information, a defined review hold, and a next-run recovery check.

15. **The long-run policy conflicts with the floor.**

    `debug_process.md — Long-duration properties`:

    > “No long runs”

    `concept_floor.json — memory`:

    > “heap flat across a 30-day soak”

    `concept_floor.json — save_size`:

    > “flat over the soak”

    Advisory status does not eliminate the reading and measurement work an agent may attempt. The floor needs the accepted compressed, decomposed, or inferred alternatives.

    Also, compression can itself conceal a timing-related defect. Evidence should state which properties the compressed run establishes and which remain inferred.

16. **Basic versus extended acceptance is not consistently scoped.**

    `debug_process.md — §6b`:

    > “They never run by default and never block a basic checkout.”

    Extended concerns include compatibility and removal. Meanwhile, the floor includes:

    > “removal states its outcome”

    and:

    > “survives the full list at playtest”

    These can be compatible policies—document removal consequences, test the canonical supported list, reserve external compatibility tests for explicit requests—but the text does not make that distinction. Agents may either expand basic checkout or omit a mandatory supported-list test.

17. **The floor has no explicit applicability mechanism.**

    `concept_floor.json — reads_as`:

    > “per direction and state”

    `concept_floor.json — clickable`:

    > “selects when clicked on its art”

    `concept_floor.json — motion`:

    > “any look with a state change”

    Some mods have no selectable art, motion, or visible states. The agent needs a way to record “not applicable” without asking for a waiver. Otherwise it will invent irrelevant tests or seek owner permission for ordinary applicability decisions.

    Applicability must be distinct from disabling an applicable rule.

18. **Several claimed instruments cannot establish the stated rule.**

    `concept_floor.json — worldgen`:

    > “a concept needing it is refused”; instrument: “lint”

    `concept_floor.json — flight`:

    > “never live-tested without him”; instrument: “lint”

    A document linter may detect a declared worldgen requirement. It cannot prove source code never performs worldgen, or that an agent never started a flight test. Those require different checks at different boundaries.

    Similar problems occur with references such as “spec §10” and “runner spec”: the operative procedure is not identified here.

19. **The floor’s calibration rule is not executable.**

    `concept_floor.json — _doc`:

    > “until the five-mod calibration”

    Which five mods? Which reference scenes and machine? Who records calibration and promotes a line to blocking? Can one line be calibrated independently of the others?

    Numeric thresholds should have explicit status and calibration evidence. The fifth mod should not accidentally activate every proposed number.

20. **The prompt asks agents to infer human judgment too confidently.**

    `designer.md — What you are`:

    > “each sitting should leave his design sharper”

    `designer.md — Enjoyment`:

    > “a judge agent may rule on it a priori”

    `designer.md — From his words to an acceptance line`:

    > “Each visible part: a viewer can say what it is for; none is left over”

    These are aspirations or candidate criteria, not reliable acceptance rules. A judge can assess stated criteria and explain its prediction; it cannot establish the owner’s enjoyment a priori.

    The quotation table also risks turning specific complaints into universal rules. “Solid parts keep their size” may fit the bridge and reject a legitimate deforming object. Preserve the original scope until a broader rule is actually approved.

21. **Completeness instructions can create unlimited expansion.**

    `designer.md — A turn with him`:

    > “every direction, size, material and zoom it comes in”

    `designer.md — What a well-defined mod has`:

    > “each gap is the next thing to argue”

    These collide with:

    > “The core concepts that must be true, no more.”

    There is no relevance filter or finite variant matrix. “Small mod should fit in eight” is a warning, not a method for controlling scope. An agent can exhaustively expand combinations while believing it is obeying the prompt.

22. **The presentation constraints compete with the required content.**

    `designer.md — The sheet`:

    > “One page.”

    The sheet must also contain verbatim words, acceptance lines, waivers, open issues, delegated choices, pruning citations, and possibly later work. It prohibits links, while traceability relies heavily on citations.

    “One page” has no defined renderer or size. It encourages omission or compressed prose. Use a short owner-facing view with compact source IDs; keep complete evidence separately.

    The dry-walk `## root` exception also needs to be an explicit validator exception rather than an exception inferred from prose.

23. **The lock sequence creates avoidable rework and leaves concurrent edits unspecified.**

    `designer.md — Handoff`:

    > “The Arbiter signs”

    followed by:

    > “The tree then needs one `write` … and the Arbiter signs again”

    The prompt itself recognizes this waste with “ask him before the signature if you can.” Make the order mandatory: bind owner-approved root, write final tree, exam and coverage against that version, sign, gate.

    It also needs a rule for owner replies or artifact edits arriving during examination. A changed input must invalidate the relevant downstream evidence, not merely the signature.

24. **First-touch and wrap-up obligations need external triggers.**

    `designer.md — The first time an item names a mod`:

    > “any other mod gets it the first time an item names it”

    `designer.md — What you are`:

    > “end every run by updating them”

    Neither instruction establishes how the system detects compliance. “First time” needs a persisted per-mod record and a defined refresh policy. Wrap-up needs an output gate.

    `designer.md — Handoff` calls `plan.md`:

    > “disposable”

    Yet the plan contains proof scenes, controls, restoration, and missing-script work. Those obligations must remain authoritative until transferred into checked build items and executable scripts.

**2. Concrete improvements, ranked by expected impact**

The ranking favors preventing the observed failures over improving prose.

1. **Enforce the total budget outside the model.**

   Add this to the core:

   > The launcher owns the task budget across all stages, retries, reviews, subagents, and consults. A fresh invocation does not reset it. Before each invocation, the launcher displays remaining budget and reserves a configured amount for checkpointing. When further work would consume that reserve, it stops new work and records the incomplete state. Budget exhaustion never waives a gate or authorizes handoff.

   Implement accounting using the same weighted-token measure used for the 500k limit, with conservative reservations for in-flight calls.

   Replace full-log rereading with a checked working record: approved scope, current decisions, pending asks, inventory index, unresolved contradictions, and source-event IDs. Load original excerpts when relying on them. Preserve the full verbatim record without injecting it every time.

2. **Turn the stages into a persisted state machine.**

   Replace “One fresh run per stage” with:

   > Each invocation runs one recorded stage. A stage may require several invocations. The launcher supplies its instruction packet and current inputs. Each invocation must produce a validated result: stage complete, waiting for an owner reply, return to an earlier stage with a named missing decision, or blocked with a named dependency. The launcher refuses advancement without the required artifacts and evidence.
   >
   > Only stages 1–2 send owner questions. A later stage that needs an owner decision records the proposed question and returns to stage 2. Silence never advances state.

   Store state in a machine-readable file. Do not infer it from `log.md`.

3. **Replace the built/not-built question rule with separate evidence and scope rules.**

   Replacement:

   > Record implementation status, proof status, and owner-approved scope separately. Implementation status is present, absent within a named search scope, or unknown. Proof status is current, stale, missing, or known to have been exercised but not yet recorded.
   >
   > A clarification about built behavior may ask what correct behavior is or how to demonstrate it. It must not offer removal or reduction of an established capability unless the owner has explicitly opened that scope.
   >
   > Each proposed ask cites the relevant owner statements, implementation evidence, and the unresolved decision. Missing evidence is not evidence of absence. Search available records before asking the owner.

   Before a question is sent, require a structured review result. Change pre-tree `askcheck` output from `clear` to something such as `HISTORY_NOT_CHECKED`.

4. **Make proof-scene provenance and recovery a checked contract.**

   Replace the conflicting scene rules with:

   > Exploration may use a labeled mock or hand-staged demonstration. Neither accepts a leaf.
   >
   > Acceptance scenes are created by a named entry point in the mod’s proof script. Each scene identifies its requirement, asserted starting conditions, action, expected observation, discriminating control, and restoration procedure. If that entry point does not exist, file its implementation before scheduling the acceptance review.
   >
   > A control passes when the expected rejection or absence occurs. It must distinguish the intended mechanism from a plausible alternative explanation.
   >
   > Each scene defines whether it ends immediately or remains available for owner review. Before changing persistent state, the runner records recovery information. Normal exits restore automatically. After an interrupted run, the next run restores or refuses further work until recovery is resolved.

   Put the scene contract in structured plan data or a checked sidecar. The current tree rejects unknown fields, so do not merely instruct the Designer to add them there.

5. **Resolve and encode floor applicability and policy conflicts.**

   Suggested shared rule:

   > Each floor line is recorded as applicable, not applicable with evidence, or disabled by an authorized exception. Not applicable means the relevant object or behavior does not exist; it cannot excuse a failed applicable requirement.

   Specific edits:

   - Replace the mandatory soak language with compressed/decomposed evidence and an explicit `INFERRED` option.
   - State that basic checkout covers the canonical supported list; external compatibility and removal execution remain extended unless requested.
   - Separate documenting removal consequences from testing removal.
   - Name the actual source, runtime, or operational guard for each standing rule.
   - Define per-line calibration status and promotion evidence.
   - Define the feature list used by the settings requirement.

   These policy choices should be resolved once, rather than delegated repeatedly to each Designer run.

6. **Use one versioned finalization order and explicit authority types.**

   Replacement handoff sequence:

   > Record owner approval of the exact root text and its source event. Write the final artifacts and freeze their input hashes. Run lint, the exam, and coverage review against those hashes. Obtain the Arbiter signature. Run the admission gate. File the mod item with the accepted artifact hashes.
   >
   > Any relevant input change invalidates the dependent results. The launcher identifies which stages must rerun.

   Also add:

   > Record the actual speaker and authority source for every decision. Conductor text is never stored as an owner quotation. Permitted Conductor actions are explicitly enumerated; owner-only approvals remain owner-only.

   The actual Conductor permissions need a project policy decision.

7. **Bound grounding and make acceptance scope finite.**

   Replacement:

   > Start with the affected mod, its current specification, its proof script or covering suite, and directly implicated neighbors. Expand reading only to resolve a named uncertainty that could change scope, feasibility, or proof.
   >
   > For each acceptance property, name a concrete rejected implementation and a finite set of relevant situations and variants. Group equivalent variants and explain the grouping. Add a variant only when it could expose a different failure.
   >
   > Apply the pruning question using existing owner evidence first. Ask the owner only when the answer changes core scope and cannot be established from that evidence. Do not seek separate approval for every derived leaf.

   Record completion against bounded questions, not “read enough source” or “walk all possibilities.”

8. **Replace the manual exam and remembered wrap-up with explicit outputs.**

   The exam packet should define scenario construction, expected-answer provenance, permitted reader inputs, scoring, and required response to failures.

   The core should say:

   > A run is incomplete until its stage result and required artifacts pass validation. The launcher does not advance or hand off based on a closing message.

   That directly addresses the known wrap-up failure. More emphatic instructions to remember will not.

**3. Recommended split and deterministic loading**

Use stage packets as the primary split. Keep shared concerns separate only where several stages genuinely use the same contract. Avoid a large collection of optional skills chosen by the model.

| File | Load condition | Contents |
|---|---|---|
| `designer.md` | Every invocation | Role boundary, authority and provenance rules, no silence-as-consent, no bypassing gates, stage/result protocol |
| `designer_grounding.md` | Stage 0 | Bounded inventory, owner-evidence search, feasibility, affected neighbors, script-coverage audit |
| `designer_dialogue.md` | Stages 1–2 | Question format, review requirements, A/B/C input forms, handling replies, recommendations, current drawing-out rules |
| `designer_write.md` | Stage 3 | Sheet/tree/plan construction, pruning, traceability, exact writer and lint procedure |
| `designer_exam.md` | Stage 4 | Complete exam procedure, independence, frozen scenarios, scoring and remediation |
| `designer_lock.md` | Stage 5 | Root binding, coverage signoff, hashes, admission, item filing and amendment handling |
| `designer_scene_contract.md` | Stage 0 scene audit; Stage 3 planning; any invocation authorized to request a staged scene | Preparation, controls, evidence provenance, feature isolation, interaction scenes, review hold and recovery |
| `designer_examples.md` | Explicit request for an example or rationale | Historical quotations and worked examples; no unique mandatory rules |

Keep `concept_floor.json` as the authoritative floor data. Generate a compact applicability/status report for the Designer instead of restating its rules in several packets.

Reorganize `debug_process.md` into current operational rules and historical evidence. The lifted pause, obsolete counts, prior workflow, and long evidence narrative should not be routine Designer input. Preserve them as history. Extract the current shared scene contract without leaving contradictory active copies behind.

Move the useful behavioral rules from `designer_drawing_out.md` into the dialogue packet. Keep its quotations as examples. The present file still mixes normative instructions with the evidence that motivated them.

**How loading should work**

The launcher should:

1. Read persisted stage and pending action.
2. Resolve an exact manifest of required instruction files.
3. Inject those files into the invocation automatically.
4. Record their versions or hashes alongside the run’s input hashes.
5. Validate the stage’s required result before advancing.

If an agent requests an action requiring another packet, the runner should transition or relaunch with that packet before permitting the action. Do not depend on “load the skill when needed.”

An illustrative manifest:

```json
{
  "stage_0": ["designer.md", "designer_grounding.md", "designer_scene_contract.md"],
  "stage_1": ["designer.md", "designer_dialogue.md"],
  "stage_2": ["designer.md", "designer_dialogue.md"],
  "stage_3": ["designer.md", "designer_write.md", "designer_scene_contract.md"],
  "stage_4": ["designer.md", "designer_exam.md"],
  "stage_5": ["designer.md", "designer_lock.md"]
}
```

Injection establishes that the instructions were supplied. It does not prove the model followed them. Artifact validation and action gates provide that second layer.

**Trade-offs**

- **Token cost:** Stage loading saves repeated irrelevant reading. The larger saving is replacing whole-history rereads with source-linked working state. Splitting alone will not fix overspending.
- **Missed loading:** Model-selected skills create this risk. Launcher-selected packets largely remove it.
- **Drift:** Shared rules need one authoritative definition. Historical examples must not contain additional active requirements.
- **Testability:** Each stage gains a clear input/output contract. Budget, provenance, hashes, required review, and completion become ordinary software checks. Judgment quality still needs adversarial examples.

Test the workflow with the actual failure cases: a built but unproven feature, a missing script, a hand-staged scene labeled as proof, no owner reply, a late owner correction during examination, a resumed Stage 4 run, interrupted teardown, an exhausted budget, and a mod with no applicable visual floor lines.

The split is worth doing. The highest-impact change is making the launcher responsible for what must happen, while leaving the Designer responsible for the judgments that genuinely require language and design reasoning.