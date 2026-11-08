"""place.py -- climbing_gear_reads_as_kit: write the climbing gear's ground sprite and worn pack facings (pass 3's codex art of
one rope, grappling hook and claw kit, judged and wired by pass 4) from art_source/installed4 into Textures/.
python3 place.py   (from the repo root; prefer art.py install --file, which records the ledger event)"""
import shutil
from pathlib import Path

MOD = Path(__file__).resolve().parents[2]
SRC = MOD / "art_source" / "installed4"
T = MOD / "Textures"
for name, rel in (("RM_ClimbingGear.png", "Things/Item/FlowWorks/RM_ClimbingGear.png"),
                  ("RM_ClimbingGear_south.png", "Things/Pawn/Humanlike/Apparel/FlowWorks/RM_ClimbingGear/RM_ClimbingGear_south.png"),
                  ("RM_ClimbingGear_north.png", "Things/Pawn/Humanlike/Apparel/FlowWorks/RM_ClimbingGear/RM_ClimbingGear_north.png"),
                  ("RM_ClimbingGear_east.png", "Things/Pawn/Humanlike/Apparel/FlowWorks/RM_ClimbingGear/RM_ClimbingGear_east.png")):
    (T / rel).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SRC / name, T / rel)
    print(rel)
