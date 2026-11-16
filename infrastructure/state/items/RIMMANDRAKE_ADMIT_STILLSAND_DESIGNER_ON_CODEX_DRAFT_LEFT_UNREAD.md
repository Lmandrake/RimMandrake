# RIMMANDRAKE_ADMIT_STILLSAND_DESIGNER_ON_CODEX_DRAFT_LEFT_UNREAD

## spec

Stillsand enters the Maturation Pipeline at Stage 1 (the Designer), its Designer run on Codex: a mod of the batch the owner asked
for on 2026-11-15 ~4:30 PM PST ("Could we do steps 1 and 2 using GPT for the remaining Biomes? That would be a LOT of user
interaction that I could help with today too."), after LeaningScrub proved the Codex Designer runner his correction asked
for (~4:40 PM PST: "I think we DO want a Designer that can run on CODEX.").

- Mod: `src/RimMandrake/Stillsand` (57 Defs XML, 42 C#, 156 PNG, 8 validation/selftest scripts; last commit 274e6da319 2026-11-11). Ranked 5th of 25 biome mods on 2026-11-15
  (`D:\ClaudeWork\rimmandrake\conductor\next_biome_mod_20261115.md`): review clean 46/129, testq 13/13 jobs done with 111 PASS and 1 FAIL row, selftests 9/9 green.
- Concept: `design/concepts/Stillsand/`, `designer_stage.py init --runner codex` (no draft: the Designer reads from the source),
  so the Dispatcher's DesignerCodex lane runs every stage on Codex, held under 25% of the Codex week left.
- Ceiling: Stage 2 (Preflight). It is not on `maturation_dispatch.json` `advancing`, so Dispatch launches no builder on
  it; moving it to Stage 3 is the Conductor's call.
- This item is the concept's ledger item: his answers to its turns are OWNER events on it.

Acceptance test: none, a Designer pass is judged by the stage machine's own result.json validation and his
certification, not by a command.
