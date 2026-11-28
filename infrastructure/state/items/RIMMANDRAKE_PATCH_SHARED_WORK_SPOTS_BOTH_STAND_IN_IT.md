# RIMMANDRAKE_PATCH_SHARED_WORK_SPOTS_BOTH_STAND_IN_IT

## What the card said

<!-- answered 2026-11-28T05:58:14Z; recorded by `file` (OWNER); written by rimflow, never by hand -->

**Question:** Fri Nov 27, 9:51 PM PST. Explosive Knockback: a colonist who carries a stack is thrown by a blast. The stack leaves its hands and lands on its own path. That is your 0.2.0 feature, and it works. The open point is what the colonist does next. Before the blast it was hauling that stack somewhere. Code added after 0.2.0 passed makes it walk back to the stack and finish the haul. No bar promises either behaviour. There are two real choices; a middle rule (walk back only when the stack is close) would cost new code for a difference few players would see. (Hard to read? Type STE, Binding or Both for a rewrite.) After the blast, what should the thrown colonist do about the stack?
**Picked:** Leave it for hauling (Recommended)
**Its description:** Why: a blast should scatter work, and you read the scatter as the fun. The colonist takes its next job by priority; the stack waits for any hauler, as in the passed 0.2.0. I take the added code out and drop the test's expectation. No new version. Costs: a revert of code that is built. Recommended: it matches your reading.
**Other options:** Walk back and finish

**Question:** Utility creatures: you order one creature to do one job, such as 'dig this pit'. First open point: how a creature comes to take such orders. Training means a handler teaches the animal a skill over days, as with hauling today. A module is a part fitted to a droid. A harness is a new wearable item for an animal that carries the tool. How should a creature come to take orders?
**His words:** Digging animals don't use shovels, they have them built-in. They should naturally dig by themselves as they desire. The training allows players to induce them to work where desired. They never need a shovel. Droids receive skills and abilities through modules and augmentation via their limbs and actuators, working together to enable the effect. Droids take work like colonists. It is open whether they can be click-commanded like a colonist or simply work in the background.
**Other options:** Train animals, module droids (Recommended) · By kind, no training · A harness makes it able · Training and a harness

**Question:** Utility creatures, second open point: the shape of one order. Your first words were about commands such as 'dig this pit' and 'cut that tree'. What should one order be?
**Picked:** One click, one job (Recommended)
**Its description:** Why: it is a command, as you said. You click one pit square or one tree; that creature does it and is free again. Simple to build and test. Costs many clicks for a big dig. Recommended: the smallest thing that proves the mod; a queue can follow.
**Other options:** A queue of jobs · A work area

**Question:** Shared work spots: one small patch lets two benches face the same standing spot, with an on/off setting. One point is open. When two workers want the shared spot at the same time, what should happen?
**Picked:** Both stand in it
**Its description:** Why: no extra code. The base game already lets two workers stand in one square while they work, so both benches run at once. Costs: two colonists drawn on top of each other.
**Other options:** One waits (Recommended) · Decide after a look
