On SteveDesktop, Windows python.exe lacked tzdata, so tps_record.py's readers crashed (ZoneInfoNotFoundError) under the lane's python.exe rerun; fixed by python.exe -m pip install --user tzdata (2026-11-25). A new Windows python on a lane host needs it before any TPS proof.
item: BRIDGE_TPS_REVIEW2_FIXES_1
home: infrastructure/stevedesktop/RUNBOOK.md
