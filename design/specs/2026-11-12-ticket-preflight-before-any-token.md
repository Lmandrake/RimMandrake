# Ticket preflight: check everything Python can, before any token is spent (spec, nothing built)

Date 2026-11-12. Item `RIMMANDRAKE_PREFLIGHT_TICKETS_BEFORE_ANY_TOKEN_IS_SPENT`.
Nothing here is built. The build tickets in section 7 are proposed, not filed.
Evidence (scripts, raw counts, the three GPT rounds): `D:\ClaudeWork\rimmandrake\conductor\ticket_preflight_20261112\`.
Every number is tagged `[measured]` (a script in that folder produced it on 2026-11-12) or `[guess ~N%]` (my confidence).

## 0. The order, and the short answer

The owner, 2026-11-12 (verbatim in `OWNER_WORDS.md` in the evidence folder and in the item's filing event): *"Before a
single token is spent, a deterministic python script should confirm everything it can about a ticket's setup,
specification, environment, basic sanity checks for its acceptance tests, etc. Any files mentioned, paths mentioned, defs
mentioned, races mentioned should all be validated as something real in the game AND that it has a reasonable expectation
to be in the game via the specified modlist. Any Full Mod tests should have to justify why they need the Full Mod test:
minimal mod lists are to be preferred unless it is explicitly a Full Mod test called out. [...] so we can stop spending 1M
tokens to say "this doesn't make sense." [...] I know we have some versions of this in place already... let's beef them
up. The only thing to watch is that they don't take 1 hour to check a ticket every time we try to start, so a metric that
should be recorded every run is the precise time this took to run."*

The short answer:

1. **One module, many doors.** One file, `src/RimMandrake/rimflow/ticket_preflight.py`, holds a list of small checks.
   Every door a ticket passes through (filing, claim/start, helper launch, live-queue submit, Relentless pickup) calls the
   same function. No model is ever called. The gates that exist today keep their own code and their own authority;
   the module times and counts them, and adds what is missing.
2. **Two moments.** CREATE (the ticket was just written) and PICKUP (someone is about to work it). CREATE checks the
   ticket against the repo and the def dump. PICKUP repeats that, because the world moved, and adds the environment.
3. **Three kinds of verdict.** REFUSE (the door stays shut and prints the smallest fix), WARN (the door opens, the worker
   sees the line first), ANNOTATE (a fact attached to the ticket, such as "needs a 22-second minimal load").
   Only a *declared* fact may refuse. A name found by pattern in prose may only warn. Section 4 has the measured reason:
   a naive pattern calls 48% of our own names unknown.
4. **It is fast because it never builds anything in the hot path.** Measured today: the checks themselves cost a median
   of 0.11 ms per ticket and 42 ms at worst; loading the ready-made indexes costs about 0.3 to 1.5 s. Budget: 1 second
   added at CREATE, 3 seconds at PICKUP, hard stop at 5 seconds (targets from a prototype; ticket 1 measures the real thing). Every run writes its total time and each check's time.
5. **It starts small and earns its teeth.** The first ticket is one hand-run command that checks declared paths and
   "is this def on this mod list", times itself, and refuses nothing. It then runs in shadow at the real doors. Only checks that
   prove themselves on real tickets are allowed to refuse. The 95 checks are the map, not the first delivery.
6. **It is honest about what it cannot see.** A check that cannot measure says UNMEASURED and lets the ticket through
   with a note. It never turns "I could not look" into "it is not there".

## 1. What already exists, and what the waste looked like

### 1.1 The checks we already have (all read today)

| Where | What it checks | When it runs | Refuses? |
|---|---|---|---|
| `rimflow/cli.py` `_mint_or_die`, `cmd_namecheck` | name grammar `PROJECT_VERB_INTENTION_TWIST` | file | yes |
| `rimflow/cli.py` `_reader_or_die` | the caller is a known seat | every verb | yes |
| `rimflow/model.py` `_missing` + the "thin:" line | no `## spec` / `## verify` / `## criteria` | file, queue | no: "A PROMPT, NOT A GATE" |
| `rimflow/cli.py` `_prooflint_say` -> `relentless.proof_refusals` -> `relentless_live.lint_lines` | the live-proof lines parse and are runnable | file (prints), Relentless pickup (refuses) | prompt at file |
| `rimflow/cli.py` `cmd_claim` | focus cap per seat | claim | yes |
| `rimflow/relentless.py` `eligible`, `admission` | state, holds, budget, repeat guard | Relentless pickup | yes |
| `rimflow/relentless.py` `reach_hold`, `contract` + `relentless_reach.needs` | the proof needs a hidden path, git history, a remote host or a Windows program the blind judge cannot reach | Relentless, before boarding | yes |
| `rimflow/relentless_names.py` | every name on a `live-mods:` line resolves to one installed mod (roll call) | Relentless, before boarding | yes |
| `rimflow/relentless_binding.py` | the obligation and the proof binding agree | Relentless | proposes a repair |
| `rimflow/relentless_envcause.py` | sorts a live failure into environment causes | Relentless, after a failure | routes |
| `rimflow/relentless.py` `first_touch_hold` | a mod with no Designer pass | Relentless pickup | holds |
| `rimflow/probe.py` | is the game running, does the bridge answer | on demand | n/a |
| `rimflow/detached_helper.py` `launch` | seat, model, brief present, time cap, item exists on origin | helper launch | yes |
| `Utils/testq/schema.py` `validate_job` | job shape | live-queue submit | yes |
| `Utils/northstar_driver/preflight.py`, `Utils/modcheck/live_queue/preflight.py`, `Utils/preflight_bridge.py` | ordered fail-fast checks before a cold load (PASS / FAIL / UNMEASURED) | before a live run | yes |
| `Utils/defindex.py` | `ModSetDefs.provided(name)` -> True / False / None: is this def on this mod list | on demand; **no door calls it** | n/a |
| `Utils/modset_builder.py`, `Utils/modlist_swap.py`, `Utils/refresh.py` | tiers, dependency closure, dump fingerprint against the load set | on demand | n/a |
| `skills/rimworld-modding/scripts/validate_patch.py` | xpath targets exist in the dump | on demand | n/a |
| `.claude/hooks` (Agent spawn: model named, bounded, slots; `queue_lint.py` on Write/Edit) | helper hygiene | every spawn / edit | yes |

What this table says: the good checks are **late and Relentless-only**. A ticket filed by hand, claimed by a seat, or
handed to a detached helper meets almost none of them. And the one tool that answers the owner's main question ("is this
def real, and is it on this mod list") is called by no door at all.

### 1.2 The deleted "expectations manifest", and what it was really about

Commit `4594675ed9` removed the L1 expectations manifest (owner pick 6). It was a hand-written JSON per item
(`{defType, defName, path, expected}`) diffed offline against a def dump. Its idea was right: **declared, machine-checkable
facts about a ticket, checked with no model.** It died because the manifests were written by hand against fixtures and
rotted on the first rename (`RSW_` to `RM_`). This design keeps the idea and goes at the cause of death (whether it works is for the shadow run to show): the declared
facts live in the ticket itself, the tool proposes them, and they are checked against the live indexes at both moments.

### 1.3 The waste, measured

| Source | Measured |
|---|---|
| Relentless store, window 2026-10-31..11-07, `attempts.jsonl` joined to `spend-*.json` | 1,880M tokens in all, 1,828M mapped to an item and generation. A work run costs a median of 374k tokens (p90 1,184k); a check run 173k `[measured]` |
| Same window, generations that **ended** in a setup-class end (the ticket could not be measured, not that the work was wrong) | 238 items, 274 generations, **228M tokens = 12.5%** of mapped spend `[measured]`. By end type: unmeasured 96.2M (70 items), rebind_proposed 33.7M (56), bad_candidate 23.9M (46), game_env_route 20.5M (39), game_refused 16.1M (17), game_unmeasured 15.7M (16), game_env_fix 13.1M (16), game_proof_unmeasured 7.5M (8), proof_unrunnable 1.8M (5) |
| Caveat on that 228M | It is the **whole spend of those generations**, so it is an upper bound, not a saving: some of that spend built real code before the setup problem showed, and several late gates (reach, roll call) were added during or after the window and already catch part of it. **What a preflight would save on top of today's gates is UNMEASURED.** Ticket 3 measures exactly that, before anything is allowed to refuse |
| Ledger, terminal events (286 drops, 111 supersedes, 120 closes with no code) | duplicates: 25 items, 5 had work started first, 22 of them in the last 30 days. Already done or moot: 34 items, 12 worked first. False premise: 9 items, 1 worked first `[measured]`. Tokens behind these: UNMEASURED |
| Ledger notes | "not in the running load / not on the list": 88 events on 20 items. "unrunnable / cannot pass": 31 events on 30 items. "no such ...": 80 events on 39 items `[measured]` |
| Open tickets today (782), prototype extraction | 2,352 path mentions: 231 (10%) point at nothing, on 129 tickets. 4,348 `RM_`/`RSW_`/`RUT_` names: 96 are real defs that are **not on the Full list** (27 tickets), 198 are found nowhere at all (up to 96 tickets) `[measured]` |
| Earlier hand counts, quoted from the code that fixed them | Reach: a blind judge spent about 1.5M tokens each to say CANNOT REACH; 32M = 11.1% of one day's spend (2026-11-04). Roll call: 31 items lost about 57 item-games to the mod list. Environment causes: 30 live items, about 105M tokens. Proof line: 9 of 17 unmeasured live runs were a refused proof line. 2026-08-22: the default `needs: offline` was wrong on 45 items and was corrected by hand |

