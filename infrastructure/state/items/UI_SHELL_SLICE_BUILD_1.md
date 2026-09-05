# UI_SHELL_SLICE_BUILD_1 — vertical slice landed, coexistence gate owed

Build the RimUtinni Shell vertical slice per `ui_shell_spec.md`:
`mandrake.rut.shell` theme mod (3 button atlases + palette meta.xml), 1
loader + 1 menu-bg art, RimThemes-coexistence gate on next load.

## 2026-09-05 (FOUNDRY, offline while the bridge was free) — landed commit `abd9fba2`

Found the build already complete and settled in the shared working tree
(files untouched for ~2 hours — not mid-write) when this item was claimed.
Verified rather than re-authored:

- `About/About.xml`, `Defs/VBE_Backgrounds_Utinni.xml` — well-formed, cite
  the real `aRandomKiwi.RimThemes`/`vanillaexpanded.backgrounds` packageIds
  (both confirmed present in the owner's live full modlist), `MayRequire`
  correctly gates the VBE def.
- `meta.xml` — the 10 palette keys named in spec §2, values match §1's
  table.
- All 7 shipped textures dimension-checked against the vanilla sizes the
  spec documents: 64×64 (3 button atlas states), 75×75 (Command.BGTex),
  10×10 (LoaderBar/TextBar), 96×96 (Icon) — all exact matches.
- Button atlas: the live one is `_artsrc/options/B_clean`, byte-identical
  (confirmed via `cmp`) — the generator's own algorithmic default; two
  alternates (`A_heavy`, `C_chalk`) are still on disk with a contact sheet
  for the owner to override if he prefers a different one.
- The two AI-generated pieces (menu background: Ishko at the temple gate;
  loader: amber tactical orrery display) — looked at both directly, both
  match their own recorded prompts and the reference art convincingly.

**Fixed before committing**: four `.gitignore` files were excluding ALL
shipped art as "regenerable derived output". True for `gen_textures.py`'s
seeded, deterministic PIL atlases — **not true** for `gen_bg.py`'s two
AI-generated pieces, which that script's own header admits are
non-reproducible on a re-run. Gitignoring them would have silently lost
real shipped game content on a fresh checkout, inconsistent with this
repo's own convention of committing final art (e.g. `RimStarWars/Cuisine`'s
icons). Removed those four `.gitignore`s; kept `_artsrc/`'s own (raw/
generation intermediates and options/ rejects are genuine scratch material,
not shipped content).

