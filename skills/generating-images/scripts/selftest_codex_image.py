#!/usr/bin/env python3
"""selftest_codex_image.py — the wrapper's contract, with no Codex call at all.

Everything here runs against stubs and temp directories. 🔴 It NEVER spends
image quota, and it must stay that way: the one thing this file exists to prove
is that a *timeout* no longer throws away a finished image, and reproducing
that for real would cost a generation every run.

    python3 selftest_codex_image.py

Exit codes: 0 all passed, 1 something failed.
"""

from __future__ import annotations

import os
import struct
import subprocess
import sys
import tempfile
import types
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import codex_image as ci  # noqa: E402

FAILURES: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}  {detail}")
        FAILURES.append(name)


def tiny_png(path: Path, w: int = 4, h: int = 4) -> Path:
    """A real, valid RGBA PNG — png_info() must be able to read it back."""
    raw = b"".join(b"\x00" + bytes([255, 0, 0, 255]) * w for _ in range(h))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )
    return path


def args_for(out: Path, home: Path | None = None) -> types.SimpleNamespace:
    return types.SimpleNamespace(
        out=str(out), prompt="a crate", image=[], timeout=30, model=None,
        reasoning_effort="low", codex_home=home and str(home), force=False,
        dry_run=False, verbose=False)


# --------------------------------------------------------------------------
# 1. the prompt no longer asks for a chroma-key background
# --------------------------------------------------------------------------

def test_prompt() -> None:
    p = ci.build_prompt("a rusty crate, transparent background", "crate.png")
    check("prompt starts with the tool invocation", p.startswith("Use $imagegen to "))
    check("prompt names the destination file", "crate.png" in p)
    low = p.lower()
    check("prompt has no chroma-key clause",
          "chroma" not in low and "#00ff00" not in low, low[:120])
    check("TRANSPARENT_CLAUSE is gone", not hasattr(ci, "TRANSPARENT_CLAUSE"))
    check("build_prompt takes no key argument",
          ci.build_prompt.__code__.co_argcount == 2)
    # chroma_key.py itself is NOT deleted: two live scripts still read
    # green-keyed raws that already exist on disk. Retirement means nothing
    # GENERATES onto a key any more, which is what the two checks above prove.


# --------------------------------------------------------------------------
# 2. run_codex reports a timeout instead of raising through it
# --------------------------------------------------------------------------

def test_run_codex_timeout() -> None:
    real_run, real_cli, real_env = ci.subprocess.run, ci.find_codex_cli, ci.child_env
    try:
        ci.find_codex_cli = lambda: Path("/nonexistent/codex.exe")
        ci.child_env = lambda home: {}

        def boom(*a, **kw):
            raise subprocess.TimeoutExpired(cmd="codex", timeout=kw.get("timeout", 1),
                                            output="partial stdout")
        ci.subprocess.run = boom
        with tempfile.TemporaryDirectory() as td:
            code, out, timed_out = ci.run_codex("p", [], Path(td), 5, False)
        check("timeout does not raise", True)
        check("timeout flagged", timed_out is True)
        check("timeout returns a non-zero code", code != 0, str(code))
        check("partial output preserved", "partial stdout" in out, out[:80])

        def fine(*a, **kw):
            return types.SimpleNamespace(returncode=0, stdout="done", stderr="")
        ci.subprocess.run = fine
        with tempfile.TemporaryDirectory() as td:
            code, out, timed_out = ci.run_codex("p", [], Path(td), 5, False)
        check("clean run not flagged as timeout", timed_out is False)
        check("clean run returns its code and output", code == 0 and "done" in out)
    finally:
        ci.subprocess.run, ci.find_codex_cli, ci.child_env = real_run, real_cli, real_env


def test_reasoning_effort_flag() -> None:
    seen: dict[str, list] = {}
    real_run, real_cli, real_env = ci.subprocess.run, ci.find_codex_cli, ci.child_env
    try:
        ci.find_codex_cli = lambda: Path("/nonexistent/codex.exe")
        ci.child_env = lambda home: {}

        def capture(cmd, **kw):
            seen["cmd"] = cmd
            return types.SimpleNamespace(returncode=0, stdout="", stderr="")
        ci.subprocess.run = capture
        with tempfile.TemporaryDirectory() as td:
            ci.run_codex("p", [], Path(td), 5, False, reasoning_effort="low")
        check("effort reaches codex as -c",
              'model_reasoning_effort="low"' in seen["cmd"], str(seen["cmd"]))
        with tempfile.TemporaryDirectory() as td:
            ci.run_codex("p", [], Path(td), 5, False, reasoning_effort="inherit")
        check("'inherit' sends no override",
              not any("model_reasoning_effort" in str(c) for c in seen["cmd"]),
              str(seen["cmd"]))
        check("low is a legal effort for the configured model",
              "low" in ci.REASONING_EFFORTS and ci.DEFAULT_REASONING_EFFORT == "low")
    finally:
        ci.subprocess.run, ci.find_codex_cli, ci.child_env = real_run, real_cli, real_env


# --------------------------------------------------------------------------
# 3. 🔴 the fix itself: a timeout with an image on disk is a SUCCESS
# --------------------------------------------------------------------------

