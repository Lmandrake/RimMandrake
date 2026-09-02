# MASS_VALIDATION_LADDER_1 — batched validation ladder (L0–L4)

Thin item — FOUNDRY decision on spec/verify/criteria, 2026-09-02. Owner's
filing (verbatim, 2026-09-02): *"I like your plan except for the human
reviewer. Please take me out of that loop so you can validate your own art
presence, etc. You don't need me to find magenta squares, don't use humans
where a screenshot will do. Anytime you can review something, just go ahead
and do so. Reserve human testing where it absolutely must be used, likely
things like gameplay, fun, overall thematic coherence, user interface
questions."*

## spec

Full ladder design: `infrastructure/VALIDATION_LADDER.md` (owner-ruled,
2026-09-01) — L0 offline / L1 resolved-live (hot-reload + `jawa/get_defs` +
manifest diff) / L2 behavior gauntlet (batched quicktest, art proven by
machine) / L3 Fable evaluation (art/style/thematic judgment, bridge in
Fable's own hands) / L4 human (gameplay/fun/thematic coherence/UI only).
This item builds the machinery; the ladder DOC states the design and is not
duplicated here.

## verify

Per `VALIDATION_LADDER.md`'s own `## Criteria (for MASS_VALIDATION_LADDER_1)`:
- A batch of builds validates through L2 in one bridge sitting, zero restarts.
- `jawa/get_defs` reads nested fields (stages etc.) after its upgrade.
- One manifest format, one runner; no bespoke V&V scripts per item.
- One measured `hot_reload_defs` trial on the full list, owner-blessed.
- First review environment staged and reviewed by the owner.

## criteria

Same five bullets as `## verify` above — this item is done when all five are
true, not before.

## 2026-09-02 (FOUNDRY) — offline half built; everything bridge/owner-gated still open

Built while a sibling fork held the bridge for unrelated work — this pass
never touched the bridge, never restarted, never deployed the companion DLL.

**"One manifest format, one runner" — DONE, offline-proven:**
- `src/RimMandrake/Utils/expectations_manifest.py` — the format. A manifest
  is one JSON file, `{"item": "...", "checks": [{"defType", "defName",
  "path", "expected"}, ...]}`. `path` is dotted-with-brackets
  (`stages[0].label`); a path with no `.`/`[` is a SCALAR check (works
  against the live `jawa/get_defs` TODAY, scalar-only), anything else is a
  DEEP check (needs the upgrade below — reads `SKIPPED-PENDING-UPGRADE`
  until it's live, never silently attempted against data that can't serve
  it). No manifest exists yet from any prior build item this session — this
  is the format going forward, not a retrofit of already-closed items.
- `src/RimMandrake/Utils/run_expectations.py` — the one runner. `--fixture
  <json>` mode is fully offline (a hand-authored `{"DefType::defName": {...
  fields...}}` stand-in for a live deep-serialized read) — this is how a
  manifest gets iterated on and CI-checked before any game is involved.
  `--live` mode calls the real bridge (`RimBridge` from
  `rimbridge_client.py`, one `jawa/get_defs` batch call per defType, scalar
  checks only until the upgrade lands). Exit 0 = all PASS/SKIPPED-PENDING-
  UPGRADE, exit 1 = any FAIL/MISSING-DEF/PATH-ERROR/unparsable manifest.
- `src/RimMandrake/Utils/selftest_expectations_manifest.py` — 20 synthetic
  assertions (path-walking, malformed-manifest rejection, PASS/FAIL/
  MISSING-DEF/PATH-ERROR/SKIPPED-PENDING-UPGRADE all exercised against real
  fixture files, not mocked internals). `python3
  src/RimMandrake/Utils/selftest_expectations_manifest.py` — 20/20 pass.
  Fixtures: `testdata/expectations_selftest_{manifest,fixture}.json`.
  Manifests for real build items belong at
  `infrastructure/state/expectations/<ITEM_ID>.expectations.json` (new
  directory, created this pass, currently empty — no existing build item
  has been retrofitted with one yet; that's follow-on work, not required to
  close this item, which is about the MACHINERY existing).

**"`jawa/get_defs` reads nested fields" — C# WRITTEN, COMPILED, NOT DEPLOYED:**
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs`
— added a `deep` parameter (default `false`, byte-identical old behaviour)
to the `jawa/get_defs` tool, and a new `DeepSerializeValue(object, int
depth)` helper. `deep=true`: a list item that is a plain object (e.g.
`ThoughtStage`) recurses into its own public fields instead of collapsing
to its bare type name; a `Def` reference still collapses to `defName`
(never expands — keeps the payload finite); depth capped at 3 to bound a
pathological object graph; a non-enumerable complex field (previously
silently DROPPED with no placeholder at all — a real, separate small bug
found while reading the old code, now also fixed under `deep=true`) is
serialized too. `deep=false` remains the exact old behaviour for every
existing caller.

Compiled: `python.exe "D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\build.py" --gm`
(plan-only, no `--apply`) — **Build succeeded, 0 Warning(s), 0 Error(s)**,
bundle-contents check clean (ships only the one DLL). **NOT deployed** — the
game is up and a sibling fork holds the bridge; deploying needs a game-DOWN
window per `rimbridge-companion` skill (`taskkill` first, DLL is memory-
mapped while RimWorld runs). Left for whoever next has a game-down window:

```
taskkill.exe /F /IM RimWorldWin64.exe
python.exe "D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\build.py" --gm --apply
<relaunch, then prove: call jawa/get_defs on a known ThoughtDef with
 fields=stages, deep=true, and read back stages[0].label for real>
```

**Still fully open, all bridge-gated and/or owner-gated — none attempted
this pass:**
- L2 batch-validate-in-one-sitting trial.
- The `hot_reload_defs` full-list measured trial (owner-blessed timing).
- The first staged review environment (L4, needs the owner's own eyes per
  his ruling above).
- Retrofitting any real build item (e.g. `FORSAKEN_CRAGS_PREDATORS_BUILD_1`)
  with an actual `.expectations.json` manifest — the format/runner exist,
  nothing has used them for real content yet.

Left `doing`.
# Hot-reload full-list trial: blessed in principle (owner card, 2026-09-02)

"Foundry currently has the bridge. Sorry. Need to do this later." ⇒ the trial
is authorized; run it at the next window the bridge is free — take it via
rimflow, time one hot_reload_defs on the full list, prove a def read
before/after, release. Do not re-ask; the blessing stands.

# 🔴 Hot-reload trial RESULT — full list HANGS (BENCH, 2026-09-02)

Ran the blessed trial on the full ~592-mod list. `jawa/hot_reload_defs`
returned success:true in 0.1s, then the game went UNRESPONSIVE re-loading all
defs + rebuilding render meshes; the play UI was lost (owner: "I see no
buttons"). Unrecoverable live hang, restart required. Disk unharmed (trial
marker reverted before the hang; 0 markers left). ⇒ hot-reload is a
MINIMAL-LIST tool only; the zero-restart L1 cycle in VALIDATION_LADDER.md
applies to minimal-list tool work, NOT the owner's play stack. Doctrine
corrected in rimworld-modding §2 and rimworld-load-round §0.
