"""Copy the round-6 shots (stamp args) from the game's Screenshots folder into Transient/r6shots. python.exe ralph/live/r6_collect.py STAMP..."""
import glob, os, shutil, sys
src = r"D:\ClaudeWork\rimmandrake\instances\b\Screenshots"
dst = os.path.join(os.getcwd(), "Transient", "r6shots"); os.makedirs(dst, exist_ok=True)
n = 0
for st in sys.argv[1:]:
    for f in glob.glob(os.path.join(src, "*_%s__*" % st)) + glob.glob(os.path.join(src, "*_%s.png" % st)):
        shutil.copy(f, dst); n += 1
print("copied", n, "to", dst)
