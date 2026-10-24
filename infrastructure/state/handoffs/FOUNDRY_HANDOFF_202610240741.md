# FOUNDRY_HANDOFF_202610240741 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610230517`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

AtmosphericBase is fully built offline and reviewed CLEAN through the Nine's defs (T3), but the ONLY live measurement so far (one run, T2 build, 50 rows: 38 PASS, 1 FAIL, 11 UNMEASURED) found Evaluate costs ~1 ms at 17-19 lamps against a provisional 0.1 ms bar, so the planned update-on-change engine (proposal B) is the next real work, not more patterns. The Nine never show in game by design until `SetScenarioDecides` is wired from a Utinni scenario (consumers wait on NINEFOLD_LOUDNESS_FRONT_1). All 15 owner decisions: design/RimMandrake/atmospheric_base_review_package_2026-10-24.md §9. (filed: lessons)

## What the owner should see

- RimPulse: step 1 is live (red only for a dead un-replaced seat; test-colony/low-memory alarms only in his own play session; 'a look is an artifact he opens'); his widget has been screenshotted once by a helper (D:\ClaudeWork\rimmandrake\pulse_shot.png) but he has not been asked if it reads better. Redesign package + GPT review: design/RimMandrake/rimpulse_redesign_2026-10-23.md. His six cards were answered; GPT's two unasked questions (how much a review packet carries; how much of the delegated-decision audit he reads) remain.
- BENCH's game was restarted for the live run: the game is up on BENCH's 14-mod list with save BENCH_bridgerun1_backup_20261023T2345 loaded (tick 14465, paused). The bridge is FREE; `./bridge` is owner-only so I could not hand it to BENCH.
- GPT biome art review (6 biomes: Pyrelands, Cauldron, Contagion, The Rot, LongShade, LeaningScrub): digest Transient/gpt_biome_art_review_2026-10-24.md. GPT wants redo/cut on 76 rows he has KEPT (flagged, not acted on) and wants RSW_Kybuck two-legged against his approved four-legged form (flagged). The helper removed nothing from the art ledger (purge needs his words); it only left 44 exact-duplicate columns off GPT's pages.
- The flora audit is done (189 pictures: 72 ACCEPT, 117 REGEN, 35 REGEN held because owner-kept); fauna round 1 done for Cauldron, Contagion, LeaningScrub, Pyrelands (TruffleMole renders failed: oversized 1536x1024 vs 256x256).

## What is half-done, and where it stops

- `ATMOSPHERIC_BASE_BUILD_PROGRAM_1` — Phases 1-4 + batch-1 + neutral set + the Nine built and CLEAN; one live run done, MOD cost finding filed; NEXT: build the update-on-change engine (proposal B) under ATMOSBASE_COST_FIX_TEN_TIMES_THE_BAR, then re-measure live.
- `ATMOSBASE_PROOF_FIX_UNLIT_LEAVES_DARK_LAMP` — filed; NEXT: restore lamp power in the ProofSample 'unlit' undo and make R2 compare lit state.
- AtmosphericBase live checks owed (one bridge sitting): `taken_after_load` stale-claim question, hook scenarios L12/L13/N1 unbuilt; NEXT: build them, then run proof_atmosphere.py --with-reload on the minimal list (modlist_swap.py swaps and restores).
- `RIMPULSE_FAILED_FIX_COUNTS_MANIFESTS_TOO` — filed; NEXT: count request files only and only failures newer than his last read in pulse_core.py.
- `RIMPULSE_DIGEST_REBUILD_THREE_QUESTIONS` and `RIMPULSE_BRIEF_BUILD_MORNING_PAPER_PHONE` — proposed; NEXT: build the phone brief after DELEGATED_DIGEST_FIX_NEVER_WRITTEN (the daily digest of agent decisions has never been written; 295+ decision files exist).
- Fauna art audit — round-2 jobs filed (Cauldron 27, Contagion 39, LeaningScrub 51), TruffleMole round 1 unjudged; NEXT: judge round-2 renders when they land, and find why the TruffleMole job asked 256x256 and got 1536x1024.
- `HELPER_BUDGET_GATE_ENFORCE_NOT_ASKING_NICELY` — filed, nothing built; NEXT: one launcher for helpers and claude -p judges that reserves allowance from a shared ledger.
- GPT biome review follow-up — digest written; NEXT: decide per biome which description rewrites to apply (proposals only so far) and review Eopie/LongtailGorg/Worrt placeholder art against GIZKA_SHEET_FIX_ALTERNATE_SHOWN_AS_RENDER.
- Carried from FOUNDRY_REBOOT_HANDOFF_202610232237 / 202610231441: `ASHPULSE_READERS_PRUNE_NOBODY_LEFT`, `FLUFF_ASKS_DECIDE_EIGHT_UNDER_VETO`, biome live rows, ModsConfig restore; NEXT: reread that handoff's pointers at wake.

## Traps learned

