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
import shutil
import tempfile
import time
import types
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import codex_image as ci  # noqa: E402

# Temp dirs here are on ext4, which would route every do_image through the D:-drive staging path.
# The contract tests below are about the unstaged core; test_staging_round_trip covers staging.
_REAL_NEEDS_STAGING = ci.needs_staging
ci.needs_staging = lambda args: False

# SANDBOX_UAC_ONE_STATE: pin the machine's "Password last set" reading so no test calls net.exe, and stub
# the pre-launch guard for the mock-run contract tests; test_ensure_home_sandbox_guard exercises the real one.
PINNED_PWSET = "2026-10-16T17:20:36Z"
os.environ[ci.MACHINE_PWSET_ENV] = PINNED_PWSET
CUR_MARKER = '{"version": 5, "created_at": "2026-10-16T17:20:37.036050700+00:00"}'
OLD_MARKER = '{"version": 5, "created_at": "2026-10-16T14:47:43.844442100+00:00"}'
_REAL_ENSURE = ci.ensure_home_sandbox
ci.ensure_home_sandbox = lambda home, base=None: (True, "selftest stub")

# The foreign-copy guard's thumbnail index must never be written into the real scratch dir by a test.
_THUMB_TMP = tempfile.TemporaryDirectory(prefix="selftest_thumbs_")
ci.FOREIGN_THUMB_DIR = Path(_THUMB_TMP.name)


def give_state(root: Path, marker: str = CUR_MARKER, users: str = '{"version": 5}') -> Path:
    """Write a sandbox state (marker + sandbox_users.json) into root."""
    (root / ".sandbox").mkdir(parents=True, exist_ok=True)
    (root / ".sandbox" / "setup_marker.json").write_text(marker)
    (root / ".sandbox-secrets").mkdir(parents=True, exist_ok=True)
    (root / ".sandbox-secrets" / "sandbox_users.json").write_text(users)
    return root

FAILURES: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}  {detail}")
        FAILURES.append(name)


def tiny_png(path: Path, w: int = 4, h: int = 4, rgba=(255, 0, 0, 255)) -> Path:
    """A real, valid RGBA PNG — png_info() must be able to read it back."""
    raw = b"".join(b"\x00" + bytes(rgba) * w for _ in range(h))

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
        dry_run=False, verbose=False, output_schema=None, output_last_message=None)


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
                             model=None, hm=None, reasoning_effort=None, **_kw):
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
                              model=None, hm=None, reasoning_effort=None, **_kw):
                return 124, "", True
            ci.run_codex = slow_and_empty
            out2 = Path(td) / "art2.png"
            rc = ci.do_image(args_for(out2))
            check("timeout with no image still fails", rc == 1, f"rc={rc}")
            check("no phantom file written", not out2.exists())

            # A clean run where the agent DID place the file needs no harvest.
            def agent_copies(prompt, images, workdir, timeout, verbose,
                            model=None, hm=None, reasoning_effort=None, **_kw):
                gen = tiny_png(home / ci.GENERATED_SUBDIR / "sess3" / "exec-3.png")
                shutil.copy2(gen, Path(workdir) / "art3.png")
                return 0, "", False
            ci.run_codex = agent_copies
            out3 = Path(td) / "art3.png"
            check("normal path still works", ci.do_image(args_for(out3)) == 0)

            # CODEX_FOREIGN_IMAGE_COPY: image_gen returned no path, the agent copied an UNRELATED older image
            # (another session's) into place while this run's own render sat in the home. Ours must win.
            stranger = tiny_png(Path(td) / "otherhome" / ci.GENERATED_SUBDIR / "old" / "bollards.png", 6, 4)
            def agent_copies_foreign(prompt, images, workdir, timeout, verbose,
                                     model=None, hm=None, reasoning_effort=None, **_kw):
                tiny_png(home / ci.GENERATED_SUBDIR / "sess4" / "exec-4.png", 8, 8)
                shutil.copy2(stranger, Path(workdir) / "art4.png")
                return 0, "", False
            ci.run_codex = agent_copies_foreign
            out4 = Path(td) / "art4.png"
            rc = ci.do_image(args_for(out4))
            check("foreign agent copy is replaced by this run's render", rc == 0 and out4.is_file()
                  and ci.png_info(out4)["width"] == 8, f"rc={rc}")

            # ...and when this run generated nothing, the foreign copy is a FAILURE, never an OK.
            def agent_copies_foreign_only(prompt, images, workdir, timeout, verbose,
                                          model=None, hm=None, reasoning_effort=None, **_kw):
                shutil.copy2(stranger, Path(workdir) / "art5.png")
                return 0, "", False
            ci.run_codex = agent_copies_foreign_only
            out5 = Path(td) / "art5.png"
            rc = ci.do_image(args_for(out5))
            check("foreign copy with nothing generated fails", rc == 1 and not out5.exists(), f"rc={rc}")
            check("the foreign copy is set aside as evidence, never at --out",
                  (Path(td) / "art5.foreign.png").is_file())

            # An alias spelling of our OWN home (symlink) among the searched roots must not make this
            # run's render look foreign: the agent placed it correctly, so the twin search finds nothing.
            alias = Path(td) / "alias_home"
            alias.symlink_to(home, target_is_directory=True)
            before7 = ci.snapshot_generated(home)
            own7 = tiny_png(home / ci.GENERATED_SUBDIR / "sess7" / "exec-7.png", 9, 3)
            placed7 = Path(td) / "art7.png"
            shutil.copy2(own7, placed7)
            ci.base_codex_home = lambda: alias
            try:
                check("an alias of our own home never marks our render foreign",
                      ci._preexisting_twin(placed7, home, before7) is None)
            finally:
                ci.base_codex_home = lambda: home

            # A file we cannot trace to any cache (the agent post-processed or moved its own render) is kept.
            def agent_postprocesses(prompt, images, workdir, timeout, verbose,
                                    model=None, hm=None, reasoning_effort=None, **_kw):
                tiny_png(home / ci.GENERATED_SUBDIR / "sess6" / "exec-6.png", 8, 8)
                tiny_png(Path(workdir) / "art6.png", 2, 2, (0, 0, 255, 255))  # a colour no cache file has
                return 0, "", False
            ci.run_codex = agent_postprocesses
            out6 = Path(td) / "art6.png"
            rc = ci.do_image(args_for(out6))
            check("untraceable agent file is kept", rc == 0 and ci.png_info(out6)["width"] == 2, f"rc={rc}")
    finally:
        ci.run_codex, ci.base_codex_home = real_run_codex, real_base
        ci.HARVEST_GRACE_S = real_grace


