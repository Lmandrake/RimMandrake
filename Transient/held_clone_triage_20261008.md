# HELD_CLONE_WORK_TRIAGE_1 decision table (2026-10-08)

origin/main at triage: `8807aaa41` then landing commit `6cdda1140`. Compared by file CONTENT (blob equality, then "is the commit's own diff already inside origin's later version", ledger shards line-by-line).

| item | verdict | evidence | sha |
|---|---|---|---|
| `_fwY_gate` RM_SluiceGate.cs, RM_SluiceGateMath.cs, RM_SluiceGateSettings.cs (modified) | LAND | no `Building_RM_SluiceGate` or math on origin (grep src/); only the empty settings stub. Added 2 Compile Include lines, winbuild FlowWorks 0 errors, DLL + .srchash committed. Draft: no ThingDef or engine hook wired yet | 6cdda1140 |
| `_fwY_gate/blood/quarry/tanker` belt_fwlogistics_*_20261005.md (4) | DROP | every one is the empty template ("(in progress)", every section "(pending)" or blank, 12-19 lines); nothing to keep | n/a |
| `reconcile` 12 patch-unique commits | DROP | art ledger events: all 11 jsonl diffs have 0 lines missing on origin (incl. both BENCH ledger events). Source effects verified on origin: LivingBolt drawSize 0.1, Abyss ShadowCharger/Thunderox gone, Cindermare Graphic_Multi, Slimification Glurro salve removed, WALL_FLIT item present. Twins on origin: Blue Desert sitting 3 `94d090639e`, Slime `79174bf845`/`c46bfc1232`, Abyss s2 `02f6ae77d6`/`586d7bcc39`. Sheet html/snapshots/decisions are regenerated artifacts; origin holds LATER owner decisions (e.g. greysea RM_BrineCrown redo 10-06 -> B 10-07) | n/a |
| `reconcile` "Rust Cathedral sheet ingested" `101aa20132` (no same-subject twin) | DROP | its 12 art events + 2 ledger events all on origin; LivingBolt xml change present (drawSize 0.1); WALL_FLIT item present (later extended by `128067cb14`); decisions.json rows 5/5 identical | n/a |
| `reconcile` untracked Transient/modcheck/fixtures.json | DROP | generated; path tracked on origin | n/a |
| `~/.cache/pyrelands_replay_1607507` f48797f41, eb90adf08 | DROP | twins `4f8ba82b4e` Contagion close (origin deleted the RustPuff pngs and closed the two items later) and BENCH events 90/90 and 61/61 present on origin | n/a |
| `~/.cache/stillsand_s2_replay` same two + `6d39812ec` "Blue Desert sheet rebuild state" | DROP | first two as above; `6d39812ec` is a working-copy html + snapshot, regenerated since (`453b228c61`, `2156f39132`, `db122e7ce1`) | n/a |
