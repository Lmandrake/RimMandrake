# Jev opportunities — where a cheap typed-judgment model changes this project

**Status: exploration. Nothing filed, scheduled or approved.**

Provenance: a five-domain repo scan on 2026-09-28 (dev tooling · runtime C# · content review ·
work record · def corpus), then an adversarial design review by GPT (gpt-6-pro) the same day,
then verification of every interface claim against TypeSafe's own docs. The review deleted or
narrowed most of the first draft's entries. This version is what survived, plus what the review
found that the scan did not.

## What Jev is, with its real limits

TypeSafe AI's "System One" model. It does not generate prose. Code hands it a `state` (arbitrary
JSON) plus a map of typed questions; it returns typed answers only: **Choice** (one of a defined
set, with a probability per option), **Noul** (probability a yes/no statement is true), **Score**
(a probability-weighted position on ordered levels). Independent questions over the same state run
in one request, in parallel, and cannot see each other's answers.

**MEASURED against `docs.typesafe.ai`, 2026-09-28 — these numbers killed three first-draft entries:**

| Fact | Source |
|---|---|
| **255 options maximum per Choice** | `primitives/choice.md`, `api.md` |
| **64k tokens per request; 32k for `state` plus the single longest question** | `models.md` |
| Rate limits 250k tokens/sec, 1,200 requests/min | `models.md` |
| Price per input token, **output free** | `models.md` |
| `confidence` is computed from **how the probability distribution is spread** — a flat shape is low, a single peak is high. It is not a correctness check. | `primitives/choice.md` |
| An **alias moves** when a release ships. Pin the versioned ID if thresholds were tuned against it. | `models.md` |

And from `model-jaggedness/jev-1.13.md`, four limits that bear directly on what follows:

- **It answers the question you wrote, not the one you meant.** Negations and implied conditions
  are read at face value.
- **Accuracy falls as `state` grows with content unrelated to the decision.** Irrelevant detail
  acts as a distractor. "One request, all candidates" is therefore not free.
- **Indirection costs accuracy** — "a property of a property", or anything needing several hops.
  Most of the first draft's def-consistency checks are exactly that shape.
- 🔴 **"State is data, and `jev-1.13` does not treat it as hostile by default. Content written to
  adversarially steer the model — an injected instruction, a deliberately misleading framing, or
  *text that argues for its own classification* — can move the answer."**
- It **struggles with numeric precision** and with counting.

Official skill: `typesafe-ai`. Our evaluation harness: `~/dev/ConsultJev`.

---

## The test every seam must now pass

The first draft's central error, named by the review and accepted: **it treated "a place where a
judgment could be inserted" as evidence that inserting judgment would help.** Its `CONFIRMED`
labels confirmed a count, a filename, or an inadequate heuristic — never the proposed intervention.

The load-bearing assumption underneath, which most of the first draft violated:

> **The decision-relevant evidence and the governing rule already exist in a compact, usable
> state, and the only missing component is judgment.**

The attack that settles it is an **indistinguishable-input counterexample**: construct two
situations that produce the same JSON but require different correct answers. Worked example, and
it is fatal to a whole cluster — send the same creature description and its local XML from two
installations, one with an applicable behaviour-adding patch and one without. A perfect model must
return the same answer to the same state, so it cannot correctly judge "this description promises
an unimplemented mechanic" in both. **That is not a calibration problem; an input is missing.**
This repo is unusually exposed to it, because our own CLAUDE.md records that an `RM_` biome's real
cast is patch-added and that reading the BiomeDef alone sees the wrong half.

So every seam owes four columns before it is worth evaluating:

1. **What evidence must be supplied for this answer to be knowable?** A seam that cannot fill this
   concretely is not ready.
2. **What is the deterministic baseline?** If ordinary code can do it, ordinary code does it.
3. **What exact downstream action does the answer drive?**
4. **What does a wrong answer cost?** — measured in the owner's attention, not in tokens.

And three claims must be kept apart rather than collapsed into one confidence:

| Claim | What would establish it | Where we stand |
|---|---|---|
| The failure exists | A documented incident, not a corpus count | **Strong** for several |
| This integration addresses its *cause* | Evidence the missed step was judgment, not retrieval or ignored guidance | **Scattered** |
| This implementation helps | Improvement over a non-model baseline under the real review budget | **No results** |

---

