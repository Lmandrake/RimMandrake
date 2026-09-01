# RESEARCH_TREE_NORMALIZATION_1 — full-game research normalization

Parent item. The RULING PHASE IS COMPLETE (all canon: `research_tree.shape_ruled`
/ `taxonomy_ruled` / `sitting_ruled` / `chains_ruled` / `tech_gating_ruled`);
this stays open to track execution and the one remaining owner pass.

## spec

Layer stack: `design/Jawa/research_normalization_principles.md` (why) →
`design/Jawa/research_tree_prep.md` (census) → `design/Jawa/research_tree_taxonomy.md`
(tabs/tiers/manifest/validator/migration + every sitting ruling in §6–7).
Execution children: RESEARCH_VALIDATOR_BUILD_1 · RESEARCH_MANIFEST_DRAFT_1 ·
TECHPRINT_FACTION_GATING_1 (all FOUNDRY). SONIC_WEAPONS_EXPANSION_1 is the
ruled creative follow-up, sequenced after the manifest lands.

## verify

Closes when: the manifest (all 515 rows, coverage-or-refuse) has passed the
validator, the owner has reviewed the prefilled manifest as a review sheet
(the last owner pass), and the retag is live with no orphaned unlocks.

## Watch out

- Research Reinvented is the substrate (ruled) — every validation runs against
  the RESOLVED post-RR dump, never raw XML; 448/515 rows carry RR techprints.
- Cherry Picker cuts are invisible to the dump; cherrypicker.py is the reader.
- 22 rows are alive with empty unlock caches (prep §1 allowlist).
- Nothing renames a defName, ever.
