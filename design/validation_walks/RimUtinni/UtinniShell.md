# UtinniShell — validation walk
subject: src/RimUtinni/UtinniShell  (packageId mandrake.rut.shell)
deps: aRandomKiwi.RimThemes (modDependencies + loadAfter), vanillaexpanded.backgrounds (loadAfter, MayRequire-guarded)
list: minimal+aRandomKiwi.RimThemes
status-hint: the campaign's UI shell — one RimThemes theme ("Utinni Shell": rust plate, chalk graffiti, brass accent) plus one VBE main-menu background (Ishko at the temple gate, animated).

## must be true
- RimThemes/Utinni Shell/meta.xml exists at the top level of the mod (the packaging pattern that survives a RimThemes workshop update) and declares the vertical-slice key set: grounds, menu-section panels, selectable options, mouseover/active accent, default text colour.
- One VBE.BackgroundImageDef (RUT_BG_ShellIshkoGate) exists, MayRequire="vanillaexpanded.backgrounds", so it loads cleanly whether or not VBE is active.
- RUT_BG_ShellIshkoGate's `path` and `iconPath` both resolve to `UI/Backgrounds/utinni_menu_1` under Textures/, and with `animated=true` a sibling `Videos/UI/Backgrounds/utinni_menu_1.webm` must exist for VBE to resolve the drawn (not just the picker-thumbnail) background.
- No C#/Harmony of its own — RimThemes and VBE do all the patching; this mod is XML+textures+video only.
- This mod ships no def whose absence would be a red load error if RimThemes or VBE are both absent — MayRequire covers the background def, and the theme folder is inert data RimThemes reads only when selected.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rut.shell" and no XML error naming Defs/VBE_Backgrounds_Utinni.xml
2. [D] def read-back: VBE.BackgroundImageDef RUT_BG_ShellIshkoGate exists; path = "UI/Backgrounds/utinni_menu_1"; iconPath = "UI/Backgrounds/utinni_menu_1"; animated = true
3. [D] file exists: `RimThemes/Utinni Shell/Textures/UI/Backgrounds/utinni_menu_1.png` under this mod's deployed Textures/ root (the static picker/fallback asset path referenced) — resolve relative to Textures/, not RimThemes/
4. [D] file exists: `Videos/UI/Backgrounds/utinni_menu_1.webm` under this mod's deployed Videos/ root (the animated asset `path` must resolve when animated=true)
5. [D] file exists: `RimThemes/Utinni Shell/meta.xml`; contains keys Widgets.WindowBGFillColor, Widgets.MenuSectionBGFillColor, GenUI.MouseoverColor, textColorGray (the full vertical-slice key set the spec requires)
6. [S] (human pass) select "Utinni Shell" in RimThemes options and confirm coexistence with the other UI mods (RimHUD, Dubs Mint Menus, Camera+, Trade UI Revised) and that the animated Ishko background actually plays on the main menu — the mod's own About.xml names this as the next-load gate; no bridge tool exists for theme selection or main-menu rendering (grepped bench_tools_dump.json: no background/theme/vbe hits)
