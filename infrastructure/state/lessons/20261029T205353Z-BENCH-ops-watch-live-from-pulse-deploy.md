The live ops_watch timer, like every Operations clock, runs from the one Operations deploy, /home/mandrake/rm/dispatch (src/RimMandrake/Utils/systemd/ops_clocks.json), not a seat clone: a new collector is live only once that tree has the published commit. Check it with git -C /home/mandrake/rm/dispatch log -1 before calling an ops_watch change live.
home: src/RimMandrake/Utils/ops_watch.py