## Part 1 — What survives

Only bounded **text-to-text comparisons**, where both texts are supplied and the question is
answerable from them alone.

### 1.1 The stale-citation family — one evaluator, several callers

Merged from three first-draft entries that asked substantially the same question.

**MEASURED: 130 of 202 live items cite an item id that exists only in `items/closed/`.** Some are
legitimate history; some are a live item about to be worked against an assumption a closure already
overturned. Confirmed doc-side instances: `design/MOVING_DUNES_DESIGN.md`,
`design/RIMPROPERTY_ANIMAL_THEFT_SPEC.md` and `design/RM_GRAFFITI_SCOPE_WIDENING.md` each still read
DRAFT/pending while citing a now-closed item.

- **Primitive:** Choice over the *relationship* — `historical mention / active dependency /
  proposition invalidated by the closure / insufficient evidence`.
- **Required evidence:** the citing passage, and the cited item's **closure resolution** — not
  merely its status. An item can close because it was abandoned or superseded while the underlying
  need survives, in which case a citation of it is not stale at all.
- **Deterministic baseline:** finding the citations is already deterministic and already done. Only
  the relationship judgment is new.
- **Same evaluator, different caller:** `FROZEN_FACT_STILL_TRUE` — ask whether a *supplied later
  record contradicts a supplied fact*, never whether a fact is globally still true. Age is a
  retrieval signal, not evidence of falsity. Live candidate:
  `infrastructure/state/facts/naming_inventory.md`, frozen 2026-08-23, predating the 2026-08-31
  rename closure it exists to inform.

### 1.2 ASSERTION_VS_CITATION

`src/RimMandrake/Utils/check_canon.py:44` — does this line **assert** a number as currently true,
or merely quote, cite or negate it? The marker heuristics (⛔ / `~~` / "was") were hand-scoped to
cell-vs-line by trial and error after two documented silent misses. The question is answerable from
the supplied line alone, which is why it survives when its neighbours do not. Noul.

### 1.3 Brief-vs-source comparison, with a corrected output contract

The first draft claimed `anooba`'s entry contradicts itself — "stripes" against "varying gray".
**That is not a contradiction; both can be true.** It is unsupported specificity. Left as written,
the checker would punish elaboration as falsehood.

- **Primitive:** Choice — `explicit contradiction / unsupported added detail / compatible /
  insufficient evidence`.
- Applies to an entry's Visual Brief against its own Sourced Text, and to a def's stated
  colour/genes/traits against the entry's sourced canon.
- **Same contract covers the cast:** one evaluator for `src/RimMandrake/Inhabited/Defs/CastRosters/`
  (**MEASURED: 294 `CharacterDef`s across 12 files**, under the namespaced tag
  `RimMandrake.Inhabited.CharacterDef` — a plain `findall("CharacterDef")` returns 0). Behaving
  bravely once does not require a permanent bravery trait: *missing mechanical corroboration* and
  *explicit mechanical contradiction* are different findings and must not share a warning stream.

### 1.4 MULTI_HOME_REASON_FLAG, strictly bounded

Does a multi-homed species' description **explicitly state** a migration or life-stage rationale?
Noul. It must never silently upgrade to "the rationale is valid" or "the exception is authorised" —
those are the owner's, per-biome, at that biome's own sitting. Flag only; **evictions are stopped
and this never edits a roster.**

### 1.5 FILE_TIME_DUP_SCREEN — bounded, but not as first drafted

A finite record collection, so exhaustive batched pairwise screening is possible without
sophisticated retrieval. Two corrections:

- ⛔ **Candidate ids cannot be the Choice options.** 202 live + 863 closed exceeds the **255-option
  cap**, and the 32k `state` budget bounds how many candidates ride in one request anyway.
- ⛔ **Single-winner Choice is the wrong *meaning*.** If a new item duplicates two existing records,
  a distribution of 0.49 / 0.49 / 0.02-for-none represents two compelling matches, and a 0.9
  threshold on the winner rejects both. Use **pairwise relationship classification** — `same
  deliverable / partial reusable implementation / complementary work / vocabulary overlap /
  insufficient evidence` — and aggregate in code.

---

## Part 2 — The category the scan missed: offline semantic compilation

The review's best contribution, and the answer to "what did five domains all miss". Every scan
asked *"where could we insert a decision?"* The better question:

