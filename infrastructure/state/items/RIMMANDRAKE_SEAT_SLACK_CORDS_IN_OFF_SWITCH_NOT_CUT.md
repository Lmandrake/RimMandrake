# RIMMANDRAKE_SEAT_SLACK_CORDS_IN_OFF_SWITCH_NOT_CUT

Gimme Some Slack **0.1.1** (a Problem in what 0.1.0 promises; his card of 2026-11-20 put it in 0.1.1). From his walk of
2026-11-20: `design/RimMandrake/validation_holding/gss_walk_20261120.md` row #1, picture `gss_walk_20261120/8.png`.

## spec

An off power switch draws both its cords as cut: frayed ends short of the switch, the powered side sparking. He said the
cords must read connected without power. Cause [measured code path]: `AddPower` takes transmitter buildings only from
the power nets' `transmitters` (`src/RimMandrake/GimmeSomeSlack/Source/CordWorldAdapter.cs:162-177`); vanilla keeps an
off switch in no net (`TransmitsPowerNow` false), so the switch gets no node and the conduit cells beside it become run
ends, drawn live or dead. No ruling makes an open switch a gap. The offline oracle copies the side effect
(`northstar_matrix/oracle.py:52`): change it in the same run. Wanted: the switch is a node whatever its state; both cords
go into its stubs (the stub rule of 2026-11-16 holds); the cord on the unpowered side draws as unpowered, never cut, and
no end sparks at the switch. Also check a switch at a map edge of two nets (the off switch splits one net in two).

## verify

Live, on any tier with Gimme Some Slack: conduit, switch, conduit, with power on one side. Flick the switch off and wait
for the re-lay. Probe `ends:<x>,<z>,1.5` at the switch's cell, then `endkind:` on each end found.

## criteria

Acceptance test: with the switch off, no strand end within 1.5 cells of the switch is a live or dead cut end; both cords
end on the switch's stubs; the same as with it on, except the powered state. Also `northstar_matrix/oracle.py` keeps an
off switch as a node. Red today: his picture 8 [measured in game by him]; the probe read is UNRUN (offline run, no game).

## refs

file: src/RimMandrake/GimmeSomeSlack/Source/CordWorldAdapter.cs
file: src/RimMandrake/GimmeSomeSlack/northstar_matrix/oracle.py
def: ThingDef/PowerSwitch
tier: gimmesomeslack
