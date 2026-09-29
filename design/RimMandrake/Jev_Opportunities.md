# Jev opportunities — where a cheap typed-judgment model changes this project

**Status: exploration.** Nothing here is filed, scheduled or approved. Produced by a
five-domain repo scan on 2026-09-28 (dev tooling · runtime C# · content review · work
record · def corpus).

## What Jev is, in one paragraph

Jev is TypeSafe AI's "System One" model. It does not generate prose. Code hands it a
`state` (arbitrary JSON) plus a map of typed questions and it returns typed answers only:
**Choice** (one of a defined option set, with a probability per option), **Noul** (the
probability a yes/no statement is true), **Score** (a probability-weighted position on
ordered levels you describe concretely). Independent questions over the same state run in
one request, in parallel. Latency ~120–220 ms; **$0.042 per million input tokens, output
free**. It cannot write text, do arithmetic, retrieve anything, or explain itself.

Two consequences shape everything below:

- **It is cheap enough to ask a question of every item in a corpus** — 137 canon entries,
  294 CharacterDefs, 202 live queue items, thousands of defs — where a Claude pass over
  the same corpus costs real tokens and a human pass costs the owner's attention.
- **It cannot retrieve, so code must supply the candidates.** For every "has this already
  been built" seam below, the judgment is not the bottleneck — *our* candidate retrieval
  is. Jev makes the last mile free; it does not find the haystack.

Official skill: `typesafe-ai` (`~/.claude/plugins/cache/typesafe-ai/typesafe/0.5.7/skills/typesafe-ai/SKILL.md`).
Our evaluation harness: `~/dev/ConsultJev`.

---

# Part 1 — Development

## 1A. Guards that pattern-match a question they cannot actually ask

This is the largest and most immediately credible cluster. Our lints and hooks are full of
regexes whose own docstrings admit they are approximating a semantic judgment, and which
were deliberately narrowed to avoid false positives — meaning they knowingly miss.

| Seam | Where | Primitive | The judgment, replacing what |
|---|---|---|---|
| **STALE_GATE_PROXIMITY** | `src/RimMandrake/rimflow/citations_lint.py:77` | Noul | Whether a citation genuinely treats a closed item as still-open. The code's own comment says it is "too noisy to gate… only reading settles" — so the check exists but cannot fire. |
| **LIVE_PROOF_PHRASE_LIST** | `src/RimMandrake/rimflow/live_proof_lint.py:51` | Noul | Whether a closing commit still owes live proof. Currently four hardcoded literal phrases; every paraphrase escapes. |
| **DOC_CLAIM_CERTAINTY** | `src/RimMandrake/Utils/doc_claims.py:108` | Choice | BEDROCK / RULED / TENTATIVE tagging, self-described as "heuristic, best-effort" regex guesswork — a natural 3-rung Choice over thousands of claims. |
| **WEAPON_ROLE_CLASSIFY** | `src/RimMandrake/Utils/weapon_tag_audit.py:123` | Choice | Tech tier from the def's real text, not from searching the label for "rifle"/"cannon" — whose named failure mode is neolithic items carrying vanilla firearm words. |
| **TAG_FAMILY_CLUSTERING** | `src/RimMandrake/Utils/weapon_tag_audit.py:104` | Choice | Semantic tag family, replacing "longest leading run of capitalised words", documented as "crude on purpose". |
| **CAST_HOOK_TRAIT_CUES** | `src/RimMandrake/Utils/cast_hook_audit.py:48` | Noul | Whether a character's prose hook implies a trait the mechanics don't back — currently ~20 hand-tuned narrow regexes that accept misses by design. |
| **ASSERTION_VS_CITATION** | `src/RimMandrake/Utils/check_canon.py:44` | Noul | Whether a line *asserts* a number as currently true or merely quotes/negates it — the real question behind hand-scoped ⛔/`~~`/"was" marker heuristics added after two documented silent misses. |
| **WALK_SUBJECT_MATCH** | `design/validation_walks/**` via `doctor` | Noul | Whether a walk's `subject:` refers to a candidate mod. CLAUDE.md measures the field as backticked in 28 walks, bare in 34, absent in 16 — the regex is why 25 of 33 "failing" walks are false positives. |

