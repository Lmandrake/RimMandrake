# GPT attack review of the Relentless Agent design (2026-11-01)

Verbatim answer below the rule. Not applied: the Conductor judges these findings. Run: gpt_consult.py --lockdown --effort medium, on the design, RELENTLESS_AGENT.md and relentless_rules.json. An earlier run at high effort with the research brief timed out at 520 s and gave no answer.

---

The central failure is that the design can make its records internally consistent without establishing that the accepted goal was achieved. Section 12 admits several versions of this, but admitting them does not narrow §1’s promise.

**Evidence labels:** **Text** means explicitly stated in the supplied material; **Inference** means a failure sequence I derive from it. Likelihoods are judgments about encountering the scenario, not measured rates. The research brief and live Python code were not supplied, so I cannot substantiate additional research claims or implementation behavior.

## 1. How can it report done when it isn’t?

### 1.1 Every gate passes against the wrong tree

**Text:** Sections 3–4 admit a tree through structural checks and an Arbiter coverage signature. Section 12 explicitly says a wrong tree passes all stages; coverage proves that lines map to leaves, not that the lines are right. Tooling goals need no concept debate.

**Sequence — inference:** An owner requests a cleanup tool that safely removes temporary files. The filer supplies a tree covering correct deletion and speed, omitting preservation of files reached through symlinks. Setter binds it faithfully. Build deletes valuable files through a symlink. Every stated leaf, guard, hold-out, and whole-scenario walk passes. Marker accepts because preservation was never part of the exam.

**Why the defence fails:** Hold-outs cannot reach beyond the tree (§3.3). Marker’s “too-easy contract” review (§8) offers another model’s judgment, not an independent statement of the missing requirement. The owner’s first mod look does not cover this tooling example.

**Likelihood: high.** Omitted requirements are ordinary, and the design expressly acknowledges this hole.

### 1.2 Every gate passes while the visible experience is wrong

**Text:** Sections 3 and 3.1 require an oracle and one named wrong world with a guard. Section 3.1 then claims guard red proves that the instrument reads the quantity the experience concerns.

**Sequence — inference:** A leaf requires an unmistakable disappearance animation. The oracle checks one selected frame and a despawn event. The guard removes that frame or suppresses despawning, and correctly produces red. The candidate shows the frame for an imperceptible duration, then leaves a misleading replacement sprite. Base red, guard red, visual check, hold-outs, and Marker all pass because they sample the same narrow evidence.

**Why the defence fails:** Detecting the planted wrong world proves sensitivity to that mutation. It does not prove sensitivity to other wrong experiences. A second model examining the same frames cannot observe the missing temporal experience.

**Likelihood: high.** Narrow observations are especially plausible for animation, timing, interaction, and visual salience. The first owner look can catch a conspicuous example; it does not establish coverage of later drift.

### 1.3 Stale leaves remain fresh because the dependency declaration is wrong

**Text:** Section 4 binds a leaf receipt to its dependency hash. Sections 5 and 8 hash inputs and reject stale dependencies. No supplied section establishes how complete leaf dependencies are discovered.

**Sequence — inference:** A leaf passes against a particular UI asset and script. Another leaf changes a global scaling setting, shared shader, or asset-loading rule absent from the first leaf’s dependency set. Its hash remains unchanged. The old receipt remains valid even though its screen is now wrong. A walk covering a different resolution passes.

**Why the defence fails:** Hashing accurately detects changes to included dependencies. It cannot detect an omitted dependency. A single-sha walk prevents mixing builds, but does not make the walk exhaustive.

**Likelihood: medium.** Shared configuration and indirect asset dependencies are common. The actual rate depends on dependency machinery that is not specified here.

### 1.4 The walk leaf certifies one route and misses the integration failure

**Text:** Section 4 requires “the whole scenario on one sha.” Section 12 concedes rare live behavior and long properties remain uncovered. Section 13 step 16 tests one historical Pit case.

**Sequence — inference:** Feature A works in a fresh session. Feature B works independently. The walk starts fresh, exercises A and B once, and passes. A real user loads an older save, performs B twice, then A; persistent state causes A to fail. All leaf receipts and the walk remain valid.

**Why the defence fails:** “Whole scenario” is a selected execution, not a proof over histories, saved states, configurations, or interactions. Putting every action on one sha fixes build consistency, not scenario completeness.

