# RIMMANDRAKE_STYLE_SLACK_BATTERY_LIKE_THE_LAMP

**Next version, Divergent** (new scope; moves no 0.1.0 bar). Gimme Some Slack. From his walk of 2026-11-20: `design/RimMandrake/validation_holding/gss_walk_20261120.md` row #11.
The battery ART in each look is ordered on RIMMANDRAKE_DESIGN_HOME_FOR_VANILLA_ELECTRICAL_ART; this item is the code.

## spec

He asked for battery looks for the styles, "like we did for the lamp already". The lamp path [measured]:
`ConduitStyles.LampDefs = { "StandingLamp" }` (`src/RimMandrake/GimmeSomeSlack/Source/Aerial/ConduitStyles.cs:30`), its
ThingStyleDefs, and "Restyle this lamp" with "Match its cable run" (`Source/Aerial/ConduitStylePicker.cs:300-320`,
`RM_MapComponent_ConduitRuns.RestyleLamp`). No battery def is in any style list [measured]. Wanted: the vanilla Battery
gets the four looks the same way: its own button, and it follows its run unless given a look of its own. The battery's
cord join (`CordWorldAdapter`, transmitter buildings) must meet each look's art; the stub census covers it.

## verify

Offline: `ConduitStyles.KeysFor("Battery").Count == 4` in the mod's selftest (as `StyleStage2Checks.cs:36` does for the lamp).
Live: a battery on a Modern run; restyle the run; read the battery's drawn texture name.

## criteria

Acceptance test: the selftest check above passes (red today: no battery keys [measured: no battery def in
`ConduitStyles.cs`]); live, the battery draws the run's look after a restyle (UNRUN).

## refs

file: src/RimMandrake/GimmeSomeSlack/Source/Aerial/ConduitStyles.cs
def: ThingDef/Battery
tier: gimmesomeslack
