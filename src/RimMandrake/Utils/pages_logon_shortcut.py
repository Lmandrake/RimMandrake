#!/usr/bin/env python3
"""pages_logon_shortcut.py: a Windows Startup shortcut that runs ./pages at logon (minimized, Chrome only).

    python3 pages_logon_shortcut.py [--repo DIR] [--dry-run] [--uninstall]
exit 0 done, 3 refused or failed. Promises: design/specs/2026-11-19-logon-tabs-shortcut/boundary.md.
"""
import os
import subprocess
import sys

NAME = "RimMandrake pages.lnk"
DEFAULT_REPO = "/home/mandrake/rm/bench"


def ps(script):
    r = subprocess.run(["powershell.exe", "-NoProfile", "-Command", script], capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout.replace("\r", "").strip(), r.stderr.strip()


def startup_dir():
    rc, out, err = ps("[Environment]::GetFolderPath('Startup')")
    if rc or not out:
        raise RuntimeError("could not read the Startup folder: %s" % err)
    return out


def plan(repo):
    """-> (target, arguments, window style)."""
    return "wsl.exe", "-e bash -c '%s/pages'" % repo, 7


def main(argv=None, runner=ps, startup=startup_dir):
    argv = sys.argv[1:] if argv is None else argv
    repo = argv[argv.index("--repo") + 1] if "--repo" in argv else DEFAULT_REPO
    dry, undo = "--dry-run" in argv, "--uninstall" in argv
    try:
        lnk = startup().rstrip("\\") + "\\" + NAME
    except (RuntimeError, OSError, subprocess.SubprocessError) as e:
        print(e)
        return 3
    if undo:
        if dry:
            print("would remove " + lnk)
            return 0
        rc, out, err = runner("if (Test-Path -LiteralPath '%s') { Remove-Item -LiteralPath '%s'; 'removed' } else { 'absent' }" % (lnk, lnk))
        print("%s: %s" % (out or "FAILED " + err, lnk))
        return 0 if rc == 0 else 3
    if not os.access(os.path.join(repo, "pages"), os.X_OK):
        print("no executable pages in %s; no shortcut written" % repo)
        return 3
    target, args, style = plan(repo)
    print("%s -> %s %s (window style %d)" % (lnk, target, args, style))
    if dry:
        return 0
    script = ("$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%s');$s.TargetPath='%s';$s.Arguments=\"%s\";"
              "$s.WindowStyle=%d;$s.Description='RimMandrake status tabs at logon';$s.Save()") % (
        lnk, target, args.replace('"', '`"'), style)
    rc, out, err = runner(script)
    if rc:
        print("FAILED: " + err)
        return 3
    print("installed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
