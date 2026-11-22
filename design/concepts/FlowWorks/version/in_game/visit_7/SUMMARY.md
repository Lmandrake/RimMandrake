# FlowWorks 0.1.0 — in-game acceptance, visit 7

Driver: detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_ACCEPTANCE_VISIT_SEVEN, game a on Archmagi.
Ran 2026-11-22 1:57 AM to 3:10 AM PST (bound 4:57 AM).

Why this visit: the solid-deck fire fix (496604468f) and the reach-row scene repair (647bc9b0db) after visit 6.
`rerun_relation.py` named 6 of 31 checks [measured]: sc_canal_fire, sc_hung_bridge, sc_moat_raid, sc_toss_flame, sc_walk,
OL_OWNER_LOOK_READS.

## Build and list

- Game a, RimWorld 1.6.4871 rev590. FlowWorks deployed in sync with the source (dry run: "in sync (1038 files)")
  [measured]. No mod code changed in this visit. Only the proof script and its selftests changed.
- Lists: the 13-mod flowworks tier (modset_builder.py, all five DLC) for the minimal checks; his full list (FULL.LATEST,
  315 mods, Camera+ in it) for sc_walk, as in visits 4 and 5. Every row carries `build_match.py identity`.

## Results [measured]

| check | verdict (last row) | runs | notes |
|---|---|---|---|
| sc_toss_flame | PASS | 1 | |
| sc_moat_raid | PASS | 1 | |
| sc_canal_fire | PASS | 1 | calm site loaded and verified first |
| sc_hung_bridge | PASS | 9 | last 3 PASS in a row on b1cc65afe2; 2 earlier FAIL rows classed HARNESS and SITE, both repaired (below) |
| sc_walk | PASS | 1 | his full list (315), 12 of 12 rows, 179 s |
| OL_OWNER_LOOK_READS | not counted (visit 4 row) | 0 | `rerun_relation.py` read it untouched by the change after this visit's proof edits; its one BLOCKED row is HARNESS, unrepaired, owner RIMMANDRAKE_REPORT_SUBMERGE_SHADOW_QUEUE_JUDGE_CANNOT_SEE_ORDER (open); it decides no bar |

### sc_hung_bridge: three faults in the scene and the instrument, repaired; no mod fault

The deciding rows the road back owed all held on every run. GRATE_fire_burns_people_above passed 9 of 9 [measured]. The
grate/solid burns were 10/0, 10/1, 10/0, 13/6, 7/0, 8/1, 9/4, 13/9 and 13/5. That is the solid-deck fix 496604468f, shown
in game. SB_islands_restore_reach passed 8 of 9; run 5 was withheld (item 3 below).

1. **UND_crush_below_and_wreck FAIL (run 3), class HARNESS.** The crush counter rose 6 -> 9, but the colonist under the
   deck read 6 hediffs before and 6 after. The row counted hediffs. A crush that destroys a part outright replaces the
   injuries on it with one MissingBodyPart, and a second injury of one kind on one part merges into the first and raises
   only its severity. Repair 581e6f4baf: `new_harm()` reads harm by (def, part), count and severity. Offline: 6 harm
   cases; the parent's count rule reads both real-harm cases as no harm (`evidence/crush_parent_rule.txt`).
   Live planted (the fall aimed off-map: no deck falls): FAIL, newHarm [] (`evidence/crush_planted.json`). Real: the
   PASS runs after it read Crack Jaw, MissingBodyPart Eye, Nose, Ear and Cut Neck.
2. **UND_shot_solid_deck FAIL (run 6), class SITE.** The spawned Mercenary_Gunner held no gun (ranged=False). Its melee
   verb reached the next square, so it read can=True over a solid deck. In the 15 earlier rows the gunner had ranged=True.
   Repair b1cc65afe2: the proof hands the gunner a revolver and requires ranged=True (SITE). Offline: an unarmed-gunner
   mock case is red on the parent (FAIL) and green on the fix (withheld). Live planted (the revolver taken away again):
   both shot rows withheld, UNMEASURED, with the run-6 reading (`evidence/unarmed_planted.json`). The deck verdict is
   unchanged; its foil UND_shot_grate_deck read can=True in every run.
