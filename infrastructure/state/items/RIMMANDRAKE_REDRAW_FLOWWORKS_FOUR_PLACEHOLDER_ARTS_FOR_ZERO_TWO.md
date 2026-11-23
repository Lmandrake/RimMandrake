## spec

Design Version: FlowWorks 0.2.0 (next, Divergent or Polish; moves no 0.1.0 bar). Filed by the FlowWorks ticket sweep of 2026-11-22
(RIMMANDRAKE_SWEEP_FLOWWORKS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE), which merged these older tickets into this one, one
cause or one file group. Each old ticket's prose is in `infrastructure/state/items/closed/<ID>.md` and its history in
`rimflow show <ID>`; read the one you work on to its end before you build.

FlowWorks 0.2.0: four placeholder or borrowed arts (gravel pile, geyser plume bubble, Modern reel tail colour, style icons in every look menu).

## merged tickets

- `GRAVEL_REDRAW_ITS_OWN_PILE` (proposed): RM_Gravel (FlowWorks Defs/Pits/ThingDefs/RM_Gravel.xml) uses placeholder texture Things/Filth/RubbleRock; needs its own broken-rock pile sprite (stack graphic)
  - sweep reading: RM_Gravel.xml:12 still texPath Things/Filth/RubbleRock (placeholder); cosmetic, no owner report: Polish
  - files: `src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_Gravel.xml`
- `RIMMANDRAKE_DRAW_GEYSER_PLUME_BUBBLE_ART_PLACEHOLDER_IN_USE` (proposed): Real art for the sunk-geyser bubble plume; today it reuses RM_Fleck_LiquidBubble (Biotech vat bubble) as a placeholder; install only via art.py install, judged against art_judge_brief
  - sweep reading: No commit names it. At HEAD RM_LiquidSurface.cs still emits RM_Fleck_LiquidBubble (the Biotech vat bubble) for the sunk-geyser plume. It is art polish on the geyser tub, with no failure and no red test; the 2026-11-22 walk geyser capture (geyser_no_white_ring.png) raised no plume finding
  - files: `src/RimMandrake/FlowWorks/Source/RM_LiquidSurface.cs`, `src/RimMandrake/FlowWorks/Defs/LiquidTypes/FleckDefs/RM_LiquidBubble.xml`
- `REEL_TAIL_VERIFY_RED_DRUM_BEIGE_TAIL` (proposed): Modern hose reel: drum hose is a red firehose (155016141574) but the C#-drawn paid-out hose may still be beige; a judge saw red-drum/beige-tail on s5_reels_13-16_v.png (2026-10-23, predates the firehose deploy) - check the current Modern hose atlas against the drum and match or rule it fine
  - sweep reading: colour-match check only: Modern drum redrawn red firehose 1550161415 (2026-10-24); the judge's red-drum/beige-tail sighting predates it and the Modern hose styles were recoloured again 99006fd7b4 (2026-11-02); no fresh sighting, a Polish-grade art check
  - files: `src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Styles/Modern`
- `RIMMANDRAKE_WIRE_STYLE_ICONS_INTO_EVERY_LOOK_MENU` (proposed): Next version (Divergent), Gimme Some Slack and FlowWorks: every four-looks menu shows one proper icon per look, from one shared piece (_Shared/StyleIcons); art ordered on RIMMANDRAKE_DESIGN_HOME_FOR_VANILLA_ELECTRICAL_ART
  - sweep reading: filed as 'Next version (Divergent), Gimme Some Slack and FlowWorks: every four-looks menu shows one proper icon per look'; no shared _Shared/StyleIcons piece exists yet
  - its check: offline selftest reads every look menu as asking the shared piece; live capture shows four distinct look icons in each menu
  - files: `src/RimMandrake/GimmeSomeSlack/Source/Aerial/ConduitStylePicker.cs`, `src/RimMandrake/FlowWorks/Source/Machinery/PipeLook.cs`

## his words (as recorded on the merged tickets)

- none recorded on these tickets

## verify

Acceptance test: none as one command, art: judged by the art judge against design/RimMandrake/art_judge_brief.md.

## criteria

- Each merged ticket above is fixed with its check passing (red first where it is a fix), or dropped with its evidence.
- No locked 0.1.0 bar is loosened or edited by this work.

## refs

item: GRAVEL_REDRAW_ITS_OWN_PILE
item: RIMMANDRAKE_DRAW_GEYSER_PLUME_BUBBLE_ART_PLACEHOLDER_IN_USE
item: REEL_TAIL_VERIFY_RED_DRUM_BEIGE_TAIL
item: RIMMANDRAKE_WIRE_STYLE_ICONS_INTO_EVERY_LOOK_MENU