**Likelihood: high.** Stateful integration failures routinely require a particular order or precondition.

### 1.5 A correct receipt certifies an obsolete candidate

**Text:** Section 8 checks that a sha is on origin/main and runs evidence at that sha. Section 12 explicitly permits failed candidates on main before checking. Section 4 specifies dependency invalidation, but no atomic relationship between a final verdict and later publication is stated.

**Sequence — inference:** Item A’s candidate passes. While its Marker is running, item B publishes a change that breaks A. A’s Marker correctly accepts the earlier exported tree. A closes while the current product contains B’s regression.

**Why the defence fails:** Every observation of A’s candidate can be true. The missing property is that the accepted candidate is still the delivered composition when completion is recorded. Dependency invalidation might catch this, but the design does not specify an atomic check covering this race.

**Likelihood: medium.** Concurrent publishing makes the ordering plausible. This is a specification gap, not a verified live-code race.

## 2. How does it loop or burn unbounded effort?

### 2.1 It produces endless “movement” without approaching completion

**Text:** Section 6 defines movement as a new fingerprint or a newly green clause. Section 12 admits meaning-level circling is unmeasured. Spend overruns only trigger review.

**Sequence — inference:** A worker keeps pursuing the same impossible approach. Each generation changes an error identifier, affected file, failing assertion, or implementation detail. New fingerprints keep appearing. Occasional incidental clauses turn green. The approach never solves the experience, but the no-movement escalation never becomes applicable.

**Why the defence fails:** The definition rewards novelty of failure, not reduction of remaining work. Exact-repeat and A–B–A detectors do not establish semantic repetition. Per-run timeouts merely divide the infinite attempt into generations.

**Likelihood: high.** The text itself says exact repetition is a minority of failure.

### 2.2 Tightening and burned hold-outs create an indefinitely retreating finish line

**Text:** Sections 3.3 and 4 require failed hold-outs to be disclosed, added to the public contract, and replaced. Tightening immediately voids old passes. Section 9 also reopens passed work after escapes.

**Sequence — inference:** Build fixes one exposed edge case. The replacement hold-out finds another. Each repair changes behavior enough to invalidate other leaves or reveal another interaction. Every cycle supplies a new fingerprint, a new clause, or a newly green clause. The item continuously qualifies as moving.

**Why the defence fails:** Neither hold-out replacement nor tightening has a finite closure condition. The stuck path requires lack of movement; this sequence manufactures movement while never finishing. Owner-only loosening does not limit tightening.

**Likelihood: medium.** An open-ended input domain or thin initial contract makes this plausible. Nothing requires malicious judging.

### 2.3 Flakes prevent failure confirmation while consuming runs

**Text:** Section 6 counts a fingerprint only after rerun confirmation on the same tree. Sections 8 and 9 require uncached evidence, Marker reruns, hold-outs, and seeds.

**Sequence — inference:** A timing-sensitive failure alternates between different symptoms and occasional success. Each confirmation rerun passes or produces a different fingerprint. Build retries evidence; Marker later sees another failure. The system spends repeatedly without accumulating the confirmed repeats needed for escalation.

**Why the defence fails:** The flake exclusion protects against wrongful stops, but removes a source of evidence for stopping pathological instability. Other signals might fire; they are not guaranteed to fire when runs alternate tests, edits, and fresh symptoms.

**Likelihood: high** for live or timing-sensitive work; **medium** across the whole admitted workload.

### 2.4 Seeds, replacement exams, and Help consume effort without an item-level bound

**Text:** Sections 3.3, 7–9 require replacement hold-outs, Help rounds, second marking in specified cases, seed generation, controls, and second reads of possible equivalent mutants. Spend limits are deliberately off.

**Sequence — inference:** A modest goal reaches a candidate, then enters repeated Marker failures, hold-out replacement, consultations, and seed adjudication. Workers remain active and produce movement. Each individual operation terminates, yet their aggregate cost keeps growing.

**Why the defence fails:** `help_cool_h` limits consultation frequency, not total consultations. `seed_rate` limits sampling frequency, not total seed cost. Offline-first changes unit cost, not total effort. No claim of a hard cost bound survives this sequence.

**Likelihood: high** that verification sometimes costs more than building; **medium** that it continues indefinitely. The design supplies no aggregate terminating condition.

