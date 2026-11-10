"""Runtime selection and native/Windows boundaries, without spending quota."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE / "artpipe"), str(HERE.parents[2] / "skills/generating-images/scripts")]
import codex_side as side
import agent_runner as ar
import gpt_consult as gc
import canon_check
import common
import ops_watch as ow

cx = ar.CX


class RuntimeTests(unittest.TestCase):
    def test_precedence_and_other_hosts(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(side.platform, "release", return_value="microsoft-WSL2"):
            for host, expected in (("Archmagi", "wsl"), ("OtherPC", "win")):
                with patch.object(side.platform, "node", return_value=host):
                    self.assertEqual(side.codex_side(), expected)
            os.environ["RM_CODEX_SIDE"] = "win"
            self.assertEqual(side.codex_side("wsl"), "wsl")
            os.environ["RM_CODEX_SIDE"] = "invalid"
            with self.assertRaises(ValueError):
                side.codex_side()
        with patch.dict(os.environ, {}, clear=True), patch.object(side.platform, "release", return_value="Linux"):
            self.assertEqual(side.codex_side(), "win")

    def test_linux_paths_home_seed_and_sandbox(self):
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {"RM_CODEX_SIDE": "wsl"}, clear=True):
            root = Path(td)
            base = root / ".codex"
            base.mkdir()
            (base / "auth.json").write_text('{}')
            (base / "config.toml").write_text("CODEX_CLI_PATH='C:\\old.exe'")
            exe = root / ".local/bin/codex"
            exe.parent.mkdir(parents=True)
            exe.touch()
            with patch.object(Path, "home", return_value=root), patch.object(cx, "wsl_to_win", side_effect=AssertionError("Windows translation on Linux")), patch.object(cx, "seed_sandbox_from_template", side_effect=AssertionError("Windows sandbox on Linux")):
                self.assertEqual(cx.base_codex_home(), base)
                self.assertEqual(cx.find_codex_cli(), exe)
                home = cx.codex_home(root / "worker")
                self.assertTrue((home / "auth.json").is_file())
                self.assertFalse((home / ".sandbox").exists())
                self.assertEqual(cx.child_env(home)["CODEX_HOME"], str(home))
                self.assertNotIn("WSLENV", cx.child_env(home))
                self.assertTrue(cx.ensure_home_sandbox(home)[0])
                self.assertTrue(common.codex_sandbox_preflight()[0])
                self.assertEqual(common._default_codex_home_root(), root / ".codex_workers/artpipe")
                self.assertFalse(cx.needs_staging(type("Args", (), {"out": str(root / "a.png"), "image": []})()))
                self.assertEqual(cx.scratch_root(), root / ".local/state/rimmandrake/scratch/codex")

    def test_windows_selection_rejects_linux_path_fallback(self):
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {"RM_CODEX_SIDE": "win"}), patch.object(cx, "in_wsl", return_value=True):
            root = Path(td)
            exe = root / "AppData/Local/OpenAI/Codex/bin/version/codex.exe"
            exe.parent.mkdir(parents=True)
            exe.touch()
            with patch.object(cx, "base_codex_home", return_value=root), patch.object(cx, "windows_home", return_value=root), patch.object(cx.shutil, "which", side_effect=lambda n: "/usr/bin/codex" if n == "codex" else None):
                self.assertEqual(cx.find_codex_cli(), exe)
            with self.assertRaises(cx.EnvError):
                cx.codex_home(root / "invisible")

    def test_shell_launcher_override_and_multiple_images(self):
        with patch.dict(os.environ, {"RM_CODEX_SIDE": "wsl"}), patch.object(cx, "CODEX_SCRATCH"), patch.object(cx, "FOREIGN_THUMB_DIR"), patch.object(cx, "find_codex_cli", return_value="codex.exe"), patch.object(cx, "base_codex_home", return_value=Path("/home")), patch.object(cx, "child_env", return_value={}), patch.object(cx, "codex_path", side_effect=lambda p: "WIN:" + str(p)), patch.object(subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as invoke:
            self.assertEqual(side.main(["--codex", "win", "exec", "-C", "/repo", "-i", "/a.png", "/b.png", "--", "-"]), 0)
            self.assertEqual(side.codex_side(), "win")
            self.assertEqual(invoke.call_args.args[0], ["codex.exe", "exec", "-C", "WIN:/repo", "-i", "WIN:/a.png", "WIN:/b.png", "--", "-"])

    def test_agent_linux_runs_in_clone_with_isolated_home(self):
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {"RM_CODEX_SIDE": "wsl"}), patch.object(cx, "find_codex_cli", return_value=Path("/bin/codex")), patch.object(cx, "wsl_to_win", side_effect=AssertionError("Windows translation on Linux")):
            root = Path(td)
            home = root / "home"
            home.mkdir()
            (home / "auth.json").write_text('{}')
            def invoke(argv, **kw):
                self.assertEqual(kw["cwd"], str(root))
                self.assertEqual(kw["input"], "native prompt")
                self.assertEqual(kw["env"]["CODEX_HOME"], str(home))
                Path(argv[argv.index("-o") + 1]).write_text("ok")
                return subprocess.CompletedProcess(argv, 0, '{"type":"turn.completed","usage":{"input_tokens":1,"output_tokens":1}}', '')
            meter = {"codex.week_used_pct": {"m": "MEASURED", "v": 50}, "codex.hours_to_reset": {"m": "MEASURED", "v": 24}}
            res = ar.run(root, "native prompt", root / "out", root / "events", root / "spend", invoke=invoke, meter=meter, codex_home=home)
            self.assertFalse(res["is_error"], res)
            self.assertNotIn("staging_cwd", json.loads((root / "spend").read_text()))

    def test_consult_lockdown_paths_both_sides(self):
        for runtime in ("wsl", "win"):
            with self.subTest(runtime=runtime), tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {"RM_CODEX_SIDE": runtime}):
                root = Path(td)
                (root / "auth.json").write_text('{}')
                def invoke(argv, **kw):
                    self.assertEqual(kw["env"]["CODEX_HOME"], str(root))
                    self.assertIn("--ephemeral", argv)
                    self.assertIn("--strict-config", argv)
                    self.assertIn("image_generation", argv)
                    self.assertEqual(argv[argv.index("-C") + 1], kw["cwd"])
                    Path(argv[argv.index("-o") + 1]).write_text("ok")
                    return subprocess.CompletedProcess(argv, 0)
                with patch.object(cx, "CODEX_SCRATCH", root / "scratch"), patch.object(cx, "base_codex_home", return_value=root), patch.object(cx, "find_codex_cli", return_value="codex"), patch.object(cx, "wsl_to_win", side_effect=lambda p: str(p)), patch.object(gc.codex_advice, "gate", return_value=0), patch.object(gc, "_receipt"), patch.object(gc, "_log_call"), patch.object(gc.subprocess, "run", side_effect=invoke):
                    self.assertEqual(gc.main(["q", "--codex-home", str(root), "--lockdown", "--effort", "low"]), 0)

    def test_quota_uses_newest_account_reading_from_either_side(self):
        import csuite_codex_limits as limits
        for runtime in ("wsl", "win"):
            with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {"RM_CODEX_SIDE": runtime, "RM_CODEX_SESSIONS": td + "/linux:" + td + "/windows", "RM_OPS_WATCH_DIR": td}):
                now = int(time.time())
                for name, age, used in (("linux", 2, 66), ("windows", 1, 67)):
                    folder = Path(td) / name
                    folder.mkdir()
                    payload = {"primary": {"used_percent": 1, "window_minutes": 300, "resets_at": now + 3600}, "secondary": {"used_percent": used, "window_minutes": 10080, "resets_at": now + 86400}}
                    (folder / "rollout-test.jsonl").write_text(json.dumps({"timestamp": now - age, "payload": {"rate_limits": payload}}) + "\n")
                reading = ow.c_codex(now, ow.load_rules(), {})
                self.assertEqual(reading["codex.week_used_pct"]["v"], 67)
                # A newer Linux reading supersedes Windows; quota is never added.
                p = Path(td) / "linux/rollout-test.jsonl"
                row = json.loads(p.read_text())
                row["timestamp"] = now
                row["payload"]["rate_limits"]["secondary"]["used_percent"] = 68
                p.write_text(json.dumps(row) + "\n")
                self.assertEqual(ow.c_codex(now, ow.load_rules(), {})["codex.week_used_pct"]["v"], 68)


if __name__ == "__main__":
    unittest.main()