⚠️ **High-likelihood downside, specific to this cluster.** Our guards are `PreToolUse`
hooks that run on every Bash/Edit call. A blocking network call adds ~200 ms to every tool
use and fails closed when the laptop is offline or the service is down. These belong in an
**advisory WARN or an async post-hoc sweep**, not in the blocking path of a hook. That is a
design constraint, not a reason to skip them.

### The seed idea, judged: code-health clean/dirty

**It does not hold for the gate itself, and it holds well one layer out.**
`code_review_status.py` decides CLEAN vs DIRTY by comparing a recorded content hash against
the bytes on disk. That is exact, free, deterministic and correct — handing it to a model
would make it slower, costlier and *less* reliable. Do not touch it.

What is expensive is what happens *after* a file goes DIRTY: a full-file Claude review.
Two real seams there:

- **REVIEW_COST_TRIAGE** (Score) — rank the DIRTY backlog by likely review cost
  (comment-only / mechanical / needs real eyes), so review effort goes where it pays.
- **REVIEW_SCOPE_SANITY** (Noul) — before a `mark-clean`, judge whether the diff since the
  last clean mark is confined to what the reviewer claims to have read. This is a genuinely
  *new* layer of protection: nothing currently checks that a review's stated scope matches
  the change it blesses.

## 1B. Re-invention prevention — the project's most expensive recurring failure

CLAUDE.md documents this repeatedly and in its own words: *"this project keeps having
already built it."* `SEA_SHORE_TILE_MUTATOR_1` was filed two days after the exact mutator
shipped. A greatbole design pass invented six mechanisms of which four already existed.
`rimflow file` currently refuses only an **exact duplicate ID string**
(`src/RimMandrake/rimflow/cli.py:1163`).

- **FILE_TIME_DUP_SCREEN** (Choice, CONFIRMED) — at `rimflow file` time, judge a new item's
  title+spec against the live and recently-closed item corpus (202 live, 863 closed). One
  request, all candidates, at file time.
- **ITEM_VS_SRC_EXISTENCE** (Noul, CONFIRMED) — judge a new item's spec against a
  keyword-retrieved candidate set of existing source files: *is this mechanism already
  implemented here?* Nothing does this today; CLAUDE.md's record shows it is caught by luck.
- **PROPOSAL_SRC_DRIFT** (Score, CONFIRMED) — score how much of a design proposal already
  exists in src. Measured candidates: `design/Jawa/proposals/propane_gas_deep_design.md`
  (14 matching src XML hits), `tar_pits_deep_design.md` (32), `sarlacc_deep_design.md` (9),
  all sitting un-cross-referenced.
- **DUPLICATE_CREATURE_CONCEPT** (Noul, CONFIRMED) — does this new def describe
  substantially the same creature as one already in the corpus, under a different invented
  name? Our naming convention makes this invisible to any string match, which is the same
  root cause as the census failure CLAUDE.md records (`RM_OssuaryShrimp` vs `RM_Fessk`).

This cluster is the strongest argument for Jev in the whole document, because the failure it
prevents is measured, repeated, and costs whole sessions.

## 1C. Doc rot and stale gates, at a volume nobody can afford

**MEASURED this pass: 130 of 202 live items cite an item id that exists only in
`items/closed/`.** Some are legitimate history; some are a live item about to be worked
against an assumption a closure already overturned. Separating those is a per-citation
semantic judgment over ~hundreds of pairs — free with Jev, unaffordable otherwise.

- **LIVE_ITEMS_CITE_CLOSED** (Noul, CONFIRMED) — per citation: stale gate, or fine
  historical mention?
