# Stillsand: journal

This is the mod's memory for the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md` §5, "The steward and the journal").
The top part, **the mod as it stands**, is rewritten at every stage change and stays under two screens. The
**history** below it is only ever added to.

Stillsand entered the pipeline on the owner's word: "Could we do steps 1 and 2 using GPT for the remaining Biomes? That
would be a LOT of user interaction that I could help with today too." (OWNER, 2026-11-15 ~4:30 PM PST), with his
correction "I think we DO want a Designer that can run on CODEX." (~4:40 PM PST). Item RIMMANDRAKE_ADMIT_STILLSAND_DESIGNER_ON_CODEX_DRAFT_LEFT_UNREAD.

## The mod as it stands

- **Waiting on:** the Designer's first-touch run, on Codex (the Dispatcher's DesignerCodex lane; stage.json `runner: codex`).
- **Stage now:** Stage 1, the Designer, since 2026-11-15 5:30 PM PST (`version/stage_record.json`).
- **Mod:** `src/RimMandrake/Stillsand`.
- **Design Version:** none yet; the pipeline locks a new mod at 0.1.0 when the Designer pass is done.
- **Ceiling:** Stage 2 (Preflight). Not on `maturation_dispatch.json` `advancing`: no builder launches on it.

## History

- 2026-11-15, BENCH: ranked 5th of 25 biome mods by measurement (review clean 46/129, testq 13/13 jobs done with 111 PASS and 1 FAIL row, selftests 9/9 green;
  `D:\ClaudeWork\rimmandrake\conductor\next_biome_mod_20261115.md`). Seeded at the Designer
  (`designer_stage.py init --runner codex`, `maturation.py seed`).
