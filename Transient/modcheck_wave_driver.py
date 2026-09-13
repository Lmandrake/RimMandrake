import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils/modcheck")
sys.path.insert(0, "src/RimMandrake/Utils")
import runner

MODS = ["Pits","Inhabited","Ninefold","RimProperty","Aftermath","Antiquities",
        "FluidCanals","Graffiti","StructureInjections","Pyrelands",
        "ResearchRetag","ShipMemory","JawaIonWeapons","StarWarsRaces",
        "Droidworks","PawnFlavor"]
pairs = [(m, "MODCHECK_MATURE_WAVE_1") for m in MODS]
t0 = time.time()
try:
    results = runner.run(pairs, debug=False)
    print("\n==== WAVE COMPLETE in %.0fs ====" % (time.time() - t0))
    for m, s in results.items():
        n = sum(len(c["components"]) for c in s.get("chains", []))
        npass = sum(1 for c in s.get("chains", []) for comp in c["components"]
                    if str(comp.get("verdict","")).startswith("PASS"))
        print("%-22s %s  %d/%d components pass, %d findings"
              % (m, "GREEN" if s.get("all_green") else "RED",
                 npass, n, len(s.get("findings") or [])))
except Exception as e:
    print("\n==== WAVE ABORTED after %.0fs: %r ====" % (time.time() - t0, e))
    raise
