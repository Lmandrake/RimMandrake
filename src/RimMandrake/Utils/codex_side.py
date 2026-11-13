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
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "skills/generating-images/scripts"))
    parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    parser.add_argument("--codex", choices=("wsl", "win"))
    selected, args = parser.parse_known_args(sys.argv[1:] if argv is None else argv)
    if selected.codex:
        os.environ["RM_CODEX_SIDE"] = selected.codex
    import codex_image as cx
    cx.select_codex(selected.codex)
    path_flags = ("-C", "--cd", "-o", "--output-last-message", "--output-schema", "--add-dir")
    images = False
    path_next = False
    for i, arg in enumerate(args):
        if arg == "--":
            break
        if path_next or (images and not arg.startswith("-")):
            args[i] = cx.codex_path(Path(arg))
            path_next = False
        else:
            images = arg in ("-i", "--image")
            path_next = arg in path_flags
    return subprocess.run([str(cx.find_codex_cli()), *args],
                          env=cx.child_env(cx.base_codex_home()),
                          timeout=8 * 3600).returncode  # an interactive session, bounded to a working day


if __name__ == "__main__":
    raise SystemExit(main())
