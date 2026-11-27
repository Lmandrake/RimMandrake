# Wrecked Machines: the open tickets, bundled for the Designer (2026-11-26)

Item: `RIMMANDRAKE_READY_PIPELINE_FOR_WRECKED_MACHINES_HE_HOLDS_GO`, step 3 of the Conductor's brief. This file is an
input for the Designer of WreckedMachines Design Version 0.1.0. It decides nothing. The Designer decides each
question below in its own stages. No ticket's work was done here.

The owner's go, 2:33 PM PST 2026-11-26, on the item: "I authorize you to do an all fable experiment on wrecked machines.
We can afford it. Let's see how it goes. Gather all those tickets together as a bundle, design run for it to clarify and
put needed bars and tests, then let's see how fable 5.2 does. Hopefully beautifully. Of course it should intelligently
subagent fanout as needed."

**How the list was made.** `python3 src/RimMandrake/rimflow/list_home.py list`, run once at 2:43 PM PST 2026-11-26
(output kept: `D:\ClaudeWork\rimmandrake\helpers\wm_fable_go_20261126\list_home.txt`). It lists 9 open tickets with
the home `mod:WreckedMachines` and 1 with the home `mod:Wreckage`. Each ticket was read whole
(`rimflow show`, kept beside the list as `show_<ID>.txt`) and against the code at origin/main 623c58bee6.

**Count.** 10 tickets. 1 is the readiness item itself (not Designer work). 0 are dropped: none is stale or wrong.
7 are design input for 0.1.0. 2 are for later versions or another mod. All are listed below.

**The mod today** [measured 2026-11-26]: `src/RimMandrake/WreckedMachines` (`mandrake.rm.wreckedmachines`; needs Harmony
and VFE Factory). C#: `WreckedMachinesMod.cs` (settings, the alloy-forge patcher), `WreckedMachinesLadder.cs` (the
grade ladder), `WreckedMachinesSalvage.cs` (the one salvage rule), `Kernel/RM_WreckedMachinesKernel.cs`. Patches: the
salvage rule, the alloy-forge gates, the distillation module, a hidden donor smelter. Old text, which is input and not
settled: `DESIGN.md`, `MACHINES.md`, `V2.md`, the north-star walk `design/validation_walks/RimMandrake/WreckedMachines.md`.
No defName, label or description in `Defs/` or `About/` names Rakatan, Utinni, Jawa or Star Wars (grep, 0 hits).

---

## The tickets that shape 0.1.0

### RIMMANDRAKE_ADMIT_WRECKED_MACHINES_FABLE_GENERIC_FIRST (the mod's first-touch Designer item)
- **Asks:** admit WreckedMachines, the generic RM_ tier, at Design Version 0.1.0; build it start to finish on Fable 5.2;
  compare it with an Opus build of a similar mod (Graffiti is the proposed control) on cycles to a green certificate,
  in-game failures and weighted tokens.
- **His words (2026-11-19, about 8:35 AM PST):** "Ok, Wrecked Machines it is. It has a generic possible implementation
  and then the Utinni-specific weaving it into the god-ship concept. First decision would be whether we even bother
  with the generic version. I suspect it's a good, strong concept save for the much larger lift in terms of art
  generation, but we're pretty good at that. Then the Utinni specialization would bring in the holy aspects of
  repairing the work. Could even be extended to ship components and things. Needs a LOT of work using our modern
  Design passes of course, we didn't have anything like that before." His hold of 9:02 AM PST the same day ("Do not
  yet run the Fable-only passes... we don't know if the Pipeline is really ready, and this is a very expensive test.")
  is lifted by his go above.
- **Still true:** yes. The concept folder is made in this run; the item's criteria name Stage 1 on Fable 5.2.
- **The Designer decides:** the case for and against a generic version, written in the design text (his "First
  decision would be whether we even bother"; the Conductor's delegated reading is that the generic mod is the one
  Fable takes). What 0.1.0 is, as experiences a player sees. The old text is input only.

### RAKATAN_ARCHOTECH_MACHINES_1 (his design session of 2026-09-15 and his rulings after it)
- **Asks:** extend Wrecked Machines into robust, graceful-failure ancient tech: study the machine as research, mobile
  structures, refurbishment that costs a scarce resource, manual first and ship automation late.
