A test-site repaint with jawa/set_terrain_batch and no clearOverlays=True does not read back on any cell where an earlier chain left floodwater, ice (tempGrid) or Substructure (foundation), because TerrainAt reads those before the top grid; a staging guard then refuses the whole chain at setup. Pass clearOverlays=True in every site prep (FlowWorks _prep_plot missed it until bcdf14415c; testq J20261127T102417Z-b7c73d).
item: HARNESS_REPAIR_CAUSE_AC81755A_4
home: skills/rimbridge/SKILL.md