- `./publish` refuses (and rebases fail) while another helper has a tracked file mid-edit; commit your own paths only and retry after that helper finishes (filed: lessons).
- A builder's own review is not review: three of four helper reviews found real bugs the builder shipped; a review that does not finish leaves files DIRTY on purpose (see: infrastructure/state/lessons/*abp*).
- `rimflow bridge give` and `./bridge` are owner-only; a forced take records the owner as holder (see: using-rimflow).
- The pulse 'jobs in failed/' count was 1020 files = 506 requests + 514 manifests over 25 days, not 1020 failures (filed: RIMPULSE_FAILED_FIX_COUNTS_MANIFESTS_TOO).
- A helper that reads a hook-injected 'handoff' prompt skips it; only the head seat writes the handoff. (filed: lessons)

## Commits

```
b0f0c8285c GPT biome review sheets: decisions stubs (no owner decisions)
dca2c62bd9 Ledger+art: FOUNDRY shards from the GPT six-biome art review (census backfill events, Gizka-item note on stale placeholder LIVE rows)
0570e772a6 Rebuild RimMandrakeFlowWorks.dll from committed source at landing
798791a076 FlowWorks hose: Gauss-Newton clothoid solver, G2 fit on by default
de00efac1a art review sheet decisions file (empty)
ceecca3816 FlowWorks+GSS GPT art review, verified: 9 items, pinned report
1d84c15b92 code_review: proof_atmosphere clean mark
eae73304d0 proof_atmosphere review: live run produces the kernel selftest log (P0), R1 re-picks its fixture, L10 hook faults read HARNESS not MOD, controls for L6a/L6c/L12 and R1 lost/never-back, D12b floor regexes
16b526b2e3 Ledger: owner shard events (bridge release)
86f77860d3 Ledger: FOUNDRY shard (live-run notes, ATMOSBASE cost and proof items)
78d59a1a1a code_review: AtmosphericBase fresh-eyes review, 13 files marked clean (no defects; scenarioDecides is staging)
7c5e0842b5 lessons: git commit -- path takes the worktree; bridge load_game returns before the map
fc1d31109c proof_atmosphere R1: wait for the fixture to reappear after reload before judging the claim
658e49d678 AtmosphericBase T3 review: Gentle floor on god tremor and scar display; wiring pins updated
2ff86836f3 lesson: judges missed wall-fixture facings running along the wall
314648dad6 ledger: portable ladder E/W facing broken (owner)
64279656bb ledger: owner E/W ladder perspective note
78b733f9d0 ledger: owner likes the north-wall ladder zooms
cde95f1c5f ledger: owner cards on pit ladders (steel+wood versions; send redraw back)
2363ad453b Ledger: owner shard events (bridge take, game up stamp, card decisions)
... 732 more: git log --oneline ef79f9321d..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M conversations/2026-10-23-0519-6e26ec97.md   (Transient/untracked: generated by earlier sessions, not mine)
 M deployed/config/ModsConfig.before-tier-flowworks.xml   (Transient/untracked: generated by earlier sessions, not mine)
?? Transient/fw_scenes/live/S1_20261017T084726.txt   (Transient/untracked: generated by earlier sessions, not mine)
?? Transient/fw_scenes/live/S1_20261017T084802.txt   (Transient/untracked: generated by earlier sessions, not mine)
?? Transient/fw_scenes/live/S1_20261017T092155.txt   (Transient/untracked: generated by earlier sessions, not mine)
?? Transient/fw_scenes/live/S1_20261017T110253.txt   (Transient/untracked: generated by earlier sessions, not mine)
?? Transient/fw_scenes/live/S1_p00.png   (Transient/untracked: generated by earlier sessions, not mine)
?? Transient/fw_scenes/live/S1_p03.png   (Transient/untracked: generated by earlier sessions, not mine)
?? Transient/fw_scenes/live/S1_p10.png   (Transient/untracked: generated by earlier sessions, not mine)
?? Transient/fw_scenes/live/S1_p14.png   (Transient/untracked: generated by earlier sessions, not mine)
?? Transient/fw_scenes/live/S2_20261017T084824.txt   (Transient/untracked: generated by earlier sessions, not mine)
?? Transient/fw_scenes/live/S2_20261017T092355.txt   (Transient/untracked: generated by earlier sessions, not mine)
?? Transient/fw_scenes/live/S2_20261017T110404.txt   (Transient/untracked: generated by earlier sessions, not mine)
?? Transient/fw_scenes/live/S2_p00.png   (Transient/untracked: generated by earlier sessions, not mine)
?? Transient/fw_scenes/live/S2_p10.png   (Transient/untracked: generated by earlier sessions, not mine)
?? Transient/fw_scenes/live/S2_p30.png   (Transient/untracked: generated by earlier sessions, not mine)
?? Transient/fw_scenes/live/S2_p60.png   (Transient/untracked: generated by earlier sessions, not mine)
?? Transient/fw_scenes/live/S3A_p20.png   (Transient/untracked: generated by earlier sessions, not mine)
?? Transient/fw_scenes/live/S3B_p06.png   (Transient/untracked: generated by earlier sessions, not mine)
?? Transient/fw_scenes/live/S3B_p16.png   (Transient/untracked: generated by earlier sessions, not mine)
... 328 more uncommitted paths (by top-level dir: Transient 173, infrastructure 152, conversations 1, deployed 1, src 1): git status --short
```