def pattern_png(path: Path, seed: int, w: int = 96, h: int = 96) -> Path:
    """A busy, seed-unique opaque RGBA picture, so two seeds never look alike to the picture check."""
    import random
    from PIL import Image, ImageDraw
    rnd = random.Random(seed)
    im = Image.new("RGBA", (w, h), tuple(rnd.randrange(256) for _ in range(3)) + (255,))
    d = ImageDraw.Draw(im)
    for _ in range(40):
        x, y = rnd.randrange(w), rnd.randrange(h)
        d.ellipse([x, y, x + rnd.randrange(w // 8, w // 2), y + rnd.randrange(h // 8, h // 2)],
                  fill=tuple(rnd.randrange(256) for _ in range(3)) + (255,))
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    return path


def resized_copy(src: Path, dst: Path, size: tuple[int, int], pad: int = 0, palette: bool = False) -> Path:
    """What the round-3 workers did: resize a foreign image (optionally into a transparent margin, or
    re-encoded as a palette PNG) before placing it, so its bytes match nothing in the cache."""
    from PIL import Image
    with Image.open(src) as im:
        im = im.convert("RGBA").resize(size, Image.LANCZOS)
    if pad:
        canvas = Image.new("RGBA", (size[0] + 2 * pad, size[1] + 2 * pad), (0, 0, 0, 0))
        canvas.paste(im, (pad, pad))
        im = canvas
    if palette:
        im = im.convert("RGB").quantize(64).convert("RGBA")
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst)
    return dst


def test_resized_foreign_copy() -> None:
    """CODEX_FOREIGN_COPY_GUARD_FIX_RESIZED: a resized/padded/recompressed foreign copy is caught, both
    from the cache and from another job's output, while an edit of this call's own input is not."""
    real_run_codex, real_base = ci.run_codex, ci.base_codex_home
    real_grace = ci.HARVEST_GRACE_S
    try:
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            home = td / "codexhome"
            (home / ci.GENERATED_SUBDIR).mkdir(parents=True)
            ci.base_codex_home = lambda: home
            ci.HARVEST_GRACE_S = 0.0
            stranger = pattern_png(td / "otherhome" / ci.GENERATED_SUBDIR / "old" / "flange.png", 1, 192, 128)
            n = [0]

            def place(make):
                def fake(prompt, images, workdir, timeout, verbose, model=None, hm=None,
                         reasoning_effort=None, **_kw):
                    n[0] += 1
                    pattern_png(home / ci.GENERATED_SUBDIR / f"s{n[0]}" / f"exec-{n[0]}.png", 100 + n[0], 80, 80)
                    make(Path(workdir))
                    return 0, "", False
                ci.run_codex = fake

            for label, kw in (("resized smaller", {"size": (64, 64)}),
                              ("resized into a transparent margin", {"size": (120, 80), "pad": 20}),
                              ("resized and re-encoded as a palette PNG", {"size": (48, 48), "palette": True})):
                out = td / f"res_{n[0]}.png"
                placed = td / "probe" / out.name
                resized_copy(stranger, placed, **kw)
                check(f"[{label}] the old byte check alone misses it",
                      ci._preexisting_twin(placed, home, ci.snapshot_generated(home)) is None)
                place(lambda wd, out=out, kw=kw: resized_copy(stranger, wd / out.name, **kw))
                rc = ci.do_image(args_for(out))
                check(f"[{label}] foreign copy replaced by this run's own render",
                      rc == 0 and ci.png_info(out)["width"] == 80, f"rc={rc}")
                check(f"[{label}] foreign copy set aside", out.with_name(out.stem + ".foreign.png").is_file())

            check("the thumbnail index was written outside the repo",
                  any(Path(ci.FOREIGN_THUMB_DIR).glob("*.json")))

            # A second look at the same cache decodes nothing but the placed file (the index answers).
            probe = resized_copy(stranger, td / "probe" / "again.png", (64, 64))
            ci.foreign_source(probe, home, ci.snapshot_generated(home))  # indexes this run's renders too
            calls, real_thumb = [], ci._thumb
            ci._thumb = lambda p: (calls.append(Path(p)), real_thumb(p))[1]
            try:
                hit = ci.foreign_source(probe, home, ci.snapshot_generated(home))
                check("indexed cache: still caught", hit is not None and hit[0] == stranger, str(hit))
                check("indexed cache: only the placed file is decoded", calls == [probe], str(calls))
            finally:
                ci._thumb = real_thumb

            # Another job's output in the same run (artpipe layout <root>/<id>/<id>.png), no cache copy.
            peer = pattern_png(td / "_artsrc" / "jobA" / "jobA.png", 3, 256, 256)
            outB = td / "_artsrc" / "jobB" / "jobB.png"
            place(lambda wd: resized_copy(peer, wd / "jobB.png", (200, 200)))
            rc = ci.do_image(args_for(outB))
            check("a resized copy of another job's output is replaced by this run's render",
                  rc == 0 and ci.png_info(outB)["width"] == 80, f"rc={rc}")

            # An EDIT whose input is itself a cache file legitimately resembles it: never foreign.
            master = pattern_png(td / "otherhome" / ci.GENERATED_SUBDIR / "old" / "master.png", 4, 128, 128)
            outE = td / "edit.png"
            place(lambda wd: resized_copy(master, wd / "edit.png", (64, 64)))
            a = args_for(outE)
            a.image = [str(master)]
            rc = ci.do_image(a)
            check("an edit that resembles its own input image is kept",
                  rc == 0 and ci.png_info(outE)["width"] == 64, f"rc={rc}")

            # A placed picture that resembles nothing is kept as placed.
            outU = td / "unique.png"
            place(lambda wd: pattern_png(wd / "unique.png", 5, 50, 50))
            rc = ci.do_image(args_for(outU))
            check("a placed picture like no other image is kept",
                  rc == 0 and ci.png_info(outU)["width"] == 50, f"rc={rc}")

            # Calibration floor: two different pictures are far apart, a resize of one is near it.
            t1, t2 = ci._thumb(stranger), ci._thumb(master)
            t1r = ci._thumb(resized_copy(stranger, td / "probe" / "r.png", (96, 64)))
            check("different pictures are not near", ci._thumb_dist(t1, t2) > ci.FOREIGN_NEAR * 3,
                  f"{ci._thumb_dist(t1, t2):.2f}")
            check("a resize is near its source", ci._thumb_dist(t1, t1r) <= ci.FOREIGN_NEAR,
                  f"{ci._thumb_dist(t1, t1r):.2f}")
    finally:
        ci.run_codex, ci.base_codex_home = real_run_codex, real_base
        ci.HARVEST_GRACE_S = real_grace


def test_force_regen_failure_does_not_report_stale_success() -> None:
    """--out already exists (only possible with --force) and the regen fails.

    The old file must not be mistaken for a successful new one just because
    out.is_file() is trivially true from before the run even started.
    """
    real_run_codex, real_base = ci.run_codex, ci.base_codex_home
    real_grace = ci.HARVEST_GRACE_S
    try:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td) / "codexhome"
            (home / ci.GENERATED_SUBDIR).mkdir(parents=True)
            ci.base_codex_home = lambda: home
            ci.HARVEST_GRACE_S = 0.0

            out = Path(td) / "art.png"
            tiny_png(out)
            stale_mtime = out.stat().st_mtime

            def does_nothing(prompt, images, workdir, timeout, verbose,
                             model=None, hm=None, reasoning_effort=None, **_kw):
                return 1, "codex: internal error", False
            ci.run_codex = does_nothing

            args = args_for(out)
            args.force = True
            rc = ci.do_image(args)
            check("a failed --force regen over an existing file reports FAILURE",
                  rc == 1, f"rc={rc}")
            check("the stale file was not touched/deleted",
                  out.is_file() and out.stat().st_mtime == stale_mtime)

            # And the successful case still works: a fresh write is recognised.
            def writes_new(prompt, images, workdir, timeout, verbose,
                           model=None, hm=None, reasoning_effort=None, **_kw):
                time.sleep(0.01)
                shutil.copy2(tiny_png(home / ci.GENERATED_SUBDIR / "sessf" / "exec-f.png"), out)
                return 0, "", False
            ci.run_codex = writes_new
            rc = ci.do_image(args)
            check("a --force regen that actually rewrites out reports SUCCESS",
                  rc == 0, f"rc={rc}")
    finally:
        ci.run_codex, ci.base_codex_home = real_run_codex, real_base
        ci.HARVEST_GRACE_S = real_grace


