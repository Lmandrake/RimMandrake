# Test Pilot (harness-only): readiness failures of RIMMANDRAKE_SET_HUGETHINGS_TREMORS_TWO_HOURS

Sitting date 2026-11-11. This was diagnosis only: no bridge take or call, no game launch, no worldgen, no install, no source or ledger edit, no commit. The host in scope is SteveDesktop; Archmagi was not touched. Every shell sourced `/home/mandrake/rm/runner/infrastructure/stevedesktop/testcentre_env.sh`. Sources read: the raw `live_run_{1,2,3}` receipts and preflight JSON, `run_live.py`, `run_live_before_byte_check.py`, `preflight_bridge.py` `c_def_lint` (O14), `costlist_resolve_check.py` imports, the `python_dependency.*`, `preflight_dependency_retry.*` and `dependency-deploy-apply.*` receipts, and STATEMENT.md. I did not read DONE, JUDGE, FINDINGS, OBSERVER, final_inspection or BLOCKED.

## Verdict
CLASS: HARNESS, for all three attempts. The mod did not fail to load, and the game never started in any attempt. The three failures had three different causes, and only one is still open:

| run | UTC | stopped at | cause | status now |
|---|---|---|---|---|
| 1 | 09:42:59-09:44:23 | preflight_offline: O13 FAIL + O14 UNMEASURED | O13: the deployed dependency mods FlowWorks (10 files) and GimmeSomeSlack (46 files) were stale. O14: lxml missing from the interpreter | O13 fixed by the dependency deploy (`dependency-deploy-apply.rc`=0, 09:49:10). Run 3 O13 = PASS, "5 mods, 1211 files: deployed == repo byte for byte" |
| 2 | 09:49:10-09:50:19 | after deploy, before preflight: `no VERIFIED byte comparison` | The harness check was wrong. `run_live_before_byte_check.py` required the string `VERIFIED` in the deploy stdout, but `deploy_custom_mods.py:897` prints "VERIFIED in sync" only after it writes something. A no-op deploy prints "in sync (15 files, 2 held) / Nothing to do" instead (grep count of VERIFIED: run1=1, run2=0, run3=0) | Fixed in `run_live.py` by comparing sha256 of the 4 HugeThings files directly. Run 3 `deploy_bytes.json` shows all 4 equal |
| 3 | 09:52:04-09:53:23 | preflight_offline: O14 UNMEASURED only. Every other row PASS (O01-O13, O10 included) | lxml missing from the interpreter that ran the preflight | **OPEN**: the only remaining blocker |

## O14 mechanism (observed, not inferred)
1. `run_live.py` `run()` runs `bash -c "source testcentre_env.sh; export ...; python3 src/RimMandrake/Utils/preflight_bridge.py ..."`, using the parent's PATH (`ENV = dict(os.environ)`).
2. In that shell, `command -v python3` gives `/usr/bin/python3` (3.14.4, prefix `/usr`). I checked this inside a `bash -c` with the same source and export lines. testcentre_env.sh only appends Windows directories (for example `/mnt/c/Program Files/Python313`) to PATH. It does not mention the venv. `VIRTUAL_ENV` and `PYTHONPATH` are unset.
3. `preflight_bridge.py` `c_def_lint` with `--modset` lints `gp.MODS_CONFIG` (`/mnt/c/Users/.../ModsConfig.xml`). That file is outside REPO, so `rel` is None and the `python.exe` branch is skipped. The command used is `[sys.executable, effective_def_lint.py, ...]`, i.e. `/usr/bin/python3` again.
4. `effective_def_lint.py:267` imports `costlist_resolve_check`, and that module's line 22 is `from lxml import etree`, which raises ModuleNotFoundError. No report is written, so O14 is UNMEASURED and the row records "wrote no report (exit 1)". This is the same traceback in runs 1 and 3.
5. `/home/mandrake/.cache/ht-warning-venv` was created at 09:45:35 (`python_dependency.rc`=0, lxml 6.1.3 installed). Its pyvenv.cfg has `home=/usr/bin`, `include-system-site-packages=false`, `version=3.14.4`, `executable=/usr/bin/python3.14`. Nothing in `run_live.py` points at it, so runs 2 and 3 still used `/usr/bin/python3`.

## Discriminating cheap check (run, read-only, import only, no lint or game)
`<PY> -I -B -c 'sys.path.insert(0,"src/RimMandrake/Utils"); find_spec("lxml"); import costlist_resolve_check; import effective_def_lint'`
- `/usr/bin/python3`: `lxml_spec False`, `costlist_resolve_check ModuleNotFoundError: No module named 'lxml'`, effective_def_lint OK (it imports lxml lazily).
- `~/.cache/ht-warning-venv/bin/python3`: `lxml_spec True`, both imports OK. The same interpreter produced the 09:46:41 `preflight_dependency_retry` with O14 PASS: "clean | .../ModsConfig.xml; cache MISS; unsupported scope: ['donor_types']" in 37.6 s.

So the failure follows the interpreter, not the mod content. This confirms the cause is a missing interpreter dependency.

## Ruled out
- Mod or load failure: the game was never launched (no `up` command in any receipt), and O14 crashed during import before it linted anything. UNMEASURED does not mean FAIL.
- Bad mod content or a stale deploy causing O14: run 3 O13 PASS byte for byte, and O14 still failed with the same ImportError.
- The Windows `python.exe` lint path: it is not reached with `--modset`, because the list file is outside the repo. The traceback paths are Linux paths (`/home/mandrake/rm/codex-ht/...`).
- PYTHONPATH or VIRTUAL_ENV leaking: both unset. `-I` reproduces the result.
- Lease, guard or host problems: take, release and guard all returned rc 0 in every run. O02 PASS (FREE). Only SteveDesktop was used.
- O10 (optional): UNMEASURED in run 1 and PASS in run 3. It is not required and played no part.

## Smallest repair (harness only, preflight unchanged)
Have `run_live.py` run the preflight under the venv interpreter. In `preflight()`, change `args = ["python3", "src/RimMandrake/Utils/preflight_bridge.py", ...]` to `args = ["/home/mandrake/.cache/ht-warning-venv/bin/python3", "src/RimMandrake/Utils/preflight_bridge.py", ...]`. preflight then passes its own `sys.executable`, which is the venv, to effective_def_lint, and lxml resolves. An equivalent option is to prepend `/home/mandrake/.cache/ht-warning-venv/bin` to `ENV["PATH"]` before `guard_before`, but that changes every child, so the one-line `preflight()` change is smaller. Keep the current `run_live.py` as a dated copy, the same way `run_live_before_byte_check.py` was kept, and write new attempts to a new `live_run_4` directory. Existing evidence is left unchanged.

Gate before the expensive retest: run the import check above with the venv python (it should report OK), then let `run_live.py` reach preflight_offline. O14 must be PASS, not UNMEASURED, before `up` runs. Expect about 40 s or more for O14 on a cache miss.

## Limits
- The last lint PASS (09:46:41) came before the 09:49:10 dependency deploy, which changed FlowWorks and GimmeSomeSlack in the game copy. O14 has never measured the current deployed content, so a real lint FAIL is still possible. That would be a genuine finding, not a harness error.
- Everything after preflight_offline has never run in any attempt: Steam launch through `steam_adapter`, live preflight, Player.log inspection, `warning_defaults_live.py`. Those paths are untested.
- The venv lives in `~/.cache` and is not recorded in the repo. A fresh shell or another seat will hit the same ModuleNotFoundError. A durable fix (system lxml, or a declared interpreter for preflight) is a project decision and was not made here.
- No live game state was observed, so no surprises were scored and nothing was filed.
