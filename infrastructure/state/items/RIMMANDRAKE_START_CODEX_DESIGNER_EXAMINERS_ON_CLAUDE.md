# RIMMANDRAKE_START_CODEX_DESIGNER_EXAMINERS_ON_CLAUDE

## spec

The brief of RIMMANDRAKE_DRAFT_BIOME_DESIGNER_PASSES_WITH_CODEX_BEFORE_RESET: "The stage's exam helpers (Examiner,
Challenger, Readers, Control) stay on Claude so the maker and its examiners are different models." The Stage 4 packet
(`designer_exam.md`) assumes the Designer spawns fresh agents with its own tool; a Codex Designer has no Claude Agent
tool, so it would either fail the exam or play the helpers itself on the same model.

Fix: `designer_stage.packet` adds one line at stage 4 for a concept whose stage.json runner is codex: start each helper
as its own Claude (Opus) process, `src/RimMandrake/Utils/claude_bounded.sh -p --model opus --output-format json "<brief>"`,
name it in exam.json by its session_id, charge it as a helper, never play one yourself. Claude concepts and other stages
are unchanged. Logged as a delegated call (`--why "delegated: model split"`).

Acceptance test: `python3 src/RimMandrake/Utils/selftest_codex_runner.py`, test `test_codex_exam_helpers_on_claude`.
It failed on the base (FAIL) and passes after. A live Stage 4 on Codex is UNRUN (no Codex concept has reached the exam);
its live test is the first such exam, read with `designer_stage.py check <dir>`.