- **His words** (verbatim in the item file `infrastructure/state/items/RAKATAN_ARCHOTECH_MACHINES_1.md`; the ones that
  bind the RM_ tier):
  - "the wrecked machines mod should be independent of the god favor... it should be its own stand-alone mod
    (RimMandrake level) and the Salvation Engine should require it."
  - "There is nothing beyond or even equal to the original."
  - "Hopefully we can structure it to actually have you study the MACHINE itself as part of the 'research.'"
  - "I would now formally like to add that other mobile structures should also be included into the mod."
  - "Mobile structures would explicitly include things like turrets, batteries, psychic emitters, and other
    traditionally 'archotech' sources. We'll undoubtedly author more as we go on."
  - "introduce the concept that refurbishment requires Ancient Components, a truly scarce and valuable resource as
    well as the tech to do so (from the ship). At first manual refurbishing is all that's possible, but eventually the
    ship's auto-repair systems will turn back on that slowly repair ship structure and refurbish ever-larger machines
    onboard automatically."
  - "There are no 'hull sockets,' they are just buildings that get installed on the gravship like any other."
  - By card 2026-10-03 (note on the item, not his typed words): wrecked ancient machines can be destroyed like any
    building; relic value does not count toward colony wealth; relics are found at ancient ruin sites.
  - His early "would exceed modern technology even in a still kludged manner" is WITHDRAWN by his later ruling that
    nothing reaches the original.
- **Still true:** yes, as rulings. The built parts are in the code (the ladder in `WreckedMachinesLadder.cs`, ratio
  settings, `RM_WM_AncientComponent`, the power-cell and emanator lines). Open since 2026-10-06: no source of Ancient
  Components, no wrecks at ruin sites, no wealth exclusion, no turret line, placeholder art, nothing proven live.
- **The Designer decides:** which of these the player meets in 0.1.0 and which wait. Where Ancient Components come
  from. Whether the "ship" words (ship tech, ship auto-repair) belong to the RM_ tier at all, since the RM_ tier must
  be "complete and playable in a vanilla game" and say no setting word; the ship parts may belong to the Utinni ticket
  below. The per-class Wrecked value for a factory (only the battery's 0.001 is set).

### SHIP_ALLOY_FORGE_1 (the alloy forge: durasteel early, plasteel late)
- **Asks:** the VFE alloy forge reachable early, its recipes unlocked in steps: durasteel early (steel + zersium, an RSW
  process), plasteel late; each step a setting.
- **His words (2026-10-09):** "Yes, I think we will need an alloy forge. Maybe even earlier, but the recipies will
  unlock later in the game for more difficult alloys. Durasteel earlier, plasteel later..." and "I like the forge makes
  that mineral. We had also said asteroids. It's ok if it's both or another minerals in space either way." By card:
  zersium's home is The Forge biome ("No. The Forge biome.").
- **Still true:** yes. Built offline at e08969370e (forge research after the smelter, industrial components in the
  early cost, plasteel behind `RM_WM_PlasteelAlloying`). Owed: a load on the small list that shows the gates (its L5)
  and the item's L1 row. The durasteel half lives in the Armoury mod (RSW tier), not here.
- **The Designer decides:** whether the forge's gates are part of WreckedMachines 0.1.0 (they live in this mod's
  patches and settings today) and what the player sees of them, as a bar that names no number.

### WM_PLASTEEL_RESTORE_FIX_FORGE_FORGETS (a live check went red on 2026-11-03)
- **Asks:** fix `plasteelAlloyEnabled_restores_the_shipped_def`: after the plasteel setting was switched off and on,
  the forge's comps and process list did not match the shipped def.
- **His words:** none (filed by a run).
- **Still true:** cannot tell. A later commit (50d9b5628e, "plasteel re-enable keeps its slot"; then e08969370e)
  changed the re-enable to return plasteel next to its loaded neighbour, which answers the process-order half. The
  comps half ("both CompPowerTrader and CompPowerTrader_Overclocked present") is not touched by any commit since, and
  may be the check's own reading (a deep list printed as type names; the same harness trap is recorded on
  WRECKED_DISTILLATION_MODULE_1). The row still exists (`validation.py` lines 486 and 508). No live run since.
