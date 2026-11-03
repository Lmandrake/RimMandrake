# Biome group-size walk (`BIOME_GROUP_SIZE_WALK_1`, 2026-11-03)

The owner, 2026-10-08: *"walk through the custom creatures we've made per biome on its review sheet and assign the
typical group size that appears when they do. I'm not even sure we've seen such numbers."* Delegated as a design call
(Conductor triage 2026-10-29; owner kept it with agents by card 2026-10-31). Every number here is PROVISIONAL,
`src: delegated:design (BIOME_GROUP_SIZE_WALK_1)`, and listed in his digest.

**Scope.** Every custom creature (PawnKindDef `RM_`/`RSW_`/`RUT_`) on the roster of a live biome: the 26 `RM_` biomes
of the painted world plus `RUT_Umbra` (`biome_rulings.md`). A roster is the BiomeDef's own `<wildAnimals>` plus every
patch Add/Replace on it, then ParentName inheritance. `RM_SeabedFloor_*` and the frozen `RUT_` twins are not walked.

**Files.**

- `biome_group_sizes.csv`: one row per (biome, creature): today's value, the canon herd ruling, the maker draft, the
  judge verdict and the size set. `wildGroupSize` lives on the PawnKindDef, so a creature has one size in every biome.
- `judge/`: the brief, the six prompts and answers, the maker draft and the rules that drafted it. Judge record:
  `infrastructure/state/delegated/2026-11-03/BIOME_GROUP_SIZE_WALK_1.json`.

**How it was decided.** A rule draft (`judge/maker_draft_rules.py`) proposed a size per creature. GPT (`gpt_consult
--lockdown`) judged every row from its description, body size, herd and predator flags and the canon ruling
(`design/RimStarWars/canon_herd_lore/canon_herd_rulings.md`): KEEP or SET. The judge's value stands. The exception is
seven creatures whose size a committed spec already states (verdict `SPEC_PINNED`, spec path in the reason): the walk
does not reopen another item's design. One of them, `RM_Ullai` 8~20, is an owner card ruling.

**Tools.** `python3 src/RimMandrake/Utils/biome_group_sizes.py measure | check | apply`.
`src/RimMandrake/Utils/selftest_biome_group_sizes.py` proves the defs and this table agree.
