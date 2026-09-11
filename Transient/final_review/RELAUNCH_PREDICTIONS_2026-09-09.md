# Deciding strings for the overnight relaunch (written BEFORE launch)
1. Companion: census via prove_new_tools.py --census must match the deployed DLL
   (build 97d0d123ae61 + ordered_job playerForced fix). LIES: an old count means
   deploy didn't take, not a missing tool.
2. ordered_job Refuel on a ChemfuelTank with fuel item: afterJobDef == "Refuel"
   and fuel level rises (was: instant fail via JobDriver_Refuel.cs:34).
3. UtinniPatches BiomeNames: world tile inspector shows "the Greentide" not
   "Cypre Jungle" after loading EXPERIMENTAL_shipcrewed.
4. allowRoads patch: cap asphalt — world screen at the antistellar cap shows road
   lines (34 tiles) that were invisible before.
5. Player.log: zero NEW "^Config error in" lines vs the pre-restart baseline
   (grep both, diff counts).
