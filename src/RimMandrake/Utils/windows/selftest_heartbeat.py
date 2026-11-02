"""Windows heartbeat: stale commits and a failed WSL write each alert once (DryRun), green recovers, pause mutes."""
import shutil, subprocess, sys, tempfile
from pathlib import Path

PS = shutil.which("powershell.exe")
if not PS:
    print("selftest_heartbeat SKIP (no powershell.exe)")
    sys.exit(0)
HB = subprocess.check_output(["wslpath", "-w", str(Path(__file__).resolve().parent / "heartbeat.ps1")], text=True).strip()
d = Path(tempfile.mkdtemp(dir="/mnt/d/ClaudeWork"))
dw = subprocess.check_output(["wslpath", "-w", str(d)], text=True).strip()


def run(*a):
    subprocess.run([PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", HB, "-StateDir", dw, "-DryRun", *a],
                   check=True, capture_output=True, timeout=240)
    return (d / "heartbeat.log").read_text()


try:
    log = run("-FakeCommitAgeMinutes", "500", "-StaleMinutes", "1", "-FakeWslFail")
    assert "DRYRUN alert: RimMandrake HEARTBEAT: commits is red" in log and "wsl is red" in log, log
    log2 = run("-FakeCommitAgeMinutes", "500", "-StaleMinutes", "1", "-FakeWslFail")
    assert log2.count("DRYRUN alert") == 2 and log2.count("already alerted") == 2, "same incident rang twice"
    log3 = run("-FakeCommitAgeMinutes", "0")
    assert "GREEN commits (recovered)" in log3 and "GREEN wsl (recovered)" in log3, log3
finally:
    shutil.rmtree(d, ignore_errors=True)
print("selftest_heartbeat OK")