def test_output_schema_passthrough() -> None:
    """--output-schema/--output-last-message reach run_codex's own kwargs.

    CODEX_PARALLEL_WORKERS_1 added these as pure pass-throughs to codex exec's
    own flags; every OTHER caller passes neither, so the thing worth proving
    is that a caller who DOES pass them gets them on the actual run_codex call
    - not that the flags exist syntactically.
    """
    real_run_codex, real_base = ci.run_codex, ci.base_codex_home
    seen = {}
    # Never let do_image snapshot/harvest the machine's REAL codex home from a selftest.
    fake_home = Path(tempfile.mkdtemp()) / "codexhome"
    (fake_home / ci.GENERATED_SUBDIR).mkdir(parents=True)
    try:
        def capture(prompt, images, workdir, timeout, verbose,
                   model=None, hm=None, reasoning_effort=None, **kw):
            seen.update(kw)
            return 0, "", False
        ci.run_codex = capture
        ci.base_codex_home = lambda: fake_home

        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "art.png"
            args = args_for(out)
            args.output_schema = str(Path(td) / "schema.json")
            args.output_last_message = str(Path(td) / "last.json")
            ci.do_image(args)  # fails to produce a file (stub writes nothing);
                               # only run_codex's own kwargs are under test here
        check("output_schema reached run_codex",
              seen.get("output_schema") is not None
              and str(seen["output_schema"]).endswith("schema.json"))
        check("output_last_message reached run_codex",
              seen.get("output_last_message") is not None
              and str(seen["output_last_message"]).endswith("last.json"))

        # And the default (neither flag passed) must stay None - a caller who
        # never asks for this must see byte-identical behaviour to before.
        seen.clear()
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "art.png"
            ci.do_image(args_for(out))
        check("no schema/message flags -> both stay None by default",
              seen.get("output_schema") is None and seen.get("output_last_message") is None)
    finally:
        ci.run_codex, ci.base_codex_home = real_run_codex, real_base
        shutil.rmtree(fake_home.parent, ignore_errors=True)


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
    # Isolate CODEX_SANDBOX_SEED so this test's result never depends on
    # whatever real template this machine happens to have captured (or not)
    # at the real default path — sandbox seeding itself is exercised by
    # test_sandbox_seed_template() and test_sandbox_fingerprint(), not here.
    real_env = os.environ.get("CODEX_SANDBOX_SEED")
    os.environ["CODEX_SANDBOX_SEED"] = "/nonexistent/no-template-here"
    try:
        _test_seed_home_body()
    finally:
        if real_env is not None:
            os.environ["CODEX_SANDBOX_SEED"] = real_env
        else:
            os.environ.pop("CODEX_SANDBOX_SEED", None)


