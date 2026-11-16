# The mod ledger's entry standard: what goes in, how small, how it is searched

Item: `RIMMANDRAKE_DESIGN_MOD_LEDGER_ENTRY_STANDARD_SMALL_SEARCHABLE` · design helper, Sun 2026-11-15 ~10:20 PM PST.
Refines the entry rules inside `design/specs/2026-11-15-holder-pipeline-fusion.md` §3.1–3.3 (whose decisions stand);
the tool is `src/RimMandrake/rimflow/modledger.py` (landed `6b4fb634a7`). Measurement for §5:
`design/specs/2026-11-15-mod-ledger-entry-standard/worked_example.py` (exit 0 = the ten tickets pass the standard and
the five planted bad entries are refused).

The owner, 2026-11-15 ~10:03 PM PST: *"We should also think of a way to structure this ledger per mod so it is not
arbitrary in size and pedantic detail. Are there standards in what to put here that will be useful and how to structure
it for rapid search?"*

Tags: `[measured]` (how is said) · `[guess ~N%]` · `[read]` a source read on its page this run · `[snippet]` a source
seen only as a search result.

---

## The rule sheet (one page, for every writer and miner)

**The test for every entry:** *would a holder picking this mod up in a month act differently because of it?* If not,
do not write it. Everything below is that test made checkable.

1. **One fact, one entry.** One event says one thing about one subject. Two facts are two events (a ticket that holds a
   finding and an instrument trap mines into a `finding.open` and a `trap.noted`).
2. **Small, and the tool refuses bigger.** `text` ≤ 320 characters, `proposed_fix` ≤ 320, `accept` ≤ 240, his
   verbatim `said` ≤ 600; one paragraph, no newline; the whole line ≤ 1,536 bytes. Nothing is spilled to a side file:
   an oversize entry is refused, with how to split it.
3. **Evidence by reference, never pasted.** Up to 6 typed refs, each ≤ 160 chars: `sha:` (the sha `./publish`
   printed, never a pre-landing one), `path:` (a repo path, optional `#row`), `ext:` (outside git: `D:\ClaudeWork\…`,
   `Transient/…`), `test:` (a command or test id), `run:` (a run or testq job id), `item:` (a rimflow ticket),
   `ledger:` (a ledger event), `card:` (a card id). Logs, stacks, diffs, code and tables stay in their files.
4. **Use the subject that exists.** Subjects are `bar:<bar id>`, `finding:<NAME>`, `cause:<slug>`, `trap:<slug>`,
   `q:<slug>`, or a singleton (`stage`, `version`, `session`). Before minting one, `modledger find` it; the append
   refuses a new subject that matches a live one unless you say why it differs.
5. **Change by a new entry, never by editing.** A later event moves a subject's status or supersedes an earlier event;
   the shard only grows.
6. **Every kind has its required fields** (table §2.2). `finding.open` needs `class`, `bars`, `text`,
   `proposed_fix`, `accept` (a runnable command and expected result, or `none, <reason>`). A fix claim or verdict needs
   `code_sha`. A live run that did not happen is `live.run` with `result: UNRUN` and its command.
7. **Refused outright:** narration ("Started…", "Now looking at…"), restating an earlier entry, a pasted log or stack,
   a status event that changes nothing (the same test, sha and result again), lifecycle noise (claims, leases,
   reassignments, "dispatcher verified"; the launcher records runs itself).
8. **His words are verbatim and carry authority.** `question.answer` / `decision` keep his sentence in `said`
   unedited, with `--owner-said`, `--by-card` or `--per-ruling`; past 600 chars, `said` holds the deciding sentence
   and `ledger:`/`card:` points at the whole.
9. **Tag with the closed sets only:** `bars` from the mod's locked bar ids (unknown ids are refused); `tags` from
   eight fixed facets: `code`, `instrument`, `test`, `live`, `settings`, `art`, `perf`, `other-mod`.
10. **Miners:** each ticket mines to its facts, not its history: at most one `finding.open`, its final state change
    (`claimed_fixed` / `verified` / `withdrawn`), and every distinct cause, trap or answer it holds; every event cites
    `item:<ticket>`. Lifecycle events are never mined.