- **STALE_CLOSED_CITATIONS** (Noul, CONFIRMED) — same judgment across `design/`. Confirmed
  live examples: `design/MOVING_DUNES_DESIGN.md`, `design/RIMPROPERTY_ANIMAL_THEFT_SPEC.md`
  and `design/RM_GRAFFITI_SCOPE_WIDENING.md` each still read DRAFT/pending while citing an
  item now closed.
- **FROZEN_FACT_STILL_TRUE** (Noul, CONFIRMED) — `infrastructure/state/facts/naming_inventory.md`
  is frozen at 2026-08-23 with pre-tier-grammar names, predating the 2026-08-31 rename
  closure it exists to inform. Judge each frozen fact against the closure record.
- **LESSONS_INBOX_ROUTING** (Choice, CONFIRMED) — ~112 ungrouped lesson bullets in
  `infrastructure/state/LESSONS_INBOX.md`; classify each to a target skill so curation
  starts from a sorted queue instead of a cold full read.

## 1D. Triage and pre-fill for the owner's scarce attention

The rule throughout: **rank, triage, flag and pre-check — never decide.** Taste verdicts
stay the owner's, and a review sheet's cut is scoped to that sheet.

- **UNREVIEWED_ENTRY_TRIAGE** (Score, CONFIRMED) — **MEASURED: 137 canon entries, 29 carry
  a real `## ruling`, 108 carry the literal placeholder.** Rank those 108 by how large a
  correction to existing art each implies, so the queue is ordered by consequence rather
  than alphabetically. *(Note: CLAUDE.md records 25 as the measured figure; 29 is the
  current count, so that line is simply out of date.)*
- **CANON_VS_DEF_CONTRADICTION** (Noul, CONFIRMED) — per entry, does our def's stated
  colour/genes/traits contradict the entry's sourced canon text? Catches the Rakata
  psychic-gene/skin-colour class across all 137 at once.
- **INTERNAL_BRIEF_CONTRADICTION** (Noul, CONFIRMED) — does an entry's own Visual Brief
  contradict its own Sourced Text? Confirmed instance: `anooba` (stripes vs "varying gray").
- **ARTPIPE_STYLE_PRESCREEN** (Noul, CONFIRMED) — does a queued art prompt violate the
  written style law (no cartoonish, no flat cel, no fused-stub limbs) *before* a generation
  is spent?
- **CAST_TRAIT_DRIFT** (Score, CONFIRMED) — **MEASURED: 294 `CharacterDef`s across 12 files
  in `src/RimMandrake/Inhabited/Defs/CastRosters/`.** Judge each character's `<traits>`
  against their own `<hook>`/`<childhood>`/`<adult>` prose. Nobody re-reads 294 bios.
- **SPAWN_RATE_PREFILL** (Score, CONFIRMED) — pre-fill a commonality band from a creature's
  description. The register's own note says every spawn rate today is agent-chosen and
  nothing measures it, so this replaces a guess with a calibratable guess.
