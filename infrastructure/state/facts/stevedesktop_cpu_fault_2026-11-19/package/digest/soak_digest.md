# Prime95 soak digest (run S20261118T012929Z and the earlier lines of soak.log)

Steps in the 72 h run: 3978; FAIL steps: 3; steps per cpu (cpu=-1 is the all-core step): {'-1': 209, '0': 211, '1': 211, '2': 211, '3': 210, '4': 209, '5': 209, '6': 209, '7': 209, '8': 209, '9': 209, '10': 209, '11': 209, '12': 209, '13': 209, '14': 209, '15': 209, '16': 209, '17': 209}

vcore_v over steps: n=3978 mean=1.023 min=0.979 max=1.035

core_max_c over steps: n=3978 mean=43.885 min=37.000 max=57.000

## Every FAIL step, whole

2026-11-18T04:23:06Z pass=11 cpu=8 FAIL prime95_died_early fatal=0 whea=0 alive=0 load=2 heat=pkg_c=40/40 core_max_c=40 hot_core=9 cores_max_c=[31,34,37,36,37,31,34,31,40] samples=64 vcore_v=1.032
2026-11-18T19:54:00Z pass=71 cpu=6 FAIL prime95_died_early fatal=0 whea=0 alive=0 load=0 heat=pkg_c=36/39 core_max_c=40 hot_core=2 cores_max_c=[34,40,38,36,36,34,31,36,30] samples=38 vcore_v=1.027
2026-11-18T21:28:51Z pass=77 cpu=8 FAIL prime95_died_early fatal=0 whea=0 alive=0 load=0 heat=pkg_c=36/36 core_max_c=38 hot_core=2 cores_max_c=[32,38,37,36,34,32,33,32,34] samples=64 vcore_v=1.030

## Every non-step line of soak.log (START, END, CONTROL, REBOOT, WAIT, PASS_COMPLETE excluded below), whole

2026-11-17T18:51:36Z SOAK START hours=6 end=2026-11-18T00:51:35Z cpus=18 core_secs=45 all_secs=90 max_c=90
2026-11-17T18:51:36Z SOAK END steps=0 passes_started=1 reason=
2026-11-17T18:51:58Z SOAK START hours=6 end=2026-11-18T00:51:58Z cpus=18 core_secs=45 all_secs=90 max_c=90
2026-11-17T19:17:06Z SOAK END steps=32 passes_started=2 reason=YIELD: STOP file
2026-11-18T01:29:29Z SOAK PLAN run=S20261118T012929Z hours=72 end=2026-11-21T01:29:29Z
2026-11-18T01:29:32Z SOAK START run=S20261118T012929Z hours=72 end=2026-11-21T01:29:29Z cpus=18 core_secs=45 all_secs=90 max_c=90 max_fails=50 boot=2026-11-17T19:51:20Z
2026-11-18T01:29:32Z PROBES run=S20261118T012929Z worker_probe=blind rimworld=0 whoami=nt authority\system
2026-11-18T01:30:00Z CONTROL run=S20261118T012929Z inject_fatal_seen=1 inject_died_seen=1 heat_seen=1 load_seen=1 load=100 ok=1
2026-11-18T01:30:00Z SOAK INTERRUPTED run=S20261118T012929Z steps=0 passes_started=1 (script exited without a reason; the next boot or task start resumes)
2026-11-18T01:31:02Z SOAK RESTART run=S20261118T012929Z same_boot=2026-11-17T19:51:20Z end=2026-11-21T01:29:29Z
2026-11-18T01:31:02Z PROBES run=S20261118T012929Z worker_probe=blind rimworld=0 whoami=nt authority\system
2026-11-18T01:31:29Z CONTROL run=S20261118T012929Z inject_fatal_seen=1 inject_died_seen=1 heat_seen=1 load_seen=1 load=100 ok=1
2026-11-18T01:40:13Z SOAK REBOOT run=S20261118T012929Z boot=2026-11-18T01:39:36Z prev_boot=2026-11-17T19:51:20Z
2026-11-18T01:40:13Z SOAK RESUME run=S20261118T012929Z end=2026-11-21T01:29:29Z cpus=18
2026-11-18T01:40:13Z PROBES run=S20261118T012929Z worker_probe=blind rimworld=0 whoami=nt authority\system
2026-11-18T01:40:41Z CONTROL run=S20261118T012929Z inject_fatal_seen=1 inject_died_seen=1 heat_seen=1 load_seen=1 load=98 ok=1
