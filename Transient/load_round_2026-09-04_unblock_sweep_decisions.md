# Load round 2026-09-04 — unblocking 4 mechanical FOUNDRY items

Decision strings written BEFORE launch, per rimworld-load-round §2.

## Restart 1 — MINIMAL list (already includes fluidcanals + inhabited + odyssey + bridge)

### INHABITED_SETTLEMENT_MAPPARENT_GAP_1
- PROVE: place/find a WorldObject_InhabitedSettlement, check its float menu options
  when a caravan is on/near its tile.
- EXPECT: no "Enter" option appears at all (WorldObject.GetFloatMenuOptions, not
  MapParent.GetFloatMenuOptions, is what runs) -> confirms dead per the review.
  If somehow enterable, watch Player.log for
  "[RimMandrake.Inhabited] composed REAL district" / "composed STUB district"
  (GenStep_ComposeSettlementDistrict's own unconditional log line) as the
  positive-run signal.
- LIES: a debug-only "visit"/teleport action could generate a map through a
  DIFFERENT path than the real caravan-arrival flow and produce a false positive.
  Use the real float-menu/caravan route, not a debug shortcut, for the primary read.

### INHABITED_TILEMUTATOR_NO_ENTRY_1
- PROVE: assign TileMutatorDef RM_InhabitedPlace to a world tile (bridge
  world-editing), generate a map there (start/visit a colony on that tile).
- EXPECT: Player.log contains "[RimMandrake.Inhabited] put " (GenStep_InhabitedStock,
  order 910 — only fires after GenStep_InhabitedCast/order 900 has filled the stock
  holder, per the file's own ordering comment) AND a live census
  (jawa/list_pawns / list_things) shows cast pawns + stock goods physically on
  the generated map.
- LIES: absence of the stock log line is necessary but not sufficient on its own —
  confirm with the positive census too, in case the log line changed/was removed
  since last read.

## Restart 2 — isolated (bridge tier + helixtellurox only)

### HELIX_TELLUROX_SHELL_LOAD_CRASH_1
- PROVE: enable mandrake.rsw.helixtellurox on the smallest possible dependency-
  complete list, launch, read Player.log.
- EXPECT: no `MissingMethodException: default ctor for System.String` and no
  "Recovered from incompatible or corrupted mods" fallback to Core-only.
- LIES: a crash from an UNRELATED mod interaction on the full 578 list would not
  reproduce here — a clean isolated load does not prove the full-list crash is
  gone, only that this mod alone isn't the cause (or is, if it reproduces).

## Housekeeping
- Restore FULL modlist before ending this round (owner's real list, before he plays).
- Bridge taken by FOUNDRY at session start; release when done driving.
