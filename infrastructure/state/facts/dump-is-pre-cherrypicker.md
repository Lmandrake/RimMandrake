# The def dump is captured BEFORE Cherry Picker removes anything

Cherry Picker is the mod that removes defs while the game loads. Its kill list is the list of defs that it is
configured to remove.

🔴 **Measured 2026-08-23 by DECIDE, after the owner asked why animals he had already cut were still in an art review
sheet. He was right; the sheet was wrong.**

- The defect was filed as `DUMP_DERIVED_SHEETS_SHOW_CUT_1` for REP. This file holds the evidence.
- DECIDE and REP are retired seat names.

🔴 **OWNER, 2026-08-23, reviewing the creature art sheet:** *"I had really thought I had already
removed all of these terrestrial animals somewhere already."*

**He had. The sheet was wrong, not his memory.**

**Measured, three ways:**

| | |
|---|---|
| Cherry Picker kill list | **1,289** `ThingDef` entries |
| of those, still present in `defs.sqlite` | **1,162 — 90%** |
| `Player.log` at the last load | `[Cherry Picker] The database was processed in 00.73 seconds…` then **1,209 defs removed**, including `ThingDef/Cat`, `ThingDef/YorkshireTerrier`, `ThingDef/Alphabeaver`, `ThingDef/BlackBear` |

⇒ 🔑 **The def dump is captured BEFORE Cherry Picker removes anything.** A cut that worked is **PRESENT** in the dump.
The dump cannot answer "is this cut" in either direction.

**What that costs.**

- Nearly every census, count, roster and **contact sheet** in this repo is built from the dump. Each one silently
  includes content that the running game does not have.
- The owner spent a review pass judging animals that no longer exist. His question read as a memory failure. The failure was
  in the instrument.

⛔ **The skill `rimworld-content-moderation` asserted the OPPOSITE** — *"the def dump is the post-removal state; a cut
that worked is ABSENT."* Nobody measured that claim. Its author reasoned from how Cherry Picker works. The skill was
corrected in place 2026-08-23. The old text stays there as a quote, so that nobody derives it again.

## ✅ FIXED for the two contact sheets, 2026-08-27 — `DUMP_DERIVED_SHEETS_SHOW_CUT_1`

- `src/RimMandrake/Utils/cherrypicker.py` is now the ONE reader of the kill list.
- Both `thing_contact_sheet.py` and `animal_contact_sheet.py` filter by default. Both print `Cuts.provenance(suppressed)`.
- ⚠️ **The kill-list numbers of the table above (1,289, 1,162, 1,209) are the 2026-08-23 reading. The list has
  grown since: 1,342 defs as of 2026-08-27.** Read the list. Never use a count that someone wrote down.
- ⛔ Six other scripts still parse the settings file with their own regex. Move each script onto the module when you
  touch that script.
- The full record was `infrastructure/state/items/DUMP_DERIVED_SHEETS_SHOW_CUT_1.md`. Commit `55c62c85c6` (2026-08-27)
  deleted that file. Read it with `git show 55c62c85c6^:infrastructure/state/items/DUMP_DERIVED_SHEETS_SHOW_CUT_1.md`.

## The fix

- **Filter every dump-derived roster against the kill list before you show the roster to a human.** Say in the artifact
  how many rows you suppressed.
- The kill list is at
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_3521312241_Mod_CherryPicker.xml`
  (repo copy: `deployed/config/v1_freeze/`).
- **Better, if cheap: parse `Player.log`'s removal block instead.** That block is runtime truth. The kill list is a
  config, and the game may not have loaded it yet. One regex does it: `^\s*-\s*(\w+)/([^,\s]+),?$` after the
  `was processed in` line.
- **Known consumers to fix or flag:** `animal_contact_sheet.py`, `animal_inventory.py`, `def_inventory.py`,
  `creature_size_review.html`, and anything else that projects over the dump.
- ⚠️ The fix is not urgent for `plant_pool.csv` / `biome_flora.py`. **Checked 2026-08-23: 0 of the 604 assigned plants
  are on the kill list.**

## verify
Pick a def that the log says was removed (`ThingDef/Cat`). The def must be absent from any sheet or census that you show
to a human. The same def must be present in `defs.sqlite`. **Both, simultaneously — that pair IS the bug.**

## criteria
- [ ] Dump-derived rosters filter against the kill list, or against the log's removal block.
- [ ] Each such artifact states how many rows it suppressed.

## Watch out

- ⚠️ **`measure` and `defs.sqlite` inherit this.** A `measure count ThingDef` counts what the dump holds, not what the
  game runs. That count is not wrong. That count answers a different question. But nothing currently says which question.
- ⛔ **Do not "fix" it by re-capturing the dump later in load.** The dump's job is the authored def set. The kill list's
  job is what survives. Two questions, two instruments.

---

## ⚠️ REFINED 2026-09-05 — true for DEFS, NOT uniformly true for LIST FIELDS

Measured during the build of the weapon register (764 weapons, full 595-mod stack):

- All **177** weapons that Cherry Picker cut carry an **empty `weaponTags`** in the dump. **No tagged weapon is cut.**
  The match is 177/177, in BOTH directions.
- So the dump is pre-Cherry-Picker about whether a **def exists**. The original finding stands, and it is why cut things
  still appear in sheets.
- But some **list fields have already been stripped** in the dump. The def of a cut weapon is present, and its
  `weaponTags` list is gone.

⇒ Do NOT read "the dump is pre-Cherry-Picker" as "every field in the dump is pre-cut." A list field can be empty
*because* the thing was cut. That reads identically to a def that never had the list. `cherrypicker.py` remains the ONLY
authority on cut state. A dump field is at best corroboration.

⚠️ So "empty `weaponTags`" cannot by itself prove a content bug. See the 56 live, uncut weapons that genuinely have no
tags (`WEAPONS_NO_TAGS_ORPHANS_1`).
