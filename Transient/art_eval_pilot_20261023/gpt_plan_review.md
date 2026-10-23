Image 1: A 19-candidate creature contact sheet, mixing detailed painterly beasts with small, heavily outlined sprites; the selected views include frontal, overhead, and side-on poses.
Image 2: A white, black-outlined creature beside a vanilla human and rat at several game scales, with nearest-neighbour enlargements of the small-scale views.

**My verdict: build the review assistant; do not enable autonomous art acceptance yet.** The pilot demonstrates useful defect detection and several broken evaluation assumptions. It does not demonstrate safe delegation of KEEP decisions or net savings in the owner’s time.

Everything below is ranked by likely impact. Calculations use your supplied tables; I have not inspected repository files.

**(1) Enhance the sheets, prompts, and pipeline by fixing the decision structure first.**

1. **Separate observations, policy, and actions.**

   Currently, KEEP/REDO mixes several questions: Is the picture acceptable? Is it the preferred candidate? Is the brief settled? Is another asset blocking it? Should existing art be removed?

   Use separate fields:

   | Layer | Example output |
   |---|---|
   | Visual observation | “Catch has an upright, supported posture; body differs from living reference.” |
   | Constraint finding | `CATCH_POSE: fail`; `SPECIES_MATCH: uncertain` |
   | Severity | Blocking under policy version X |
   | Asset status | Acceptable / unacceptable / unresolved |
   | Workflow status | Ready / blocked on source / needs runtime check |
   | Preference | B preferred to C |
   | Action | Retain, request revision, route to owner |

   Let code derive the final disposition from explicit policy where possible. This makes Opus’s alleged severity problem independently testable.

   **A catch awaiting its living design should usually be BLOCKED, not automatically REDO.** The existing catch might remain usable. Regeneration should follow an actual mismatch after the source settles.

2. **Preserve the evaluation evidence permanently.**

   Snapshot the exact images, hashes, displayed letters, slot roles, brief, scale facts, owner decision, and owner-visible sheet at decision time. Retain rejected originals.

   Reconstructing which picture the owner saw is already consuming substantial effort and weakening the benchmark. This is a higher-priority infrastructure task than building another template.

   Preserve distinctions such as:

   - Acceptable primary.
   - Acceptable variant.
   - Useful regeneration base.
   - Unchosen, quality unknown.
   - Explicitly rejected.
   - Reference only.

   **“Not picked” must never imply “bad,” and reviewer rejection must never imply permanent deletion.**

3. **Build question-specific views instead of one enormous universal card.**

   The proposed composite, every facing, every variant, scale panels, references, and few-shots will become crowded and expensive. Apparel alone can exceed the proposed image budget.

   Use a compact overview plus the images needed for each check:

   | Check | Best evidence |
   |---|---|
   | Facing identity | Aligned S/E/N strips at shared scale |
   | Tiny eyes, limbs, pipe openings | Tight, labelled crops with surrounding context |
   | Style consistency | Candidate beside two or three relevant accepted siblings |
   | Runtime legibility | Target-scale raster on representative backgrounds |
   | Variant consistency | Paginated pool at shared scale |
   | Assembly/layering | Runtime assembly capture |

   Image 1 exposes the problem: equal-sized cells contain radically different amounts of subject detail, and “most frontal” does not mean a consistent surface. Keep contact sheets for navigation and gross screening.

   Image 2 has a useful scale comparison, but substantial empty space. Supply compact, consistently ordered strips, with text facts outside the image.