def test_timeout_still_harvests() -> None:
    real_run_codex, real_base = ci.run_codex, ci.base_codex_home
    real_grace = ci.HARVEST_GRACE_S
    try:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td) / "codexhome"
            (home / ci.GENERATED_SUBDIR).mkdir(parents=True)
            ci.base_codex_home = lambda: home
            ci.HARVEST_GRACE_S = 0.0

            def slow_but_done(prompt, images, workdir, timeout, verbose,
                             model=None, hm=None, reasoning_effort=None):
                # The image lands; our ceiling then expires during the wrap-up.
                tiny_png(home / ci.GENERATED_SUBDIR / "sess" / "exec-abc.png")
                return 124, "", True
            ci.run_codex = slow_but_done

            out = Path(td) / "art.png"
            rc = ci.do_image(args_for(out))
            check("timeout with an image returns SUCCESS", rc == 0, f"rc={rc}")
            check("the harvested image landed at --out", out.is_file())
            if out.is_file():
                info = ci.png_info(out)
                check("harvested file is a readable PNG",
                      info["width"] == 4 and info["has_alpha_channel"], str(info))

            # ...and a timeout with nothing on disk is still a failure.
            def slow_and_empty(prompt, images, workdir, timeout, verbose,
                              model=None, hm=None, reasoning_effort=None):
                return 124, "", True
            ci.run_codex = slow_and_empty
            out2 = Path(td) / "art2.png"
            rc = ci.do_image(args_for(out2))
            check("timeout with no image still fails", rc == 1, f"rc={rc}")
            check("no phantom file written", not out2.exists())

            # A clean run where the agent DID place the file needs no harvest.
            def agent_copies(prompt, images, workdir, timeout, verbose,
                            model=None, hm=None, reasoning_effort=None):
                tiny_png(Path(workdir) / "art3.png")
                return 0, "", False
            ci.run_codex = agent_copies
            out3 = Path(td) / "art3.png"
            check("normal path still works", ci.do_image(args_for(out3)) == 0)
    finally:
        ci.run_codex, ci.base_codex_home = real_run_codex, real_base
        ci.HARVEST_GRACE_S = real_grace


def test_harvest_grace() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        (home / ci.GENERATED_SUBDIR).mkdir()
        before = ci.snapshot_generated(home)
        check("grace poll gives up when nothing appears",
              ci.harvest_with_grace(home, before, 0.0) == [])
        tiny_png(home / ci.GENERATED_SUBDIR / "s" / "a.png")
        found = ci.harvest_with_grace(home, before, 0.0)
        check("grace poll finds a late file", len(found) == 1, str(found))
        check("only NEW files are harvested",
              ci.harvest_with_grace(home, ci.snapshot_generated(home), 0.0) == [])


# --------------------------------------------------------------------------
# 4. per-worker CODEX_HOME isolation
# --------------------------------------------------------------------------

def test_child_env_wslenv() -> None:
    # ⚠️ The measured trap: a Windows child does NOT inherit a bare env var
    # from WSL. It must be named in WSLENV or it arrives empty.
    if not ci.in_wsl():
        print("  skip WSLENV checks (not running under WSL)")
        return
    env = ci.child_env(Path("/mnt/c/Users/Mandrake/.codex"))
    check("CODEX_HOME is set for the child", "CODEX_HOME" in env)
    check("CODEX_HOME is a Windows path", ":\\" in env["CODEX_HOME"], env["CODEX_HOME"])
    names = [n.split("/")[0] for n in env.get("WSLENV", "").split(":") if n]
    check("CODEX_HOME is listed in WSLENV", "CODEX_HOME" in names, env.get("WSLENV", ""))

    old = os.environ.get("WSLENV")
    try:
        os.environ["WSLENV"] = "CODEX_HOME/p:OTHER"
        env = ci.child_env(Path("/mnt/c/Users/Mandrake/.codex"))
        names = [n.split("/")[0] for n in env["WSLENV"].split(":") if n]
        check("an existing CODEX_HOME entry is not duplicated",
              names.count("CODEX_HOME") == 1, env["WSLENV"])
        check("other WSLENV entries survive", "OTHER" in names, env["WSLENV"])
    finally:
        if old is None:
            os.environ.pop("WSLENV", None)
        else:
            os.environ["WSLENV"] = old


def test_seed_home() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td) / "base"
        (base / "skills" / ".system" / "imagegen").mkdir(parents=True)
        (base / "skills" / ".system" / "imagegen" / "SKILL.md").write_text("x")
        for name in ("auth.json", "config.toml"):
            (base / name).write_text("{}")
        (base / ci.GENERATED_SUBDIR).mkdir()
        tiny_png(base / ci.GENERATED_SUBDIR / "old" / "shared.png")

        worker = Path(td) / "worker"
        ci.seed_codex_home(base, worker)
        check("worker home is logged in", (worker / "auth.json").is_file())
        check("worker home carries config.toml", (worker / "config.toml").is_file())
        check("worker home carries the $imagegen system skill",
              (worker / "skills" / ".system" / "imagegen" / "SKILL.md").is_file())
        check("worker home does NOT inherit the shared image pile",
              not (worker / ci.GENERATED_SUBDIR).exists())
        check("re-seeding an existing home is a no-op",
              ci.seed_codex_home(base, worker) == worker)


def test_home_must_be_windows_visible() -> None:
    if not ci.in_wsl():
        print("  skip /mnt guard (not running under WSL)")
        return
    try:
        ci.codex_home("/tmp/definitely-not-visible-to-windows")
        check("a WSL-only worker home is refused", False, "no EnvError raised")
    except ci.EnvError as exc:
        check("a WSL-only worker home is refused", "Windows" in str(exc), str(exc))


def main() -> int:
    for fn in (test_prompt, test_run_codex_timeout, test_reasoning_effort_flag,
               test_timeout_still_harvests, test_harvest_grace,
               test_child_env_wslenv, test_seed_home,
               test_home_must_be_windows_visible):
        print(fn.__name__)
        fn()
    print()
    if FAILURES:
        print(f"FAILED {len(FAILURES)}: {', '.join(FAILURES)}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
