# RIMMANDRAKE_ADMIT_CAULDRON_DESIGNER_ON_CODEX_RANKED_SECOND

## spec

Cauldron enters the Maturation Pipeline at Stage 1 (the Designer), its Designer run on Codex: a mod of the batch the owner asked
for on 2026-11-15 ~4:30 PM PST ("Could we do steps 1 and 2 using GPT for the remaining Biomes? That would be a LOT of user
interaction that I could help with today too."), after LeaningScrub proved the Codex Designer runner his correction asked
for (~4:40 PM PST: "I think we DO want a Designer that can run on CODEX.").

- Mod: `src/RimMandrake/Cauldron` (34 Defs XML, 24 C#, 93 PNG, 9 validation/selftest scripts; last commit d1817022db 2026-11-15). Ranked 2nd of 25 biome mods on 2026-11-15
  (`D:\ClaudeWork\rimmandrake\conductor\next_biome_mod_20261115.md`): review clean 52/78, testq 5/5 jobs done with 154 PASS and 3 FAIL rows, selftests 10/10 green.
- Concept: `design/concepts/Cauldron/`, `designer_stage.py init --runner codex` (no draft: the Designer reads from the source),
  so the Dispatcher's DesignerCodex lane runs every stage on Codex, held under 25% of the Codex week left.
- Ceiling: Stage 2 (Preflight). It is not on `maturation_dispatch.json` `advancing`, so Dispatch launches no builder on
  it; moving it to Stage 3 is the Conductor's call.
- This item is the concept's ledger item: his answers to its turns are OWNER events on it.

Acceptance test: none, a Designer pass is judged by the stage machine's own result.json validation and his
certification, not by a command.
