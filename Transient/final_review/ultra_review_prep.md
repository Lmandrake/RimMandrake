# Ultra Review Prep — Census + Action List
Generated 2026-09-09, read-only analysis. No code changed, no commits, no game/bridge touched.

## 1. CODE_REVIEW_STATUS.json summary

`python3 src/RimMandrake/Utils/code_review_status.py list` — 1476 tracked entries:

- **CLEAN: 1143**
- **DIRTY: 333** (all reason-tagged `edited since / uncommitted`; zero `never reviewed`
  lines seen because everything in this dump is a superset over the whole tracked
  file list — untracked-but-relevant new files like `OracleClient.cs` don't even
  appear in the list, `check` reports them `never marked clean` instead)

Note: `[x2]`/`[x3]` suffixes on some CLEAN lines are duplicate-hash entries (same
content hash recorded more than once), not multiple files — cosmetic, not a defect
worth chasing here.

## 2. Review-scope files (this session's recent commits)

Commits inspected: `git log --oneline -25` plus targeted `git log -- <dir>` and
`git show --stat` on: `ef628781` (Oracle rewrite), `618f9486` (RaidRedesigner
Property guard), `71bd2f54` (ordered_job + build.py ORACLE_MOD_DIR), `555ef84b`
(StarWarsRaces MayRequire guard), and the uncommitted working-tree diff.

### C# — Oracle transport rewrite (`ef628781`, per owner's 2026-09-05 ruling)
| File | Status | Note |
|---|---|---|
| `src/RimMandrake/Oracle/Source/OracleClient.cs` | DIRTY — never marked clean | **NEW, 302 lines.** Shells to `claude -p`. Highest-priority review target — brand-new subprocess/child-process code. |
| `src/RimMandrake/Oracle/Source/OracleHttpClient.cs` | DIRTY — file no longer exists on disk | Deleted as part of the rewrite; nothing to review, but confirm no stray reference (checked below — none in `.cs`/`.csproj`, only historical mentions in CLAUDE.md/design docs). |
| `src/RimMandrake/Oracle/Source/OracleGameComponent.cs` | DIRTY — changed since 43f96b1b | Touched to call the new client. |
| `src/RimMandrake/Oracle/Source/OracleSettings.cs` | DIRTY — changed since 43f96b1b | Dropped baseUrl/model/apiKey, added `claudeCliPath`. |
| `src/RimMandrake/Oracle/Source/Oracle.csproj` | not in tracked list (project file, not reviewed by this tool) | New `OracleClient.cs` compile entry. |
| `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchOracleTools.cs` | DIRTY — changed since 46ac7699 | `jawa/oracle_configure` updated for new settings shape. |
| `src/RimMandrake/Oracle/About/About.xml` | DIRTY — changed since 06da6f34 | Documents new machine dependency. |