Plain reading: **about one token in eight, in the one week we can measure, went to a generation that ended on a ticket
problem and not on the work.** Each class was later fixed by its own late gate. The pattern is the finding: we pay for
each class once in tokens, then write a gate for it. The preflight is the place those gates go *first*.

What this evidence does **not** show: that every check in section 2 pays for itself. It shows the classes exist and
were dear. So the build is ordered to measure before it enforces (section 7).

### 1.4 The history that limits this design

- **2026-08-21/22, owner: "a missing field is not a rejection".** A completeness gate at claim made thin tickets
  *invisible*; three starved, and 18 of 21 complete tickets became unreachable. So here: a refused ticket is **never
  hidden**. It stays in the queue with its fix line. And a *missing* section only warns (question 1).
- **Refusal contract (spec of the same day).** The concept-floor gate refused 2,599 times on 31 items with one sentence.
  So here: every refusal names the smallest fix, and the same refusal on an unchanged ticket is never repeated silently.
- **Relentless freeze (owner card 2026-11-06).** No new rule, layer, judging machinery or `relentless_rules.json` key.
  So here: Relentless gets no new gate. Its existing checks are *called through* the shared module, and anything new
  runs there in report-only mode until the owner says otherwise (question 2).

## 2. The catalogue of checks

How to read the tables.

- **When**: C = CREATE (just filed or just edited), P = PICKUP (claim, start, helper launch, queue submit, Relentless).
- **Cost class** (per ticket, indexes already loaded): `a` under 1 ms; `b` 1 to 20 ms; `c` 20 to 200 ms;
  `d` 0.2 to 2 s (allowed at PICKUP only, and only when the ticket needs it).
- **Verdict**: every check returns one plain observation: PASS, FAIL or UNMEASURED, with its evidence and, if it has
  one, a proposed repair. What a FAIL *does* is decided afterwards by the door's policy. The column gives the default
  policy: R = refuse, W = warn, A = annotate. "R/W" means: refuse when the fact is *declared* (a machine field or
  the `## refs` block of section 4), warn when it was only found by pattern in prose.
- **Today**: `have` = exists and is called through; `late` = exists but only inside Relentless; `new`.
- Any check may answer UNMEASURED (its data source is missing or stale). UNMEASURED never refuses.

### A. Identity and duplicates (8)

| id | Check | Data source | Cost | When | Verdict | Today |
|---|---|---|---|---|---|---|
| A1 | Name follows the grammar; the verb is a known verb | `cli._mint_or_die` | a | C | R | have |
| A2 | The id is not already used by a live or closed item | ledger replay (already loaded by the CLI) | a | C | R | have |
| A3 | Near-duplicate of an **open** item: same name words or same declared refs | ledger + item titles; word-set overlap | b | C | W, lists the top 3 | new |
| A4 | Looks already done: a **closed** item in the last 60 days with the same subject words or the same declared refs | ledger closes | b | C, P | W, names the close and its sha | new |
| A5 | Still workable: not closed, dropped, superseded or held by another seat since the queue was read | ledger replay | a | P | R, names the successor | have (claim), late |
| A6 | The prose file exists, is non-empty, is the one the ledger names, and has not changed since the last verdict (else re-check) | `infrastructure/state/items/<ID>.md`, content hash | a | C, P | R if missing | new |
| A7 | This exact ticket text was already refused or returned N times unchanged | `repeat_guard.py` (the existing guard, with its own rule; the new repeat *counter* of section 3 is separate and refuses nothing) | a | P | R, routes | late |
| A8 | The verb fits the content: a DESIGN ticket whose criteria demand a build, a BUILD ticket with no build target | name verb + `## criteria` words | a | C | A | new |

### B. References: is the thing real (18)

| id | Check | Data source | Cost | When | Verdict | Today |
|---|---|---|---|---|---|---|
| B1 | Every repo path named exists in the tracked tree | `git ls-files` index (59,743 paths, 0.08 s to build) | a | C, P | R/W, suggests the moved file by basename | new |
| B2 | A path named as "to be created" does **not** exist yet, and its parent folder does | same | a | C | W | new |
| B3 | Paths outside the repo (`D:\ClaudeWork\...`, the game folder) exist | `os.path.exists`, with a 200 ms cap for slow mounts | b | P | W; also feeds D7 | new |
| B4 | Every def named exists in the def dump | `Utils/defindex.py` `Index` (59,262 defs, 316 mods) | a | C, P | R/W, suggests the nearest name | new |
| B5 | A def missing from the dump but present in our source is **"ours, not loaded yet"**, not "missing" | `defindex.src_defs` | a | C, P | A: "build/deploy/dump owed" | new |
| B6 | A def has the kind the ticket says: a "race" is a ThingDef with a race block, a "pawnkind" is a PawnKindDef, a "biome" is a BiomeDef | def index `defType` + race flag | a | C, P | R/W | new |
| B7 | A known rename: the name is an old form (`RSW_X`) of a live name (`RM_X`) | rename map built from the two indexes | a | C, P | W with the new name | new |
| B8 | A texture path resolves to a loose PNG in a mod's `Textures`; base-game and bundle art is UNMEASURED, never "missing" | texture stem index over mod folders | a | C, P | W | new |
| B9 | A C# class or method named exists in our source | C# symbol index (6,928 symbols, 1.5 s to build) | a | C, P | W | new |
| B10 | Every item id named exists; a named item that is dropped or superseded is flagged with its successor | ledger | a | C, P | R/W | new |
| B11 | Every commit sha named resolves in this clone, and is an ancestor of the branch the work starts from (not a commit that never landed) | `git cat-file --batch-check` (12 ms), `git merge-base --is-ancestor` | b | C, P | R/W for "does not resolve"; W for "not landed" | new |
| B12 | Every script in a `## verify` command exists and is tracked; every selftest named is in the selftest registry | ls-files index; `Utils/run_selftests.py` list | a | C, P | R | new |
| B13 | Every mod named (name or packageId) resolves to exactly one installed mod | `relentless_names.resolve` | b | C, P | R on `live-mods:` lines, W in prose | late |
| B14 | Every bridge tool named (`jawa/...`, `rimbridge/...`) is on the last recorded tool list | cached tool list from the last bridge session | a | C, P | W | new |
| B15 | A skill, hook or CLI verb named exists | skills folder listing; `rimflow --help` verb list cached by file hash | a | C | W | new |
| B16 | `file.py:1234` points inside the file | line counts in the path index | a | C | A | new |
| B17 | The ticket names a thing on the retired list (FOUNDRY, the L1 manifest, deleted tools) | a short retired-names file, each with its replacement | a | C, P | W with the replacement | new |
| B18 | A patch file the ticket declares: every xpath matches something in the dump of the ticket's list (a patch that matches nothing logs nothing in game) | `skills/rimworld-modding/scripts/validate_patch.py` with `--defs`, called as a library, declared files only | c | C, P | W; UNMEASURED when the dump is of another list | new |

### C. Mod list: can the game hold what the ticket needs (12)

| id | Check | Data source | Cost | When | Verdict | Today |
|---|---|---|---|---|---|---|
| C1 | The tier named is a real tier | `Utils/modset_builder.py` tier table | a | C, P | R | new |
| C2 | Every declared def is **provided by the declared mod list** | `defindex.ModSetDefs(index, packages, src).provided()` | a | C, P | True ok; False (the owning mod is not on the list) = R with "add mod X" or "use tier Y" as a *candidate* fix; None = UNMEASURED. A True means "the owning mod is on the list", not "the game will surely hold it": conditional loading is not checked (2.2) | new |
| C3 | Every mod on `live-mods:` resolves, and the dependency closure completes | `relentless_names`, `modset_builder` closure | b | C, P | R | late |
| C4 | **Full Mod reason on record.** A ticket that asks for the Full list must carry a `full-why:` line with one of the allowed reasons (section 2.1) | live-proof file / `## refs` | a | C, P | R, and prints a candidate minimal list | new |
| C5 | **Minimal list candidate.** From the declared defs, compute the owning mods plus closure and print it as a ready `live-mods:` line. It is a candidate: a 22-second load on it shows the list loads, and only the proof run shows the test can pass on it | def index owner field + closure | b | C | A | new |
| C6 | The proof script's own def names are on the mod list (the script is scanned like a ticket) | script text + C2 | b | C, P | W | new |
| C7 | A `live-without:` mod is not a hard dependency of a required mod | closure | a | C, P | R | new |
| C8 | Our mod's deployed copy matches the source (the game reads the game folder, not the repo) | `deploy_custom_mods.py` plan, cached by tree hash | c | P, live only | A: "deploy owed" | new |
| C9 | The running load set against the list the ticket needs; cost of getting there (22 s minimal, about 25 min Full) | `refresh.py` fingerprint; `ModsConfig.xml` **parsed** | b | P, live only | A | new |
| C10 | The dump is of the list the ticket means: a def "missing" from a dump of a *different* list is UNMEASURED | dump capture fingerprint | a | C, P | a FAIL from B4 or C2 becomes UNMEASURED (status), which the door shows as a warning (severity) | new |
| C11 | The **order** of an explicit mod list obeys each mod's `loadAfter` / `loadBefore`, and has no order cycle | `About.xml` of the listed mods (parsed, cached by installed-mods fingerprint) | b | C, P | R on a declared list, with the corrected order as the fix | new |
| C12 | No two mods on the list declare each other incompatible; each supports the installed game version | `About.xml` `incompatibleWith`, `supportedVersions` | b | C, P | R | new |

