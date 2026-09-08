import sys, json
sys.path.insert(0, "/mnt/d/Luke/dev/Rimworld/src/RimMandrake/Utils")
from rimplace.core import Palette, Rect
from rimplace.luaenv import run_template
from rimplace.plan import compile_calls
from pathlib import Path

REPO = Path("/mnt/d/Luke/dev/Rimworld")
TEMPLATES = REPO / "design" / "Jawa" / "templates"
PALETTE = json.loads((REPO / "src" / "RimMandrake" / "Utils" / "rimplace" / "palette.json").read_text(encoding="utf-8"))

SITES = [
    ("waste_camp", Rect(75, 30, 20, 20)),
    ("boneyard", Rect(120, 75, 24, 24)),
    ("long_crossing", Rect(160, 30, 20, 16)),
]

params = {
    "faction": "none", "rooms": 0, "occupants": 0, "wealth": "modest",
    "techLevel": "Industrial", "defended": "none", "condition": "ruined",
    "climate": "auto", "temperature_c": 43.0, "seed": 7,
}

out = {}
for name, rect in SITES:
    path = TEMPLATES / f"{name}.lua"
    palette = Palette(PALETTE, params["faction"], params["techLevel"], params["wealth"])
    plan = run_template(path, rect, params, palette, params["seed"])
    calls = compile_calls(plan, faction=None, dry_run=False)
    out[name] = {"rect": [rect.x, rect.z, rect.w, rect.h], "calls": calls, "notes": plan.notes}
    print(name, "->", len(calls), "calls,", len(plan.notes), "notes")

Path("/mnt/d/Luke/dev/Rimworld/Transient/desert_build_calls.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print("wrote Transient/desert_build_calls.json")
