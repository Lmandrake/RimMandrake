<!-- status: draft -->
# UI appearance — the visual shell of the Utinni campaign

_Draft spec, 2026-09-05, written AFK on the owner's brief: "write that spec for mods
that change background and appearance." Scope is the game's **shell** — main-menu
background, loading screen, UI chrome (buttons, windows, tabs, gizmos), fonts, title
art. World content, sprites, terrain and pawn art are other specs. Every mechanism
claim below was read from the 1.6 C# source, the installed mods' own files, or the
live `ModsConfig.xml` (600 mods at time of writing). Nothing here is deployed, built
or ruled._

---

## 0. What is already true (measured)

| fact | where it was read |
|---|---|
| **Vanilla Backgrounds Expanded** (`vanillaexpanded.backgrounds`, WS 2775017012) is **ACTIVE** | live ModsConfig |
| It adds `VBE.BackgroundImageDef` defs (`path`, `iconPath`, `animated`) and a mod-options picker with cycle/timer; its own description says the images cover **main menu and loading screen** | `1.6/Defs/Backgrounds.xml`, `1.5/Source/VBE/*.cs` |
| Its images are **2560×1440** PNGs under `Textures/`; `animated` backgrounds are `.webm` under `Videos/` | its Textures folder, `BackgroundImageDef.cs` |
| Vanilla picks the menu background from **`ExpansionDef.backgroundPath`** (Core = `UI/HeroArt/BGPlanet`, 2048×1280) via Options; the loading screen draws the **same** `UIMenuBackgroundManager.background` | `ExpansionDefs.xml`, `UI_BackgroundMain.cs`, `LongEventHandler.cs:227-236` |
| Every UI texture is fetched by `ContentFinder<Texture2D>.Get(path)`, which walks the mod list **last-to-first** and falls back to Core's bundled resources — so a loose PNG at the same path in any later mod **replaces it with no C#** | `ContentFinder.cs` |
| Window/section **colours are C# constants** in `Widgets` (fill `(21,25,29)`, border `(97,108,122)`, section `(42,43,44)`, tutor window `(133,85,44)`/`(176,139,61)`), not textures | `Widgets.cs` static ctor |
| **Fonts** are Unity `Font` assets loaded by `Resources.Load("Fonts/Arial_small")` etc. — not a texture, not a def | `Text.cs:157-159` |
| **RimThemes** (`aRandomKiwi.RimThemes`, WS 1668983184, lists 1.6) is **installed but NOT active**; so are *Basic RimThemes Recolours* and *Graphics Settings+*. No font mod is installed (`font.rimesis` is the Rimesis mod by author "Font") | workshop folder census vs ModsConfig |
| A RimThemes theme is a folder: `meta.xml` (fonts by OS name, ~40 colour keys, menu alignment, window anim), `Textures/<Class>.<Field>.png` overrides, `Loader/` (loading bg jpg/webm + bar), `Songs/`, `Sounds/` | `Themes/Cyberpunk/` |
| Already-active mods that **own** parts of the in-game chrome: **RimHUD** (inspector pane), **Dubs Mint Menus** (architect/bill menus), **Trade UI Revised**, **Camera+**, **Searchable/Float Sub-Menus** | live ModsConfig |
| `required_mods.md:1083` already ruled on fonts once: *"if any global font hurts readability, skip the font … the Jawa-ness is 90% in the words"* | required_mods.md |

---

## 1. Visual identity

