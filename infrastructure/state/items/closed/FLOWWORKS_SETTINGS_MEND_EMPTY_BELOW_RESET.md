# FLOWWORKS_SETTINGS_MEND_EMPTY_BELOW_RESET

Class: MOD (presumed, untraced). Found live 2026-10-19 by BENCH's FlowWorks session (flowworks tier, 11 mods,
FlowWorks DLL from HEAD ccf36a9af7, deployed md5 9035a401).

The FlowWorks Mod Settings dialog (surface `RimMandrakeFlowWorksMod`) draws its title, the search box and
"Reset all to defaults" and then NOTHING: the body is empty, opened twice, 3 s apart, game paused.
`rimworld/get_ui_layout` lists no label after "Search settings". Picture:
`Transient/live_session/20261018T230250/settings_dialog_empty.png` (pinned).
live_session B2 reads it as five FAIL rows (FALL_DAMAGE A1, PIT_ROOM A1, PIT_ALERT A1, BEACH_RING A1, FALL_GUARDRAILS A2).

Leads (unproven): `DoWindowContents` sizes the scroll view from `lastListHeight` measured on an earlier frame
(RimMandrakeFlowWorksMod.cs ~line 891) - a stale small height or a stale `scrollPosition` would clip everything below
the reset button; the 601e7482f3 "settings headers use keys" change touched the section headers. Player.log had
stopped writing (Verse.Log cap) so an exception during the draw may be hidden: Log.Clear first, then reopen.

Bar: the dialog shows the sections; B2's five label rows PASS.
