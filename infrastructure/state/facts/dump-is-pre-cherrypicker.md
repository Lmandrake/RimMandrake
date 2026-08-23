# The def dump is captured BEFORE Cherry Picker removes anything

🔴 **Measured 2026-08-23 by DECIDE, after the owner asked why animals he had already cut were
still in an art review sheet. He was right; the sheet was wrong.** Filed as
`DUMP_DERIVED_SHEETS_SHOW_CUT_1` for REP — this file holds the evidence.


🔴 **OWNER, 2026-08-23, reviewing the creature art sheet:** *"I had really thought I had already
removed all of these terrestrial animals somewhere already."*

⭐ **He had. The sheet was wrong, not his memory.**

**Measured, three ways:**

| | |
|---|---|
| Cherry Picker kill list | **1,289** `ThingDef` entries |
| of those, still present in `defs.sqlite` | 🔴 **1,162 — 90%** |
| `Player.log` at the last load | `[Cherry Picker] The database was processed in 00.73 seconds…` then **1,209 defs removed**, including `ThingDef/Cat`, `ThingDef/YorkshireTerrier`, `ThingDef/Alphabeaver`, `ThingDef/BlackBear` |

⇒ 🔑 **The def dump is captured BEFORE Cherry Picker removes anything.** A cut that worked is
**PRESENT** in the dump. The dump cannot answer "is this cut" in either direction.

**What that costs.** Every census, count, roster and **contact sheet** built from the dump —
which is nearly all of them in this repo — silently includes content the running game does not
have. The owner spent a review pass judging animals that no longer exist, and asked a question
that read as a memory failure and was actually an instrument failure.

⛔ **`rimworld-content-moderation` asserted the OPPOSITE** — *"the def dump is the post-removal
state; a cut that worked is ABSENT."* Never measured, reasoned from how Cherry Picker works.
Corrected in place 2026-08-23 with the old text quoted so it is not re-derived.

## The fix
**Filter every dump-derived roster against the kill list before showing it to a human**, and say
in the artifact how many rows were suppressed. The kill list is at
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_3521312241_Mod_CherryPicker.xml`
(repo copy: `deployed/config/v1_freeze/`).

⭐ **Better, if cheap: parse `Player.log`'s removal block instead.** That is runtime truth rather
than a config that may not have been loaded yet. One regex: `^\s*-\s*(\w+)/([^,\s]+),?$` after
the `was processed in` line.

**Known consumers to fix or flag:** `animal_contact_sheet.py`, `animal_inventory.py`,
`def_inventory.py`, `creature_size_review.html`, and anything else projecting over the dump.
⚠️ Not urgent for `plant_pool.csv` / `biome_flora.py` — **checked 2026-08-23: 0 of the 604
assigned plants are on the kill list.**

## verify
Pick a def the log says was removed (`ThingDef/Cat`). It must be absent from any sheet or
census shown to a human, and present in `defs.sqlite`. **Both, simultaneously — that pair IS
the bug.**

## criteria
- [ ] Dump-derived rosters filter against the kill list, or against the log's removal block.
- [ ] Each such artifact states how many rows it suppressed.

## Watch out
⚠️ **`measure` and `defs.sqlite` inherit this.** A `measure count ThingDef` is a count of what
the dump holds, not of what the game runs. That is not wrong — it is answering a different
question — but nothing currently says which question.
⛔ **Do not "fix" it by re-capturing the dump later in load.** The dump's job is the authored
def set; the kill list's job is what survives. Two questions, two instruments.
