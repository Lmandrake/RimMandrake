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
      `meta.xml`. Could NOT get the bridge to actually SELECT it:
      `Themes.changeThemeNow` (decompiled via `ilspycmd`, confirmed exact
      mechanism) fires from a `Widgets.ButtonImage` click at a specific rect
      inside the dialog; `rimworld/click_ui_target` reports success against
      that exact target (verified twice, correct target-id-to-rect mapping
      confirmed against the decompiled row-layout code) but the main menu
      never visibly re-themes afterward. RimThemes patches Unity's own GUI
      pipeline extensively (`WindowStackOnGUI_Patch`, `Widgets_ButtonImage_
      Patch`, and ~15 more Harmony patches on core GUI internals) — plausible
      that its own patches intercept the bridge's synthetic click in a way
      a normal button doesn't hit. **Needs a human click** (5 seconds at the
      keyboard: main menu → the bottom-left RimThemes icon row → Utinni
      Shell → its select icon) to actually complete the visual gate, or a
      bridge-side fix if this class of RimWorld mod (heavy GUI-pipeline
      patchers) turns out to be a recurring click-injection blind spot worth
      naming as its own item.
- [ ] §5 verify: `validate_patch.py --live` after a dump (only `--defs`
      static-checked this pass), VBE picker shows the menu background,
      loader shows on the next cold load — all still pending the theme
      actually being selected.

Left `doing` — the offline half is done, the gate is one human click and a
four-screenshot pass away from complete.
