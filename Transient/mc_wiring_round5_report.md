# MessyConduit wiring round 5 (tap clamp per look, StandingLamp styles)

Started 2026-10-04.

## Status
DONE offline: 39c587662 source, fe0e7f78e DLL+.srchash from committed source. NOT deployed (no --apply), NOT run live.

## Findings
- Clamp art: root Aerial/TapClamp.png (Scrapper) + Aerial/Styles/{Industrial,Modern,Futuristic}/TapClamp.png. Code read only root (static tapMat).
- Lamp art: Styles/<Look>/StandingLamp.png x4. Legacy switch = Thing.StyleDef postfix returns null (StylePicker.StyleFor knows only stage-1 defs) -> unstyled keeps current art. Lamp will do the same: unstyled lamp = vanilla art.
- Built: ConduitStyles.LampDefs/IsLampDef/TapClampPath/TapLook; picker registers lamp (not a run member); 4 StandingLamp_<Look> ThingStyleDefs; guarded patch op; RM_MapComponent_Aerial per-look TapMat; selftests in StyleStage2Checks. Building next.
- winbuild 0 errors; selftest_messyconduit 577/577; validation_style --offline S0+S0b PASS (28 style defs, 30 art files). Running run_selftests.
- run_selftests 177/178: the one failure is northstar_matrix C2 (existing live shots, wire UNMEASURED), the same pre-existing failure the stage reports list.

## What was built
- Tap clamp: `RM_MapComponent_Aerial.TapLookOf(tap)` = `ConduitStyles.TapLook(RawLook(victim), DefaultLook)`, so the clamp takes the stored look of the run member it bites. A legacy (unstyled) member, hidden conduit or no victim gets the default look. `TapMat(look)` caches one material per look: Scrapper is the root `Aerial/TapClamp`, the others are `Aerial/Styles/<Look>/TapClamp`. If a look's art is missing, the root clamp is drawn and a warning is logged once. The state read is `TapPaths`.
- Floor lamp: `ConduitStyles.LampDefs = {StandingLamp}`, with 4 looks and no Modern colours. ConduitStylePicker registers it, so it gets the build-button menu, the designator getter, Copy carry and the Frame guard (StyleIndex flag). It is NOT added to `members`, because a lamp is a machine and machines end a run: no run rule, no Restyle gizmo, no bridging through a lamp. It is drawn by the 4 `StandingLamp_<Look>` ThingStyleDefs (Graphic_Single, vanilla drawSize/shadow, art `Styles/<Look>/StandingLamp`).
- Legacy lamp = same as the legacy switch. The stage-1 `Thing.StyleDef` postfix asks `StylePicker.StyleFor`, which knows only anchors and reels, so an unstyled lamp reads null and keeps the vanilla art whatever the default look is. A NEW lamp gets the picked or default look from the menu.
- Patch: a guarded CompProperties_Styleable op for StandingLamp. It normally adds nothing, because vanilla already lists the comp. With the mod removed, a saved lamp style becomes a dead ThingStyleDef reference that is dropped, and the vanilla lamp keeps working (same as switch; unproven live).
- Selftests (StyleStage2Checks): 28 names; lamp has 4 keys, takes no colour and is not a switch or conduit; the clamp path for each look; the clamp-look rule, with a can-fail showing that a global-default rule is right in only 4 of 20 pairs.
- validation_style.py `--offline` S0b: now covers the lamp style defs (art per own look), the lamp patch guard, and the lamp + clamp art (30 files). It FAILED before the defs were added (extra StandingLamp_*), which proves it can see them. No live lamp row was added.

## Unproven live / caveats
- Everything on screen: each clamp look drawn on a styled run, lamp menu icons and the lamp art at drawSize 1 (128 px art on a 64 px vanilla footprint), save/load of a lamp's style, mod-removal behaviour.
- For lamps, our designator getter overrides a non-precept ideoligion style with the picked or default look (precept-sourced designators are untouched).
- Owed: `deploy_custom_mods.py --mod MessyConduit --apply` at the next shutdown.
