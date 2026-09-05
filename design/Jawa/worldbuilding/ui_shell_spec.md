# RimUtinni Shell — UI theme + loading-art spec

_Design spec, 2026-09-05, BENCH with the owner. Successor scope to
`ui_appearance_spec.md` §3 (which surveyed the mechanisms); this is the
buildable plan. Owner ruled the path by card: **RimThemes full look ·
vertical slice first · still art now, animate the best later.** Nothing here
is deployed until the slice is built and the RimThemes-coexistence gate passes._

References the owner supplied live in
`design/Jawa/worldbuilding/ui_references/` (Galaxy's Edge control panels +
tactical display). Read them before authoring any texture.

---

## 0. What was measured (not assumed)

- **RimThemes** (`aRandomKiwi.RimThemes`, WS 1668983184) is a Harmony UI mod,
  installed **inactive**. A theme it consumes is a folder of
  `Textures/<Class>.<Field>.png` overrides + a `meta.xml` of ~40 colour keys,
  fonts, `Loader/`, `Songs/`, `Sounds/`. It reaches the **text-button atlases**
  (`Widgets.ButtonBGAtlas`, `...Click`, `...Mouseover`, `ButtonSubtleAtlas`),
  tabs, checkboxes, radios, command/gizmo bg (`Command.BGTex`), the title
  (`MainMenuDrawer.TexTitle`) and the menu background — a **superset** of the
  loose-PNG path, which can never touch the colour constants.
- **Theme packaging is our own mod.** Measured on *Basic RimThemes Recolours*
  (`MrSamuelStreamer.RimThemesRecolours`): a mod contributes a theme by shipping
  a top-level **`RimThemes/<ThemeName>/`** folder — no DLL. So our theme lives in
  `mandrake.rut.shell` and a RimThemes workshop update can never overwrite it.
- **VBE Backgrounds** (`vanillaexpanded.backgrounds`, ACTIVE) drives the
  main-menu background via `VBE.BackgroundImageDef` (jpg/webm, picker + timer).

## 1. Visual language (from the refs)

- **Grounds / window fills:** deep indigo-black (the Ash'karr night sky), the
  same dark field the nine god icons sit on.
- **Plate / panels:** oxidised-red rusted metal; recessed grey sub-panels.
- **Line work:** chalk-white outline "graffiti" (ref #1) as section/command
  borders.
- **Active state / accent:** one hot **brass/amber** — the glow in a Jawa's
  hood, the eyes on `god1_ishko.png`. Used for mouseover edges, selected
  options, indicator LEDs.
- **Screens (loader):** amber Aurebesh-on-black tactical read-outs (ref #3).

**Palette (author against these; tune on the first look):**

| role | RGB | note |
|---|---|---|
| ground / window fill | `(18, 21, 26)` | indigo-black |
| menu section fill | `(38, 28, 24)` | dark rust |
| border (default) | `(150, 160, 175)` | chalk grey-white |
| border / accent (active) | `(198, 138, 58)` | brass |
| option selected fill | `(74, 44, 30)` | warm rust |
| indicator / warning | `(196, 72, 54)` | LED red |
| text (default) | `(222, 214, 200)` | bone |

## 2. Vertical slice — the build (offline)

Mod `mandrake.rut.shell`, folder `src/RimStarWars/.../UtinniShell/` (tier: RUT —
this is campaign shell). Tree:

```
UtinniShell/
  About/About.xml            packageId mandrake.rut.shell; modDependencies RimThemes; loadAfter RimThemes
  RimThemes/Utinni Shell/
    meta.xml                 the ~10 highest-impact colour keys (§1 palette) + flags
    Textures/
      Widgets.ButtonBGAtlas.png          rust plate, 9-slice
      Widgets.ButtonBGAtlasMouseover.png brass edge
      Widgets.ButtonBGAtlasClick.png     pressed dark
      Command.BGTex.png                  chalk-outline grey sub-panel (one gizmo bg)
    Loader/
      BGLoader.jpg                       ONE loading screen (tactical/amber, ref #3)
      LoaderBar.png  TextBar.png         progress bar in brass
    Misc/Icon.png                        theme picker icon
  Defs/VBE_Backgrounds_Utinni.xml        ONE BackgroundImageDef (a god or the planet)
  Textures/UI/Backgrounds/utinni_menu_1.png   the menu-background art
```

**meta.xml keys for the slice** (the ones that move the needle):
`Widgets.WindowBGFillColor`, `Widgets.WindowBGBorderColor`,
`Widgets.MenuSectionBGFillColor`, `Widgets.MenuSectionBGBorderColor`,
`Widgets.OptionSelectedBGFillColor`, `Widgets.OptionUnselectedBGFillColor`,
`GenUI.MouseoverColor`, `FloatMenuOption.ColorBGActive`,
`FloatMenuOption.ColorBGActiveMouseover`, `textColorGray`. Font: **omit** for
the slice (owner's standing rule — skip a font that hurts readability; Aurebesh
is unreadable as UI). Author the atlases as 9-slice at the source dimensions VBE
/ vanilla use (`Widgets.AtlasUV_*` quarters); do not rescale the atlas grid.

## 3. Art pipeline (first pieces)

Offline generation via the image skills (`generating-images` /
`generating-rimworld-sprites` / MandrakeVisualize). Slice needs **two** pieces:
one menu background (a god — Ishko — or the planet Ash'karr) and one loader
screen (amber tactical). Still PNGs. Keep the generator + prompts in the repo so
the set scales; art itself is derived (gitignore, provenance = the prompt).
Full set later: 9 gods + planet + 3–5 places, then animate standouts.

## 4. The gate — RimThemes coexistence (before real art commits)

RimThemes Harmony-patches the same UI other active mods touch: **RimHUD**, **Dubs
Mint Menus**, **Trade UI Revised**, **Camera+**, Searchable/Float Sub-Menus.
Before investing the full art set: activate RimThemes + the slice on a load,
select the Utinni Shell theme, and screenshot the main menu, a gizmo row, a
window, and a float menu. **Pass** = the four surfaces render themed with no red
errors and the other UI mods still work. **Fail** = capture the conflict, decide
loose-PNG fallback for the affected surface. This rides the next restart (the
same down-window as the Ninefold/VF/level-up deploys).

## 5. Verify

- `validate_patch.py` clean on the VBE def (`--defs`, and `--live` after a dump).
- Theme appears in RimThemes' picker (folder discovered).
- Buttons/colours change on selection; the four gate surfaces screenshot themed.
- Menu background shows in VBE's picker; loader shows on the next cold load.

## 6. Explicitly out of the slice (YAGNI)

Custom font · UI sounds/music · the full 9-god + places art set · animated webm ·
tabs/checkboxes/work-boxes retexture · title logo. All land after the slice
proves the chain and the gate passes.