def _test_seed_home_body() -> None:
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


def test_sandbox_seed_template() -> None:
    """A fresh worker home gets its Windows-sandbox setup COPIED from a
    captured template, instead of needing its own (UAC-gated) setup.

    CODEX_PARALLEL_WORKERS_1: every brand-new --codex-home used to trigger a
    fresh `codex-windows-sandbox-setup.exe` run, which creates two local
    Windows accounts and needs a UAC consent dialog per home - unworkable for
    N unattended workers. This is the fix under test.
    """
    real_env = os.environ.get("CODEX_SANDBOX_SEED")
    try:
        with tempfile.TemporaryDirectory() as td:
            template = Path(td) / "template"
            (template / ".sandbox").mkdir(parents=True)
            give_state(template)
            (template / ".sandbox-bin").mkdir()
            (template / ".sandbox-bin" / "codex-command-runner-1.2.3.exe").write_bytes(b"x")
            (template / ".sandbox_migration").write_text("1")
            os.environ["CODEX_SANDBOX_SEED"] = str(template)

            # The "installed" side — a matching runner version, so this is
            # the CODEX_UAC_STORM_1 "compatible" case.
            installed_base = Path(td) / "installed_base"
            (installed_base / ".sandbox-bin").mkdir(parents=True)
            (installed_base / ".sandbox-bin" / "codex-command-runner-1.2.3.exe").write_bytes(b"y")
            give_state(installed_base)

            check("sandbox_seed_template() finds a valid template",
                  ci.sandbox_seed_template() == template)

            fresh = Path(td) / "fresh_worker"
            fresh.mkdir()
            got = ci.seed_sandbox_from_template(fresh, installed_base)
            check("seed_sandbox_from_template reports success with a matching template",
                  got is True)
            check("sandbox setup marker copied into the fresh home",
                  (fresh / ".sandbox" / "setup_marker.json").is_file())
            check("sandbox-bin copied into the fresh home",
                  (fresh / ".sandbox-bin" / "codex-command-runner-1.2.3.exe").is_file())
            check("sandbox-secrets copied into the fresh home",
                  (fresh / ".sandbox-secrets" / "sandbox_users.json").is_file())
            check(".sandbox_migration file copied into the fresh home",
                  (fresh / ".sandbox_migration").is_file())

            # SANDBOX_UAC_ONE_STATE (2026-10-16): a home holding an OLD or half-written provisioning
            # (marker, no sandbox_users.json - artpipe w0/w3/w4) used to be "left untouched", and re-ran
            # the UAC setup on its next launch. It is now re-synced to the current state.
            already_set_up = Path(td) / "already_set_up"
            (already_set_up / ".sandbox").mkdir(parents=True)
            (already_set_up / ".sandbox" / "setup_marker.json").write_text('{"real": true}')
            got2 = ci.seed_sandbox_from_template(already_set_up, installed_base)
            check("a stale already-set-up home is reported as fine", got2 is True)
            check("a stale already-set-up home's marker is replaced by the current one",
                  ci.sandbox_state_blob(already_set_up) == ci.sandbox_state_blob(template))

            # No template at all -> honest False, never a raise, never a fake claim.
            # Redirect the DEFAULT lookup too (not just the env override) - this
            # machine has a real template at the real default path once the fix
            # this test is proving has actually been applied, so leaving the
            # default path live here would test nothing.
            os.environ.pop("CODEX_SANDBOX_SEED", None)
            real_windows_home = ci.windows_home
            ci.windows_home = lambda: Path(td) / "nothing_here"
            try:
                no_template_home = Path(td) / "no_template"
                no_template_home.mkdir()
                check("no template configured -> sandbox_seed_template() is None",
                      ci.sandbox_seed_template() is None)
                check("no template -> seed_sandbox_from_template returns False, not a raise",
                      ci.seed_sandbox_from_template(no_template_home) is False)
            finally:
                ci.windows_home = real_windows_home

        # seed_codex_home() must actually CALL this, not just have it exist unused.
        with tempfile.TemporaryDirectory() as td2:
            template = Path(td2) / "template"
            (template / ".sandbox").mkdir(parents=True)
            give_state(template)
            (template / ".sandbox-bin").mkdir()
            (template / ".sandbox-bin" / "codex-command-runner-9.9.9.exe").write_bytes(b"x")
            os.environ["CODEX_SANDBOX_SEED"] = str(template)

            base = Path(td2) / "base"
            base.mkdir()
            (base / "auth.json").write_text("{}")
            (base / "config.toml").write_text("{}")
            # seed_codex_home()'s own `base` IS what seed_sandbox_from_template
            # compares against (see its call site) — give it a MATCHING
            # .sandbox-bin so this stays the "compatible" case.
            (base / ".sandbox-bin").mkdir()
            (base / ".sandbox-bin" / "codex-command-runner-9.9.9.exe").write_bytes(b"y")
            give_state(base)

            worker = Path(td2) / "worker"
            ci.seed_codex_home(base, worker)
            check("seed_codex_home() itself seeds the sandbox template",
                  (worker / ".sandbox" / "setup_marker.json").is_file())
    finally:
        if real_env is not None:
            os.environ["CODEX_SANDBOX_SEED"] = real_env
        else:
            os.environ.pop("CODEX_SANDBOX_SEED", None)


