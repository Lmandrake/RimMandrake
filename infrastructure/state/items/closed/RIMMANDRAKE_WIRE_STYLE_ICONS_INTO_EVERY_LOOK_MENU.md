# RIMMANDRAKE_WIRE_STYLE_ICONS_INTO_EVERY_LOOK_MENU

**Next version, Divergent** (new scope; moves no 0.1.0 bar). Gimme Some Slack and FlowWorks. From his walk of 2026-11-20:
`design/RimMandrake/validation_holding/gss_walk_20261120.md` row #10. The icon ART is ordered on RIMMANDRAKE_DESIGN_HOME_FOR_VANILLA_ELECTRICAL_ART ("icons for the style
choices used by every mod"); this item is the code that shows them, once, for every mod.

## spec

Every menu that offers the four looks (Scrapper, Industrial, Modern, Futuristic) shows one proper icon per look, the same
icon in every mod. Today each menu borrows a piece of the thing [measured]:
- Gimme Some Slack: "Restyle this run" on conduit, switch, pole and bracket (`src/RimMandrake/GimmeSomeSlack/Source/Aerial/ConduitStylePicker.cs:328-350`, a cable strip per look via `Icon`, `:188-198`); "Restyle this lamp" (`:304-320`); the conduit and switch build-button look menus (`Patch_DesignatorBuild_ProcessInput_Conduit`, `:355` on).
- FlowWorks: pipe "Choose style" (`src/RimMandrake/FlowWorks/Source/Machinery/PipeLook.cs:166-185`); tank and pump "Choose style" (`CompTankLook`, `:236-275`); the build-button look menu for pipes and bridge decks (`PipeLook.cs:268-271`, decks registered in `Pits/Suspension/RM_SuspensionPatches.cs:978-990`); hose reel "Choose style" (`Hose/CompHoseReel.cs:843-856`); weir "Choose style" (`Rivers/RM_Weir.cs:820-832`); built bridges once RIMMANDRAKE_ADD_FLOWWORKS_CHOOSE_STYLE_TO_BUILT_BRIDGES lands; the drawbridge picks art per look (`Pits/Drawbridge/RM_DrawbridgeArt.cs:11`).
Home: one shared piece, `src/RimMandrake/_Shared/StyleIcons/` (linked into each mod like `_Shared/SlackGeometry`), that
maps a look name to its icon; every menu above asks it. The gizmo's own icon shows the current look's icon.

## verify

Offline: a selftest that lists every `FloatMenuOption` built in a look menu in the two mods' sources and asserts each gets
its icon from the shared piece. Live: open each menu once and capture it.

## criteria

Acceptance test: the offline selftest reads every look menu listed above as asking the shared piece (red today: none does
[measured: no such piece exists]); the live capture shows four distinct look icons in each menu (UNRUN).

## refs

file: src/RimMandrake/GimmeSomeSlack/Source/Aerial/ConduitStylePicker.cs
file: src/RimMandrake/FlowWorks/Source/Machinery/PipeLook.cs
tier: gimmesomeslack_flowworks
