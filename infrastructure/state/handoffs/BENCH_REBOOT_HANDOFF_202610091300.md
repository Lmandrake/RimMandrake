# BENCH_REBOOT_HANDOFF_202610091300 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610090437`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The owner's ruled art sheets are carried out with `art.py enact` alone. Since tonight it takes a followed note off the open notes; the owner ruled *"You shouldn't leave my notes AFTER you follow the notes"*. It also flags any pick made before a sheet rebuild as a stale-letter CONFLICT. **Never act on a sheet note by hand or brief an agent from raw decisions notes.** Run the enact preview, which shows what is already followed and what is genuinely open. The day's morning list for him is `Transient/bench_night_digest_2026-10-09.md`; it is ranked.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
Everything he needs is ranked in `Transient/bench_night_digest_2026-10-09.md` (native `D:\Luke\dev\RimMandrake\Transient\bench_night_digest_2026-10-09.md`). The top five:
- **Renders to judge:** 32 overnight renders on one image (`Transient/morning_art_contact_2026-10-09.png`). The Hawkbat flying master east passed canon 7/7 and is his gate for the next stage.
- **canon_check passes wrong art.** It passed 23 of the 23 renders he rejected. The stricter v2 grader is committed but off, because it didn't clearly win. A 15-entry Must-show rewrite is waiting as a sample for him to judge before any more.
- **Sketto lock: three decisions.** Where the plate comes from (option A prepped), a new S/N floor (0.38 is unreachable), and an east path (plate v3 east failed canon).
- **Two design drafts:** lost-cargo quests and species traits. Also the xenotype canon rulings, and name lists for 22 species.
- **Sheet decisions:** 35 enact conflicts and 11 sheet notes need him. 70 cartoonish-era textures are owed a re-ruling (13 verified swap pairs are on an image). Should the art ledger get a `retract` verb for 28 spurious rejected events?
Shipped tonight but **not deployed** (the next restart picks it up):
- Anomaly suppression in Utinni (40 events + monolith).
- Force-disturbance wording.
- Greentide art.
- Species-ability gene removals (31).
- Surnames for 41 namers.
- Twilight and Scald flora with their C#.
- Thurlsponge wrecks.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `ART_SHEET_DONOR_JOIN_GAPS_1` — implemented c6e6be2c0 (`_Wild` join stems); the join shows on the next sheet rebuild; NEXT: verify on the next rebuild that RSW_Plant_Nysyllin_Wild joins its renders, then close.
- `CANON_ENTRY_BRIEFS_OWED_1` — 15 Must-show lists rewritten as a sample (b138dc0d5..ebc2825c6), paused for the owner's verdict; NEXT: card the owner on whether to apply the body-plan/colour/negative format to the remaining entries, including the gorg "two legs" contradiction.
- `SCALD_UNDERWATER_FLORA_1` — implemented 09255bb7d + 6c08832b8; not deployed; NEXT: after the next restart, open a new Scald map and confirm the 7 flora and the wreck thurlsponge spawn (toggle off = none).
- `SHEET_DONOR_COLUMN_FALSE_PASS_1` — implemented (already fixed at 98b0bac5f; gate req 4 passes 27/27); NEXT: close it with sha 98b0bac5f after one rebuilt sheet confirms.
- `TWILIGHTSEA_FLORA_PASS_1` — implemented 3a2393b3f + 33846bde3 (+ fix 7723bd5f4); not deployed; NEXT: after the next restart, check the floor flora, well placement and both comps live on a Twilight map.
- `UNSUBSTANTIATED_SPECIES_ABILITIES_1` — owner rulings applied, 31 genes removed (87888849a); not deployed; NEXT: after the next restart, spawn one Anzati and one Cerean and confirm the removed genes are gone.
- `WEATHER_STONES_OWN_ART_1` — renders done (wsart_RM_*), released; NEXT: put the 3 renders to the owner for a pick, then `art install` them.
- `FLYER_STABLE_BODY_GATE_1` — Hawkbat master east done; Sketto option A prepped (56568324e); NEXT: card the owner on the three Sketto lock decisions in `Transient/sketto_repose_fix_2026-10-09.md` and on OKing the Hawkbat east master.
- `LEANINGSCRUB_VENOMVINE_SITTING_1` — run-sheet ready (620b54f6f), deferred to next session by card; NEXT: take the bridge and stage the sitting per `Transient/venomvine_sitting_runsheet_2026-10-09.md` once the owner is present.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- canon_check passes wrong art: 23/23 owner rejects passed (filed: lessons)
- Sheet rebuild re-letters columns; the old ingest wrote 28 spurious rejected events, now guarded (filed: lessons)
- Subagent "KEEP-ruled"/"no ruling" claims were false twice in one night (filed: lessons)
- Followed sheet notes re-fire if left open (see: memory followed-sheet-notes-must-be-cleared; enact 6f7940ee8, 374c9b87b)

