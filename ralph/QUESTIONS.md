# Questions for the owner

**Anima, polux and harbinger trees don't appear on Pyrelands maps.** The north star says no wild plant other than ember
grass, quick grass and scorch-fruit grows there, and these trees are placed by name, so the plant allowlist never sees
them. I blocked their map-generation steps and their spawn incidents, plus the ambrosia, gauranlen and boomshroom
sprouts. The cost: a psycaster colony landing here has no anima tree and has to go elsewhere for one. I recommend
keeping it this way, because the fire biome reads cleaner and its bar is explicit. If you want the anima tree back, delete
`AnimaTrees` from `preventGenSteps` in `Defs/BiomeDefs/Pyrelands.xml` and `AnimaTreeSpawn` from
`Patches/RM_Pyrelands_NoForeignArrivals.xml`.