### 2.5 The stuck path transfers the obligation to an unattended human

**Text:** Sections 6–7 hold an item for Conductor after two unproductive Help rounds. A Conductor answer returns it to the top. No response deadline or terminal outcome is specified. Interruptions initially run report-only. First mod GREEN also requires an owner look (§3).

**Sequence — inference:** The item reaches `stuck` while the owner and Conductor are absent. It remains held. Alternatively, Conductor returns it with a suggestion, two more Help rounds fail, and it returns to the same hold.

**Why the defence fails:** A hold stops burning only while held. It does not establish that completion is impossible or that human intervention is truly necessary. Repeated release can resume the burn. Report-only signals do not stop it at all during rollout.

**Likelihood: high** that unattended work waits on a human; **medium** for repeated release cycles.

**Defence that holds:** A functioning stuck hold does stop active execution. I cannot honestly call the held interval itself an infinite compute loop.

## 3. How does memory poison it?

### 3.1 A citation verifies perfectly and supports the wrong conclusion

**Text:** Section 5 rehashes citations and preserves `reading` when the cited bytes are unchanged. Readings are explicitly interpretations. The binding contract says a new attempt must differ from every tried row; the design instead says rows impose no prohibitions.

**Sequence — inference:** A worker records “API X cannot support this feature,” citing a real failed run caused by an incorrect setup. The output and files never change. Every lease verifies the citation. Future workers repeatedly receive the row among the eight most relevant and avoid the viable approach.

**Why the defence fails:** Byte identity validates provenance, not inference. The binding contract’s “must differ” rule can turn the mistaken interpretation into an exclusion even though design §5 calls it advice.

**Likelihood: high.** Misinterpreting a legitimate failure requires no fabrication.

### 3.2 Supervisor rows give misleading classifications mechanical authority

**Text:** Section 5 always writes supervisor fields, even after worker death: signature, generation, tree hash, fingerprint, and gate. The worker supplies the interpretation and citations at handoff.

**Sequence — inference:** A worker dies during a test because of host pressure. The surviving supervisor row associates the failure with the active approach and gate. The next worker treats repeated rows as evidence that the approach fails, although the approach never received a valid trial.

**Why the defence fails:** Mechanical authorship does not make attribution correct. The row records where execution ended, not necessarily why the approach failed. There is also an unresolved rule interaction: rows without checked citations are dropped, but supervisor rows are “always written.” The text does not say what survives or how it is presented.

**Likelihood: medium.** The design explicitly anticipates worker death, and the rules include memory pressure, stale runs, and forced stops.

### 3.3 Cold redesign inherits the previous approach through the clone

**Text:** Section 5 gives each generation the same clone. Cold redesign removes `reading` and `state.md`, but retains evidence columns. Help sees the clone read-only.

**Sequence — inference:** The failed approach has shaped abstractions, test fixtures, comments, filenames, and diagnostic outputs. A fresh redesign worker reads those artifacts and reconstructs the same explanation. Help reaches the same recommendation from the same code and selected evidence.

**Why the defence fails:** Withholding two narrative channels does not remove the assumptions embedded in the workspace or in evidence selection. “Cold” describes a reduced brief, not independent reconstruction.

**Likelihood: high.** An implementation is a durable record of its author’s assumptions.

### 3.4 A false cache hit steers Build away from the actual regression

**Text:** Section 5 calls the cache a grader, depends on observed reads, defaults to miss, and excludes unobserved or external input. Auditing is sampled. Gate and Marker never use it.

**Sequence — inference:** Dependency tracing fails to represent a relevant absence, directory membership change, or indirect asset dependency. The cache returns an old pass. Build trusts it, investigates unrelated code, and records misleading tried rows. The uncached gate eventually fails, starting another cycle.

**Why the defence fails:** The default-miss rule only helps when the system recognizes uncertainty. An observation gap misclassified as complete can yield a false hit; sampled audits need not select it promptly.

**Likelihood: medium.** It depends on tracing details absent from the supplied material.

**Defence that holds:** The cache cannot directly provide the final PASS under §§5 and 8. The supported attack is wasted effort and poisoned search, not a cache-only false completion.

## 4. Where does the Judge collude?

Here “collude” means correlated or mutually reinforcing judgment. The text does not establish deliberate conspiracy.

### 4.1 Setter chooses the interpretation that Marker later validates

