Fresh independent read-only Opus5.5 acceptance. Exact whole brief: evidence/judge_input.txt; call provenance: evidence/judge_call.json; original envelope: evidence/judge_raw.json. Result below is copied verbatim.

**Verdict: accept.** The repair is already in current production source, the offline checks run the real production methods and fail when the repair is removed, and source and shipping identity are recorded and unchanged. I hashed nothing myself (read-only tools only), so all hash claims below rest on the recorded readbacks.

## Bullet 1 — production invalidates carried, unlaid and retracting routes, including the shadow index; laid lower hoses still cast shadows: **accepted**

- **Carried:** in shipping mode (when `LegacyFrame` is off), a carried hose's cached route is dropped before the carried trail is drawn (`RM_MapComponent_Hoses.cs:1636`).
- **Unlaid:** a hose with no lay drops its route before being marked as drawing nothing (`:1646`).
- **Retracting:** a winding hose drops its route before the cache lookup (`:1670`). It also never re-caches while winding, because its key stays null (`:1721`). So it cannot rejoin the shadow index, and it casts no shadow itself (`:1760`).
- **What a drop does:** `DropMeshes` (`:1794`) destroys the cached meshes, removes the cache entry and calls `crossIndex.Drop`. That call (`HoseCrossShadows.cs:108-113`) removes the strand and marks every nearby upper hose as needing a re-check.
- **Upper hoses recover:** on re-check, the dropped strand's id is gone from the lower set, so the key changes (`:178`). The spans are rebuilt, and `BuildCrossMesh` destroys the old shadow mesh and clears it (`:1931-1932`). With no spans left, no shadow is drawn (`:1909`).
- **Laid lower hoses stay:** they keep their index entry. Lower sets still require a strictly lower rank (`:174`), and rank moves mark neighbours for a re-check (`:2095-2099`).
- **No path leaves the index out of step with the cache:** every place the cache is cleared or removed also updates the index (`:164-165`, `:183`, `:1070`, `:1794`).
- **Legacy versus shipping:** the legacy comparison mode skips these three drops on purpose, and its all-pairs scan keeps the original behaviour (`:1896-1907`). The shipping default is off.

## Bullet 2 — production-linked offline checks that reject regressions, with source and artifact identity recorded: **accepted**

**What the harness tests.**
- `HoseShadowHarness.targets` copies the seven whole production methods (`DrawAll` through `BuildCrossMesh`) into the test build every time it compiles. `HoseShadow.generated.txt` contains the exact drop lines.
- The real `HoseCrossShadows.cs` is compiled in (`csproj:197`). Only lay discovery, ranks, rendering and the clock are substituted.
- There are nine HS cases:
  - carried, unlaid and retracting transitions, each run in both upper-first and lower-first draw order;
  - budget deferral, then draining, then a repeated drop;
  - rank toggling and a re-laid hose with the same key;
  - legacy versus shipping.
- The cases check an independent all-pairs oracle and a live lower hose that keeps its one real crossing (`:191-192`).

**Actual test results.**
- Focused run (focused3): 10/10 cases plus HoseCarryChecks 41/41, return code 0.
- Standard runner: `run_selftests.py --only selftest_flowworks_stock.py --workers 1` was GREEN. It ran with 0 cached passes, 1287/1287 C# cases and 457/457 hose assertions.

**Negative controls.** Each variant mutated only the external test stage, compiled cleanly, failed on a real behaviour assertion, and the stage was restored byte-exact.

| Variant | Failed cases |
|---|---|
| Carry drop removed | Carry transitions and the legacy/shipping case ("transition removes full-route mesh and strand") |
| Unlaid drop removed | Unlaid transitions |
| Retract drop removed | Retract transitions |
| `DropMeshes` keeps the index entry | All 9 |
| Index drop doesn't remove the strand | All 9 |
| Index drop doesn't mark neighbours | All 9 |
| Rank comparison reversed | All 9 |
| Old shadow mesh not cleared | Budget case and rank case ("drawing destroyed mesh") |

The "original" controls rebuild the pre-fix behaviour by deleting each drop line from the current file, not by compiling the historical commits. The published parent sources are kept under `raw/original/` for provenance.

**Identity.**
- `RM_MapComponent_Hoses.cs` hashes to `bc4d5b8e…` and `HoseCrossShadows.cs` to `45307b36…`. Both are identical in the before, pre-proof and after manifests.
- The shipping build stamp's expected value for `RM_MapComponent_Hoses.cs` equals its actual value, so the shipping DLL was built from the tested source.
- DLL `ec29517d…`, stamp `b1375866…` and the installed `Assembly-CSharp.dll` (`5cf1b5be…`) are unchanged.
- The only changed paths are four SelfTest files.

## Bullet 3 — fresh broaden and judge; GSS cord look and shipping art preserved; live behaviour unverified: **accepted, for the judge and preservation parts**

- No shipping C# changed and no build was run. All 181 texture paths in the manifest are unchanged, so the approved GSS cord appearance and shipping art can't have moved.
- Live rendered behaviour is explicitly not claimed.
- A broaden record exists, but as instructed I didn't read it. Its content and independence are outside this judgement.

## Remaining limits (none blocks acceptance)

1. **One stale frame in upper-first order.** An upper hose drawn before the dropped lower one shows the old shadow for one frame. The pending re-check is kept, and the harness asserts this.
2. **Budget deferral can stretch that.** When the frame's shadow budget is spent, the old shadow survives until a later frame scans it. Progress is guaranteed because the budget resets every frame and the deferred reel is drawn first next time.
3. **Retracting hoses get no shadow at all.** Upper hoses cast nothing onto the still-visible part of a hose being wound in. This is an under-shadow, not a phantom one, and it is outside "laid" hoses.
4. **The harness uses stand-ins.** It runs extracted methods against substitutes for the game and engine. Unity mesh lifecycle, real job and save flows, and a carried hose with an empty trail are not exercised.
5. **The standard runner flagged its test script as "changed during the run."** It reported `selftest_flowworks_stock.py` as not recordable for that reason. The receipt's content hashes are unchanged and the result was GREEN, so this looks like a bookkeeping flag, not a content change. I didn't confirm its cause.
6. **No live rendered certification exists, and none is claimed.**

would show: yes