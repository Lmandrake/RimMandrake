# Lantern Deeps flora/fauna review sheet — build report

**Sheet:** `Transient/deeps_flora_fauna_review_2026-09-18.html` (id `deeps_flora_fauna_review_2026-09-18`)
**Decisions:** `Transient/deeps_flora_fauna_review_2026-09-18.decisions.json` (posture `blacklist`)
**Thumbs:** `Transient/deeps_review_thumbs_2026-09-18/` — 28 PNGs, 160px max, alpha kept
**Generator:** `src/RimUtinni/LanternDeeps/build_species_sheet.py` (rerunnable; refuses to overwrite
a decisions file carrying `savedBy`/nonzero `writeCount`)

## Row counts

- **Deeps flora: 12** = every `RUT_LanternDeeps.wildPlants` entry (measured from the biome def)
  = every non-abstract Plant ThingDef under `LanternDeeps/Defs/`. `DeepFloraPlanter.cs` confirms
  the planter reads `map.Biome.wildPlants` directly — no separate species table exists. 10
  `owned`; 2 `approved — not yet wired` (TwitchingPuffer: facts-PASS, no owner decision recorded
  anywhere; PrennaLace: facts-PASS AND owner recorded **keep** on all 4 renders in
  `deeps_art_review_2026-09-18.decisions.json`) — both render from `_artsrc/<job>/` since their
  `Textures/` folders are empty. 0 missing.
- **Deeps fauna: 16** = every `RUT_LanternDeeps.wildAnimals` entry (no LanternDeeps-owned race
  ThingDef exists, no patch elsewhere in `src/` names this biome — wildAnimals IS the cast). All
  16 are RSW_ ports in one file. 16 `donor` (SWBestiary `_south.png`); 0 missing. **No rows with
  no art found anywhere.**

**Excluded:** the 4 lanternstone rock formations are Buildings, not Plants, not in `wildPlants` —
out per the task's flora definition. The sowable lanternstone (a real Plant) IS included, and
shares its grown texPath with the Medium *building* — noted on its row.

## Invented rules (also `CONFIG.invented` on the page)

1. Two groups as above. 2. Rock formations excluded (Buildings). 3. Flora thumbnail = grown-stage
graphic, first alphabetical variant; other stages named in the note. 4. Fauna thumbnail = south
sprite of the PawnKindDef's LAST life stage; a larva/pupa with its own wildAnimals entry gets its
own row from its own stage art. 5. "approved — not yet wired" covers both owner-approved and
facts-PASS-only renders — distinguished in each row's note, not by a 6th chip.

## Gate result

`check_sheet.py … --decisions …` → **0 FAIL · 1 WARN · 33 ok, exit 0**. The WARN ("28 rows
missing from the [decisions] file") is expected: decisions.json starts empty by design, same as
`build_art_sheet.py`'s own output — each row's default lives in the item's `"prefill"` field.
Not run by this subagent: `serve_sheet.py` (parent session serves it, per task rules).
