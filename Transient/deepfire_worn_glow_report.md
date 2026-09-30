# DEEPFIRE_WORN_GLOW_1 — build report (2026-09-30)

Status: BUILT, NOT live-proven. Nothing deployed, no game or bridge touched.
Proof to run: `python.exe src\RimMandrake\bridgetools\prove_deepfire_worn_glow.py --start`

## What was built (spec §3.4, §10 step 8)

| piece | where |
|---|---|
| Per-pawn moving light: one proxy per glowing pawn; colour = coat-weighted hue blend lit at the brightest coat's intensity; radius = highest coat. Polled every 15 ticks and moved by `proxy.Position = cell; ForceRegister`, never respawned. 250-tick sweep rebuilds after load and drops dead/unspawned pawns. No off switch. | `Source/MapComponent_DeepfireLights.Worn.cs`, `Source/DeepfireWornGlow.cs` |
| `CompDeepfire` hooks: `Notify_Equipped/Unequipped/WearerDied`; coat or colour change on worn gear refreshes the wearer's light | `Source/CompDeepfire.cs` |
| New proxy def `RM_DeepfireWornLightProxy`, category **Ethereal** (see finding 1) | `Defs/ThingDefs_Misc/RM_DeepfireLightProxy.xml` |
| Gizmo *lacquer worn item...* (Pawn.GetGizmos passthrough postfix, one per colonist) → float menu of worn apparel and equipped weapons with coats < 3 → `RM_LacquerWornItem`: fetch 3 Deepfire, go to the nearest powered `RM_DeepfirePress`, 1000 ticks × WorkSpeedGlobal, `AddCoat` | `Source/JobDriver_LacquerWornItem.cs`, `Defs/JobDefs/RM_DeepfireJobs.xml` |
| Styling station: a per-apparel *Deepfire coat (3)* checkbox next to the ideo and favourite colour buttons. It is only enabled while the colony holds enough Deepfire and the item has coats < 3. Accept queues the same lacquer job at that station. | `Source/DeepfireStylingStationPatches.cs` |
| Ranged: postfix on `ShotReport.HitReportFor` multiplies the private `factorFromTargetSize` by 1.25, clamped 0.5–2. A `GetTextReadout` postfix adds a *Glowing in the dark* line. | `Source/DeepfireCombatPatches.cs` |
| Melee: `RM_StatPart_GlowingTarget` on `MeleeDodgeChance` (XML patch, creates `<parts>`), −0.08 on the final value, with an explanation line | same + `Patches/DeepfireGlowingTargetStatPart.xml` |
| Dev actions `T: WornGlow: ...` for the proof | `Source/DeepfireWornGlowDebugActions.cs` |
| Quicktest (not run) | `src/RimMandrake/bridgetools/prove_deepfire_worn_glow.py` |

Numbers are named constants in `DeepfirePaintDefaults` (`DeepfirePaintUtility.cs`). Wiring them to Mod Settings is DEEPFIRE_MOD_SETTINGS_1's job, as for steps 6–7.

## Engine facts confirmed (RimSage)

- `CompGlower.ForceRegister` = DeRegister + Register. `GlowLight` caches `position` when it is registered, so the sequence "set Position, then ForceRegister" darkens the old rect and lights the new one. `Thing.Position`'s setter re-registers a spawned thing in thingGrid and regions itself.
- GenSpawn.Spawn: when the new thing is **Item**-category and the cell is already at `GetMaxItemsAllowedInCell` (1 on a plain cell), the existing item is **despawned and moved aside**. `GetItemCount` also counts Item-category things. SpawningWipes: an Ethereal thing that is Standable, has fillPercent 0 and is not an edifice trips no wipe rule.
- Darkness: lights accumulate additively (`CombineColorsJob.AddColors`). A light's centre cell gets `glowColor × Lerp(1 − 1/r, 1, 0.4)` (`ComputeGlowGridsJob.SetGlowFromDist`, intDist 100). `GroundGlowAt` = min(0.5, maxChannel/255 × 3.6). Our own centre contribution is subtracted from `VisualGlowAt` to get "dark without our light".
- `StatWorker.FinalizeValue` runs parts **before** `postProcessCurve`. MeleeDodgeChance's unfinalized value sits on a 5..60 scale that the curve maps to 0..0.5, so a raw −0.08 part would do nothing. The part therefore evaluates the curve, subtracts 0.08, and inverts the curve.
- `Dialog_StylingStation.DrawBottomButtons` orders `UseStylingStation` only when a style changed. A colour-only Accept only sets `DesiredColor`. So the spec's "postfix on UseStylingStation's finish" would never fire for "tick Deepfire only". The checkbox instead queues our own job at the station.
- Also confirmed via RimSage: `ThingWithComps` forwards `Notify_Equipped/Unequipped` for both apparel and equipment, and `Pawn_EquipmentTracker.pawn` and `MapPawns.AllPawnsSpawned` (IReadOnlyList) exist.

## Findings for the coordinator

1. **The existing `RM_DeepfireLightProxy` (category Item) displaces items and blocks storage.** A step-5/6 proxy spawned on a cell that holds an item moves that item aside (GenSpawn, above). Every proxy cell also counts as occupied for storage, so each coated 3×3 floor block in a stockpile loses a storage cell. Not changed here, because it was proven live and the brief says never to undo it. The worn proxy's Ethereal shape is the candidate fix once it proves out live.
2. Only the **indoor** darkness branch is exercised by the proof: roofing stands in for night. The outdoor branch (sky ≤ 0.35) is untested.
3. Only worn-gear glow counts as "glowing" for combat. Cuisine hediff glows do not.
4. The styling checkbox UI itself is not driven by the proof. The proof calls its Accept entry point (`StylingStationLacquer.QueueLacquer`). A human click-through is owed.
5. The press path's power check lives in the job and gizmo. The proof does not cover the press path: a quicktest press has no grid.

## Verification

- `dotnet build` (Release) with the Windows SDK: 0 warnings, 0 errors. DLL and .srchash regenerated.
- XML parse OK: the proxy def, the job defs and the new patch.
- `run_selftests.py`: 78/79 passed, 0 failed (1 unmeasured, `selftest_tool_metadata.py`, needs the bridge).
- `py_compile` of the proof script is OK.

## Proof (not run)

`python.exe src\RimMandrake\bridgetools\prove_deepfire_worn_glow.py --start [--x 40 --z 60]`. It covers these steps:

- A roofed baseline that must read dark.
- A walker in a 3-coat parka sampled on every 15-tick poll over 30 cells. At each sample the proxy must sit on the pawn's cell and GroundGlowAt must exceed 0.3.
- Stripping the coats, after which the pawn must go dark.
- 20 fresh coated/plain pairs, each with a higher AimOnTargetChance for the coated twin, the readout line, lower dodge and the dodge explanation line.
- A styling-station lacquer that must reach coats 1 and consume 3 Deepfire.
- A clean log.