## criteria
- [x] Mod skeleton, theme, and art built (offline half of spec §2/§3).
- [x] Shipped art actually committed, not silently gitignored.
- [x] **§4 gate — RESOLVED** (see the 2026-09-05 real-OS-click entry below):
      activated `aRandomKiwi.RimThemes` +
      `mandrake.rut.shell` in the live ModsConfig (596 mods now), restarted,
      confirmed both load with **zero errors** (`Player.log` grepped clean
      for either packageId). RimThemes' own theme picker
      (`Dialog_ThemesList`, opened directly via
      `rimworld/open_window_by_type` since the main menu's own button row
      isn't reachable through `get_ui_layout`/`click_ui_target` — it's drawn
      by `MainMenuDrawer` directly, not as a `Window`) **correctly discovers
      "Utinni Shell"** with its real name, description and icon pulled from
      `meta.xml`.

  **2026-09-05 (FOUNDRY), deeper pass — root cause narrowed, still unresolved.**
      Two things that looked like plausible culprits are now RULED OUT by
      decompile (`ilspycmd` against the live `RimThemes.dll`,
      `1668983184/1.6/Assemblies/`):
      - `Widgets_ButtonImage_Patch` (the obvious suspect) only patches the
        **6-arg** `Widgets.ButtonImage(Rect, Texture2D, Color, Color, bool,
        string)` overload. The select-icon button in `Dialog_ThemesList`
        calls the **4-arg** overload (`Rect, Texture2D, bool, string`) —
        completely unpatched, runs stock vanilla code. Not the interceptor.
      - `WindowStackOnGUI_Patch`'s per-frame "only the topmost layer-1 window
        draws" gate doesn't apply either: with only `Dialog_ThemesList` open
        (plus the debug-toolbar `ImmediateWindow`, a different layer), it's
        trivially the sole layer-1 window and always wins the "topmost" check.
      A REAL bug was found and is now understood: the bridge's `targetId`
      embeds a frame/surface generation number
      (`ui-element:<surface>:2:<n>`) that **increments continuously** even
      with no clicks happening — a `targetId` captured by `get_ui_layout` and
      then used a few hundred ms later in `click_ui_target` times out
      ("Timed out waiting ... to be redrawn") because that exact generation
      no longer exists. Fetching the target immediately before the click
      fixes this and produces a clean `success: true` — a real, generally
      useful finding for anyone else driving dialogs through this bridge.
      **But even with a fresh, non-stale target and a `success: true` /
      non-timeout click: the theme selection still does not take effect.**
      Proven definitively this pass, not just inferred: opened the dialog,
      screenshotted it (`Transient/rimthemes_after_click.png` — not
      committed, Transient convention), clicked Utinni Shell's select icon
      (fresh target, `success: true`, message "Activated an icon button...
      UI state did not change"), screenshotted again — **the selection
      marker never moved off "Centipede"** (the colourful hex icon stays on
      Centipede's row; Utinni Shell's icon stays the plain grey unselected
      hex). Repeated against **Vanilla** as a control (not our mod, to rule
      out something Utinni-Shell-specific) — same result: click reports
      success, selection marker doesn't move. **This is a general
      RimThemes-dialog click-injection gap, not specific to our theme or to
      a target-mapping bug** — the click is delivered and accepted by Unity
      IMGUI (no timeout, a real `ButtonInvisible`-equivalent presumably
      returns true) but `Themes.changeThemeNow` (or its precondition) isn't
      firing through to `Settings.curTheme`. Not chased further into
      `Themes.changeThemeNow`'s own body this pass — worth a look if anyone
      picks this up again, but likely an IMGUI hot-control/event-consumption
      interaction between the bridge's synthetic input and RimThemes' custom
      `GUI.BeginGroup`/`EndGroup` nesting around each row, not something
      fixable from the tool-call side.
      **RESOLVED, same pass, without a human click.** The owner was away
      from the keyboard and suggested "consider computer usage" — instead of
      the bridge's semantic `click_ui_target` (which only simulates a click
      to RimWorld's own input handling), drove the REAL OS mouse: Windows
      `user32.dll` via `ctypes` (`SetProcessDpiAwareness(2)` first — without
      it, `GetWindowRect`/`GetClientRect` return virtualized 96-DPI
      coordinates and every computed screen point is wrong on this
      multi-monitor, scaled setup), `SetCursorPos` + `mouse_event`
      LEFTDOWN/LEFTUP at the real screen coordinates (RimWorld's window was
      already OS-foreground; UI-space coordinates from `get_ui_layout`
      mapped 1:1 to logical screen pixels once DPI-awareness was set, no
      scale correction needed). **Worked on the first attempt** — confirmed
      by two screenshots: the dialog itself re-skinned live the instant the
      click landed (its own "Supported by" button, row highlighting, and
      the Utinni Shell row's select icon all switched to the selected/brass
      look), and after closing the dialog with a second real click, the
      **main menu now renders the Utinni Shell button atlas** and the
      bottom-right RimThemes indicator shows our icon as active. This
      strongly confirms the earlier root-cause theory (an IMGUI
      hot-control/event-consumption gap specific to the bridge's synthetic
      injection path) rather than anything wrong with the target mapping or
      RimThemes itself — a real OS click sails through with no special
      handling needed. Worth a `rimbridge-companion` note: for dialogs from
      mods with heavy custom GUI patching, a real `SendInput`-based click is
      a working fallback the bridge doesn't offer natively yet.
- [ ] §5 verify, remainder: `validate_patch.py` doesn't actually apply here
      (`VBE_Backgrounds_Utinni.xml` is a plain `BackgroundImageDef`, not a
      `PatchOperation` file — nothing for that tool to check). VBE
      Backgrounds ships no assembly and no picker dialog for this def type
      (confirmed: no DLL under the mod's workshop folder) — it's rotated in
      randomly by VBE's own main-menu background system, so "shows in the
      picker" isn't a real verification step; the honest check is "does our
      background ever get drawn," which needs either several main-menu
      reloads (nondeterministic) or reading VBE's own selection code. Not
      done this pass. **Loader art on a cold load** is still genuinely
      pending — needs an actual ~25-minute cold load with the full modlist,
      not a quicktest.

Left `doing` — the offline half is done, the gate is one human click and a
four-screenshot pass away from complete.

## 2026-09-05 (BENCH, owner-authorized takeover after FOUNDRY's seat was
OOM-killed) — §5 remainder in progress

- **VBE background question SETTLED by decompile** (subagent, `ilspycmd` on the
  live workshop DLL; scratch at `/tmp/vbe_decomp/`). Corrects the earlier "VBE
  ships no assembly / no picker" note: workshop folder `2775017012` ships
  `1.6/Assemblies/VBE.dll`. `VBESettings.Allowed()` gates only on: def resolved,
  `enabled[defName]` (defaults **true** via `CheckInit()`), not-animated, and no
  pinned `current`. Defaults are `randomize=true, cycle=true (10–15s),
  current=null`, and **no VBE settings file exists in Config/** — install runs
  on code defaults. So `RUT_BG_ShellIshkoGate` is in the live rotation pool
  as-shipped, and TWO user-facing pickers list it
  (`HarmonyPatches.DoMenuBackgroundButton` float menu; `VBEMod.
  DoSettingsWindowContents` thumbnail grid). Spec §5's "shows in VBE's picker"
  is therefore checkable in-game after all.
- **Theme persistence PROVEN on disk**: `Config/Mod_1668983184_RimThemes.xml`
  carries `curTheme>mandrake.rut.shell§Utinni Shell` — FOUNDRY's OS-click
  selection survived the session.
- **Full-stack session log is clean for our mod**: preserved at
  `Transient/Player_log_quicktest_crash_2026-09-05.log`; exactly one mention of
  `mandrake.rut.shell` (the mod-list line), no error naming it or Utinni Shell.
- ⚠️ **`rimworld/start_debug_game_ready` KILLED the 596-mod game** — log stops
  mid-quicktest-setup (Ninefold research grants), no managed exception, no
  Unity crash dump (latest is Sep 1). Cause UNMEASURED. The 2026-08 measurement
  (78.5 s on 580 mods) no longer guarantees safety at this stack size.
- Cold load relaunched (the load §5 was owed anyway); loader-art capture loop
  running (`Transient/loadercaps/`). Mid-load frame already shows the amber
  tactical orrery loader art rendering on the real stack.

## 2026-09-05 (BENCH) — cold-load verdicts. §5 is done except two map shots.

- **Loader art on a real cold load: MEASURED PASS.** The 596-mod load rendered
  the amber tactical orrery full-screen; captured frames
  (`Transient/loadercaps/`, full-res `Transient/foundry_window_check2.png`)
  match `_artsrc/raw/loader_tactical_raw.png` element-for-element (Star
  Destroyer inset, glyph clusters, orrery rings).
- **Theme persistence across restart: MEASURED PASS.** Twice over: RimThemes
  config carries `curTheme>mandrake.rut.shell§Utinni Shell` pre-launch, and
  post-restart the picker shows the colourful selected-hex on Utinni Shell's
  row (screenshot `rimbridge_20260905_151314.png` in the game's Screenshots
  folder) while every other theme wears grey. Dialog chrome renders themed.
- **Runtime def presence: MEASURED PASS.** `jawa/get_defs`
  `VBE.BackgroundImageDef/RUT_BG_ShellIshkoGate` → found, label intact
  ("1 of 1 def(s) resolved"). With the decompile eligibility analysis above,
  the background is in VBE's live rotation pool and both pickers.
- **Post-restart log: clean.** No error naming the mod; the two "Utinni"-ish
  config errors are the pre-existing AdvancedShowers/VCE_StewCooking research
  coord collision on `RUT_Tree_Hearth`, not the theme.
- Clean themed-menu shot post-restart: `rimbridge_20260905_151441.png`.
  ⚠️ Honest note: B_clean is vanilla-faithful wood, so the menu-button skin is
  not visually distinguishable from vanilla in a still; the selected-hex +
  active indicator carry the proof. A B_clean mouseover (strong amber) hover
  test came back inconclusive — likely focus mechanics, not evidence against.
- **Remaining, deferred to a map session:** themed **gizmo row** and **float
  menu** screenshots (§4's last two surfaces) plus RimHUD/Dubs sanity — needs
  a map, and `start_debug_game_ready` on the full stack killed the game once
  today with host RAM at 9.4 GB free. Ride the next load round, a
  minimal-list+theme restart (22 s), or a moment with host headroom.
