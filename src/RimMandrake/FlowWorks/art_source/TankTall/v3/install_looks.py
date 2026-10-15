"""TANK_TALL_BUILD_TWICE_THE_DRINK v3 install: the 16 kept tank looks (v3/<Look>/<Tank>.png) into
Textures/RimMandrake/FlowWorks/Tank/<Look>/<Tank>.png through the art ledger, on the owner's words; then retire the old
single-look tank art under Things/Building/FlowWorks/ (the tanks' base texPath now reads the Scrapper look).
Ran once 2026-10-15; re-running reports already-live / absent. usage: install_looks.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FW = HERE.parents[2]
sys.path.insert(0, str(FW.parent / "Utils" / "art"))
import artledger as L  # noqa: E402

SAID = ("I like the new ones much better. They should have the same four variant styles as Gimme Some Slack. "
        "And yes regen the short ones too to match.")
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
TANKS = ["RM_LiquidTank", "RM_LiquidTankTall", "RM_UniversalCargoTank", "RM_UniversalCargoTankXTall"]
OLD = [f"Things/Building/FlowWorks/{t}.png" for t in TANKS] + ["Things/Building/FlowWorks/Machinery/RM_UniversalCargoTank.png"]

for look in LOOKS:
    for tank in TANKS:
        (FW / "Textures" / "RimMandrake" / "FlowWorks" / "Tank" / look).mkdir(parents=True, exist_ok=True)
        sha = L.store_put_bytes((HERE / look / f"{tank}.png").read_bytes())
        r = L.install("src/RimMandrake/FlowWorks", f"RimMandrake/FlowWorks/Tank/{look}/{tank}.png", sha, owner_said=SAID)
        print(look, tank, r["status"])
for rel in OLD:
    print(rel, L.retire(FW / "Textures" / rel, owner_said=SAID)["status"])
