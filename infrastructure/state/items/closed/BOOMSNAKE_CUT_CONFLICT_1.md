## spec
`GR_Boomsnake`'s ThingDef was Cherry-Picker cut by `BOOM_FAMILY_CUT_1`
(2026-09-10), yet `design/Jawa/worldbuilding/biomes/rosters/the_pyrelands.json`
still imported it (commonality 0.5) and it was wired live into
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml`
(`PYRELANDS_FAUNA_WIRING_1`, 2026-09-13) and spawning on the live map as of
2026-09-14 (MEASURED, per `BOOMALOPE_CUT_EVERYWHERE_1`'s flagging note).
Investigate whether a later, specific ruling restored it; fix only if
unambiguous.

## timeline, reconstructed from git history and the ledger (all 2026-09-10 unless noted, local -0700)
- `06:20:55` — `design/Jawa/worldbuilding/review/round2/decisions_propagated.json`'s
  `homeless:GR_Boomsnake` row records `"decision": "move"`, `"note": "Pyrelands"`
  — the round-2 move-mapping call, made before any awareness of same-day
  events below.
- `07:41:33` (commit `69f46929c`) — `design/Jawa/worldbuilding/review/round2/
  biome_findings.md` is authored, already stating (bottom of its Pyrelands
  section): *"Arrivals (2): AA_Razorjack, Dalgo (GR_Boomsnake's 'Pyrelands'
  move is voided by the boom-family cut)."*
- `12:48:45` (commit `e75fa1114`) — `BOOM_FAMILY_CUT_1` lands: `ThingDef/
  GR_Boomsnake` (and 14 siblings) Cherry-Picker cut, proven live.
- `17:45:17` (commit `d4a4c10d9`) — `biome_findings.md`'s own summary line is
  edited and STILL reads "boom family (15) CUT — including GR_Boomsnake's
  'Pyrelands' move" — the voiding is reconfirmed after the technical cut, not
  contradicted by it.
- `19:44:43`/`20:53:54` (commits `2533bf0a5`, `9406d5e08`) — the Pyrelands
  fire-web recast lands: *"RECAST: Razorjack arrives as the fire-follower
  (flame-edge hunter); Barbslinger routed here as the ash-grazer"* — the niche
  GR_Boomsnake would have filled is explicitly reassigned to AA_Razorjack,
  with no mention of restoring Boomsnake.
- `23:59:55` (commit `688bddbb2`, `ROSTER_MOVE_APPLY_1`) — a mechanical
  "land all 114 ruled fauna moves into biomes/rosters" pass re-adds the
  `GR_Boomsnake` import row (commonality 0.5, `"law": "owner review 2026-09
  (round2 move mapping): Pyrelands"`) into `the_pyrelands.json` — applying the
  06:20 decision literally, **hours after** `biome_findings.md` had already
  recorded that exact move as voided, and with no reconciliation between the
  two.
- `2026-09-13` (commit `e36c3f8b5`, `PYRELANDS_FAUNA_WIRING_1`) — wires the
  roster (including the stale `GR_Boomsnake` row) into live XML, its own
  header citing "the GR_ correction pass" as one of three sources feeding the
  JSON — but that phrase, read at its actual source
  (`the_pyrelands.json`'s own `GR_Mantistanis` row: *"restored by the GR_
  correction pass"*), belongs to **`GR_Mantistanis`, not `GR_Boomsnake`**.
  `GR_Boomsnake`'s own `"law"` field never claims a correction-pass
  restoration — only "round-2 move mapping."
- `2026-09-14` (commit `5087c0f19`, `BOOMALOPE_CUT_EVERYWHERE_1`) — flags this
  exact landmine and defers it to this item.

## verdict: UNAMBIGUOUS — no ruling ever restored GR_Boomsnake
No commit, card, or design document at any point states a decision to keep
or restore `GR_Boomsnake` after the boom-family cut. The only "later" event
touching it is a **mechanical, blind re-application** (`ROSTER_MOVE_APPLY_1`)
of a decision made *before* the cut, which the same day's own design record
(`biome_findings.md`) had already voided *hours earlier*. The "GR_ correction
pass" the task brief's premise cites as a restoration is a real phrase, but
it belongs to a different creature (`GR_Mantistanis`) in the same roster
file — an adjacency mixup in downstream citations, not a real ruling. This is
the identical landmine pattern already found and fixed for Boomalope in
`BOOMALOPE_CUT_EVERYWHERE_1`: a stale pre-cut roster/wiring artifact that
outlived the cut it should have been reconciled against.

**The boom-family cut stands; the roster and wiring were wrong.** Fixed to
match:
- `design/Jawa/worldbuilding/biomes/rosters/the_pyrelands.json`: removed the
  `GR_Boomsnake` fauna row (last entry in the `fauna` array); added an
  eviction entry (`"disposition": "cut:BOOM_FAMILY_CUT_1 (BOOMSNAKE_CUT_CONFLICT_1,
  2026-09-14)"`) citing this timeline, right after the Boomalope eviction row.
- `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml`: removed
  `<GR_Boomsnake>0.5</GR_Boomsnake>` from the Vanilla Genetics Expanded
  `PatchOperationAdd` block; updated the header's roster count (14→13
  animals, sum 4.21→3.71), the Vanilla Genetics Expanded roster-and-
  verification prose (dropped the `GR_Boomsnake` citation line), the
  LEFT-OUT block, and added a dated note mirroring the 2026-09-14
  `BOOMALOPE_CUT_EVERYWHERE_1` note above it.
- `infrastructure/state/items/PYRELANDS_FAUNA_WIRING_1.md`: added a matching
  status note and corrected its own EXPECT list (14→13 entries, dropped
  `GR_Boomsnake`, added it to the NOT-expected list) so the next live
  verification doesn't go looking for a cut animal — same fix as
  `BOOMALOPE_CUT_EVERYWHERE_1` made for that file on Boomalope.

**Cherry Picker cut files themselves are UNCHANGED** — `ThingDef/GR_Boomsnake`
stays cut in both `deployed/config/v1_freeze/Mod_3521312241_Mod_CherryPicker.xml`
and `infrastructure/state/cherrypicker/CherryPicker.SHIP.xml` (this was
never the wrong side of the conflict). No `PawnKindDef/GR_Boomsnake` cut was
added either, per `BOOMFAMILY_PAWNKIND_CUTS_1`'s explicit exclusion — leaving
that as a live open question is now moot since the roster/wiring fix removes
the only path anything would spawn it, but the PawnKindDef cut itself is
still owed if the owner wants full-set parity with the other 14 boom-family
creatures; not added here since it wasn't part of what this item's timeline
work justified doing unprompted.

## fallout — same file, same day
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml`'s edit is the
only live-game-facing wiring anywhere for `GR_Boomsnake`; grepped `src/` for
any other reference — none found.

## verify (owed on next deploy-authorized/bridge session)
`validate_patch.py` (no `--defs`, offline this pass) → `WildAnimals_Pyrelands.xml`
OK, 0 errors, 0 warnings. A bridge def-read of `RM_FE_Pyrelands` wildAnimals
should show 13 entries and NOT `GR_Boomsnake` once the game is restarted on a
mod list matching the live def dump (same caveat `PYRELANDS_FAUNA_WIRING_1`
already carries) — live spawn count on the current running map is a separate,
already-placed fact this item does not retroactively undo (offline pass,
no bridge).