3. **SB_islands_restore_reach UNMEASURED (run 5), class SITE.** The spawned colonist's Mining was disabled by backstory, so
   `set_pawn_skill` refused and the row was withheld. Repair b1cc65afe2: a colonist whose Mining is disabled is drafted
   and another spawned, up to 5 tries. 1 of 13 workers spawned on 2026-11-22 had Mining disabled [measured]. Offline: a
   mock with 1 disabled colonist first reads PASS, and with every colonist disabled reads withheld. The parent read the
   all-disabled case PASS.
4. Real build after both repairs: three full runs in a row PASS on b1cc65afe2. GRATE 9/4, 13/9, 13/5; reach, crush and
   shot rows PASS in each (`evidence/sc_hung_bridge_20261122T0232*`, `T0235*`, `T0238*`).

`maturation.py red-seen` cannot record these reds: each fault lives in the test's own file (refused by name), and a live
check's C# fault never reaches the game from the tree. sc_hung_bridge is not an offline decider, so no certificate reads
it. The planted live runs above are its red, and the last row's `repair` names them.

## Owed cases

- Road back, sc_hung_bridge GRATE three runs in a row (RIMMANDRAKE_GATE_INFERNO_DECK_CHANCE_SOLID_OUTBURNS_GRATE,
  RIMMANDRAKE_DECIDE_FLOWWORKS_SOLID_DECK_LOW_CHANCE_SATURATES_IN_ONE_BURN): met. The last 3 rows PASS in a row on
  b1cc65afe2, and GRATE passed in all 9 runs.
- Road back, sc_hung_bridge reach (RIMMANDRAKE_UNSTICK_FLOWWORKS_FILL_JOB_HOLDS_GRAVEL_BESIDE_THE_HOLE): met, 8 of 9 PASS.
  The ninth was withheld for a Mining-disabled worker, now repaired.
- sc_walk (RIMMANDRAKE_FINISH_FLOWWORKS_WALK_SCENE_HALF_THE_BAR_UNASKED): met on his full list.
- sc_hole_prison three in a row (RIMMANDRAKE_TRACE_FLOWWORKS_AWAKE_PRISONER_MEAL_SKIPPED_ONE_RUN_IN_TWO): met in visit 6 on
  65c45b6e98, and untouched since.
- The other road-back rows (sc_fill_front, sc_fill_tiers, sc_garden, sc_hose_look, sc_pit_trap_raid, sc_source_pays,
  sc_trench_cover, sc_fetch_fallen, sc_geyser_tub, sc_ice, PIT_LOOK_1114_LIVE) and the blind cycle 4 owed cases (sc_garden
  and the planted faults): untouched by this change. Their visit 3 to 6 rows carry, as `rerun_relation.py` reads them.
- OL_OWNER_LOOK_READS items: carried, not counted, owner as above.

## Beyond the checks

Desktop and map captures (`screenshots/`), looked at. Two things looked odd, and both are explained: chunk lines and a dark
block that stand on the calm site save loaded fresh (`strange.jsonl`).

## The savegame

No new savegame. The walk savegame stays visit 4's, as in visits 5 and 6. Game a's FlowWorks is now deployed at the source,
and the save loads it as deployed:
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT4_FULL_20261121_1727.rws`
(13.6 MB) [measured].

## Items filed

None. No mod fault was seen. The three scene and instrument faults were repaired in the sitting (581e6f4baf, b1cc65afe2).

## Exit
```
ingame_rows: {sc_canal_fire: pass, sc_hung_bridge: pass, sc_moat_raid: pass, sc_toss_flame: pass, sc_walk: pass, OL_OWNER_LOOK_READS: unmeasured}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT4_FULL_20261121_1727.rws
exit_met: true
```
