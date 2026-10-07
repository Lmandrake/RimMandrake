"""Build the minimal+mods+GimmeSomeSlack ModsConfig for modcheck mods (game must be DOWN). usage: foundry_l2_prep.py Mod [Mod...]"""
import os, subprocess, sys
sys.path.insert(0, "/home/mandrake/rm/foundry/src/RimMandrake/Utils")
sys.path.insert(0, "/home/mandrake/rm/foundry/src/RimMandrake/Utils/modcheck")
import runner as R
GSS = "mandrake.rm.gimmesomeslack"
runner_mods = sys.argv[1:]
R.swap_to_test_list()
ids = []
for m in runner_mods + ["GimmeSomeSlack"]:
    d = R.find_mod_dir(m)
    folded = R.composed_into(m)
    args = ("--compose", folded[0]) if folded else ("--mod", m)
    r = subprocess.run(R.py_cmd(os.path.join(R._UTILS, "deploy_custom_mods.py"), *args, "--apply"), cwd=R.ROOT, capture_output=True, text=True)
    print(m, "deploy rc", r.returncode, (r.stdout + r.stderr).strip()[-200:])
    if r.returncode: sys.exit(2)
    for x in R.mod_dependency_ids(d):
        if x not in ids: ids.append(x)
    own = folded[1] if folded else R.mod_package_id(d)
    if own not in ids: ids.append(own)
    if folded:
        for t in R.tier_package_ids(m):
            if t not in ids: ids.append(t)
if GSS not in ids: ids.append(GSS)
R.compose_test_list(ids)
print("composed", len(ids), ids)
