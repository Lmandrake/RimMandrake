# Wrapper: python.exe lacks fcntl, so run()'s subprocess swap/deploy/restore cannot run on Windows python.
# Swap/deploy/compose are done beforehand from WSL; restore afterwards from WSL.
import sys, os, runpy, subprocess
sys.path.insert(0, "src/RimMandrake/Utils/modcheck"); sys.path.insert(0, "src/RimMandrake/Utils")
import runner
runner.swap_to_test_list = lambda package_ids=(): None
runner.restore_full = lambda: None
runner.compose_test_list = lambda *a, **k: None
import json, time
runner.emit_verify = lambda *a, **k: None
_ff = []
runner.file_findings = lambda item, mod, f: _ff.append(f)
_rs = runner.run_suite
def _rs2(suite, s, **k):
    out = _rs(suite, s, **k)
    try:
        json.dump(out, open("Transient/modcheck/%s_situational_summary.json" % k.get("mod"), "w"), indent=1, default=str)
    except Exception as e:
        print("summary dump failed", e)
    return out
runner.run_suite = _rs2
_real = subprocess.run
def _run(cmd, *a, **k):
    if isinstance(cmd, list) and any("deploy_custom_mods" in str(c) for c in cmd):
        return subprocess.CompletedProcess(cmd, 0, "skipped", "")
    return _real(cmd, *a, **k)
subprocess.run = _run
sys.argv = ["cli.py"] + sys.argv[1:]
runpy.run_path("src/RimMandrake/Utils/modcheck/cli.py", run_name="__main__")
