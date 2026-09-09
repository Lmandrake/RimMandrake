## STATUS 2026-09-09: tool built and committed, blocked on a live-proof pass — not closeable right now

The companion tool this item asked for exists on disk and is already committed:
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchBedTools.cs`, tool
`jawa/set_bed_owner_type` (writes `Building_Bed.ForOwnerType` directly, bypassing the
in-game `Command_Toggle` gizmo). Commit `67ed9f07`. A `build.py --gm` pass confirmed 0
errors and the tool present among 317 tools in the built DLL.

**What is NOT done:** the criteria below requires the live proof — spawn a bed, call
`jawa/set_bed_owner_type` on it, fire vanilla "Add Prisoner", confirm a prisoner actually
lands on a quicktest map. A 2026-09-09 ~14:27 note on `BLUE_DESERT_WORLD_SWITCH_1` records
that this DLL (with the PitCell bed tool) was deployed live in that session's restart, but
explicitly says it was "not individually verified live yet."

**Why this session did not attempt that proof:** invoked mid-crash-reboot on the full
~600-mod list, explicitly instructed not to attempt live bridge calls until the game is
confirmed reachable. Checked `rimflow bridge who` — held by FOUNDRY for a different item
(`BIOME_ENRICHMENT_POISON_FOREST_1`), not free regardless. No live-proof attempt made this
session; nothing new to verify or close.

**For whoever picks this up next:** confirm bridge reachable, confirm holder is not mid-use
on other work, spawn a bed on a quicktest map, call `jawa/set_bed_owner_type` to force
`ForOwnerType=Prisoner`, fire the vanilla Add Prisoner debug action, confirm via
`jawa/list_pawns` (or equivalent) that a prisoner actually landed. On success this item and
`RIMMANDRAKE_PITS_BUILD_1`'s last open verify line both close.

---

## spec (from the `file` event, RIMMANDRAKE_PITS_BUILD_1, 2026-09-07)

PitCell prisoner-intake gizmos (`RM_PlaceInPitCell`, `RM_FeedCaptive`, assign-nearest,
toggle-gate) could not be exercised end-to-end from the bridge because nothing could get an
eligible prisoner onto a fresh map: `DebugToolsPawns.AddGuest(GuestStatus.Prisoner)`
(vanilla "Add Prisoner" debug action) only fires if a `Building_Bed` with
`ForPrisoners==true` already exists on the map, and `Building_Bed.ForPrisoners` is a public
settable property reachable only via its in-game `Command_Toggle` gizmo — no reflective
setter existed anywhere on the `jawa/` or `rimworld/` bridge surface, and no standalone
debug-menu leaf set it either. Root-caused 2026-09-06 during `RIMMANDRAKE_PITS_BUILD_1`'s
live-proof pass; gate/toggle/report/feed hooks themselves all work once a prisoner exists.

## criteria

A new companion tool (delivered: `jawa/set_bed_owner_type`) lets a bridge session put an
eligible prisoner on a quicktest map without a human clicking anything, then PitCell
assign/place/feed can finally be exercised live and this item and
`RIMMANDRAKE_PITS_BUILD_1`'s last open verify line both close.

## verify

- [x] Tool exists, compiles clean, appears in the built DLL's tool list.
- [ ] Live: bed spawned, `ForOwnerType` force-set via the tool, Add Prisoner fires, a
      prisoner is actually on the map afterward (checked by listing pawns, not by the
      placement log — a net count can hide a wash).
