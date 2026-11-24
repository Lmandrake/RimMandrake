# RIMMANDRAKE_ROUTE_PYRE_TESTQ_OFF_STEVE_NO_SITE_THERE

## spec

Pyrelands test jobs on the SteveDesktop lane measure nothing. Since 2026-11-19, 5 Pyrelands testq jobs ran there (4
requested by `BENCH.filler`, purpose guard canaries; 1 by BENCH) and 0 had a PASS row [measured from
`D:\ClaudeWork\rimmandrake\testq\done\`, 2026-11-22]. Each spends about 20 min of SteveDesktop (deploy 297 s, run 716 s in
J20261122T172224Z-ccc309) and ends UNMEASURED SITE: "could not make a Pyrelands site current (tried map 1, read
'RM_TheRot')", plus a stale-load bounce (mandrake.rm.weathersuite, mandrake.rut.patches, mandrake.rsw.swbestiary,
mandrake.rm.patches not loaded). Testq ingest files each sighting as a harness fault. The in-game visits do not use the
lane (visit 5: "SteveDesktop was not used ... no Pyrelands site there").

Merged by the ticket sweep of 2026-11-22 (RIMMANDRAKE_SWEEP_PYRELANDS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE) from:
RIMMANDRAKE_LOAD_PYRELANDS_SITE_IN_TESTQ_CHAINS_RAN_BOREAL (the offline half, `_on_site` loading the registered site,
landed ee595f31a7; the live half never read true), PYRELANDS_REBUILD_CALM3_DONORS_IN_HEADER (the registered site
NS_Pyrelands_site_1_417df172fdb5_calm3 names three retired donors in its header), HARNESS_REPAIR_CAUSE_AC81755A_2
(absent_from_sheet) and HARNESS_REPAIR_CAUSE_01DAD227 (site_hold) - four views of one cause: the lane has no loadable
Pyrelands site, and the filler keeps queuing the mod there.

Owed, builder's choice, say which: give the SteveDesktop lane a donor-free Pyrelands site that loads (rebuild the
registered site on the pyrelands tier and ship it to the lane, as the visits do on Archmagi), or make the filler skip a
mod whose registered site the lane cannot load, naming it once.

## Acceptance test

`python3 -c "import json,glob,sys,time; t=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time()-86400)); b=[f for f in glob.glob('/mnt/d/ClaudeWork/rimmandrake/testq/done/*.json') for d in [json.load(open(f))] if d.get('job',{}).get('mod')=='Pyrelands' and d['job'].get('lane')=='stevedesktop' and (d['job'].get('submitted') or '')>t and not ((d.get('result') or {}).get('counts') or {}).get('PASS')]; print(len(b),'Pyrelands SteveDesktop jobs with no PASS in 24 h'); sys.exit(bool(b))"`
exits 0 over a day after the fix. Watched red 2026-11-22 3:29 PM PST: 3 such jobs.
