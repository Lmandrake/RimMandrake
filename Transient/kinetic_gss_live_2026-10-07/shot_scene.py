"""Stage one KA/EK scene, step N ticks, screenshot it. python.exe, cwd = repo root.
usage: shot_scene.py <proofType KA|EK> <scene> <x> <z> <ticks> <name>"""
import sys, time, os, shutil, json
REPO = os.getcwd()
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack"))
import validation_aerial as VA  # noqa: E402
T = {"KA": "RimMandrake.KineticArms.RM_KineticArmsProof", "EK": "RimMandrake.ExplosiveKnockback.RM_KnockbackProof"}
B = VA.A()
typ, scene, x, z, ticks, name = T[sys.argv[1]], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
print(B.call("jawa/static_call", type=typ, method="Stage", args="%s,%d,%d" % (scene, x, z)).get("result"))
B.call("rimworld/step_game_ticks", ticks=ticks, pauseFirst=True, timeoutMs=120000)
print(B.call("jawa/static_call", type=typ, method="Verdict", args=scene).get("result"))
B.call("jawa/clear_ui", all=True)
B.call("rimworld/frame_cell_rect", x=x - 8, z=z - 6, width=18, height=13, paddingCells=1)
time.sleep(2.5)
r = B.call("jawa/take_screenshot", fileName=name)
src = r.get("filePath")
for _ in range(20):
    if src and os.path.exists(src):
        break
    time.sleep(0.5)
dst = os.path.join(REPO, "Transient", "kinetic_gss_live_2026-10-07", name + ".png")
shutil.copyfile(src, dst)
print("->", dst)
