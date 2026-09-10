# How should we store the canon? — options, tradeoffs, and a recommendation

_A design-discussion report (task product for later review), BENCH, 2026-09-10.
Written at the owner's request; nothing here is decided or applied. Informed by a
web pass on current practice — sources at the end._

Storytelling is an unfolding process, not a one-time delivery. So the real question
is not "what's the best knowledge store" in the abstract — it's **which store lets a
living, growing canon stay retrievable, updatable, and self-consistent without a
heroic clean-up every few weeks.** That reframes the whole thing: good storage is the
thing that makes `CANON_DRAIN_1` a *continuous property* instead of a recurring event.

## The one trap, stated first

Every serious source says the same thing in different words: **have exactly one source
of truth, and never let a second one drift.** The story-bible world puts it bluntly —
"if it isn't in the bible it isn't canon" turns the bible from documentation into
*governance*; and **"a lighter document you update beats a thorough one you abandon,
because an out-of-date bible actively misleads."** Our failure mode is not too little
lore — it's a second, stale copy of a fact that someone trusts. Any design is judged
first on whether it makes drift *impossible* or at least *loud*.

## The three families (and where a knowledge graph fits)

### A. Narrative-primary — prose is truth, claims derived on demand (what we do now)
The docs are canonical; when we need a fact we read/extract it (effectively what
`doc_claims.py` + our sittings do).
- **a) Retrieval:** slow and lossy at scale — you re-read prose to answer, and overlap
  between docs means the same fact is stated (and can rot) in several places.
- **b) Updatable:** excellent — editing prose is natural, and prose is what storytelling
  *is*. This is the family's real strength and why we shouldn't abandon it.
- **c) Self-healing:** weak — nothing detects that doc X now contradicts doc Y. Drift is
  invisible until a human trips on it. This is the pain you're feeling.

### B. Fact/atom-primary — a database of atomic claims, narrative composed from them
Invert it: the atoms are canonical, prose is generated/assembled on demand.
- **a) Retrieval:** excellent — atomic claims "chunk" perfectly for lookup and for
  vector/graph search; each is standalone.
- **b) Updatable:** good for *facts*, bad for *voice*. The atomic-notes world's own
  warning: over-atomizing accrues "technical debt," and **a story told from atoms loses
  its soul** — prose carries tone, rhythm, implication that no fact table holds. You'd be
  maintaining a database and *still* writing the prose.
- **c) Self-healing:** strong — atoms are where contradiction/gap checks are cheap.
- **Verdict:** the wrong master. We are a *storytelling* project; the narrative cannot be
  the derived artifact.

### C. Hybrid — canonical prose + a thin derived index of claims/entities (the Dialexis shape)
Prose stays the source of truth. On top of it sits a **mechanically-maintained index**:
each fact extracted as an atomic claim, tagged to the entities it's about, **carrying a
provenance link back to the exact prose line**, and answered from the index — *falling
back to the source doc when the index can't answer, to be sure it wasn't just an
extraction error.* This is exactly the method you described, and the research calls it
the robust pattern: retrieve from the fast layer, verify against source.
- **a) Retrieval:** fast (query the index) with a correctness backstop (fall back to prose).
- **b) Updatable:** you still edit prose naturally; the index is *regenerated*, never
  hand-kept, so it can't drift from the prose — the single-source rule is preserved by
  construction.
- **c) Self-healing:** this is where it earns its keep (next section).
- **Cost:** the index + checker is real work, but far less than a full ontology.

