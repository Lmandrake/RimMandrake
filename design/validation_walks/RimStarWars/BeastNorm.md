# BeastNorm — validation walk
subject: src/RimStarWars/BeastNorm  (packageId mandrake.rsw.beastnorm)
deps: mlie.starwarsanimalcollection (Star Wars Animal Collection (Continued))
list: minimal+mlie.starwarsanimalcollection
status-hint: patches best-hit melee tool power/cooldown on 105 SW beasts (bs>=1) to scale with bodySize (power=15*bs, DPS=10*sqrt(bs)), and raises manhunterOnDamageChance/manhunterOnTameFailChance on big herbivores (bs>=1.5, no carnivore tag) so docility reads as "provoked", not passive.

## must be true
- Every PatchOperationConditional in BeastNorm_Law3.xml is keyed to a real donor defName from mlie.starwarsanimalcollection and no-ops (never errors) if that beast is renamed or removed upstream.
- Dewback's best tool (tools/li[2]) power=45.0, cooldownTime=2.6 (bodySize 3.0: 15*3=45, DPS 10*sqrt(3)=17.31 matches manifest).
- Rancor's best tool (tools/li[3]) power=90.0, cooldownTime=3.67 (bodySize 6.0).
- Bantha (a raised-revenge herbivore) gets both its horns tool retuned AND manhunterOnDamageChance raised 0.35→0.9, manhunterOnTameFailChance 0.05→0.4.
- Beasts under bodySize 1 (55 of them) are untouched — this mod's own manifest excludes them, not a runtime gate.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rsw.beastnorm" and no XML error naming BeastNorm_Law3.xml   # load-time
2. [D] def read-back: ThingDef Dewback/tools/li[2]/power=45.0, cooldownTime=2.6
3. [D] def read-back: ThingDef Rancor/tools/li[3]/power=90.0, cooldownTime=3.67
4. [D] def read-back: ThingDef Bantha/tools/li[1]/power=60.0, cooldownTime=3.0; race/manhunterOnDamageChance=0.9; race/manhunterOnTameFailChance=0.4
5. [B] jawa/get_def {defName: "Dewback"} → statBases/comps confirm power=45.0 resolved post-patch (not just the raw XML), same for Rancor and Bantha
6. [B] jawa/spawn_batch {ops: "Dewback:X,Z"} then jawa/damage on the spawned Dewback with a Blunt hit → single-hit outcome is bimodal (badly hurt or dies), matching the K=15 calibration claim in About.xml, not a guaranteed no-op scratch
7. [S] (human pass) none — this mod is stat-only, no new art or scenes
