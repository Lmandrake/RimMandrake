## spec
BENCH verify of 1e41c7f1c7: `C:\ProgramData\OpenAI\Codex\config.toml` (codex's SYSTEM config layer) steered a fully
guarded GptConsult judge to a VALID vote. Full spec and evidence:
`D:\ClaudeWork\rimmandrake\arena\verify_judge_homefix\spec_programdata.md`, probe_results.jsonl (case programdata).
Fix: before and after every call refuse while anything exists under `<ProgramData>\OpenAI\Codex`; check the other
system layers codex might read; add a mutant.

Built: c5a22b84fb (system_layer_violations: 4 ProgramData roots, policy keys, CODEX_/OPENAI_ env, wired pre+post) and
ff2c69f342 (every case variant followed; per-root native `cmd.exe if exist` probe for 8.3 aliases; win_to_local tested).
What codex reads at system level (measured): `D:\ClaudeWork\rimmandrake\arena\programdata_fix\probe_sys.jsonl`.
GPT reviews: `D:\ClaudeWork\rimmandrake\foundry_builder\gpt_pd\r1.md`, `r2.md`.
Not covered: a non-English Windows (reg.exe absent text) refuses every call (fails closed); 8.3 alias resolution by
`if exist` is Win32 semantics, not measured (setting a short name needs admin).

## criteria
- A1 L0: selftest_judge_codex_home t_system: every shape of `<root>\OpenAI\Codex` at each of 4 roots, policy keys, env, native probe refused; 26 source mutants killed
- A2 L0: a real `C:\ProgramData\OpenAI\Codex` plant makes verify_home refuse (listing and native probe both hit); removing it clears
- A3 L1: an independent tester (not the builder) re-runs a real judge call with a ProgramData config.toml plant and sees the call refused, not a VALID vote
