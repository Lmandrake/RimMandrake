# LeaningScrub: journal

This is the mod's memory for the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md` §5, "The steward and the journal").
The top part, **the mod as it stands**, is rewritten at every stage change and stays under two screens. The
**history** below it is only ever added to.

LeaningScrub entered the pipeline on the owner's word: "Could we do steps 1 and 2 using GPT for the remaining Biomes? That
would be a LOT of user interaction that I could help with today too." (OWNER, 2026-11-15 ~4:30 PM PST), with his
correction "I think we DO want a Designer that can run on CODEX." (~4:40 PM PST). Item
RIMMANDRAKE_ADMIT_LEANINGSCRUB_DESIGNER_ON_CODEX_FIRST_PROOF.

## The mod as it stands

- **Waiting on:** the Designer's first-touch run, on Codex (the Dispatcher's DesignerCodex lane; stage.json `runner: codex`).
- **Stage now:** Stage 1, the Designer, since 2026-11-15 5:30 PM PST (`version/stage_record.json`).
- **Mod:** `src/RimMandrake/LeaningScrub`, the RM_LeaningScrub biome.
- **Design Version:** none yet; the pipeline locks a new mod at 0.1.0 when the Designer pass is done.
- **Ceiling:** Stage 2 (Preflight). Not on `maturation_dispatch.json` `advancing`: no builder launches on it.
- **Input:** a Codex first-touch draft, to verify, never to copy: `D:\ClaudeWork\rimmandrake\codex_designer_drafts_20261115\LeaningScrub.designer_draft.md` (stage.json `draft_input`).

## History

- 2026-11-15, BENCH: ranked 3rd of 25 biome mods by measurement (review clean 85/129, testq 3/5 jobs done with 49 PASS
  and 0 FAIL rows, selftests 10/10 green; `D:\ClaudeWork\rimmandrake\conductor\next_biome_mod_20261115.md`). Seeded at
  the Designer (`designer_stage.py init --runner codex --draft`, `maturation.py seed`).

## Stage 3 — rm-role-designercodex-1794799806

Wrote sheet/tree/plan/scenes/floor and supporting source/setting/audit contracts. Gate A, showcase set and stage check pass; result.json is done for this run only.70 leaves,81 planned scenes,7 showcases and7 remainder checks cover71 required units; two absent cuts retain an explicit check. Five proof-contract build items filed without queue priority. No live acceptance, exam, signature or lock inferred. No bridge, game, restart, deployment, mod-code or art action. See write_checks_03.json and record.stage_3. Launcher alone closes/advances the stage.