A refusal always says what was measured, what would pass, and the smallest fix (the refusal ruling); e.g.
`REFUSED text: 611 chars > 320 · would pass: ≤ 320 · smallest fix: split into two events, or move the detail into a
file and cite it with --evidence path:…`.

---

## 1. Outside standards

Each source, the one idea taken, and what is deliberately not taken.

| standard | source | the idea we take | what we do not take |
|---|---|---|---|
| Architecture Decision Records (Nygard, 2011) | https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions `[read]` | Supersede, never delete: *"If a decision is reversed, we will keep the old one around, but mark it as superseded. (It's still relevant to know that it was the decision, but is no longer the decision.)"* And small beats complete: *"Large documents are never kept up to date. Small, modular documents have at least a chance at being updated. Nobody ever reads large documents, either."* | The one-to-two-page essay form (*"full sentences organized into paragraphs"*): our unit is one fact, a paragraph at most; a decision's reasoning, when long, lives in a spec the entry cites. |
| MADR (Markdown Any Decision Records) | https://adr.github.io/madr/ `[read: the page's own decision list]` | Its record carries **considered options** and a **confirmation** heading (how you will know the decision holds): our `finding.open` carries `accept`, the command that confirms the fix, and `cause.refuted` carries what refuted it. | Pros-and-cons tables per entry. |
| CloudEvents 1.0 envelope | https://raw.githubusercontent.com/cloudevents/spec/main/cloudevents/spec.md `[read]` | A small fixed envelope (`id`, `source`, `type`, optional `subject`) around a free body, and *"Consumers MAY assume that Events with identical `source` and `id` are duplicates"*: our `writer`+`key` idempotency, and our `subject` as the routing key the index is built on. | Transport bindings, `datacontenttype`, `dataschema`. |
| OpenTelemetry semantic conventions | https://opentelemetry.io/docs/specs/semconv/general/naming/ `[read]` | A **registry** of names, reused before new ones are minted, and *"Attributes, metrics, and events SHOULD NOT be removed … When the convention is renamed or no longer recommended, it SHOULD be deprecated."*: our closed kind, facet and bar sets, and subjects that are superseded, never renamed. | Dotted attribute namespaces per field; we have eight facets, not a taxonomy. |
| Event sourcing and snapshots (Fowler) | https://martinfowler.com/eaaDev/EventSourcing.html `[read]` | Snapshots are rebuilt state, taken at any time: *"New snapshots can be made at any time in parallel without bringing down the running application."* Our per-version digest and the index are snapshots; the shards are the record. | Fowler leaves the system of record open (*"can either be the event logs or the current application state"*); the fusion spec already chose the log. |
| Keep a Changelog 1.1.0 | https://keepachangelog.com/en/1.1.0/ `[read]` | *"Changelogs are for humans, not machines"* and *"The same types of changes should be grouped"*, plus its argument against commit-log diffs: a reader wants the grouped outcome, not the trail. Our views group by status (open, refuted, verified), never by time. | The six change types as kinds: ours are lifecycle states of findings, not release notes. |
| Conventional Commits 1.0.0 | https://www.conventionalcommits.org/en/v1.0.0/ `[read]` | A **typed prefix and scope** before a short description is enough structure for tools: our `kind` + `subject` + one-paragraph `text`. | Free-form multi-paragraph bodies (*"A commit body is free-form"*): our body is capped. |
| Blameless postmortems (Google SRE book, ch. 15) | https://sre.google/sre-book/postmortem-culture/ `[read]` | Write one only on a **trigger**, not by habit (*"we are deliberate in choosing when to write one"*), and focus *"on identifying the contributing causes"*: our "would a holder act differently" test, and `cause.*` entries about mechanisms, never about which run erred. Action items with an owner and tracking: our `proposed_fix` goes to the holder. | The full document (timeline, impact, lessons): timelines are what the shards already are. |
| Long-running agent harness (Anthropic, Nov 2025) | https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents `[read]` | A progress file plus a feature list each session reads first; they chose JSON because *"the model is less likely to inappropriately change or overwrite JSON files compared to Markdown files"*, and agents may only flip a `passes` field. Our typed JSON events, where the only way to change state is a new typed event. | Hand-edited progress text (`claude-progress.txt`): our packet is generated. |
| Context engineering (Anthropic, Sep 2025) | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents `[read]` | Structured notes outside the window, and *"the minimal set of information that fully outlines your expected behavior. (Note that minimal does not necessarily mean short …)"*: the packet's bound is a budget of current facts, not a truncation of history. | — |
| Lab-notebook / ALCOA data integrity | search results only, e.g. https://www.research.colostate.edu/integrity-security-compliance/quality-assurance/good-documentation-practice-gdp `[snippet]` | Attributable, contemporaneous, never obscured: changes are recorded *"without obscuring the original"* (secondary source). Our writer-per-shard and append-only. | Signatures; no primary GLP text was read. |
| W3C PROV-O | https://www.w3.org/TR/prov-o/ `[snippet; not read on the page]` | Entity / activity / agent, `wasDerivedFrom`: our `item:` and `ledger:` refs on mined events (derived from that ticket) and `writer`/`run` (the agent and activity). | RDF, qualified relations. |
| SQLite FTS5 | https://sqlite.org/fts5.html `[read: contents and the external-content section headings]` | An external-content FTS table indexes text kept elsewhere, and the `rebuild` command regenerates it: our index is built from the shards and thrown away. | Triggers to keep it in sync: we rebuild whole when the shard offsets change. |

