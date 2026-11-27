# Wrecked Machines, Designer turn 3 (stage 2: the edge of the mod)

Run `rm-role-designer-1795761299`, 2026-11-26, 10:45 PM PST. For the Conductor to serve as a question card. The new
ask is in `record.json` (`a_who_moves_a_wreck`). The two asks of turn 2 still wait and do not change. A fresh agent
that did not write this page reviewed the ask and the page before sending (the review line is at the end).

## What I took from your reply

Your reply, 2026-11-26 at 10:20 PM PST: "Yes I will look at the existing wrecked machines. By the way they CAN be
moved with special hauler droids or machines you can ride in through droidworks but notified or built."

- **You will look.** The look is now owed work, with its own item
  (`RIMMANDRAKE_STAGE_WRECKED_MACHINES_LOOK_HE_SAID_YES`). What the save shows is written in
  `D:\Luke\dev\RimMandrake\design\concepts\WreckedMachines\look_01.md`: the smelter, the power cell and the psychic
  emanator at each built grade side by side, a colonist sent to study a wreck, a Kludged smelter about to be built over
  a wreck, and a wrecked smelter beside a wrecked power cell with a colonist, so that you can see what moving a wreck
  is today. I do not stage it; a Designer run may not take a game.
- **A wreck can be moved, by a special hauler droid or by a machine that a colonist rides in.** I took that as said.
  It corrects reading 1 of turn 2, where I had a colonist take a big wreck up by hand like furniture.
- **"but notified or built".** I read nothing into these four words. The Conductor asked you what they mean.

## What I measured after your reply

- A hauler exists in code. The job is in the Property mod (`src/RimMandrake/RimProperty`, the RimMandrake tier). The
  job names no droid: a pawn whose race carries a marker may uninstall a building of any faction and carry it off.
  Patches put the marker on five Droidworks chassis: the Muckraker and four labour and mining droids.
- That job acts only on a building that has a carried form. The built smelter wreck has none. So today no pawn, a
  hauler droid included, can lift the built smelter wreck. The power cell wreck and the emanator wreck have a carried
  form, and a colonist lifts them.
- The lift list of 2026-11-01 (`design/RimMandrake/salvage_lift_policy_2026-11-01.md`) agrees on the droid: a wrecked
  machine is "droid only", and "a colonist still may not move it". It does not name ride-in machines. The pass that
  would apply that list in the game is not built: its tags are in no def and no code of a mod.
- I found no machine that a colonist rides in and that moves a building. I searched Droidworks' defs and source for it.
  A search that finds nothing is not proof that none is planned.
- Droidworks is a RimStarWars mod. Its own page calls it a "Private campaign mod", and it needs Humanoid Alien Races.
  Wrecked Machines stands alone at the RimMandrake tier (your ruling), so it cannot lean on Droidworks.
- The factory mod's smelter is 3 by 4 cells and weighs 60 kg. All 16 machines in the factory mod's own def file have a
  carried form. (Turn 2 counted 18 production machines; the other two were not read again in this run.)

## Reading 1 of turn 2, corrected

What stands: a wreck is brought to a safe place, and each repair is made on the machine where it stands. The build
gives the smelter wreck a carried form, because a hauler needs one too.

What is open again: **who lifts it.** In the campaign your reply answers it: a hauler droid, or a machine that a
colonist rides in. In a stranger's game there is no Droidworks. That is the ask.

## Ask 3: who moves a wreck in a game without Droidworks

**Claim.** In a game without Droidworks, colonists move a wreck by hand. Who may lift a wreck is data, and the campaign
narrows it to haulers.

**Attack.** An ancient machine of 3 by 4 cells that one colonist picks up like a bed does not read as ancient or as
heavy. Your reply says that a wreck can be moved by a hauler droid or a ride-in machine. The lift list of 2026-11-01
makes a wrecked machine "droid only". The built mod's own design says that a wreck is "not haulable" at all.

