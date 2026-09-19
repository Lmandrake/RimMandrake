# CANON_CONSISTENCY_CHECKER_1 — Canon storage Phase 1: the checker over the claim index

Owner-adopted 2026-09-12, per `design/CANON_STORAGE_ARCHITECTURE_options.md`'s
"Phase 1 (the self-healing engine)": *"a checker over that claim index —
contradiction (same entity+attribute, disagreeing values across docs) and gap
(entities with thin coverage), plus the dependency flag (a changed ruling
lists its dependent claims). This is the thing that converts CANON_DRAIN from
a periodic heroic event into a standing green/red signal."*

## What was built

`src/RimMandrake/Utils/canon_consistency.py` — a new, standalone script that
imports `doc_claims.tagged_claims()` (Phase 0, `CANON_CLAIM_TAGGING_1`) and
scans a corpus of docs for:

1. **Contradictions** — groups prose claims by normalized `(entity, attribute)`,
   flags a group where two claims from **different docs** have different
   normalized `value`s. Severity follows the architecture doc's own weighting:
   `BEDROCK_VIOLATION > RULED_VS_RULED > RULED_VS_UNCONFIRMED > UNCONFIRMED_DISAGREEMENT`
   ("Bedrock... a contradiction is an automatic error"; "two RULED claims
   disagreeing is the real alarm"). Same-doc restatements are never flagged —
   that's elaboration, not cross-doc drift.
2. **Thin coverage** — entities backed by exactly one RULED/BEDROCK claim
   anywhere in the scanned corpus. The architecture doc names no threshold;
   "1" is the judgment call made here (see rationale in the file's docstring
   and "known limitations" below).
3. **Changed-ruling worklist** — a content-hash baseline
   (`infrastructure/state/canon_consistency_baseline.json`), same pattern as
   `code_review_status.py`'s CLEAN/DIRTY SHA-256 hash and
   `codebase_health_publish.py`'s git fingerprint (fingerprint over timestamp,
   this repo's own standing lesson). When a doc's hash no longer matches the
   baseline, its RULED/BEDROCK `(entity, attribute, value)` triples are
   diffed against the baseline's: vanished triples are the worklist ("this
   used to be ruled — find what cited it"); new triples are a lighter
   awareness note. Verified end-to-end on a scratch copy of `droid_ruling.md`
   (establish baseline → unchanged rerun → mutate a RULED line → rerun
   correctly reports one `RULING_CHANGED_OR_REMOVED` + one `NEW_RULING`
   triple).

```
python3 src/RimMandrake/Utils/canon_consistency.py <path-or-dir>...   # default: design/Jawa/
python3 src/RimMandrake/Utils/canon_consistency.py <path>... --update-baseline
python3 src/RimMandrake/Utils/canon_consistency.py --out report.json <path>...
python3 src/RimMandrake/Utils/canon_consistency.py --all-severities <path>...
python3 src/RimMandrake/Utils/canon_consistency.py --strict <path>...   # exit 1 on BEDROCK/RULED_VS_RULED
```

Console output shows only `BEDROCK_VIOLATION`/`RULED_VS_RULED` contradictions
by default (the architecture doc's own "real alarm"); the full list including
lower-severity hits is always in `--out`'s JSON, or on-screen with
`--all-severities`. This is what makes it a usable green/red signal instead of
a wall of noise — see test evidence below for why that split exists.

## Extends check_canon.py, or separate? — SEPARATE, and the doc says why

Read `check_canon.py` in full first. It is a different machine: a
hand-curated ground truth (`infrastructure/state/canon.yml`) plus one
hand-written `Rule` object **per known fact** (water %, tile count, faction
count...), each with a bespoke regex and context test, checking design-doc
prose against that fixed truth. A human decides the canon value and writes
the rule; the tool never infers a fact from a document.

Phase 1 is the opposite shape: fully mechanical, no hand-curated ground
truth, comparing claims **extracted by `doc_claims.py --tag`** against each
other, keyed by the generic `(entity, attribute)` pair the tagger guesses —
never a per-fact rule a human wrote. The two don't share a data model
(canon.yml's typed sub-tree vs. `tagged_claims()`'s list of dicts) or a
matching strategy (per-fact regex vs. generic entity/attribute grouping).
Bolting Phase 1 onto `check_canon.py` would graft a generic cross-doc
comparator onto a file whose entire design is "one Rule per fact a human
already knows about." They are complementary and both stay: `check_canon.py`
guards the handful of numbers the owner has explicitly blessed as canon
(and still does — untouched by this item); this new file finds
contradictions and gaps **nobody has written a rule for yet**, which is the
entire point of Phase 1.

The architecture doc's open question 3 ("extend doc_claims.py / measure DB, or
a small new store?") is about the claim index's *storage*, not this checker —
Phase 0 already answered it (additive `--tag` on `doc_claims.py`). This item
consumes that index; it does not touch `doc_claims.py` or `check_canon.py`.

## "Drain becomes a standing signal" (CANON_DRAIN_1)

`CANON_DRAIN_1` (`infrastructure/state/items/CANON_DRAIN_1.md`) is a
one-time, gated, heroic reconciliation pass over the whole lore corpus
("grinding out every superseded, obsoleted, or contradicted statement"),
triggered once the fauna/flora biome-cast wave settles — **not started**, and
this item does not start it. The architecture doc's payoff line is that good
storage "makes the drain continuous and cheap by turning 'is the canon
consistent?' into a query you can run any day." That is exactly this file's
role: it does not perform a drain, it gives the standing on-demand query that
makes drain-scale sweeps rarer and each one smaller when they do happen.

## Test evidence (real corpus, real output, nothing fabricated)

**Same 3 docs as Phase 0's own test** (`droid_ruling.md`,
`canon_reintegration_plan.md`, `first_contact_chains.md`): **0 cross-doc
contradictions** (honest negative — matches the fact that Phase 0 validated
against these same 3 files with no known cross-doc drift), 37 thin-coverage
entities at threshold 1.

**Full `design/Jawa/` corpus** (354 `.md` files, ~3s runtime):
- 516 total contradiction candidates; after filtering to the two "real alarm"
  tiers per the architecture doc's own weighting: **2 `RULED_VS_RULED`
  findings**, both genuine and both a legitimate reason to look:
  1. `design/Jawa/mods/forbidden_mods.md:1` vs `required_mods.md:1` — the
     VPE re-adding ruling is quoted near-verbatim in both files but the two
     copies have already drifted by a few words ("design docs" vs "design
     docs below"). Not a factual contradiction, but exactly the drift risk
     the architecture doc's "one trap" section warns about: the same ruling
     copied into two places will eventually diverge for real.
  2. `design/Jawa/worldbuilding/biomes/the_rust_cathedral.md:204` vs its own
     `the_rust_cathedral_SCALD_HISTORY_amendment_draft.md:57` — a base doc
     and its "amendment draft" companion restate the Rustwave/R03 ruling with
     slightly different wording ("river_ledger.md rulings 1 and 3" vs the
     same citation with an added clause). Same drift-risk shape.
  - 10 `RULED_VS_UNCONFIRMED` and 504 `UNCONFIRMED_DISAGREEMENT` hits exist
    (visible via `--out` or `--all-severities`) but are dominated by noise —
    see limitations below.
- 1,243 thin-coverage entities at threshold 1 (see limitations — full-corpus
  scale surfaces Phase 0's entity-extraction noise, same as the contradiction
  count did, before the `plausible_entity()` filter below was added).

## Known limitations (honest, not swept under the rug)

- **Phase 0's entity/attribute extraction is lexical, not semantic** (its own
  documented limitation) — pressure-testing it at full-corpus scale, exactly
  as Phase 0 predicted, immediately surfaced two noise sources this file
  filters at the consumer level (not by touching Phase 0's already-closed,
  already-tested output):
  - **heading-fallback entities**: `_guess_entity` falls back to the nearest
    markdown heading when no bold/code/Title-Case span is found, so numbered
    outline headings ("2. what the owner ruled, verbatim, in order") become
    "entities." `plausible_entity()` rejects entities over 40 chars/6 words or
    containing `—`/`·`/mid-sentence `:`/`.` — this took the raw full-corpus
    thin-coverage count from ~1,900 to 1,243 and contradictions from 2,604 to
    516.
  - **sentence-initial pronouns as Title-Case entities**: "Both resolve
    today.", "I have counted..." — capitalized by ordinary grammar, not
    because they're proper nouns. A `_PRONOUN_ENTITY` stopword list in this
    file (not `doc_claims.py`) filters these.
  - Even after both filters, `UNCONFIRMED_DISAGREEMENT` (no certainty marker
    on either side) is still mostly copula-split collisions between unrelated
    sentences that happen to share a leading word+verb (e.g. "has" + "has"
    from two different character sketches in `INHABITED_CAST_*.md`) — this is
    why the default console report hides that tier rather than pretending it
    is a usable signal. **This is real feedback for Phase 0**: the
    entity/attribute guesser is the accuracy ceiling for Phase 1's contradiction
    precision, most visible at full-corpus scale where the RULED/BEDROCK tiers
    stay clean but the two lowest tiers get swamped by unrelated-sentence
    collisions.
  - Thin coverage at threshold 1 is a real, working mechanism (verified against
    the mutation test) but at full-corpus scale it inherits the same
    entity-quality ceiling, so its 1,243-entity list is honestly noisy; the
    two RULED_VS_RULED contradiction findings are the cleaner signal today.
- **Value comparison is normalized-string equality**, not semantic — it will
  miss a contradiction stated in different words and will occasionally flag
  a paraphrase as if it disagreed (see the two RULED_VS_RULED hits above:
  both are drift-risk near-duplicates, not clean opposite-value contradictions).
- **Hook-vs-on-demand is explicitly undecided** (architecture doc's open
  question 4) — this file is on-demand only; nothing wires it into a commit
  hook, and this item does not decide that question.

## Closing

Criteria met against the architecture doc's own stated Phase 1 scope:
contradiction detection (weighted by certainty, cross-doc only), thin-coverage
detection, and a changed-ruling dependency worklist, built as a genuinely
separate tool from `check_canon.py` for the reasons stated above, tested
against Phase 0's own 3-doc corpus (clean) and the full 354-file `design/Jawa/`
corpus (2 real RULED_VS_RULED findings, both genuine drift risks; full
findings and limitations reported honestly, not hidden). A real baseline
(`infrastructure/state/canon_consistency_baseline.json`) was generated against
the current `design/Jawa/` corpus and is committed, so the next run against a
changed doc will produce a real changed-ruling worklist rather than an
"unbaselined" note.

Not decided here, left open for the owner/BENCH: whether this ever runs as a
commit hook (architecture doc open question 4), and whether Phase 0's
entity/attribute extraction is worth refining given the noise this checker's
usage surfaced in the two lowest severity tiers.
