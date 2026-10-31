# Haiku product census, 2026-10-31

Item: HAIKU_CENSUS_VERIFY_BY_TRANSCRIPT. Owner: "use as many subagents as you need to verify any product Haiku generated that we still depend on. Any code or design document that Haiku emitted is suspect until proven by a higher model."

Bottom line: from 2026-09-30 on, Haiku wrote no repo code and no repo doc (MEASURED: 96 turns, 0 Write/Edit calls). One product touches the trial, and a Sonnet check already corrected it. The real exposure is the 45% of history before transcripts begin (UNMEASURED), where four repo products name Haiku in their own text.

## 1. Instrument

Streaming parser over every transcript jsonl, one tally per file of `message.model`, plus every Agent/Task dispatch and every tool call by a Haiku turn. Git trailers were not the instrument.

| Measure | Value | Status |
|---|---|---|
| Files, volume, lines | 7,578 jsonl, 13.9 GB, 2.18M lines, 0 parse errors | MEASURED |
| Assistant turns | opus-5-5 406,907; sonnet-5-5 144,153; opus-4-8 411; opus-5 20; haiku-5-5 96 (`<synthetic>` 234 are not real turns) | MEASURED |
| Files with a Haiku turn | 22 | MEASURED |
| Sanity probe | Independent grep gives 37 files. All 15 extra are explained: 5 parent sessions that passed `model:"haiku"`, 10 temp files holding only `<synthetic>`. Parser-only hits: 0 | MEASURED |
| Scratch-home meter runs, `~/.seat-tmp` | About 5 unique runs, about 13 further turns (grep count, not parser) | MEASURED, approximate |
| Agent dispatches | 4,882: opus 2633, sonnet 2205, none 37, haiku 7. First haiku dispatch 2026-10-23 | MEASURED |
| Tools used by Haiku turns | 0 Write, 0 Edit. Files written through Bash: scratch census.py and census.out, scratch hits, and `arm_audit.md` by heredoc | MEASURED |
| Other stores | Windows store 79 files back to 08-10: 0 Haiku. Arena dir 55 jsonl: 0. SteveDesktop WSL 10 jsonl: 0. SteveDesktop Windows: 0 jsonl | MEASURED |

## 2. Blind spots

- **History before 2026-09-30.** WSL transcripts begin 09-30. 10,473 of 23,364 commits (45%) are older than that; the Windows store holds only 13 of those sessions, and the September cloud sessions (Claude-Session trailers) are not retained here. No Haiku count exists for this era: UNMEASURED. Section 5 lists what repo text reveals, which is a floor.
- **Gateway remap.** Before about 10-20, `model: haiku` resolved to a Sonnet on the gateway (commits ae19eda0ab, 9bb8664372; `skills/agent-fanout-research/SKILL.md:70`). A "haiku sweep" from that time may have run on Sonnet. Treated as suspect regardless.
- **No-transcript routes.** `claude -p --no-session-persistence` (judge, critic tester, mutants, reader_pass) leaves no transcript. Code defaults are Opus and the judge refuses anything else, but `ARENA_CRITIC_MODEL` and the arm `*_MODEL_CMD` are environment settings, so the value a given run actually used is not proven by this census: see batch T2.
- **Background small-fast model.** Session titles and the WebFetch summariser are invisible in transcripts. WebFetch: 249 calls, 243 returned, all retained-era, summarised by an unrecorded model. Any fact taken from a WebFetch summary may be Haiku-condensed: UNMEASURED.
- **Mac laptop (MACBENCH).** No ssh host: UNMEASURED.
- **Other projects on this machine.** `.claude.json` shows small `lastModelUsage` Haiku entries for other repos (`/mnt/g/My Drive/Personal/Rimworld` 54,927 in / 1,738 out, Hestia, Nemotron, NewHarness). Last session only, outside this repo.
- **Provenance gap.** Ledger close SHAs cb0f7506, af539d5a, 34cc5907 predate a history rewrite and do not resolve.

## 3. Routes