**Picture.** A stranger's game has Wrecked Machines and the factory mod, and no Droidworks. Three colonists stand in
the rooms of an ancient ruin, in front of a wrecked smelter.

- If colonists move it by hand: they uninstall the wreck, as they would any machine of the factory mod. One colonist
  carries it across the map. To take it to another tile, the caravan must carry 60 kg, and one colonist carries
  35 kg, so the wreck takes most of what two colonists can carry. At home they set it down and begin the study. In the campaign the
  lift list takes the lift from colonists, and a hauler droid walks the wreck out; this mod does not know that
  Droidworks exists.
- If only a heavy hauler moves it, and this mod brings one: the stranger must first get the hauler, a machine that this
  mod adds for a game without Droidworks. It is new: a thing to design, to draw and to build, larger than the
  onboarding of one factory machine. Only then does the wreck come home.
- If only a heavy hauler moves it, and this mod brings none: in a stranger's game the smelter wreck stays in the ruin.
  The colony can study it there, and the knowledge stays with the colony. A colony repairs a wreck only where it
  lies, and a repair in a ruin on another tile is left behind when the colonists go home. So the wreck that a stranger
  restores and uses is the rare one on the home map. The root's sentence "found and retrieved to a safe location" is
  then true only where a hauler from another mod is loaded.

> **a_who_moves_a_wreck.** A stranger's game has Wrecked Machines and the factory mod, and no Droidworks. Three
> colonists stand in an ancient ruin in front of a wrecked smelter of 3 by 4 cells. How does it get home?
> - (a) By hand: colonists uninstall it and carry it, as they carry any machine of the factory mod. Who may lift a
>   wreck is data that a layer above can narrow, so the campaign gives the lift to hauler droids and ride-in machines
>   only.
> - (b) Only by a heavy hauler, in every game, and this mod brings a plain hauler of its own for a game without
>   Droidworks.
> - (c) Only by a heavy hauler, in every game, and this mod brings none: without one, a colony repairs a wreck only
>   where it lies.
>
> I recommend (a). The test I judged on: can a stranger with this mod and the factory mod alone do what your statement
> says, "found and retrieved to a safe location"? What (a) costs: in a stranger's game an ancient machine is as easy
> to lift as a loom.

## The two asks of turn 2 still wait

- **a_which_factory_machines:** how many of the factory mod's machines are ancient in 0.1.0: one, all, or a proven
  handful of three. I recommend the handful.
- **a_component_source:** where an Ancient Component comes from: out of another wreck that is taken apart, a rare find
  in a ruin, or both. I recommend both.

The full text of both is in `D:\Luke\dev\RimMandrake\design\concepts\WreckedMachines\turn_02.md`.

## What I did not ask, and why

- What the hauler droid or the ride-in machine is, and how it lifts: that is Droidworks' and the Property mod's
  design, not this mod's.
- Whether a Kludged machine can be moved: it is data of each machine and stays as built (turn 2, reading 1).

## Review

A fresh Opus judge (agent a44e086c95b4295e7, not the author) read the ask and this page against your words on the
ledger, the built mod, the Property mod's hauler, the lift list and the factory mod's defs. The ask passes: your reply
settles the campaign only, nothing built settles a stranger's game, and each answer builds something different. It
found that the ask reads nothing into "but notified or built". What the review changed on this page:

- A sentence that guessed the four words might be this same question is gone.
- The Attack no longer says that your reply, the old design and the lift list "all say" one thing. Your reply says a
  wreck *can* be moved by a hauler; the lift list says "droid only"; the built mod's design says "not haulable".
- The line on the lift list no longer says that it says what your reply says. It agrees on the droid and does not name
  ride-in machines.
- The picture for answer (c) now matches the answer's own words: a repair in a ruin is possible and is left behind.

The judge checked every other measured claim against its source and found each one true. It could not check the count
of 18 machines of turn 2 (this run read 16 in one def file) or how complete my search for a ride-in machine was; its
own search also found none.
