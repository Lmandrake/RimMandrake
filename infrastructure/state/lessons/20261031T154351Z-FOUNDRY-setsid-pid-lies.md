setsid nohup cmd & then ps -p $! shows nothing even though the job is alive: setsid forks when it is a process-group leader, so $! is setsid's own pid. I took a live replay arm for dead and rm -rf'd its 6.2G clone under it. Check liveness with pgrep or launch with systemd-run --user --slice=rm-harness.slice (the Bash tool's cgroup also kills plain children).
home: git-efficiency
