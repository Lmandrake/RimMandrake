# Prompts — how a reviewer run is assembled (do not run from here; the race harness does)

Per subject: `00_preamble.md` + the class prompt for the card's `class` + the subject's `card.md` + its images
(`page_facings.png`, `page_flight.png` if present, every `<letter>_scale_full.png`). Optionally the class contact
sheet from `bundle/contact/` for whole-sheet calibration.

| card class | class prompt |
|---|---|
| flora/ground_cover | `class_flora_ground_cover.md` |
| flora/bush | `class_flora_bush.md` |
| flora/tree | `class_flora_tree.md` |
| flora/special | `class_flora_special.md` |
| fauna/walker, fauna/walker_pack | `class_fauna_walker.md` |
| fauna/flyer | `class_fauna_flyer.md` |
| fauna/swimmer, fauna/amphibious | `class_fauna_swimmer.md` |
| item/catch | `class_item_catch.md` |

Every owner quote cited in these prompts comes from a sheet OTHER than the one under test (Weeping Stones,
2026-10-10), so no prompt leaks an answer. Sources: art ledger owner events
(`infrastructure/state/art/events/*.jsonl`), `skills/rimworld-sprite-facings` (2026-09-15 sitting),
`design/RimMandrake/art_judge_brief.md`.