`[measured]` FTS5 is present in this machine's Python (`sqlite3` 3.46.1, a `fts5` table created in memory).

---

## 2. What goes in, and what stays out

### 2.1 The test, and the three things that are always worth an entry

The test is the rule sheet's first line. In practice three kinds of fact pass it every time, because each changes what
the next holder does:

- **a state change of something tracked** (a finding opened, claimed fixed, verified, withdrawn; a bar locked; a stage
  accepted; a test result that differs from the last one on the same subject and sha);
- **a thing ruled out** (a cause refuted, with what refuted it and what it depends on), so nobody chases it again;
- **a thing a reader would otherwise get wrong** (a trap: the instrument that is green for the wrong reason, the dead
  sha, the setting name kept only as a mirror). The journal's "Oddities" section is exactly this kind
  (`design/concepts/GimmeSomeSlack/journal.md`, 8 of them `[measured]`).

Everything else (what a run did, in what order, how it felt about it) is in git, the run's own log, or nowhere.

### 2.2 Per kind: required fields

Envelope fields are written by the tool (`id`, `key`, `ts`, `tsn`, `mod`, `version`, `writer`, `run`, `kind`,
`subject`, `evidence`, and `supersedes`, `code_sha`, `token`, `authority` when they apply). The body fields:

| kind | required body | also required |
|---|---|---|
| `finding.open` | `class` (problem / polish), `bars` (list; may be empty only with facet `instrument` or `test`), `text`, `proposed_fix`, `accept` | ≥ 1 evidence ref |
| `finding.claimed_fixed` | `text` (what changed; the causes it fixed, named in a clause each), `test` (the command, red and green) | `code_sha` |
| `finding.verified` / `finding.reopened` | `text` | `code_sha`; writer JUDGE |
| `finding.withdrawn` *(new)* | `text` (why it is not a defect), `how_checked` (`test` / `repro` / `reading`; `reading` alone is shown as weak) | `code_sha` |
| `finding.disputed` | `text`, `counter` (what the holder would do instead) | — |
| `cause.tried` | `text` (the hypothesis), `finding` (its finding subject), `decides` (the one observation that settles it) | — |
| `cause.refuted` | `text` (what refuted it), `finding`, `depends_on` (paths) | `code_sha` |
| `trap.noted` / `trap.cleared` *(new)* | `text` (what a reader would get wrong, and the truth), `where` (a path, row or instrument) | — |
| `question.ask` | `text`, `obvious`, `against` (the Evidence-for-Ask ruling) | — |
| `question.answer`, `decision` | `said` (his words, verbatim) or `text` (a steward decision) | `authority` |
| `test.run`, `live.run` | `result` (PASS / FAIL / UNMEASURED / UNRUN), `command`, `bar` when it decides one | `code_sha` unless UNRUN |
| `session.checkpoint` | `done` (≤ 320, refs in evidence), `next` (one imperative, ≤ 160), `ruled_out` (cause subjects) | — |
| `note` | `text`, `about` (an existing subject) | — (never shown in the packet; searchable only) |

