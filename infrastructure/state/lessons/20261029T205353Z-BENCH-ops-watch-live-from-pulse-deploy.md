The live ops_watch timer runs from D:\ClaudeWork\rimmandrake\pulse-deploy, not a seat clone: a new collector is live only once that tree has the published commit. Check it with git -C .../pulse-deploy log -1 before calling an ops_watch change live.
home: src/RimMandrake/Utils/ops_watch.py