No live `--model haiku` in `src/`. `role_launch.py:170` maps the alias only. `arena_judge` refuses a non-Opus model. `critic_mutants`, `reader_pass` and art default to Opus or GPT. `rm-search` moved from haiku to sonnet at 9245af7dbe today. `owner_tags.py` (the Haiku tagger) is designed but not built. `~/dev/DispatchOpenCode/bin/delegate` is absent here: UNMEASURED. `/home/mandrake/rm/dispatch` is a repo clone with the same design hits, no separate route.

Text still contradicting today's ruling is filed as HAIKU_LEFTOVERS_FIX_STALE_RUNGS.

Ladder history: nobody passed `model:haiku` as of 08-24 (hook docstring); ladder added 09-29 (b1cced6e56); struck 10-01 (063612964a); restored 10-20 (b869b11ba4); `rm-search` on haiku 10-23 to 10-31.

## 4. Still depended on, ranked

### Rank 1: feeds the arena trial

| # | Product | Current state | Risk |
|---|---|---|---|
| T1 | `arm_audit.md` by agent a0d25bd21b4747a5d (10-31 14:47): `D:\ClaudeWork\rimmandrake\arena\freeze_prep\arm_audit.md`, 13 must-change of 40 lines for dropping v3c | Sonnet re-check `arm_audit_verified.md` (14:51-14:55): about 27 confirmed, 6 wrong, up to 5 missed; corrected list sent to the freeze builder, who had held the Haiku path since about 14:48. Freeze 15:02, pool_sha256 6d0ef9951f22411ebdd31dd0d649945ac176dfccf5d5d6608826f14f74ab2319, 29 tasks | The freeze may carry a Haiku error or miss one of the 5. Opus should read the v3c-drop freeze diff against the verified list |
| T2 | Meter proof runs on Haiku (10-30 to 10-31): arena-probe-arm-meter, arena-probe-tester-meter, ed3f25f3 run1-3, mh1, mh3, rv_mid, rv_every. Back ARENA_METER_BUILD_SPEND_BY_CLONE_PATH, ARENA_TESTER_SPEND_ENFORCE_METERED_HOME, ARENA_TESTER_SPEND_ENFORCE_SELF_ERASED_LOGS, ARENA_MIRROR_FAILURE_ENFORCE_SILENT_LOSS. Evidence: `D:\ClaudeWork\rimmandrake\arena\verify_spend\run{1,2,3}_cli.json`, `verify_mirror\real_{mid,every}_cli.json` | Numbers come from API usage, not Haiku judgment. Haiku was the load, not the author | Run2 Haiku refused the `rm` and ran `ls`, so check who deleted in the "real mid-session rm". One Sonnet meter probe replaces the Haiku load. Also confirm the actual `ARENA_CRITIC_MODEL` and judge `modelUsage` in the 19 records that carry it |

Not a product: the "claude-haiku" string in `foundry_vet/before.json`, `judge/hidden/RP_DELEGATED_DIGEST_FIX_NEVER_WRITTEN.json`, `repair_b4/{par,ser}.json` and `verify_final/census_pool.json` is the test fixture `model="claude-haiku-x"` quoted inside task text. MEASURED on all five. No judge or task record names a Haiku `modelUsage`. Vet labels: no Haiku turn in the retained era.

### Rank 2: shipped code and data

| # | Product | Current state | Risk |
|---|---|---|---|
| S1 | DROID_ASIMOV_SAVE_SCRUB_1 D0: frozen-save edit, 0c6f993ef9 (09-06, trailer Fable 5.1, item tasked to haiku): 82 + 133 need entries removed from the worldmap and gravship saves | Done. Actual model unknown (blind era) | Shipped data. Recount against the saves and the backups |
| S2 | No shipped code by a Haiku transcript in the retained era | MEASURED, 0 Write/Edit | None retained-era. Earlier: UNMEASURED |

### Rank 3: rules and tools every seat uses

| # | Product | Current state | Risk |
|---|---|---|---|
| R1 | Token floor ROLE_CAPS_TUNE_ABOVE_RUN_FLOOR: OK runs 0c641caf, 70444eb5 as measurements; `selftest_role_tokens` W4, `selftest_dispatcher` proof records | Mechanical | A Haiku floor can differ from a Sonnet or Opus one. Confirm the cap is not sized on Haiku alone |
| R2 | Lesson 20261028T041510Z: `claude -p --json-schema` takes schema text, from arbiter_schema Haiku probes | Mechanical CLI fact | Reproduce once |