### 2.3 Caps

| field | cap | why this number |
|---|---|---|
| `text`, `proposed_fix`, `done` | 320 chars | the largest real fact in the worked example fits in 320 (§5); the theft ticket's verbatim GPT block is 986 chars `[measured]` and mines to one 250-char text plus a cited ref |
| `accept`, `command`, `test` | 240 chars | one command line and its expected result |
| `said` | 600 chars | his longest quoted words tonight run 358 (card answer 1) and 367 (his additions) chars `[measured: the fusion spec]`; longer quotes keep the deciding sentence and a ref |
| evidence | 6 refs × 160 chars | the worked example needed at most 4 `[measured]` |
| whole line | 1,536 bytes | the largest worked-example line is 1,163 `[measured]`; well under the 4,096-byte atomic append limit `modledger` already enforces |

Caps are per field, so "not arbitrary in size" holds per entry; §3 makes it hold for the whole.

### 2.4 How the lint enforces it

Two places, one rule set (a `standard` table in `modledger.json`, so the numbers live once):

- **`modledger append` refuses** a missing required field, a field over its cap, a line over 1,536 bytes, an untyped
  or oversize evidence ref, a multi-line or code-fenced text, a stack-frame pattern, a narration opener from a short
  list (`I `, `We `, `Now `, `Started`, `Began`, `Working on`, `Looking at`, `Continuing`), an unknown bar id or facet,
  a body whose normalised text already exists on the same subject, and a `test.run`/`live.run` identical in command,
  sha and result to the subject's last one. Each refusal prints `REFUSED <field>: <measured> · would pass: … ·
  smallest fix: …` and exits 2.
- **`modledger lint` (at `./publish`) re-runs the same checks** over every new line since `origin/main` (a hand-written
  line that skipped `append` is caught there), and checks each `sha:` ref resolves on `origin/main`
  (`git cat-file -e`) — the trap the theft fix hit, a sha rewritten at landing (§5).

The mechanical checks catch shape, not judgement: narration in plain clothes passes them. That is what the backfill
judge's sample and the packet regression tests (fusion spec §3.3) are for. `[guess ~70%]` the opener list and the
duplicate check catch most of the narration seen in today's ticket notes; the planted cases in `worked_example.py` show
the checks fire, not their recall.

---

## 3. "Only grows" and "not arbitrary in size", both

- **Growth follows facts, not activity.** A run that changes nothing writes nothing (status-without-change is refused).
  The worked example: 10 tickets and their 41 ledger events became 23 entries `[measured]`; 14 of the 41 were
  lifecycle (7 reassign, 2 claim, 2 lease, 1 raise, 1 start, 1 "dispatcher verified" note) `[measured: event types over
  all shards]` and are not mined.
- **Each entry is bounded** (§2.3), so the ledger's size is about entries × ~760 bytes `[measured: 17,446 / 23]`. A mod
  with 400 findings over its life, three facts each, is ~0.9 MB `[guess ~60%: assumes the example's mix]`: small for
  git and for the index, and never read whole.
- **What is read is bounded separately.** The packet reads the *reduced state*, not the history: open findings (text,
  proposed fix, accept), causes refuted and still valid, traps not cleared, his answers on open subjects, open
  questions, the last checkpoint, and a count line per bar of what is closed. Closed subjects collapse to one line each
  (`finding:X verified 6f8bfb47c4`), and past the 15k-token budget to a count. Its size depends on what is *open*, which
  the pipeline drives down, not on how long the mod has lived.
- **Snapshots are views.** At every `version.open` (and on demand), `modledger views` writes `views/closed_<version>.md`:
  one line per subject closed in that version, its final status and sha. It is a generated file checked by the views
  lint like the others; nothing is deleted, and `modledger show <subject>` still returns the full trail.
- **Supersession keeps it current.** A refuted cause whose `depends_on` paths changed after its `code_sha` shows as
  *stale* in the packet (not as refuted), so a growing history never preserves a stale verdict as current
  (fusion spec §3.1).

---

## 4. Structure for rapid search

### 4.1 Controlled vocabulary

- **Kinds:** the closed list in `modledger.json writers` plus the two new ones (§6). No free kinds.
- **Subjects** are stable ids with a class prefix:
  - `bar:<id>`: the mod's locked bar ids (GSS: the `tree.json` leaves and `record.json` rows, 48 `[from the journal]`);
    minted only by `bar.locked` / `bar.added`.
  - `finding:<NAME>`: a name in the project grammar (`PROJECT_VERB_INTENTION_TWIST`, checked by `rimflow namecheck`);
    mined findings keep their ticket's name, so the ticket, the ledger and every old commit message share one id.
  - `cause:<kebab-slug>` (with its `finding`), `trap:<kebab-slug>`, `q:<kebab-slug>`: minted by their first event.
  - singletons: `stage`, `version`, `session`, `lease`.
- **Who mints, and how duplicates are prevented.** Any writer allowed the kind mints by writing the subject's first
  event. At mint, `append` runs the new text against the index's live subjects of the same class; if the best match
  clears a threshold (BM25 rank, tuned on the backfill) it refuses with the candidates (`trap:x looks like
  trap:geometry-check-reads-seven-oracle-scenes (live, BACKFILL seq 18): write to it, or pass --new-subject "<why it
  differs>"`). The override is recorded in the body, so a near-duplicate is a searchable decision.
- **Tags** are two closed sets: `bars` (the mod's own ids) and eight facets fixed in `modledger.json`. No per-mod free
  tags: a free tag set is the vocabulary sprawl OpenTelemetry's registry exists to stop.

### 4.2 The index: generated, disposable

`modledger index --mod <Mod>` builds `/tmp/modledger-index/<Mod>.sqlite` (a program reads it, so `/tmp`, never the
repo). Every query command checks the shards' byte offsets against the ones stored in the index and rebuilds whole when
they differ; deleting it loses nothing. Never committed, never cited, never a second source of truth.

- `ev(id, shard, seq, ts, writer, kind, subject, class, bars, tags, code_sha, authority, text, fix, accept, said,
  evidence, supersedes, superseded_by)`: one row per event;
- `subj(subject, class, status, stale, last_ts, last_id, bars)`: the reducer's state per subject;
- `fts`: an FTS5 table over `subject, text, fix, said, evidence` with `content='ev'`.

### 4.3 The queries a holder runs

| question | command (proposed) |
|---|---|
| Has this cause been refuted? | `modledger find --mod GimmeSomeSlack --class cause "planner kinks the lead"` → each match with its status now: refuted, *stale* (its files changed since), tried, reopened |
| What did he say about X? | `modledger find --mod GimmeSomeSlack --his "shock"` → OWNER events and answers only, `said` verbatim, with ledger id and authority |
| Open findings on bar N | `modledger open --mod GimmeSomeSlack --bar no_unforced_sharp_turn` → open and claimed-fixed findings with proposed fix and accept |
| What changed since I last looked? | `modledger since --mod GimmeSomeSlack <cursor>` → status changes only, grouped by subject; the cursor is the offset set the packet prints on its last line (or an event id, or a time) |
| Any trap where I am about to work? | `modledger find --mod GimmeSomeSlack --class trap --path src/RimMandrake/GimmeSomeSlack/Source/Aerial/` → live traps whose `where` or evidence is under that path |
| Was this found before (reopen, don't re-file)? | `modledger find --mod GimmeSomeSlack --class finding --all "illegal characters in path"` → including withdrawn and verified |
| The whole trail of one subject | `modledger show --mod GimmeSomeSlack finding:<NAME>` (exists today) |

`--mod all` searches the three pilots at once, so a system fix found on one is visible from the others (his card:
*"When one reveals a needed fix to the system all three benefit."*).

---

## 5. Worked example: ten Gimme Some Slack tickets

Five open (`RIMMANDRAKE_UNBEND_GSS_LEAD_AT_JUNCTION_BATTERY_TWICE`, `RIMMANDRAKE_TRACE_GSS_ILLEGAL_PATH_ONLY_ON_FIRST_START`,
`RIMMANDRAKE_BUILD_GSS_FLOOR_END_SHOCK_ANSWERED_WEEK_AGO`, `RIMMANDRAKE_LIFT_GSS_FALLEN_WIRE_OFF_WALL_CORNER`,
`GSS_POWER_THEFT_FIX_WRONG_VICTIM`) and five closed (`GSS_MULTILINK_FIX_PIPE_POLE_RANGE`,
`GSS_DETERMINISM_FIX_IGNORES_STALE_PIECES`, `GSS_COLOUR_SEED_FIX_HIDDEN_CONDUIT_SPLIT`,
`RIMMANDRAKE_UNBEND_GSS_RANDOM_BASES_SEVEN_SCENES_HID_IT`, `RIMMANDRAKE_UNGATE_GSS_DROPPED_CORDS_FROM_OVERHEAD_MASTER`),
mined by hand into 23 events and appended through the real `modledger.append` (BACKFILL, a temp root)
by `worked_example.py`, which also runs the prototype checks.

**Bytes** `[measured, run 2026-11-15 ~10:15 PM PST]`:

| | bytes | ≈ tokens |
|---|---|---|
| before: ticket prose (10 files) | 16,639 | |
| before: their rimflow ledger events (41 lines) | 26,165 | |
| **before, total** | **42,804** | ~10.7k |
| **after: 23 events** | **17,446** | ~4.3k |
| of which body / evidence / envelope | 8,084 / 2,489 / 6,873 | |
| largest line | 1,163 (cap 1,536) | |

Down 59%. The envelope (id, key, ts, writer, kind, subject …) is 39% of what is left, ~299 bytes an event; that is the
price of one fact per entry and is worth it (each event is independently addressable and deduplicated).

**What the ten became:** 10 `finding.open` · 4 `finding.claimed_fixed` · 1 `finding.verified` · 2
`finding.withdrawn` · 3 `trap.noted` · 1 `question.answer` · 1 `test.run` · 2 `live.run` UNRUN. Three show the standard
doing work a ticket cannot:

- `RIMMANDRAKE_TRACE_GSS_ILLEGAL_PATH_ONLY_ON_FIRST_START` held two facts; it became a finding (the illegal-path
  exception) and a trap (`trap:z-log-budget-charges-stackless-errors`: the null-texture error is charged to GSS by the
  instrument's design, not evidence against it).
- `GSS_POWER_THEFT_FIX_WRONG_VICTIM`'s 13 ledger events (7,298 bytes, mostly leases, claims and reassignments) held one
  durable lesson nobody had written as one: the first fix sha `101e561a6e06` no longer resolves (rewritten at landing).
  It became `trap:built-sha-rewritten-at-landing`, and the lint rule that `sha:` refs must resolve on `origin/main`.
- `RIMMANDRAKE_UNBEND_GSS_RANDOM_BASES_SEVEN_SCENES_HID_IT` yielded `trap:geometry-check-reads-seven-oracle-scenes`
  (a 4,513/4,513 green check that read only seven scenes): the most valuable line in the ten for the next holder, and
  in the ticket it was a sub-clause of the evidence.

Two closed-as-no-defect findings (`GSS_MULTILINK_FIX_PIPE_POLE_RANGE`, `GSS_COLOUR_SEED_FIX_HIDDEN_CONDUIT_SPLIT`)
became `finding.withdrawn` with `how_checked` (`reading`, `reading+test`), carrying the Conductor's "reopen, never
re-file" in one clause: today there is no kind for "not a defect", and the only record was a free note.

**Deliberately left out:** GPT's verbatim finding blocks and code excerpts (cited by `ext:…GPT_REVIEW.md#<finding id>`);
the Producer's re-plan prose and the A1–A3 criteria restated from `## verify` (folded into `accept`); `found-by`
provenance lines (the `item:` ref carries it); lease, claim, start, raise, reassign and "dispatcher verified" events;
the second implemented event's housekeeping; the "Status at filing" lines (the event kind is the status); the long cause
list of the bends fix beyond four named causes (the commit `6f8bfb47c4` holds the rest).

**Planted bad entries, watched refused (5 of 5):** narration (`Started looking at the bend again…`), a pasted stack in
`text`, a 700-char text, a `claimed_fixed` with no `code_sha`, and a finding with no `proposed_fix` and an untyped
evidence ref (`see the log`).

**Limits.** I mined by hand with the tickets open; a miner reading 413 items will be less careful `[guess ~75%]`, which
is why the backfill is sampled by a judge that did not write it (owner note on the build item, ~10:00 PM PST). Two bar
assignments are my reading, not a recorded link: `statics_clear_between_games` for the illegal-path finding and
`four_looks_one_run` for the colour seed `[guess ~60%]`; a miner that cannot tell writes `bars: []` with a facet and
the lint lets it through.

---

## 6. Changes owed in `modledger` and the fusion spec (for the builder; nothing here was edited)

In `src/RimMandrake/rimflow/modledger.py` and `modledger.json`:

1. **Add a `standard` block to `modledger.json`**: the caps of §2.3, the required-fields table of §2.2, the facet
   list, the narration openers, the line cap 1,536. One place for every number.
2. **Replace the spill with a refusal.** `_spill` today keeps an oversize body by writing it to `ledger/text/<sha>.txt`
   (`SPILL_HEAD = 300`); under the standard an oversize field is refused with the split advice, and `ledger/text/` is not
   written. (Long material belongs in a file the event cites.)
3. **Enforce required fields per kind and the caps in `append`**, with the refusal format of the rule sheet (measured
   value, would pass, smallest fix), exit 2.
4. **Typed evidence refs** (`sha:`, `path:`, `ext:`, `test:`, `run:`, `item:`, `ledger:`, `card:`), ≤ 6 × 160 chars;
   `lint` checks `sha:` resolves on `origin/main` and `path:` exists.
5. **New kinds:** `finding.withdrawn` (JUDGE, STEWARD, HOLDER-with-test; reducer status `withdrawn`), `trap.noted` and
   `trap.cleared` (HOLDER, JUDGE, STEWARD, BACKFILL; reducer `traps{}`, packet section "Traps"). Today
   `worked_example.py` maps both onto `note`.
6. **Subject classes**: validate the `bar:` / `finding:` / `cause:` / `trap:` / `q:` prefix and singletons; `bar:`
   ids against the mod's locked bars; `finding:` names through the project namecheck.
7. **Refuse no-change and duplicate events**: identical normalised text on the same subject; a `test.run`/`live.run`
   identical in command, sha and result to the subject's last.
8. **Mint-time duplicate check** against the index (FTS5 BM25 over live subjects of the class), with `--new-subject
   "<why>"` recorded in the body.
9. **The index and query verbs**: `index`, `find` (`--class`, `--kind`, `--his`, `--path`, `--all`, `--mod all`),
   `open --bar`, `since <cursor>`; the packet prints its cursor as its last line.
10. **Packet**: closed subjects one line each, then a count past budget; refuted causes whose `depends_on` changed since
    their `code_sha` shown as *stale*; notes never in the packet.
11. **Views**: `views/closed_<version>.md` written at `version.open`.
12. **The lint**: rerun the append checks over new lines since `origin/main`; selftest cases for each refusal (the five
    planted entries of `worked_example.py` are a ready start).

In `design/specs/2026-11-15-holder-pipeline-fusion.md`:

1. §3.1 "Event shape": add one line pointing at this standard for the body rules and caps, and the two new kinds to the
   kinds list.
2. §3.1: replace any wording that implies oversize bodies are kept (the spill) with "refused; long material is cited".
3. §3.3 "The packet": add the cursor line, the stale-cause rule and the traps section.
4. §3.2 / the backfill brief: the miner's rule (rule sheet line 10) and the facts-not-history count, with this spec's
   worked example as the backfill judge's reference.
