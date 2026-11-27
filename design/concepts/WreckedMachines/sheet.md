# Wrecked Machines, Design Version 0.1.0: the sheet

This page is the short view of the design. The complete text of each bar, with its pictures and its test, is in
tree.json. The record of every question and answer is record.json and log.md. An agent wrote the bars from your words;
each line under "does" names the bar that carries it. You can change any word.

Two words used below. An ancient machine is a machine that this mod has made ancient: each production machine of
Vanilla Furniture Expanded - Factory, the vanometric power cell and the psychic emanator, while its line in Mod
Settings is on. A level is one of Wrecked, Kludged, Refurbished and Original.

## his words

- 2026-11-26, 9:00 PM PST, typed (OWNER:1795755622961436106): "The mod changes specified furniture-installable machines such as Vanilla Factory Enhanced into advanced, ancient machines that can no longer simply be researched and built like normal. Instead, they must be found and retrieved to a safe location, studied to enable research, and then slowly repaired through several levels of functionality: wrecked (nonfunctional), Kludged (minimal), Refurbished (full functionality but slower than original), Original (no longer attainable through research or repair, used only for comparison). Each repair requires machine study, research bench time, and considerable resources. The final refurbishment requires a rare ancient component. While the concept may be applied to any game tree, the mod's initial version will only support Vanilla Factory Enhanced in this fashion."
- The same event: "This is the original intention of this mod and remains true. Please revise with the current version's detail while maintaining the truth of this statement. remember: we must first prioritize Utinni service, and VFE plus some versions of vanilla expanded items like archotech power supplies and psychic emitters will be the only supported options."
- 2026-11-26, 9:00 PM PST, by card (OWNER:1795755647483442186), on when the mod first shows itself: "Ruins, plus a rare wreck".
- 2026-11-26, 9:01 PM PST, typed (OWNER:1795755673273656447): "Giving the "smelter first" is an Utinni-tier decision independent of this mod about machine availability. Each machine Certainly Will need specific recipies blessed per repair tier, production rates, etc... that will be the normal onboarding process for any device into the Wrecked Machines mod. We may be able to semi-automate this to support other machines, but not in 0.1.0. Water Distillation is definitely a FlowWorks machine that would then be onboarded into this mod to become Wrecked if we so desired (and without this, it would remain a fully functional machine in FlowWorks)."
- 2026-11-26, 10:20 PM PST, typed (OWNER:1795760440829904733): "Yes I will look at the existing wrecked machines. By the way they CAN be moved with special hauler droids or machines you can ride in through droidworks but notified or built."
- 2026-11-26, 10:38 PM PST, by card (OWNER:1795761534460592124), on how many of the factory's machines are ancient in 0.1.0: "All 18 machines".
- 2026-11-26, 10:39 PM PST, typed (OWNER:1795761550785045693), on where a colony gets an Ancient Component: "Only found in ruins or via plot".
- 2026-11-26, 10:56 PM PST, by card (OWNER:1795762605668672773), on how a wreck gets home in a game without Droidworks: "Colonists carry it".
- 2026-11-27, 12:44 AM PST, typed (OWNER:1795769070699312426), on what gives plasteel: "1: b." Option b was our text: the Refurbished forge; plasteel is the recipe that the last repair brings.
- 2026-09-15 (OWNER:1795749349214480499): "the wrecked machines mod should be independent of the god favor... it should be its own stand-alone mod (RimMandrake level) and the Salvation Engine should require it."
- 2026-09-15 (OWNER:1795749411129133147): "There is nothing beyond or even equal to the original."
- 2026-09-15 (OWNER:1795749426260848822): "Hopefully we can structure it to actually have you study the MACHINE itself as part of the 'research.'"
- 2026-09-15 (OWNER:1795749529567808948): "The existing mod is about repairing big machines in place, and that's excellent."
- 2026-09-15 (OWNER:1795749476635482102): "introduce the concept that refurbishment requires Ancient Components, a truly scarce and valuable resource"
- 2026-09-16 (OWNER:1795749543738184808): "remove the VFE factory, not the manual one."
- 2026-11-06 (OWNER:1793986102064766481): "For wrecked machines, they should ALL draw in the piping and conduit the same way, not only at a certain value of fixedness. Otherwise it produces gaps between pipes, conduit, and the unit that are not representative."
- 2026-11-19 (OWNER:1795106694655684530): "I suspect it's a good, strong concept save for the much larger lift in terms of art generation, but we're pretty good at that."

## what it is

Wrecked Machines changes specified machines that install like furniture, such as those of Vanilla Furniture Expanded - Factory, into advanced, ancient machines. A colony can no longer simply research and build one. A colony must find one and bring it to a safe place. Colonists study the machine, and the study opens its research. Then they repair the machine slowly, through levels of function. A Wrecked machine does not work. A Kludged machine works at a minimum. A Refurbished machine has full function, but is slower than the original. The Original is a fourth level, there only for comparison: no research and no repair reaches it. Each repair needs study of the machine, time at a research bench and considerable resources. The last repair, to Refurbished, also needs a rare Ancient Component. The idea can be applied to any game tree. This first version supports only Vanilla Furniture Expanded - Factory in this way, and some versions of vanilla expanded items such as archotech power supplies and psychic emitters.

That paragraph is your statement, rephrased as you allowed. It is the root of the design (root.md).

