# MenuShell — validation walk
subject: src/RimUtinni/MenuShell  (packageId mandrake.rut.menushell)
feature: menu-shell-core
deps: vanillaexpanded.backgrounds (loadAfter; all ten BackgroundImageDefs carry MayRequire="vanillaexpanded.backgrounds" so it is a soft dep, not a hard one)
list: minimal   # loads clean with VBE absent (MayRequire skips before type resolution); minimal+vanillaexpanded.backgrounds needed to exercise the ten BackgroundImageDefs themselves
status-hint: the campaign's menu/loading-screen shell — ten VBE.BackgroundImageDef main-menu backgrounds (pantheon slide + one per god icon), a Core-planet-background fallback texture with no VBE dependency, and a 30-line Jawa-voiced TipSetDef read by GameplayTipWindow. Pure XML + textures, no C#, no Harmony.

## must be true
- With vanillaexpanded.backgrounds ABSENT, all ten VBE.BackgroundImageDef nodes are skipped cleanly (MayRequire short-circuits before DirectXmlLoader resolves the "VBE.BackgroundImageDef" type) — no red config error, and Textures/UI/HeroArt/BGPlanet.png is what actually shows behind the main menu (overrides Core's own planet background by load order).
- With vanillaexpanded.backgrounds PRESENT, all ten RUT_BG_* defs resolve and each def's path and iconPath point at the same texture file (RimUtinni/MenuShell/BG_PantheonSlide, BG_God_Ishko, BG_God_Ohm, BG_God_Oomo, BG_God_Mobunloo, BG_God_Rekko, BG_God_Tabaa, BG_God_Zizzik, BG_God_Ozzik — nine gods + the pantheon slide).
- RUT_TipSet_Jawa loads with its full 29-line <tips> list intact and no def has zero tips.
- No .cs, no Assemblies/ folder in this mod — any load-time error naming MenuShell.dll or a C# type would mean the About.xml's "XML/texture only" claim is false.

## the walk
1. [L] Player.log after load (minimal list, VBE absent) contains no "Config error in mandrake.rut.menushell" and no XML error naming BackgroundImageDefs.xml or TipSetDefs.xml
2. [D] def read-back: TipSetDef RUT_TipSet_Jawa exists; tips list has 29 entries, first entry = "Ash'karr turns but never spins - one face burns, one face freezes, and the clan lives on the line between."
3. [L] with vanillaexpanded.backgrounds active in the load, Player.log after load still has no "Config error in mandrake.rut.menushell" and no XML error naming BackgroundImageDefs.xml
4. [D] with vanillaexpanded.backgrounds active: def read-back defType=VBE.BackgroundImageDef defName=RUT_BG_PantheonSlide exists; path = "RimUtinni/MenuShell/BG_PantheonSlide", iconPath = same value
5. [D] with vanillaexpanded.backgrounds active: def read-back defType=VBE.BackgroundImageDef defName=RUT_BG_God_Ozzik exists; path = "RimUtinni/MenuShell/BG_God_Ozzik"
6. [S] (human pass) the main menu actually shows BGPlanet.png (VBE absent) or the VBE picker offers the pantheon/god backgrounds (VBE present), and a loading-screen tip from RUT_TipSet_Jawa appears during a cold load

## north star
state: DRAFT
validated-hash:

Seeded 2026-10-01 by an agent (NORTH_STAR_WALK_AUTHORING_1) from this walk's
`## must be true` and the mod's shipped sprites, defs and settings, on the owner's
ruling that day: *"You are mostly seeding the field right now with reasonable
initial guesses for refinement later through debugging needs or live feedback."*
Every line is an agent guess for him to accept, edit or cut; `(guess)` marks the
least certain. `### the experience` is his to dictate.

### the experience  (OWNER'S WORDS)
(not yet dictated)

### must show

**The main menu**
- [ ] `menushell_background_is_campaign_art` — the main menu shows a campaign
      background (the pantheon slide or one of the god icons), not RimWorld's stock
      art.
- [ ] `menushell_fallback_planet` — without Vanilla Backgrounds Expanded the menu
      still shows the campaign's own planet background (`UI/HeroArt/BGPlanet`).
- [ ] `menushell_background_fills_screen` — the art fills the screen at common
      resolutions without stretching or letterboxing. (guess)

**Loading tips**
- [ ] `menushell_jawa_tips_show` — the loading screen shows a Jawa-voiced tip from
      `RUT_TipSet_Jawa`. (guess: may belong to the read axis instead)

### cannot show

- [ ] `menushell_never_stock_menu` — the vanilla RimWorld main-menu art while this
      mod is active.
