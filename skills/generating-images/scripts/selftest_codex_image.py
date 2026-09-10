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
import time
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
                tiny_png(Path(workdir) / "art3.png")
                return 0, "", False
            ci.run_codex = agent_copies
            out3 = Path(td) / "art3.png"
            check("normal path still works", ci.do_image(args_for(out3)) == 0)
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
                tiny_png(out)
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
    real_run_codex = ci.run_codex
    seen = {}
    try:
        def capture(prompt, images, workdir, timeout, verbose,
                   model=None, hm=None, reasoning_effort=None, **kw):
            seen.update(kw)
            return 0, "", False
        ci.run_codex = capture

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
        ci.run_codex = real_run_codex


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
            (template / ".sandbox" / "setup_marker.json").write_text('{"version": 5}')
            (template / ".sandbox-bin").mkdir()
            (template / ".sandbox-bin" / "codex-command-runner-1.2.3.exe").write_bytes(b"x")
            (template / ".sandbox-secrets").mkdir()
            (template / ".sandbox-secrets" / "sandbox_users.json").write_text("{}")
            (template / ".sandbox_migration").write_text("1")
            os.environ["CODEX_SANDBOX_SEED"] = str(template)

            # The "installed" side — a matching runner version, so this is
            # the CODEX_UAC_STORM_1 "compatible" case.
            installed_base = Path(td) / "installed_base"
            (installed_base / ".sandbox-bin").mkdir(parents=True)
            (installed_base / ".sandbox-bin" / "codex-command-runner-1.2.3.exe").write_bytes(b"y")

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

            # A home that already has its OWN real setup is left untouched -
            # never overwritten by the template.
            already_set_up = Path(td) / "already_set_up"
            (already_set_up / ".sandbox").mkdir(parents=True)
            (already_set_up / ".sandbox" / "setup_marker.json").write_text('{"real": true}')
            got2 = ci.seed_sandbox_from_template(already_set_up)
            check("an already-set-up home is reported as fine", got2 is True)
            check("an already-set-up home's OWN marker is not overwritten",
                  "real" in (already_set_up / ".sandbox" / "setup_marker.json").read_text())
            check("an already-set-up home did NOT get .sandbox-bin from the template",
                  not (already_set_up / ".sandbox-bin").exists())

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
            (template / ".sandbox" / "setup_marker.json").write_text("{}")
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
        template = root / "template_match"
        (template / ".sandbox").mkdir(parents=True)
        (template / ".sandbox" / "setup_marker.json").write_text("{}")
        (template / ".sandbox-bin").mkdir()
        (template / ".sandbox-bin" / "codex-command-runner-1.0.0.exe").write_bytes(b"y")
        status, tfp, ifp, msg = ci.check_sandbox_fingerprint(base, template)
        check("matching versions -> status match", status == "match", status)
        check("match carries no message", msg == "", msg)
        check("match reports both fingerprints", tfp == ifp == "codex-command-runner-1.0.0.exe")

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
        real_env = None
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


def main() -> int:
    for fn in (test_prompt, test_run_codex_timeout, test_reasoning_effort_flag,
               test_timeout_still_harvests,
               test_force_regen_failure_does_not_report_stale_success,
               test_output_schema_passthrough,
               test_harvest_grace,
               test_child_env_wslenv, test_seed_home, test_sandbox_seed_template,
               test_sandbox_bin_fingerprint_picks_newest_by_version,
               test_check_sandbox_fingerprint,
               test_seed_sandbox_from_template_refuses_on_mismatch,
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
