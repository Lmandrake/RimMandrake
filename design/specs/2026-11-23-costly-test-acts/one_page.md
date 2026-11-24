# Costly test acts: one page

Full tables and sources: `analysis.md` beside this page. Study of 2026-11-23/24. No test, mod or game was changed.

**Your question.** You saw the ship fly again and again, and asked for one ship that shows everything at once.

**Short answer.** The ship flew twice, not many times. [measured] Two is the fewest the bars need today. [measured, code read]
The waste was in how each flight was staged. That waste is small: about 3 minutes of 143. [guess ~70%]
The large waste is elsewhere, and this page ranks it.

## The gravship (Gimme Some Slack)

- Visit 1 made **2 flights**: one with the keep-wires switch on, one with the switch off. [measured]
- Visit 2, which you watched, also made 2. [measured]
- The mod reads that switch once for all wires at take-off. So one flight has one switch value. [measured, code read]
- One flight needs a new offline test of the switch guard. The Conductor decides that. [guess ~70%]
- The driver builds and boards a new ship for each flight. Each boarding wait is **83.4 s, in all six flights on record**. [measured]
- The boarding order never ends when the colonists arrive. It ends only at its limit of 5,000 ticks. [measured]
- Better: build one ship, save it boarded, fly it, load the save, fly it again. 256 s becomes about 80 s. [guess ~70%]

**What the one ship carries:**
- wall brackets with a span, masts with a span, and a cut span;
- a battery with two consumers on one net;
- each look, a wall lamp, a switch and a tangle;
- a conduit run that crosses the ship's edge;
- a mast on the ground strung to the ship.

**Your wire that breaks at take-off.** The driver strings a ship-to-ground wire already, and reads it only after landing. [measured]
The mod does not break that wire. The mod takes the wire down, coils it, and shows one message. [measured, code read]
A wire that snaps is a change to the mod, so the Conductor decides it.

**A fault of the present scene.** Its text asks for brackets, a battery, two consumers and a planted control.
The scene that passed has none of the four; it has one lamp. [measured, code read] The grouped scene must add them.

## The largest savings (wall time per visit)

| rank | saving | where | build |
|---|---|---|---|
| 1 | up to 42 min [measured 2,541 s; can it wait: guess ~70%] | FlowWorks: the mod changed twice during visit 9, so 26 passes ran again | small |
| 2 | about 36 min [guess ~55%] | Pyrelands: four checks wait 37.6 game days one after another; one map needs about 15 | large |
| 3 | about 28 min [measured; needs a fix in the visit: guess ~60%] | Slack: run the full-list part last. Visit 2 already does this | none |
| 4 | 47 min [measured] | Knockback: two full-list loads. Already removed tonight | none |
| 5 | about 12 min [measured 757 s] | FlowWorks: 40 orders wait on a paused game until they time out | small |
| 6 | about 11 min [guess ~65%] | Slack: the same 172 proof rows run again on a second mod list | medium |
| 7 | about 9 min [guess ~70%] | FlowWorks: one colonist walks 17 pads, one order each, 6.7 s per order | medium |
| 8 | about 5 min [guess ~50%] | Pyrelands: 48 site loads, most checks have their own pad | medium |
| 9 | about 5 min [guess ~60%] | Knockback: 55 processes each read and write all settings | small |
| 10 | about 4 min [guess ~40%] | FlowWorks: two extra mod lists, each for one check | small |
| 11 | about 3 min [guess ~70%] | Slack: the gravship, above | small to medium |

Ranks 1 and 5 are not shared stagings. They are waste that this study found while it counted.

**What a bundle costs.** One spoiled staging loses all its readings. So each bundle saves checkpoints, and each reading keeps its
own named row. Each part also stays runnable alone, because a change reruns only the checks that it touches.

## What the scene library can do now

Three names work: `scene.open`, `s.run` and `s.raw`. The other seven are `NOT_BUILT`. [measured]
`s.run` can already end a wait on a state. `s.run` also records a value on every tick. [measured]
Ranks 2, 5, 7 and 11 need `s.stage` and `s.act`, and the gravship also needs a launch verb. [measured, pages read]
No group can give a counting verdict through the library yet. `contract` and `judge` are not built. [measured]

## Not measured

- The time that each raid costs inside a scene. No record splits it.
- The time between scripts in a visit. No record ties an agent's work to it.
- The bars of each of Slack's 206 rows. This study read only the gravship rows and the named scenes.
- A grouped scene that keeps every verdict. No grouped scene has run.
