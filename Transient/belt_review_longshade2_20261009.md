# LongShade second pass 2026-10-09

Full-file reads, zero significant findings, no source edits (no rebuild needed):
RM_ShadeExtras.cs, RM_LongShadeMapgen.cs, RM_Patch_DewfringeWildSpawnGate.cs, RM_ShipfallCommons.cs, Kernel/RM_LongShadeKernel.cs, SelfTest/LongShadeFuzz.cs, SelfTest/Program.cs (SelfTest is the offline fuzz csproj, not in RM_LongShade.csproj; reachable via selftest_longshade_fuzz.py).
Checked: tickers (awning Rare now has tickerType), Scribe symmetry (stampede runnersSave, hull, commons rebuilt not saved), list mutation (tow copies list, prune collects then removes), spawn-before-find (road wrecks, graves, terminus marker finally-destroyed), index math (road k>=1), null guards.
Nits, not changed: Dewfringe wrapper comment says gate degrades to never-restrict when grid absent, but OnRim returns false (no dewfringe) in that case; LongShadeFuzz.cs:441 has a vacuous `|| true` Check (line 442 is the real assert); fuzz header omits the extras family.
No dotnet in WSL: fuzz not run.