## Closed since the last handoff (6)

- `CANON_REALISTIC_REFERENCE_SWEEP_1` — 29a03f481
- `BIOME_MOD_UNIFICATION_1` — 33408ba72
- `GREYSEA_FLORA_PASS_1` — 20fd7cf7c
- `PROPANELAKE_FLORA_PASS_1` — 865c70ad6
- `BIOME_MOD_SPLIT_EXECUTION_1` — 8d1104bdfb43068735266ce426fa366e49530732
- `ART_PIPELINE_DAEMON_1` — 368794eb1

## Filed and still open (4) — the next seat's queue

- `SELFTEST_DRIFT_CLEANUP_1` — Selftests red from FOUNDRY in-flight work 2026-10-08: FlowWorks settings table lacks excavationLoadRepairEnabled (selftest_flowworks_northstar); termi
- `TWILIGHT_SEABED_WELLS_MISSING_1` — Twilight skylight wells run only on the old pocket-map floor; the RM_SeabedLayer floor gets none, so well-driven flora (gleamfloss, farwick, tollhorn)
- `DUMP_REFRESH_JAWARETURNTOW_1` — Refresh def dump: RUT_JawaReturnTow now loads (9b48689f2) but load-14 dump predates it; selftest_utinnipatches_dump red
- `SUMP_NOOTHELM_B_PLANT_1` — New Sump plant from the noothelm B render, cuisine implications

## Commits

```
75e72d80b Digest: sheet TODO sweep
c8b1b18e3 Sheet TODO sweep: 24 enact notes marked done with evidence; 11 left for owner
ef1b635e2 Acceptance sweep 10-09b: 1 pass, 1 fail, 2 partial recorded
8de3580f3 CLAUDE.md: rimflow/modcheck are PATH commands, not R="python3 ..."; $R
7a204f7af belt offline progress 2026-10-09b
4e1bb4e26 ledger: reconcile venomvine forms pitch complete
9d104d93f Sketto option A east follow-up: plate v3 east failed canon; attempt1 as donor measured
15990ca80 Digest: Sketto option A prep
56568324e Sketto option A prep: flyer_plate_from_master script, selftest, measured notes, before/after picture
b7799653c Digest: sheets gate
a5f966b31 Rebuild 12 stale biome sheets: gate 27/27; stale-letter notes
a4814abb9 Digest: painterly swap image
0dc6c9494 Painterly swap candidates: 13 verified of 28 census pairs
a3687a359 Digest: cartoonish-era census
e9ab6ca45 Cartoonish-era art census 2026-10-09
8270d4435 artreg: remove dead verdict/committed/deployed verbs (0 callers, 0 events)
8d9b562bb artpipe_state find: drop art_status.json (derived dup of registry.jsonl); notes on why hub readers stay
3f86bf032 Delete dead round2 deck builders (0 callers, last touched 2026-09-10)
85bdf9d5d apply_assignment_verdicts reads propagated notes from the art ledger; delete dead round2 deck builders
c2340fc39 Retire apply_verdicts.py and make_verdict_sheet.py (0 live readers; superseded by art ledger)
... 334 more: git log --oneline ce6c50383..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-09T12:54:34Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/artpipe_orphan_masters.md   artpipe orphan census tool output (derived; not this window)
 M Transient/modcheck/fixtures.json   FOUNDRY modcheck run output (not this window)
?? conversations/   earlier BENCH windows' conversation exports (not this window)
?? deployed/config/ModsConfig.before-tier-explosiveknockback.xml   earlier BENCH windows (unchanged since the 10-08 morning handoff, which attributes them)
?? deployed/config/ModsConfig.before-tier-flowworks.xml   earlier BENCH windows (unchanged since the 10-08 morning handoff, which attributes them)
?? deployed/config/ModsConfig.before-tier-kineticarms.xml   earlier BENCH windows (unchanged since the 10-08 morning handoff, which attributes them)
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Doors/   earlier BENCH windows (unchanged since the 10-08 morning handoff, which attributes them)
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Excavation/   earlier BENCH windows (unchanged since the 10-08 morning handoff, which attributes them)
?? src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Modules/   earlier BENCH windows (unchanged since the 10-08 morning handoff, which attributes them)
```

