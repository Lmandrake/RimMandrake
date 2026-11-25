A rimflow close --publish run from a helper clone on SteveDesktop printed PUBLISHED <sha> and the commit is on origin/main, yet the clone's HEAD stayed one commit behind with the same ledger lines left as a working-tree diff. The next git pull then refuses. Check git status after a --publish write; if the diff equals lines already on origin/main, git checkout the shard and pull.
item: BELT_WATER_HARNESS_1
home: skills/using-rimflow/references/traps.md
