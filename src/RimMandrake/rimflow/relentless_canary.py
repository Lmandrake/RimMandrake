#!/usr/bin/env python3
"""relentless_canary.py -- the live harness's canaries, run IN the supervisor's service context before a live round spends a
slot (VALIDATOR_REPLAY_BUILD_GOOD_AND_BAD; spec design/RimMandrake/test_tolerance_gpt_advice_2026-11-04.md, rank 5: "run
cheap canaries through the actual supervisor service context").

    python3 src/RimMandrake/rimflow/relentless_canary.py show       # the cached health, its fingerprint and age
    python3 src/RimMandrake/rimflow/relentless_canary.py run        # run them now from THIS shell (a developer read:
                                                                    # the round's own run is the one that counts)

WHY IN THE SERVICE CONTEXT. TITANIC was held by the tick's PATH bug (no powershell.exe on the unit's PATH: the game read as
not running) while every read worked from a developer shell. So relentless_live_round.run_round calls gate() itself, in
the process the supervisor launched (Effects.live_round_launch: its env, its PATH, its cwd), and a proof's commands run
exactly as a proof's do (Fx.run_proof: bash, model.bridge_holder.process_env()).

THE CANARIES, cheap first; the first that fails ends the run and names itself:
  interop      the proof shell reaches Windows: `python.exe` answers a nonce (Windows/WSL interop and the PATH a proof gets)
  game         exactly one RimWorld runs and its start time reads (Fx.game_started, the round's own identity of the game)
  -- bridge taken here (`rimflow bridge take --idle-ok`), released whatever happens --
  holder       `rimflow bridge who` names RELENTLESS: the identity our takes carry (model.bridge_identity) is the one held
  bridge       a round trip: rimbridge/ping from python.exe answers
  load         jawa/running_mods answers and holds the base game (ludeon.rimworld): the load's identity is readable
  known        a disposable known observation: live_def_check --has ThingDef/Wall exits 0 (vanilla's wall resolves)
  wrong        an intentionally wrong expectation is REJECTED: live_def_check --has ThingDef/<a def nobody defines> exits
               1. Exit 0 is an instrument that says yes to anything; exit 2 one that cannot answer.
A bridge that cannot be taken is no canary verdict: gate() says "bridge not taken" (the round's STOP word) and caches nothing.

CACHE. <RELENTLESS_ROOT>/live/canary.json holds the last verdict with the FINGERPRINT of everything the canaries depend on
(PATH, user, WSL_INTEROP, the interpreter, where python.exe/powershell.exe/wslpath resolve, the bytes of the bridge client,
live_def_check and this file, the running game's start). Healthy is reused for ttl_s, sick for fail_ttl_s, and only while
the fingerprint is the same: a new game, a new PATH or a changed client runs them again. Rules: relentless_rules.json
live.canary {enabled, ttl_s, fail_ttl_s}.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
DEFAULTS = {"enabled": True, "ttl_s": 3600, "fail_ttl_s": 600, "step_max_s": 120}
CHECKS = ("interop", "game", "holder", "bridge", "load", "known", "wrong")
KNOWN = "ThingDef/Wall"
WRONG = "ThingDef/RM_CanaryNoSuchDef_ZZ9"     # no mod defines it: the game must answer no
HELD_BY_US = "bridge held by RELENTLESS"     # `rimflow bridge who`'s line (the driver-lock line above it names RELENTLESS too)
NOT_TAKEN = "bridge not taken"                # relentless_live_round.STOP's word: the round ends, nothing is cached
DEPENDS = (os.path.join(UTILS, "rimbridge_client.py"), os.path.join(UTILS, "live_def_check.py"), os.path.abspath(__file__))


def cfg(r):
    out = dict(DEFAULTS)
    out.update(((r or {}).get("live") or {}).get("canary") or {})
    return out


def path_of(root):
    return os.path.join(root, "live", "canary.json")


def _file_hash(p):
    try:
        with open(p, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]
    except OSError:
        return "unreadable"


def fingerprint(env=None, started=None, which=shutil.which, files=DEPENDS):
    """-> a short hash of what the canaries' verdict depends on, and the parts (shown in canary.json)."""
    env = os.environ if env is None else env
    parts = {"PATH": env.get("PATH", ""), "user": env.get("USER", ""), "uid": os.getuid(),
             "WSL_INTEROP": env.get("WSL_INTEROP", ""), "python": sys.executable,
             "which": {t: which(t, path=env.get("PATH")) for t in ("python.exe", "powershell.exe", "wslpath")},
             "files": {os.path.basename(p): _file_hash(p) for p in files}, "game": started}
    return hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()[:16], parts


def read(root):
    try:
        with open(path_of(root), encoding="utf-8") as f:
            v = json.load(f)
        return v if isinstance(v, dict) else None
    except (OSError, ValueError):
        return None


def write(root, rec):
    os.makedirs(os.path.dirname(path_of(root)), exist_ok=True)
    tmp = path_of(root) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    os.replace(tmp, path_of(root))


def cached(rec, fp, now, c):
    """-> the cached record when it still speaks for this fingerprint, else None."""
    if not rec or rec.get("fingerprint") != fp or not isinstance(rec.get("at"), (int, float)):
        return None
    ttl = c["ttl_s"] if rec.get("ok") else c["fail_ttl_s"]
    return rec if 0 <= now - rec["at"] < ttl else None