# --------------------------------------------------------------------------
# 3b. version-aware sandbox seeding (CODEX_UAC_STORM_1, 2026-09-09)
# --------------------------------------------------------------------------

def test_sandbox_bin_fingerprint_picks_newest_by_version() -> None:
    """Real machine state, 2026-09-09: BOTH the shared home's and the seed
    template's `.sandbox-bin` hold every codex build's runner exe ever seen
    (nothing prunes old ones), and a `cp -r` recapture gives several of
    them the SAME copy-time mtime. The fingerprint must therefore be the
    highest VERSION, not the newest file by mtime or a bare string sort."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        d = root / ".sandbox-bin"
        d.mkdir()
        for name in ("codex-command-runner-0.147.0-alpha.6.6.exe",
                     "codex-command-runner-0.148.0-alpha.9.exe",
                     "codex-command-runner-0.153.4.exe",
                     "codex-command-runner-0.153.1.exe"):
            (d / name).write_bytes(b"x")
        check("newest-by-version wins even though it is not last created",
              ci.sandbox_bin_fingerprint(root) == "codex-command-runner-0.153.4.exe")

        # A bare string sort would get this one wrong: "10" < "4" as text.
        (d / "codex-command-runner-0.153.10.exe").write_bytes(b"x")
        check("0.153.10 sorts after 0.153.4 numerically, not as a string",
              ci.sandbox_bin_fingerprint(root) == "codex-command-runner-0.153.10.exe")

        check("no .sandbox-bin at all -> None, not an exception",
              ci.sandbox_bin_fingerprint(root / "nope") is None)

        empty = root / "empty" / ".sandbox-bin"
        empty.mkdir(parents=True)
        check("a .sandbox-bin with no runner exe -> None",
              ci.sandbox_bin_fingerprint(empty.parent) is None)


def test_check_sandbox_fingerprint() -> None:
    """check_sandbox_fingerprint() is the ONE comparison the seeder and the
    daemon preflight both use — proven directly here, independent of
    whichever caller invokes it."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)

        # no template at all - stub sandbox_seed_template() itself (rather
        # than relying on real machine/env state) so `template=None` really
        # means "none configured", not "let the real lookup decide".
        real_template_fn = ci.sandbox_seed_template
        ci.sandbox_seed_template = lambda: None
        try:
            status, tfp, ifp, msg = ci.check_sandbox_fingerprint(root / "base", None)
        finally:
            ci.sandbox_seed_template = real_template_fn
        check("no template -> status no_template", status == "no_template", status)
        check("no_template carries no fingerprints", tfp is None and ifp is None)
        check("no_template message names the env var", "CODEX_SANDBOX_SEED" in msg, msg)

        # matching versions -> match
        base = root / "base_match"
        (base / ".sandbox-bin").mkdir(parents=True)
        (base / ".sandbox-bin" / "codex-command-runner-1.0.0.exe").write_bytes(b"x")
        give_state(base)
        template = root / "template_match"
        give_state(template)
        (template / ".sandbox-bin").mkdir()
        (template / ".sandbox-bin" / "codex-command-runner-1.0.0.exe").write_bytes(b"y")
        status, tfp, ifp, msg = ci.check_sandbox_fingerprint(base, template)
        check("matching versions -> status match", status == "match", status)
        check("match carries no message", msg == "", msg)
        check("match reports both fingerprints", tfp == ifp == "codex-command-runner-1.0.0.exe")

        # SANDBOX_UAC_ONE_STATE: base == template but BOTH on an older provisioning than the machine's
        # (the 2026-10-16 state after worker w1 re-ran setup) -> mismatch, naming --sync-sandbox.
        give_state(base, OLD_MARKER)
        give_state(template, OLD_MARKER)
        status, _t, _i, msg = ci.check_sandbox_fingerprint(base, template)
        check("base+template stale vs machine -> mismatch", status == "mismatch", status)
        check("stale message names --sync-sandbox", "--sync-sandbox" in msg, msg)
        os.environ[ci.MACHINE_PWSET_ENV] = "none"
        try:
            give_state(base)
            give_state(template)
            status, _t, _i, msg = ci.check_sandbox_fingerprint(base, template)
            check("machine reading unavailable -> mismatch, never a pass", status == "mismatch", status)
        finally:
            os.environ[ci.MACHINE_PWSET_ENV] = PINNED_PWSET

        # mismatched versions (the actual CODEX_UAC_STORM_1 root cause)
        base2 = root / "base_mismatch"
        (base2 / ".sandbox-bin").mkdir(parents=True)
        (base2 / ".sandbox-bin" / "codex-command-runner-0.153.4.exe").write_bytes(b"x")
        template2 = root / "template_mismatch"
        (template2 / ".sandbox").mkdir(parents=True)
        (template2 / ".sandbox" / "setup_marker.json").write_text("{}")
        (template2 / ".sandbox-bin").mkdir()
        (template2 / ".sandbox-bin" / "codex-command-runner-0.153.1.exe").write_bytes(b"y")
        status, tfp, ifp, msg = ci.check_sandbox_fingerprint(base2, template2)
        check("mismatched versions -> status mismatch", status == "mismatch", status)
        check("mismatch message names the template build", "0.153.1" in msg, msg)
        check("mismatch message names the installed build", "0.153.4" in msg, msg)
        check("mismatch message names the recapture command", "cp -r" in msg, msg)
        check("mismatch message names the template path", str(template2) in msg, msg)

        # template with .sandbox/setup_marker.json but NO .sandbox-bin at all
        # -> unknown, refused, never a silent pass.
        base3 = root / "base_for_no_bin"
        (base3 / ".sandbox-bin").mkdir(parents=True)
        (base3 / ".sandbox-bin" / "codex-command-runner-1.0.0.exe").write_bytes(b"x")
        template3 = root / "template_no_bin"
        (template3 / ".sandbox").mkdir(parents=True)
        (template3 / ".sandbox" / "setup_marker.json").write_text("{}")
        status, tfp, ifp, msg = ci.check_sandbox_fingerprint(base3, template3)
        check("template with no .sandbox-bin -> status mismatch, not match",
              status == "mismatch", status)
        check("unknown template fingerprint is reported as UNKNOWN", tfp is None)

        # capture-time stamp, if present, wins over deriving from .sandbox-bin
        template4 = root / "template_stamped"
        (template4 / ".sandbox").mkdir(parents=True)
        (template4 / ".sandbox" / "setup_marker.json").write_text("{}")
        (template4 / ".sandbox-bin").mkdir()
        (template4 / ".sandbox-bin" / "codex-command-runner-1.0.0.exe").write_bytes(b"x")
        (template4 / ci.SANDBOX_SEED_STAMP).write_text('{"fingerprint": "stamped-value"}')
        check("a capture-time stamp overrides deriving from .sandbox-bin",
              ci.template_sandbox_fingerprint(template4) == "stamped-value")


