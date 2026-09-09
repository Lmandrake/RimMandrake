## symptom
Owner, 2026-09-07, on a screenshot after the worldmap import: **"the labels are
now HUUUGE"**. Region names (Sunreach, Gray Sea, Ashen Wastes, South Crags,
Umbra, Cinderdark) are drawn across huge arcs of the globe and overlap each
other. Settlement names render normally — it is only `WorldFeature` labels.

Screenshot: `C:\Program Files (x86)\Steam\userdata\40784075\760\remote\294100\screenshots\20260907154916_1.jpg`

## MEASURED 2026-09-07 (live, `jawa/world_features_get`, 71 features)

| feature | maxDrawSizeInTiles |
|---|---:|
| Deadstone | **99.6** |
| Dune Sea | **90.5** |
| Glare | 65.2 |
| Kiln | 65.2 |
| Nightspill | 64.3 |
| Twilight Sea | 64.2 |

**max 99.6 · min 8.8 · mean 34.1** across 71 features on a 21,872-tile planet.

## root cause — arithmetic, and it checks out

`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchWorldTools.cs:4614`

```csharp
f.maxDrawSizeInTiles = Math.Max(6f, (float)Math.Sqrt(kv.Value.Count) * 2.2f);
```

Vanilla, `FeatureWorker.cs:94`: `maxDrawSizeInTiles = bestTileDist * 2f * 1.2f`
— i.e. **2.4 × radius**.

A roughly circular region of `A` tiles has radius `r ≈ sqrt(A/π) = sqrt(A)/1.7725`.
So vanilla's `2.4r` = **`sqrt(A) × 1.354`**.
⇒ **our 2.2 multiplier is 1.63× vanilla.**

✅ **Confirmed against the live numbers**: the Dune Sea is 1,692 tiles;
`sqrt(1692) × 2.2 = 90.5`, which is exactly what the game reports.

## fix

```csharp
f.maxDrawSizeInTiles = Math.Max(6f, (float)Math.Sqrt(kv.Value.Count) * 1.35f);
```
Predicted after the change: Deadstone ≈ 61, Dune Sea ≈ 55.5, mean ≈ 21.

⚠️ **That alone may not be enough, and the owner should look before we call it
done.** There are TWO contributors and only one is a bug:
1. our multiplier is 1.63× vanilla (a defect — fix it);
2. **our regions are genuinely enormous** — 71 features over 21,872 tiles, so
   ~308 tiles each, where vanilla's features are typically far smaller. Even at
   vanilla's own formula a 1,692-tile sea earns a 55-tile label.

⇒ After the multiplier fix, if it still reads too big, the answer is a **cap**
(or splitting the largest regions), not a smaller multiplier — a multiplier below
vanilla's would misdraw the small features to fix the big ones.
🔑 **Judge it by LOOKING at the globe, not by the number.**

## a second formula exists — do not let them drift apart
`src/RimMandrake/Utils/ashkarr_paint.py:1041` computes the same field a different
way: `round(2.0 * spread / 1.35, 1)` (angular spread ÷ mean tile spacing).
Whichever path writes features must be the only one that owns this, or the labels
change size depending on which tool last ran.

## gates
C# in the companion DLL ⇒ build + deploy in a game-DOWN window, then a restart.
Cheap to verify afterwards: `jawa/world_features_get` + one screenshot of the globe.

## UPDATE 2026-09-09 (FOUNDRY) — C# fix confirmed, Python formula reconciled, deploy still owed

**C# fix**: already source-committed (found already in place this pass, at
`864ac9a5`, before this pass started — the prior note in this item's history
misnamed the commit as `b0e18f89`). Rebuilt the companion DLL locally
(`python.exe src/RimMandrake/bridgetools/build.py`, plan-only, no `--apply`):
**0 Warning(s), 0 Error(s)**. Not deployed — the game is up; deploy plan also
shows the built DLL is missing the GM tool pair (`--gm` was off) and would
regress several live tools, so a deploy from this build needs the full
`build.py --gm --apply` flow anyway, done in a game-down window per this
item's own gates.

**The "no drift" note above (2026-09-09T03:39:05Z) was wrong** — it saw `1.35`
in both files and called it confirmed-matching without reading what the
number multiplied. Actually traced it this pass:
- `ashkarr_paint.py`'s old formula, `round(2.0 * spread / 1.35, 1)`, used
  `1.35` as a divisor on the largest-connected-component's angular spread in
  degrees — a different input and a different operation than the C#'s
  `sqrt(regionTileCount) * 1.35`. Same digits, unrelated formula. It only
  looked consistent by coincidence of both authored the same day.
- Traced consumers to find which formula is actually live: `w9_run.py` (the
  only caller of `jawa/world_features_import`) feeds it `ASHKARR_WORLDMAP_tiles.csv`
  — the importer (`JawaBenchWorldTools.cs`) groups that CSV's `region` column
  and computes size **itself**, `Math.Max(6f, sqrt(count) * 1.35f)`. It never
  reads `_meta.json` or any precomputed size field at all.
- The offline SVG renderer (`worldview.py`'s label pass) also computes its own
  independent font-size, `max(11, min(28, 5.6*sqrt(tileCount)))`, and likewise
  never reads `_meta.json`'s `maxDrawSizeInTiles`.
- Conclusion: `_meta.json`'s `features[].maxDrawSizeInTiles` (written by
  `ashkarr_paint.py`'s `write_bundle()`) is **not consumed by anything that
  draws or writes a live label** — it was dead weight that happened to drift
  from the value the game will actually use, which is exactly the trap this
  item warned about ("labels change size depending on which tool last ran").
- **Fix applied** (option a): `src/RimMandrake/Utils/ashkarr_paint.py` now
  computes that field with the corrected C# formula exactly —
  `round(max(6.0, sqrt(len(tiles)) * 1.35), 1)`, using the same
  full-region tile count the C# importer groups by (`len(tiles)`, already
  stored alongside as `"tiles"`) rather than the unrelated angular-spread
  quantity, which was removed as unused. `python3 -m py_compile` clean.
  This makes the metadata field an accurate prediction of what
  `world_features_import` will write, even though nothing currently reads it
  back — so a future consumer (or a human reading meta.json) isn't misled.

**Still owed**: deploy the built DLL (`build.py --gm --apply`, game-DOWN
window), restart, then verify by LOOKING — `jawa/world_features_get` numbers
+ a globe screenshot, per this item's own gates. Not attempted here; game is
currently up and in active use.
