# BeastLairs — validation walk
subject: src/RimStarWars/BeastLairs  (packageId mandrake.rsw.beastlairs)
deps: none (Ludeon.RimWorld only)
list: minimal
status-hint: adds RSW_BeastNest_Large, a 3x3 non-buildable map-gen scatter prop (dressing for a lair, not a spawner) that scatters its own filth once on spawn via vanilla CompSpawnerFilth.

## must be true
- ThingDef RSW_BeastNest_Large exists, is a 3x3 non-rotatable Building, not player-buildable (no designationCategory) and not claimable.
- It carries CompProperties_SpawnerFilth (Filth_AnimalFilth, count 6, radius 3) and no pawn-spawning comp of any kind.
- Placing an instance on a live map fires the filth spawn once at PostSpawnSetup — dressing scatters itself, no player or lord action required.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rsw.beastlairs" and no XML error naming RSW_BeastLairs_Buildings.xml   # load-time
2. [D] def read-back: ThingDef RSW_BeastNest_Large exists; size=(3,3), rotatable=false, building/claimable=false, no designationCategory field, comps/li[@Class="CompProperties_SpawnerFilth"]/filthDef=Filth_AnimalFilth, spawnCountOnSpawn=6, spawnRadius=3
3. [B] jawa/spawn_batch {ops: "RSW_BeastNest_Large:X,Z"} on a dev quicktest map → returns success, one building placed
4. [B] jawa/list_things {defName: "Filth_AnimalFilth", rect: <3-tile radius around X,Z>} → 6 filth things present immediately after spawn (confirms CompSpawnerFilth fired once on placement, per struct spec — not a live spawner)
5. [S] (human pass) RSW_BeastNest_Large.png reads as a denned-in mound at 3x3 scale, not a flat scenery tile
