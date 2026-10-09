# BENCH overnight, 2026-10-08 23:00 → 2026-10-09

Everything below is committed and pushed. Nothing is deployed. Every change waits for the next restart, which FOUNDRY holds.

## Needs you (ranked)
1. **Hawkbat flying master, east.** It passed canon 7/7. OK it so the south/north masters and wing frames can follow: `D:\Luke\dev\_artpipe\_artsrc\hawkbat_fly_master_v1_east\hawkbat_fly_master_v1_east.png`
2. **The canon check passes wrong art.** It passed 23 of the 23 renders you rejected. The likely fix is tighter Must-show lines in the canon entries, and those entries are yours to edit. The stricter v2 grader didn't clearly beat v1 when tested, so it's committed but switched off. `D:\Luke\dev\RimMandrake\Transient\canon_check_leniency_2026-10-09.md`, `D:\Luke\dev\RimMandrake\Transient\canon_check_v2_prototype_2026-10-09.md`
3. **Design drafts to review:**
   - lost-cargo quests: `D:\Luke\dev\RimMandrake\Transient\fallzone_lost_cargo_quests_draft_2026-10-09.md`
   - species traits instead of aptitudes: `D:\Luke\dev\RimMandrake\Transient\species_traits_over_aptitudes_draft_2026-10-09.md`
4. **Xenotype canon list, re-measured, with draft rulings.** Cosmetic items are marked as needing your permission: `D:\Luke\dev\RimMandrake\Transient\xenotype_canon_correction_rulings_2026-10-09.md`
5. **Sketto wing frames.** Two still fail canon on tusks and legs, and the plate replaces both of those in the lock step. Should body lines be not-applicable on wing frames?
6. **Sheet leftovers:**
   - Abyss: Durrgak "rename to Sorter", plus 4 conflicts.
   - Deep Desert: 3 Vozzik conflicts.
   - Six sheets are unruled (cauldron, floodedcanyon, theforge, therot, wasteland, weepingstones).
7. **Facing audit.** Dredgel v2 renders are done and await your pick: `D:\Luke\dev\RimMandrake\Transient\facing_coherence_backlog_2026-10-09.md`. Flat placeholder squares are still live for Murrelith and Drommath (both your redos; their new renders await your pick) and Chellow east. For Chellow, choose: finish the beakless v2 set (it needs a new north) or derive an east from the beaked south now in game. Thavrik and Sorruth are cut, as you ruled: `D:\Luke\dev\RimMandrake\Transient\flat_square_art_check_2026-10-09.md`
8. **Name lists drafted for 22 of the 23 species with no namer.** They are canon names first, then a few invented ones marked as such. Ugnaught is the most visible. `D:\Luke\dev\RimMandrake\Transient\species_name_lists_draft_2026-10-09.md`
9. **Code review of tonight's C#.** One crash bug was fixed (7723bd5f4). Small calls for you:
   - Thurlsponge is a deep-floor plant but grows on the shallow tiles beside wrecks.
   - Gloamurn can never charge on the seabed-layer Twilight map.
   - The Anomaly suppression has no Mod Settings toggle.
   `D:\Luke\dev\RimMandrake\Transient\night_csharp_review_2026-10-09.md`
10. **The sheet script had a stale-letter hole, now closed (ab6bed31a).** The audit of tonight's ingests found every ruling and install correct. It did find 28 spurious `rejected` events on 10 redo rows, and those now block 7 pictures from mechanical re-install. Decide: should the art ledger get a `retract` event type? `D:\Luke\dev\RimMandrake\Transient\stale_letter_ingest_audit_2026-10-09.md`
11. **Venomvine sitting run-sheet** is ready for next session. Seven forms share one texture: `D:\Luke\dev\RimMandrake\Transient\venomvine_sitting_runsheet_2026-10-09.md`

## Done overnight
- **Species abilities:** your card rulings are applied. 31 genes were removed across 14 races (87888849a).
- **Surnames:** 41 species namers now use their surname lists, with a selftest (ee3b0049d).
- **Flora built:**
  - Twilight Sea: 10 flora, plus Route B placement and the gloamurn and murkspindle comps (3a2393b3f, 33846bde3).
  - Scald: 7 flora (09255bb7d), plus thurlsponge colonising wrecks (6c08832b8).
- **Sheet enactment:**
  - 17 more biome sheets plus Deep Desert and Lantern Deeps.
  - Followed notes are cleared on every sheet, and about 60 failed redraws were re-filed.
  - enact can no longer re-queue a followed or done note (6f7940ee8, 374c9b87b).
- **Selftests:**
  - The proof_all crash, the memwatch crash and the JawaBench tool test are fixed.
  - The one remaining red test is the stale def dump (DUMP_REFRESH_JAWARETURNTOW_1, FOUNDRY).
- **Ledger cleanup:**
  - 5 stale BENCH items closed, 8 reclaimed.
  - The canon realism sweep is closed.
  - Found: Twilight wells don't exist on the seabed layer (TWILIGHT_SEABED_WELLS_MISSING_1).
- **Art:**
  - Sketto plate v2 jobs are filed; green Swarmling v2 is rebuilt from your pick.
  - Kinrath is redrawn as v3 (v2 drew a fifth leg).
