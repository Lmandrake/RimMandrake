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
- [ ] **§4 gate, needs the game DOWN then a bridge session**: activate
      RimThemes + this theme, screenshot the main menu / a gizmo row / a
      window / a float menu, confirm no red errors and RimHUD/Dubs Mint
      Menus/Camera+/Trade UI Revised still work. Rides the next restart
      alongside whatever else needs one.
- [ ] §5 verify: `validate_patch.py --live` after a dump (only `--defs`
      static-checked this pass), theme appears in RimThemes' picker, VBE
      picker shows the menu background, loader shows on the next cold load.

Left `doing` — the offline half is done, the gate is real remaining work.