**Text:** Setter cannot reword criteria, but selects instruments, guards, and hold-outs (§3). Marker judges those artifacts. Section 12 acknowledges shared-model blindness.

**Sequence — inference:** An ambiguous experience admits two interpretations. Setter selects the easier one through its scenario and instrument. Build implements it. Marker independently finds that same interpretation natural and accepts the evidence.

**Why the defence fails:** Criterion text can remain byte-identical while its operational meaning changes through instrument choice. Role separation removes shared conversational history, not shared interpretation.

**Likelihood: high.** The live rules name one model, and semantic ambiguity is not exceptional.

### 4.2 Seeds and controls establish competence on a self-selected exam

**Text:** Section 9 draws seeds from known DEFECTS classes. Setter writes them. Suspected equivalent mutants are second-read by a human or another model. Controls are called known-good. Section 12 limits conclusions to seeded classes.

**Sequence — inference:** Setter produces easy, recognizable faults matching its own theory of failure. Marker catches them. Controls share the same unrecognized defect as real candidates and pass. Another model agrees that disputed mutants are equivalent. TRUST reports a strong catch rate while the unknown defect class escapes repeatedly.

**Why the defence fails:** Seed generation, seed validity, control validity, and marking can share the same blind spot. Controls establish false-fail rates only if their goodness is independently justified; that justification is not specified.

**Likelihood: high** for overinterpreting the result; **medium** for a particular hidden class dominating production.

**Defence that holds:** Section 12 explicitly forbids claiming coverage of unseeded classes. A correctly limited per-class catch rate is not itself fraudulent.

### 4.3 The packet and permitted tree still carry Build’s framing

**Text:** Section 8 allows Build to author artifact descriptions, command/expected-output pairs, and flat unverified clauses. Marker also receives Build-authored source, tests, and the diff. Lint uses schema, forbidden words, then Marker’s semantic check.

**Sequence — inference:** Build describes a narrow test as “end-to-end verification,” names a fixture as representative, and supplies an expected output that omits the relevant discrepancy. Source comments repeat that assumption. None requires an advocacy word. Marker follows the supplied route and adopts its framing.

**Why the defence fails:** Schema and word lint restrict syntax, not semantic anchoring. The semantic backstop is the same reader being anchored.

**Likelihood: high.** Ordinary descriptive language can frame an evaluation without violating a forbidden-word list.

**Defence that holds:** A correctly enforced mount wall blocks direct reading of excluded store files. The attack survives through explicitly allowed material; it does not require breaking the wall.

### 4.4 Hold-out burning and disagreement tuning make the evaluator progressively less independent

**Text:** Failed hold-outs become public clauses (§3.3). Marker/human disagreements feed Arbiter tuning, with seeded misses as regression tests (§8). Step 4 reruns the same seed set used for the baseline.

**Sequence — inference:** Build adapts to exposed hold-outs. Marker tuning improves performance on the known disagreement and seed corpus. Replacement hold-outs reflect the same emerging taxonomy. Scores rise while both sides become increasingly specialized to the evaluated cases.

**Why the defence fails:** New instances and hidden files do not create a fresh distribution. Reusing the seed set after tuning measures adaptation to that set as well as general improvement.

**Likelihood: high.** Exposure and tuning are explicit parts of the process.

### 4.5 `oracle_diff` shows the change without supplying the missing oracle

**Text:** Build may implement instruments (§3.2). Supervisor computes `oracle_diff`; a second model marks instrument or gate changes (§8).

**Sequence — inference:** Build writes a visual check that validates the wrong region or misinterprets a renderer value. The diff is accurate and plausible. Guard red succeeds because the guard perturbs that same region or value. Both models approve the test and reproduce its result.

**Why the defence fails:** Diff visibility establishes what changed. It does not establish the correctness of the mapping from experience to measurement. The second model receives the same potentially insufficient evidence.

**Likelihood: medium to high.** This is the builder-written-exam problem moved into instrument implementation rather than contract prose.

## 5. What is overbuilt?

The supplied evidence establishes defects in the present process. It does **not** establish the return on most proposed mechanisms. The strongest criticism is excessive guaranteed machinery against unmeasured marginal benefit.

### 5.1 The packet purity apparatus can become a separate rejection treadmill