#### 2.1 Full Mod justification (the owner's explicit rule)

The default is the smallest list that holds the ticket's declared defs. A ticket may ask for the Full list only with one
`full-why:` line that starts with one of these words, followed by the specifics:

- `interaction:` with a named mod that is not ours (the named mod must resolve, B13);
- `load-order:` a conflict or patch order that only shows with the whole list;
- `performance:` a cost that only shows at full scale;
- `owner-save:` the test needs the owner's campaign or a save made on the Full list;
- `explicit:` the ticket *is* a Full Mod test by name, called out by the owner or the Conductor. The line must name the
  ledger event or ruling id that says so, and that id must exist (B10). A copied quote with no event behind it does not count.

No line, or a line that names none of these: REFUSE, and the refusal prints a candidate minimal list, so obeying costs
one paste. The preflight reports "reason recorded", never "justified": it checks shape and real names only, and the
five words could become a password that agents paste. So the weekly report lists every Full reason given, by reason
and by ticket, for a person to read. The candidate list is never called equal to the Full list; a ticket with few
declared defs gets a poor candidate, and the output says how many defs it was computed from.

### D. Environment (13, PICKUP only)

| id | Check | Data source | Cost | When | Verdict | Today |
|---|---|---|---|---|---|---|
| D1 | The game is running and the bridge answers, **only if the ticket needs a live game** | `rimflow/probe.py` `measure` (1.6 s measured) | d | P | A + route to the live queue; never a refusal of the ticket | have |
| D2 | The def dump is fresh against the load set | `Utils/refresh.py` | b | P | W; turns def refusals into warnings | have |
| D3 | Free disk on the scratch drive and the game drive | `shutil.disk_usage` (0.2 ms) | a | P | R below a floor, for build and live tickets | new |
| D4 | The clone is not far behind origin; the ticket's files are not dirty from another seat | `git status --porcelain -uno` (0.1 s), last fetch | c | P | W | new |
| D5 | The tools the ticket needs are present: build chain, codex CLI, Python modules | `shutil.which`, `importlib.util.find_spec` | b | P | R | new |
| D6 | Who holds the bridge lock | `rimflow bridge who` data | a | P, live | A | have |
| D7 | Reach: the proof needs a hidden path, git history, a remote host or a Windows program this worker cannot reach | `relentless_reach.needs` | a | C, P | R/route | late |
| D8 | The Windows mounts the ticket names are mounted | `os.path.ismount` | a | P | R | new |
| D9 | An environment variable a tool needs is set (the value is never read out or printed) | `os.environ` | a | P | R for art and GPT tickets | new |
| D10 | A `DEPLOY_HOLD.txt` covers a file the ticket must deploy | mod folder | a | P | W | new |
| D11 | The live queue's depth and the last measured wait | `testq` state | a | P, live | A | new |
| D12 | A known environment cause is active right now (the class list of `relentless_envcause`) | last probe + envcause table | a | P, live | A + route | late |
| D13 | A mod-list swap is in flight or was never restored (the game's next load is not what anyone thinks) | `Utils/modlist_swap.py` state file; `ModsConfig.xml` parsed against its backup | b | P, live | A + route | new |

### E. Specification completeness (11)

| id | Check | Data source | Cost | When | Verdict | Today |
|---|---|---|---|---|---|---|
| E1 | Has `## spec`, `## verify`, `## criteria` | `model._missing` | a | C, P | W (owner ruling 2026-08-21) | have |
| E2 | Size: a body under about 200 characters, or over about 40,000 | prose file | a | C | W: "too thin to work" / "split it" | new |
| E3 | `needs` agrees with the content: a ticket with live-proof lines or bridge calls is not `offline` | ledger field + proof file | a | C, P | R with the corrected value | new |
| E4 | No placeholders left in spec or criteria: `TODO`, `TBD`, `???`, `<fill in>` | prose | a | C | W | new |
| E5 | Every criterion has an id, and the ids are unique | `## criteria` | a | C | W (a missing field is not a rejection); R only for two criteria with the same id | new |
| E6 | Collides with a standing ruling by its own words: asks for worldgen, a live flight test of a flyer, a FOUNDRY build, a tile count for our biome as a defect | pattern list tied to `design/RimMandrake/standing_rulings.md` anchors | a | C, P | W, quotes the ruling | new |
| E7 | Provenance is present: an owner quote or a `--why` | filing event | a | C | A | have |
| E8 | `needs: owner` carries a question the owner can answer (a question block exists) | prose | a | C | W | new |
| E9 | Scope: the declared refs span more than N mods or M files | `## refs` | a | C | A: "consider splitting" | new |
| E10 | A design parent is named for a build ticket, and the parent spec file exists | `## refs` + B1 | a | C | W | new |
| E11 | The declared block and the proof file parse strictly: no unknown key (a typo that silently switches a check off), no two different tiers, no malformed value | the `## refs` grammar; live-proof line kinds | a | C, P | R, names the line and the nearest valid key | new |

### F. Acceptance-test sanity (13)

| id | Check | Data source | Cost | When | Verdict | Today |
|---|---|---|---|---|---|---|
| F1 | `## verify` names at least one **runnable** thing: a command, a selftest, or a live-proof id | prose + proof file | a | C, P | W at C, R at P for build/fix tickets | new |
| F2 | The command is valid shell (`bash -n`, not a Python guess at shell) and its Python script compiles | `bash -n` with a timeout; `ast.parse` (under 200 ms on our largest file) | c | C, P | R | new |
| F3 | The live-proof lines lint clean | `relentless_live.lint_lines` | a | C, P | R | late |
| F4 | **Can fail.** The proof is not empty of judgement: the script has a failing path (an assert, a FAIL row, a non-zero exit) and the criterion states an expected value or comparison | script text patterns | b | C | W | new |
| F5 | **Can pass on this tier.** Everything the criterion names is provided by the ticket's mod list | C2 over criterion refs | a | C, P | R | new |
| F6 | **Measurable where it says.** `needs: offline` but the verify script imports the bridge client, or the reverse | script import scan | b | C, P | W with the fix (an import is a hint, not proof of use) | new |
| F7 | Every criterion id has a proof bound to it, and every proof id has a criterion | proof file ids against criteria ids; `relentless_binding` | a | C, P | R | late |
| F8 | The proof's fixtures exist: saves, scenario JSON, expected files. A save fixture's own mod list (read from its header) fits the ticket's list | B1 over the proof's paths; first kilobytes of the `.rws` | b | C, P | R for missing; W for a mod-list mismatch | new |
| F9 | The proof's producer ran in the last 14 days (the refusal contract's "attainable" rule) | run records | a | P | W | new |
| F10 | The proof uses a forbidden method: worldgen, flying a flyer | a machine line that names the forbidden tool call; script patterns + E6 list | a | C, P | R on a machine line, quoting the ruling; W on a pattern (a test that *asserts* worldgen is off must not be stopped) | new |
| F11 | Expected run time of the proof from past runs of the same script, against the limits it must fit (the 540 s command limit, the helper's time cap) | run records; the brief's `max-s` | a | P | A; W when the median past run is over the limit | new |
| F12 | The last known result of the named selftest at this tree (from cache; preflight **never runs** a test) | selftest result cache | a | P | A | new |
| F13 | A failure cannot reach the judge: the verify command pipes into `tail`/`grep`/`tee` with no `pipefail`, ends in `\|\| true`, or wraps everything in a bare `except: pass` | command text; script AST | b | C, P | W with the corrected command | new |

### G. Dependencies and ordering (7)

| id | Check | Data source | Cost | When | Verdict | Today |
|---|---|---|---|---|---|---|
| G1 | Every `blocked-by` item is closed | ledger | a | P | R, names the blocker | new |
| G2 | No dependency cycle | ledger graph | b | C | R | new |
| G3 | Depends on a dropped or superseded item | ledger | a | C, P | W with the successor | new |
| G4 | Another in-flight item or seat declares the same files | declared refs of started items | b | P | W, names the other item | new |
| G5 | First-touch hold: the mod has no Designer pass | `relentless.first_touch_hold` | a | P | hold | late |
| G6 | Build order: a ticket marked "N of a spec" while N-1 is open | parent spec ticket list | a | P | W | new |
| G7 | Waits on an owner answer that is still open | question items in the ledger | a | P | R/route | new |

### H. Budget and model routing (6)

| id | Check | Data source | Cost | When | Verdict | Today |
|---|---|---|---|---|---|---|
| H1 | A token cap exists for this kind; the median past spend of the kind is attached | spend records | a | C, P | A | new |
| H2 | Past spend on **this** item against its cap (one item took about 90M against a 4M cap) | Relentless store `spend-*.json` | b | P | R, routes to a consult or a Test Pilot sitting | late |
| H3 | Three non-pass runs in a row | attempts | a | P | route to Test Pilot | late |
| H4 | The model fits the kind: design and hard code on opus, checkable fixes on sonnet, never haiku | helper brief / hook | a | P | R | have |
| H5 | Helper slots and helper budget | `.claude/hooks`, `helper_budget.py` | a | P | R | have |
| H6 | Reading cost: the declared files, or the helper brief itself, add up to more than a set size | path index byte sizes; brief length | a | C, P | A: "measure, do not read" | new |

### I. Seat and authority (7)

| id | Check | Data source | Cost | When | Verdict | Today |
|---|---|---|---|---|---|---|
| I1 | This seat may work this ticket (BENCH takes only `needs: owner` live looks; FOUNDRY is retired) | standing rulings table | a | P | R | new |
| I2 | Focus cap | `cli.cmd_claim` | a | P | R | have |
| I3 | A provenance flag is well formed: `--owner-said` carries a quote | filing args | a | C | R | have |
| I4 | A declared write target is forbidden: the read-only mirror, the game's Mods folder by hand, `~/dev` scratch | `## refs` `new:` lines | a | C, P | R | new |
| I5 | The ticket would change a frozen thing (a new `relentless_rules.json` key, a new Relentless rule) | declared refs + freeze entry | a | C, P | W, quotes the freeze | new |
| I6 | The item exists on origin, so a helper in another clone can see it | `detached_helper.launch` | b | P | R | have |
| I7 | One ticket all the way down: the proof file's ids, the helper brief and the queue job all name **this** item | proof file, brief text, job JSON | a | P | R | new |

**Total: 95 checks.** 8 + 18 + 12 + 13 + 11 + 13 + 7 + 6 + 7. Of these, 13 exist and are called through, 10 exist only
inside Relentless and are moved earlier, 72 are new. None needs a model. How much code each takes is not known until built; the isolation, the overlay and the repair
proposals are the larger parts.

What Python deliberately does **not** try: whether the idea is good, whether the criteria are the right ones, whether a
Full Mod reason is true. Those stay with people and models. The preflight only removes "this cannot be worked as written".

### 2.1b A thing the ticket will make is not a thing that is missing

Several checks (B1, B12, F1, F2, F7, F8) would stop a build ticket whose job is to write its own test script or
fixture. So: anything listed under `new:` or `new-def:` is exempt from "must exist" at CREATE and PICKUP, and is owed at
close. Every "does not exist" refusal offers two fixes: the corrected name, **or** "declare it `new:` if this ticket
creates it". The same holds for the environment: a ticket whose declared output is a tool is not refused for lacking it.

### 2.2 Considered and put off (each needs a prepared data source we do not have, or has no measured waste behind it)

| Idea | Why not now |
|---|---|
| Harmony targets checked by exact signature against the game's assembly | Needs an assembly metadata index and a builder for it. Worth doing if the backtest shows wrong-overload waste; UNMEASURED today |
| Parent and cross-references of a declared def resolve inside the tier | Needs a def reference graph per tier. The dump has the data; the index does not carry it yet |
| Conditional loading (`MayRequire`, versioned folders) of a declared def | Same: needs load-rule metadata in the index |
| Translation keys and their placeholders | No measured waste in the ledger or the store |
| Typed criteria checked for contradiction (two bounds that cannot both hold) | Needs typed criteria; ours are prose with ids |
| Token count of a brief against the model's window | Needs a tokenizer in the hot path; byte size (H6) is the cheap stand-in |
| Budget reservations across jobs running at once on one item | A new admission mechanism, not a check; and frozen ground in Relentless |

### 2.3 Three shelves: what is built first, and what must earn a place

The catalogue is everything Python could reasonably check. It is not all built at once, and some of it may never be.

| Shelf | Checks | Rule |
|---|---|---|
| CORE (tickets 1 and 2) | Ticket 1: B1, B4, B5, C1, C2, C10. Ticket 2: B6, B10, B11, C4, E11. Ticket 3 adds the wrappers that observe and time every `have` and `late` row | Existing indexes only. The owner's named asks |
| NEXT (tickets 5 to 9) | The rest of B and C, D, E1, E3, E5, E6, F1 to F3, F5 to F8, F10, F13, G1 to G5, G7, H1 to H5, I1 to I7, A3, A4 | Built in the order of section 7 |
| CANDIDATE | A8, B16, E2, E4, E8, E9, E10, F4, F9, F11, F12, G6, H6 | Heuristics with no measured waste behind them yet. Each is built only if the shadow run (ticket 3) shows the class costs tokens, and ships as WARN or ANNOTATE |

## 3. What a refusal looks like, and who may override

### 3.1 The shape

A refusal obeys the refusal contract (`design/specs/2026-11-12-refusal-contract-for-judges-and-gates.md`). It carries the
same fields: `clause` (the check id), `evidence` (where the preflight looked), `observed`, `would_pass`, `smallest_fix`
(with `attainable` and a cost class), `new_since` (is this the first time, or unchanged since when).

What the worker sees at the door (the ticket, mod and file names in this example are made up to show the shape):

```
PREFLIGHT REFUSED  RIMMANDRAKE_FIX_SHIELD_PULSE_ON_MINIMAL   (pickup, 412 ms, 61 checks: 58 ok, 2 warn, 1 refuse)

REFUSE C2  def not on the ticket's mod list
  observed:    RUT_ShieldGenerator is a real ThingDef (mod mandrake.util.shields) but live-mods names 13 mods, none provide it
  looked at:   def index capture 2026-11-12T08-10-06Z; live_proofs/<ID>.txt line 3
  would pass:  the def is provided by the list
  proposed repair (one line, no tokens; a candidate, the proof run decides):  live-mods: +mandrake.util.shields
  first seen:  now

WARN  B1   Transient/shield_notes.md is not in the tree. Nearest: design/RimMandrake/shields/shield_notes.md
WARN  E4   "TBD" in ## criteria line 4

To go ahead anyway:  rimflow claim <ID> --preflight-override "C2: <why>"
```

Rules that make this safe:

1. **No fix, no refusal.** A check may be registered as REFUSE only if it has a function that returns a **proposed
   repair** as a concrete edit or command. The selftest does more than look for the function: for each refusing check
   it applies the proposed repair to the planted bad ticket and requires that the **whole report** is then clean
   (adding a mod can satisfy C2 and break C7) and that nothing else in the ticket changed. A check that can only say "something is wrong" is a WARN.
   A proposed repair is a proposal. A nearest file name or a renamed def may not be what the author meant, so the
   refusal says "proposed", and where there are two candidates it lists both.
2. **Never "nothing could pass".** If the smallest fix is not attainable (the def exists in no installed mod; the
   blocker was dropped with no successor), the preflight says so in those words, marks the criterion `unattainable`,
   and raises the existing alarm `REFUSAL_NOTHING_COULD_EVER_PASS` to the Conductor. It does not keep the ticket at the
   door to be refused again.
3. **Never the same refusal twice in silence.** The verdict is cached by (ticket content hash, index fingerprints).
   An unchanged ticket refused again prints "unchanged since <date>, refused N times" and, on the third time, files
   one note to the Conductor: the ticket needs an editor, not another attempt. This is a counter, not a new gate.
4. **A refused ticket stays visible, and stays repairable.** `rimflow queue` and `next` show it with its fix line.
   Nothing is filtered out. (This is the 2026-08-21 lesson.) Editing a ticket is never a pickup and is never refused.
   Who repairs: whoever tried to pick it up, if the repair is one line (they paste it and claim again); otherwise the
   third-refusal note of rule 3 puts it in front of the Conductor, who repairs it, drops it, or overrides.
   A refusal whose cause the ticket itself is meant to remove (2.1b) is not a refusal.
5. **UNMEASURED is not a refusal.** A missing index, a stale dump, a slow mount: the check says UNMEASURED with the
   reason and the command that would make it measurable.
6. **The preflight never weakens a gate we already have.** The existing gates (`have` and `late` rows) keep deciding
   in their own code, called by their own doors, exactly as today, including what they do when they throw. The
   preflight *observes* them: it records their answer and their time under its check id. A gate's authority moves into
   the registry only later, one gate at a time, after a selftest shows the two give the same answer on the same
   tickets, exceptions included. A **new** check that throws reads UNMEASURED (error) and is recorded. If the runner
   itself fails (corrupt cache, import error), the door says "preflight did not run" and carries on with its own gates.
   A failure to write the timing line is reported and stops nothing.
7. **The tool proposes; it does not edit.** `rimflow preflight <ID> --fix` prints the proposed edits as a diff and
   changes nothing. Mechanical repairs (a mistyped key, a `needs` value that contradicts the proof file) and
   meaning-changing ones (another path, another def, another mod list) are labelled apart. An engine that applies
   repairs is put off until the proposals have been read on real tickets.

### 3.2 Override

- **Who:** any worker, with a recorded reason (recommended; question 5). The owner's own history says a gate that only
  the Conductor can open starves tickets.
- **How:** `--preflight-override "<check id>: <why>"` on the same verb. The override names the check; there is no
  blanket override. It is written into the ledger event the door already writes, with the provenance `--why`.
- **Only new checks.** The override opens checks this design adds. Every gate that exists today (focus cap, helper
  slots and budget, seat rules, reach, roll call, proof lint) keeps the override rule it has now, which for most is
  none. The flag is refused for their ids.
- **What cannot be overridden by a worker:** I4 (writing the mirror or the game folder by hand) and F10/E6 (a standing
  ruling). Those need the owner's word, recorded with `--owner-said`.
- **What happens to overrides:** they are counted per check in the weekly timing report. A check that is overridden in
  more than about a third of its refusals is flagged for review in the report; a person reads the cases and decides.

## 4. Finding mentions in prose without a model

### 4.1 What the prototype measured (782 open tickets, script `proto_extract.py`)

| Pattern | Mentions | Result |
|---|---|---|
| Repo-like paths | 2,352 | 2,043 resolve; 231 missing (10%); 78 more are missing but sit next to "create/new/add" |
| `RM_` / `RSW_` / `RUT_` names, checked against the def dump only | 4,348 | 1,994 on the Full list; 96 real but not on the Full list; **2,071 (48%) unknown** |
| The same 2,071, after also checking C# symbols (826), file and texture stems (373), any source text (597), wildcard prefixes like `RM_Huge*` (77) | | **198 found nowhere** (plus 34 in create context) = 5.3% of mentions |
| ALLCAPS item-like ids | 2,615 | 916 unknown: mostly handoff ids, constants, headings |

So a pattern alone is wrong about half the time when it asks one index, and still wrong often enough to matter when it
asks all of them. **A pattern must never shut a door.** But the 198 + 231 + 96 that remain are exactly the lines a worker
wants to see before starting.

### 4.2 The answer: both, with three levels of trust

Every mention becomes one record, whatever its source: `{kind, value, intent: exists | created-here, origin: machine |
confirmed | auto | prose, where: file and line}`. One rule then covers what was scattered: only `machine` and
`confirmed` origins may refuse; `created-here` exempts the **existence** check and nothing else (a planned script is
still checked for a valid command and for a criterion bound to it); two records that contradict each other (two tiers,
a def both `exists` and `created-here`) are a FAIL that names both lines.

| Level | What | May refuse? |
|---|---|---|
| 1. Machine fields | The ledger fields (`needs`, `blocked-by`), the live-proof file lines (`live-proof`, `live-tier`, `live-mods`, `live-without`, `live-deploy`, `live-companion`), the commands inside `## verify` | yes |
| 2. Declared block | A `## refs` section in the ticket, one fact per line (below) | yes |
| 3. Prose patterns | Backticked tokens, path shapes, our name prefixes, item-id shapes, 7 to 40 hex characters next to "sha" or "commit" | no: warn or annotate only |

The declared block (example values, not checked names):

```
## refs
file:    src/RimMandrake/HugeThings/Source/Kernel/RM_HugeTitanKernel.cs
def:     ThingDef/RM_HugeTitanKernel
race:    RM_Wuum
mod:     mandrake.util.shields
item:    RIMMANDRAKE_BUILD_PREFLIGHT_SPINE_TIMED_FROM_BIRTH
sha:     4594675ed9
symbol:  RM_HugeTitanKernel.TickLong
texture: Things/Building/RM_Shield/RM_Shield_south
tier:    minimal
full-why: interaction: with VFE Mechanoids patch order
new:     src/RimMandrake/rimflow/ticket_preflight.py
new-def: ThingDef/RM_ShieldRelay
```

`new:` and `new-def:` mean "this ticket creates it": the check is reversed (it must *not* exist yet at CREATE, and it
must exist at close, which gives the closing gate a free check later).

**Nobody types this block.** At filing, the preflight runs the level-3 patterns, resolves what it can, and prints the
block ready to paste, with the unresolved names listed apart ("found nowhere: is it new, or a typo? nearest: ..."). With
`rimflow file --refs-auto` it writes the resolved lines itself. Declaring costs nothing; that is what killed the L1
manifest and it must not kill this.

**A guess written down is still a guess.** A line the tool wrote carries the mark `(auto)` at its end. An `(auto)` line
is treated as level 3: it may warn, never refuse. It becomes a declared fact when a person or the working agent removes
the mark from **that line**, which is the act of saying "yes, the ticket needs this". There is no command that confirms
them all at once; that would turn every guess into a fact with one keystroke.
Otherwise a name the prose only mentioned in passing ("unlike X") would become a reason to shut a door.

**Why this will not rot like the L1 manifest, and how we will know if it does.** The manifest was checked against a
frozen fixture and only when someone remembered. These lines are checked against the live indexes at every door, so a
rename shows up the same day with the new name proposed. Two ways it can still fail, and the counter for each:
agents confirm everything to quiet the warnings, or declare nothing so nothing can refuse. So every verdict states its
**coverage** ("declared 6, auto 9, prose-only 14; 61 of 70 checks ran"), and the weekly report gives the share of
picked-up tickets with no declared line and the share of refusals later overridden. A ticket with nothing declared is
no worse off than today: it still gets its warnings.

### 4.3 Keeping false alarms down

- Level 3 asks **every** index before it speaks (defs, source defs, C# symbols, file stems, texture stems, item ids),
  and speaks only about names found in none.
- Words around the mention decide its sense: "create, add, new, will write, propose" make it a `new:` candidate;
  "deleted, retired, removed, was, old, no longer" make it a skip; a trailing `*` or `...` makes it a prefix.
- Fenced code is read as code only inside `## verify`; elsewhere it is an example and only annotates.
- At most 8 warning lines per ticket, strongest first (declared, then exact-shape paths, then names). The rest are
  counted, and `rimflow preflight <ID> --all` shows them.
- Nearest-name suggestions come from `difflib` over the index, only for unknown names, at most 20 per ticket.
- A pattern class goes live only after the backtest (section 8) shows under 10% false alarms on a hand-labelled sample;
  until then it runs silently and is only counted.

## 5. Speed: budget, caches, and the recorded time

### 5.1 What things cost today `[all measured, 2026-11-12, this machine]`

| Step | Time |
|---|---|
| Ledger replay (the CLI already pays this on every verb) | 1.9 s |
| `rimflow namecheck` end to end | 1.8 s |
| Def index: cold build from today's dump (59,262 defs, 316 mods) | 62 s |
| Def index: warm load from cache | 0.27 to 0.44 s |
| Our source defs (`src_defs`) | 1.24 s |
| `git ls-files` (59,743 paths) | 0.08 s |
| C# symbol index (6,928 symbols) | 1.48 s |
| Any-source-token index (16,789 tokens) | 1.53 s |
| Extract and resolve one ticket, indexes loaded | median 0.11 ms, p95 5.75 ms, max 41.7 ms |
| `probe.measure` (game + bridge) | 1.59 s |
| `git status --porcelain -uno` | 0.10 s |
| `git cat-file -e <sha>` | 12 ms |
| `ast.parse` of our largest file (8,500 lines) | 0.19 s |
| Disk free | 0.2 ms |

In the prototype, extracting and resolving is nearly free; the cost is loading indexes, and the danger is *building*
them. That decides the design. The prototype is not the catalogue: ticket 1 measures the real command.

### 5.2 The budget

| Trigger | Added time, p95 target | Hard stop | What is allowed |
|---|---|---|---|
| CREATE (`file`, an edit of the ticket) | **1.0 s** | 3 s | classes a, b, c. No game probe, no subprocess except one batched git call |
| PICKUP, offline ticket | **1.0 s** | 3 s | the same, plus D3 to D5 |
| PICKUP, live ticket | **3.0 s** | 5 s | plus the game probe (1.6 s, with its own 2.5 s timeout) and C8/C9 |
| Sweep of all open tickets (782 today) | **under 5 s in all** | 30 s | indexes loaded once; no environment group |

"Added" means on top of the ledger replay the CLI already pays. A check that passes its own limit (default 250 ms; the
probe 2.5 s) is cut off and reports UNMEASURED (timeout). When the hard stop is reached the remaining checks are skipped
and listed as UNMEASURED, and the door opens with the note. **A slow preflight degrades to a weaker preflight. It never
becomes a long wait, and it never becomes a refusal.**

How the stop is real and not a wish: Python cannot interrupt a blocking call, and a thread stuck on a dead mount can
hold the whole command open. So: (1) **all new checks and all index loading run in one child process** with one
absolute deadline; the parent kills it at the hard stop and uses whatever observations it had already sent back, one
line each as they finish. The parent hands the child the few ledger facts it needs, so the ledger is not replayed
twice. (2) The existing gates run outside that child, in their own doors, as today: the deadline cannot weaken them.
(3) Parsing is bounded: a ticket over 200 kB or a script over 1 MB is not parsed, and reads UNMEASURED (too large).
(4) Checks that may refuse run first, so a cut-off costs annotations first. Every verdict prints its coverage
("61 of 70 checks ran, 9 cut off"), so a weak run cannot pass for a full one.

The numbers in 5.1 are for a prototype that extracts and resolves; they are not the finished system. Ticket 1's proof
is the real measurement: whole command, cold and warm, with another seat busy in the clone.

### 5.3 Caches: a door loads, it never builds

| Index | Key | Built by | If it is missing at the door |
|---|---|---|---|
| Def index (`~/.cache/rimmandrake/defindex/<capture>.json.gz`, exists) | the dump's capture stamp | `Utils/refresh.py` right after a dump (62 s, once per dump) | def checks say UNMEASURED and print the build command. The door does **not** build it |
| Reference index (new, `~/.cache/rimmandrake/refindex/<tree>.json.gz`): tracked paths with sizes and line counts, our source defs, C# symbols, texture and file stems | `git rev-parse HEAD^{tree}` + index schema version; **plus a bounded overlay** (next column). Installed-mod textures are keyed by the installed-mods fingerprint, not the tree | an explicit command, `rimflow preflight --build-index` (full build about 4.3 s `[measured sum]`), run outside any door; which existing step calls it (after a landing, after a sync) is settled in ticket 4. A door **never builds**. It loads the newest prepared index and overlays the files that differ from it (`git diff --name-only <indexed tree> HEAD` plus the changed files), re-reading at most about 200 `[guess ~80%: under 0.3 s for a normal day's commits]` | no prepared index, or more than about 200 differing files: reference answers read UNMEASURED and the command to build is printed |
| Ledger summary for duplicate and dependency checks | the replay the CLI already did | in memory | n/a |
| Mod name resolver, tier table | the installed-mods fingerprint | `relentless_names` (exists) | UNMEASURED |
| Verdict cache (`<scratch>/preflight/verdicts/<ID>.json`) | ticket content hash + proof file hash + def capture + tree + installed-mods fingerprint + registry version + trigger | each run | recomputed |

The verdict cache serves only the read-only views (`queue`, `next`, the Agent-spawn hook). **A door that leads to tokens
always runs the checks again**; they cost milliseconds, and a cached "ok" from before a commit is how stale answers
start. Index files are written to a temporary name and renamed, so a reader never sees half an index.

Uncommitted files: the overlay above means an uncommitted rename or a file written a minute ago is seen, for paths,
source defs and symbols alike.

### 5.4 The metric the owner asked for

Every run, at every door, writes one line, including runs that were cut off. The write is best effort: if it fails,
the door says so on screen and goes on, and the gap shows as a missing run id against the ledger events.

- **Where (detail):** `~/.local/state/rimmandrake/preflight/runs.jsonl` on the Linux file system, beside the existing
  `~/.cache/rimmandrake` (a program reads it, so it is not in the repo; and not on a Windows mount, where a stalled
  drive is a known way to hang). Rotated by size. **Every attempt is a line: passes, refusals, overrides, cut-offs and crashes.**
  A refused claim writes no claim event, so without this the dearest cases would vanish from the numbers.
  One line: `run_id, at, item, trigger, door, seat, total_ms, index_load_ms, cache (hit/miss per index), verdict,
  checks: [{id, ms, verdict}], cut_off, override`. Timing by `time.perf_counter_ns`.
- **Where (durable):** the ledger event the door already writes (`file`, `claim`, `start`) gains two fields:
  `preflight_ms`, `preflight_run` (the same `run_id`) and `preflight` (the verdict and the refusing check ids). The run
  id is what lets a later count say "this refusal came before any token" or "this spend followed an override". No new event kind for a pass.
- **Refusals in the ledger:** the first refusal of a ticket at a given content writes one `note` event with the check
  ids and the run id. A repeat on the unchanged ticket writes nothing to the ledger (the 2,599-repeats lesson); the
  local file has them all.
- **How to read it:** `rimflow preflight --timing` prints, for the last 200 runs and per trigger: count, p50, p95, max,
  the five slowest checks, cache miss rate, cut-off rate, coverage, override rate per check, and per ticket the
  **total time spent at the door over all its visits**.
- **Drift alarm:** (1) the p95 of the last 50 runs of a trigger is over its target; or (2) a check's p95 has doubled
  against its own first 200 runs; or (3) cut-offs pass 2% of runs. The alarm is one line at the door
  ("preflight is slow: p95 1.8 s against 1.0 s, slowest C8") and one filed item, once, under one fixed name so it cannot
  pile up. (4) A selftest runs the preflight over a fixed corpus of 50 tickets and fails if the total passes a set
  limit, so a slow check is caught at commit, before it reaches a door.

## 6. Where it lives, and which doors call it

### 6.1 One shared module (recommended), not one per door

Separate checks per door is what we have now, and section 1.1 shows the result: good checks that most tickets never meet.
The price of one module is that one bug reaches every door. Three things bound that: the existing gates stay in their
own code (3.1 rule 6); a runner failure opens the door with a note and never shuts it; and the selftest breaks each
adapter on purpose and requires the other doors to keep working.

| File | Role |
|---|---|
| `src/RimMandrake/rimflow/ticket_preflight.py` (new) | The registry of checks, the runner (`run(item_id, trigger, door) -> Report`), the timing, the refusal text, the verdict cache, and **one policy table per door** (which groups run, which may refuse there). Each check is a small function with: id, group, triggers, cost class, verdict kind, data needs, and (if it may refuse) a repair function. Each check's imports are lazy: an offline claim never imports the live-game or bridge code, so a break there cannot stop an offline door |
| `src/RimMandrake/rimflow/ticket_refs.py` (new) | Extraction: machine fields, the `## refs` block, prose patterns. Pure text in, typed mentions out |
| `src/RimMandrake/rimflow/ref_index.py` (new) | The reference index of 5.3 and one question: `what_is(name) -> [(kind, where)]`. Wraps `Utils/defindex.py`; does not replace it |
| `src/RimMandrake/rimflow/selftest_ticket_preflight.py` (new) | For every check: one planted bad ticket it must catch, one good ticket it must pass; the registry rule "no fix, no refusal"; the timing corpus |
| The result type | Reuse the PASS / FAIL / UNMEASURED `Check` shape of `Utils/northstar_driver/preflight.py`, extended with `ms` and `fix` |

### 6.2 The doors

| Door | Code | Trigger | Behaviour |
|---|---|---|---|
| Filing | `cli.cmd_file` | CREATE | Runs groups A, B, C, E, F, G2, H1, I3 to I5. Prints the proposed `## refs` block. Refuses only on level 1 and 2 facts (question 1 decides whether CREATE refuses at all) |
| Ticket edited | `.claude/hooks/queue_lint.py` (exists, on Write/Edit of `items/*.md`) | CREATE | The same run, warnings only, so a repaired ticket gets its answer at once |
| Claim / start | `cli.cmd_claim`; `start` (the `_simple("start")` handler, whose help says "never refused for missing prose": that stays true, a missing section only warns) | PICKUP | Everything. This is the main door: the last moment before tokens |
| Queue / next | `cli` `queue`, `next` | none | Reads the verdict cache and shows the fix line beside a refused ticket. Runs nothing; hides nothing |
| Helper launch | `detached_helper.launch` | PICKUP | Everything, run **in the helper's clone at launch**, against the ticket and proof file that clone holds (I6, I7), so a pass in the launcher's clone cannot stand in for a stale copy. Its own five checks stay in its code and are observed |
| Live-queue submit | `Utils/testq/schema.py` `validate_job` and its caller | PICKUP (live) | Groups C, D, F for the job's ticket. The three existing pre-load preflights stay where they are (they check the *load*, not the ticket) and share the result type |
| Relentless pickup | `relentless.eligible` / `admission` | PICKUP | Under the freeze: **report-only**. The checks Relentless already has (reach, roll call, proof lint, binding, first touch, repeat guard) keep refusing exactly as today, in their own code. A thin wrapper records each one's answer and time. New checks only write to the metric; turning any of them into a refusal there needs the owner's separate word (question 2) |
| Agent spawn | `.claude/hooks` PreToolUse Agent | none | **Not a recompute, and not enforced.** If the brief names an item id, the hook reads the verdict cache and warns when the last verdict is a refusal or is missing. Under 10 ms. Later ticket. Said plainly: an in-session helper is covered by its parent's claim, not by this hook |
| By hand | `rimflow preflight <ID> [--trigger create|pickup] [--json] [--fix] [--all]`, `rimflow preflight --sweep`, `--timing` | either | For workers, the Conductor and the backtest |

### 6.3 What is absorbed and what is beefed up

- **Observed first, unchanged in behaviour and in authority:** `_mint_or_die`, `model._missing`,
  `relentless_live.lint_lines`, `relentless_reach.needs`, `relentless_names.resolve`, `relentless_binding`,
  `first_touch_hold`, `repeat_guard`, `probe.measure`, the focus cap, the five `detached_helper` checks. Their pure
  functions are also *called* by the new doors (reach and roll call at claim), where they start as warnings.
- **Beefed up:** the thin-ticket line (from "sections missing" to the whole of group E, with a fix line each);
  the proof lint (from "the line parses" to F4 to F8: can fail, can pass on this tier, measurable where it says);
  the roll call (from "the names resolve" to C2, C4, C5: the defs are on the list, Full must be justified, here is the
  minimal list); reach (moved from Relentless-only to every door, and to CREATE).
- **Moved earlier:** the `late` rows whose "When" column in section 2 says so (reach, roll call, proof lint, binding)
  also run at filing and at claim, as warnings first. The others keep the trigger their row gives.
- **Left alone:** the three pre-cold-load preflights, `validate_patch.py`, the hooks. They answer other questions.
- **Not brought back:** hand-written manifests against fixtures.

## 7. Build tickets (proposed, not filed)

Ordered to **measure before enforcing**, then by tokens saved soonest. Each is small. **Every ticket's proof has the same
core: for each check it adds, one planted bad ticket the check must catch and one good ticket it must pass, in
`selftest_ticket_preflight.py`; for a refusing check, the proposed repair applied to the bad ticket makes it pass; and
the timing line of the run is in `runs.jsonl`.** The names of tickets 1 to 5 passed `rimflow namecheck` today.

| # | Name | What | Proof beyond the core | Saves |
|---|---|---|---|---|
| 1 | `RIMMANDRAKE_BUILD_PREFLIGHT_SPINE_TIMED_FROM_BIRTH` | One hand-run, report-only command: `rimflow preflight <ID>`. Reads only declared `file:`, `new:`, `def:` and `tier:` lines and the proof file's `live-mods:` / `live-tier:` lines. Checks B1, B4, B5, C1, C2, C10 with the two indexes that exist today (`git ls-files`, `defindex`). Returns PASS / FAIL / UNMEASURED observations, runs in the supervised child with the deadline, writes one timing line. **No door is touched.** | Six planted cases: a real path, a missing path, a planned (`new:`) path, a def on the list, a def off the list, a malformed line; plus a failed git call and a deadline expiry, both reading UNMEASURED. Whole-command time, cold and warm, printed and recorded | Nothing yet, by design. It answers the owner's main question by hand from day one, and gives the time metric from the first run |
| 2 | `RIMMANDRAKE_EXTEND_PREFLIGHT_CORE_KINDS_IDS_SHAS_FULL_REASON` | The rest of CORE on the same command: the reference record of 4.2 with its strict parse (E11), def kinds and races (B6), item ids (B10), shas (B11), the Full Mod reason (C4). `--sweep` over all open tickets | A sweep of the 782 open tickets finishes inside 5.2 and writes 782 lines; planted bad and good for each check; two contradicting lines are reported with both line numbers | Still nothing enforced. The Full Mod rule becomes visible on every ticket |
| 3 | `RIMMANDRAKE_BACKTEST_PREFLIGHT_OVER_REAL_PAST_TICKETS` | Section 8. The look back over past tickets, **and the shadow run**: filing prints the lines as a prompt (as the proof lint does today); claim, helper launch and Relentless pickup run it and record; thin wrappers record the answer and time of each existing gate. It stops nothing. The question is the increment: what would this catch that today's gates do not | The per-check table with audited counts; the joint false-block rate; breaking the preflight on purpose leaves every door working; the list of checks proposed for enforcement | Stops us building 95 checks on a guess, and stops a gate that starves tickets (the 2026-08 failure) |
| 4 | `RIMMANDRAKE_ENFORCE_PREFLIGHT_AT_CLAIM_DECLARED_FACTS_ONLY` | `cmd_claim`, `start` and `detached_helper.launch` refuse on the checks ticket 3 cleared; the refusal text of section 3; the override flag (new checks only); `queue` and `next` show the fix line; the first-refusal note; the verdict cache for those read-only views | A planted ticket with a def off its list is refused at claim with the proposed line, and accepted once it is pasted; an override is recorded; the flag is refused for an existing gate's id; a refused ticket is still listed and still editable | The first real saving: every hand-claimed and helper-launched ticket |
| 5 | `RIMMANDRAKE_BUILD_REFERENCE_INDEX_ONE_ANSWER_WHAT_EXISTS` | `ref_index.py` and the prose side of `ticket_refs.py`: the prepared index with its bounded overlay and its build command, C# symbols, texture and file stems, the rename map, prose patterns, the `(auto)` refs block printed at filing, B2, B3, B7 to B9, B12 to B15, B17, B18 | The prototype's counts are reproduced by the real code within 2% (2,352 paths, 231 missing; 198 names found nowhere); the overlay after a one-file commit is timed; an uncommitted rename is seen | Warnings on everything a ticket names, and tickets that declare themselves at no effort |
| 6 | Full Mod: candidate minimal list and list sanity | C5, C7, C11, C12; the weekly list of Full reasons | The candidate list for 10 real tickets closes offline, and for 2 of them loads in a real 22-second load | Minutes of load per live run; Full-list failures that were never about the ticket |
| 7 | Acceptance-test sanity | F1, F2, F5, F6, F8, F10, F13, E3, E5 (F3 and F7 exist and are only observed) | Planted bad and good for each; a build ticket that creates its own test script is **not** refused | The "unmeasured" class, the largest in the measured week |
| 8 | Duplicates and dependencies | A3, A4, G1 to G4, G7 | Of the 25 known duplicates, how many are flagged against their twin (reported, with the false flags on 100 non-duplicates) | Duplicate and already-done work (59 items measured, 17 worked first) |
| 9 | Environment, budget, the live-queue door | Groups D and H not yet in | Planted: low disk, missing tool, unset variable, spend over cap, a swap never restored | Environment loops |
| 10 | Timing report, drift alarm, the Agent-spawn cache read | `--timing`, the alarm, the hook | A planted slow check trips the alarm once, and only once | Keeps it fast for good |
| 11 | Relentless: chosen new checks from shadow to refusing | Only on the owner's separate word (question 2) | Per check, its audited row | The automated line |
| 12 | The CANDIDATE shelf | Only the checks whose class showed up as real waste in ticket 3 | As the core | Whatever the data says |

Tickets 1 to 3 change no behaviour at any door, so they are safe to build at once. Ticket 4 is the first that can
refuse, and it refuses only what ticket 3 has cleared. The read-only sweep of the open queue is part of ticket 2; the
worst-first list it prints is for a person to read, and no ticket is changed by it.

**The smallest version that answers the heart of the order** is tickets 1 to 4: declared paths and defs checked for
"real" and "on this list", a recorded reason for Full, the precise time of every run, shown at filing and enforced at
claim. Whether that is "most" of the saving is what ticket 3 measures; it is not known today.

## 8. Backtest plan

The question is the **increment**: had this run then, what would it have caught *that the gates we already have did
not*, and what would it have wrongly stopped?

**Looking back (corpus).**

1. *The 782 open tickets*, as they are today. Cheap; gives volume and timing.
2. *Tickets closed, dropped or superseded in the last 60 days*, each rebuilt **as it stood at first pickup** (the prose
   and proof file at the commit before the first `claim` or `start` event), not as first filed and not as finally fixed.
3. *The 238 items of the measured week* (2026-10-31..11-07) whose generations ended in a setup-class end, with the ticket
   text as of the generation's start. These carry tokens.
4. *The labelled lists from the ledger*: 25 duplicates, 34 already-done, 9 false premise, the 20 items with "not on the
   list" notes, the 39 with "no such" notes.

**Looking forward (shadow).** The same checks run at the real doors and only record. This is the part that cannot be
fooled by hindsight. Seven days is the least time it runs, not proof by itself: a check is judged when enough of its
would-be refusals have been read (below), however long that takes.

**The traps, stated up front.**

- *Today's world is not then's world.* The def dump, the installed mods, the standing rulings, the ledger state and the
  run history have all moved. The reference index can be rebuilt at any commit; the rest cannot. Every backtest answer
  is tagged by the input it used: "as it was" or "today's, stand-in". Only "as it was" answers count toward a rate. A
  ruling made after the ticket's pickup is not used against it.
- *A later pass does not prove an early refusal wrong.* If the ticket passed only after someone repaired the very thing
  the check named, the refusal was right. So each sampled refusal is judged at the moment of pickup: was the named fact
  true then, and was the proposed repair the one later made?
- *The quiet losers.* Tickets dropped or left to rot after a block do not appear among "passed". They are counted in
  their own row.
- *Counting a saving twice.* A wasted generation is credited to one check: the earliest that would have fired.
- *Tokens saved is not the generation's spend.* The saving is the spend **after** the first moment the check could have
  spoken, where the store's attempt order lets us tell, and otherwise it is reported as an upper bound and called one.
- *Already caught.* An item that today's reach, roll call or proof lint gate would also have stopped is credited to that
  gate, not to the preflight.

**Measures.**

| Measure | How | Bar |
|---|---|---|
| Fires, per check | count over each corpus and over the shadow week | reported |
| Incremental catch | corpus 3 and 4 and shadow: the check fired, the class matches how the item actually ended, and no existing gate fires | reported in items and in tokens (bounded as above) |
| **False refusal, per check** | every would-be refusal of the check is read by a person and judged **as of pickup**: was the named fact true then? (The proposed repair need not match the repair later made; more than one can be right.) Reported as: audited n, false k, and the interval that goes with them | to be allowed to refuse: **at least 30 audited and at most 1 false**. With fewer than 30 it stays a WARN and keeps collecting. Honest reading: 0 false in 30 still allows a true rate near 10%, so the override count keeps watching after it goes live |
| **Joint false block** | the share of worked tickets wrongly stopped by **any** check | **under 5%**, with its interval stated; if over, the worst checks are demoted until it is not |
| Unworked tickets | would-be refusals of tickets nobody later worked | reported in their own row, not in any rate |
| False alarm (warnings) | hand label 50 warnings | under 10%, or the pattern stays silent |
| Repair quality | 50 proposed repairs read by a person: would this repair have been a right one? | at least 45 of 50, or the check proposes nothing and so may not refuse |
| Time | whole command, p50, p95, max per door, cold and warm | inside section 5.2 |

**Proving the instrument can see.** Before any "0 caught" is believed: plant 10 known-bad tickets in the corpus (one per
group) and confirm each is caught. A zero from a backtest that cannot see is the most likely bug.

**Output.** One table in the ticket's evidence folder and one paragraph for the owner: "over N past tickets and seven
days at the doors it would have stopped X before any token that nothing else stopped, worth at most Y tokens, and
wrongly stopped Z."

## 9. Questions for the owner (six)

**Q1. When a declared fact is wrong, what happens at filing and at pickup?**
Context: on 2026-08-21 you removed the completeness gate ("a missing field is not a rejection") after thin tickets
starved. Your new order names both moments. "Declared" means a machine field or a line someone confirmed; never a guess.
- (a) Filing warns and prints the proposed repair; pickup stops. **Recommended.**
- (b) Both stop.
- (c) Both only warn.
The trade: (a) never stops an idea being written down, and still stops tokens. (b) catches it a step earlier but makes
filing a fight when the dump is stale. (c) is close to what we have, and warnings get skipped.

**Q2. Relentless, during the freeze: collect reports now, or wait?**
Context: the 2026-11-06 card says no new rule or judging machinery in Relentless until the 3-day check. Your order names
pickup.
- (a) Collect now: it runs there, records and times, and refuses nothing new. Any new refusal in Relentless needs your
  separate word after you have seen the numbers. **Recommended.**
- (b) Allow new refusals there now, counted as fixes for measured failures.
- (c) Keep it out of Relentless entirely until the freeze ends.
The trade: (a) keeps the freeze honest and still gets the evidence. (b) saves tokens sooner but is a new gate by any name.

**Q3. Declared references: optional, required, or machine fields only?**
The tool proposes the lines at filing; a proposed line only warns until someone confirms that line.
- (a) Optional. **Recommended.**
- (b) Required for build, fix and live tickets (a ticket with none is stopped at pickup).
- (c) No declared block at all; only the machine fields we have today can stop a ticket.
The trade: only declared facts can stop a ticket. (a) costs nothing and tells us, by the coverage number, how many
tickets declare; (b) gets them all, at the price of one more required thing, which is the kind of gate you removed in
August; (c) means a wrong def or path in the prose can never stop anything.

**Q4. A Full Mod test with no reason on record: stop it, or warn?**
- (a) Stopped at pickup, with a candidate minimal list printed to paste. **Recommended.**
- (b) Warned, and it runs on Full.
The trade: (a) costs one line and makes Full a choice somebody made. (b) keeps the 25-minute load as the easy path.
Also: are the five reasons in 2.1 (interaction, load-order, performance, owner-save, explicit) the right list?
Python can record a reason; it cannot tell a good one from a pasted one. You would see the reasons weekly.

**Q5. Who may bypass a new refusal?**
- (a) Any worker, naming the check and a reason, recorded. **Recommended.**
- (b) Only the Conductor.
- (c) Nobody but you.
The trade: (a) cannot starve a ticket, and the count of bypasses shows which checks to look at. (b) and (c) are stricter
and will queue tickets behind a person. In every case the gates that exist today keep their own rules, and the standing
rulings (no worldgen, no flyer flight test, no writing the mirror) need your word.

**Q6. When the preflight cannot look (an index is missing or stale, or it ran out of time): go ahead, or prepare first?**
- (a) Go ahead with a visible "not checked" line and the command that would make it checkable. **Recommended.**
- (b) For live tickets only, stop and prepare first (a fresh dump, a built index), because a live run is the dear one.
- (c) Always prepare first.
The trade: (a) means our own instrument can never block work, at the price of some tickets going in unchecked; the
coverage number says how many. (c) is the safest per ticket and is how a check becomes an hour's wait.

## 10. What the GPT rounds changed, and what I rejected

Three rounds through `gpt_consult.py`; the answers are `gpt_r1_expansion.md`, `gpt_r2_teardown.md` and
`gpt_r3_improvement.md` in the evidence folder.

**Round 1, expansion. Taken:** seven checks (mod order C11, incompatibility and game version C12, patch xpaths B18,
strict parse E11, a swap in flight D13, a failure that cannot reach the judge F13, one ticket all the way down I7), and
four widenings (a sha must have landed, a save fixture's mod list, run time against the limits, `explicit:` must name a
real event). Also the `(auto)` mark: a line the tool wrote is still a guess. **Put off** (2.2): Harmony signatures, def
reference graphs, conditional loading, translations, typed criteria, token counts, budget reservations: each needs a
data source we do not have, or has no measured waste behind it. **Rejected:** checking that evidence is fresh and from
this build (that is the closing gate's work, not a pre-work check); atomic admission with reservations (new machinery,
and frozen ground).

**Round 2, teardown. Taken, and it changed the design most:**
- Existing gates keep their own code and authority; the preflight observes them. (I had them "called through".)
- A bypass opens only new checks.
- The 228M is an upper bound on a class, not a saving; the increment over today's gates is unmeasured. So the build now
  measures first: shadow and backtest before any refusal, and a three-shelf catalogue in place of 95 checks at once.
- A def "on the list" means its owning mod is on the list, no more; a computed list is a candidate.
- Refusals that would stop the work that fixes them: the `new:` rule (2.1b); E5, F6 and F10 demoted to warnings.
- Cache keys with an overlay for uncommitted files; the time file on the Linux side; every attempt recorded, since a
  refused claim writes no claim event.
- The backtest's traps: hindsight in every input, a later pass that does not prove an early refusal wrong, the joint
  false-block rate.
- "Reason recorded", never "justified", for Full Mod.
**Rejected:** cutting F4 (the brief asks for "can fail"), B17 (stale names are a measured class: two open tickets cite
a tool path that does not exist) and A3/A4 (25 duplicates measured, 22 in the last 30 days). They stay, as warnings, and
most of the others it named went to the CANDIDATE shelf, not out. Also rejected: splitting into per-door modules. The
owner asked for the versions we have to be beefed up and shared; lazy imports and a policy table per door bound the risk.
And invalidating a confirmed line whenever the prose around it is edited: the lines are re-checked against the live
indexes at every door, which is the cheaper cure for rot.

**Round 3, improvement. Taken:** one plain observation per check (PASS / FAIL / UNMEASURED) with the door's policy
applied afterwards; one record shape for every reference; one child process with one deadline for everything new, and
no index ever built at a door; the repair engine put off (the tool proposes, it does not edit); enforcement judged on
audited counts per check; seven contradictions between sections and seven claims larger than their evidence, fixed;
question 6 changed from "sweep now or later" (a delivery, not a policy) to "what when the preflight cannot look".
**Partly rejected:** its cut of ticket 1 down to paths only. "Is this def on this mod list" is the owner's main ask and
the index for it exists, so it stays in ticket 1; kinds, ids, shas and the Full reason moved to ticket 2 as it advised.
