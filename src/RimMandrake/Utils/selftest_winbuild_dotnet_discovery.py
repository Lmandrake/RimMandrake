#!/usr/bin/env python3
"""Selftest for winbuild.dotnet_exe discovery: WINBUILD_DOTNET wins and fails loudly by name when wrong; PATH
(dotnet.exe) is next; then the known install dirs (Program Files, any /mnt/c/Users/*/.dotnet); none -> exit naming
the env var. No hardcoded user name."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import winbuild as WB  # noqa: E402

FAILS = []


def check(ok, msg, detail=""):
    print(("ok    " if ok else "FAIL  ") + msg + ("" if ok else "  %s" % (detail,)))
    if not ok:
        FAILS.append(msg)


def mk(p):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").close()
    os.chmod(p, 0o755)
    return p


def call():
    try:
        return WB.dotnet_exe()
    except SystemExit as e:
        return "EXIT:%s" % e


def main():
    with tempfile.TemporaryDirectory() as td:
        env = os.path.join(td, "envdn", "dotnet.exe")
        onpath = mk(os.path.join(td, "bin", "dotnet.exe"))
        users = os.path.join(td, "Users")
        pf = os.path.join(td, "pf", "dotnet.exe")
        other = mk(os.path.join(users, "sjlewis", ".dotnet", "dotnet.exe"))
        WB.DOTNET_USER_GLOB = os.path.join(users, "*", ".dotnet", "dotnet.exe")
        WB.DOTNET_FIXED = [pf]
        old_env, old_path = os.environ.get("WINBUILD_DOTNET"), os.environ.get("PATH")
        try:
            os.environ.pop("WINBUILD_DOTNET", None)
            os.environ["PATH"] = os.path.join(td, "empty")
            check(call() == other, "user .dotnet glob finds any Windows user's SDK (not just Mandrake)", call())
            mk(pf)
            check(call() == other, "per-user .dotnet beats Program Files (Archmagi order kept)", call())
            os.remove(other)
            check(call() == pf, "Program Files found", call())
            os.remove(pf)
            os.environ["PATH"] = os.path.join(td, "bin")
            check(call() == onpath, "PATH dotnet.exe is the last resort", call())
            mk(other)
            mk(env)
            os.environ["WINBUILD_DOTNET"] = env
            check(call() == env, "WINBUILD_DOTNET wins over PATH", call())
            os.environ["WINBUILD_DOTNET"] = os.path.join(td, "nope.exe")
            r = call()
            check(r.startswith("EXIT:") and "WINBUILD_DOTNET" in r, "bad WINBUILD_DOTNET fails loudly by name, no fallback", r)
            os.environ.pop("WINBUILD_DOTNET")
            os.environ["PATH"] = os.path.join(td, "empty")
            os.remove(other)
            r = call()
            check(r.startswith("EXIT:") and "WINBUILD_DOTNET" in r, "nothing found: exit names WINBUILD_DOTNET", r)
        finally:
            for k, v in (("WINBUILD_DOTNET", old_env), ("PATH", old_path)):
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
    print("FAILED %d" % len(FAILS) if FAILS else "ALL OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
