# VALIDATE_PATCH_BLIND_SPOTS_1 — three real gaps in validate_patch.py, found reviewing it and using it

Found in the same session, from two directions: a full-file code review of
`skills/rimworld-modding/scripts/validate_patch.py` (2514 lines), and actually running it
across all authored XML (`XML_PATCH_VALIDATION_SWEEP_1`).

## spec

1. **`MayRequire`/`MayRequireAnyOf` is never read anywhere in the file** (grep confirmed
   zero hits). Consequence: an operation guarded only by `MayRequire` (no
   `PatchOperationConditional`/`FindMod`) gets a false "unguarded" WARN, and when the
   required mod is absent a legitimate 0-match result is reported as a hard ERROR
   ("would silently do nothing") instead of the no-op treatment `Conditional`/`FindMod`
   already get. Real repo file hits this today:
   `src/SPLIT_Phase3/Jawa_Patches/Patches/ThirdPartyStunBodySize_Squared.xml`, bare
   `MayRequire`, comment states the whole file is intentionally a no-op when the mod
   is absent.
2. **Vanilla-packed-asset `texPath`s report as false ERRORs.** Vanilla RimWorld ships
   its art inside Unity asset bundles under `Data/Core|Biotech|Anomaly|Odyssey` — there
   is no loose `Textures/` folder to scan, so ANY def (ours or absorbed third-party
   content) that legitimately reuses a vanilla texPath by string will always fail the
   directory-scan check. Measured: 21 false ERRORs in one file alone
   (`src/RimStarWars/Armoury/Defs/Absorbed_KotorCore/*`), every one individually
   verified against vanilla's own Defs as a real, currently-used vanilla texPath.
3. **`check_dict_keyed_fields()` — the check for this project's own headline
   `<li>`-in-dict-field defect** (cost 101 CharacterDefs/26 BiomeDefs historically,
   `rimworld-custom-loader-li-trap` doctrine) **— only runs on the `<Patch>` code path**
   (around line 2264), not on the `<Defs>` code path (`check_def_structure`, ~1964-2074
   has no equivalent). A raw `Defs/*.xml` file with this exact defect currently passes
   clean.

Lower-confidence, same review pass, worth a look but not confirmed as load-bearing:
line 619's "unguarded modifying op" WARN only checks for `" > "` in the path, so an op
wrapped only in a bare `PatchOperationSequence` (no Conditional/FindMod) reads as
guarded and is never warned; `_guarded_by_identical_test`/`_dead_in_nomatch` (~483-537)
only recognize a direct child of `<match>`, not a `Sequence`-wrapped multi-op
add-if-missing pattern; `count_matches()` (~1289) swallows per-document exceptions with
no logging, silently undercounting on a crash; `check_value_shape()` (~1674) only
guards Add/Insert, not Replace/AttributeAdd/AddModExtension.

## verify

Each item above reproduces against a real file in this repo (named) or was
demonstrated live during the sweep (the 21-error KotorCore case). A fix should show
the same false ERROR/WARN gone against those exact files, and `selftest_validate_patch.py`
still 100%.

## criteria

1. This is a **skill script** — per CLAUDE.md ("skills/ tooling + how-to, curated in
   fresh-context passes") it is edited in a dedicated curation session, not ad hoc mid
   sweep. This item exists so that session has the findings ready, source-verified,
   not re-derived.
2. Fix #2 (vanilla texPath) is the highest-value one — it produced the most false
   positives in one real run and will keep firing on every future `Absorbed_*` file
   that legitimately reuses vanilla art.
