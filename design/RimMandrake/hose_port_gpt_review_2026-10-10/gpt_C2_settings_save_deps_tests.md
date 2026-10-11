## Findings

Paths below are relative to `src/RimMandrake/`.

1. **MAJOR — Steps 2–4 are not independently landable with preserved settings.**  
   **Evidence:** GSS writes the hose settings through `Hose.FireHosesMod` at `GimmeSomeSlack/Source/GimmeSomeSlackMod.cs:375` and draws its screen at `:398`. FlowWorks explicitly delegates settings serialization and drawing to its sections at `FlowWorks/Source/RimMandrakeFlowWorksMod.cs:466-473,1235`.  
   **Why:** Step 2 deletes `FireHosesMod` and its tab; import arrives in step 3, and the replacement settings screen in step 4. The intervening releases lose access to the hose controls and have no specified path for loading existing preferences. That contradicts “behaviour unchanged” and the full-settings-screen requirement.  
   **Fix:** Land the static section, serialization, screen, and import with step 2, or specify a temporary settings host that preserves all four until their replacement lands.

2. **MAJOR — Legacy unstyled reels lose their existing look.**  
   **Evidence:** `GimmeSomeSlack/Source/Aerial/StylePicker.cs:70` derives the default look from GSS’s global setting; `:73-76` makes an unstyled thing use that default.  
   **Why:** §6.3 imports only the hose settings file, while §8 introduces a Scrapper default. An unstyled reel previously appearing Modern, Industrial, or Futuristic changes appearance after migration. Preserving style defNames does not preserve this fallback.  
   **Fix:** Import the old global style once into `hose_defaultLook`, using the relevant GSS/MessyConduit settings file and enum-to-look mapping. Keep Scrapper for fresh installs. This requires no runtime dependency on GSS.

3. **MAJOR — The shared style extraction omits GSS’s bracket initialization.**  
   **Evidence:** `GimmeSomeSlack/Source/Aerial/StylePicker.cs:52` calls `InjectBracketOffsets`; `:128-141` writes per-facing offsets into both style graphics and blueprint graphics using `AerialMaterials`.  
   **Why:** §5.2 describes GSS’s replacement as thin patch classes over the shared picker, but does not retain this startup behavior. Moving it into shared code preserves an aerial dependency; dropping it changes bracket graphics and their alignment.  
   **Fix:** Explicitly retain a GSS-only registration/bootstrap and offset injector, run after its styles register. Keep the shared core free of `AerialMaterials` and preserve the GSS-facing helper API.

4. **MAJOR — The moved tests do not compile against FlowWorks’ runner as specified.**  
   **Evidence:** `GimmeSomeSlack/Source/SelfTest/HoseCarryChecks.cs:13` and `HoseLiveChecks.cs:14` call `Program.Check`. FlowWorks’ runner instead uses `Case` at `FlowWorks/Source/SelfTest/Program.cs:69`, recording one result per case at `:74,79`; it has no `Check` method.  
   **Why:** “Moved whole” plus namespace changes leaves unresolved calls. Wrapping an entire suite in one `Case` also destroys the assertion-count accounting required by §5.6.  
   **Fix:** Specify the runner adapter, invoke every moved suite from `Main`, and preserve assertion-level identities/counts separately from FlowWorks’ case count. Gate execution and failure propagation, not merely compilation or file presence.

5. **MAJOR — A separate net model cannot provide the promised production proof.**  
   **Evidence:** `FlowWorks/Source/SelfTest/Program.cs:15-25` explicitly explains why tests compile production logic instead of maintaining a transcription. `FlowWorks/Source/SelfTest/SequenceFuzz.cs:6-8` explicitly distinguishes its test-side composition from the game’s grid walk.  
   **Why:** §5.6 proposes a Verse-free *model* of the new net. That model can pass while production seeding, traversal, route recording, or cache logic is wrong. Existing stock/channel tests do not close this gap. Its timing also cannot establish production net cost.  
   **Fix:** Extract a Verse-free production net kernel used by `RM_LiquidNet` and compile that same source into SelfTest. Test routes, disabled links, freshness, and repeated tank selection through it. Treat any independent model as an oracle, and measure game-side overhead separately.

6. **MAJOR — Step 1’s visibility gate is impossible for the intended implementation.**  
   **Evidence:** `GimmeSomeSlack/Source/Core/CordMath.cs:36-38` declares public operators on `Cell`. Those operators must remain `public static` even when `Cell` becomes internal. Existing shared types likewise have public members inside internal types, for example `_Shared/SettingsKit/SettingsKitCore.cs:23-29`.  
   **Why:** `grep "public " _Shared/SlackGeometry == 0` rejects a correct extraction. Changing every member to internal would make the operators invalid C#.  
   **Fix:** Check type visibility rather than all member modifiers: require internal top-level types and audit exposed APIs. Retain required public operators, overrides, and interface implementations inside those internal types.

7. **MAJOR — Essential compatibility patches have no specified safe failure path.**  
   **Evidence:** `_Shared/HarmonyResilience/PatchApplier.cs:88-94` catches patch failures and continues. Classes without a feature setting switch nothing off (`:28-30`). Its own limitation requires a setting gate for surviving partial patches (`:17-18`).  
   **Why:** §8 makes save-skip and type alias unconditional but prescribes only a red log on failure. The installer supplies no stronger guarantee. The design itself states that failed save-skip writes the component into saves; logging does not preserve that invariant. The actual save-skip implementation is outside this slice.  
   **Fix:** Specify individual target/patch success checks and an explicit fallback for each essential patch. Prevent hose map-state initialization without working save suppression; use unconditional compatibility shims or another reliable fallback for legacy driver resolution. Include the pipe-def alias in this critical-patch policy.

## Design claims verified

- Both production projects use explicit compile lists; their supplied references contain no GSS↔FlowWorks assembly dependency.
- Internal source-linked shared types match the SettingsKit and HarmonyResilience precedent.
- The style picker really has all five named Harmony patches and registers the reel beside aerial anchors.
- GSS already uses `PatchApplier` (`GimmeSomeSlackMod.cs:359`); the independent review’s PatchAll characterization is stale.
- GSS’s legacy prefix rewrites `ref typeName`; its mapping supports the proposed namespace-prefix composition.
- `LegacyName.SettingsHandles` includes `FireHosesMod`, and migration copies files without deleting originals.
- FlowWorks already exposes `RM_Liquid_FreshWater` through DefOf.
- EnvironmentalHazards supplies the proposed def-name postfix pattern; its engine rationale is documented in comments.

## Outside this slice

- Net merging/splitting, pumps, reach, transfer call sites, converters, adapters, reactions, baths, multi-liquid behavior, relay traversal, topology freshness, and production performance.
- Hose runtime code: save suppression, Scribe keys, driver state, port caches, flow providers, tint, and disable/re-enable behavior.
- Actual hose settings defaults, the 17/15-key census, `MigrateMaxLength`, and the universal-pipe setting migration.
- Engine behavior for `curDriver`, type-name lookup, duplicate defs, and generated blueprint/frame names. The supplied review and comments are not engine code.
- Mixed-version detection reliability, deployed build staging, validation/proof manifests, toggle rows, and pre-port save fixtures.
- Reported test totals and live results; no suites were executed.