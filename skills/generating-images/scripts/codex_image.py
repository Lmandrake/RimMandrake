#!/usr/bin/env python3
"""codex_image.py — drive Codex's built-in $imagegen and harvest the result.

Codex runs as a Windows binary; this script is usually invoked from WSL. It
handles locating the CLI, translating paths across the WSL/Windows boundary,
and — the part that actually matters — recovering the generated file even when
the Codex agent does not copy it where it was told to.

Every fact encoded here was verified on 2026-08-12 against
codex-cli 0.147.0-alpha.6.6. See ../references/codex-contract.md.

Usage
-----
    python codex_image.py generate --prompt "..." --out art.png
    python codex_image.py edit --image src.png --prompt "..." --out out.png
    python codex_image.py probe          # is the whole chain wired up?

Exit codes: 0 ok, 1 generation failed, 2 environment not usable.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import time
from pathlib import Path

# Codex streams agent output; a cold start plus a high-quality render has been
# observed to take several minutes. This is a ceiling to avoid hanging a
# session forever, not a target.
DEFAULT_TIMEOUT_S = 900

# The built-in image_gen tool writes here and ignores any destination argument.
# Harvesting by directory diff is therefore more reliable than trusting the
# agent to copy the file. See references/codex-contract.md.
GENERATED_SUBDIR = "generated_images"


class EnvError(RuntimeError):
    """The Codex toolchain is not usable; the message says what to fix."""


# --------------------------------------------------------------------------
# locating things
# --------------------------------------------------------------------------

def windows_home() -> Path | None:
    """Best guess at the Windows user profile, seen from WSL."""
    users = Path("/mnt/c/Users")
    if not users.is_dir():
        return None
    # USERPROFILE is not exported into WSL, so fall back to the newest profile
    # directory that actually contains a .codex install.
    candidates = [p for p in users.iterdir() if (p / ".codex").is_dir()]
    if not candidates:
        return None
    return max(candidates, key=lambda p: (p / ".codex").stat().st_mtime)


def codex_home() -> Path:
    """$CODEX_HOME, or the discovered Windows .codex directory."""
    env = os.environ.get("CODEX_HOME")
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    for base in (windows_home(), Path.home()):
        if base and (base / ".codex").is_dir():
            return base / ".codex"
    raise EnvError(
        "Cannot find CODEX_HOME. Looked at $CODEX_HOME, /mnt/c/Users/*/.codex "
        "and ~/.codex. Is the Codex app installed?"
    )


def find_codex_cli() -> Path:
    """Locate codex.exe.

    The desktop app installs it under a content-hash directory that changes on
    every update, so the hash is never hardcoded. Order: config.toml (which the
    app itself keeps current) -> PATH -> glob of the install root.
    """
    home = codex_home()

    cfg = home / "config.toml"
    if cfg.is_file():
        # CODEX_CLI_PATH = 'C:\...\codex.exe'  (single or double quoted)
        m = re.search(
            r"CODEX_CLI_PATH\s*=\s*['\"](.+?)['\"]", cfg.read_text(errors="replace")
        )
        if m:
            p = win_to_wsl(m.group(1))
            if p.is_file():
                return p

    on_path = shutil.which("codex") or shutil.which("codex.exe")
    if on_path:
        return Path(on_path)

    wh = windows_home()
    if wh:
        root = wh / "AppData/Local/OpenAI/Codex/bin"
        if root.is_dir():
            exes = sorted(
                root.glob("*/codex.exe"), key=lambda p: p.stat().st_mtime, reverse=True
            )
            if exes:
                return exes[0]

    raise EnvError(
        "Cannot find codex.exe. Checked CODEX_CLI_PATH in config.toml, $PATH, "
        "and AppData/Local/OpenAI/Codex/bin/*/codex.exe. Install or update the "
        "Codex app, or set CODEX_CLI_PATH."
    )


def auth_mode() -> str:
    """'chatgpt', 'apikey', or 'unknown'.

    This decides which imagegen paths are open: the deterministic CLI fallback
    (exact --size/--out, true transparency) needs an API key, which a chatgpt
    login does not provide.
    """
    try:
        data = json.loads((codex_home() / "auth.json").read_text())
    except (OSError, ValueError):
        return "unknown"
    if data.get("OPENAI_API_KEY"):
        return "apikey"
    return data.get("auth_mode") or "unknown"


# --------------------------------------------------------------------------
# path translation
# --------------------------------------------------------------------------

def in_wsl() -> bool:
    return "microsoft" in os.uname().release.lower()


def wsl_to_win(p: Path) -> str:
    """WSL path -> Windows path, for handing to codex.exe."""
    p = p.resolve()
    if not in_wsl():
        return str(p)
    try:
        out = subprocess.run(
            ["wslpath", "-w", str(p)], capture_output=True, text=True, timeout=10
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    # Fall back to the /mnt/<drive>/ convention wslpath would have used.
    s = str(p)
    if s.startswith("/mnt/") and len(s) > 6:
        return f"{s[5].upper()}:\\{s[7:].replace('/', chr(92))}"
    raise EnvError(f"Cannot express {p} as a Windows path; codex.exe needs one.")


def win_to_wsl(p: str) -> Path:
    """Windows path -> WSL path."""
    if not in_wsl():
        return Path(p)
    s = p.strip().strip("'\"")
    s = s.replace("\\\\?\\", "")
    m = re.match(r"^([A-Za-z]):[\\/](.*)$", s)
    if m:
        return Path(f"/mnt/{m.group(1).lower()}/{m.group(2).replace(chr(92), '/')}")
    return Path(s)


# --------------------------------------------------------------------------
# PNG inspection (no third-party dependency on purpose)
# --------------------------------------------------------------------------

_COLOR_TYPES = {0: "grey", 2: "rgb", 3: "palette", 4: "grey+alpha", 6: "rgba"}


def png_info(path: Path) -> dict:
    """Width, height, colour type and whether alpha is possible, from the IHDR."""
    with open(path, "rb") as fh:
        head = fh.read(33)
    if len(head) < 33 or head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    width, height = struct.unpack(">II", head[16:24])
    bit_depth = head[24]
    color_type = head[25]
    return {
        "width": width,
        "height": height,
        "bit_depth": bit_depth,
        "color_type": color_type,
        "color_name": _COLOR_TYPES.get(color_type, f"?{color_type}"),
        "has_alpha_channel": color_type in (4, 6),
        "bytes": path.stat().st_size,
    }


# --------------------------------------------------------------------------
# harvesting
# --------------------------------------------------------------------------

def snapshot_generated(home: Path) -> set[Path]:
    root = home / GENERATED_SUBDIR
    if not root.is_dir():
        return set()
    return {p for p in root.rglob("*") if p.is_file()}


def harvest_new(home: Path, before: set[Path]) -> list[Path]:
    """Files that appeared under generated_images, newest last."""
    after = snapshot_generated(home)
    new = [p for p in (after - before) if p.suffix.lower() in {".png", ".webp", ".jpg"}]
    return sorted(new, key=lambda p: p.stat().st_mtime)


# --------------------------------------------------------------------------
# running codex
# --------------------------------------------------------------------------

def run_codex(prompt: str, images: list[Path], workdir: Path, timeout: int,
              verbose: bool) -> tuple[int, str]:
    cli = find_codex_cli()
    cmd = [str(cli), "exec", "--sandbox", "workspace-write", "--skip-git-repo-check"]
    for img in images:
        if not img.is_file():
            raise EnvError(f"Input image does not exist: {img}")
        cmd += ["-i", wsl_to_win(img)]
    # `-i/--image <FILE>...` is VARIADIC. Without a `--` terminator it keeps
    # consuming positionals, swallows the prompt as another filename, and codex
    # then falls back to reading the prompt from stdin - which is empty, so it
    # exits 0 having done nothing. Verified 2026-08-12; cost one silent no-op.
    if images:
        cmd.append("--")
    cmd.append(prompt)

    if verbose:
        print(f"[codex] {cli}", file=sys.stderr)
        print(f"[codex] cwd={workdir}", file=sys.stderr)

    try:
        proc = subprocess.run(
            cmd, cwd=str(workdir), capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        raise EnvError(
            f"codex exec exceeded {timeout}s. Image generation is slow but not "
            f"this slow - check whether the Codex app needs re-authentication."
        )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


# --------------------------------------------------------------------------
# the two operations
# --------------------------------------------------------------------------

TRANSPARENT_CLAUSE = (
    "Render the subject on a perfectly flat solid {key} chroma-key background. "
    "The background must be one uniform colour with no shadow, gradient, "
    "texture, reflection, floor plane or lighting variation. Keep the subject "
    "fully separated from the background with crisp edges and generous "
    "padding. Use {key} nowhere in the subject itself."
)


def build_prompt(user_prompt: str, out_name: str, chroma_key: str | None) -> str:
    parts = ["Use $imagegen to " + user_prompt.strip()]
    if chroma_key:
        parts.append(TRANSPARENT_CLAUSE.format(key=chroma_key))
    parts.append(
        f"Then copy the generated image into the current working directory as "
        f"{out_name}. Report the absolute path of the file you saved."
    )
    return "\n\n".join(parts)


def do_image(args) -> int:
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and not args.force:
        print(f"ERROR refusing to overwrite {out} (pass --force)", file=sys.stderr)
        return 1

    home = codex_home()
    workdir = out.parent
    images = [Path(i).resolve() for i in (args.image or [])]

    prompt = build_prompt(args.prompt, out.name, args.chroma_key)
    if args.dry_run:
        print(f"codex:   {find_codex_cli()}")
        print(f"auth:    {auth_mode()}")
        print(f"workdir: {workdir}")
        print(f"images:  {[str(i) for i in images] or 'none'}")
        print("--- prompt ---")
        print(prompt)
        return 0

    before = snapshot_generated(home)
    started = time.time()
    code, output = run_codex(prompt, images, workdir, args.timeout, args.verbose)
    elapsed = time.time() - started

    if args.verbose and output:
        print(output[-4000:], file=sys.stderr)

    # The agent was asked to copy the file here. Trust, then verify.
    if not out.is_file():
        candidates = harvest_new(home, before)
        if candidates:
            chosen = candidates[-1]
            shutil.copy2(chosen, out)
            print(f"note: agent did not place the file; harvested {chosen.name} "
                  f"from {GENERATED_SUBDIR}/", file=sys.stderr)

    if not out.is_file():
        print(f"ERROR no image produced after {elapsed:.0f}s (exit {code}).",
              file=sys.stderr)
        if output:
            print("--- last codex output ---", file=sys.stderr)
            print(output[-2000:], file=sys.stderr)
        return 1

    info = png_info(out) if out.suffix.lower() == ".png" else {}
    print(f"OK  {out}")
    if info:
        print(f"    {info['width']}x{info['height']}  {info['color_name']}  "
              f"{info['bytes']:,} bytes  ({elapsed:.0f}s)")
    return 0


def do_probe(args) -> int:
    """Report whether every link in the chain is present. Never calls the API."""
    ok = True
    try:
        cli = find_codex_cli()
        print(f"OK   codex cli      {cli}")
    except EnvError as exc:
        print(f"FAIL codex cli      {exc}")
        return 2
    try:
        home = codex_home()
        print(f"OK   CODEX_HOME     {home}")
    except EnvError as exc:
        print(f"FAIL CODEX_HOME     {exc}")
        return 2

    mode = auth_mode()
    print(f"{'OK  ' if mode != 'unknown' else 'WARN'} auth mode      {mode}")
    if mode == "chatgpt":
        print("     -> built-in image_gen only. No OPENAI_API_KEY, so the")
        print("        deterministic CLI fallback and true model-native")
        print("        transparency are NOT available. Alpha must come from")
        print("        chroma-key + local removal.")

    gen = home / GENERATED_SUBDIR
    print(f"{'OK  ' if gen.is_dir() else 'WARN'} output dir     {gen}"
          f"{'' if gen.is_dir() else '  (absent until first generation)'}")

    try:
        res = subprocess.run([str(cli), "--version"], capture_output=True,
                             text=True, timeout=120)
        print(f"OK   version        {res.stdout.strip() or res.stderr.strip()}")
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"FAIL version        {exc}")
        ok = False

    return 0 if ok else 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--out", required=True, help="destination PNG path")
        p.add_argument("--prompt", required=True)
        p.add_argument("--chroma-key", metavar="HEX", default=None,
                       help="request a flat key background, e.g. '#00ff00'. "
                            "Required for any asset that needs alpha.")
        p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_S)
        p.add_argument("--force", action="store_true")
        p.add_argument("--dry-run", action="store_true",
                       help="print the resolved command and prompt, call nothing")
        p.add_argument("--verbose", action="store_true")

    g = sub.add_parser("generate", help="make a new image from a prompt")
    common(g)
    g.set_defaults(func=do_image, image=[])

    e = sub.add_parser("edit", help="modify existing image(s) with a prompt")
    common(e)
    e.add_argument("--image", action="append", required=True,
                   help="input image; repeat for multiple, order is meaningful")
    e.set_defaults(func=do_image)

    p = sub.add_parser("probe", help="check the toolchain without generating")
    p.set_defaults(func=do_probe)

    args = ap.parse_args()
    try:
        return args.func(args)
    except EnvError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
