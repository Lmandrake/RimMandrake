# RIMMANDRAKE_TEACH_DESIGNER_CLEANSE_RULES_BRIEF_ONLY_KNEW

FINDING (measured 2026-11-17 7:55 PM PST, git): the Designer's standing instructions, `src/RimMandrake/rimflow/roles/designer.md`, last changed 2026-11-16 6:48 PM PST (76dd23d59d, spend hiding), before the Codex cleanse began 11:07 PM PST that night. The rules the cleanse enforces live only in `src/RimMandrake/rimflow/roles/designer_cleanse.md` and `designer_cleanse.py`. A new concept designed by the ordinary Designer is still written under the old rules and can lock another 64-bar first version. The parent item's scope is the cleanse of existing concepts; nothing in it edits `designer.md`.

FIX: fold into `designer.md` (and any stage-3/4 text the Designer reads) only what the owner has already ruled by card 2026-11-17 (parent item, "What the card said"):
- a biome mod's first version (0.1.0) is land, life (terrain, plants, animals, weather) and exactly ONE signature mechanic; everything else moves out;
- an extra ruled out of the first version is written up for the next version and its code switched off;
- the checker after writing is one whole-mod check (conflicting bars, promised mechanics with no spec, scenes with the main mechanic off, tuning numbers), one round of fixes, then lock.
NOT in scope: the "definition of a bar" in `design/specs/2026-11-16-designer-cleanse-and-bar-definition.md`, still marked proposed. No rule is restated twice: `designer_cleanse.md` points at `designer.md` for whatever moves.

Acceptance test: not yet drafted (owed at launch, before any builder starts): a case file that reads `designer.md` and fails on base 0fd6e764c7 for each of the three rules above, plus a check that `designer_cleanse.md` does not restate them. Not launched: Codex runway reads 0.41 with the cleanse fleet and the judge ticket's round 4 running (2026-11-17 7:55 PM PST); launch when the fleet ends.

## done 2026-11-19 (detached helper of the Conductor, item RIMMANDRAKE_READY_PIPELINE_FOR_WRECKED_MACHINES_HE_HOLDS_GO)
- `roles/designer.md` (in every stage 0-5 packet of `designer_manifest.json`) now carries "What a first version may
  contain" and "The fate of an extra" word for word from `designer_cleanse.md`, and his third answer with the truth
  beside it: stage 4 still ends on the exam and stage 5 on coverage (the launcher enforces both; the card was about a
  cleansed design). The text is COPIED, not moved: the cleanse launcher pastes `designer_cleanse.md` alone, so moving it
  would strip the cleanse brief. `selftest_designer_first_version_rules.py` (in `publish_tree_checks.json`) keeps the
  two copies equal.
- Lane F's two objections (note 2026-11-18): rule 3 is stated without lifting the stage gates; Pyrelands and every
  version locked before 2026-11-17 keep their scope (a Divergent change never moves the current bars), so no Write run
  rewrites a locked version.
- Open for the Conductor: whether the third answer should also replace stages 4 and 5 for ordinary (non-cleanse)
  Designer runs. No ticket filed; it is a design question, not a defect.

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_designer_first_version_rules.py` (16 checks): 14 FAIL on
b2bdcaafc8, 16 PASS after. Mutations watched red: one word edited in the copy (6 FAIL), "still" gate line removed (2 FAIL).
