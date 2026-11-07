# Questions for the owner

**Anima, polux and harbinger trees don't appear on Pyrelands maps.** The north star says no wild plant other than ember
grass, quick grass and scorch-fruit grows there, and these trees are placed by name, so the plant allowlist never sees
them. I blocked their map-generation steps and their spawn incidents, plus the ambrosia, gauranlen and boomshroom
sprouts. The cost: a psycaster colony landing here has no anima tree and has to go elsewhere for one. I recommend
keeping it this way, because the fire biome reads cleaner and its bar is explicit. If you want the anima tree back, delete
`AnimaTrees` from `preventGenSteps` in `Defs/BiomeDefs/Pyrelands.xml` and `AnimaTreeSpawn` from
`Patches/RM_Pyrelands_NoForeignArrivals.xml`.

**Pyrelands grass still bursts, but gently.** You ruled by card "Let Pyrelands grass burst too". Live, that made 11,039 stacks of hay in three days on a carpet this dense, counted as 44,000 of colony wealth (raids scale on it), and bursts bruised colonists crossing the grass until they went down. I kept the burst (it pops and sows sprouts, one in three as you ruled) and removed its hay, filth, blow to pawns and message, for these two grasses only (`gentleBurst` in `RM_ExplosiveGrowthRoster.xml`). The cost: hay no longer falls as free fuel on this biome. I recommend keeping it. Delete the flag to get the old behaviour back.

**Scorch-fruit pods no longer burst on their own.** The Tinder top popped each pod within hours, so none stood to be harvested, which the north star requires. They now stand until they rot (`noCycle` on the row). The Tinder top still fires when forced, so its proofs hold, but it no longer happens in ordinary play. I recommend keeping it: the north star's line beats the roster's.
