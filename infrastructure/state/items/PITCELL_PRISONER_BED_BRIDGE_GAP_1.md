## STATUS 2026-09-10 ~01:00: live-proof attempt made — the GAME crashed mid quicktest-map-gen before `jawa/set_bed_owner_type` could even be called. Still not closeable.

Bridge was FREE, campaign was up (5 colonists, stable, per handoff note). Took the
bridge, called `rimworld/go_to_main_menu` then `rimworld/start_debug_game_ready`
per the `rimworld-debug-testing` skill (quicktest, not the real campaign). The
`start_debug_game_ready` call exceeded the 30 s client timeout as the skill warns
it will — did not retry it, opened a fresh connection and polled `jawa/list_pawns`
instead. `Player.log` shows `start_debug_game_ready` DID begin real work (a fresh
world tile 110145, "River & RiverTerrain" landform, ore-generation loop, research
satiation ticks from mods) — then the log **stops cold mid map-gen**, no exception,
no `ConfigErrors`, no shutdown line, nothing. `tasklist.exe` confirms
`RimWorldWin64.exe` is no longer running. This is a silent full-process crash
during quicktest world/map generation **on the live ~600-mod list**, not on the
13-mod minimal list the debug-testing skill's timings assume — matches this
session's stated context ("multiple crash incidents tonight from bridge-driving
quicktests"). Ran bare `./game`, which measured NOT RUNNING and corrected the
ledger from the stale `UP` it held. Released the bridge (`bridge release`).

**`jawa/set_bed_owner_type` itself was never reached** — the crash happened
during `start_debug_game_ready`'s own map generation, one step before a bed
could be spawned. This session settles NOTHING about the tool's correctness; it
only reconfirms the environment's crash-on-quicktest problem on the full mod
list. Did not attempt a cold-load restart to retry: that is expensive-list
ceremony (~15 min) and, given the crash pattern already flagged for tonight, a
second attempt without changing anything would risk repeating it for no new
information. Left `doing`, not closed, not dropped — the tool is unverified
either way, exactly as before this pass, plus the crash symptom is now on
record.

**For whoever picks this up next:** either (a) run this same live-proof but on
the 3-mod or minimal-list bridge tier (`modset_builder.py --tier bridge`) where
quicktest map-gen is seconds not a hang risk — proves the mechanism, not the
full-list interaction — or (b) retry on the full list only after a deliberate
cold-load slot, watching `/proc/loadavg` and Player.log live during
`start_debug_game_ready` instead of polling blind. The original criteria and
verify checklist below are unchanged; only the tool's own correctness remains
open, since it was never invoked this pass.

---

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
