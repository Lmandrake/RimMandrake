# RIMMANDRAKE_ADMIT_FEVERWOOD_DESIGNER_ON_CODEX_DRAFT_IN_HAND

## spec

FeverWood enters the Maturation Pipeline at Stage 1 (the Designer), its Designer run on Codex: the first mod of the
batch the owner asked for on 2026-11-15 ~4:30 PM PST ("Could we do steps 1 and 2 using GPT for the remaining Biomes? That
would be a LOT of user interaction that I could help with today too."), after LeaningScrub proved the Codex Designer runner
his correction asked for (~4:40 PM PST: "I think we DO want a Designer that can run on CODEX.").

- Mod: `src/RimMandrake/FeverWood` (55 Defs XML, 44 C#, 156 PNG, 3 validation/selftest scripts; last commit 52b041e51a
  2026-11-15). Ranked 9th of 25 biome mods on 2026-11-15 (`D:\ClaudeWork\rimmandrake\conductor\next_biome_mod_20261115.md`).
- Concept: `design/concepts/FeverWood/`, `designer_stage.py init --runner codex --draft` the lane-E Codex draft (input
  to verify, not output), so the Dispatcher's DesignerCodex lane runs every stage on Codex.
- Ceiling: Stage 2 (Preflight). It is not on `maturation_dispatch.json` `advancing`, so Dispatch launches no builder on
  it; moving it to Stage 3 is the Conductor's call.
- This item is the concept's ledger item: his answers to its turns are OWNER events on it.

Acceptance test: none, a Designer pass is judged by the stage machine's own result.json validation and his
certification, not by a command.
