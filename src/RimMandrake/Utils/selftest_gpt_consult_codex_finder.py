#!/usr/bin/env python3
"""gpt_consult.py finds Codex with the image skills absent (RIMMANDRAKE_MOVE_IMAGE_SKILLS_TO_WORKFLOWS_GPT_TOOL_BORROWS).

gpt_consult used to import `skills/generating-images/scripts/codex_image.py` for its Codex finder, so moving
that skill out of the repo broke the ask-GPT tool. Each case runs in a fresh interpreter whose import of
`codex_image` raises, as it would with the skill folder gone, and a fake HOME holding a Linux `codex`.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

PROBE = r"""
import sys, importlib.abc
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path=None, target=None):
        if name == "codex_image":
            raise ImportError("codex_image blocked: the image skill folder is absent")
        return None
sys.meta_path.insert(0, Block())
sys.path.insert(0, sys.argv[1])
import gpt_consult as GC
assert "codex_image" not in sys.modules, "gpt_consult still loaded codex_image"
cli = GC.codex_cli
print("CLI=" + str(cli.find_codex_cli()))
print("HOME=" + str(cli.base_codex_home()))
print("ENV=" + cli.child_env(cli.base_codex_home())["CODEX_HOME"])
print("SCRATCH=" + str(cli.CODEX_SCRATCH))
"""


def run(home, env_extra):
    env = {k: v for k, v in os.environ.items() if k not in ("CODEX_HOME", "CODEX_SCRATCH")}
    env.update(HOME=str(home), RM_CODEX_SIDE="wsl", PATH="/usr/bin:/bin", **env_extra)
    return subprocess.run([sys.executable, "-c", PROBE, str(HERE)], capture_output=True, text=True, env=env,
                          timeout=60)


def main():
    fails = 0
    with tempfile.TemporaryDirectory() as t:
        home = Path(t)
        exe = home / ".local/bin/codex"
        exe.parent.mkdir(parents=True)
        exe.write_text("#!/bin/sh\necho ok\n")
        exe.chmod(0o755)
        (home / ".codex").mkdir()
        cases = [
            ("finds Linux codex and home with codex_image unimportable", {},
             ["CLI=%s" % exe, "HOME=%s" % (home / ".codex"), "ENV=%s" % (home / ".codex")]),
            ("CODEX_SCRATCH override reaches the finder", {"CODEX_SCRATCH": str(home / "scr")},
             ["SCRATCH=%s" % (home / "scr")]),
        ]
        for name, extra, want in cases:
            r = run(home, extra)
            got = r.stdout.splitlines()
            missing = [w for w in want if w not in got]
            if r.returncode != 0 or missing:
                fails += 1
                print("FAIL %s: rc=%d missing=%s\n%s" % (name, r.returncode, missing, r.stderr.strip()[-600:]))
            else:
                print("PASS %s" % name)
        exe.unlink()
        r = run(home, {})
        if r.returncode != 0 and "Cannot find Linux codex" in r.stderr:
            print("PASS no codex anywhere fails by name")
        else:
            fails += 1
            print("FAIL no codex anywhere: rc=%d\n%s" % (r.returncode, (r.stdout + r.stderr).strip()[-600:]))
    print("%s: %d failure(s)" % ("FAIL" if fails else "OK", fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
