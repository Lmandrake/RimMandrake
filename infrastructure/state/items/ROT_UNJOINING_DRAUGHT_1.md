# ROT_UNJOINING_DRAUGHT_1 — The Unjoining Draught: a brutal purge, learned from the rite, that drives parasites, symbionts and Anomaly metalhorrors out of a body, anywhere

Caused by `ROT_SCORING_SITTING_1` (turn 1, new-marks redo). Free tier (`mandrake.rm.therot`) for the draught,
its research and its purge; the trigger from the rite is campaign (`ROT_UNJOINING_RITE_1`). Design:
`design/Jawa/worldbuilding/biomes/rot_new_marks_redo_2026-10-02.md` T2, review
`design/Jawa/worldbuilding/biomes/rot_bedazzle_review_2026-10-02.md` §8. Mark 2 (technology that travels).

Ruling: **tech = BOTH The Gut-Mother and The Unjoining Draught** (decision taken by question card 2026-10-02
10:50 PDT). Ban 4 holds: the draught is a medicine made anywhere, not a tea or symbiont; it removes symbionts,
it never carries one.

## spec

**Measured in RimSage 2026-10-02:** vanilla `HediffDef`s `MuscleParasites` and `GutWorms`; Anomaly's
`HediffDef MetalhorrorImplant` (class `Hediff_MetalhorrorImplant`) and the public static
`MetalhorrorUtility.TryEmerge(Pawn infected, string reasonKey = null, bool sympathetic = false)`, which the debug
action `EmergeMetalhorrors` and `DelayedMetalhorrorEmerger` also use.

1. **The purge hediff.** `HediffDef RM_UnjoiningPurge`: one in-game day of severe sickness (consciousness and
   moving down, pain high, vomiting via the vanilla vomit chance), then gone. Shared with the rite
   (`ROT_UNJOINING_RITE_1`), which applies the same hediff.
2. **The draught.** `ThingDef RM_UnjoiningDraught`, an ingestible medicine made at a drug lab (recipe: fungal
   material from the Rot kit plus herbal medicine; measure the kit's material defNames), usable anywhere. New
   C# `IngestionOutcomeDoer_RM_Unjoining`, driven by a list def `RM_UnjoiningTargetsDef`:
   - **removes** `MuscleParasites`, `GutWorms`, every Rot symbiont hediff (`RM_Sym_Quickflesh`,
     `RM_Sym_Nightwake`, `RM_Sym_Sheenblood`, `RM_Sym_Mycoid`, and `RM_SheenSymbiosis`), and any hediff whose def
     carries `RM_UnjoinableExtension` (so other mods' and future parasites opt in by data);
   - drops one `ThingDef RM_SymbiontHusk` per symbiont removed (the dead symbiont, a grey husk: a readable sign);
   - **forces out a metalhorror:** if `MetalhorrorImplant` is present, call `MetalhorrorUtility.TryEmerge(pawn,
     <our reason key>)` (the horror bursts out now, where it can be seen and fought), never a silent delete;
   - always adds `RM_UnjoiningPurge` and a small permanent organ injury (liver or kidney, setting).
3. **Learning it.** `ResearchProjectDef RM_UnjoiningDraught` (prerequisite `RM_AdvancedFungi`, expensive): in the
   free tier it is ordinary research, so the free mod stands alone. In the campaign the first completed Unjoining
   rite finishes it at once (`ROT_UNJOINING_RITE_1` part 6: the doctor watched a symbiont die and learned how).
4. **Readable signs:** the purge on the patient, the husk, a letter when a metalhorror is forced out (*"The
   draught found something that was not a parasite."*).
5. **Mod Settings** (Technology section): on/off; organ damage on/off; purge length.

Depends on: none hard. Blocks: `ROT_UNJOINING_RITE_1` (purge, husk, research). Art: `RM_UnjoiningDraught`,
`RM_SymbiontHusk` in `infrastructure/artpipe/art_lists/rot_turn1_2026-10-02.csv`.

## criteria

Deterministic, in `THE_ROT_FIRST_SCRIPT_1`'s `validation.py`, through `jawa/get_defs` and debug `[Tool]`s:
- Defs resolve: `HediffDef/RM_UnjoiningPurge`, `ThingDef/RM_UnjoiningDraught`, `ThingDef/RM_SymbiontHusk`,
  `ResearchProjectDef/RM_UnjoiningDraught`, the recipe, `RM_UnjoiningTargetsDef` (one).
- A colonist given `MuscleParasites`, `GutWorms` and `RM_Sym_Sheenblood` who ingests the draught: all three are
  gone, `RM_UnjoiningPurge` is present, one `RM_SymbiontHusk` is on the map, and the colonist has one new
  permanent organ injury (with organ damage on; none with it off).
- A colonist with `MetalhorrorImplant` (added by debug) who ingests it: the hediff is gone and the map's count
  of metalhorror pawns rose by ≥ 1 within 60 ticks.
- A colonist with none of the listed hediffs: only the purge is added.
- With the campaign loaded, completing one Unjoining rite sets `RM_UnjoiningDraught` research finished; in the
  free tier it is reachable by ordinary research (prerequisites met → project startable).
- Toggle off: the recipe is not offered and the outcome doer does nothing.
</content>
</invoke>
<invoke name="Bash">
<parameter name="command">cd /home/mandrake/rm/bench/infrastructure/state/items; for f in ROT_*.md; do t=$(head -1 $f | awk '{print $2}'); [ "$t.md" = "$f" ] && echo "ok $f" || echo "MISMATCH $f $t"; done