def test_seed_sandbox_from_template_refuses_on_mismatch() -> None:
    """The seeder itself: a proven mismatch raises EnvError naming both
    builds and the recapture command, and NEVER copies anything into the
    doomed home first."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        base = root / "base"
        (base / ".sandbox-bin").mkdir(parents=True)
        (base / ".sandbox-bin" / "codex-command-runner-2.0.0.exe").write_bytes(b"x")
        template = root / "template"
        (template / ".sandbox").mkdir(parents=True)
        (template / ".sandbox" / "setup_marker.json").write_text("{}")
        (template / ".sandbox-bin").mkdir()
        (template / ".sandbox-bin" / "codex-command-runner-1.0.0.exe").write_bytes(b"y")
        os.environ["CODEX_SANDBOX_SEED"] = str(template)
        try:
            home = root / "doomed_worker"
            home.mkdir()
            try:
                ci.seed_sandbox_from_template(home, base)
                check("a version mismatch raises EnvError", False, "no exception raised")
            except ci.EnvError as exc:
                check("mismatch EnvError names both builds",
                      "1.0.0" in str(exc) and "2.0.0" in str(exc), str(exc))
                check("mismatch EnvError names the recapture command",
                      "cp -r" in str(exc), str(exc))
            check("no sandbox artifacts were copied into the doomed home",
                  not (home / ".sandbox-bin").exists())
        finally:
            os.environ.pop("CODEX_SANDBOX_SEED", None)

        # And the false-confidence print this item also fixes: seed_codex_home
        # must propagate the raise rather than printing "no UAC prompt
        # expected" over a home it never actually finished seeding.
        os.environ["CODEX_SANDBOX_SEED"] = str(template)
        try:
            base_home = root / "base_full"
            base_home.mkdir()
            (base_home / "auth.json").write_text("{}")
            (base_home / "config.toml").write_text("{}")
            (base_home / ".sandbox-bin").mkdir()
            (base_home / ".sandbox-bin" / "codex-command-runner-2.0.0.exe").write_bytes(b"x")
            worker = root / "worker_full"
            try:
                ci.seed_codex_home(base_home, worker)
                check("seed_codex_home propagates the sandbox mismatch", False,
                      "no exception raised")
            except ci.EnvError as exc:
                check("seed_codex_home's own EnvError is the sandbox mismatch",
                      "sandbox" in str(exc).lower(), str(exc))
        finally:
            os.environ.pop("CODEX_SANDBOX_SEED", None)


# --------------------------------------------------------------------------
# 4. orphaned windows-sandbox helper cleanup (CODEX_EDIT_TIMEOUT_1)
# --------------------------------------------------------------------------

def test_kill_orphaned_sandbox_helpers_parses_pids() -> None:
    """The powershell call's stdout (one PID per line) is counted correctly."""
    real_run = subprocess.run

    def fake_run(cmd, **kwargs):
        if cmd[0] != "powershell.exe":
            return real_run(cmd, **kwargs)  # e.g. wsl_to_win's own `wslpath`
        check("targets codex.exe by name", "codex.exe" in cmd[-1])
        check("filters on --run-as-windows-sandbox",
              "--run-as-windows-sandbox" in cmd[-1])
        return types.SimpleNamespace(stdout="1234\n5678\n", stderr="", returncode=0)

    subprocess.run = fake_run
    try:
        with tempfile.TemporaryDirectory() as td:
            n = ci.kill_orphaned_sandbox_helpers(Path(td))
            check("counts one PID per stdout line", n == 2, f"n={n}")
    finally:
        subprocess.run = real_run


