"""Shared Codex runtime selection. Explicit switch > RM_CODEX_SIDE > host default."""
import os
import platform


def in_wsl():
    return "microsoft" in platform.release().lower()


def codex_side(override=None):
    side = override or os.environ.get("RM_CODEX_SIDE")
    if side is None:
        side = "wsl" if in_wsl() and platform.node().lower() == "archmagi" else "win"
    if side not in ("wsl", "win"):
        raise ValueError("RM_CODEX_SIDE must be wsl or win (got %r)" % side)
    return side


def main(argv=None):
    """Shell callers supply Linux paths; translate only path-valued exec options."""
    import argparse
    import subprocess
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    parser.add_argument("--codex", choices=("wsl", "win"))
    selected, args = parser.parse_known_args(sys.argv[1:] if argv is None else argv)
    if selected.codex:
        os.environ["RM_CODEX_SIDE"] = selected.codex
    import dispatch_door
    door = dispatch_door.load()
    runtime = "linux" if codex_side() == "wsl" else "windows"
    home = door.default_home(runtime)
    if runtime == "windows":
        ok, why = door.windows_sandbox_ready(home)
        if ok is not True:                  # a launch would raise the Windows sandbox-setup dialog
            print("codex_side: refusing to launch codex.exe: %s" % why, file=sys.stderr)
            return 22
    path_flags = ("-C", "--cd", "-o", "--output-last-message", "--output-schema", "--add-dir")
    images = False
    path_next = False
    for i, arg in enumerate(args):
        if arg == "--":
            break
        if path_next or (images and not arg.startswith("-")):
            args[i] = door.codex_path(runtime, Path(arg))
            path_next = False
        else:
            images = arg in ("-i", "--image")
            path_next = arg in path_flags
    return subprocess.run([str(door.find_codex(runtime)), *args],
                          env=door.child_env(runtime, home),
                          timeout=8 * 3600).returncode  # an interactive session, bounded to a working day


if __name__ == "__main__":
    raise SystemExit(main())
