# Bark Head East Fix — Vanilla Races Expanded: Phytokin — validation walk
subject: src/RimMandrake/MandrakePatches  (packageId `mandrake.rm.patches`)
feature: phytokin-bark-head-east-fix
absorbed: PhytokinBarkHeadFix (dying id rm.phytokinbarkheadfix) folded into MandrakePatches at Textures/Things/Pawn/Humanlike/Heads/BarkSkinFemale_Wide_Normal_east.png in Sprint wave A (commit 7e6eda0bd) — no longer ships alone.
deps: `vanillaracesexpanded.phytokin` (Vanilla Races Expanded - Phytokin, third-party, hard modDependency)
list: minimal+vanillaracesexpanded.phytokin
status-hint: pure loose-texture supply mod, no defs and no code — ships one missing east-facing head texture (female Phytokin, bark skin, heavy jaw) at the filename the donor's own HeadTypeDef already asks for; the donor's art existed under a " copy" filename the game never looked for

## must be true
- This mod has no ThingDef, no HeadTypeDef, no C# assembly — one loose PNG at the exact texPath
  <!-- walklint-ok: HeadTypeDefs.xml is the DONOR's (vanillaracesexpanded.phytokin) own shipped file, not ours -- never present under src/ -->
  `vanillaracesexpanded.phytokin`'s own `HeadTypeDefs.xml` (`VRE_BarkHeavy_Female`, `graphicPath` `Things/Pawn/Humanlike/Heads/BarkSkinFemale_Wide_Normal`) already declares.
- `Things/Pawn/Humanlike/Heads/BarkSkinFemale_Wide_Normal_east.png` must exist, 256x256, alpha channel identical to the donor's own male Wide east head (same silhouette, only RGB in the lip region differs — the whole proof this fix targeted the right file).
- LOAD ORDER: this mod must load AFTER `vanillaracesexpanded.phytokin` (declared in `loadAfter`) since it overrides a loose file at a path the donor's own loadFolders.xml also serves.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.patches" (the id this fix now ships under, since it absorbed into MandrakePatches) and no "Failed to find any textures at" naming `BarkSkinFemale_Wide_Normal`   # load-time
2. [D] confirm this mod is present and ordered AFTER `vanillaracesexpanded.phytokin` in the live `ModsConfig.xml` activeMods list — the fix depends entirely on this ordering
3. [D] file check (no def exists to read back): `Things/Pawn/Humanlike/Heads/BarkSkinFemale_Wide_Normal_east.png` exists under the deployed mod's `Textures/` folder, 256x256, non-blank alpha
4. [B] jawa/spawn_pawn a Phytokin with `VRE_BarkSkin` + `Jaw_Heavy` genes (confirm exact gene defNames against the live `vanillaracesexpanded.phytokin` def dump before writing the concrete spawn call — do not guess them from this file's own prose) and `gender=Female`, then rotate to `Rot4.East` and pull `jawa/pawn_portrait`/`jawa/pawn_atlas` → confirm the rendered head is NOT a mirrored front-facing view (the specific defect: "a whole head, on a colonist, every time she walks horizontally")

## [S]
The actual visual correctness of the east-facing bark head on a walking colonist (and west, mirrored from it) is the human-pass concern this mod exists to satisfy — "Failed to find any textures" never fires for one missing direction among four, so no log line can independently confirm the fix beyond step 4's rotation check.