### Rank 4: design documents

| # | Product | Current state | Risk |
|---|---|---|---|
| D1 | `design/Jawa/droids/D1_donor_reference_grep.md` (09-06, "haiku, treat as evidence") | Spot-checked and a citation corrected, 6d7fac3b9f (Sonnet trailer); only a spot check. 15 Depot-gated refs | Full re-grep of donor references |
| D2 | `design/Jawa/droids/A3_frozen_save_droid_census.md` | VOIDED (DROID_PROGRAM_STATE:185) yet on main; item DROID_FACTIONS_IN_FROZEN_SAVE_1 redid it at a05be1b472 | Delete under HAIKU_LEFTOVERS_FIX_STALE_RUNGS after a check of inbound references |
| D3 | OWNER_SAID_PROVENANCE_GUARD_1 design consequence, from a Haiku env print (09-19) | Environment identity only | Low; re-run the print under a current model |

### Rank 5: the rest

| # | Product | Current state | Risk |
|---|---|---|---|
| O1 | Agent a2c190654d2806a00 (10-24): `artpipe/failed` census, 1022 = 506 requests + 514 manifests + 2 stale. Led to RIMPULSE_FAILED_FIX_COUNTS_MANIFESTS_TOO | Parent checked the sum | Recount if the item is still live |
| O2 | Agent aaedd6a1a2351c401 (10-24): "Nine light patterns" search, surfaced AtmosphericBase, leading to ATMOSPHERIC_BASE_BUILD_PROGRAM_1 | Positive confirmed by the parent in the design doc. Its negative, "exact feature not in dirs", was never checked | Re-run the negative |
| O3 | Flora artpipe audit, 9c9538bf00 (09-20, the only Haiku 4.5 trailer in 23,364 commits): `Transient/flora_improve_artpipe_audit_20260920.md`, 148 rows, 141 "genuinely owed" | File gone from the tree, no item filed. Same session has 755 commits, 1 of them Haiku | Check whether the 141 fed any flora queue item |
| O4 | UNUSED_MUTATORS_WORLD_ASSIGNMENT_1 (open): instructs a "haiku-tier" census, not yet run | Instruction, not product | In the stale list; run on a higher model |

## 5. No longer depended on

| Product | Reason |
|---|---|
| Agent ae833d742344ca8cd (10-24) git and disk health report | Transient report, acted on then gone |
| DEAD_PYTHON_CANDIDATES_VERIFY_1 sweep (09-05) | FOUNDRY verified each of 23 scripts, 2 deleted |
| DROID_FACTIONS_IN_FROZEN_SAVE_1 | Replaced the A3 result; a05be1b472 carries a Sonnet trailer |
| Probes zz-probe a/b/c, rm-fixer base probe, ae3db smoke, wake_proof x2, a7a46 placeholder | No product |
| Dispatches "Hook test general-purpose" (f5cc5e85, 10-23) and "Definition test rm-search" | No Haiku transcript; probes by name |
| `narrative_dictionary_pilot/blind_answers_2026-10-03.md` | Its header says Sonnet; plan text mentioned Haiku only |
| `fauna_review_deck.html`, `creature_art_review.html`, `creature_size_review.html` | Deck hit is "haiku" inside base64; the two creature pages no longer exist in the tree |
| MODEL_TIER_ROUTING_1, DETERMINISM_ASSESSMENT:237, ladder docs | Routing text, not product; in the stale list |

## 6. Verification batches

| Batch | Items | Verifier | Size |
|---|---|---|---|
| A | T1 | Opus, read-only, against `arm_audit_verified.md` | One diff |
| B | T2 | Opus or Sonnet with a Sonnet meter probe, FOUNDRY clone | 4 items, 1 probe |
| C | S1, D1 | Opus, with save tooling (skill rimworld-savegame) | 2 recounts |
| D | R1, R2, D3 | Sonnet | 3 probes |
| E | O1, O2, O3 | Sonnet | 3 checks |
| F | HAIKU_LEFTOVERS_FIX_STALE_RUNGS with D2 | BENCH Sonnet | Text purge plus 1 deletion |