## does

- [leaf:only_by_repair] A player cannot research and build an ancient machine, and nothing in the world gives the colony a working one: the colony gets a working one only when its colonists repair a wreck.
- [leaf:wreck_is_found] A player meets wrecked machines in the world: they lie in the rooms of ancient ruins, and now and then one lies half-buried on an ordinary map when the colony arrives.
- [leaf:wreck_comes_home] Colonists can take up any wreck, carry it away and set it down where the colony wants it.
- [leaf:study_opens_research] Colonists study the machine itself, and only that study opens the research for its next repair.
- [leaf:repair_on_the_machine] A player orders a repair on the machine, colonists bring the materials and work at it where it stands, and the machine stays in sight at its old level until the work is complete.
- [leaf:levels_of_function] A Wrecked machine does no work, a Kludged machine does a small part of the machine's work, a Refurbished machine does all of it, and no repaired machine does it as well as the Original.
- [leaf:last_repair_needs_component] The repair to Refurbished needs an Ancient Component, and a colony gets one only by finding it in an ancient ruin.
- [leaf:levels_told_apart] At play zoom a player tells a Wrecked machine, a Kludged machine and a whole machine apart by eye, and what the picture shows agrees with what the machine's text says.
- [leaf:switch_gives_machine_back] In Mod Settings a player switches any one ancient machine off, and that machine is then the ordinary machine that it was without this mod.
- [leaf:no_setting_named] A player reads no name or mark of any story setting in this mod: no ship, no faction and no god.
- [leaf:wrecks_join_lines] Pipes and conduit that run to a wreck draw into it as they draw into the same machine at its repaired levels, with no gap.
- [leaf:whole_journey] With every ancient machine on and nothing done by a command, a colony finds a wreck, brings it home, studies it, repairs it to Kludged and uses it, then studies it again and repairs it to Refurbished with an Ancient Component from a ruin, and at each step the player can tell what the machine needs next.

## calls that an agent made, which you can undo

Each call is the Designer's and is logged for your daily digest. None is your words.

- From turn 5, shown to you on turn_05.md: a repair is ordered and made on the machine, and a cancelled repair never costs the colony the machine. While a machine's line is on, the world hands out no working one, the base game's vanometric power cell and psychic emanator included. Gravlite sits with plasteel on the Refurbished forge.
- New in this stage. A wreck can be set down on any firm ground. A working level needs the ground that the factory mod's machine needs, which is the factory floor. So a repair order on a wreck that stands on other ground is unavailable and says so, and the factory floor stays in the build menu behind the factory mod's own research. Measured from the factory mod's files: 14 of its machines in the main file need that floor, and the floor is opened by the research Basic Factories.
- New in this stage. An order to uninstall a machine that is under repair cancels the repair first: the materials are given back and the machine is carried at its old level.
- New in this stage. The first showcase, the mod's face, is the smelter's road home: a wrecked smelter found in a ruin, carried home, studied, made Kludged, studied again and made Refurbished with a component. Nothing was found against it: the smelter is the one machine with pictures of its own today, and the build takes it first.
- "Via plot" is read as the campaign's story. This mod has no plot; the component is a plain item that a mod above this one can hand out.

## what it costs

- Pictures. Each of the 18 factory machines needs 8 new pictures (Wrecked and Kludged, four facings); the smelter has its 8. The power cell and the emanator each need a Wrecked and a Kludged picture of their own, and the Ancient Component needs one. An art judge reads each against the canon library.
- Research screen. Two restoration projects for each of 20 machines: 40 projects, on one tab of their own.
- A stranger's game. With the mod at shipped settings, the factory mod's production machines leave the build menu, and the base game no longer hands out a working vanometric power cell or psychic emanator. One line in Mod Settings gives any one machine back.
- A colony that finds no Ancient Component stops at Kludged. With this mod and the factory mod alone, a Kludged alloy forge makes obsidian and nothing else.
- Onboarding is by hand: 19 more machines after the smelter, each with its table of what every level makes.

## does not

- It does not leave a relic's value out of colony wealth. That is on the list for the next version.
- It has no turret, no ship part and no holy repair. The Utinni layer is a separate design after this one.
- It does not move the salvage rule or the water distillation machine. Both work as built until they move to their own homes, and no bar of 0.1.0 judges them.
- It has no quest that leads to a wreck or rewards a component.
- It does not onboard a machine by a program. Onboarding is by hand in 0.1.0, in your words.

## later

- A relic's value left out of colony wealth (the bench's note of your card of 2026-10-03).
- A salvaged turret, and the other carried machines that you named on 2026-09-20.
- Onboarding helped by a program, for the machines of other mods.
- The water distillation machine: its working form moves to FlowWorks, and it is then onboarded here from FlowWorks.
- The one salvage rule moves out of this mod's folder to shared code with a home of its own.
- Repair extended to ship components (a next-version ticket exists).
- The Utinni specialization: the holy side of repair, woven into the god-ship (its own design ticket exists).
- A quest that points at a wreck, and a story source for a component inside this mod.

## not read

- Your four words "but notified or built" (2026-11-26, 10:20 PM PST). Their meaning is not known, and nothing in this design rests on them.
- Your reaction to the 9 captures of the first look, which the Conductor sent you at 12:00 AM PST on 2026-11-27. No word of yours about them is on the ledger. A word from you reopens the design.
