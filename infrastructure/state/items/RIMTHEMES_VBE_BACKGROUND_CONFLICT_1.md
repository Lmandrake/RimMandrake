# RIMTHEMES_VBE_BACKGROUND_CONFLICT_1 — RimThemes appears to block VBE's main-menu background entirely

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

## criteria
- [x] Reproduced cleanly, isolated from our own mod's correctness (VBE
      renders fine the moment RimThemes reverts to Vanilla, same settings).
- [ ] Root cause: RimThemes intentional-suppression vs. genuine bug vs. our
      own mod's design (background should ship inside the theme, not
      alongside it via VBE) — not determined.
- [ ] Fix or workaround, once the cause is known.
