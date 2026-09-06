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

## PIVOT, 2026-09-05 (owner, mid-review of the vertical slice) — read this first

**The material direction below (oxidised red-rust plate) is superseded.**
Owner, reviewing the shipped vertical slice: *"I think the console should be
more like the ancient ship controls than the rusty scavenger look. The whole
UI should look like you are at the helm of the Utinni. So it can look old
and worn but not brown rusted."* Also asked for the "minimal" look to lean
into the **vector-line schematic graphics common in Star Wars interfaces**,
and for typography with an **Aurebesh-flavored but still legible** character.

- **Material**: aged grey-green/gunmetal machined metal (riveted, painted-
  then-worn, NOT oxidised/rusted brown). Amber remains the primary glow
  accent; cyan is now a live secondary option (see `ref4` and the Zero
  Company reference below).
- **Graphic language**: thin white/silver vector schematic lines connecting
  components (circuit-trace style), amber or cyan tactical-display readouts
  with small glyph-style labels — not painted texture/grain.
- **Typography**: swap the display face for something evoking Aurebesh's
  blocky, angular letterforms while staying Latin-legible (first pass used
  **Orbitron**, paired with **Rajdhani** for sub-labels — see the review
  artifact). Real Aurebesh fonts (glyph-substitution) are explicitly OUT —
  the owner wants legible.
- **Four new reference images** landed alongside the original two (all in
  `ui_references/`, all read before this pivot note was written):
  `ref4_grey_console_bank_cyan_navplot.jpg` (owner-supplied, mid-conversation
  — light grey panel banks + cyan vector nav-plot screens), plus three
  already on disk from the same reference-gathering session:
  `01_07_5100052.webp` (a cockpit fuel/Aurebesh readout — amber vector bars
  in a worn grey housing with visible wiring), `c4e687d92e01e0941121d656f0e46449.jpg`
  (an R2-D2 technical blueprint sheet — Aurebesh glyph shapes, thin blue
  linework), and `How-Star-Wars-Zero-Company-blends-XCOM-with-Mass-Effect-…png`
  (a modern SW game's own UI chrome: dark navy panels, cyan bracket corners,
  angular cut edges, bold clean sans labels — useful for window/tab chrome,
  distinct from the physical-panel references).
- **First concept render** (FOUNDRY, cloud-only Codex generation, all six
  references as `--edit-image` conditioning): `Transient/console_concept_panel.png`
  (not committed — Transient convention; regenerate from the prompt in the
  review artifact if needed). Read as a mood/direction check, not a
  shippable 9-slice asset — the actual button atlases, `Command.BGTex`, and
  loader/menu-bg would need re-authoring in this direction once the owner
  confirms it, likely by extending `_artsrc/gen_textures.py` with a new
  style rather than shipping a raw AI render as a 9-slice (a painted image
  doesn't tile/slice correctly at the corners the way vanilla's button atlas
  needs to).
**LOCKED, same day — owner, on seeing the concept render**: *"I love love
love the tech panel you made. Rusty buttons are out."* Not a direction to
keep exploring; a decision.

**Built and shipped** (commit `506daf52`): a fourth procedural style,
`D_helm`, added to `_artsrc/gen_textures.py` alongside the three rust
options (kept on disk, archived, no longer live contenders) and made the
new `DEFAULT_STYLE`. Grey-green gunmetal plate (`metal_plate()`, cool
scuff/grime blotches, no rust tint), a crisp single-pixel vector-line
bracket inset with amber corner ticks (`vector_inset()`, replacing
`chalk_inset()`'s soft hand-drawn look), amber glow accent kept from the old
palette (it was already light/glow-coded, not material, so it survives the
pivot unchanged). `Command.BGTex` and the theme-picker `Icon` re-authored to
match. **This is a real deterministic PIL 9-slice asset, not the AI concept
render** — it tiles correctly at the button-atlas corners, unlike a raw
painted image would.

**Still NOT re-authored, old rust-direction art still shipping**: the Ishko
temple-gate menu background and the amber-orrery loader screen (both
image-gen pieces from `gen_bg.py`, not procedural — re-doing these needs a
fresh generation pass in the new material language, not a script edit).
Typography (Orbitron/Rajdhani pairing) only exists on the review artifact
page so far, not wired into the actual RimThemes `meta.xml` font keys.
Review artifact: `https://claude.ai/code/artifact/d63666e5-28ca-4019-a037-749c9fbb9b4e`.

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
