"""Install RM_Vaalok north+east from their own finished artpipe renders (they were RM_Aurrok's bytes). South is queued (wsfix_RM_Vaalok_south_v2)."""
import sys
sys.path.insert(0, "/home/mandrake/rm/bench/src/RimMandrake/Utils/art")
import artledger as L
S = "/mnt/d/Luke/dev/_artpipe/_artsrc"
for f in ("north", "east"):
    print(L.install_file(f"src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Vaalok/RM_Vaalok_{f}.png",
        f"{S}/RM_Vaalok_{f}/RM_Vaalok_{f}.png", reason="script:Transient/biome_art_refresh_2026-10-07/wrong_subject_install.py"))
