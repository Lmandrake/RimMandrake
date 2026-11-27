When many helpers publish at once, a plain ./publish can sleep 20+ minutes on its retry loop and the harness moves it to the background and cuts it at 10 more minutes; run ./publish under 'waitalive.py run --name <n> -- ./publish ...' (55-minute wait) from the start. Measured 2026-11-26: batch 2a of CANON_DRAIN_1 took about 28 minutes to land.
item: CANON_DRAIN_1
home: skills/clone-landing-commits
