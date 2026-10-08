import sys, os
root=os.getcwd()
U=os.path.join(root,"src","RimMandrake","Utils")
for p in (U, os.path.join(U,"modcheck")): sys.path.insert(0,p)
import runner
print(runner.ensure_playing_map())