- **MULTI_HOME_REASON_FLAG** (Noul, CONFIRMED) — does a multi-homed species' description
  name a migration or life-stage reason (the owner's only valid carve-out)? Pre-populates
  the note each per-biome sitting sheet needs across the 55 multi-homed species. **Flag
  only — evictions are stopped and this must never edit a roster.**

✅ **We already hold the ground truth to calibrate this cluster.** The review sheets'
`*.decisions.json` files record real human verdicts, including rows where the owner
*overturned* a prefill — which is exactly the labelled set a calibration needs. This is the
single most important practical note in the document: it means the question "is Jev good
enough here" is answerable before anything is wired.

## 1E. Corpus-wide semantic consistency in the defs

Judgments no schema validator or XML lint can make, now affordable per-def.

- **DESC_PROMISES_MECHANIC** (Noul, CONFIRMED) — does a def's description promise behaviour
  its comps do not implement? The reason this check does not exist today is false positives:
  `RM_SunSphere.xml:28` says "It never explodes", which any keyword lint flags and a semantic
  read does not. Jev makes the check viable rather than abandoned.
- **HEDIFF_MECHANISM_CLAIM** (Noul, UNCERTAIN) — same shape for HediffDefs whose prose makes
  a mechanism claim ("not an infection") the comp shape does not back.
- **TWIN_ROSTER_COHERENCE** (Score, CONFIRMED) — read an `RM_` biome's own placeholder roster
  *together with* its patch-added campaign cast, as the player actually experiences it, and
  score thematic coherence. Directly targets the twin trap that produced two wrong fauna
  censuses.
- **MAYREQUIRE_GUARD_AUDIT** (Noul, CONFIRMED) — given a guarded PatchOperation's real target
  and value, does the content genuinely depend on the named mod? **MEASURED: 2,365
  `MayRequire` sites in our defs and patches, 61 of them on a top-level `<Operation>` node**
  where the attribute is inert (CLAUDE.md records 74 sweep-wide). This class already reset the
  live `ModsConfig.xml` to Core-only twice in one night.
- **FLIGHT_FICTION_SCREEN** (Noul, UNCERTAIN) — does a creature's description use airborne
  language without `MaxFlightTime` set? Cheap enough to run on every future creature edit,
  which is what the standing "if it flies in the fiction, it flies in the game" rule needs.
- **QUEST_TEXT_VS_GRAPH** (Noul, UNCERTAIN) — does a quest's letter text match its actual
  ask/choice/failure/reward fields? Aimed at the "most quest bugs are silent" failure mode
  before the quest corpus outgrows one reviewer.

⚠️ **High-likelihood downside on two of these.** `CANON_TIER_MISPLACEMENT` (is this name
genuine Star Wars IP or invented flavour?) and `EARTH_FAUNA_BAN_PRESCREEN` (does this read as
a retextured Earth animal?) both depend on Jev's *parametric world knowledge*, which it cannot
cite and we cannot verify. Both are attractive because they target real past failures, and
both are the shape of judgment most likely to be confidently wrong. Treat as flag-only, and
never as a canon determination — canon comes from the Wookieepedia API, which works from here.

---

# Part 2 — Runtime

The seam that makes this cluster credible: **RimWorld's own decision surfaces are already
typed.** `IncidentParms`, a `RaidStrategyDef` list, a `PawnGroupMaker`, an enum — the output
is a fixed option set, so there is nothing to parse and no prose to guard. This is the
difference between a Jev call and the Oracle's prose call, and it is why Jev's shape
*structurally* satisfies the Oracle's first law (text/menu authority only) instead of us
enforcing it by discipline.

## 2A. Decisions currently made by a coin flip or a first match

| Seam | Where | Primitive | The judgment, replacing what |
|---|---|---|---|
| **GATE_SEARCH** | `src/RimMandrake/Inhabited/Source/GateSearchHook.cs:35` | Noul | Whether a settlement searches a departing party — currently a flat per-faction `Rand.Chance` that reads neither what the party carries nor how they are regarded. The file's own header defers "real per-faction tuning". |
| **ELDER_NOVELTY** | `src/RimMandrake/DivingInteraction/Source/RM_ElderTradeUtility.cs:71` | Noul | Whether an offered item is genuinely novel to the Elder, from its actual description — currently a xenotype/kind/def string match the author flagged `[INVENTED]`. |
| **WARDEN_HEIR_PICK** | `src/RimMandrake/Miasma/Source/RM_WardenMotherSuccession.cs:358` | Choice | Which surviving young succeeds a dead warden mother — currently first in list order, with bond and behaviour ignored. |
| **NINEFOLD_FRONT_SWING** | `src/RimMandrake/Ninefold/Source/GameComponent_Ninefold.cs:238` | Noul | Whether an event was violent enough to shift which god holds the spotlight — currently one hardcoded magnitude-tag comparison. |
| **NINEFOLD_MOOD** | `src/RimMandrake/Ninefold/Source/GameComponent_Ninefold.cs:385` | Score | Each god's disposition, grounded in what actually happened to the colony — currently an admittedly untuned random walk. |
| **SUULK_ENTICEMENT** | `src/RimMandrake/TerminalBiomes/Source/RM_IncidentWorker_SuulkArrival.cs:45` | Score | How enticed a light-grazing creature is to arrive — currently linear in glower *count*, blind to placement, brightness and map conditions. |
| **ANIMAL_THEFT_WORTH** | `src/RimMandrake/RimProperty/Source/AnimalTheft/AnimalTheftUtility.cs:41` | Score | Which unattended item is actually worth stealing — currently "closest reachable under a mass cap". |
| **CONTAGION_BUD** | `src/RimMandrake/Contagion/Source/CompRandomizeUnfinished.cs:103` | Noul | Whether an Unfinished buds into something dangerous — currently a flat 12% untouched by which limb-hediffs it already rolled. |

Each of these is a place where the game currently cannot tell the difference between two
situations that a player can obviously tell apart. That is the "richer" axis, and it is the
one Jev is actually shaped for: none of these needs prose, all of them need situational
common sense over state the game already has in hand.

## 2B. Raid and inhabitant composition

Known to us already, recorded here for completeness. `src/RimMandrake/RaidRedesigner/` is a
real mod (~11 source files: old friends, world-pawn pinning, threat-point replacement) and
**`Oracle` appears in only one of them, `RaidRedesignerSettings.cs`** — a toggle, not calls.
The seam is open, not spent. Same shape for the `INHABITED_*` family: deciding what inhabits
a place is a typed selection over a roster we already own.

⚠️ **High-likelihood downside for all of Part 2.** A runtime call needs the network, and
people play RimWorld offline. The Mod Settings law already requires every feature to degrade
gracefully with everything off, so the vanilla path must stay intact and the Jev path must be
an enhancement — never a dependency. Additionally, ~200 ms is fine off-tick but not
synchronously inside map generation; anything in a gen path needs precompute or async.

---

# Two structural notes

**1. The transport doctrine is the actual decision, and it is the owner's.** CLAUDE.md's
2026-09-05 ruling is that in-game LLM access is `claude -p` as a subprocess, never a hosted
API key — and that ruling is now *implemented*: `src/RimMandrake/Oracle/Source/OracleClient.cs`
is a real subprocess client, and `ORACLE_CLIENT_CLAUDE_CODE_REWRITE_1` is closed. So adding a
runtime Jev call is a doctrine change, not a code change. The coherent proposal is **two
transports for two shapes of question**: `claude -p` for anything producing text a player
reads, Jev for anything producing a configuration. Nothing in Part 2 should proceed without
that ruling.

**2. What "measure it first" means concretely here.** The official skill's own caution is
*"typed output guarantees the interface, not truth"* — validate in the target domain. We are
unusually well placed to do that, because three labelled sets already exist: the review
sheets' `*.decisions.json` human verdicts (including overturned prefills), the 863 closed
items as ground truth for duplicate detection, and the canon library's 29 real rulings. A
first evaluation should use one of those, not a new hand-built reference set — a reference set
written by whoever is testing the thing measures agreement with its author.

# Shortlist, by leverage

1. **FILE_TIME_DUP_SCREEN + ITEM_VS_SRC_EXISTENCE** (1B) — prevents the most expensive
   documented failure in the project, and calibrates against 863 closed items.
2. **LIVE_ITEMS_CITE_CLOSED** (1C) — 130 of 202 live items already implicated; pure win,
   no runtime risk, no doctrine change.
3. **UNREVIEWED_ENTRY_TRIAGE + CANON_VS_DEF_CONTRADICTION** (1D) — orders 108 unreviewed
   canon entries by consequence and pre-flags contradictions across all 137.
4. **REVIEW_SCOPE_SANITY** (1A) — a protection layer that does not exist today, on the
   system the owner already identified.
5. **GATE_SEARCH / ELDER_NOVELTY / ANIMAL_THEFT_WORTH** (2A) — the cheapest runtime
   demonstrations: each is one flat roll today, each has a typed output, none is on a
   generation path.
