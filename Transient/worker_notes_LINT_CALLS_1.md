# LINT_CALLS_1 worker notes
- started
- source: Transient/bench_tools_dump.json (live census, 438 tools)
- tool_schemas.py + json built
- census lacks 30 tools that exist in C# source (stale census): adding --supplement-csharp parser
- snapshot 482 tools; lint runs; baseline 7 problems; next: selftest, baseline md, commit