def run_checks(fx, c, nonce):
    """-> [(name, ok, why)], stopping at the first failure. fx: relentless_live.Fx (or a fake): game_started, rimflow,
    shell(cmd, timeout) -> (exit, output) run exactly as a proof is. A bridge take refused -> the list ends with
    (NOT_TAKEN, None, why): no verdict either way."""
    out = []
    t = c["step_max_s"]

    def step(name, ok, why=""):
        out.append((name, bool(ok), "" if ok else why))
        return ok

    code, said = fx.shell('python.exe -c "print(\'%s\')"' % nonce, t)
    if not step("interop", code == 0 and nonce in said,
                "python.exe from the proof shell: exit %s: %s" % (code, said.strip()[-200:])):
        return out
    if not step("game", fx.game_started() is not None, "no single running RimWorld whose start time reads"):
        return out
    took = fx.rimflow("bridge", "take", "--idle-ok", "--for", "relentless live canary: read-only harness checks")
    if took.returncode != 0:
        out.append((NOT_TAKEN, None, (took.stderr or took.stdout).strip()[-300:]))
        return out
    try:
        who = fx.rimflow("bridge", "who")
        text = (who.stdout or "") + (who.stderr or "")
        if not step("holder", who.returncode == 0 and HELD_BY_US in text,
                    "bridge who does not name RELENTLESS after our take: %s" % text.strip()[-200:]):
            return out
        client = os.path.join(UTILS, "rimbridge_client.py")
        code, said = fx.shell('python.exe "$(wslpath -w %s)" --timeout 30 --call rimbridge/ping' % client, t)
        if not step("bridge", code == 0, "rimbridge/ping from python.exe: exit %s: %s" % (code, said.strip()[-200:])):
            return out
        code, said = fx.shell('python.exe "$(wslpath -w %s)" --timeout 60 --call jawa/running_mods --json '
                              '\'{"details": false, "assembly": ""}\'' % client, t)
        if not step("load", code == 0 and "ludeon.rimworld" in said.lower(),
                    "jawa/running_mods: exit %s, base game %s: %s" % (
                        code, "named" if "ludeon.rimworld" in said.lower() else "not named", said.strip()[-160:])):
            return out
        check = "python3 %s --has %s" % (os.path.join(UTILS, "live_def_check.py"), "%s")
        code, said = fx.shell(check % KNOWN, t)
        if not step("known", code == 0, "the known observation %s: exit %s (want 0): %s" % (
                KNOWN, code, said.strip()[-200:])):
            return out
        code, said = fx.shell(check % WRONG, t)
        step("wrong", code == 1, "the wrong expectation %s: exit %s (want 1: %s): %s" % (
            WRONG, code, "the instrument says yes to anything" if code == 0 else "it could not answer",
            said.strip()[-200:]))
        return out
    finally:
        fx.rimflow("bridge", "release", "--mine")


def gate(fx, root, r, now=None, env=None, nonce=None):
    """-> None when the canaries are healthy (cached or run now), else why not, starting "canary <name>: " (or
    NOT_TAKEN). Called by relentless_live_round.run_round in the round's own process."""
    c = cfg(r)
    if not c["enabled"]:
        return None
    now = time.time() if now is None else now
    fp, parts = fingerprint(env, fx.game_started())
    hit = cached(read(root), fp, now, c)
    if hit:
        return None if hit["ok"] else hit["why"]
    nonce = nonce or "canary-%d" % int(now)
    checks = run_checks(fx, c, nonce)
    if checks and checks[-1][0] == NOT_TAKEN:
        return "%s: %s" % (NOT_TAKEN, checks[-1][2])
    bad = [x for x in checks if not x[1]]
    ok = not bad and [x[0] for x in checks] == list(CHECKS)
    why = None if ok else "canary %s: %s" % (bad[0][0], bad[0][2]) if bad else "canary: the checks stopped early"
    write(root, {"at": now, "ok": ok, "why": why, "fingerprint": fp, "parts": parts,
                 "checks": [{"name": n, "ok": k, "why": w} for n, k, w in checks]})
    return why


class ShellFx(object):
    """The real effects for the CLI and the round: a proof's shell, relentless_live.Fx's game and rimflow."""

    def __init__(self, fx):
        self.fx = fx

    def game_started(self):
        return self.fx.game_started()

    def rimflow(self, *a, **kw):
        return self.fx.rimflow(*a, **kw)

    def shell(self, cmd, timeout):
        sys.path.insert(0, HERE)
        import model
        try:
            p = subprocess.run(cmd, shell=True, cwd=self.fx.books, capture_output=True, text=True, timeout=timeout,
                               executable="/bin/bash", stdin=subprocess.DEVNULL, env=model.bridge_holder.process_env())
            return p.returncode, (p.stdout or "") + (p.stderr or "")
        except subprocess.TimeoutExpired:
            return None, "timed out after %ds" % timeout


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("show", "run"))
    a = ap.parse_args(argv)
    root = os.environ.get("RELENTLESS_ROOT") or "/home/mandrake/rm/relentless"
    if a.cmd == "show":
        rec = read(root)
        if rec is None:
            print("UNMEASURED: no %s" % path_of(root))
            return 2
        print(json.dumps({k: rec.get(k) for k in ("ok", "why", "fingerprint", "checks")}, indent=1, sort_keys=True))
        print("age %ds" % int(time.time() - rec.get("at", 0)))
        return 0 if rec.get("ok") else 1
    sys.path.insert(0, HERE)
    import relentless_live as L
    with open(os.environ.get("RELENTLESS_RULES") or L.RULES, encoding="utf-8") as f:
        r = json.load(f)
    fx = ShellFx(L.Fx(seat=r.get("seat") or "BENCH"))
    c = cfg(r)
    checks = run_checks(fx, c, "canary-cli-%d" % int(time.time()))
    for n, k, w in checks:
        print("%-8s %s %s" % (n, {True: "ok", False: "FAIL", None: "--"}[k], w))
    return 0 if [x[0] for x in checks] == list(CHECKS) and all(x[1] for x in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
