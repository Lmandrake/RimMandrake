# FlowWorks UX review — player's-eye, from source (2026-10-22, BENCH helper)

Status: DONE (offline; no game). Scope read: every buildable def's label/description (47 with a
designationCategory + the inherited machinery/works/stills), all four Keyed files, every gizmo
`defaultLabel`/`defaultDesc` in Source, the dig/fill designators, alerts, messages, letters,
and the whole Mod Settings page (RimMandrakeFlowWorksMod.cs + its 16 sub-section files).

## Wording fixes made (XML/Languages only, defNames unchanged, no behaviour change) — 14

| file | fix |
|---|---|
| Keyed/FlowWorks_Keys.xml `RMFlow_JumpIntoPitDesc` | "adjacent superdeep pit … no climbing out without a ladder" → "the pit beside them … no way back without a lowered ladder, a ramp or climbing gear" (ramps, portable ladders and gear exist now) |
| `RMFlow_JumpIntoPitConfirm` | same: "until a ladder is placed" → "until there is a way out (a lowered ladder, a ramp or climbing gear)" |
| `RMFlow_PumpModeDesc`, `RMFlow_PumpNoTank`, Machinery `RMFlow_ConverterNoTank` | "touching it or on a hose run to it" → "touching it, or joined to it by pipe or hose" (universal pipes join the net too; the old text sent players hunting for a hose) |
| `RMFlow_PumpCircle` | adds the remedy: "(move one hose end)" |
| `RMFlow_PumpPourNeedsDumpMessage`, Machinery `RMFlow_TankJobsMessage` | removed patch-note "now" wording; names the **Job** button |
| Machinery `RMFlow_NetTooLarge` | "pipe cells, hoses and members" (jargon) → "pipe squares, hoses and connected buildings … Split it into smaller networks." |
| Machinery `RMFlow_AdapterBroken` | "Pipe net not found" (wrong: it fires when the adapter fails closed) → "Shut itself: it could not work with the Vanilla Expanded pipe network (details in the log). Set its mode again to retry." |
| Defs FlowWorks_Doors.xml (sluice, security grate) | "Nobody stuck down in a superdeep pit" → "Nobody trapped down in a pit can open it from below" |
| Defs RM_HoseReel.xml | was "A scrap pump hookup … Lay the hose out … in one go" (it is not a pump, and a colonist carries the end). Now says how to start: build it touching a tank/pump/pipe, Deploy hose, couple or leave free (Free end button), Retract hose |
| Defs RM_LiquidPump.xml | adds "It needs power" and "Join it to a liquid tank (touching it, or by pipe or hose)" |
| Defs RM_LiquidTank.xml (tank + tall tank) | adds the Job button (Store / Fill / Empty / Dump) — the only way to move liquid tank-to-tank, never mentioned on the tank |
| Defs RM_PumpingStation.xml (kludged + repaired) | "every tank on its hose line" → "pipe or hose line" |
| Defs RM_LiquidDrill.xml | "Its readout says what the survey found under this map." (honest pointer; the real fix is #1 below) |
| Defs FlowWorks_JobDefs.xml `RM_OperateLadderJob` | report "moving X on its rails" → "raising or lowering X" |

## Ranked UX problems (behaviour or C# text — not fixed here)

1. **Drill/tap survey is a dead-end until built** (`Building_LiquidDrill.GetInspectString`): the
   subsurface result ("nothing drillable found under this map") is readable only on a BUILT drill.
   A player spends steel, components and 400 W to learn there was nothing to drill. Show the survey
   while placing (PlaceWorker readout / ghost text) or on the map's info. **Filed `DRILL_SURVEY_EXPLAIN_BEFORE_STEEL_IS_SPENT`.**
2. **Settings page grouping**: "Pits, ladders and shooting" holds ~90 controls including liquid
   looks (sheen, wakes, bubbles, see-through), the per-liquid "can fill a cut" list, the water-
   levelling engine (level by surface / exactly level / settles flat), viscosity, sluice doors,
   concealed pits and trench cover. Pipe settings are split three ways ("Liquid machinery",
   "Hoses and pipes", "The liquid tank" — which owns the *pump* on/off; tank Jobs live under Hoses).
   Suggested sections: Digging · Water and levelling · Pits and climbing · Falls, spikes, rails ·
   Pit prisoners · Drowning, poison, slime, exposure · Concealed pits · Combat at pits (cliff
   shooting, trench cover) · How cuts and liquids look · Tanks, pumps, pipes and hoses (one
   section). **Filed `FLOWWORKS_SETTINGS_UNTANGLE_THE_JUNK_DRAWER`.**
3. **Settings that do nothing**: the "Sluice gates" section (on/off + open/shut delays) drives
   `Building_RM_SluiceGate`, which **no def uses**; the player's sluice is `RM_Sluice`, a door
   (`Building_RM_FlowDoor`). Three different things are also called "sluice" (canal sluice door,
   these gate settings, the river *sluice box*). **Filed `SLUICE_GATE_SETTINGS_EXCISE_KNOBS_ON_NOTHING`.**
4. **Developer jargon on the settings page (C# strings)**: "superdeep" (lines ~1012, 1326, 1351,
   1361, 1506, 1563, 1657, 1873 of RimMandrakeFlowWorksMod.cs), "owner decision 2026-10-15",
   "came in with the liquid-types merge", "per that liquid's registry row", "PROVISIONAL",
   "first-guess number" (dig finds, swale, sluice delays), "(owner's pick: 8)", "The fourth
   acquisition route", "the shipped campaign behaviour", "the job-loop bug", "the old rule" /
   "as before" / "how the mod behaved before this", "Shipped:" vs "default" mixed, raw ticks
   ("every 250 ticks", "~700 ticks; a soil cut is 3200"), "Thirst provider". **Filed `FLOWWORKS_SETTINGS_POLISH_SUPERDEEP_LEAKS`.**
5. **Contradictory tooltips about getting out of a pit** (C#): "A ladder is needed to get out"
   says a pit holds you "until a ladder stands in their cell" — ladders hang on a wall square,
   and ramps, portable ladders, climbing gear and jumps are all exits now. "Your own pit takes your
   own people" says "a superdeep cell … to build the ladder". (Folded into item 4.)
6. **Hose reel "Fitting: nozzle / end cap / open" is looks-only** but sits beside "Free end:
   Capped / Intake / Outflow". A player sets *Fitting: end cap* to stop flow and nothing changes.
   Rename to "End look: …" or derive the look from the role. **Filed `HOSE_FITTING_RENAME_CAP_IS_NOT_CAPPED`.**
7. **Dig deeper than colonists may**: "Dig to depth" lists every half-metre to 20 m (40 options)
   with "machines only past 2 m" in parentheses; an order past 2 m in a colony with no mechanoid or
   droid digger just sits, with no inspect line or alert saying why. Hide or grey the machine-only
   depths when no machine can dig, or say so on the designation. **Filed `DEEP_DIG_EXPLAIN_WAITING_ON_NO_DROID`.**
8. **Units drift**: bridges/ramps say "squares", pipes/hoses/sprinklers/settings say "cells";
   "level"/"fill level" leaks ("Fill in canal … by one level", "a fill level every N s",
   "Liquid held per hose cell"); tank capacity in kL beside litres everywhere else. Pick
   squares + metres + litres (Folded into item 4.)
9. Hose messages print raw coordinates ("Hose end dropped at (12, 0, 34)") — the LookTarget is
   enough; drop the vector (C#, minor; folded into item 6).
10. Dig canal / Fill in canal descriptions never say the work type (Mining) — a new player with
    no miner wonders why nothing digs (C# designator text; folded into item 4).
11. Pump "Pouring into the channel" also pours out of Outflow hose ends and only drains Dump
    tanks — label is narrower than the behaviour (a one-time message covers it). Minor.
12. Guardrail refusal names a fixed 1.5 m (the person-climb band) while spikes and concealed pits
    talk about 2 m and a setting — consistent in code, confusing side by side. Minor.

## What already works well (keep)

- Pump/converter/drill/tank inspect lines give a reason for idling (no tank, no room, foreign
  liquid, tank empty, needs Dump, network too large) — the "why isn't it pumping" answer exists.
- Hose refusals explain themselves ("Cannot deploy the hose there: route too long …", full stretch).
- Ladder/ramp/portable-ladder place refusals and inspect lines are clear and use metres.
- Settings: per-section reset, search box, dependent greying, honest Off: lines on nearly every toggle.
- Concealed-pit naming is consistent across defs, keys and settings ("concealed pit (planks)").
- Dig depth: colonists 2 m / machines 20 m is stated the same way in the designator and settings.

## Selftests

FlowWorks selftests + northstar + xml lint: 44/47 PASS. The 3 FAILs are pre-existing and unrelated to
text: `northstar/selftest_drawbridge_proof.py` (DRAWBRIDGE_CASES drift: 3 Looks cases),
`northstar/selftest_extensions.py` (mock lacks row `X8b_cover_occupant_stays_below`, from fd94feb446),
`selftest_review_map.py` (uncovered RM_Spikes textures).

## Items filed
DRILL_SURVEY_EXPLAIN_BEFORE_STEEL_IS_SPENT · FLOWWORKS_SETTINGS_UNTANGLE_THE_JUNK_DRAWER ·
SLUICE_GATE_SETTINGS_EXCISE_KNOBS_ON_NOTHING · FLOWWORKS_SETTINGS_POLISH_SUPERDEEP_LEAKS ·
HOSE_FITTING_RENAME_CAP_IS_NOT_CAPPED · DEEP_DIG_EXPLAIN_WAITING_ON_NO_DROID (all BENCH, needs offline)

## Commits
(see report)
