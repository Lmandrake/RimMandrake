# CANON_CLAIM_TAGGING_1 — Canon storage Phase 0: certainty tiers + entity tags

Owner-adopted 2026-09-12, per `design/CANON_STORAGE_ARCHITECTURE_options.md`'s
recommendation ("Phase 0 (cheap, high-value, do first)"): add certainty tiers and
entity tags to how facts are recorded, extending `doc_claims.py` to emit
`{entity, attribute, value, provenance, certainty, valid-time}`. This is data-shape
only — the contradiction/gap checker over this shape is `CANON_CONSISTENCY_CHECKER_1`
(Phase 1), a separate later item, not built here.

## What changed

`src/RimMandrake/Utils/doc_claims.py`:
- `claims(text)` — the existing mechanical splitter (prose/table/code, one claim per
  sentence-ish unit) — is **unchanged in behavior**, only additive: each claim dict
  now also carries `line_start`/`line_end` (1-indexed, into the source text). The
  two-blind-arms audit and `CANON_DRAIN_1` keep working unmodified; claim counts are
  identical to before this change.
- New `tag_claim()` / `tagged_claims()` and CLI flag `--tag` add the Phase 0 shape as
  an opt-in output, so nothing that already calls this file breaks.

## Output schema (`--tag`)

```
{
  "id": int,                       # same numbering as the base claims() output
  "entity": str | null,            # best-effort subject: bold span > code span >
                                    #   Title-Case run > nearest heading > null.
                                    #   null (not guessed) for table/code claims —
                                    #   a table has no single subject.
  "attribute": str | null,         # text up to the first copula/verb (is/are/has/
                                    #   must/cannot/...), trimmed to <=8 words. null
                                    #   when the sentence doesn't split cleanly —
                                    #   most prose doesn't, and that's the correct
                                    #   degrade, not a bug (see file docstring).
  "value": str,                    # text after the attribute split, or the full
                                    #   claim text when attribute is null, or the
                                    #   whole table/code block verbatim.
  "provenance": {
    "doc": str,                    # source file path, as given on the CLI
    "heading": str,                # nearest markdown heading above the claim
    "line_start": int | null,
    "line_end": int | null
  },
  "certainty": "BEDROCK" | "RULED" | "TENTATIVE" | null,
  "valid_time": "YYYY-MM-DD" | null,   # first ISO date found in the claim text or
                                        #   its heading; null when none is present —
                                        #   never fabricated (most older claims carry
                                        #   no date and stay null, as expected)
  "kind": "prose" | "table" | "code",
  "text": str                      # the original claim text, for reference/debug
}
```

### Certainty vocabulary — taken from the architecture doc, not invented

`design/CANON_STORAGE_ARCHITECTURE_options.md` §"3. Certainty" names exactly three
rungs: **Bedrock** (driving invariant; a contradiction is an automatic error),
**Ruled** (decided at a sitting, stable, citable), **Tentative/provisional**
(floated, not yet ruled, safe to prune). `doc_claims.py` uses those three tier names
verbatim (`BEDROCK`/`RULED`/`TENTATIVE`) and nothing else. Detection is regex over
the claim text + its heading:
- `RULED` — "OWNER'S RULING"/"ruled"/"CLOSED"/"DECIDED"/"SUPERSEDED"/"adopted"/an
  "(owner, YYYY-...)" or "— owner, YYYY-..." byline. (An explicit "⛔ SUPERSEDED"
  banner counts as RULED: supersession is itself a ruling — that a thing is dead.)
- `TENTATIVE` — "draft"/"proposal"/"PLANNING DOC"/"not ruled"/"speculative"/
  "candidate"/"open question"/"provisional"/"under discussion".
- `BEDROCK` — literal "bedrock"/"invariant"/"never changes"/"permanently". Rare by
  design: the architecture doc itself flags "who blesses a fact as bedrock?" as an
  open question for the owner, so this tier is only lit by an explicit textual
  marker, never inferred from tone.
- No marker found → `null` ("unspecified"), not a default tier. Guessing RULED for
  unmarked prose would fabricate confidence the text doesn't carry.

## Test evidence (real corpus, real values, nothing fabricated)

Ran `--tag` against three docs under `design/Jawa/`:

| doc | claims | kinds | certainty tagged | table/code claims with entity guessed (should be 0) |
|---|---|---|---|---|
| `droid_ruling.md` | 242 | prose 226 / table 10 / code 6 | RULED 24, TENTATIVE 1, null 217 | 0 |
| `canon_reintegration_plan.md` | 177 | prose 173 / table 4 | RULED 34, BEDROCK 3, TENTATIVE 2, null 138 | 0 |
| `first_contact_chains.md` | 78 | prose 78 | RULED 2, null 76 | 0 |

Default (no `--tag`) claim counts on the same files are identical to the tagged
counts (242 / 177 / 78) — confirms the base extraction is unchanged.

Sample real triple (from `droid_ruling.md`, id 1, the file's own supersession
banner):
```
entity: "SUPERSEDED"
certainty: "RULED"
valid_time: "2026-09-06"
provenance: {doc: "design/Jawa/droid_ruling.md", heading: "", line_start: 1, line_end: 2}
value: "no rogue droid faction and no droid faction of any kind; droids are fielded
        inside every faction's own loadouts and the capture line is the Empire's
        attack droids: `design/Jawa/droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md` §0
        ruling 2 ..."
```
All values above are copied straight out of the extraction run against the real
file — no hand-authored example data.

## Known limitations (honest, not blocking)

- `attribute`/`value` splitting is a first-copula heuristic; on ~55-90% of prose
  claims (varies by doc) it finds no clean split and falls back to
  `attribute=null, value=full text` — expected for a storytelling corpus where most
  sentences aren't subject-verb-object facts. This is the documented degrade, not a
  defect: forcing structure onto prose that doesn't have it would fabricate data.
- `entity` extraction is lexical (bold/code/Title-Case), not semantic — it can pick
  a stray capitalized phrase over the "real" subject. Acceptable for Phase 0: the
  field exists and is populated from real text; refining it is exactly the kind of
  thing Phase 1's checker usage will pressure-test and improve.
- `valid_time` only looks at the claim's own text and its nearest heading, not
  further up the doc (e.g. a byline date one paragraph above with no heading
  between). Undercounts dates rather than ever inventing one.

## Closing

Criteria met: `doc_claims.py` extended to emit the exact
`{entity, attribute, value, provenance, certainty, valid-time}` shape the queue
summary specified, using the certainty vocabulary the architecture doc actually
names, tested against three real `design/Jawa/` docs with real (non-fabricated)
extracted values, base extraction behavior unchanged for existing callers.
Phase 1 (`CANON_CONSISTENCY_CHECKER_1`) is intentionally not started here.