Ash'karr is a frozen desert under a Star Wars sky, and the clan that lives on it owns
nothing it did not pull out of something else. The shell should read the same way the
Kolyska does — *"old, rusty brown, and terrible"* (owner, `gravship_wear_pass.md`).
**Palette:** oxidised iron and dried-blood rust for structure; sun-bleached sand and
bone for grounds; a single hot **brass/amber** accent for the active state (the glow
in a Jawa's hood, the eyes on `god1_ishko.png`); deep indigo-black for the sky and for
window fills, so the desert colours sit on it like the god icons sit on their dark
fields. Vanilla's own tutor-window pair `(133,85,44)/(176,139,61)` is already a
rust/brass pair — the identity is a shift of the whole UI toward that corner, not a
new invention. **Motifs:** riveted plate, scored and patched edges, hooded silhouettes,
the nine god glyphs as ornament (never as buttons), the temple-ship as the one
recurring hero image. **Tone:** worn, warm, hand-maintained. Nothing chrome, nothing
clean, nothing that glows blue. The existing art sets the register:
`design/Jawa/art/pantheon_slide.png` (1672×941), `design/Jawa/art/gods/*.png`
(1254×1254, nine), `design/Jawa/art/faction_icons/*.png` (128×128 masks, DESIGN done).

---

## 2. Main-menu background

**Mechanism — use the framework already active.** One `VBE.BackgroundImageDef` per
image in a mandrake mod, PNG under that mod's `Textures/`. VBE picks it up
automatically, the owner selects it (or a cycle of ours) in VBE's mod options, and the
**loading screen inherits it for free** (§5). No Harmony, no C#, no risk beyond a
texture that fails to load (which VBE logs).

```xml
<VBE.BackgroundImageDef>
  <defName>RUT_BG_TempleShip</defName>
  <label>The Salvation over Ash'karr</label>
  <description>The temple-ship above the split world.</description>
  <path>RimUtinni/MenuShell/BG_TempleShip</path>   <!-- Textures/RimUtinni/MenuShell/BG_TempleShip.png -->
  <iconPath>RimUtinni/MenuShell/Icon_Utinni</iconPath>
</VBE.BackgroundImageDef>
```

**Fallback if VBE is ever dropped:** the same PNG shipped at
`Textures/UI/HeroArt/BGPlanet.png` overrides Core's planet by load order alone (§0,
ContentFinder). Keep both paths in the mod; the second costs one file.

**Candidates — author at 2560×1440 to match VBE's set; VBE and vanilla both letterbox
any aspect, so nothing breaks at other ratios.**

| # | image | source | new art? |
|---|---|---|---|
| A | **The temple-ship over the split world** — the Kolyska hanging above Ash'karr's day/night terminator, desert below, stars above | none yet | **yes** — hero render, the one piece worth commissioning |
| B | **The pantheon slide** | `pantheon_slide.png` 1672×941 | **no, with a caveat**: needs a 1.53× upscale (or a letterboxed 2560×1440 with a dark field) — ships day one as the *placeholder* |
| C | **Desert vista** — dune sea, a wreck half-buried, two hooded figures with a cart | none | yes, secondary; good as the second image in a cycle |
| D | **God-icon field** — one god icon large on indigo, rotating through the nine | `gods/*.png` | no — composite only; 9 defs, one per god, put in the cycle |

**Recommendation:** ship B and D in v1 (zero new art), commission A, cycle A/B/C/D.

---

## 3. UI chrome — buttons, windows, tabs, gizmos

Three mechanisms, three risk tiers. Every surface below names which one it needs.

**Tier 1 — texture override, no C# (SAFE).** A PNG at the vanilla path in a later-loaded
mod. Atlases are 9-slice (`Widgets.AtlasUV_*` quarters), so keep the source dimensions
and corner layout and only repaint.

| surface | vanilla path | proposal |
|---|---|---|
| every text button | `UI/Widgets/ButtonBG`, `ButtonBGMouseover`, `ButtonBGClick` | riveted rust plate; mouseover = brass edge; click = darker |
| subtle buttons (lists, main menu options) | `UI/Widgets/ButtonSubtleAtlas` | sand-on-indigo wash |
| inspector/window tabs | `UI/Widgets/TabAtlas` | scored plate tab |
| gizmo (command) backgrounds | `UI/Widgets/DesButBG`, `UI/Widgets/AbilityButBG` | dark iron with a brass rim on `AbilityButBG` |
| checkboxes, radios | `UI/Widgets/CheckOn`, `CheckOff`, `CheckPartial`, `RadioButOn`, `RadioButOff` | rivet-head on/off |
| slider | `UI/Buttons/SliderRail`, `SliderHandle` | rail = pipe, handle = bolt |
| window drop shadow | `UI/Widgets/DropShadow` | leave, or warm it slightly |
| main-menu title | `UI/HeroArt/GameTitle` (1032×146, drawn at ½) | see §3a |

