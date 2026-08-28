# LESSONS INBOX

One line per lesson, appended by any window at any time — especially at reboot.
Claim only, no essay: `sprite facings: generate individually, composite sheets
drift — seen twice`. **No skill, memory, or doctrine file is edited at reboot
time**; a fresh-context curation session (owner says "curation pass") drains this
file into the right skills, merging rather than appending, and empties it.

---
- RETRACTED-and-corrected (2026-08-27, same session): the 'jawa/list_things serves stale rows' lesson was my own read bug - rimworld/get_cell_info nests its payload under 'cell', so r.get('things') reads None and 'empty' was never measured. Read r['cell']['things'].
- destroy_batch and jawa/damage both report success on hitPoints:-1 buildings (e.g. AncientHeatVent) and change NOTHING; the working route is execute_debug_action 'Actions\T: Destroy' with x/z, then verify via get_cell_info's cell.things.