> **Where could one bounded classification produce reusable metadata that eliminates repeated
> decisions?**

The output is a **versioned, reviewable metadata artifact**, not a fresh verdict each time a
consumer needs one. Two concrete advantages here:

- **It attacks re-invention at the retrieval boundary, which is where the failure actually lives.**
  A closure record linking an implemented capability to its real files and aliases stays
  discoverable when the next agent invents a different name — which is precisely our failure shape,
  since our naming convention is invented exotic words. The model may *propose* classification
  tags; **file references come from recorded changes, and the model never invents provenance.**
- **It moves most runtime aspirations out of runtime entirely.** Classify or propose authoring
  metadata once, keep the owner's approval where required, and let ordinary code apply explicit
  policy to live game state. No new runtime transport needed.

Its advantage is architectural: **it concentrates uncertainty at one reviewable boundary instead of
replicating it across forty call sites.** Start with one existing taxonomy and one consumer. Store
inferred hints separately from authoritative facts, invalidate them when their sources change, keep
the original evidence. This still has to prove its value like everything else.

---

## Part 3 — Cut, with reasons, so they are not re-proposed

Each of these was in the first draft. They are recorded as decisions, not as live proposals.

**Because a deterministic check is the right instrument:**

- **WALK_SUBJECT_MATCH** — the measured failure is inconsistent formatting (backticked in 28 walks,
  bare in 34, absent in 16). Parse the three representations; report an absent subject as missing
  data. Do not replace a broken parser with a semantic guess about authorial intent. (The walk model
  was separately ruled to change to a `feature:` key, which is the actual owed work.)
- **MAYREQUIRE_GUARD_AUDIT** — an attribute on an ineffective node is structural. **Proven by my own
  measurement: a deterministic XML pass found all 61 inert top-level `<Operation MayRequire=…>` sites
  out of 2,365 total, in about three seconds.** Whether a *correctly placed* guard is semantically
  appropriate is a separate and much harder question; the 61 do not validate it.
- **WEAPON_ROLE_CLASSIFY** — ThingDefs carry an authoritative tech-level field. Read it, including
  inheritance. Semantic inference is a fallback for genuinely missing metadata, never a substitute
  for an available fact.
- **TWIN_ROSTER_COHERENCE** — the documented defect was a wrong census caused by not combining the
  inline and patch-added rosters. Fix the combination and the counting. A thematic-coherence Score
  neither repairs the census nor identifies a non-aesthetic defect.
- **WARDEN_HEIR_PICK** — bond, age or an explicit succession rule sort deterministically with a
  seeded tie-break. Replacing list order is warranted; a model is not.

**Because the proposed answer is not knowable from the evidence supplied:**

