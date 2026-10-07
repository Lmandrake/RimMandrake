"""Container recipes per material + stone bottle reads 'glass'. python.exe, cwd = repo root."""
import sys, os, json, time
REPO = os.getcwd()
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack"))
import validation_aerial as VA  # noqa: E402
B = VA.A()
R = ["RM_Make_Bottle_Leather", "RM_Make_Bottle_Glass", "RM_Make_Bottle_Metal", "RM_Make_Barrel_Wood", "RM_Make_Barrel_Metal",
     "RM_Make_Barrel_Plasteel", "RM_Make_Bucket_Wood", "RM_Make_Bucket_Metal", "RM_Make_Bucket_Leather"]
out = {}
out["recipes"] = B.call("jawa/get_defs", defs=";".join("RecipeDef/" + r for r in R), fields="recipeUsers,products,fixedIngredientFilter,defaultIngredientFilter")
benches = ["CraftingSpot", "HandTailoringBench", "TableStonecutter", "ElectricSmelter", "FueledSmithy", "ElectricSmithy", "TableMachining", "FabricationBench"]
out["benches"] = B.call("jawa/get_defs", defs=";".join("ThingDef/" + b for b in benches), fields="AllRecipes")
# one of each container x material, spawned with its stuff, labels read back
X, Z = 150, 60
B.call("jawa/destroy_batch", rects="%d,%d,12,6" % (X, Z), categories="All")
B.call("jawa/set_fog", action="unfog", rect="%d,%d,12,6" % (X, Z))
combos = [("RM_BottleEmpty", "Leather_Plain"), ("RM_BottleEmpty", "BlocksGranite"), ("RM_BottleEmpty", "Steel"),
          ("RM_BarrelEmpty", "WoodLog"), ("RM_BarrelEmpty", "Steel"), ("RM_BarrelEmpty", "Plasteel"),
          ("RM_BucketEmpty", "WoodLog"), ("RM_BucketEmpty", "Steel"), ("RM_BucketEmpty", "Leather_Plain")]
out["spawned"] = []
for i, (d, s) in enumerate(combos):
    x, z = X + (i % 5) * 2, Z + (i // 5) * 2
    r = B.call("jawa/spawn_batch", ops="%s:%d,%d" % (d, x, z), stuff=s)
    lt = B.call("jawa/list_things", defName=d, rect="%d,%d,1,1" % (x, z), limit=3)
    th = (lt.get("things") or [{}])[0]
    out["spawned"].append({"def": d, "stuff": s, "spawn": r.get("message") or r.get("success"), "thing": {k: th.get(k) for k in ("label", "labelCap", "stuff", "id", "def")}})
B.call("jawa/clear_ui", all=True)
B.call("rimworld/frame_cell_rect", x=X - 1, z=Z - 1, width=12, height=6, paddingCells=1)
time.sleep(2.5)
r = B.call("jawa/take_screenshot", fileName="containers_per_material")
p = os.path.join(REPO, "Transient", "kinetic_gss_live_2026-10-07", "containers_%s.json" % time.strftime("%H%M%S"))
out["shot"] = r.get("filePath")
open(p, "w").write(json.dumps(out, indent=1, default=str))
print(json.dumps(out["spawned"], default=str)); print("shot", out["shot"]); print("->", p)
