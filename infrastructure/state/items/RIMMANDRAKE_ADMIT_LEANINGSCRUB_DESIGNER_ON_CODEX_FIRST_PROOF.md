# RIMMANDRAKE_ADMIT_LEANINGSCRUB_DESIGNER_ON_CODEX_FIRST_PROOF

## spec

LeaningScrub enters the Maturation Pipeline at Stage 1 (the Designer), its Designer run on Codex: the first mod of the
batch the owner asked for on 2026-11-15 ~4:30 PM PST ("Could we do steps 1 and 2 using GPT for the remaining Biomes? That
would be a LOT of user interaction that I could help with today too.") and the end-to-end proof of the Codex Designer
runner his correction asked for (~4:40 PM PST: "I think we DO want a Designer that can run on CODEX.").

- Mod: `src/RimMandrake/LeaningScrub` (51 Defs XML, 46 C#, 305 PNG, 10 validation/selftest scripts; last commit ebd8f544f6
  2026-11-12). Ranked 3rd of 25 biome mods on 2026-11-15 (`D:\ClaudeWork\rimmandrake\conductor\next_biome_mod_20261115.md`).
- Concept: `design/concepts/LeaningScrub/`, `designer_stage.py init --runner codex --draft` the lane-E Codex draft (input
  to verify, not output), so the Dispatcher's DesignerCodex lane runs every stage on Codex.
- Ceiling: Stage 2 (Preflight). It is not on `maturation_dispatch.json` `advancing`, so Dispatch launches no builder on
  it; moving it to Stage 3 is the Conductor's call.
- This item is the concept's ledger item: his answers to its turns are OWNER events on it.

Acceptance test: none, a Designer pass is judged by the stage machine's own result.json validation and his
certification, not by a command.

## What the card said

<!-- answered 2026-11-16T13:24:22Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** Mon Nov 16, 5:21 AM PST. Leaning Scrub, card 3 of 3, the last one. Recorded so far: promises 1, 2, 3 and 5 binding as written; 4 binding plus your healing-rub reason; 6 (ruins-to-water and camps) moved to the next version; 7 keeps the fire-stamping giants and witness tracking, with the pyre beliefs moved to the next version; 8 removed as a Leaning Scrub promise, because working settings and save/reload are a floor every mod already owes, and no old-save work is done at all. One thing left: the 'flagship', the single in-game scene shown to you first and used as the mod's headline proof. An agent picked it, and the judge says that pick must be yours. The agent's pick: a colony running on wind power does a routine haul that takes the safe detour beside a dangerous vine shortcut, then you order an expedition into the vines and it returns. Which scene should be the flagship?
**His words:** Why am I choosing between these? These are all important.
**Other options:** Home, routes, expedition (Recommended) · The vine forms · The weather · Wildlife on the runways
