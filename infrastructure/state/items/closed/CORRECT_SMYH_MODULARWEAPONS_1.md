# CORRECT_SMYH_MODULARWEAPONS_1 — SMYH_MODULARWEAPONS_PAWNGEN_CRASH_1's verify criteria are already satisfied

## Spec
`SMYH_MODULARWEAPONS_PAWNGEN_CRASH_1` (BENCH's item) diagnosed a transpiler
collision between ModularWeapons2 and Show Me Your Hands (SMYH) that crashed
pawn generation on any new map. Its own `## verify` section calls for: a
dev quicktest generates a map and starting pawns with 0
`InvalidProgramException` in `Player.log`, and a positive sighting of a
pawn spawning holding a weapon.

Its option 3 ("Disable ModularWeapons2") landed as a side effect of
`ARMOURY_MW2_CUT_1` (owner ruling 2026-09-13: cut MW2 entirely, superseding
the item's own option list, which had recommended option 2 — drop SMYH —
as the cheaper unblock). MW2 is now fully removed from ModsConfig and SMYH
is restored active. This session (FOUNDRY, 2026-09-14) ran exactly the
quicktest this item's verify section describes, on the full 594-mod list
(not minimal+affected, but a strictly harder test):

- `rimworld/start_debug_game_ready` generated a quicktest map with three
  starting pawns (Giggles, Nadd, Wouter) — **zero**
  `InvalidProgramException` anywhere in `Player.log` for this whole session
  (grep confirmed across the full log, not just the map-gen window).
- SMYH's own hand-draw path is active and running: `[ShowMeYourHands]:
  Defined hand definitions of 748 weapons` appears in the boot log (up from
  656 pre-cut, consistent with MW2's part-slot suppression no longer
  applying).
- Positive sighting beyond the item's own bar: equipped `guy762_brifle` on
  a colonist via `jawa/pawn_gear`, confirmed via `jawa/pawn_get` it
  resolves correctly, drafted the pawn, ordered `AttackStatic` against a
  spawned hostile — it fired and downed the target
  (`[Ninefold] Shkaar satiation +3.0 (downed in battle: Kit, Prodigy)`
  logged the outcome). So not just "a pawn holds a weapon" but "a pawn
  holds, draws, and fires a weapon with SMYH active."

Full step-8 account (deploy fix, cross-reference cleanup, canonical resave):
`infrastructure/state/items/ARMOURY_MW2_CUT_1.md`, section "Step 8 verify —
done 2026-09-14".

**The correction**: close `SMYH_MODULARWEAPONS_PAWNGEN_CRASH_1` — its root
cause is gone (no ModularWeapons2 assembly left to transpile anything) and
its own verify criteria are met, evidenced above.

## Verify
`rimflow show SMYH_MODULARWEAPONS_PAWNGEN_CRASH_1` reads `state: done` (or
equivalent closed state), citing this item or `ARMOURY_MW2_CUT_1`'s commit
as the closing sha.

## Criteria
BENCH reviews the evidence above (or re-runs the same quicktest check) and
closes `SMYH_MODULARWEAPONS_PAWNGEN_CRASH_1` if satisfied, or says what
additional verification it still wants.

## Watch out
- This was checked against the FULL 594-mod list, not the
  minimal+affected list the item's own verify text names — a harder test
  (more mods, more interaction surface), so it should not need re-running
  on the smaller list to count.
- The `InvalidProgramException` grep covered the entire session's
  `Player.log` (a fresh boot to `Bridge token:`, cold start), not just a
  narrow post-map-gen window — no false negative from checking too small a
  slice.
