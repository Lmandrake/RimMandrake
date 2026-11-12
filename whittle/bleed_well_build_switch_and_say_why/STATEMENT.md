# BLEED_WELL_BUILD_SWITCH_AND_SAY_WHY — done statement

Owner's card, 2026-10-23: "Bleed well: what should change? → Add a toggle + clear status (Recommended)".
Item title: Bleed well (RM_LiquidTap) and liquid drill: On/Off toggle, a visible status icon with the reason when it
can't run, and a god-mode 'give this map a subsurface yield' debug action.

Built at 8df1c0db13f1 (code b26a96a424). A1 (L0, selftest `DrillWhyNot_each_condition_names_its_reason`) is not owed.
Owed: A2 (L4; Conductor triage 2026-10-29 re-levelled it to an agent-staged zoomed capture judged by a naive Opus,
recorded at L3, the owner seeing it as feedback on his next FlowWorks walk). The ledger text of A2 is cut off at
"the inspe"; the bullets below read it as "the inspect pane says why".

- **Switch:** a placed bleed well (RM_LiquidTap) shows an On/Off switch gizmo when selected.
  Evidence: zoomed capture of the selected bleed well with its gizmo bar, in `evidence/`.
- **Debug yield:** the god-mode debug action "Give this map a subsurface yield..." exists and gives the current map a
  yield of a picked liquid. Evidence: the inspect line before/after (Subsurface: unsurveyed/none → "Subsurface: <liquid>,
  <n> remaining"), captured or read through the bridge.
- **It pours:** with that yield and a dug outlet channel at the cell it faces, the switched-on bleed well puts liquid into
  the outlet. Evidence: outlet fill read through the bridge rising over a timed window, plus a capture of the filled outlet.
- **Switched off it stops:** after the switch is turned off the outlet fill stops rising (and the inspect line reads
  "Not running: switched off..."). Evidence: outlet fill read flat over the same length of window, plus inspect text.
- **Blocked states show a ? and say why:** at least one blocked state that is not off/unpowered/brimming (no dug outlet,
  or no subsurface yield) draws the ? overlay icon over the well and its inspect pane names that reason
  (e.g. "Not running: the outlet cell x,z is not dug. Dig a channel there."). Evidence: zoomed capture showing the ?
  and the inspect text.
- **Judged:** a fresh Opus that did not stage the scene judges the captures against these bullets and agrees.
