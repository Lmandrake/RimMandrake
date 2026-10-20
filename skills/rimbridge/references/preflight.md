# Pre-flight: before a cold load, and in its first five minutes

*Fold-in owed: this is the full text; `SKILL.md` carries one pointer row. Skills are curated in
fresh-context passes, so this file waits for one.* Source: `src/RimMandrake/Utils/preflight_bridge.py`
(`PREFLIGHT_BUILD_85_ROWS_OF_HINDSIGHT`). Design: GPT's review §3
(`Transient/foundry_bridge_system_review_gpt_20261010.md`, expires) and
`design/RimMandrake/bridge_debugging_system.md` §5.3.

## Run it

```
python3 src/RimMandrake/Utils/preflight_bridge.py --tier full --deep     # before launching the full list
python3 src/RimMandrake/Utils/preflight_bridge.py --tier minimal --purpose menu
python3 src/RimMandrake/Utils/preflight_bridge.py --modset acc_green_min # any modset_builder tier as the intended list
python3 src/RimMandrake/Utils/preflight_bridge.py --tier full --live     # after launch: files + OS only, no bridge call
```

Exit **0 GREEN**, **1 NO-GO** (a FAIL), **2 NOT-GREEN** (no FAIL, but a required check is UNMEASURED or
was skipped by fail-fast). Each line: `STATUS id name req|opt seconds reason`. Report:
`D:\ClaudeWork\rimmandrake\scratch\preflight\last_preflight.json` (also `--json <path>`); `experiment_manifest.py
complete` reads it.

- **Cheapest first, fail-fast.** A required FAIL stops the run; `--all` runs everything.
- **"Could not ask" is UNMEASURED, never PASS.** GREEN needs no FAIL and no required UNMEASURED.
- **`--deep`** lets the patched-tree lint build on a cache miss (~1-3 min under `python.exe` on 551 mods).
  Without it a miss is UNMEASURED, so a changed mod set cannot read GREEN by accident.
- **`--purpose test`** (default) refuses known wedgers (RealFoW on a bland-world run). Use
  `campaign`, `menu` or `review` when the run does not destroy ruins on a second map.
- Its one write: the current `Player.log` is copied to `D:\ClaudeWork\rimmandrake\scratch\preflight\playerlogs\`
  before the next launch truncates it (`--no-archive` skips).
- It never takes the bridge, launches or kills the game, or writes `ModsConfig.xml`.

## Offline checks (game down)

| id | check | catches (debugging doc §4 row) |
|---|---|---|
| O01 | one-or-zero `RimWorldWin64`; down for a cold launch | #21, #39 |
| O02 | bridge lease free or ours (`infrastructure/state/BRIDGE`) | #22, #50 |
| O03 | free disk C: >= 20 GB, D: >= 10 GB | |
| O04 | live `ModsConfig.xml` == intended list, **ordered**; names a Core-only reset | #19, #47, #54 |
| O05 | intended list: no composed-member ids, duplicates or uninstalled ids | #58, #80 |
| O06 | every mod we build is on the full list (opt; `modmanifest.shipping_gap`) | P-a |
| O07 | known wedgers for the purpose | #61 |
| O08 | previous `Player.log` archived | #26 |
| O09 | deployed companion == repo artifact (sha + build id) | #51, #57, P-c |
| O10 | RimBridgeServer / Harmony / Assembly-CSharp fingerprint vs baseline (opt; `--accept-deps` records it after a green load) | prediction 14, 18 |
| O11 | bridge-lint snapshot covers every `[Tool("...")]` in the companion source (opt) | P-d |
| O12 | repo load killers: BiomeWorker `.Rivers`, abstract Alert leaf, missing `<Compile Include>` | #33, #24 |
| O13 | every mandrake mod on the list: repo == deployed copy, content hash and DLL bytes (`run_identity`) | #31, #46, #52, #57 |
| O14 | patched-tree lint, `effective_def_lint.py` (below) | #24, #30, #36, #37, #41, #53, #66 |

The intended list is `--modset <tier>` when given, else `modmanifest.py`'s
`infrastructure/state/modlists/manifest.<TIER>.json`, else the snapshot `ModsConfig.FULL.LATEST.xml` /
`ModsConfig.MINIMAL.xml`. GPT's warning stands: never infer the full list from what is deployed.

## Live checks (`--live`, read-only)

| id | check |
|---|---|
| L01 | this PID started before the log was last written, its log holds `Bridge token:`, and the bridge port is held by that PID |
| L02 | no `Resetting mods config` / `Recovered from incompatible or corrupted mods` |
| L03 | `launch_gate`: no missing RimMandrake types; prints the FIRST exception and the `Config error in` count |
| L04 | the running list (RimDefDump's `manifest.json`, written after this PID started) == intended, ordered |
| L05 | `[JawaBench] ready: N tools, build X`: X == the repo artifact's build |
| L06 | `[JawaBench] TPS sampler installed (bridge-registration)` (opt) |
| L07 | `[JawaBench] map awareness:` installed, not failed (opt) |

Not covered yet (GPT §3.4): main-thread round trips, `Prefs.RunInBackground`, modal allow-list,
resolved-def audit inside the running game. Those need a bridge call or a companion tool.

## The patched-tree lint

```
python.exe src/RimMandrake/Utils/effective_def_lint.py infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml
python3    src/RimMandrake/Utils/effective_def_lint.py --src-only
... 'mandrake.rsw.armoury=\\wsl.localhost\Ubuntu\home\mandrake\rm\foundry\src\RimStarWars\Armoury'   # prove an undeployed fix
```

It builds the effective def tree the way the engine does (Defs, LoadFolders, patches in load order,
MayRequire, ParentName) and runs every check in its docstring. `crash` means a decompiled-1.6 path
dereferences the value during load (a costList miss on a `recipeMaker` def NREs in
`RecipeDefGenerator.SetIngredients`; on Minify Everything's Mass path it NREs in the implied-def postfix).
Results are cached by file content in `D:\ClaudeWork\rimmandrake\scratch\effective_def_lint\`.

🔴 It reads the **deployed** Mods folders. A fix committed but not deployed still shows; use an
override to prove the fix, then deploy.
