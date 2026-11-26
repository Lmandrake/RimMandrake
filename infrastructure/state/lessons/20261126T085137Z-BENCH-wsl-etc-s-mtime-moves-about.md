On WSL, /etc's mtime moves about every 200 s because WSL rewrites the /etc/resolv.conf link (measured 2026-11-26 on SteveDesktop). Any 'folder changed since the run began' guard over /etc fires on that churn: known_results refused 46 of 433 records for it until CHURN exempted resolv.conf. A guard that reads a system folder's mtime must name that folder's own churn.
item: RIMMANDRAKE_KEY_TESTQ_SKIP_CACHE_ON_INPUTS
home: infrastructure/state/facts/instrument_traps.md