**Text:** Section 8 adds fixed JSON fields, length restrictions, forbidden words, semantic inspection, and a fresh Marker after contamination. The measured evidence is six of 48 evidence fields containing history or advocacy words, explicitly a grep floor.

**Sequence — inference:** A substantively checkable candidate repeatedly receives packet rejections over descriptions or flat disclosures. Each rejection consumes another fresh Marker without examining the product.

**Why the defence fails:** The semantic layer is another subjective judgment. The six contaminated fields establish exposure to advocacy, not that this whole rejection apparatus improves verdict accuracy enough to justify its cost.

**Likelihood: medium.** The guaranteed parsing and review cost is clear; the false-rejection rate is not measured.

### 5.2 Mandatory verification multiplies per-leaf work before its yield is known

**Text:** Sections 3 and 8 combine base red, guard red, supervisor execution, Marker reruns, one to three hold-outs per leaf, and conditional second marking. Instrument leaves have their own guards. Section 9 adds seeds and controls.

**Sequence — inference:** A small feature requires new instrumentation and several leaves. Most elapsed effort goes into constructing and repeatedly checking the exam; tiny changes invalidate receipts and repeat the process.

**Why the defence fails:** “Cheapest tier” reduces execution price but does not reduce the number of obligations. The supplied 48 closes and 42 selftest references do not measure the marginal catch yield of each added layer.

**Likelihood: high.** Multiplication of work follows directly from the requirements. Whether its benefit exceeds its cost remains unshown.

### 5.3 The diagnostic bureaucracy can measure activity more precisely than progress

**Text:** Sections 5–7 introduce citation management, relevant-row selection, fingerprints, diff oscillation, finding curves, time categorization, cache-weighted churn, staged hooks, Help scoring, and cooldowns. Section 6 calls thresholds unmeasured; §12 admits semantic circling remains unmeasured.

**Sequence — inference:** Workers generate novel but useless failures. The system maintains detailed ledgers and fires overlapping signals, while the actual repeated misconception survives. Replay and threshold tuning become substantial work of their own.

**Why the defence fails:** Precision about time allocation and surface repetition does not establish progress toward the goal. The design’s own admitted blind spot survives the machinery.

**Likelihood: high.** The maintenance cost is structural; the central semantic gap is explicit.

### 5.4 Extraction and adapter conformance add another project without validating the promise

**Text:** Section 11 adds seven ports, a core/domain boundary, word lint, schema versions, a toy adapter, and cross-adapter conformance. Its justification is an owner-requested extraction, not measured improvement in unattended completion.

**Sequence — inference:** The team spends effort keeping a toy adapter and core vocabulary conformant while both adapters retain the same faulty acceptance assumptions. All conformance tests pass; false completion remains possible.

**Why the defence fails:** Shared selftests and fault tables establish consistency for those cases. They do not establish that a real accepted goal reaches a truthful terminal outcome.

**Likelihood: high** that this adds cost without directly buying evidence for §1.

The owner explicitly requested extraction. That establishes authorization, not evidence of benefit to the promise under review.

## 6. What is untestable or cannot be proved as written?

### 6.1 “A check that cannot go red is refused” is stronger than its proof procedure

**Text:** Section 13 step 6 promises this refusal. Section 3.1 observes base red and one guard red.

**Sequence — inference:** A check fails correctly on the base and planted guard, but always passes a large family of other wrong candidates. Step 6 passes.

**Why the defence fails:** Two observed failures cannot establish general falsification power. Conversely, inability to find a failing input does not prove that a check cannot fail. The build-order wording claims more than its finite experiment can decide.

**Likelihood: high.** This is a logical limitation of the stated proof.

### 6.2 Base red is impossible for legitimate preservation obligations

**Text:** Every clause requires base red with the contract’s failure signature (§§3.1, 8). Existing-store items receive a tree from their item text (§3).

**Sequence — inference:** A goal adds functionality while preserving an existing latency limit or preventing deletion of existing user files. The original build already satisfies that preservation clause. Its correct oracle is green at the lease sha.

**Why the defence fails:** A guard can establish that the oracle detects a planted violation, but it cannot make the unmodified base violate a property it already satisfies. The supplied design states no exemption. Instrument leaves can have the same problem when their prerequisite instrument does not yet exist and the base invocation crashes, which §3.1 explicitly excludes.

