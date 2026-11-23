# The def dump still holds most defs that Cherry Picker cut

The file name says "pre-cherrypicker". That explanation is wrong (corrected 2026-11-23). The name stays, because code
cites the path.

**Measured 2026-11-23.** In one `Player.log` (the game ArchBig on Archmagi, 314 mods), the Cherry Picker block is at line 1279 and the dump
starts at line 2817. So Cherry Picker runs FIRST. `RemoveDef` in the 1.6 `CherryPicker.dll` (decompiled with `ilspycmd`)
does two different things:

| what Cherry Picker does | types | of the defs that the log reports removed, still in capture `2026-11-23T19-47-11Z` |
|---|---|---|
| **deletes the def** (`DefDatabase<T>.Remove`) | `GeneDef`, `XenotypeDef`, `BackstoryDef`, `ResearchProjectDef`, `RecipeDef`, `TraitDef`, `HairDef`, `BeardDef`, `TattooDef`, `MemeDef`, `PreceptDef`, `RitualPatternDef`, `DesignationCategoryDef` | 0 of 9 `GeneDef`, 0 of 13 `XenotypeDef`, 0 of 109 `ResearchProjectDef`, 0 of 2 `RecipeDef` |
| **changes fields and leaves the def** | `ThingDef`, `PawnKindDef`, `BiomeDef`, `IncidentDef`, `HediffDef`, `FactionDef`, `AbilityDef` and most others | 397 of 397 `ThingDef`, 19 of 19 `PawnKindDef`, 11 of 11 `BiomeDef`, 9 of 9 `IncidentDef`, 3 of 3 `HediffDef`, 2 of 2 `AbilityDef` |

- The fields that it changes include: `weaponTags`, `apparel.tags`, `tradeability`, `thingCategories`, the commonality of
  the animal in `race/wildBiomes` and in each biome's `wildAnimals` and `pollutionWildAnimals` (set to 0),
  `BiomeDef.implemented` (set to false), and three world-creation fields of a `FactionDef`.
- Cherry Picker does not touch `coastalWildAnimals` (read in the code; not tested in game).
- A `FactionDef` with `maxConfigurableAtWorldCreation` at 0 or below is skipped with no message.
- The practical rule does not change: for a type of the second row, a dump cannot say "is this cut". Use the kill list or
  the log. For a deleted type, PRESENT means that the cut did not work, or that the dump comes from a load whose kill list did not hold the def.

The rest of this file is the record of 2026-08-23 to 2026-09-05. Where it says that the dump comes before Cherry Picker,
the explanation above replaces it. Its measurements stand.

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

⇒ 🔑 **A cut `ThingDef` that worked is PRESENT in the dump.** The dump cannot answer "is this `ThingDef` cut" in either
direction.

**What that costs.**

- Nearly every census, count, roster and **contact sheet** in this repo is built from the dump. Each one silently
  includes content that the running game does not have.
- The owner spent a review pass judging animals that he had already cut. His question read as a memory failure. The failure was
  in the instrument.

⛔ **The skill `rimworld-content-moderation` asserted the OPPOSITE** — *"the def dump is the post-removal state; a cut
that worked is ABSENT."* Nobody measured that claim. Its author reasoned from how Cherry Picker works. The skill was
corrected in place 2026-08-23. The old text is in the skill's `references/history.md`.

## ✅ FIXED for the two contact sheets, 2026-08-27 — `DUMP_DERIVED_SHEETS_SHOW_CUT_1`

- `src/RimMandrake/Utils/cherrypicker.py` is now the ONE reader of the kill list.
- Both `thing_contact_sheet.py` and `animal_contact_sheet.py` filter by default. Both print `Cuts.provenance(suppressed)`.
- ⚠️ **The kill-list numbers of the table above (1,289, 1,162, 1,209) are the 2026-08-23 reading. The list has
  grown since: 1,342 defs as of 2026-08-27.** Read the list. Never use a count that someone wrote down.
- ⛔ On 2026-08-27, eight scripts parsed the settings file with their own regex. The two contact sheets moved; six were
  left. `cherrypick_build.py` still does (2026-11-23). Move each such script onto the module when you touch that script.
- The full record was `infrastructure/state/items/DUMP_DERIVED_SHEETS_SHOW_CUT_1.md`. Commit `55c62c85c6` (2026-08-27)
  deleted that file. Read it with `git show 55c62c85c6^:infrastructure/state/items/DUMP_DERIVED_SHEETS_SHOW_CUT_1.md`.

## The fix

- **Filter every dump-derived roster against the kill list before you show the roster to a human.** Say in the artifact
  how many rows you suppressed.
- The kill list is at
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_3521312241_Mod_CherryPicker.xml`
  (repo copy: `deployed/config/v1_freeze/`).
- **Better, if cheap: read `Player.log`'s removal block instead (`cherrypicker.from_log()`).** That block is runtime truth. The kill list is a
  config, and the game may not have loaded it yet. One regex reads the lines, except a `- FAILED:` line: `^\s*-\s*(\w+)/([^,\s]+),?$` after the
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

## ⚠️ REFINED 2026-09-05 — the def stays, some LIST FIELDS do not

Measured during the build of the weapon register (764 weapons, full 595-mod stack):

- All **177** weapons that Cherry Picker cut carry an **empty `weaponTags`** in the dump. **No tagged weapon is cut.**
  The match is 177/177, in BOTH directions.
- So the **def** of a cut weapon is still in the dump. So cut things still appear in sheets.
- But some **list fields have been stripped** in the dump. The def of a cut weapon is present, and its
  `weaponTags` list is empty.

⇒ A list field can be empty
*because* the thing was cut. That reads identically to a def that never had the list. `cherrypicker.py` remains the ONLY
authority on cut state. A dump field is at best corroboration.

⚠️ So "empty `weaponTags`" cannot by itself prove a content bug. See the 56 live, uncut weapons that genuinely have no
tags (`WEAPONS_NO_TAGS_ORPHANS_1`).