def test_kill_orphaned_sandbox_helpers_survives_powershell_failure() -> None:
    """A powershell/OS failure is swallowed - this is best-effort cleanup,
    never something that should turn a successful harvest into a crash."""
    real_run = subprocess.run
    subprocess.run = lambda *a, **k: (_ for _ in ()).throw(OSError("no powershell.exe"))
    try:
        with tempfile.TemporaryDirectory() as td:
            n = ci.kill_orphaned_sandbox_helpers(Path(td))
            check("OSError from the subprocess call is swallowed, not raised",
                  n == 0, f"n={n}")
    finally:
        subprocess.run = real_run


def test_orphan_cleanup_only_fires_on_timeout_with_home_override() -> None:
    """Cleanup must never run for the shared default home (--codex-home
    unset) - a concurrent unrelated call could legitimately have its own
    helper there - and must never run on a clean (non-timeout) exit."""
    real_run_codex, real_base, real_kill, real_codex_home = (
        ci.run_codex, ci.base_codex_home, ci.kill_orphaned_sandbox_helpers,
        ci.codex_home)
    real_grace = ci.HARVEST_GRACE_S
    calls: list[Path] = []
    ci.kill_orphaned_sandbox_helpers = lambda home: (calls.append(home) or 0)
    try:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td) / "codexhome"
            (home / ci.GENERATED_SUBDIR).mkdir(parents=True)
            worker_home = Path(td) / "worker0"
            (worker_home / ci.GENERATED_SUBDIR).mkdir(parents=True)
            ci.base_codex_home = lambda: home
            # Real codex_home() refuses a /tmp path as not Windows-visible -
            # correct behaviour, but out of scope here: this test is only
            # about do_image's OWN decision of when to call cleanup.
            ci.codex_home = lambda override=None: (
                worker_home if override else home)
            ci.HARVEST_GRACE_S = 0.0

            def timed_out_no_image(prompt, images, workdir, timeout, verbose,
                                    model=None, hm=None, reasoning_effort=None, **_kw):
                return 124, "", True
            ci.run_codex = timed_out_no_image

            # shared home (no --codex-home override): must NOT clean up.
            ci.do_image(args_for(Path(td) / "a.png"))
            check("no cleanup against the shared default home", calls == [])

            # isolated home override + timeout: MUST clean up.
            ci.do_image(args_for(Path(td) / "b.png", home=worker_home))
            check("cleanup runs for a timed-out isolated-home call",
                  calls == [worker_home], str(calls))

            # isolated home, but a clean (non-timeout) run: must NOT clean up.
            calls.clear()

            def clean_no_image(prompt, images, workdir, timeout, verbose,
                                model=None, hm=None, reasoning_effort=None, **_kw):
                return 1, "codex: some other failure", False
            ci.run_codex = clean_no_image
            ci.do_image(args_for(Path(td) / "c.png", home=worker_home))
            check("no cleanup for a non-timeout failure", calls == [])
    finally:
        ci.run_codex, ci.base_codex_home = real_run_codex, real_base
        ci.kill_orphaned_sandbox_helpers = real_kill
        ci.codex_home = real_codex_home
        ci.HARVEST_GRACE_S = real_grace


def test_home_must_be_windows_visible() -> None:
    if not ci.in_wsl():
        print("  skip /mnt guard (not running under WSL)")
        return
    try:
        ci.codex_home("/tmp/definitely-not-visible-to-windows")
        check("a WSL-only worker home is refused", False, "no EnvError raised")
    except ci.EnvError as exc:
        check("a WSL-only worker home is refused", "Windows" in str(exc), str(exc))