4. **Make scale and visibility tests reproducible.**

   Show both:

   - Shared game scale, preserving real size differences.
   - Detail-normalized views, explicitly labelled as such.

   Show sprites against light and dark flat backgrounds as well as terrain; checkerboard alone is a poor halo test.

   For play zoom, retain the actual target-resolution raster and provide a separately labelled integer enlargement. Enlarging a 32-pixel render helps inspect its pixels; it does not recreate the experience of seeing it at game size.

   “PNG ≤2000 px” does **not** establish “no resize.” Image processing depends on the model and detail setting. Official OpenAI documentation also identifies counting and precise spatial reasoning as limitations. Record the actual image configuration and test tiny-feature detection through the actual transport. [Official OpenAI vision documentation](https://developers.openai.com/api/docs/guides/images-vision)

5. **Replace leading style laws with subject-specific acceptance criteria.**

   “Name its closest Earth animal; if identifiable, REDO” will reject useful art. Your own Burrak and Vobbal counterexamples already show this.

   Better:

   > Intended baseline: otter-like body. Required departures: split jaw, six paddle limbs, asymmetric head crest. Familiar body resemblance is acceptable if these departures are clear.

   Likewise, “cute,” “realistic,” and “painterly vanilla” need visual anchors. Those words can pull toward conflicting styles. Use a few owner-approved examples spanning the acceptable range.

   Do not silently convert a new owner preference into a universal blocking rule.

6. **Make uncertainty an answer to each question.**

   Use `present / absent / occluded / unreadable / not applicable`, rather than yes/no everywhere.

   Four visible legs do not prove a six-legged animal has only four. Eyes visible from a rear-facing animal do not necessarily prove it faces forward. Geometry and anatomy can create legitimate exceptions.

   Require a facing/panel identifier and short evidence statement for each blocking finding. Treat generated coordinates as navigation aids, not verified measurements.

**(2) The skeptical review: several conclusions are stronger than the evidence.**

**The ensemble’s headline metric hides the error you most care about.** From the supplied tables:

| Quantity | Pilot result | Implication |
|---|---:|---|
| Joint KEEPs | 25 | This is the acceptance population |
| Owner REDOs among joint KEEPs | 4/25 = **16%** | Agreement is insufficient for auto-acceptance |
| Joint REDOs | 7 | Very little evidence for autonomous rejection |
| Owner KEEP among joint REDOs | 1/7 | Automatic regeneration is also uncertain |
| Owner REDOs caught by either model | 14/18 | Useful triage, with four historical misses |

The approximate 95% Wilson interval for the joint-KEEP error rate is **6–35%**, even treating subjects as independent and labels as correct. Some misses involve reconceptualization; that means you need better labels, not that the remaining acceptance policy is validated.

**N=47 is smaller than it looks.** You have only 18 REDOs, one biome, one owner sitting, related species/catches, and shared candidate families. Those are not 47 independent demonstrations of generalization.

GPT’s REDO recall, 11/18, has an approximate 95% Wilson interval of **39–80%**. Opus’s 9/18 is approximately **29–71%**. The data do not establish either reviewer above the proposed 70% bar.

Flora has only **one REDO across 13 subjects**. There is essentially no evidence about plant defect recall. The pilot provides no direct performance evidence for buildings, apparel, ports, pits, or UI icons.

“Statistically indistinguishable” also does not mean “equally capable.” It means this experiment cannot resolve the difference.

**The pilot compares two different operating procedures.** GPT received fresh per-subject calls; Opus reviewed all 47 in one continuing context. That changes cross-subject anchoring, accumulated context, latency, and potentially access to images. You cannot attribute the entire difference to model capability. Run both with fresh, equivalent contexts and log exactly which images each inspected.

**The historical key is not a clean art-quality oracle.**

- A KEEP accompanied by “redo more alien” is not an unambiguous final acceptance.
- A roster CUT is outside visual art evaluation.
- A new creature concept is not a defect in faithfully rendered old instructions.
- A changed brief or standing policy can make an old acceptance obsolete.
- “50% larger” may require a def change rather than new art.

Label these separately. Do not simply discard reversed rulings: they are evidence about ambiguity, changing policy, or missing context, and may be precisely the cases that should trigger abstention.

The SCORE also says CUT was not offered, but the supplied preamble explicitly offers CUT. That discrepancy should be corrected.

**“Opus perceives; GPT is blind” is a hypothesis.** The manual reason assessment is useful, but one scorer’s interpretation of short explanations does not identify the models’ internal failure mechanisms. A missing mention can mean missed perception, omitted reporting, wrong priority, or insufficient image inspection. A model can also write a plausible criticism without reliably detecting the feature.

Test perception with narrow crop-level questions whose answers are independently labelled.

**Your anti-anchoring measures are incomplete.**

- One card per call prevents conversational carryover, not anchoring within a candidate set.
- Installed/donor/date labels reveal status even when letters are balanced.
- Owner notes and exemplars can dominate subsequent inspection.
- Two models can agree because the same prompt induces the same mistake.
- Different model families do not guarantee independent errors.

Perform an initial visual-quality pass without provenance, then apply provenance and ownership rules separately. Those rules remain important; they need not contaminate visual judgments.

The two-pass description approach is worth testing, but the rule “feature absent from first observation ⇒ UNSURE” is too rigid. Initial descriptions are incomplete. Permit reinspection and record what changed.

**The proposed prompt fixes risk overfitting this sitting.** Making wall-clinger overhead views, raised wings, and one-sided equipment universally “polish” because the owner tolerated three examples is unsafe. The reverse mistake—turning every criticism into REDO—is equally unsafe.

Use explicit exceptions supported by standing policy. Treat all 47 pilot subjects as development data after this analysis.

**The frozen regression set will stop being independent.** Repeatedly inspecting it and revising prompts against it turns it into development data. An owner override used to design a new question is also not an independent test of that question, even if its image never becomes a few-shot.

Keep a regression suite for known failures and a separate, periodically refreshed untouched qualification set.

**Fourteen templates are an organizational proposal, not a measured requirement.** PNG count is the wrong denominator for review workload. Three facings, twelve animation frames, and one portrait do not represent equivalent review jobs.

Count resolved subjects, variant sets, runtime configurations, review frequency, and owner minutes. Implement shared check modules and a few validated configurations. Swimmers and catches may need separate qualification despite sharing much of the creature infrastructure.

**The offline/capture percentages are overconfident.** The path classification combines pawn and apparel assets, so it cannot substantiate an 86% offline share without further separation.

Deterministic rendering is not the same as faithfully reproduced rendering. Validate offline composition against runtime examples covering offsets, tinting, body types, overlays, materials, rotations, and special graphic classes.

Use:

> Offline eligibility after renderer validation; capture required for unvalidated configurations.

A keeper save helps reproduce a scene. It does not make an old capture valid after textures, defs, code, mods, or rendering behavior change. Store capture provenance and invalidate it appropriately. Reviewers should know whether evidence is a runtime capture or an offline approximation.

**Numeric measurements are not automatically trustworthy gates.** A script can correctly measure the wrong thing: canvas versus body mass, appendage height versus size, or a poor ellipse fit. Hard-fail only validated invariants. Heuristic measurements should flag review, with applicability and uncertainty.

**The cost model omits the largest costs.** Measure owner verification, bad regeneration cycles, capture maintenance, benchmark curation, retry handling, quota delays, and false-approval cleanup.

Three regeneration rounds can amplify a mistaken review rule. Keep revision history, detect repeated objections, and escalate when revisions stop improving.

The owner-facing pipeline also remains ambiguous: it says joint KEEPs appear on the owner’s sheet, while projected savings assume many need no review. Define whether each action means “skip,” “glance,” or “inspect fully,” then measure the actual savings.

**(3) Alternatives worth testing, in priority order:**

| Rank | Alternative | Concrete recommendation |
|---:|---|---|
| 1 | Crop-specific checklists | Ask a few factual questions per relevant crop before judging severity. Highest-value test for eyes, limbs, bores, and catch posture. |
| 2 | Pairwise comparison | Compare two candidates for specific criteria, with **both unacceptable**, **both acceptable**, and **insufficient evidence** options. Preference alone cannot establish ship-worthiness. |
| 3 | Retrieval from past owner notes | Retrieve a small balanced set of accepted/rejected examples by visual problem and module. Retrieve images and policy context, not just similarly worded criticism. Exclude related held-out families. |
| 4 | Disagreement-driven active learning | Prioritize model disagreements, unstable answers under harmless layout changes, and new configurations. Preserve random sampling of agreements to detect shared misses. |
| 5 | Rubric scoring | Use anchored dimensions: facing, identity, style, scale, runtime integrity. Blocking failures remain vetoes; an attractive palette must not average away a wrong species. |
| 6 | Sibling image comparison | Use registration, alpha masks, dimensions, palette summaries, overlays, and image diffs to expose changes. Pixel difference does not measure style quality or anatomical correctness. |
| 7 | Alternative reviewer arrangements | Compare two-model agreement with one model plus a specialist crop pass. Add a third reviewer only if it catches additional owner-confirmed errors at worthwhile cost. |
| 8 | Other human reviewers | A RimWorld artist can independently label facing, assembly, and style issues on a small set. This tests the rubric; owner-specific preferences still require the owner. |
| 9 | Model-generated reference images | Useful for exploring and agreeing on a visual brief. Require owner approval before treating them as targets; generated references can repeat the same anatomical and perspective errors. |

A particularly promising architecture is **one model for visual observations, explicit policy for severity, and a second reviewer only where measured value justifies it**. Test it against the default ensemble; do not assume it wins.

**(4) The next experiment should distinguish input failures, perception failures, and policy failures.**

I would start with **T1 creatures and the catch dependency module**, where the pilot exposes the clearest problems. Do not build fourteen templates first.

Use approximately **60 new creature families across at least three biomes**, with walkers, swimmers, and flyers represented. Include associated catch slots when available; score them separately and cluster results by family. This is a diagnostic experiment, not sufficient certification for every subgroup.

Freeze the briefs and policies before running. Use the existing 47 subjects for development only.

For both reviewers, in fresh per-subject contexts, run a paired 2×2 comparison:

| | Existing prompt logic | Explicit observations + severity policy |
|---|---|---|
| Existing image presentation | Control | Tests policy improvement |
| Overview + targeted detail crops | Tests presentation improvement | Tests combined improvement |

Keep the underlying artwork identical. Randomize candidate letters and presentation order. On a subset, repeat with swapped positions to test decision stability. Log model version, images inspected, request configuration, tokens where available, retries, and elapsed time.

Have the owner evaluate each new subject **once, without model verdicts visible**, recording:

- Acceptable candidates, independently of preferred candidate.
- Blocking defects and relevant panel.
- Polish requests.
- Brief unresolved or changed.
- Workflow dependencies.

Repeat about 10–12 owner cases later, hidden among other cases, to estimate the consistency of the labels. Do not ask the owner to score eight model outputs per subject.

After independent labelling, show model assistance on a randomized subset to measure correction burden and review time. If time allows, a later counterbalanced workflow trial should compare ordinary review against assisted review on matched new subjects.

Primary outcomes should be:

1. **Blocking-error rate among proposed automatic KEEPs.**
2. **Owner minutes saved, including corrections.**
3. False regeneration rate.
4. Automatic-decision coverage.
5. Defect-specific recall and answer stability.

Use family-level uncertainty estimates. Report representative production results separately from any deliberately enriched defect challenge set.

**Production qualification should be per action and validated configuration, not one global model score.** My suggested initial rules are:

| Permission | Qualification rule |
|---|---|
| Annotate sheets | Owner retains decisions; annotations are easy to verify and show positive net time savings |
| Recommend regeneration | Correct defect evidence; no destructive removal; owner approves while precision is being established |
| Regenerate automatically | One-sided 95% lower bound on blocking-defect precision ≥90%, within a validated configuration; archive everything |
| Accept automatically | One-sided 95% upper bound on owner-confirmed blocking-error rate ≤2%, with meaningful coverage and demonstrated time savings |
| New module or rendering configuration | Shadow mode until separately qualified |

For perspective, with **zero errors**, a one-sided 95% binomial upper bound falls below:

- **5% after 59** independently audited automatic KEEPs.
- **2% after 149**.
- **1% after 299**.

Those counts assume independent, representative cases and a frozen decision policy. Related assets and repeated tuning weaken that interpretation. Accumulate qualification evidence through ordinary work; do not make the owner label hundreds of examples in one special sitting.

Require useful coverage as well—say at least 25% of eligible subjects—and target at least 30% owner-time savings, with evidence that savings are positive. Otherwise a reviewer can appear safe simply by abstaining on everything.

After qualification, audit a random sample of automatic decisions plus all disagreements and new configurations. Repeated failures in a defining feature should suspend that module. A reviewer that passes plants should gain no automatic authority over swimmers, apparel, or machine assemblies.

**The first production milestone should be faster owner review with preserved evidence. Autonomous KEEP decisions should be earned separately.**