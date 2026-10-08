# Oracle validation (Approach B), 2026-10-07 - DONE, nothing committed

Sizing: 690 lines; done despite the ~800-line bar because the brief names it. About 330 lines are pure (command line, retry / candidate state machine, classify, budget, delivery, queue, lint); the process plumbing (Process, stdin, WaitForExit, Kill), the GameComponent letter delivery, the settings UI and the debug actions are engine and stay.

## Kernel (Verse-free, `src/RimMandrake/Oracle/Source/Kernel/OracleKernel.cs`; Oracle.csproj now has a `Compile Remove="SelfTest/**"` because it uses the default glob)
- `QuoteArgument` / `BuildArguments` (moved out of OracleClient), `SystemPrompt` (law + exactly one god block), `TimeoutMs`, `Candidates` (override / last-started / PATH / installer path), `IsRetryable` + `RunOnce` + `RunWithRetry` (taking the process call as a delegate), `Classify` (exit code, stdout / stderr), `Admit` (kill switch + per-day budget), `ChooseForLive` / `ChooseFallback` / `Resolve` / `Refused` (laws 1 and 2), `OracleDeliveryQueue`.
- OracleClient keeps only the Process plumbing and calls these; OracleGameComponent asks `Admit`, then `Resolve`, and delivers one `Outcome` per request (a refusal, a failure, a rejected reply and a good reply all end in the same single `Deliver`).
- The lint `OracleValidator` and the prompt text `OracleRegisterBlocks` were already pure and are compiled by the self-test unchanged.

## Fuzz
`python3 src/RimMandrake/Utils/selftest_oracle_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only argv|timeout|launch|classify|budget|pipeline|queue|lint]` (project `Source/SelfTest/RimMandrakeOracle.SelfTest.csproj`).
- argv: `BuildArguments` round-trips through TWO independent CommandLineToArgvW parsers (classic and UCRT) for prompts full of backslashes, quotes, tabs, newlines, unicode, `%PATH%`, `|&^<>`, plus the real law + Ohm prompt: exactly the 6 flag args + the prompt as ONE argument + the denied-tool list; `QuoteArgument` is always one token.
- timeout: `TimeoutMs` over int edges: >= 1000 ms, saturating, never wrapped, monotone.
- launch: candidate order (explicit path alone and trimmed; last-started first; PATH; installer path last; no duplicates) and the retry / candidate machine against a model over scripted outcomes: skipped when unstartable, first non-start exception propagates, all-unstartable -> FileNotFound listing the tried, at most one retry, timeouts and missing binaries never retried, the LAST failure is reported, a started-then-failed executable is pinned for next time.
- classify: exit code is the only success signal; stderr noise on a good run is ignored; the diagnostic is stderr else stdout, capped at 300; clean exit with no output is a (retryable) failure.
- budget (sequences): the kill switch refuses and never counts; a spent / zero / negative budget refuses and never counts; the day rolls the counter (even with the switch off, and when the clock goes back); admitted per day <= budget; model-checked.
- pipeline (laws): for every (kill switch, budget, reply incl. every lint tell, failure, fallback incl. rejected / null) exactly one letter ships, it passes the lint (law 1), it is live only for an admitted, successful, lint-clean reply, a rejected fallback is replaced by the hardcoded safe text which itself passes the lint (law 2), the failure reason is logged.
- queue (sequences): FIFO, every delivery runs once, a throwing delivery is reported and the rest still run.
- lint: `TryValidateOhm` against an independent reference over fragments (tells in any case, Zizzik, brackets, length 600 / 601, null / whitespace); cap > the 500 characters the prompt asks for; every tell the lint forbids except "we are one" is also forbidden in the Law prompt; Ohm's block keeps its Zizzik prohibition; Law names no single god.
- Seeds: 37,500 cases at default (0.4 s). `--fuzz-scale 25`: 937,500 cases, 3.85M steps, 8.6 s, 0 failures. Blind check: round trips, timeouts, retries, all-unstartable, timeouts-not-retried, pins, live / fallback / safe-default letters, rejected replies, refusals, day rollovers, queue errors must all be reached.

## Mutation (28 planted, 28 caught, all restored byte-identical)
`python3 src/RimMandrake/Utils/mutate_kernel_fuzz.py selftest_oracle_fuzz.py src/RimMandrake/Utils/mutations_oracle_fuzz.json`. Planted: backslashes before a quote / trailing backslashes not doubled, seconds*1000 wraps, zero seconds, claude / installer path listed twice, timeouts retried, missing binary retried, a second retry, first instead of last failure, no pin after a started failure, stderr leaks into a reply, diagnostic prefers stdout / uncapped, empty output is success, refusal counts as a call, day never rolls back, one call too many, kill switch ignored, fallback / live reply shipped unlinted, unlinted safe default, a throwing delivery stops the drain, lint length cap +1, closing bracket missed, Zizzik taboo gone, case-sensitive tells, the law stops forbidding "part of me".
Shared-tool fixes: two mutants first failed to build (out param with `&&`) and were rewritten; `mutate_kernel_fuzz.py` now decodes the child's output with `errors="replace"` (a dotnet error line with a non-UTF-8 byte crashed the whole harness mid-run; the file was still restored by its `finally`).

## Lint
Not applicable: Oracle ships no Defs / Patches XML, so `lint_mod_defs.py` is UNMEASURED by construction. No wrapper written.

## Defects
- `Math.Max(1, timeoutSeconds) * 1000` overflowed int for a Scribed `timeoutSeconds` above 2,147,483 (the slider caps at 180, the saved file does not): the product wraps, and a wrapped -1 means WaitForExit(-1) = wait FOREVER on a hung `claude`, any other negative throws. Fixed: `TimeoutMs` saturates.
- Hardened: the launch list could name the installer path twice (when it was also the last-started executable), so a missing binary was attempted twice per try; deduplicated.
- NOTE (not changed): loading an earlier save resets the daily budget (the day rolls on any change of day number, not only forward); the lint cannot see "Z i z z i k" / fullwidth spellings; "we are one" is forbidden by the lint but never mentioned in the Law prompt.

## Build / regressions
`winbuild.py Oracle/Source/Oracle.csproj` -> 0 warnings 0 errors; DLL + .srchash rebuilt, UNCOMMITTED. `Oracle/validation.py` has no source-text scans. `run_selftests.py`: 280/281; the one failure is `selftest_jawarules_fuzz.py` (JawaRules, another builder's mod in progress); nothing pinned Oracle source text.
