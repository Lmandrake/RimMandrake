# FOUNDRY_REBOOT_HANDOFF_202610230722 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610230517`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Owner order 2026-10-23: RimPulse is STOPPED (its fixes are built, NOT live; RIMPULSE_DEPLOY_FIX_RUNS_THE_BENCH_CLONE stays parked); work FlowWorks and the Four Biomes, then dirty code, then older tickets. Offline lanes for all of those are now exhausted and code review is at 0 DIRTY; what remains needs the bridge (game UP on a 16-mod list, bridge free), a deploy (game down), or the owner. (filed: lessons)

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Flier afternoon: judge `D:\ClaudeWork\rimmandrake\scratch\flier_afternoon\preview.html` (lift vs paddle; frame 6 has jagged wing-root stubs) for FLIER_AFTERNOON_EXPERIMENT_PROVE_STILL_TORSO / FLIER_FRAMES_AUDIT_BODY_NOT_WING_EXTREMES.
- Ruling wanted: should the EGROWTH master switch also stop the bands (EGROWTH_MASTER_FIX_SPARES_THE_BANDS, blocked)?
- Guardrail art (GUARDRAIL_ART_RESKIN_BORROWED_FENCE) and water-depth reskin want his look in game.
- Live sweep: Contagion northstar has two real FAILs (CONTAGION_BURN_DIAGNOSE_NATIVE_FEELS_NOTHING, COALESCENCE_STAGE_DIAGNOSE_STUCK_AT_ONE); FlowWorks live_session logged FAILs listed on the sweep's ledger notes.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `BARKWARDEN_TINT_JUDGE_GREY_ON_GREY` — done 341283011, three tints dropped (delegated: art); NEXT: view the three creatures in the next review save, close if fine
- `BIOME_DEFNAME_MIGRATION_WAVE_1` — rename done 80e0635c3, implemented; NEXT: with game down run the biomes deploy and a live tile-count check, then rimflow verify
- `CANAL_LAKE_COLOUR_UNIFY_TWO_BLUES` — diagnosis only f188ddfd1; the two blues were two depths; NEXT: get the frame check and his art review at the next live sitting
- `FAUCET_REDRAW_BORROWED_BLEED_WELL` — built 799e2490e, own art in four looks; NEXT: deploy FlowWorks and look at the faucet in game
- `GUARDRAIL_ART_RESKIN_BORROWED_FENCE` — built 34cbcbdef, own rail art; NEXT: deploy FlowWorks and show him the rail in game
- `LADDER_DRAFTS_RETIRE_SEVEN_FOR_ONE` — BENCH deleted the drafts and closed it 34e6494ba; NEXT: confirm closed in the ledger, nothing else
- `PIPE_FAUCET_BUILD_TAP_NAME_NOW_FREE` — built 31f0455f6, DLL committed not deployed; NEXT: deploy FlowWorks, run the T30_pipe_faucet live row, rimflow verify
- `WRECK_ART_WIRE_RENDERS_NOBODY_POINTS_AT` — done b9c1c073e, four wrecks wired; NEXT: verify the wrecks draw in the next biome walk

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
A helper's rebuilt-definition run left the live ModsConfig as a 16-mod list; validate_patch --defs reads it, so pass explicit lists (filed: lessons)

## Closed since the last handoff (5)

- `TEST_SWITCH_FIX_NO_SCRIBE_NO_PEACE` — d3278bc42
- `MODCHECK_SETUP_UNMEASURED_FIX_READS_AS_FAIL` — 528d1f95d
- `CAULDRON_FLECKS_FILL_SEVEN_STILL_BLANK` — 49f734a92
- `SELFTEST_SWEEP_FIX_FOUR_REDS_REMAIN` — 4cdec5dd8
- `CARGO_PORT_DECIDE_PERCHED_ON_SHOULDERS` — f30947df0

## Filed and still open (10) — the next seat's queue

