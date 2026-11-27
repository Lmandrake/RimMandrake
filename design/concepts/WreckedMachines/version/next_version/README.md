# Wrecked Machines: next version (after 0.1.0)

Divergent work: anything that shifts or extends the 0.1.0 design (`../../sheet.md`, `../../tree.json`). Each entry is a
pre-written ticket with its acceptance test, who proposed it, when, and why it was not taken now. **Protected:
append-only for agents; removing an entry is his call.** Nothing here changes a 0.1.0 bar, and nothing here starts
work. A next version opens only after his review of a scope proposal page.

Written by the Designer at stage 3, 2026-11-27 (run `rm-role-designer-1795776308`). The entries are the lines under
"later" on `../../sheet.md`.

## A relic's value is left out of colony wealth

- **What:** the market value of this mod's machines does not count toward colony wealth, so a colony that restores
  machines does not raise its raids by it. A machine keeps its trade value. Feasibility is read from the game source
  (record decision `d_feasible_wealth`): the game's wealth count adds each player building's value, and one Harmony
  patch there can leave this mod's machines out.
- **Who, when, why not now:** the bench's note of his card of 2026-10-03 (event 1791074563677309893 in the BENCH shard;
  the card text could not be read, record scope `s_card_2026_10_03`). The note names no version, and his statement of
  the mod (OWNER:1795755622961436106) does not need it. So it is an extra, and his first-version card sends an extra
  to the next version (record decision `d_wealth_next_version`). It is not built, so no switch-off ticket is owed.
- **Acceptance test:** a staged live read, not seen red by this run (a Designer run takes no game): on a quicktest
  map, read the colony's building wealth, install one Refurbished power cell, and read it again. The two readings are
  equal, and the cell's own market value reads above zero. On the 0.1.0 build the second reading is higher.

## More carried machines: a salvaged turret first

- **What:** the other carried machines that he named, onboarded like the power cell and the emanator. A turret is the
  first. The base game has no ancient turret to be its Original, so a turret needs art of its own and its own combat
  behaviour at each level.
- **Who, when, why not now:** owner, 2026-09-20 (OWNER:1795749443608988682: "other mobile structures should also be
  included into the mod"; OWNER:1795749459948262983: "Mobile structures would explicitly include things like turrets,
  batteries, psychic emitters, and other traditionally 'archotech' sources. We'll undoubtedly author more as we go
  on."). His
  statement of 2026-11-26 names what 0.1.0 supports: the factory mod, and "archotech power supplies and psychic
  emitters" (OWNER:1795755622961436106). A turret is not in that set.
- **Acceptance test:** none yet: that version's Designer writes the bar (what a Kludged turret does in a fight) with
  its red-first check.

## Onboarding helped by a program

- **What:** a tool that drafts a machine's onboarding table (its levels, what each level makes, its two projects)
  from the machine's own defs, so that a machine of another mod can be onboarded with less hand work.
- **Who, when, why not now:** owner, 2026-11-26 (OWNER:1795755673273656447): "We may be able to semi-automate this to
  support other machines, but not in 0.1.0."
- **Acceptance test:** none yet: the tool's page of promises comes first. The oracle that it will be read against
  exists after 0.1.0: the tool's draft for the smelter equals the smelter's hand-written row
  (check `C_onboarding_table_offline` of `../../tree.json`).

## The water distillation machine moves to FlowWorks, and is then onboarded here

- **What:** the working form of the water distillation machine becomes a FlowWorks machine. Wrecked Machines then
  onboards it from FlowWorks like any other machine, with a Wrecked and a Kludged level. Its text stops naming the
  ship (bar `no_setting_named` already reads its words in 0.1.0). Until the move, the machine works as built
  (rule `R_riders`, check `C_distillation_loads`).
- **Who, when, why not now:** owner, 2026-11-26 (OWNER:1795755673273656447): "Water Distillation is definitely a
  FlowWorks machine that would then be onboarded into this mod to become Wrecked if we so desired (and without this,
  it would remain a fully functional machine in FlowWorks)." 0.1.0 supports the factory mod and the two base-game
  machines only. The open item `WRECKED_DISTILLATION_MODULE_1` holds the built machine's own debts.
- **Acceptance test:** fails today (the file exists), passes after the move:
  `test ! -e src/RimMandrake/WreckedMachines/Patches/WreckedMachines_DistillationModule.xml`, and FlowWorks' own
  check of its machine list names a working distillation machine. The second half is written by the run that moves
  the machine, because FlowWorks' def name for it does not exist yet.

## The one salvage rule gets a home of its own

- **What:** the rule for what smelting and cremation give back leaves this mod's folder. Its kernel is shared code
  already (`src/RimMandrake/_Shared/SalvageRule/`); this mod alone links it and carries its Harmony postfix, its patch
  and its two settings. After the move a game without Wrecked Machines can have the rule, and Wrecked Machines alone
  no longer changes every smelter and crematorium. Until the move the rule works as built (rule `R_riders`, check
  `C_salvage_rule_offline`).
- **Who, when, why not now:** the Designer's call (record decisions `d_riders_fate` and `d_riders_move_no_interim`;
  not his words). His answer on the three rules (OWNER:1795755673273656447) did not speak of the salvage rule. It is
  not the onboarding of a machine, so it is outside the promise of 0.1.0. It is not switched off first, because the
  rule acts on every smelter and crematorium of the campaign today. Which mod is its home is that version's first
  decision.
- **Acceptance test:** fails today (both files exist), passes after the move:
  `test ! -e src/RimMandrake/WreckedMachines/Source/WreckedMachinesSalvage.cs && test ! -e src/RimMandrake/WreckedMachines/Patches/WreckedMachines_SalvageRule.xml`,
  and the rule's selftest passes from its new home with its 41 variants (today:
  `python3 src/RimMandrake/WreckedMachines/selftest_salvage_rule.py`).

## Repair extended to ship components

- **What, who, when:** the open item `RIMMANDRAKE_EXTEND_WRECK_REPAIR_TO_SHIP_PARTS_NEXT_VERSION` holds it (owner,
  2026-11-19, OWNER:1795106694655684530: "Could even be extended to ship components and things."; the Conductor's
  call that it is next-version work is record decision `d_ship_parts_next`).
- **Acceptance test:** none, design work for a later version (the item says so).

## The Utinni specialization: holy repair, woven into the god-ship

- **What, who, when:** the open item `RIMMANDRAKE_DESIGN_UTINNI_HOLY_REPAIR_AFTER_GENERIC` holds it. It is a separate
  design in the RimUtinni tier, not a version of this mod (record decision `d_utinni_separate`). It is listed here so
  that a reader of this mod finds it. 0.1.0 leaves it three openings, each data or a signal that this mod raises
  without knowing who listens: the level-changed signal (rule `R_signal`), who may lift a wreck (rule `R_lift`), and
  the weighted list of which wrecks lie where (bar `wreck_is_found`).
- **Acceptance test:** none, design work in another tier.

## A quest that points at a wreck, and a source of a component inside this mod's own story

- **What:** a quest or an event of this mod that leads a colony to a wreck, or that rewards an Ancient Component.
- **Who, when, why not now:** the Designer's reading of his words "Only found in ruins or via plot"
  (OWNER:1795761550785045693): "via plot" is the campaign's story, and this mod has no plot (record decision
  `d_component_from_ruins`; shown to him on turn_04.md and on the sheet). A quest inside this mod would be a second
  source of the component and a different build. He can change the reading; a word from him moves this entry.
- **Acceptance test:** none yet: the bar is an experience that the Designer writes first if he asks for it.
