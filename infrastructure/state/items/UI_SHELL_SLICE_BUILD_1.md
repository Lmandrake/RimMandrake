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
- [~] **§4 gate, partial**: activated `aRandomKiwi.RimThemes` +
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
      **Needs a human click** (5 seconds at the keyboard: main menu → the
      bottom-left RimThemes icon row → Utinni Shell → its select icon) to
      actually complete the visual gate, or a bridge-side engineering fix if
      this class of RimWorld mod (heavy GUI-pipeline patchers with custom
      nested `BeginGroup`/`EndGroup` layouts) turns out to be a recurring
      click-injection blind spot worth naming as its own item.
- [ ] §5 verify: `validate_patch.py --live` after a dump (only `--defs`
      static-checked this pass), VBE picker shows the menu background,
      loader shows on the next cold load — all still pending the theme
      actually being selected.

Left `doing` — the offline half is done, the gate is one human click and a
four-screenshot pass away from complete.