⚠️ These are **universal** — every mod's dialog uses `Widgets.ButtonText`. A repaint
that reads well on the main menu must also read at 24 px in a 600-mod bills tab. Test
on the minimal list (22 s load), then on the full list once.

**Tier 2 — colour constants (CHEAP C#, or RimThemes).** `Widgets.WindowBGFillColor`,
`WindowBGBorderColor`, `MenuSectionBGFillColor/BorderColor`,
`OptionSelected/UnselectedBGFillColor`, `InspectPaneUtility.InspectTabButtonFillTex`
(a solid-colour texture) are static fields set in static constructors. Two routes:
(a) a ~40-line `[StaticConstructorOnStartup]` class in our own mod that reflection-sets
them once at startup — this is exactly what RimThemes' `meta.xml` keys
(`Widgets.WindowBGFillColor` etc.) do; (b) activate RimThemes and write a theme.
Route (a) is one small DLL we already know how to build and touches no draw code;
proposal: window fill indigo-black `(18,16,22)`, border rust `(122,72,48)`, section
fill `(38,32,30)`, selected option brass `(0.42,0.32,0.16)`. Risk: low — a field set,
not a patch — but it is C#, so it lives in the DLL deploy window.

**Tier 3 — layout/behaviour (FRAGILE; RimThemes or Harmony).** Menu alignment, window
open animation, "buttonNoBg", per-element enable, custom cursor, UI sounds. Only
RimThemes offers these without writing our own draw patches. **Not v1.** RimThemes is
a Harmony UI engine over a 600-mod stack that already has RimHUD, Dubs Mint Menus and
Trade UI Revised rewriting the same panes; it is installed, so a test load is cheap,
but it is a load-round item, not a spec decision.

**Surfaces owned by other active mods** — do not retexture around them, configure them:
RimHUD (inspector layout/colours: its own settings, unverified field names), Dubs Mint
Menus (architect menu), Trade UI Revised. Their look should be *checked* against the
palette, not patched.

### 3a. The title

`UI/HeroArt/GameTitle` is a plain texture override (Tier 1) — a "RimWorld" wordmark in
rusted plate, or a campaign wordmark, costs one PNG. **Whether to replace Ludeon's
wordmark at all is a taste ruling for the owner** (card it); the mechanism is free
either way. `UI/HeroArt/LudeonLogoSmall` stays.

---

## 4. Fonts and text

**There is no safe font route today.** Vanilla fonts are Unity `Font` resources
(`Text.cs`), not textures; nothing in XML touches them. RimThemes replaces them by **OS
font name** (`<customFontSmallDefault>Nasalization</...>`, no `.ttf` shipped in the
theme) — so the player's machine must have the font installed, or it silently falls
back. For a campaign shipped as a savegame to other machines that is a broken promise
unless we also ship and register the TTF, which is our own C# (`Font.CreateDynamicFontFromOSFont`
after copying, or an embedded Unity font asset) — fragile and untested here.
`required_mods.md:1083` already anticipated this: **skip the global font; the voice is
in the words.** What IS cheap and in-palette: text **colours** via the Tier-2 field set
(`Widgets.NormalOptionColor` is a cold `(0.8,0.85,1)` blue-white — warm it to sand),
and the `TipSetDef` copy in §5. **v2 at best**, and only if a load-round test of
RimThemes' font path passes on the full list.

---

## 5. Loading and transition screens

`LongEventHandler` draws (1) the **same menu background** (§2 — free), (2) a small
status window (`Widgets.DrawWindowBackground` → Tier-2 colours, free), (3)
**`GameplayTipWindow`**, which pulls every `TipSetDef` in random order, and (4) the
mod-summary window. **The tips are the cheap win nobody has taken:** a `TipSetDef` of
Jawa-voiced tips is pure XML, zero risk, and it is the one text surface the player
reads for 25 minutes on a cold load. Write ~30 in the clan's register (lore, doctrine,
one-line jokes; the canon anchor is `JawaVoice`). RimThemes' `Loader/` (custom bar,
loader jpg/webm) is Tier 3 — not v1. In-game scene transitions (menu→map) use the same
long-event path; there is no separate transition surface to skin.

---

## 6. Feasibility and priority

