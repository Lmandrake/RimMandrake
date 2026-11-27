# Wrecked Machines 0.1.0: the models

A model is the cheapest instrument that settles a risk which an argument cannot settle. The first one is built first:
one meeting of `tree.json` (`study_progress`) is `unknown` and names it. The question "offline simulation: yes or no,
and why" is answered in `plan.md` under `## offline simulation`; the second and third entries here are the detail of
that yes.

## Study on a building

- **The question.** Does the base game's own study of a thing work on a building in play, as the design needs it: a
  researcher takes the study by himself after the player turns it on once, the research screen names the machine that
  is not yet studied, and the machine shows how far its study is?
- **What it informs.** Bar `study_opens_research`; bar `whole_journey`; rules `R_two_projects` and `R_study_carrier`;
  the `unknown` meeting `study_progress`.
- **Form.** A live spike, not an offline model. No offline instrument can be believed here: the unknown is the
  behaviour of the game's own job and work givers on a thing class that the base game never gives them.
- **Assumptions.** Read from the game's source through RimSage (record decision `d_feasible_study_in_vanilla`): the
  comp that unlocks research after analysis has a study-in-place switch, a required count, progress and completion
  letters; a research project that lists a thing as "must be analysed" stays locked until the count is met; progress
  is kept by an analysis id in the game's manager, not on the thing. Biotech's mechanitor chips use it on items. No
  base-game building uses it.
- **Inputs and range.** One wreck def with the comp, one project that lists it, one researcher. Three variations: the
  wreck installed at home and standing where it was found; Research Reinvented absent and loaded (the small list holds
  it); a save and a reload in the middle of the study. Left out: all 20 machines (one def decides the mechanism).
- **What in the real game checks it.** The game itself: `jawa/research_availability` before and after, the
  researcher's job while the clock advances, the wreck's inspect text, and one capture of the research screen with the
  locked project selected.
- **Output.** A table of six rows (the three variations, each for "takes the job by himself" and "screen names the
  machine"), and one sentence: the base game's study carries the design, or it does not.
- **The decision it changes.** If the study does not work on a building, the build writes a study job of its own
  (rule `R_study_carrier` is attacked first; the bar does not move). If Research Reinvented's study on top hides or
  doubles the base game's, the mod's Research Reinvented defs are removed or kept, by what a player then sees.
- **Build trigger.** The `unknown` meeting. It is the first thing built, before any machine is onboarded.

## Repair state walk

- **The question.** Over every state of a machine under repair and every event that can reach it, do the three
  statements hold: a cancel never loses the machine; the level changes only on complete work; the level-changed signal
  fires once for each change?
- **What it informs.** Bars `repair_on_the_machine` and `whole_journey`; rules `R_uninstall_cancels`, `R_ground`,
  `R_signal` and `R_destroyable`; check `C_repair_state_walk`; the meetings `machine_level` and `repair_order`.
- **Form.** The shipped code against a fake game: the repair record and its transitions live in the Verse-free kernel
  (`src/RimMandrake/WreckedMachines/Source/Kernel/RM_WreckedMachinesKernel.cs`), and the walk drives that kernel as the
  existing fuzz does (`Source/SelfTest/WreckedFuzz.cs`). Not a copy of the logic.
- **Inputs and range.** States: level (Wrecked, Kludged, Refurbished) x study (none, part, complete) x project (locked,
  open, finished) x order (none, given, materials in part, materials complete, work in part) x ground (donor's floor,
  other) x component (none, one). Events: order, cancel, deliver, work, uninstall, destroy, save and load, the
  machine's line switched off and on. Every reachable pair is visited, and seeded random event strings of length up to
  40 on top.
- **Left out.** Colonist jobs, hauling and paths; the base game's study comp; placement on maps; pictures. Those are
  read live.
- **What in the real game checks it.** The scenes `sc_repair_on_machine`, `sc_repair_cancelled` and
  `sc_uninstall_during_repair`: the live readings of level, record and delivered materials at each step must equal the
  walk's states for the same event string. Agreement on those three strings is enough.
- **Output.** A table of states by events with the next state, about 600 cells, and the list of event strings that
  break a statement (expected: none).
- **Build trigger.** Built with the repair mechanism itself, test first: the three statements are red on a kernel
  that has no repair record.

## Onboarding table against the donor

- **The question.** Does each of the 20 onboarding rows keep the one rule of the table: the Kludged level is a part
  of the donor machine's work that is not empty, and the Refurbished level is all of it?
- **What it informs.** Bar `levels_of_function`; rules `R_onboarding`, `R_forge` and `R_kludged_move`; checks
  `C_onboarded_set`, `C_onboarding_complete` and `C_onboarding_table_offline`; the meetings `onboarding_table` and
  `forge_processes`.
- **Form.** An offline read of data: the mod's shipped XML and patches applied to the factory mod's real defs with
  the patch interpreter that `src/RimMandrake/WreckedMachines/selftest_wm_onboarding_table.py` holds.
- **Inputs and range.** The factory mod's defs as installed (workshop folder 3686924415, 1.6), with and without
  Vanilla Cooking Expanded; all 20 rows; the processes that load only with another mod.
- **Left out.** Whether a Kludged part is useful to a colony: a judgment, read by the bar. What the C# changes at
  startup: read live by `sc_levels_do_their_work`.
- **What in the real game checks it.** One live read of `jawa/comp_read` for the processes of each level of two
  machines; the lists must equal the offline lists.
- **Output.** One row for each machine: the donor's processes, the Kludged part, the Refurbished list, and a pass or
  a named fault.
- **Build trigger.** Built with the second machine's onboarding: the smelter's row is written by hand first, and the
  read must pass on it before a second row is added.
