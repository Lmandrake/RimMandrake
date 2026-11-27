A capacity check that sizes the next unit by the units present now breaks when the mix changes: SteveDesktop's room check sized a new helper clone by the pool's clones, so an empty pool read COULD_NOT_LOOK and a pool holding one full warm spare read SHORT (5.1 GB per clone where a new one is 1.5 GB). Size the next unit from its source (here a git ls-tree of the store's HEAD), and keep the present units as a measurement only.
item: RIMMANDRAKE_SHRINK_STEVEDESKTOP_CLONES_FOUR_FILL_ITS_EIGHTY_GIG
home: infrastructure/stevedesktop/RUNBOOK.md