### C# — RaidRedesigner (`618f9486` + uncommitted)
| File | Status | Note |
|---|---|---|
| `src/RimMandrake/RaidRedesigner/Source/Patch_CaravanRobbed.cs` | DIRTY — changed since b87a3622 | Now manually `TryPatch()`-gated behind `ModsConfig.IsActive("mandrake.rm.property")` instead of a hard `[HarmonyPatch]` attribute — this is the actual bugfix, worth close attention (PatchAll's eager attribute-scan resolution risk). |
| `src/RimMandrake/RaidRedesigner/Source/RaidRedesignerMod.cs` | DIRTY — changed since b1655903 | Wires the manual TryPatch call. |
| `src/RimMandrake/RaidRedesigner/Source/RM_RaidRedesigner.csproj` | DIRTY — never marked clean (not a `.cs`, csproj isn't normally tracked but `check` flags it dirty on request) | Fixed stale `RimMandrakePropertyDll` path (`Property` → `RimProperty`). |
| `src/RimMandrake/RaidRedesigner/Assemblies/RimMandrakeRaidRedesignerDLL` | binary, not source-reviewed | Rebuilt output of the above. |

### C# — bridgetools companion (touched, mostly incidental)
| File | Status | Note |
|---|---|---|
| `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchJobTools.cs` | DIRTY — changed since 86ac78d7 | `ordered_job` now sets `playerForced` (5-line fix per `71bd2f54`); reachability confirmed — `jawa/ordered_job` is a live registered tool string, referenced by `JawaBenchZoneTools.cs` and its own doc comments. |
| `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchEventTools.cs`, `JawaBenchFactionTools.cs`, `JawaBenchTerrainTools.cs`, `JawaBenchWorldTools.cs` | DIRTY (uncommitted edits) | Not covered by the commits inspected above — edited in the working tree outside the sampled commit range; scope them in before the ultra pass if they're meant to ship together. |

### XML
| File | Status | Note |
|---|---|---|
| `src/RimMandrake/StarWarsRaces/Defs/HeadTypeDefs/SW_HeadTypes.xml` | not tracked by this tool (XML defs aren't in the CLEAN/DIRTY ledger) | 36 `<li>` guarded with `MayRequire=neronix17.toolbox` (`555ef84b`) — the actual fix for a def-discarding silent failure. Validated already: `validate_patch.py` 0/0, `check_declarations.py` clean, per the commit message. |

### Python
| File | Status | Note |
|---|---|---|
| `src/RimMandrake/Utils/gen_races_mod.py` | DIRTY — changed since 43f96b1b (line was already marked clean at that hash, now dirty from the 10-line MayRequire-guard fix in `555ef84b`) | Reachable: cited as the owning generator by 6 docs/skills; regenerates `SW_HeadTypes.xml`. |
| `src/RimMandrake/Utils/w9_run.py` | DIRTY — changed since prior clean mark | Reachable: cited by `.claude/hooks/selftest_documented_commands.py`, 8+ design/state docs, and calls out to `ashkarr_populate.py`/`save_played_tiles.py`. Two recent commits (`9cf1c2ed`, `452cefe8`) both fixing real bugs (report-always-written, halt-on-unchecked-failures). |
| `src/RimMandrake/bridgetools/build.py` | DIRTY — changed since 2aeb5193 | Added `ORACLE_MOD_DIR` env override (`71bd2f54`). Reachable: >20 docs/scripts cite it as the deploy entry point; it is THE build tool for the companion DLL. |

## 3. Dead-file candidates

**None found in review scope.** Checked every touched Python/C# file above for a
live caller before concluding reachability — not a grep-only ruling:

- `gen_races_mod.py` — grepped for the bare module name across `*.py`/`*.md`/`*.sh`;
  6 doc/skill hits plus its own file. Live.
- `w9_run.py` — same sweep; hit in a hook selftest (`.claude/hooks/selftest_documented_commands.py`)
  plus 8 design/state docs and 2 calling scripts. Live.
- `src/RimMandrake/bridgetools/build.py` — same sweep; >20 hits including skills
  references, item files, and direct importers (`load_session.py`,
  `prove_new_tools.py`, `selftest_tool_metadata.py`, `rimbench/formations.py`,
  `rimbench/terrain.py`). Live.
- `JawaBenchJobTools.cs` (`jawa/ordered_job`) — grepped the tool-name string per
  CLAUDE.md's reflection-registration rule, not just C# call sites; found live
  references from `JawaBenchZoneTools.cs` and its own registration block. Live.
- `OracleHttpClient.cs` — confirmed absent from disk (`ls src/RimMandrake/Oracle/Source/`)
  and absent from `Oracle.csproj` and every `.cs` file; only referenced in prose
  (CLAUDE.md, design docs, item files) describing the now-superseded architecture.
  This is a **completed deletion**, not a dead-file-to-flag — nothing to delete,
  it's already gone. The `code_review_status.json` entry for it is inert (reports
  "file no longer exists on disk") and can be dropped from the ledger whenever
  someone next touches that file's neighborhood; not urgent.

Transient/ scratch scripts from tonight's session (`Transient/gravship_cycle.py`,
`Transient/load_verify_save.py`, etc.) were excluded per instruction — throwaway
by rule, not evaluated for reachability.

## 4. Prioritized review-ready checklist

**Mark-clean now (unchanged content, or trivial/mechanical fixes already
validated by their own commit's tooling):**
- `src/RimMandrake/StarWarsRaces/Defs/HeadTypeDefs/SW_HeadTypes.xml` — not tool-tracked,
  but already validated 0/0 by `validate_patch.py` + `check_declarations.py` per commit
  `555ef84b`. No action needed from the review tool (XML isn't in its scope), but no
  further scrutiny warranted either.
- `src/RimMandrake/RaidRedesigner/Source/RM_RaidRedesignerDLL` / other unrelated
  CLEAN entries in the RaidRedesigner and bridgetools folders (the ~50 `.cs` files
  in `JawaBenchXXXTools.cs` that show CLEAN above) — untouched by this session,
  already recorded clean, nothing to do.

**Genuinely need review before the ultra pass (real logic changes, not yet marked clean):**
1. `src/RimMandrake/Oracle/Source/OracleClient.cs` — new, 302 lines, spawns a
   child process (`claude -p`) with a timeout/retry/kill-switch. Highest priority:
   new subprocess-execution surface, security- and reliability-relevant.
2. `src/RimMandrake/RaidRedesigner/Source/Patch_CaravanRobbed.cs` +
   `RaidRedesignerMod.cs` — changed patch-application strategy (manual `TryPatch()`
   behind an `IsActive` gate instead of a hard Harmony attribute) to avoid an
   eager-resolution crash across all 8 capture hooks. Correctness-critical: verify
   the gate actually prevents `PatchAll`'s attribute scan from touching this patch
   when Property is inactive.
3. `src/RimMandrake/Oracle/Source/OracleGameComponent.cs`, `OracleSettings.cs`,
   `JawaBenchOracleTools.cs`, `Oracle/About/About.xml` — supporting changes for
   the transport rewrite; review together with #1 since they share the interface.
4. `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchJobTools.cs` — small
   (5-line) but behavior-changing fix (`playerForced`); low review cost.
5. `src/RimMandrake/bridgetools/build.py` — `ORACLE_MOD_DIR` addition; low
   review cost, mechanical env-var passthrough.
6. `src/RimMandrake/Utils/gen_races_mod.py`, `src/RimMandrake/Utils/w9_run.py` —
   both carry real logic fixes (generator provenance guard; halt-on-failure
   behavior); review before trusting their next run's output.
7. Uncommitted, not yet attributed to a reviewed commit: `JawaBenchEventTools.cs`,
   `JawaBenchFactionTools.cs`, `JawaBenchTerrainTools.cs`, `JawaBenchWorldTools.cs`
   — scope these explicitly (what changed, why) before the ultra pass, since they
   weren't covered by any commit message inspected here.

**Dead / flag for deletion:** none. See §3 — every touched file is reachable.
The only "gone" file (`OracleHttpClient.cs`) is already deleted; only cleanup
item is that its stale ledger entry can be dropped next time that area is touched
(not urgent, not a code change).

## 5. Top actions to make the branch review-ready
1. Run the ultra review against the 8 files in checklist items 1–3 first (Oracle
   transport rewrite) — it's the largest new-code surface (302 new lines,
   subprocess execution) and has the most owner-doctrine riding on it
   (CLAUDE.md's "In-game LLM access" section).
2. Review `Patch_CaravanRobbed.cs`'s new gating logic next — it's a correctness
   fix for a crash that could previously take down 8 unrelated capture hooks.
3. Sweep the 4 uncommitted `JawaBench*Tools.cs` files (Event/Faction/Terrain/World)
   for what changed and why before including them in the same review batch —
   they have no commit message to anchor a reviewer's understanding yet.
4. After review, run `mark-clean` on whichever of the above pass with zero
   significant findings; that shrinks the DIRTY-333 count and narrows future
   incremental (diff-scoped) reviews.
5. No deletions needed — the reachability sweep found nothing dead in scope.