- `PURGE_CARDS_FIX_WRONG_POCKET` — Art ledger: 19 owner purge events carry card text in said; art.py correct-provenance refuses non-ruling events — extend it to purges or record why the
- `FAUCET_REDRAW_BORROWED_BLEED_WELL` — RM_PipeFaucet art: it borrows RM_LiquidTap's side-on bleed-well picture at drawSize 0.8 (PLACEHOLDER); draw a top-view faucet that sits on a universal
- `ART_GUARD_FIX_REFUSES_THE_DELEGATE` — art_guard (pre-push) refuses a delegated art install recorded with --why alone (reason 'agent-why' not mechanical), contradicting delegation_policy.md
- `BARKWARDEN_TINT_JUDGE_GREY_ON_GREY` — RM_Barkwarden (color 168,170,172) and RM_TheUnfinished (168,54,96) multiply a tint over their own regenerated art; the Barkwarden tint was the cougar-
- `EGROWTH_TINDER_HAY_PROVE_COMES_UP_EMPTY` — northstar chain tinder_leaves_fuel FAIL: Tinder burst left Hay=0 (expected 8-14) at RM_TopResolver.Burst(tinder:true) on grasslands quicktest 2026-10-
- `WRECK_ART_WIRE_RENDERS_NOBODY_POINTS_AT` — Four wreck children draw the family's vanilla ShipChunk placeholder although their renders are on disk with no def pointing at them: RM_LongShadeWreck
- `COALESCENCE_REPORT_PROVE_THING_ARG_BINDS` — RM_CoalescenceProof.AbsorbReport takes a Thing but jawa/static_call passes args as one string (validation.py coalescence chain passes the thing id): p
- `EGROSTER_DEAD_ROWS_PRUNE_SILENT_SKIPS` — UtinniPatches RUT_ExplosiveGrowthRoster campaign rows name 10 plants no Defs folder defines (lint eg-roster-rows): RUT_RustPuff/PaleTree/PaleMoss are 
- `CONTAGION_BURN_DIAGNOSE_NATIVE_FEELS_NOTHING` — Contagion northstar 2026-10-23 (quicktest RM_Contagion map, 16-mod list): burn_forced.burn_hurts_native_spares_armored FAIL - the UV-shy native took n
- `COALESCENCE_STAGE_DIAGNOSE_STUCK_AT_ONE` — Contagion northstar 2026-10-23: coalescence_absorbs_and_grows_a_stage FAIL - after 10 passes Stage 1 mass 0; 6 of 6 Unfinished alive, none inRing, sti

## Commits

```
a276e1918 conversations: catch-up 1 record(s)
168c920fe FOUNDRY acceptance sweep 4: FlowWorks live_session rows recorded (4 FAIL on pit/pond/ledger items), Scald steam lock partial
c1e46d9e7 ledger: EGROWTH x3, DONOR_ROSTER_GUARDS implemented; PALETREE dropped; fliers noted
85fe6a480 RM_Bileworm roster guards: packageId mandrake.rm.warscar (the Scarlands mod's real id; scarlands never existed). No Zrrik roster row remains.
a07618819 Code-review marks: ExplosiveGrowth kernel, map component, fuzz CLEAN
e7dc6f86e ExplosiveGrowth: suppression off clears laid grids; out-of-scope maps drop charges; tell stage follows charge down (EGROWTH_SUPPRESS_FIX_OFF_STILL_SUPPRESSES, EGROWTH_SCOPE_FIX_FROZEN_CHARGES_GAMBLE, EGROWTH_TELL_FIX_STAGE_RATCHET_STUCK)
6fba42fad Code-review marks: remaining 67 DIRTY files CLEAN (DIRTY 0)
e795b217d lesson: retarget collisions leave duplicate generated blocks
796ae548e BiomeCastEvictions_WildBiomes: drop 541 ops on the 10 AB_* biomes (sarg.alphabiomes retired); header counts corrected
8bc71b238 AnimalTolerances_Ashkarr: merge 56 duplicate per-animal blocks to the widest band (retarget collisions let a later raw-band pin undo the fit on 61 bounds; WIDEN ONLY)
2ef2513f8 BeastNorm_Law3: drop dead op on bare donor Devourers (RSW_Devourers already holds 37.5/2.37)
98752c2f1 OnlyOurFactions: header cited a stale count (48; file has 42 ops)
21f19ae3e RUT_ScaldFish: drop stale TEMPORARY-art comment on RUT_BladderboilCatch (finished render installed 2026-10-07)
06f752d35 Code-review marks: RSW races, StarWarsRaces generated defs, Waterline/HuttEyes/PlantNames/SW_Support CLEAN
b6db219a5 Code-review marks: 26 DIRTY def/patch files CLEAN (Kotor absorbed, SeaBeasts, Rot/Webwork/Wrecked, Armoury patches, casts)
22bfbfbe2 FOUNDRY acceptance sweep 3: Contagion northstar live runs recorded; two FAILs filed (burn native, coalescence stage)
18e9b17b1 Cast EMPIRE: drop SurvivalTools_Multitool (mod retired 2026-09-11; the card-13 regen resurrected it from the notes)
d03d553fe Armour_Leather: repoint RUT_MushroomLeather/RUT_MoonlessSilk to the RM_ defs that exist (patch was a silent no-op)
50ed8bbfc ledger sync + lessons: GUARDRAIL_ART implemented, REEL_TAP needs owner, PIT_SUPERDEEP reconciled partial
515001c30 Code-review marks: guardrail atlas builder, artlist, FlowWorks_ThingDefs.xml, review_map_coverage.py CLEAN
... 90 more: git log --oneline ef79f9321..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-23T07:21:22Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M infrastructure/state/ledger/events/OWNER.jsonl   owner-seat ledger events, not mine
?? src/RimMandrake/FlowWorks/northstar/live_session_result_20261022T235239.json   the live-sweep subagent's generated FlowWorks result
```

