import sys, json
sys.path.insert(0, r"\\wsl.localhost\Ubuntu\home\mandrake\rm\relentless\clones\RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_VISIT_TWO.det\src\RimMandrake\Utils")
import validation_core as V
B = V.Bridge()
tool = sys.argv[1]; args = json.loads(sys.argv[2])
print(json.dumps(B.call(tool, **args))[:int(sys.argv[3]) if len(sys.argv) > 3 else 3000])
