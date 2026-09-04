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

## criteria

Written by BENCH 2026-09-02 from this item's own `## verify`, which already stated
the closing conditions — the section was simply missing, and `next` was flagging the
item THIN for it. Nothing here is a new decision; every ruling is already canon
(`research_tree.shape_ruled` / `taxonomy_ruled` / `sitting_ruled` / `chains_ruled` /
`tech_gating_ruled`).

1. **Coverage, not a sample.** The manifest holds a row for all 515 research defs —
   each either placed (tab + tier) or carrying an explicit refusal reason. A row that
   is merely absent is a failure, never a pass: assert coverage against the inventory
   rather than reading a healthy-looking count.
2. **The validator passes against the RESOLVED post-RR dump**, whose fingerprint
   matches the live mod set — not raw mod XML, and not a dump whose currency is
   assumed. `cherrypicker.py` is the reader for what has been cut, because a Cherry
   Picker cut is invisible to the dump.
3. **The owner has reviewed the DELTA sheet** (ruled 2026-09-04 by card: "Delta
   sheet only"). The frozen deck round 3 (2026-09-04) discharged tree placement;
   the remaining pass covers only what the deck never showed him — the
   faction-held rows' holders, the Rites/Antiquities rows, and every row whose
   current fate differs from the 09-03 prefill. Still his pass alone; it cannot
   be delegated or inferred from a clean validator run.
4. **The retag is live with no orphaned unlocks** — every unlock still resolves after
   the retag, and the rows alive with empty unlock caches are exactly the prep §1
   allowlist — 30 as of 2026-09-04 (the original 22 plus 8 hand-verified additions,
   each with evidence in prep §1 "+8 more") — not a set that grew silently.
5. **No defName was renamed**, anywhere, by anything.

The three execution children (RESEARCH_VALIDATOR_BUILD_1 · RESEARCH_MANIFEST_DRAFT_1 ·
TECHPRINT_FACTION_GATING_1, all FOUNDRY) close on their own criteria; this parent
closes only when all five conditions above hold together.

## Watch out

- Research Reinvented is the substrate (ruled) — every validation runs against
  the RESOLVED post-RR dump, never raw XML; 448/515 rows carry RR techprints.
- Cherry Picker cuts are invisible to the dump; cherrypicker.py is the reader.
- 22 rows are alive with empty unlock caches (prep §1 allowlist).
- Nothing renames a defName, ever.

## Rulings 2026-09-04 (owner, by question card)

1. **techLevel retag: BUILD.** The 185 tier-vs-techLevel mismatches get a def
   patch (tier grammar's mapping); cost multiplier consequences accepted.
2. **Mechanitor hardware: LEAVE AS LOOT.** No Cherry Picker cuts for mechlinks/
   subcores/gestators — they drop and trade as flavor junk the Jawa can sell;
   they unlock nothing (research is cut).
3. **GravBionics: Rust Cathedral boon-gate**, same as GravWeapon — all personal
   gravtech is Rataka boon-tech (recorded on the manifest row).
4. **The Rites: AUTHOR as real rows** — 5-row locked tree, revealed-not-bought;
   the reveal mechanism is later ship-memory work.
