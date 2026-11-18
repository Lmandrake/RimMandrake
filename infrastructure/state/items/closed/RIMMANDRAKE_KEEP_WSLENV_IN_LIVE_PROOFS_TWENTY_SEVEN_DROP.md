## spec
27 files in infrastructure/state/live_proofs/ set `WSLENV=<names>` on a `live-proof` line, which REPLACES the inherited
WSLENV. On SteveDesktop the worker's WSLENV carries `RM_DATA_ROOT/p`; once it is replaced, Windows `python.exe` has no
RM_DATA_ROOT, and the bridge client dies in `ensure_playing_map` with `RmDataRootUnset` after 240 s. Every clause then
reads UNMEASURED (or FAIL on a traceback). Measured on the three RIMMANDRAKE_PROVE_FLOWWORKS_TOGGLES_DENSE jobs
J20261113T054922Z-25284e, J20261113T054923Z-701934, J20261113T054923Z-b7c13e (proof_A*.log on Steve). That file was fixed
in fd568d495b by appending: `WSLENV=${WSLENV:+$WSLENV:}NAMES`.

Fix: either rewrite the 27 lines the same way, or make the worker immune (run_proofs re-exports RM_DATA_ROOT/p into
WSLENV after the line's own assignments, or translates a bare `WSLENV=` assignment into an append) and add a lint that
refuses a bare `WSLENV=` in a live-proof line.

## acceptance
Acceptance test: `python3 - <<'X'
import glob,re,sys
bad=[f for f in glob.glob('infrastructure/state/live_proofs/*.txt') for l in open(f) if l.startswith('live-proof') and re.search(r'(^|\s)WSLENV=(?!\$\{?WSLENV)', l)]
print(len(set(bad)), 'files'); sys.exit(1 if bad else 0)
X` exits 0. It exits 1 with "27 files" at fd568d495b (watched). Expected after the fix: "0 files". If the worker-side route is
taken instead, its selftest must show a proof line with a bare `WSLENV=X` still passing RM_DATA_ROOT to the child.
