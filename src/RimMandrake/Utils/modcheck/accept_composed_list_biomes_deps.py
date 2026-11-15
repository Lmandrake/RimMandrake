"""Acceptance test for RIMMANDRAKE_COMPOSE_BIOMES_DEPS_INTO_MODCHECK_PIGMENT_LEFT_OUT.

modcheck run() composes a folded biome's list from the SOURCE mod's About deps, so the deployed Baroque Biomes' hard
dependency mandrake.rm.luminouspigment is missing and a keep-less run reads "loaded but not composed" on a correct load.
Base 2026-11-15 (f604a6de8e): exit 1, Webwork FAIL + Cauldron FAIL. Correct: exit 0, 2 PASS.
    python3 src/RimMandrake/Utils/modcheck/accept_composed_list_biomes_deps.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import runner as R
ok = 0
for m in ("Webwork", "Cauldron"):
    d = R.find_mod_dir(m); folded = R.composed_into(m); ids = []
    ids.extend(x for x in R.mod_dependency_ids(d) if x not in ids)
    own = folded[1] if folded else R.mod_package_id(d)
    ids.append(own); ids.extend(t for t in R.closure_ids(m, folded) if t not in ids)
    ids = R.with_own_dependencies(ids)
    good = "mandrake.rm.luminouspigment" in ids
    print(m, "PASS" if good else "FAIL", ids); ok += good
sys.exit(0 if ok == 2 else 1)