- **The Designer decides:** whether a setting that restores its def is a bar of 0.1.0 ("every switch, off then on,
  gives back the shipped behaviour"), and so whether this row becomes a deciding check with a red-first test.

### SALVAGE_RULE_PROVE_ON_A_REAL_FURNACE (the one salvage rule, never loaded)
- **Asks:** a live proof that the one salvage rule pays `Thing.SmeltProducts` for multi-material apparel smelted and a
  dressed corpse cremated, and that the settings-off paths pay the donor rule and vanilla.
- **His words:** none (filed by a run that had no Windows access).
- **Still true:** yes. The code exists (`WreckedMachinesSalvage.cs`: `RM_ResultWorker_SalvageRule`, a Harmony patch on
  `Process.SpawnOrPushToNet`, `RM_RecipeWorker_CremateSalvage`; `Patches/WreckedMachines_SalvageRule.xml`, 3
  workerClass edits). No load has run it.
- **The Designer decides:** whether the salvage rule is part of this mod's 0.1.0 (it touches the smelter and the
  crematorium, not wrecks), and if so the experience bar and its test. The jawa scavenge design below may claim the
  same ground.

### WRECKED_DISTILLATION_MODULE_1 (a distillation machine in the wreck grammar)
- **Asks:** a Wrecked/Kludged/Repaired distillation building that turns distillable liquids into fresh water, refuses
  tar and oil, with a rate per tier.
- **His words:** none on the item.
- **Still true:** yes, built (3e473f37c0, `Patches/WreckedMachines_DistillationModule.xml`, conditional on FlowWorks);
  the defs loaded once (2026-10-07); salt-to-fresh and tar refused were never run live; placeholder art. The FlowWorks
  sweep of 2026-11-22 kept it for FlowWorks 0.2.0, not a FlowWorks 0.1.0 bar.
- **The Designer decides:** whether it is a WreckedMachines bar, a FlowWorks one, or neither in 0.1.0. Its tier names
  use "Repaired", which the 2026-09-15 ruling made the 1.0 rung with no def of its own.

---

## Tickets for later versions or another mod (input, not 0.1.0 bars)

### RIMMANDRAKE_DESIGN_UTINNI_HOLY_REPAIR_AFTER_GENERIC
- **Asks:** a separate RimUtinni-tier design of the holy aspect of repair on the Jawa god-ship, after the generic
  design locks.
- **His words:** "It has a generic possible implementation and then the Utinni-specific weaving it into the god-ship
  concept. ... Then the Utinni specialization would bring in the holy aspects of repairing the work."
- **Still true:** yes; not before 0.1.0 locks.
- **The Designer decides (now):** only what 0.1.0 must leave open for it: the neutral "grade changed" signal a layer
  above can listen to, and how a wreck that can be destroyed (his card of 2026-10-03) sits with V2.md §7's "sacred
  scrap cannot be cleared". That conflict is a question for the Utinni design; 0.1.0 follows the card.

### RIMMANDRAKE_EXTEND_WRECK_REPAIR_TO_SHIP_PARTS_NEXT_VERSION
- **Asks:** extend wreck repair to ship components, in the next Design Version.
- **His words:** "Could even be extended to ship components and things."
- **Still true:** yes; Divergent, never a 0.1.0 bar.
- **The Designer decides:** to record it as a next-version line, nothing more.

### SALVAGE_WRECKAGE_EVERYWHERE_1 (home `mod:Wreckage`: another mod, `src/RimMandrake/Wreckage`, `mandrake.rm.wreckage`)
- **Asks:** wreck families scattered in every hostile biome, weathered per biome, with loot on careful deconstruction.
- **His words (2026-09-25):** "I like the wreckage you made, game should be filled with lots of this all over the place
  given it's salvage focus." His card rulings of 2026-10-03 (notes on the item) set the density by biome, a full
  scavenging loop with a new Salvaging skill, and smelting as an "unholy" fallback.
- **Still true:** yes, for the Wreckage mod. It is not WreckedMachines' work.
- **The Designer decides:** only the border between the two mods: a wreck family (Wreckage, loot on deconstruction)
  and a wrecked machine (WreckedMachines, repaired up a ladder) must stay two different things to the player, and
  0.1.0 must not take Wreckage's scavenging loop.

### RIMMANDRAKE_READY_PIPELINE_FOR_WRECKED_MACHINES_HE_HOLDS_GO (the readiness item)
- Not Designer work. It holds the readiness list
  (`D:\ClaudeWork\rimmandrake\conductor\readiness_wreckedmachines_20261126.md`) and this bundle.

---

## Faults seen on the way (one line each; no ticket)
- The ticket `RIMMANDRAKE_LIFT_VOID_HOLD_ON_DONE_RUN_NOT_MIDNIGHT` (not this mod's) reads proposed although its fix
  landed (36e31b05f0). Recorded on the readiness list.