- **UNREVIEWED_ENTRY_TRIAGE** — cannot rank the magnitude of corrections to *existing art* from
  entry text. Jev is text-only, and a generation prompt is not proof of what an image depicts. A
  narrower live question ("does this entry state an appearance requirement that conflicts with
  recorded art metadata?") would need that metadata first, and its acquisition cost belongs in the
  proposal. **MEASURED: 137 entries, 29 carry a real `## ruling`, 108 carry the placeholder** —
  CLAUDE.md's figure of 25 is simply out of date.
- **DESC_PROMISES_MECHANIC / HEDIFF_MECHANISM_CLAIM / FLIGHT_FICTION_SCREEN / QUEST_TEXT_VS_GRAPH** —
  all need an **effective-behaviour representation**, and local XML is not one. They are the
  indistinguishable-input counterexample above. Split into "what does the prose explicitly promise?"
  and "what evidence supports it?", and compose the stages **in code** — parallel questions are
  isolated and cannot form a reasoning pipeline.
- **DOC_CLAIM_CERTAINTY** — if BEDROCK/RULED convey *authority*, the field is wrong: a confident
  invented claim is not bedrock, and a hedged sentence can quote an authoritative ruling. Authority
  comes from provenance and recorded rulings. A model can classify *assertive wording*, which is a
  different field with a different name.
- **SPAWN_RATE_PREFILL** — "a calibratable guess" is not an improvement until there is something to
  calibrate against. A description does not determine an appropriate gameplay frequency, and "rare"
  does not specify a normalised share among eligible creatures. The real gap is observing spawn
  consequences.
- **ARTPIPE_STYLE_PRESCREEN** — can catch a self-contradictory prompt; cannot establish that a
  compliant prompt yields unfused limbs. No evidence yet that prompt violations cause the waste.
- **CANON_TIER_MISPLACEMENT / EARTH_FAUNA_BAN_PRESCREEN** — unverifiable parametric world knowledge.
  Flag-only does not rescue a warning stream that costs more attention than it saves. Canon comes
  from the Wookieepedia API, which works from here.
- **TAG_FAMILY_CLUSTERING** — a Choice cannot discover a taxonomy nobody supplied; with predefined
  families it is classification, not clustering. And "crude on purpose" is not a demonstrated cost.
- **PROPOSAL_SRC_DRIFT** — 14 or 32 XML hits are not evidence the proposal's mechanisms exist; they
  may be names, references or adjacent ideas. A scalar Score hides the denominator. If revived, use
  the proposal's own obligations as units and aggregate per obligation in code.
- **DUPLICATE_CREATURE_CONCEPT** — thematic similarity is not redundant design; two similar
  scavengers can differ in biome function, life cycle or deliberate placement. The honest output is
  a *related-concept candidate*.

**Because the problem was never shown to exist:**

- **REVIEW_SCOPE_SANITY** — the first draft called this "a protection layer that does not exist
  today". No incident of an inaccurate scope declaration was ever cited, and a reviewer claiming
  "I read the whole file" defeats it trivially. At best it audits the *declaration*, not the review.
- **REVIEW_COST_TRIAGE** — confuses effort with priority. A tiny semantic change can be dangerous; a
  large repetitive one can be trivial. Decide first whether the objective is estimated effort,
  defect risk, or expected value of review.
- **LESSONS_INBOX_ROUTING** — mechanically plausible (~112 bullets), but a backlog count does not
  show that *sorting* is the obstacle. It may just produce a neatly distributed backlog.
- **LIVE_PROOF_PHRASE_LIST** — can judge whether prose acknowledges an outstanding obligation;
  cannot determine whether the obligation exists without the governing rule and the evidence record.

### The seed idea, judged: code-health clean/dirty

**It does not hold, and the reasoning is worth keeping.** `code_review_status.py` decides CLEAN vs
DIRTY by comparing a recorded content hash against the bytes on disk. That is exact, deterministic,
free and correct; a model would make it slower, costlier and less reliable. **Do not touch it.** The
two follow-ons the first draft proposed one layer out — triaging the DIRTY backlog by review cost,
and checking a review's declared scope — are both cut above, for different reasons.

---

## Part 4 — Runtime: withdrawn from the first round

The scan found eight live decision points that are currently a flat random roll, a first match, or a
hardcoded threshold (`GateSearchHook.cs:35`, `RM_ElderTradeUtility.cs:71`,
`RM_WardenMotherSuccession.cs:358`, `GameComponent_Ninefold.cs:238` and `:385`,
`RM_IncidentWorker_SuulkArrival.cs:45`, `AnimalTheftUtility.cs:41`,
`CompRandomizeUnfinished.cs:103`). Several carry their author's own deferred-tuning note, so they are
flagged-unfinished rather than settled — but that does not make them Jev opportunities.

**The first draft's criterion was wrong.** "The game cannot tell apart two situations a player can"
is not a defect criterion: a game may deliberately ignore a distinction to preserve uncertainty,
fairness, pacing, or a rule players can learn. What is needed is a *desired behavioural difference*,
not an available input feature.

On inspection most of these want something other than a model:

- **Missing numerical features, not missing judgment** — `SUULK_ENTICEMENT` needs a real light-exposure
  or habitat measure computed spatially; Jev cannot spare the calculation and adding it to a derived
  score buys nothing.
- **A missing policy definition** — `ELDER_NOVELTY` needs persistent encounter history and an
  equivalence policy. If novelty means "first of each kind", string identity is already right. A
  familiar item with a florid rewritten description must not become valuable again.
- **An explicit utility rule** — `ANIMAL_THEFT_WORTH`: an animal taking the most *valuable* object is
  less believable than one taking the nearest food or nesting material. "Worth" needs a
  species-specific objective.
- **A deliberate pacing constraint, possibly** — `CONTAGION_BUD`'s independent 12%, and
  `NINEFOLD_FRONT_SWING`'s magnitude threshold. No player-facing problem has been shown with either.
- **An observability decision first** — `GATE_SEARCH`: if the model sees actual contraband, guards
  become selectively omniscient. Specify what a guard may observe and what the player can learn.

Three further corrections that apply to any future runtime use:

- 🔴 **A Noul is not an authored rate.** "How confident are you a search is warranted" is not "what
  fraction of otherwise identical departures should produce a search". Sampling a game event from the
  first number is a design choice, and calling it a probability does not justify it.
- 🔴 **A Score is a probability-weighted mean of level indices.** Half the probability on levels 0 and
  2 yields the same mean as certainty at level 1 — so it silently collapses "either harmless or
  alarming" into "middling". Preserve the distribution; put policy in code.
- 🔴 **Typed selection does not establish authority.** The first draft claimed Jev's shape
  *structurally satisfies* the Oracle's text/menu-authority law. **That claim is withdrawn.** A legal
  `RaidStrategyDef` can still be wrong for the faction, map, budget or scenario, and independently
  selected composition elements can violate a joint constraint. The enumerated option set and the code
  executing it establish the authority boundary — not the absence of prose. Runtime use would still
  need candidate eligibility checks, joint-constraint enforcement and an explicit application policy.
- **"Async" does not buy lifecycle correctness.** A theft target can vanish in flight; a fallback can
  already have fired when a late answer lands. That needs snapshot identity, revalidation, deadlines,
  at-most-once application, and save/reload that does not silently redraw a decision — all of it true
  even when every response arrives in 200 ms correctly typed.

**Disposition:** keep Part 4 as separately commissioned game-design exploration, contingent on the
owner's transport ruling. `src/RimMandrake/RaidRedesigner/` remains a real mod whose Oracle wiring is a
settings toggle rather than calls, so that seam is unspent — but it is not a first-round candidate.

---

## Calibration: what we actually have

The first draft claimed three ground-truth datasets and called this the most important practical note
in the document. **That claim is withdrawn.** We have three collections of *historical records*, some
of which may contain usable labels. The difference matters because it is the difference between
"answerable now" and "a project".

| Collection | What it establishes | What it does **not** |
|---|---|---|
| Review-sheet `*.decisions.json` | The owner chose a disposition for a row in a sitting | That the row held a canon contradiction, or a valid migration rationale |
| 863 closed items | Those items reached a closed status | Which pairs are duplicates, or whether a mechanism existed when another was filed |
| 29 canon rulings | The owner issued those rulings | A representative contradiction sample, or calibration across the other 108 |

Four traps, all accepted:

- **The 863 closed items are objects, not 863 duplicate labels.** Only explicit recorded duplicate
  relationships are labels.
- **A review-sheet cut may have been about that sheet's scope**, not about anything wrong with the
  creature — using it as a contradiction label would violate the scoping rule we correctly keep
  elsewhere.
- **"Not overturned" is not "affirmatively verified."** An overturned prefill is real evidence of
  disagreement; a retained one may be deliberate agreement or a persisted default. Check what the
  interface records before assuming equal scrutiny.
- **Leakage: reconstruct what was knowable at decision time.** Do not grade a model on an
  already-corrected Visual Brief against the verdict that caused the correction, and do not search
  *current* source to ask whether an implementation was discoverable before a past re-invention. Where
  the owner decided from an image or from a whole-sheet comparison, mark the record **not evaluable
  for this question** — decided in advance, never after seeing the output.
- **The 29 reviewed entries may be the most contentious or simply the earliest**, and hundreds of
  characters from a few templates are not hundreds of independent tests. Split by family, batch or
  period, not by random rows sharing near-identical text.

**Calibration is also not the thing we need.** A predictor returning 0.10 for every record can be
perfectly calibrated where 10% of records carry the defect, and useless for ordering a queue. Measure
what the workflow needs: useful findings inside a fixed review budget, false alarms requiring
investigation, missed known cases, and the share where supplied evidence is insufficient. For
re-invention, **measure retrieval separately from judgment.**

🔴 **The economics that the first draft got backwards.** Jev's price is not the binding cost. A
1,000-item sweep with 1% true defects at 90% recall and a 5% false-positive rate yields ~9 true alerts
and ~50 false ones. **Cheap inference readily buys expensive owner attention** — which is the one
budget this project cannot refill.

The defensible conclusion may be *"we have useful regression cases, but not enough compatible labels
for calibration."* That is a result, not a failure.

---

## What becomes expensive to change later

The HTTP client is not the lock-in. The judgment definitions, the evidence preparation, and the habits
are.

- **Thresholds** belong to a model version, a question wording, an option set and an input
  construction. TypeSafe's own docs say an alias moves when a release ships and recommend pinning the
  versioned ID once thresholds are tuned.
- **Taxonomies** — once thirty consumers understand your categories and Score levels, changing them is
  a data migration. The risk is not replacing Jev; it is discovering that "contradiction", "duplicate"
  and "review cost" were badly defined.
- **Evidence preparation** — the retrieval index, an effective-def export, claim decomposition and
  context assembly can end up larger than the integration, and need maintenance as the suite changes.
- **Historical results** — cached judgments are uninterpretable later unless the input hash, model
  version, question version, candidate set and the underlying distribution are stored **separately
  from the action taken**. A dismissed warning is not a false judgment.
- **Workflow** — "advisory" acquires de facto authority. Agents will stop searching after "no
  duplicate found", and the owner may never see what is repeatedly ranked last. Never let a model
  negative erase a candidate or retire existing evidence.
- **Runtime** — once players have experienced a succession or economy policy, changing provider becomes
  changing gameplay. Saved decisions and fallback semantics become part of the product.

## 🔴 The trust boundary nobody in the scan noticed

**Almost everything we would ask Jev to judge is agent-authored — and Jev's own documentation says it
does not treat `state` as hostile, and that "text that argues for its own classification" can move the
answer.**

Our queue items, item prose, commit bodies and design docs are written by agents that have an interest
in the verdict. A commit body reading *"this is a cosmetic change; no live proof is required"* is
exactly the shape the jaggedness page warns about, aimed at exactly the checks Part 1 proposes. Typed
answers do not prevent it.

⇒ Keep source material separate from authoritative policy, and test these cases deliberately before
treating a high-confidence answer as permission. For any distributed runtime use, also settle who
supplies credentials, who pays, and what player or save data leaves the machine — "two transports" is
not an operational answer to those.

---

## The first experiment

Not a shortlist of five. **One bounded text-comparison trial, plus one retrieval diagnostic.**

**A. The retrieval diagnostic, on the documented re-invention incidents.** Replay each against the
repository state *as it was before* the mistake, in three conditions:

| Condition | What it tells you |
|---|---|
| Current retrieval, shown without Jev | Whether ordinary discovery already surfaces the implementation usefully |
| Identical candidates, ranked or classified by Jev | Jev's incremental contribution |
| Known implementation evidence deliberately included | Whether judgment works when retrieval succeeds — a diagnostic, not a production result |

If the implementation never enters the candidate set, **stop improving the judge**: detection is
`P(retrieved) × P(detected | retrieved)`, and 60% recall with 95% conditional detection is 57%
end-to-end. If it was already prominently displayed, the question is why an agent ignored it, which no
model fixes. Our strongest documented failure is **not yet** our strongest argument for Jev.

**B. The text-comparison trial: the stale-citation evaluator (1.1).** It has the cleanest shape —
both texts supplied, no effective-behaviour representation needed, a deterministic baseline already in
place for finding the citations, 130 real candidates, and a downstream action that is a warning on an
item nobody has claimed yet.

**The success criterion:** not that Jev emits plausible answers cheaply across the corpus, but that
**one narrowly defined use saves more investigation than it creates, without converting missing
evidence into apparent certainty.**

---

## Review record

GPT's review is treated as guidance, not authority, per standing rule. Accepted in full: the central
error, the omitted-input counterexample, the Choice-meaning and option-cap corrections, the negative's
overclaim, the calibration downgrade, the lock-in analysis, the Noul/Score semantics, the withdrawal of
the authority claim, and offline semantic compilation as the missed category. Its three interface
claims were **verified against `docs.typesafe.ai` before being written here** — all three held.

**Contested:** the review framed the runtime seams as "uncommissioned design changes". Several are
their own author's explicitly deferred tuning (`GateSearchHook.cs`'s header defers "real per-faction
tuning"; the Elder novelty check is marked `[INVENTED, flagged]`), so they are flagged-unfinished
rather than uncommissioned. This strengthens rather than weakens the conclusion: they are real owed
design decisions, and most of them want explicit rules or missing numerical features rather than a
model.
