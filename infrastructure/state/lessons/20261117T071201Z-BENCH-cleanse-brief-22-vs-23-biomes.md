The Designer Cleanse brief counts 22 biomes other than Pyrelands; design/Biomes.compose.json has 24 biome entries, 23 but Pyrelands. The fleet reads the compose file (fleet_order), so it runs 23. A count written into a brief goes stale; the brief should say 'every biome entry of Biomes.compose.json but Pyrelands'.
item: RIMMANDRAKE_UPGRADE_DESIGNER_CLEANSE_SIXTY_FOUR_BARS_LOCKED
home: src/RimMandrake/rimflow/roles/designer_cleanse.md
