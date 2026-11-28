# RIMMANDRAKE_FLESH_OUT_UTILITY_CREATURES_AND_SHARED_SPOTS_HIS_PICK

## What the card said

<!-- answered 2026-11-28T05:31:41Z; recorded by `file` (OWNER); written by rimflow, never by hand -->

**Question:** Fri Nov 27, 9:25 PM PST. Explosive Knockback 0.2.0 passed your walk on Nov 26. One day later a test run found a real fault: a colonist thrown while hauling loses the haul. The carried stack lands a moment after the colonist, and the mod had stopped looking for it. The fix is already in the code, and a fresh reader found nothing wrong in it. By the record, one thing is still owed: one in-game run of the thrown-hauler scene at the map spot where the fault showed. A patch version (0.2.1) only corrects: it adds no feature and moves no bar. A next version opens only on your answer. (Hard to read? Type STE, Binding or Both for a rewrite.) What should the next Explosive Knockback version hold?
**His words:** I don't read this as a fault. A colonist hauling something loses the haul... it flies out of their hand and lands awhile later. Sounds great! what's the problem?
**Other options:** Patch now, test now (Recommended) · Patch now, test later · No patch; next feature version

**Question:** Three ideas of yours sit in the Pre-Design Concepts store. A Pre-Design Concept is an idea that nobody has designed yet; it sleeps until you pick it. To flesh one out means a design talk between you and me that ends in a design, not in a build. No idea is lost if it sleeps: this card comes back in a week. Which ideas do you want to flesh out now?
**Picked:** Utility creatures
**Its description:** Why: you called it a good one. The player orders one trained animal or droid to do one job, such as 'dig this pit' or 'cut that tree'. A new mod. Costs the longest talk: which creatures take orders, how one learns to, and how it holds a shovel are all open.
**Picked:** Shared work spots
**Its description:** Why: tighter workshops. Two benches may face one shared standing spot. You already placed it in the small patches mod, as polish. Costs the least: one small patch and one live look at whether two workers queue or stand in each other. That mod is not in the pipeline yet.
**Other options:** Lost cargo quests · Let all three sleep (Recommended)

**Question:** You wrote tonight: 'I think making tree shade might be a timely pre-design or design-adaptation project, given we worked on it and it technically touches all of our biome mods'. What exists: tree shade is a part of Direct Sun, the one heat-and-shade model for every map. Its code sits in two mods, Creature Behaviors and Environmental Hazards. Three design files describe it. Four parked tickets plan to move it into its own mod. On Nov 26 you called Direct Sun 'an essential mod that's quite welcome to develop alongside us'. It has no place in the mod pipeline yet: no vision, no bars, no version. The Designer is the role that writes a mod's vision and bars. What form should the tree shade project take?
**His words:** I'd like it to remain as part of Direct Sun, as an addition to the obvious shade induced by hard walls. We should also add shadows cast by mountain-covered squares that are much larger than short walls would, so you get a feel for said mountain on the map depending on the sun angle. Very cool! So Tree Shade + Direct sun + mountain shade should all receive this design attention now to bring it to a full modern design with tests, etc.
**Other options:** Design it as its own mod (Recommended) · Concept file only · Adapt each biome design · Leave it parked

## What the card said

<!-- answered 2026-11-28T05:58:14Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

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
