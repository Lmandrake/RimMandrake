"""Windows heartbeat: stale commits and a failed WSL write each alert once (DryRun), green recovers, pause mutes.
Todoist is retired as an alert route (owner, 2026-11-19): a red run without -TodoistAlarmPosts attempts no HTTP call to
Todoist (Invoke-RestMethod is stubbed and records every call), and the same stub does see the post when the switch is on."""
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
    for on in (False, True):
        sd = d / ("on" if on else "off")
        sd.mkdir()
        (sd / "todoist_token").write_text("not-a-real-token")
        sdw = subprocess.check_output(["wslpath", "-w", str(sd)], text=True).strip()
        callsw = sdw + "\\calls.txt"
        cmd = ("function global:Invoke-RestMethod { Add-Content -LiteralPath '%s' -Value ($args -join ' ') }; "
               "& '%s' -StateDir '%s' -FakeCommitAgeMinutes 500 -StaleMinutes 1 -FakeWslFail%s"
               % (callsw, HB, sdw, " -TodoistAlarmPosts" if on else ""))
        subprocess.run([PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd], check=True,
                       capture_output=True, timeout=240)
        calls = (sd / "calls.txt").read_text() if (sd / "calls.txt").exists() else ""
        hlog = (sd / "heartbeat.log").read_text()
        if on:
            assert calls.count("api.todoist.com") == 2, "the stub must see the post when the switch is on: %r" % calls
        else:
            assert "todoist" not in calls.lower(), "Todoist retired, yet an HTTP call was attempted: %r" % calls
            assert hlog.count("todoist posting off") == 2, hlog
finally:
    shutil.rmtree(d, ignore_errors=True)
print("selftest_heartbeat OK")