**Likelihood: high.** Regression-preservation clauses are ordinary requirements. This produces refusal or blockage of legitimate work, not proof of correctness.

### 6.3 The Pit proof can pass by making completion impossible

**Text:** Section 13 step 16’s preregistered condition is only that the system “must not say GREEN” on the historical Pit.

**Sequence — inference:** The implementation rejects every packet, leaves the item perpetually queued, or returns UNJUDGEABLE for everything. It never says GREEN. The named Pit condition succeeds.

**Why the defence fails:** A negative-only result cannot distinguish detection of the visual defect from universal refusal or nontermination. Section 9’s controls address Marker false failures, but step 16 does not state a corresponding positive outcome for its integrated system proof.

**Likelihood: high** as a weakness in the proof criterion. This does not mean implementers will deliberately exploit it.

### 6.4 Several build-order “proofs” establish plumbing, not the claimed property

**Text:** Step 8 checks that a burn moves a clause and creates a replacement. Step 10 compares returns-to-done with the old memory tail. Step 13 checks consult delivery and holding. Step 17 reuses selftests and fault tables.

**Sequence — inference:** Replacement hold-outs are worthless; poisoned interpretations survive; Help produces irrelevant options; both adapters share a false-pass bug. Every named plumbing test still succeeds.

**Why the defence fails:** File movement does not prove hold-out quality. Completion speed does not prove truthful completion. A hold proves stopping, not that the stated reason is true. Shared tests do not detect shared omissions.

**Likelihood: high.** These are direct counterexamples to treating the named tests as proofs of the broader claims.

### 6.5 `TRUST.md` contains measures that are not fully computable as stated

**Text:** Section 9 says `relentless trust` computes the report “from the store, no prose.” Its table leaves important predicates undefined.

**Sequence — inference:** Two implementations consume identical records and produce different valid-looking reports:

- **Finish rate:** “accepted” is not explicitly distinguished from intake acceptance, and “unaided” has no rule for owner looks, Help, Conductor answers, or loosening. Windowing and unfinished cohorts are unspecified.
- **Escaped defects:** reopened PASSes, repeat PASSes, duplicate escape reports, and exposure age lack counting rules. Recent passes can look cleaner simply because nobody has encountered their defects yet.
- **Marker catch rate:** equivalent mutants require adjudication. “Known-good” controls require an external correctness judgment. Raw store contents do not establish either predicate.
- **True stops:** Conductor agreement can be counted, but it is not independent ground truth that human intervention was necessary.
- **Help value:** “movement after Help” is computable once the window is fixed; attributing that movement to Help is not. Build could have found it anyway.
- **Repeat work:** identifying hours attributable to a cache-known result requires an attribution rule when reading, waiting, and parallel activity overlap; the time ledger categories alone do not supply it.

**Why the defence fails:** Storing judgments makes a report mechanically renderable. It does not make the judgments objective or remove missing counting definitions.

**Likelihood: high.** These ambiguities are present in the table itself.

### 6.6 The baseline and replay claims lack a clean comparison

**Text:** Section 13 says measure before improvement. Yet wall and packet changes precede the first catch-rate baseline in step 3. Step 4 reuses the same seed set. Sections 6 and 13 require wrongful stops below `false_stop_limit`; the supplied live rules contain neither that limit nor several named signal thresholds.

**Sequence — inference:** The wall changes what Marker sees before baseline measurement. Later tuning improves scores on the reused seeds. A hand-labelled replay passes a selected threshold, but deployment encounters different long investigations and failures.

**Why the defence fails:** The baseline cannot measure the earlier wall’s effect. Reused cases cannot isolate generalization from adaptation. The replay can measure agreement on its labelled sample; it cannot prove the future false-stop rate. Missing thresholds also prevent reproducing the proposed acceptance decision from the supplied rules.

**Likelihood: high** that the stated proofs support narrower conclusions than claimed. The missing rules are implementation debt in this draft, not evidence that they can never be implemented.

## Three strongest attacks

1. A structurally valid but incomplete tree lets every oracle, guard, hold-out, walk, and Judge pass while the owner’s actual goal remains unmet.
2. Endless new fingerprints and tightening count as movement, so the agent can spend indefinitely without reaching either completion or the stuck path.
3. Setter, builder-written instruments, Marker, seeds, and tuning can validate one shared misconception; independent instances then certify the same wrong experience.