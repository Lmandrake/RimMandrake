# RIMMANDRAKE_ADMIT_DIRECT_SUN_WITH_TREE_AND_MOUNTAIN_SHADE

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

<!-- answered 2026-11-28T10:31:46Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** Direct Sun is the sun-and-shade mod. Its Designer needs one root sentence: the picture of play that every later design choice must serve. The proposed root: "On a world whose sun stands still, Direct Sun makes the sun a thing the player plans around on every sunlit map. The sun's heat a colonist feels follows the sun's height, dimmed only by cloud: a high sun burns hard and leaves shade only under cover and tree crowns; a low sun burns gently and throws long shadows. Everything solid casts shade by one geometry: a roof, a tent or a parasol covers its ground, a wall or a rock throws a short lee, a tree's crown shades the ground under it and down-sun of it, and a mountain throws a long shadow out over the open ground that shows its bulk and grows as the sun drops. Colonists and animals live by it: a forest is mostly shade and its clearings sunlit, animals dash across hot ground from shade to shade, and the lee of a mountain is a refuge from the sun. The player sees where the shade lies and what casts it, the shade overlay shows the shade a colonist feels, and no biome changes the rule." The Designer's doubt: near the edge of the day side the sun stands about 5 degrees high, so each unit of height throws about 11 squares of shade. A mountain or a forest may then shade most of the open ground there, so 'plans around on every sunlit map' may be false on those maps. Mountain shade is also not designed or built yet. (Hard to read? Type STE, Binding or Both for a rewrite.) Which root do you want?
**His words:** Soften every sunlit map but also add language that planning for unwanted mountain shade is a major concern too.
**Other options:** Soften 'every sunlit map' (Recommended) · Accept as written · Root without mountains for now · Limit how long a shadow gets

**Question:** Direct Sun, second question. A mountain will throw a long shadow that colonists feel. The game itself draws a rock's shadow only about one square long. The only long drawn shadow we have is the trial on one giant tree (the greatbole crown shadow), staged for your look on the small Archmagi game as the save CROWN_SHADOW_GREATBOLE_REVIEW; you have not ruled on that trial yet. The shade overlay is the map view that colours each square by the shade a colonist feels there. How should the player see a mountain's long shadow?
**Picked:** Draw a soft dark band on the ground
**Its description:** Why: the player should see the shade without opening the overlay. Buys a map that reads at a glance. Costs: the same drawing work as the tree shadow at a larger scale, and it commits before you have judged the tree trial.
**Other options:** Overlay now, decide after the tree look (Recommended) · Overlay and square readout only
