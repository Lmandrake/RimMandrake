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
