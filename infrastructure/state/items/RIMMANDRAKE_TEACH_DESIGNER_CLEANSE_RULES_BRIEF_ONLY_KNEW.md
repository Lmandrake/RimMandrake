# RIMMANDRAKE_TEACH_DESIGNER_CLEANSE_RULES_BRIEF_ONLY_KNEW

FINDING (measured 2026-11-17 7:55 PM PST, git): the Designer's standing instructions, `src/RimMandrake/rimflow/roles/designer.md`, last changed 2026-11-16 6:48 PM PST (76dd23d59d, spend hiding), before the Codex cleanse began 11:07 PM PST that night. The rules the cleanse enforces live only in `src/RimMandrake/rimflow/roles/designer_cleanse.md` and `designer_cleanse.py`. A new concept designed by the ordinary Designer is still written under the old rules and can lock another 64-bar first version. The parent item's scope is the cleanse of existing concepts; nothing in it edits `designer.md`.

FIX: fold into `designer.md` (and any stage-3/4 text the Designer reads) only what the owner has already ruled by card 2026-11-17 (parent item, "What the card said"):
- a biome mod's first version (0.1.0) is land, life (terrain, plants, animals, weather) and exactly ONE signature mechanic; everything else moves out;
- an extra ruled out of the first version is written up for the next version and its code switched off;
- the checker after writing is one whole-mod check (conflicting bars, promised mechanics with no spec, scenes with the main mechanic off, tuning numbers), one round of fixes, then lock.
NOT in scope: the "definition of a bar" in `design/specs/2026-11-16-designer-cleanse-and-bar-definition.md`, still marked proposed. No rule is restated twice: `designer_cleanse.md` points at `designer.md` for whatever moves.

Acceptance test: not yet drafted (owed at launch, before any builder starts): a case file that reads `designer.md` and fails on base 0fd6e764c7 for each of the three rules above, plus a check that `designer_cleanse.md` does not restate them. Not launched: Codex runway reads 0.41 with the cleanse fleet and the judge ticket's round 4 running (2026-11-17 7:55 PM PST); launch when the fleet ends.
