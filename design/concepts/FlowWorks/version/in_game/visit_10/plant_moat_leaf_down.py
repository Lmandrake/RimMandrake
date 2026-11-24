"""plant_moat_leaf_down.py --out X: sc_moat_walkers with a planted fault: the 'raised' stage keeps its leaf down, so the colonist
walks over the bridge (visit 10; the scene's MW_raised_leaf row and its drained row must FAIL)."""
import os, sys
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)
for p in ("src/RimMandrake/Utils", "src/RimMandrake/Utils/modcheck", "src/RimMandrake/FlowWorks/northstar"):
    sys.path.insert(0, os.path.join(R, *p.split("/")))
import concept_scenes as C
stage = C._moat_stage
C._moat_stage = lambda S, raised=True, raiders=True: stage(S, raised=False, raiders=raiders)
sys.argv += ['--scene', 'scene_moat_walkers']
sys.exit(C.main())
