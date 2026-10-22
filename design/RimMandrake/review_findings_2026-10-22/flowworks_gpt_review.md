# FlowWorks GPT review, 2026-10-22 (read-only; nothing fixed)

Consults: RM_WaterLooks.cs + RM_WaterLookMath.cs + RM_SettingsReset.cs; RM_SheetMath.cs (kernel, commit ac508ba27; 77a6f18c9 itself is only a code_review ledger commit). GPT found nothing in RM_SettingsReset.cs or RM_WaterLookMath.cs. All paths under `src/RimMandrake/FlowWorks/Source/`.

| File:line | Failure scenario | Sev | Status |
|---|---|---|---|
| RM_WaterLooks.cs:116 (also :207) | DeepWaterTint and WetWallBand redraw only on the Terrain mesh flag. Water crossing 5 m / 10 m (or the band gap changing) within one terrain rung dirties nothing (RM_WaterLadder says "no terrain change"; the only Terrain dirtiers are SetTerrain calls in the excavation engine, RM_LiquidLooks.RefreshMaps and PitScorch), so tint and band stay stale. | Medium | Verified by code: no Terrain dirty on a water-level-only change. Not run live. |
| RM_WaterLooks.cs:134 | `new float[w*h]` per section per Regenerate, even for dry sections or tint off (Visible is false, but Regenerate still runs on a Terrain change). About 1.4 KB each. | Low (GC) | Verified. |
| RM_SheetMath.cs:459 (Tiers/Compact:590) | `PurgeAll` then a refill before the next `Pulse`: `Dried` is appended after the `Occ` transitions, so a consumer sees (None to Film) then (old tier to None) and clears the refilled cell's picture. | Medium | Verified by code; the kernel has no non-test callers yet, so it is latent. |
| RM_SheetMath.cs:390-393 | Sink/Receiver drain ignores `Kind.Door`; a water-filled door beside a sink or receiver drains at full rate, bypassing `DoorLeakPermille` (D4 is applied only at :309/:328). | Medium (spec deviation) | Verified. |
| RM_SheetMath.cs:267,278,509 | Every `Pulse` allocates `touched` and `seen` (bool[n]) and scans all n cells even with no water or all-asleep puddles. | Low-Med (perf) | Verified. |
| RM_SheetMath.cs:159 | `Dried` is not saved, so save-after-PurgeAll-before-Pulse loses the removal notifications. | Low | Verified, but it matches the field's own comment ("not saved"); likely intended. |

Dropped: none outright false; GPT's "no other findings" for RM_SettingsReset.cs was not independently audited.