| change | mechanism | new art | effort | risk | when |
|---|---|---|---|---|---|
| Menu/loading background: pantheon slide + nine god fields | `VBE.BackgroundImageDef` + PNG | none (upscale/compose) | S | **low** | **v1 — safe win** |
| Menu/loading background: temple-ship hero render | same | **yes** (2560×1440) | M (art) | low | v1 art, ships when done |
| Desert-vista second image | same | yes | M (art) | low | v1.5 |
| Animated `.webm` background (ship drifting) | VBE `animated` + `Videos/` | yes, video | L | low-med (video memory on a 600-mod load) | v2 |
| Jawa loading tips | `TipSetDef` XML | none | S | **none** | **v1 — safe win** |
| Button / tab / gizmo / checkbox / slider repaint | Tier-1 texture overrides (9-slice kept) | yes, ~14 small PNGs | M | low-med (universal, readability at 24 px) | v1 after a minimal-list look |
| Title wordmark | Tier-1 override of `UI/HeroArt/GameTitle` | yes | S | low (taste, not tech) | v1 **pending owner card** |
| Window fill/border/section/selected colours, option text colour | Tier-2 reflection set, own DLL | none | S (C#) | low | v1 |
| Inspector tab fill colour | Tier-2 (solid texture field) | none | S | low; RimHUD may own the pane anyway | v1 with the above |
| RimHUD / Dubs Mint palette conformance | their mod settings | none | S | none | v1 config pass |
| Fonts | RimThemes OS-font, or own C# TTF loader | font licence | M–L | **high** (OS dependency, readability, 600-mod text) | **v2 / likely never** (per required_mods §1083) |
| Menu alignment, window anims, cursor, UI sounds | RimThemes theme folder (Tier 3) | some | M | **high** (Harmony UI engine vs RimHUD/Dubs) | v2, gated on a load-round test |
| Expansion icons, Ludeon logo | — | — | — | — | leave |

**Safe wins (do first, no C#):** backgrounds via VBE; loading tips; Tier-1 repaint.
**Cheap C#:** the colour field set. **Fragile:** fonts; RimThemes as an engine.
**No viable mechanism in reach:** none — every listed surface has a route; the two
weak routes (fonts, Tier 3) are weak because of dependency risk, not absence.

---

## 7. Proposed mods (tier grammar, `design/NAMING_SCHEME_PLAN.md`)

Split by the engine/content rule — one mod may not straddle:

| packageId | folder | tier test | contents |
|---|---|---|---|
| **`mandrake.rut.menushell`** — *RimUtinni: Menu Shell* | `src/RimUtinni/MenuShell/` | names Ash'karr, the Nine, the Salvation | `RUT_BG_*` background defs + PNGs, `RUT_TipSet_Jawa`, title wordmark if ruled, `Textures/UI/HeroArt/BGPlanet.png` fallback. XML + textures only. |
| **`mandrake.rm.rustchrome`** — *RimMandrake: Rust Chrome* | `src/RimMandrake/RustChrome/` | a medieval-tribe player would install a rusted-metal UI skin alone and understand it | Tier-1 atlas repaints at vanilla paths + the Tier-2 colour-set DLL (`RimMandrake.RustChrome`). No campaign names anywhere in it. |

Load order: both late (after VBE and after every retexture, so ContentFinder's
last-wins walk finds ours). `deploy_custom_mods.py` handles texture-only mods already
(`AshkarrLandmarkArt` precedent). VBE stays a soft dependency: the defs are
`MayRequire="vanillaexpanded.backgrounds"`-safe only if VBE's def type is absent when
it is off — since an unknown def type discards the def with a red error, write the
background defs in a `LoadFolders`/patch guarded by `PatchOperationFindMod`, and let the
`BGPlanet.png` fallback carry the no-VBE case.

## 8. Open for the owner (cards, not prose)

1. Replace the RimWorld wordmark on the main menu, or keep it? (§3a)
2. Commission the temple-ship hero render now, or ship pantheon + gods and wait? (§2)
3. Is a full-UI rust repaint wanted at all, or only the menu/loading shell? (§3 Tier 1
   is universal; there is no "menu-only" button texture.)
4. Fonts: confirm the standing "skip it" from `required_mods.md:1083`, or fund the
   RimThemes load-round test.
