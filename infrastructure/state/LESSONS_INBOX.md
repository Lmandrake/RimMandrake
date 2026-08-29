# LESSONS INBOX

One line per lesson, appended by any window at any time — especially at reboot.
Claim only, no essay: `sprite facings: generate individually, composite sheets
drift — seen twice`. **No skill, memory, or doctrine file is edited at reboot
time**; a fresh-context curation session (owner says "curation pass") drains this
file into the right skills, merging rather than appending, and empties it.

---
- RETRACTED-and-corrected (2026-08-27, same session): the 'jawa/list_things serves stale rows' lesson was my own read bug - rimworld/get_cell_info nests its payload under 'cell', so r.get('things') reads None and 'empty' was never measured. Read r['cell']['things'].
- destroy_batch and jawa/damage both report success on hitPoints:-1 buildings (e.g. AncientHeatVent) and change NOTHING; the working route is execute_debug_action 'Actions\T: Destroy' with x/z, then verify via get_cell_info's cell.things.
- jawa/set_substructure_batch action=set reports success + cellsFailedVerify 0 while silently skipping every cell whose floor already wrote under-terrain — read foundation back; recovery is set_terrain_layer layer=removeTop, then set, then re-floor (2026-08-28, gravship engine room).
- jawa/destroy_batch on stuffed walls drops full material leavings as ground items (37 MegaBone hull cells -> 217 Steel stacks): a silent colony-wealth injection that skews raid points — sweep items after any structural demolition (2026-08-28).
- zsh does NOT word-split unquoted $VAR (a $CLI reassign loop failed 30/30 silently under >/dev/null); use explicit commands or arrays in loops — seen once, cost one redo
- queue_lint counts a reassign as a claim, so reassigning an item you filed burns your filer-exemption; a hook that can't see WHO is editing needs the payload session_id, not env — fixed 2026-08-28, generalises to any identity-checking hook
- a known-answer calibration (rimplace contract) rots silently when the source legitimately grows a parameter; adding a companion tool param means updating the calibration in the same commit — cost one day of UNMEASURED contract checks
- jawa/clear_ui does not close MainTabWindow_Menu (it is not a debug window): check get_ui_layout surfaces and close with rimworld/close_window before screenshots (2026-08-28).
- CompFacility links form ONCE at the facility's spawn and never retry: a gravship thruster whose exclusion zone touches substructure at spawn is permanently unlinked even after the zone clears — rebuild the thing, don't wait (2026-08-28).
- The build_batch later-op-destroys trap also kills PRE-EXISTING buildings: shrine dressing silently destroyed the campaign's PilotConsole; after building near existing structures, re-census the named defs that were already there (2026-08-28).
- Vanilla's gravship LANDING chain (captures + camera-pan callbacks) can wedge forever under bridge automation, before the ship is placed; the marker is consumed and only a save reload recovers — make the save first, always (2026-08-28).
- A DLL byte-scan guard must match LENGTH-PREFIXED tool names: description strings merely MENTIONING jawa/fire_incident blocked every default companion deploy until 2026-08-28; calibrate such scans against a known answer in BOTH directions (build.py verify_gm_gate carries the encoding argument).
- deploy_custom_mods.py answers "in sync" for MODS only — the JawaBench companion (no packageId) deploys via bridgetools/build.py, and "everything in sync" from the mod tool says nothing about it.
- rimflow subcommands take --to for their target (reassign --to FOUNDRY, needs --to bridge); bare positionals are refused.
- refresh.py called defs.sqlite "current" while its provenance named a capture retention had already PRUNED (built 08-23, newest 08-29): DumpDB.stale checks the mod fingerprint, not whether its source capture still exists — rebuild whenever provenance names a missing capture. (BENCH 2026-08-29)
- The frozen OFFICIAL capture can be deleted out from under the registry with nothing noticing until refresh.py says REPLACED: the registry entry is not a backup, and .keep only protects while it exists — verify the frozen capture DIRECTORY exists at session start, not just the registry line. (BENCH 2026-08-29)
- tool_surface's phantom names (a tool name quoted in another tool's description) make any ==-count census fail forever: subtract a named PHANTOMS set, never widen the tolerance. (BENCH 2026-08-29)
- Dialog_NodeTree can absorb all input while ignoring its own buttons; get_ui_state/get_ui_layout/click_ui_target unsticks it without a restart (rimbridge traps.md, 2026-08-29)
