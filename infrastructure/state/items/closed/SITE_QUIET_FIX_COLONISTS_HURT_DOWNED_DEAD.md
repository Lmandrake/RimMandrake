## spec
The Steve chain's test sites do not stay quiet: during `safe_advance` / the site hold, colonists were hurt
(ToxicBuildup), downed or killed, the colony was lost, or raiders arrived. The run then ends with no verdict on the mod.
Jobs: a0fa57 (toggle_bottle_loop), 386617 (plot_C_limitless_canal: colony_loss, GameEnded, hostile_arrival),
e8c645 (dead colonists), 0ae6fe (Stillsand: downed). Merged from HARNESS_REPAIR_CAUSE_4D2C5B87, _5495932D, _8A6B00BD,
_FA96BB79, _FCC08D84, _4AFBF8A2.

First diagnose each surprise as one of these. The answer decides what gets built:
- **MOD.** The thing under test hurt the colonist: toxic fluid from a FlowWorks bottle or canal reached a pawn it should
  not reach. That is a FlowWorks defect, or a design question about whether it should reach pawns. File it against
  FlowWorks with the job evidence. Do NOT fix it in the harness.
- **SITE.** The harness put colonists where the plot's own hazards reach them, or left raids and threats on. Fix the
  staging: colonists outside the hazard's reach (or none, where the plot needs no pawn), threats and storyteller
  incidents off for the hold, and the plot's hazard footprint known before pawns are placed.
- **ENVIRONMENT.** The run fell inside a SteveDesktop fault window (`testq/fault_windows.json`). Supersede it onto
  STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO. Nothing is built.

Forbidden fixes, because each hides a real defect: healing or resurrecting pawns, god mode, raising the hurt or downed
tolerance, or dropping the surprise check. A colonist hurt by the mod under test must still end the run as a MOD
finding.

## verify
- Each of the four jobs has a written classification (MOD / SITE / ENVIRONMENT) with the evidence: the hediff source,
  the pawn's position against the plot, and the fault-window check.
- SITE fixes: the same four plots, re-run on Steve through testq outside a fault window, end with a verdict on the mod
  (PASS or FAIL rows), with no `site_hold` or `safe_advance` surprise.
- Negative control: a staged plot whose fluid is made to reach a pawn on purpose still ends the run with a MOD
  finding. The harness change must not swallow it.
- MOD findings are filed as their own FlowWorks items, with the job ids.
