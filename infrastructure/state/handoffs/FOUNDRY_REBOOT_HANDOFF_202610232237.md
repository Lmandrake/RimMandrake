# FOUNDRY_REBOOT_HANDOFF_202610232237 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202610231441`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Helper cost is messages x ~500k context, not output: a long Opus helper re-reads hundreds of millions of cached tokens, and the pipeline's own `claude -p` judge calls (90 runs today, 64 of them one prompt comparison) are unmeasured and probably bigger. Rules and numbers: `skills/rimworld-art-evaluation/references/subagent_budget.md`. BENCH's `rm-*` bounded agent definitions load at session start; this session predates them and the hook refuses unbounded spawns, so spawn nothing until a restarted session has them.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
The Opus session limit resets 1:10pm PT; the owner is upset about the burn. Offer him at most one 'here's what the model saw' single image after the flora/fauna runs resume (drafts: `Transient/phone_art_candidates_2026-10-23.md` if the prompt helper wrote it). Kept Pyrelands art (EmberGrass A, Quickgrass A, Quickgrass _b) was held against the pipeline's regen verdict: his call whether to apply it literally.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `HELPER_BUDGET_GATE_ENFORCE_NOT_ASKING_NICELY` — filed, nothing built; NEXT: build one launcher for helpers and claude -p judges that reserves allowance from a shared ledger and refuses at zero.
- FLORA art audit (Pyrelands/Cauldron/Contagion/LeaningScrub) — 74 of 189 pictures judged, 7 Pyrelands regen jobs queued, nothing installed, no digests; NEXT: after 1:10pm PT with a bounded rm-* helper, re-run the interrupted flora runs (commands in this session's flora report, drivers in /home/mandrake/.seat-tmp/FOUNDRY/s/), file regens, then write Transient/art_flora_<biome>_2026-10-23.md.
- FAUNA art audit — interrupted by the limit, partial runs and a regen-rounds merge patch in place; NEXT: restart it as one bounded helper per biome and check `rimflow` art items before re-judging (verdicts are cached per subject).
- `race.py` (art_eval prompt race, committed fbea2ea05) — prompts V1cal adopted (agreement 27->36, false accepts 0->0, only 24 not-accept rows) and code marked DIRTY; NEXT: full-file read of src/RimMandrake/Utils/art_eval/race.py then code_review_status.py mark-clean.
- ART PROMPT ROUND 2 — owed (GPT second look anchors on the concern it is handed; 15 false rejects remain); NEXT: one round, incumbent plus two variants, at most 12 rows, only after the budget launcher exists.
- ASHPULSE_READERS_PRUNE_NOBODY_LEFT, FLUFF_ASKS_DECIDE_EIGHT_UNDER_VETO, biome live rows, ModsConfig restore (modlist_swap) — carried from FOUNDRY_REBOOT_HANDOFF_202610231441; NEXT: reread that handoff's pointers at wake.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A first helper_cost.py double-counted streamed transcript records (~2x); dedupe by message id (filed: lessons)
- `rimflow file` refuses names over 44 chars / 7 words; use `rimflow namecheck` first (see: ticket_naming_2026-10-10.md)
- A session begun before the rm-* agent commit cannot spawn at all (hook refuses unbounded agents) (see: skills/efficient-subagents/SKILL.md)

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (4) — the next seat's queue

- `ARTEVAL_STRICTNESS_TUNE_KEEPS_REDRAWN` — art_eval incumbent prompts reject 24 of 27 owner-kept pictures (race r1: 51 owner-ruled rows, 0 false accepts, 24 false rejects); Opus never reaches G
- `ARTEVAL_CANON_CARD_FIX_LLAMA_SLIPPED` — art_eval cards carried no canon Must show unless the spec supplied it: RSW_Gualaar A (owner REDO, canon NEGATIVE 'not a slim llama, not two thin backw
- `ARTEVAL_DEPARTURES_TUNE_ALMOST_EVERYTHING` — departures brief invents specifics; first pass 61 of 65 live fauna REGEN
- `HELPER_BUDGET_GATE_ENFORCE_NOT_ASKING_NICELY` — One launcher for helpers and claude -p judges enforcing budgets from a shared ledger

## Commits

```
fbea2ea05 Art-eval prompts V1cal adopted (agree 27->36, false accepts 0->0, holdout 6->9); race.py replay-gpt
cdd8e7ed9 block_unbounded_agent: drop the pre-definition session exemption; definitions hot-load
bd20f1511 Transient: pin wave brief
71a01490e efficient-subagents: context-burn section, rm-* rules, fix stale haiku line
258d8c17f Bounded subagents: rm-* agent definitions (compact at 150k), unbounded-spawn hook, token_census.py 2026-10-23 census: 2.18B tokens, 89% helpers re-reading 300k-966k contexts on a 1M window that never compacted. Definitions load at session start; sessions begun before this commit are let through until restart.
0923d07e4 File HELPER_BUDGET_GATE_ENFORCE_NOT_ASKING_NICELY; name it in the budget reference
c00023f5e Budget rules: GPT-review fixes (default 30 turns, call counts, cache key); helper_cost dedupes streamed records
263752ec4 Subagent token budgets for art review and live proof (owner 2026-10-23)
16a91a2fa lesson: token census 2026-10-23 — long Opus helpers re-reading huge contexts
d58f5c8fb Rebuild RimMandrakeFlowWorks.dll from committed source at landing
ea2495985 SLACK_LOOP_REDRAW_STANDS_UP_IN_PROFILE: raised ropes lie as flat ground coils in every rotation
9e575a950 Fauna art-eval: non-kept installs carry the mechanical script reason the push guard requires
ad7ba08a5 Fauna art-eval: first 3 regens installed (Ullai, Emberscythe, Barbslinger; kept art replaced per owner card 2026-10-23), compare/digest/install gates, runner rounds lock
5c182a4e7 Flora art-eval, first passes: Pyrelands judged; Cauldron/Contagion/LeaningScrub partial (Opus session limit until 13:10)
88a791e0f Fauna art-eval: first pass over Pyrelands/LeaningScrub/Cauldron/Contagion (65 judged), spec+drive tools
f51549835 art_eval: prompt-variant race harness (race.py, ART_EVAL_REFS), canon auto-fill for RSW_ cards, round-1 race data
2f141d772 Ledger: note on LADDER_EW_FIX_LEANS_THE_WRONG_WAY
024edbd50 LADDER gen_a8.py: reproduce committed E/W art (translate +-174px)
37391a7bc Transient: pin 1 path(s)
e0a902f05 Ledger: TANKS_ROW_FIX_LEVELS_WHAT_RULING_FORBADE built at 8c4ff4f1c36f; live re-run of TANKS_JOINED_STORE_HOLD owed
... 67 more: git log --oneline 4fb88fb7d..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     BENCH bridge run 1 resume (no-blocking day, full FlowWorks live test)

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M deployed/config/ModsConfig.before-tier-flowworks.xml   BENCH
 M infrastructure/state/ledger/events/OWNER.jsonl   OWNER
?? deployed/config/ModsConfig.swap-active.json   BENCH
?? infrastructure/state/art_eval/regen_rounds.json.lock   FOUNDRY (stale lock from the flora helper, ignore)
?? src/RimMandrake/FlowWorks/northstar/live_session_result_20261023T044826.json   BENCH
```

