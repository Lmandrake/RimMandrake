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
