# BUILD_PY_TOOLNAME_SCAN_FALSE_LOSS_1 — build.py's tool-removal guard reads DLL bytes and reported a fictitious lost tool

Found 2026-09-06 deploying the JawaBenchSocietyTools review fixes. `src/RimMandrake/bridgetools/build.py:253` derives the companion's tool set with `re.findall(r"jawa/[a-z_]{3,40}", blob.decode(enc, "ignore"))` over the raw DLL — a byte-scan, the instrument class `instruments-that-lie-with-a-number` warns about. It reported `LOSES jawa/pawn_` and REFUSED the deploy. `jawa/pawn_` is not a tool: a description string near `jawa/pawn_severity_adjust` changed in the edit, and the byte fragment the OLD dll happened to contain vanished. Ground truth: 313 `[Tool("jawa/…")]` declarations in source == 313 live-registered names in this session's tool dump, zero difference either way. Deployed with `--allow-tool-removal` on that evidence (commit note).

## spec
- Replace the byte-scan with a metadata read: the `[Tool]` attribute's first constructor argument lives in the custom-attribute blob (UTF-8 SerString), not the #US heap — use `src/RimMandrake/Utils/ilprobe/` (meta reader) or the .NET metadata tables to enumerate `Tool` attributes and their name arguments exactly. Fall back to parsing the SOURCE (`[Tool(\s*"jawa/…"`) which is what this repo compiles from and is exact.
- Compare SETS of full names; a candidate that is a strict prefix of a declared name (trailing `_`, shorter than any declared name) is a scanner artifact and must never be reported as a loss.
- Selftest: build the current source, scan, assert scan == source-declared set (313 today).

## verify
```
PROVE   build.py plan on an unchanged build prints 0 losses; with one tool deliberately deleted from source it names exactly that tool
EXPECT  no partial-name tokens ever appear in the LOSES list
LIES    a scan that passes because both sides are wrong the same way — the selftest must compare against the SOURCE declarations, not a previous scan
```
