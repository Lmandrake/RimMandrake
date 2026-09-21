# RIMTHEMES_VBE_BACKGROUND_CONFLICT_1 — RESOLVED: RimThemes has its own native background slot, use that instead of VBE

**Root cause found and fixed, 2026-09-05, same day as filing.** Not a bug,
not a mod conflict — our own mod was using the wrong channel. Decompiled
`aRandomKiwi.RimThemes.UI_BackgroundMain_Patch` (the live installed DLL,
RimThemes NX rev10): it Harmony-prefixes vanilla's `Verse.UI_BackgroundMain
.BackgroundOnGUI` and, whenever a non-Vanilla theme is active, **returns
`false`, fully replacing vanilla's own background draw with the theme's
own asset** — looked up by the literal texture key
`Themes.getThemeTex("UI_BackgroundMain", "BGPlanet", ...)`, plus a
directory scan of the theme's own `Textures/` folder for any file starting
`UI_BackgroundMain.BGPlanet` ending `.webm` (RimThemes' own first-party
animated-background feature, independent of and unrelated to VBE). VBE's
own background code never runs in this branch at all — this is why VBE's
`current`/`allowAnimated` settings, all separately confirmed correct, never
mattered.

**A web search independently corroborated this** (RimThemes' GitHub +
Steam Workshop discussion), including confirming VP8 (not VP9) is the
documented required codec since "RimThemes NX rev5" — matching the codec
bug already found and fixed in `UI_SHELL_SLICE_BUILD_1` by direct
measurement, good independent confirmation of both findings from a
different source.

**Fix**: shipped our menu background under RimThemes' own naming
convention instead of (in addition to) VBE's —
`RimThemes/Utinni Shell/Textures/UI_BackgroundMain.BGPlanet.png` (static
fallback) and `UI_BackgroundMain.BGPlanet.webm` (the animated loop, same
VP8 file already built). **Verified live**: main menu now shows the full
Ishko-gate scene with Utinni Shell active, and the animated loop is
confirmed actually playing — two screenshots 2 seconds apart show the
pulsing-eye glow at different points in its cycle (a static asset could
never do that). VBE's own `RUT_BG_ShellIshkoGate` def is left in place
unchanged — it still serves players on Vanilla theme or other
non-conflicting themes via VBE's normal rotation.

**The owner's "Star Wars mods" collision concern, checked**: live
`jawa/harmony_patches` against `UI_BackgroundMain.BackgroundOnGUI` on the
minimal test list shows exactly one patch — RimThemes' own. No collision
found on this list. **Caveat, not fully closed**: this was checked on the
21-mod minimal list, not the owner's full 596-mod stack (which includes the
RimStarWars-tier mods the concern was about) — a full-stack
`start_debug_game_ready` check is currently blocked by the separate,
already-filed `NINEFOLD_DEBUG_GAME_READY_CRASH_1` crash. The mechanism
itself (a directory scan scoped to each theme's OWN folder, keyed by that
theme's own id string) makes a real collision unlikely unless another
active mod ships an actual RimThemes theme reusing the exact same theme
name/id, which no known SW-tier mod does — but this is inference from the
mechanism, not a full-stack live check.

---

_Original filing, superseded by the fix above — kept for the investigation trail:_

While verifying `UI_SHELL_SLICE_BUILD_1`'s animated menu background
(2026-09-05), found a structural incompatibility: **VBE Backgrounds'
main-menu background renders solid black whenever a non-Vanilla RimThemes
theme is active**, independent of anything about our own mod's def, video
encoding, or settings — all of which were separately confirmed correct.

## What was measured

On the minimal 23-mod list (`brrainz.harmony` + core DLCs + `vanillaexpanded.backgrounds`
+ `aRandomKiwi.RimThemes` + `mandrake.rut.shell`, nothing else UI-related to
interfere):

- `mandrake.rut.shell`'s `RUT_BG_ShellIshkoGate` def confirmed live via
  `jawa/get_defs`: `animated: true`, correct `path`/`iconPath`, no config
  errors, no `[VBE] Could not load video` error.
- `VBEMod.Settings` (`vanillaexpanded.backgrounds`'s own settings object,
  read/written via `rimworld/get_mod_settings`/`update_mod_settings`)
  confirmed persisted to `Config/Mod_2775017012_VBEMod.xml`:
  `allowAnimated=True`, `current=RUT_BG_ShellIshkoGate`, `cycle=False`.
- With RimThemes' `curTheme` = `mandrake.rut.shell§Utinni Shell`: main menu
  background is **solid black**, every time, across three separate cold
  restarts (one before the codec fix below, two after).
- With RimThemes' `curTheme` = `Vanilla` (theme picker, same real-OS-click
  method as `UI_SHELL_SLICE_BUILD_1`), **identical VBE settings otherwise
  untouched**: the main menu immediately shows a normal VBE background (a
  cat-on-a-fence sunset image from VBE's own rotation pool — not proof our
  specific video played, since `current`+`cycle=False` should have pinned
  ours, but decisive proof VBE's rendering path is alive and painting
  SOMETHING only once RimThemes stops intercepting it).

## What this is not

- **Not a bug in our video or def.** Confirmed correct at the XML/settings
  level independent of this issue (see `UI_SHELL_SLICE_BUILD_1`'s own
  write-up for the VP9→VP8 codec fix and the deploy-drift catch, both real
  and separately fixed).
- **Not new breakage from this session's animation work.** The same
  RimThemes-active-suppresses-VBE behavior would apply to the ORIGINAL
  static Ishko-gate PNG just as much as the new webm — nothing about
  `animated=true` specifically triggers it (the black screen was already
  reproduced before the codec fix, under the exact same "Utinni Shell
  active" condition).

## Open questions, not chased further this pass

- Does RimThemes suppress VBE's background drawing INTENTIONALLY (e.g. a
  theme is expected to ship its own `isTheme`-flagged background, and VBE's
  own picker skips those with the "returning empty string... part of a
  theme" log line seen for RimThemes' bundled themes) — meaning our mod's
  actual design flaw is trying to pair a RimThemes theme with an
  independent VBE background at all, rather than shipping the background
  AS PART OF the RimThemes theme package?
- Or is this a genuine compatibility bug between the two mods that a real
  player with both active would also hit, unrelated to our own mod?
- Either way: **has the Ishko-gate background ever actually been visible
  during real play with Utinni Shell selected?** `UI_SHELL_SLICE_BUILD_1`'s
  earlier BENCH pass proved themed BUTTONS post-restart but the record
  doesn't show a background-visible confirmation captured at the same time
  — worth checking whether this was already silently broken.

## criteria (all from the original filing — see the RESOLVED section above)
- [x] Reproduced cleanly, isolated from our own mod's correctness (VBE
      renders fine the moment RimThemes reverts to Vanilla, same settings).
- [x] Root cause: our own mod's design — the background belongs inside the
      RimThemes theme package (`UI_BackgroundMain.BGPlanet.*`), not
      alongside it via VBE. Confirmed by decompile, not a RimThemes bug.
- [x] Fix shipped and live-verified (see above). Full-modlist collision
      check with the RimStarWars-tier mods still owed, blocked on the
      separate `NINEFOLD_DEBUG_GAME_READY_CRASH_1` crash.