def test_staging_round_trip() -> None:
    """ext4 caller paths: inputs copied into a scratch job dir, codex runs THERE, outputs come back."""
    real_run_codex, real_scratch, real_base = ci.run_codex, ci.CODEX_SCRATCH, ci.base_codex_home
    seen = {}
    try:
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            ci.CODEX_SCRATCH = td / "scratch"
            home = td / "codexhome"
            (home / ci.GENERATED_SUBDIR).mkdir(parents=True)
            ci.base_codex_home = lambda: home
            ref = tiny_png(td / "in" / "ref.png")
            schema = td / "schema.json"
            schema.write_text("{}")

            def fake(prompt, images, workdir, timeout, verbose, model=None, hm=None,
                     reasoning_effort=None, output_schema=None, output_last_message=None):
                seen.update(workdir=workdir, images=images, schema=output_schema, model=model)
                shutil.copy2(tiny_png(home / ci.GENERATED_SUBDIR / "s" / "exec-s.png"), Path(workdir) / "art.png")
                Path(output_last_message).write_text('{"status":"ok"}')
                return 0, "", False
            ci.run_codex = fake
            args = args_for(td / "out" / "art.png")
            args.image = [str(ref)]
            args.model = ci.DEFAULT_MODEL
            args.output_schema = str(schema)
            args.output_last_message = str(td / "out" / "last.json")
            check("ext4 paths need staging", _REAL_NEEDS_STAGING(args) is True)
            rc = ci.stage_and_run(args)
            check("staged run succeeds", rc == 0)
            check("codex ran inside the scratch job dir",
                  str(seen.get("workdir", "")).startswith(str(ci.CODEX_SCRATCH)), str(seen))
            check("the input image handed to codex is the staged copy",
                  all(str(i).startswith(str(ci.CODEX_SCRATCH)) for i in seen.get("images", [])))
            check("schema staged too", str(seen.get("schema", "")).startswith(str(ci.CODEX_SCRATCH)))
            check("output copied back to the caller's path", (td / "out" / "art.png").is_file())
            check("last message copied back", (td / "out" / "last.json").read_text() == '{"status":"ok"}')
            check("job dir removed after success", not any(ci.CODEX_SCRATCH.iterdir()))
            check("default model is passed explicitly", seen.get("model") == ci.DEFAULT_MODEL)
            args2 = args_for(Path("/mnt/d/x/art.png"))
            check("Windows-drive paths are not staged", _REAL_NEEDS_STAGING(args2) is False)
    finally:
        ci.run_codex, ci.CODEX_SCRATCH, ci.base_codex_home = real_run_codex, real_scratch, real_base


def test_ensure_home_sandbox_guard() -> None:
    """SANDBOX_UAC_ONE_STATE: the hard pre-launch guard. Never launches codex."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        base = give_state(root / "base")
        (base / ".sandbox-bin").mkdir()
        (base / ".sandbox-bin" / "codex-command-runner-1.0.0.exe").write_bytes(b"x")
        home = root / "w0"
        (home / ".sandbox").mkdir(parents=True)
        (home / ".sandbox" / "setup_marker.json").write_text(OLD_MARKER)  # half-written, no users file
        ok, why = _REAL_ENSURE(home, base)
        check("current base + stale home -> synced and ready", ok, why)
        check("home now carries the base's exact state",
              ci.sandbox_state_blob(home) == ci.sandbox_state_blob(base))
        check("home got the base's runner", ci.sandbox_bin_fingerprint(home) == "codex-command-runner-1.0.0.exe")

        give_state(base, OLD_MARKER)
        stale_home = give_state(root / "w1", '{"x": 1}')
        ok, why = _REAL_ENSURE(stale_home, base)
        check("stale base -> refused", not ok, why)
        check("refusal names --sync-sandbox", "--sync-sandbox" in why, why)
        check("refused home is left untouched", '{"x": 1}' in (stale_home / ".sandbox" / "setup_marker.json").read_text())

        os.environ[ci.MACHINE_PWSET_ENV] = "none"
        try:
            give_state(base)
            ok, why = _REAL_ENSURE(home, base)
            check("unreadable machine provisioning -> refused", not ok, why)
        finally:
            os.environ[ci.MACHINE_PWSET_ENV] = PINNED_PWSET

        found = ci.find_current_sandbox_state([give_state(root / "old", OLD_MARKER), base])
        check("find_current_sandbox_state picks the current home", found == base, str(found))

        # _do_image must refuse BEFORE run_codex when the guard says no.
        give_state(base, OLD_MARKER)
        real_run, real_env_home = ci.run_codex, os.environ.get("CODEX_HOME")
        launched = []
        ci.run_codex = lambda *a, **k: launched.append(1) or (0, "", False)
        ci.ensure_home_sandbox = _REAL_ENSURE
        os.environ["CODEX_HOME"] = str(base)
        try:
            rc = ci.do_image(args_for(root / "out.png"))
        finally:
            ci.run_codex = real_run
            ci.ensure_home_sandbox = lambda home, base=None: (True, "selftest stub")
            if real_env_home is None:
                os.environ.pop("CODEX_HOME", None)
            else:
                os.environ["CODEX_HOME"] = real_env_home
        check("do_image exits 2 on a not-ready sandbox", rc == 2, str(rc))
        check("do_image never launched codex", not launched)


def main() -> int:
    for fn in (test_prompt, test_staging_round_trip, test_run_codex_timeout, test_reasoning_effort_flag,
               test_timeout_still_harvests, test_resized_foreign_copy,
               test_force_regen_failure_does_not_report_stale_success,
               test_output_schema_passthrough,
               test_harvest_grace,
               test_child_env_wslenv, test_seed_home, test_sandbox_seed_template,
               test_sandbox_bin_fingerprint_picks_newest_by_version,
               test_check_sandbox_fingerprint,
               test_seed_sandbox_from_template_refuses_on_mismatch,
               test_ensure_home_sandbox_guard,
               test_kill_orphaned_sandbox_helpers_parses_pids,
               test_kill_orphaned_sandbox_helpers_survives_powershell_failure,
               test_orphan_cleanup_only_fires_on_timeout_with_home_override,
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