**Where a knowledge graph fits:** a KG is one *shape* of the index in family C — entities
as nodes, relations as edges. The 2025 head-to-heads are clear: graph retrieval wins
**multi-hop and "global sense-making"** questions ("how do the Cathedral, the Scald, and
the Deeps connect?"), plain vector/text retrieval wins **single-hop factual lookup**
("what colour is the Scald water?"), and **neither wins outright.** A full KG also costs
*weeks–months of ontology work* and doubles memory. So: **graph the relationships you
actually need multi-hop answers over (factions, sites, the terramanufacture chain), and
do not graph everything.** "Stop graphing everything" is the current consensus.

## The three cross-cutting dimensions that decide the design

### 1. Provenance + the self-healing engine (borrow from truth-maintenance systems)
Classical **truth-maintenance / belief-revision** systems keep, for every belief, a
*dependency record* of what it rests on. When a belief is retracted, everything derived
from it is automatically flagged as needing re-examination. That is precisely our
"self-healing" wish. Concretely, for us:
- Each claim in the index carries **provenance** (which doc/line) and, where it's a
  *consequence* of a ruling, **what it depends on**.
- When a ruling changes (e.g. today's coolant-leak retirement, or "the Overdrive is now
  the Helix's name"), the checker lists every claim that depended on the old truth and
  says "these need review." The drain stops being a blind full sweep and becomes a
  **worklist of exactly what the last change disturbed.**
- Two cheap checks give most of the value without any AI: **contradiction** (two claims
  about the same entity+attribute disagree) and **gap** (an entity a sitting will touch
  has thin or no coverage). Run them on write, or nightly.

### 2. Time — canon evolves, so distinguish two clocks (bitemporal)
The literature's "bitemporal" idea is worth stealing in miniature: separate **valid time**
(true *in the fiction* — "before the collapse" vs "now") from **transaction time** (when
*we decided* it). We already do the second informally with dated amendments; making it
explicit means a query can ask "what's canon *as of now*" and cleanly ignore superseded
records without deleting the history (git already holds transaction time for free). This
is also what lets "supersede" be safe: the old record is *time-bounded*, not lying.

### 3. Certainty — your specific question: helpful or hurtful?
**Helpful — but only as a small ordinal tier, never a numeric confidence score.** The
research offers weighted triples with a confidence `st ∈ [0,1]`; for a hand-authored
lore corpus that's *false precision nobody will maintain* (is a fact 0.7 or 0.8?). What
*is* powerful is a 3–4 rung ladder, and it maps onto something storytellers already do —
the "working bible vs published bible" split:
- **Bedrock** — driving truths that will not change (the world is tidally-locked; the
  Scald sources the rivers; the Assailants ruined everything). These are *invariants*:
  the checker treats a new claim that contradicts bedrock as an automatic error, and the
  drain never touches them.
- **Ruled** — decided at a sitting, stable, citable.
- **Tentative / provisional** — floated, not yet ruled; agents must not build load-bearing
  work on these, and the drain is *allowed* to prune them.
So certainty does three jobs: it tells an agent **how much to rely** on a fact, it tells
the drain **what's safe to grind vs what's load-bearing**, and bedrock facts become the
**anchors the contradiction-checker measures everything against.** That last one is the
self-healing keystone — without a "this cannot change" set, a consistency checker has no
fixed point. So: include it, keep it ordinal and few-runged.

## What I'd actually recommend for *this* project

We are git-backed markdown, multi-agent, no infra team, and the prose *is* the product.
That rules out a heavy graph-DB (too much ontology work for an evolving world) and rules
out atom-primary (kills the storytelling). The fit is **family C, built in cheap phases**:

- **Phase 0 (cheap, high-value, do first):** add **certainty tiers** and **entity tags**
  to how we record facts, and keep the delete-don't-supersede discipline (already in
  force). This alone makes the eventual drain far smaller and gives agents a reliance
  signal. Extend `doc_claims.py` to emit claims with `{entity, attribute, value,
  provenance, certainty, valid-time}`.
- **Phase 1 (the self-healing engine):** a checker over that claim index — contradiction
  (same entity+attribute, disagreeing values across docs) and gap (entities with thin
  coverage), plus the dependency flag (a changed ruling lists its dependent claims). This
  is the thing that converts `CANON_DRAIN` from a periodic heroic event into a standing
  green/red signal.
- **Phase 2 (only if multi-hop retrieval hurts):** promote the entity index to a light
  knowledge graph for the *relationship* questions (factions ↔ sites ↔ history), leaving
  single-fact lookup on the text index. Graph the connected subsystems, not the whole
  corpus.

Prose stays canonical throughout. The index is always *derived and regenerable*, so there
is never a second source of truth to drift — the one trap, designed out by construction.

**The payoff line:** good storage doesn't replace the drain — it makes the drain
*continuous and cheap* by turning "is the canon consistent?" into a query you can run any
day, and turning "what did this new ruling break?" into a generated worklist.

## Open questions for the review sitting
1. Is Phase 0 worth doing *before* the big fauna/flora wave, or fold it into `CANON_DRAIN_1`?
2. The bedrock set — who blesses a fact as "will not change"? (Likely: only you, explicitly.)
3. Tooling home: extend the existing `doc_claims.py` / measure DB, or a small new store?
4. Do we want the checker to run on every commit (a hook), or as an on-demand sweep?

## Sources
- [Knowledge Graph vs RAG: when each wins](https://atlan.com/know/knowledge-graphs-vs-rag-for-ai/) · [VectorRAG vs GraphRAG technical challenges](https://www.falkordb.com/blog/vectorrag-vs-graphrag-technical-challenges-enterprise-ai-march25/) · [Stop graphing everything (VentureBeat)](https://venturebeat.com/orchestration/stop-graphing-everything-when-graphrag-actually-beats-vector-rag)
- [Reason maintenance (Wikipedia)](https://en.wikipedia.org/wiki/Reason_maintenance) · [Truth maintenance systems tutorial (IEEE)](https://dl.acm.org/doi/10.1109/64.363270)
- [Towards Probabilistic Bitemporal Knowledge Graphs](https://dl.acm.org/doi/fullHtml/10.1145/3184558.3191637) · [Uncertainty management in knowledge graphs: a survey](https://drops.dagstuhl.de/storage/08tgdk/tgdk-vol003/tgdk-vol003-issue001/TGDK.3.1.3/TGDK.3.1.3.pdf)
- [How to build a story bible](https://app.blurbbio.com/blog/how-to-build-a-story-bible) · [What is a production bible (Storyflow)](https://storyflow.so/blog/what-is-a-production-bible-complete-guide)
- [Evergreen notes should be atomic (Matuschak)](https://notes.andymatuschak.org/Evergreen_notes_should_be_atomic) · [Principle of atomicity](https://memo.d.foundation/topics/zettelkasten/how-to-take-smart-notes/principle-of-atomicity)
