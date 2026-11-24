# RIMMANDRAKE_LOAD_SLACK_POLE_ICONS_ON_MAIN_THREAD

Gimme Some Slack **0.1.1** (his card of 2026-11-20). From his walk of 2026-11-20: `design/RimMandrake/validation_holding/gss_walk_20261120.md` row #9, picture
`gss_walk_20261120/11.png`.

## spec

A pole's "Link wire", "Unlink wire" and "Unlink all" buttons draw the red-X missing-texture square. The paths are vanilla's
and exist (`UI/Commands/TryReconnect`, `UI/Designators/Cancel`; RimSage `CompPower.cs:182`, `Designator_Cancel.cs:18`).
Cause [measured]: `IconLink` and `IconUnlink` are `static readonly` fields of `CompAerialAnchor`
(`src/RimMandrake/GimmeSomeSlack/Source/Aerial/CompAerialAnchor.cs:115-116`), initialised on the loading thread during
the mod's construction. Player.log of the walk, lines 518-519: `Tried to get a resource "UI/Commands/TryReconnect" from a
different thread. All resources must be loaded in the main thread.` and the same for `UI/Designators/Cancel`, just before
`[RimMandrake.GimmeSomeSlack] Harmony: patched 30`. ContentFinder answers null off the main thread, so the fields stay
null. Fix: fetch on first use on the main thread (a lazy getter), or a holder class nothing touches before startup. Sweep
the mod for other static texture or material fields in classes that the mod constructor or Harmony patching reaches; the
same log line names any of them. New icon art for these buttons is ordered on
RIMMANDRAKE_DESIGN_HOME_FOR_VANILLA_ELECTRICAL_ART; this item makes any icon load.

## verify

Cold load (any tier with Gimme Some Slack). Read Player.log for the literal line. Select a pole with a link and read its
gizmos' icons (a bridge read of `Command.icon` names, or a capture of the command bar).

## criteria

Acceptance test: Player.log after a cold load holds no line `Tried to get a resource "UI/Commands/TryReconnect" from a
different thread` and no such line for `UI/Designators/Cancel` or any Gimme Some Slack path; the three buttons' icons are
not null. Red today [measured: the walk's Player.log, lines 518-519]. The green side is UNRUN.

## refs

file: src/RimMandrake/GimmeSomeSlack/Source/Aerial/CompAerialAnchor.cs
def: ThingDef/RM_AerialMast
tier: gimmesomeslack
