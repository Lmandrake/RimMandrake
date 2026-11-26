#!/usr/bin/env python3
r"""walk_stage.py - stage a mod's walk on a named game in ONE command, with no model call.

    python3 src/RimMandrake/Utils/walk_stage.py <Mod> --game ArchSmall [--rebuild] [--spec PATH] [--out DIR]
    python3 src/RimMandrake/Utils/walk_stage.py accept <Mod> --game ArchSmall     the item's live acceptance, recorded
    python3 src/RimMandrake/Utils/walk_stage.py verify <Mod>                       read that record (the item's check)

Owner, 2026-11-24, after a model helper took 42 minutes to stage the Gimme Some Slack walk: "Boy it feels like writing a
testing environment should just be a Python call -> BRIDGE -> done in under a minute. What are all the delays as it
works? Why are LLM calls being used to set up a testing environment for GSS?" Page, with where those 42 minutes went:
design/specs/2026-11-26-one-call-walk-stage/boundary.md.

The steps, each timed and printed as one `step` line:
  list      the mod's small list (design/concepts/<Mod>/version/small_list.json: its tier, resolved by modset_builder on
            THIS game's install). A needed mod that is not installed stops here, before the game is touched: exit 1,
            and the line names the mod. Every packageId in the spec's `requires` and `also` must be on the list.
  lock      the game's driver lock (game_lock.run): this process holds it, and it frees when this process ends.
  deploy    deploy_custom_mods.py --mod <Mod> --instance <game>: a plan first; --apply only when the plan differs.
  game      start or reuse: a game that is up, runs this list (jawa/running_mods) and ran no older build, is reused;
            else it is stopped by pid, ModsConfig is written (modset_builder --tier T --apply) and it is launched.
  save      walk_stage.json's `save`: loaded when its header's mods are the list (a list that only adds harness mods,
            such as the zoom mod or Character Editor, is the same list: the load is re-saved once as <save>_SMALL);
            else, or with --rebuild, its `rebuild` steps run and the result is saved as a new keeper.
  hostiles  jawa/kill_hostiles (corpses too), then a read: 0 hostile pawns.
  pause     paused, and the tick does not move over 2 s.
  capture   one picture per station of walk_stage.json, into the capture folder.
  exception the first exception of the session (jawa/first_exception, armed before the load) and of Player.log after a
            launch. One exception is not READY.
The last line is `READY <Mod> on <game>: save <name> | list <n> mods (<tier>) | captures <folder>` with exit 0, or
`NOT READY <Mod> on <game>: <step>: <why>` with exit 1 (a fault), 2 (could not look) or 75 (the game is held).

Bridge calls run in python.exe (RimBridge binds Windows loopback; WSL2 has no route), as a child of this process:
`walk_stage.py --bridge-phase <job.json>`. No step starts a model: nothing here calls claude, codex or an API.
Selftest: selftest_walk_stage.py.
"""
import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RIMFLOW = os.path.join(os.path.dirname(HERE), "rimflow")
for _p in (HERE, RIMFLOW):
    if _p not in sys.path:
        sys.path.insert(0, _p)

EX_OK, EX_FAULT, EX_BLIND, EX_HELD = 0, 1, 2, 75
HARNESS = ("brrainz.rimbridgeserver", "ray1203.simplecamerasetting", "brrainz.cameraplus", "void.charactereditor")
HELD_ENV = "RM_WALK_STAGE_HELD"
# budget: danger=a hung deploy or modset write holds the game's lock for ever; measured need 180 s (deploy, 2026-11-24
# budget: 09:06-09:09 PST); 10x
STEP_S = 1800
# budget: danger=a hung rebuild script holds the game's lock for ever; measured need 175 s (human_review.py --build
# budget: --fresh-map, 2026-11-24 09:17 PST); 10x and more
REBUILD_S = 2400
# budget: danger=a bridge phase that never returns holds the lock for ever; measured need about 60 s (load, sweep, 38
# budget: captures); 10x and more, plus the rebuild's own
PHASE_S = 3600 + REBUILD_S


class Stop(Exception):
    """A step that cannot go on: code is EX_FAULT, EX_BLIND or EX_HELD; step names it."""

    def __init__(self, step, why, code=EX_FAULT):
        super().__init__("%s: %s" % (step, why))
        self.step, self.why, self.code = step, why, code


def norm(p):
    p = str(p or "").strip().lower()
    return p[:-len("_steam")] if p.endswith("_steam") else p


# --- pure parts (selftest_walk_stage.py) ----------------------------------------------------------------------------
def config_path(mod, root=REPO):
    return os.path.join(root, "design", "concepts", mod, "version", "walk_stage.json")


def load_config(mod, path=None, root=REPO):
    """-> the mod's walk_stage.json: {save, rebuild: {steps, save_as}, stations: [{name, rect}]}. Raises Stop."""
    p = path or config_path(mod, root)
    try:
        with open(p, encoding="utf-8") as f:
            c = json.load(f)
    except FileNotFoundError:
        raise Stop("config", "%s has no walk_stage.json (%s): write one (its save, rebuild steps and stations)" % (mod, p))
    except (OSError, ValueError) as e:
        raise Stop("config", "%s: %s" % (p, e), EX_BLIND)
    bad = []
    if not str(c.get("save") or "").strip():
        bad.append("no `save`")
    st = c.get("stations")
    if not isinstance(st, list) or not st:
        bad.append("no `stations`")
    else:
        for i, s in enumerate(st):
            r = s.get("rect") if isinstance(s, dict) else None
            if not (isinstance(s, dict) and str(s.get("name") or "").strip() and isinstance(r, list) and len(r) == 4
                    and all(isinstance(v, int) for v in r) and r[2] > 0 and r[3] > 0):
                bad.append("station %d needs a name and rect [x, z, w, h]" % i)
        names = [s.get("name") for s in st if isinstance(s, dict)]
        dup = sorted({n for n in names if names.count(n) > 1})
        if dup:
            bad.append("station names repeat: %s" % ", ".join(map(str, dup)))
    rb = c.get("rebuild")
    if rb is not None:
        steps = rb.get("steps") if isinstance(rb, dict) else None
        if not isinstance(steps, list) or not steps or not str(rb.get("save_as") or "").strip():
            bad.append("`rebuild` needs steps and save_as")
        else:
            for i, s in enumerate(steps):
                if not isinstance(s, dict) or not (("run" in s and isinstance(s.get("args", []), list)) or
                                                   isinstance(s.get("ticks"), int)):
                    bad.append("rebuild step %d is neither {run, args} nor {ticks}" % i)
    if bad:
        raise Stop("config", "%s: %s" % (p, "; ".join(bad)))
    return c


def list_verdict(spec, ordered, missing, refusals):
    """-> (the list, []) or ([], [one line per fault, each naming its mod]). `ordered`, `missing` and `refusals` are
    modset_builder.resolve_tier's answer for the spec's tier on this game's install."""
    faults = ["%s is not installed on this game (a mod the small list needs)" % m for m in missing or []]
    faults += [str(r) for r in refusals or []]
    have = [norm(x) for x in ordered or []]
    named = list(spec.get("requires") or []) + list((spec.get("also") or {}).keys())
    for pid in named:
        if norm(pid) not in have and not any(norm(pid) in f for f in faults):
            faults.append("%s is named by small_list.json but is not on the resolved list (not installed, or not in "
                          "tier %s)" % (norm(pid), spec.get("tier")))
    return ([], faults) if faults else (have, [])


def save_mods(path, head=4 << 20):
    """-> the packageIds in a save's meta header, in order, or None when the file has no readable header."""
    try:
        with open(path, "rb") as f:
            text = f.read(head).decode("utf-8", "replace")
    except OSError:
        return None
    m = re.search(r"<modIds>(.*?)</modIds>", text, re.S)
    if not m:
        return None
    return [norm(x) for x in re.findall(r"<li>\s*([^<]+?)\s*</li>", m.group(1))]


def save_decision(want, saves_dir, save, rebuild=False):
    """-> (action, name, why). action: load (the save is on the list), load_resave (it lacks only harness mods: load
    it, save it once as <save>_SMALL), or rebuild. A <save>_SMALL already on the list is loaded first."""
    w = set(want)
    if rebuild:
        return "rebuild", None, "asked (--rebuild)"
    for name in (save + "_SMALL", save):
        mods = save_mods(os.path.join(saves_dir, name + ".rws"))
        if mods is None:
            continue
        s = set(mods)
        if s == w:
            return "load", name, "its header holds the list (%d mods)" % len(w)
        lack, more = w - s, s - w
        if not more and lack and all(m in HARNESS for m in lack):
            return "load_resave", name, "its header lacks only harness mods: %s" % ", ".join(sorted(lack))
        why = "the header of %s.rws differs from the list: lacks %s; has also %s" % (
            name, ", ".join(sorted(lack)) or "none", ", ".join(sorted(more)) or "none")
    else:
        why = locals().get("why") or "%s.rws is not in %s" % (save, saves_dir)
    return "rebuild", None, why


def userdata(letter):
    """-> a game's save-data folder (Saves, JawaBenchReviewSigns, Player.log of a named game)."""
    import game_instance as G
    return os.path.dirname(G.a_saves_dir()) if letter == "a" else G.data_dir(letter)


def bring_save(names, here, others, copy=shutil.copy2):
    """Copy the first of `names` that is in no Saves folder of `here` but in one of `others` (other games' save-data
    folders), with its sign sidecar (JawaBenchReviewSigns/<name>.txt: the station labels). -> [what was copied]. A save
    already here is never overwritten."""
    done = []
    for name in names:
        if os.path.exists(os.path.join(here, "Saves", name + ".rws")):
            return done
        for o in others:
            src = os.path.join(o, "Saves", name + ".rws")
            if os.path.exists(src):
                os.makedirs(os.path.join(here, "Saves"), exist_ok=True)
                copy(src, os.path.join(here, "Saves", name + ".rws"))
                done.append(src)
                side = os.path.join(o, "JawaBenchReviewSigns", name + ".txt")
                if os.path.exists(side) and not os.path.exists(os.path.join(here, "JawaBenchReviewSigns", name + ".txt")):
                    os.makedirs(os.path.join(here, "JawaBenchReviewSigns"), exist_ok=True)
                    copy(side, os.path.join(here, "JawaBenchReviewSigns", name + ".txt"))
                    done.append(side)
                return done
    return done


def restart_why(want, running, deployed_changed):
    """-> None when a running game can be reused, else why it restarts. running: its packageIds (None: down)."""
    if running is None:
        return "the game is down"
    if deployed_changed:
        return "the deploy wrote new files: a running game keeps the old defs and DLL"
    r, w = [norm(x) for x in running], list(want)
    if set(r) != set(w):
        return "it runs another list: lacks %s; has also %s" % (", ".join(sorted(set(w) - set(r))) or "none",
                                                               ", ".join(sorted(set(r) - set(w))) or "none")
    return None


def first_log_exception(text):
    """-> the first exception line of a Player.log text, or None."""
    for line in text.splitlines():
        if re.search(r"\b\w*Exception\b(:| in | was thrown)", line) and "LogException" not in line:
            return line.strip()
    return None


def summary(rows):
    return "\n".join("step %-9s %6.1fs  %s" % (r["step"], r["s"], r["what"]) for r in rows)


# --- the WSL orchestrator ------------------------------------------------------------------------------------------
def _now():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


class Run:
    def __init__(self, mod, game, out, spec_path=None, rebuild=False, config=None):
        self.mod, self.game, self.out = mod, game, out
        self.spec_path, self.rebuild, self.config_path = spec_path, rebuild, config
        self.rows = []
        self.t = time.time()

    def row(self, step, what):
        now = time.time()
        self.rows.append({"step": step, "s": round(now - self.t, 1), "what": what})
        self.t = now
        print("step %-9s %6.1fs  %s" % (step, self.rows[-1]["s"], what), flush=True)

    def sh(self, step, argv, timeout=STEP_S):
        try:
            p = subprocess.run(argv, cwd=REPO, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            raise Stop(step, "%s did not end in %d s (the hang guard)" % (" ".join(argv[:3]), timeout), EX_BLIND)
        return p.returncode, (p.stdout or "") + (p.stderr or "")

    # list ---------------------------------------------------------------------------------------------------------
    def the_list(self):
        import small_list as SL
        import modset_builder as MB
        try:
            spec = json.load(open(self.spec_path, encoding="utf-8")) if self.spec_path else SL.load_spec(REPO, self.mod)
        except (OSError, ValueError, SL.CouldNotLook) as e:
            raise Stop("list", "the small list cannot be read: %s" % e, EX_BLIND)
        if not spec or not str(spec.get("tier") or "").strip():
            raise Stop("list", "%s has no small_list.json with a tier (%s)" % (self.mod, SL.spec_path(REPO, self.mod)))
        try:
            installed = SL.scan()
        except SL.CouldNotLook as e:
            raise Stop("list", "the installed mods cannot be read: %s" % e, EX_BLIND)
        if MB.tier_def(spec["tier"], installed) is None:
            raise Stop("list", "modset_builder has no tier %s" % spec["tier"])
        ordered, missing, refusals = MB.resolve_tier(spec["tier"], installed)
        want, faults = list_verdict(spec, ordered, missing, refusals)
        if faults:
            raise Stop("list", "; ".join(faults))
        self.spec, self.want = spec, want
        self.row("list", "%d mods, tier %s" % (len(want), spec["tier"]))

    # deploy -------------------------------------------------------------------------------------------------------
    def deploy(self):
        base = [sys.executable, os.path.join(HERE, "deploy_custom_mods.py"), "--mod", self.mod, "--instance", self.game]
        rc, text = self.sh("deploy", base)
        if rc == 0 and "Everything in sync" in text:
            self.deployed_changed = False
            self.row("deploy", "in sync, nothing written")
            return
        if rc not in (0, 1):
            raise Stop("deploy", "the plan failed (exit %d): %s" % (rc, text.strip().splitlines()[-1:] or ""))
        rc, text = self.sh("deploy", base + ["--apply"])
        if "locked by the running" in text:
            self.stop_game("the deploy needs the DLL the game holds")
            rc, text = self.sh("deploy", base + ["--apply"])
        if rc != 0:
            raise Stop("deploy", "--apply failed (exit %d): %s" % (rc, " | ".join(text.strip().splitlines()[-3:])))
        self.deployed_changed = True
        self.row("deploy", "applied")

    # game ---------------------------------------------------------------------------------------------------------
    def gi(self, *args, timeout=STEP_S):
        return self.sh("game", [sys.executable, os.path.join(HERE, "game_instance.py")] + list(args), timeout=timeout)

    def is_up(self):
        rc, text = self.gi("pid", self.letter)
        return rc == 0 and text.strip().isdigit()

    def stop_game(self, why):
        if not self.is_up():
            return
        rc, text = self.gi("stop", "--instance", self.letter, "--for", "walk_stage %s: %s" % (self.mod, why))
        if rc != 0:
            raise Stop("game", "the stop failed (exit %d): %s" % (rc, text.strip()), EX_BLIND if rc == 2 else EX_FAULT)
        self.row("stop", "stopped: %s" % why)

    def modsconfig(self):
        import game_paths as GP
        import xml.etree.ElementTree as ET
        try:
            a = ET.parse(GP.MODS_CONFIG).getroot().find("activeMods")
            return [norm(li.text) for li in a.findall("li")] if a is not None else []
        except (OSError, ET.ParseError):
            return None

    def game_up(self):
        running = None
        if self.is_up():
            running = self.phase({"do": "probe"}).get("running")
            if running is None:
                raise Stop("game", "the game is up and its running mods cannot be read through the bridge", EX_BLIND)
        why = restart_why(self.want, running, self.deployed_changed)
        if why is None:
            self.launched = False
            self.row("game", "reused: up on the list")
            return
        self.stop_game(why)
        if self.modsconfig() != list(self.want):
            rc, text = self.sh("game", [sys.executable, os.path.join(HERE, "modset_builder.py"), "--tier",
                                        self.spec["tier"], "--apply"])
            got = self.modsconfig()
            if rc != 0 or got is None or set(got) != set(self.want):
                raise Stop("game", "ModsConfig is not the list after modset_builder --apply (exit %d): %s" % (
                    rc, " | ".join(text.strip().splitlines()[-3:])))
        import game_instance as G
        self.log_mark = 0
        rc, text = self.gi("launch", self.letter, "--wait", timeout=STEP_S + G.WAIT_S)
        if rc != 0:
            raise Stop("game", "the launch failed (exit %d): %s" % (rc, text.strip()))
        self.launched = True
        self.row("game", "launched (%s): %s" % (why, text.strip().splitlines()[-1]))

    # bridge phase -------------------------------------------------------------------------------------------------
    def phase(self, job):
        """Run one bridge job in python.exe -> its result dict. Raises Stop on a phase that did not answer."""
        os.makedirs(self.out, exist_ok=True)
        jf = os.path.join(self.out, "job_%s.json" % job["do"])
        rf = os.path.join(self.out, "result_%s.json" % job["do"])
        job = dict(job, result=_win(rf), repo=_win(REPO), out=_win(self.out))
        with open(jf, "w", encoding="utf-8") as f:
            json.dump(job, f, indent=1)
        if os.path.exists(rf):
            os.remove(rf)
        exe = shutil.which("python.exe")
        if not exe:
            raise Stop(job["do"], "no python.exe on PATH: the bridge is reachable only from Windows Python", EX_BLIND)
        try:
            p = subprocess.run([exe, _win(os.path.abspath(__file__)), "--bridge-phase", _win(jf)], cwd=REPO,
                               capture_output=True, text=True, timeout=PHASE_S)
        except subprocess.TimeoutExpired:
            raise Stop(job["do"], "the bridge phase did not end in %d s (the hang guard)" % PHASE_S, EX_BLIND)
        with open(os.path.join(self.out, "phase_%s.log" % job["do"]), "w", encoding="utf-8") as f:
            f.write((p.stdout or "") + (p.stderr or ""))
        try:
            with open(rf, encoding="utf-8") as f:
                r = json.load(f)
        except (OSError, ValueError):
            raise Stop(job["do"], "the bridge phase wrote no result (exit %d): %s" % (
                p.returncode, " | ".join(((p.stdout or "") + (p.stderr or "")).strip().splitlines()[-4:])), EX_BLIND)
        return r

    def stage(self, cfg):
        import game_instance as G
        here = userdata(self.letter)
        saves = os.path.join(here, "Saves")
        others = [userdata(n) for n in G.instances() if n != self.letter]
        got = bring_save([cfg["save"] + "_SMALL", cfg["save"]], here, others)
        if got:
            self.row("bring", "copied from the other game: %s" % ", ".join(_win(x) for x in got))
        action, name, why = save_decision(self.want, saves, cfg["save"], self.rebuild)
        if action == "rebuild" and not cfg.get("rebuild"):
            raise Stop("save", "%s cannot be loaded (%s) and walk_stage.json has no rebuild steps" % (cfg["save"], why))
        self.row("decide", "%s %s: %s" % (action, name or "", why))
        job = {"do": "stage", "action": action, "save": name, "resave": (name or "") + "_SMALL",
               "rebuild": cfg.get("rebuild"), "stations": cfg["stations"], "mod": self.mod,
               "save_as": "%s_%s" % ((cfg.get("rebuild") or {}).get("save_as") or cfg["save"], _now())}
        r = self.phase(job)
        self.phase_result = r
        for s in r.get("steps") or []:
            self.row(s["step"], s["what"])
        if not r.get("ok"):
            raise Stop(r.get("step") or "stage", r.get("why") or "the bridge phase did not say why",
                       EX_BLIND if r.get("blind") else EX_FAULT)
        self.result = r
        if action != "load":                    # a new keeper: on disk, under its name, before READY names it
            f = os.path.join(saves, "%s.rws" % r.get("save"))
            for _ in range(30):
                if os.path.exists(f) and os.path.getsize(f) > 0:
                    break
                time.sleep(1)
            else:
                raise Stop("save", "save_game answered, but %s is not on disk" % f)
        if getattr(self, "launched", False):
            text = ""
            try:
                text = open(G.log_path(self.letter) if self.letter != "a" else _a_log(), encoding="utf-8",
                            errors="replace").read()
            except OSError:
                pass
            ex = first_log_exception(text)
            if ex:
                raise Stop("exception", "the cold load logged an exception: %s" % ex)
        return r


def _win(p):
    """A WSL path in its Windows spelling (python.exe reads it): /mnt/<d>/... -> D:\\..., the clone -> \\\\wsl.localhost\\..."""
    if not p.startswith("/"):
        return p
    import game_paths as GP
    if p.startswith("/mnt/"):
        return GP.wsl_to_win(p)
    try:
        r = subprocess.run(["wslpath", "-w", p], capture_output=True, text=True, timeout=60)  # budget: danger=a hung wslpath; measured need under 0.1 s
    except subprocess.TimeoutExpired:
        raise Stop("path", "wslpath -w %s did not answer" % p, EX_BLIND)
    if r.returncode != 0 or not r.stdout.strip():
        raise Stop("path", "wslpath -w %s: %s" % (p, (r.stderr or "").strip()), EX_BLIND)
    return r.stdout.strip()


def _a_log():
    import game_paths as GP
    return GP.PLAYER_LOG


AIMED_ENV = "RM_WALK_STAGE_AIMED"
LIST_ENV = "RM_WALK_STAGE_LIST"


def stage_main(a):
    """Three processes, one command: (1) aim this shell at the game and re-exec; (2) the list check, before the game is
    touched, then game_lock.run of (3) the staging itself, which holds the game's lock for its life."""
    import game_lock
    import game_names
    try:
        letter = game_lock.check_game(a.game)
    except Exception as e:  # noqa: BLE001 - an unknown name is refused by name
        print("NOT READY %s on %s: game: %s" % (a.mod, a.game, e))
        return EX_FAULT
    game = game_names.show(letter)
    if os.environ.get(AIMED_ENV) != letter:
        env = game_lock.aim_env(letter, dict(os.environ))
        env[AIMED_ENV] = letter
        env.pop(LIST_ENV, None)
        env.pop(HELD_ENV, None)
        sys.stdout.flush()
        os.execve(sys.executable, [sys.executable, os.path.abspath(__file__)] + sys.argv[1:], env)
    out = a.out or os.path.join(_showings(), "walk_stage_%s_%s" % (a.mod, _now()))
    R = Run(a.mod, game, out, a.spec, a.rebuild, a.config)
    R.letter = letter
    try:
        cfg = load_config(a.mod, a.config)
        if os.environ.get(HELD_ENV) != "1":
            R.the_list()
            os.environ[LIST_ENV] = json.dumps({"want": R.want, "spec": R.spec, "rows": R.rows})
            os.environ[HELD_ENV] = "1"
            rc = game_lock.run(letter, "walk_stage %s (one-call walk staging)" % a.mod,
                               [sys.executable, os.path.abspath(__file__)] + sys.argv[1:] + ["--out", out])
            if rc == game_lock.EX_HELD or rc == game_lock.EX_HIS:
                print("NOT READY %s on %s: lock: the game is held (game_lock.py query %s); take another game" % (
                    a.mod, game, game), flush=True)
                return EX_HELD
            return rc
        got = json.loads(os.environ[LIST_ENV])
        R.want, R.spec, R.rows = got["want"], got["spec"], got["rows"]
        R.row("lock", "held: %s" % game)
        R.deploy()
        R.game_up()
        r = R.stage(cfg)
    except Stop as e:
        fe = (getattr(R, "phase_result", None) or {}).get("first_exception")
        if fe:
            print("first exception: %s" % fe, flush=True)
        print("NOT READY %s on %s: %s: %s" % (a.mod, game, e.step, e.why), flush=True)
        _write_record(out, R, ok=False, why="%s: %s" % (e.step, e.why))
        return e.code
    total = sum(x["s"] for x in R.rows)
    _write_record(out, R, ok=True, result=r)
    print("READY %s on %s: save %s | list %d mods (%s) | captures %s | %.0f s" % (
        a.mod, game, r.get("save"), len(R.want), R.spec["tier"], _win(out), total), flush=True)
    return EX_OK


def _showings():
    from rmpaths import rm_str
    return rm_str("showings")


def _write_record(out, R, ok, result=None, why=None):
    os.makedirs(out, exist_ok=True)
    rec = {"mod": R.mod, "game": R.game, "ok": ok, "why": why, "rows": R.rows, "list": getattr(R, "want", None),
           "tier": (getattr(R, "spec", None) or {}).get("tier"), "result": result,
           "at": datetime.datetime.now().astimezone().isoformat(timespec="seconds")}
    with open(os.path.join(out, "walk_stage.json"), "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1, default=str)


# --- the bridge phase (python.exe) ---------------------------------------------------------------------------------
def bridge_phase(job_path):
    job = json.load(open(job_path, encoding="utf-8"))
    res = {"ok": False, "steps": []}
    t = [time.time()]

    def step(name, what):
        now = time.time()
        res["steps"].append({"step": name, "s": round(now - t[0], 1), "what": what})
        t[0] = now

    def done():
        with open(job["result"], "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)

    try:
        import rimbridge_client as rbc
        host, port, token = rbc.resolve_endpoint()
        B = rbc.RimBridge(host=host, port=port, token=token, timeout=600.0).connect()
        call = lambda tool, **kw: B.call(tool, kw, check=False) or {}  # noqa: E731
        if job["do"] == "probe":
            rm = call("jawa/running_mods", details=False)
            mods = rm.get("packageIds")
            if isinstance(mods, list):
                res["running"] = [norm(m.get("packageId") if isinstance(m, dict) else m) for m in mods]
            res["ok"] = res.get("running") is not None
            res["raw_keys"] = sorted(rm)
            return done()
        _stage(job, call, res, step)
    except Exception as e:  # noqa: BLE001 - every failure is said in the result, never lost
        res.update(ok=False, blind=True, step=res.get("step") or "bridge", why="%s: %s" % (type(e).__name__, e))
    done()


def _stage(job, call, res, step):
    def fail(s, why, blind=False):
        res.update(ok=False, step=s, why=why, blind=blind)
        try:                                    # NOT READY prints the session's first exception beside its cause
            first = ((call("jawa/first_exception").get("session") or {}).get("firstException") or {})
            res["first_exception"] = str(first.get("text") or "") or None
        except Exception:  # noqa: BLE001 - the cause above is the answer; this is a courtesy read
            pass
        raise _Done()

    try:
        call("jawa/first_exception", action="arm", label="walk_stage %s" % job["mod"])
        act = job["action"]
        if act in ("load", "load_resave"):
            r = call("rimworld/load_game_ready", saveName=job["save"])
            if r.get("success") is False:
                fail("save", "load_game_ready %s refused: %s" % (job["save"], r.get("message") or r.get("error")))
            name = job["save"]
            step("load", "loaded %s" % name)
        else:
            name = _rebuild(job, call, step, fail)
        hs = (call("jawa/companion_handshake").get("game") or {})
        if hs.get("programState") != "Playing":
            fail("save", "after the load the game reads %s, not Playing" % hs.get("programState"), blind=True)
        res["handshake_save"] = hs.get("save")
        if act != "rebuild" and hs.get("save") != job["save"]:
            fail("save", "the bridge reads save %r loaded, not %s" % (hs.get("save"), job["save"]))
        k = call("jawa/kill_hostiles", destroyCorpses=True)
        if k.get("success") is False:
            fail("hostiles", "kill_hostiles refused: %s" % (k.get("message") or k.get("error")))
        ps = call("jawa/list_pawns", limit=2000).get("pawns")
        if not isinstance(ps, list):
            fail("hostiles", "list_pawns gave no list", blind=True)
        hostile = [p for p in ps if p.get("hostile") and not p.get("dead")]
        res["hostiles"] = len(hostile)
        if hostile:
            fail("hostiles", "%d hostile pawn(s) left after kill_hostiles: %s" % (
                len(hostile), [p.get("label") or p.get("def") for p in hostile[:5]]))
        step("hostiles", "0 hostile pawns (%s killed)" % k.get("killed"))
        call("rimworld/pause_game", pause=True)
        a = call("rimworld/get_game_info").get("ticksGame")
        time.sleep(2)
        b = call("rimworld/get_game_info").get("ticksGame")
        if a is None or a != b:
            fail("pause", "ticksGame %s -> %s over 2 s" % (a, b), blind=a is None)
        res["tick"] = b
        step("pause", "paused at tick %s" % b)
        if act == "load_resave" or act == "rebuild":
            keep = job["resave"] if act == "load_resave" else job["save_as"]
            name = _keeper(call, keep, fail) or name
            step("save", "saved %s" % name)
        res["save"] = name
        call("jawa/clear_ui")
        shots, missing = {}, []
        for s in job["stations"]:
            x, z, w, h = s["rect"]
            r = call("rimworld/screenshot_cell_rect", x=x, z=z, width=w, height=h, paddingCells=1,
                     fileName="walkstage_%s_%d" % (re.sub(r"\W+", "_", s["name"]), time.time_ns() // 1000000),
                     suppressMessage=True)
            src = r.get("path") or r.get("filePath")
            dst = os.path.join(job["out"], re.sub(r"[^\w.-]+", "_", s["name"]) + (os.path.splitext(src)[1] if src else ".png"))
            if src and os.path.exists(src):
                shutil.copyfile(src, dst)
                shots[s["name"]] = dst
            else:
                missing.append(s["name"])
        res["captures"] = shots
        if missing:
            fail("capture", "%d station(s) gave no picture: %s" % (len(missing), ", ".join(missing[:6])), blind=True)
        step("capture", "%d stations captured" % len(shots))
        c = call("rimworld/get_game_info").get("ticksGame")
        if c != b:
            fail("pause", "the game moved during the captures: tick %s -> %s" % (b, c))
        fe = call("jawa/first_exception")
        win = fe.get("window") or {}
        first = win.get("firstException") or {}
        res["exception_state"] = fe.get("state")
        if fe.get("state") == "SEEN" and first:
            fail("exception", "%s (tick %s)" % (first.get("text"), first.get("tick")))
        if fe.get("state") not in ("NONE_SEEN", "SEEN"):
            fail("exception", "the first-exception tap reads %s: %s" % (fe.get("state"), fe.get("blind")), blind=True)
        step("exception", "none seen since the load")
        res["ok"] = True
    except _Done:
        pass


class _Done(Exception):
    pass


def _rebuild(job, call, step, fail):
    rb = job["rebuild"]
    for s in rb["steps"]:
        if "ticks" in s:
            call("rimworld/step_game_ticks", ticks=int(s["ticks"]))
            step("rebuild", "%d ticks" % s["ticks"])
            continue
        argv = [sys.executable, os.path.join(job["repo"], s["run"])] + [a.replace("{out}", job["out"]) for a in s.get("args", [])]
        try:
            p = subprocess.run(argv, cwd=job["repo"], capture_output=True, text=True, timeout=REBUILD_S)
        except subprocess.TimeoutExpired:
            fail("rebuild", "%s did not end in %d s (the hang guard)" % (s["run"], REBUILD_S), blind=True)
        with open(os.path.join(job["out"], "rebuild_%s.log" % os.path.basename(s["run"])), "w", encoding="utf-8") as f:
            f.write((p.stdout or "") + (p.stderr or ""))
        if p.returncode != 0:
            fail("rebuild", "%s exit %d: %s" % (s["run"], p.returncode, " | ".join(
                ((p.stdout or "") + (p.stderr or "")).strip().splitlines()[-3:])))
        step("rebuild", "%s ok" % os.path.basename(s["run"]))
    return job["save_as"]


def _keeper(call, name, fail):
    r = call("rimworld/save_game", saveName=name)
    if r.get("success") is False:
        fail("save", "save_game %s refused: %s" % (name, r.get("message") or r.get("error")))
    return name


# --- the item's acceptance -------------------------------------------------------------------------------------------
ACCEPT = "walk_stage_accept.json"


def _children_claude(root_pid):
    """-> pids of claude processes that descend from root_pid (read from /proc)."""
    kids, found = {}, []
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        try:
            with open("/proc/%s/stat" % d) as f:
                st = f.read()
            comm = st[st.index("(") + 1:st.rindex(")")]
            ppid = int(st[st.rindex(")") + 2:].split()[1])
            with open("/proc/%s/cmdline" % d, "rb") as f:
                cmd = f.read().replace(b"\0", b" ").decode("utf-8", "replace")
        except (OSError, ValueError, IndexError):
            continue
        kids.setdefault(ppid, []).append((int(d), comm, cmd))
    todo = [root_pid]
    while todo:
        p = todo.pop()
        for pid, comm, cmd in kids.get(p, []):
            first = os.path.basename(cmd.split(" ", 1)[0]) if cmd else ""
            if comm == "claude" or first in ("claude", "claude.exe", "codex", "codex.exe"):
                found.append((pid, cmd))
            todo.append(pid)
    return found


def _watched(argv, log):
    """Run argv; poll its process tree for a model process every 0.2 s. -> (exit code, output, [model processes])."""
    seen = {}
    with open(log, "w", encoding="utf-8") as f:
        p = subprocess.Popen(argv, cwd=REPO, stdout=f, stderr=subprocess.STDOUT, text=True)
        while p.poll() is None:
            for pid, cmd in _children_claude(p.pid):
                seen[pid] = cmd
            time.sleep(0.2)
    return p.returncode, open(log, encoding="utf-8", errors="replace").read(), sorted(seen.items())


def accept_main(a):
    """The item's acceptance on a free game: a planted missing mod is refused by name; the real run is READY; then a
    fresh bridge read shows the save loaded, paused and 0 hostiles; a capture file per station; no model process."""
    import tempfile
    rec = {"mod": a.mod, "game": a.game, "at": datetime.datetime.now().astimezone().isoformat(timespec="seconds")}
    import small_list as SL
    spec = SL.load_spec(REPO, a.mod)
    planted = dict(spec, requires=list(spec.get("requires") or []) + ["mandrake.rm.walkstageplantedmissing"])
    d = tempfile.mkdtemp(prefix="walk_stage_accept_")
    sp = os.path.join(d, "small_list.json")
    json.dump(planted, open(sp, "w"))
    me = [sys.executable, os.path.abspath(__file__), a.mod, "--game", a.game]
    rc, text, model = _watched(me + ["--spec", sp, "--out", os.path.join(d, "planted")], os.path.join(d, "planted.log"))
    rec["planted"] = {"exit": rc, "names_mod": "mandrake.rm.walkstageplantedmissing" in text.splitlines()[-1] if text else False,
                      "last": (text.strip().splitlines() or [""])[-1], "model_processes": model}
    rc, text, model = _watched(me + (["--rebuild"] if a.rebuild else []), os.path.join(d, "real.log"))
    last = (text.strip().splitlines() or [""])[-1]
    if rc == EX_HELD:                           # the game was taken between the caller's look and the claim: no record
        print("ACCEPT %s: COULD NOT RUN, %s is held: %s" % (a.mod, a.game, last))
        return EX_HELD
    m = re.search(r"captures (\S+)", last)
    out = m.group(1) if m else None
    rec["real"] = {"exit": rc, "last": last, "model_processes": model, "steps": [l for l in text.splitlines() if l.startswith("step ")]}
    if out:
        import game_paths as GP
        wout = GP.win_to_wsl(out)
        try:
            r = json.load(open(os.path.join(wout, "walk_stage.json"), encoding="utf-8"))
            cfg = load_config(a.mod)
            caps = (r.get("result") or {}).get("captures") or {}
            rec["captures"] = {s["name"]: (caps.get(s["name"]) if caps.get(s["name"]) and os.path.exists(
                GP.win_to_wsl(caps[s["name"]])) else None) for s in cfg["stations"]}
            rec["record"] = os.path.join(out, "walk_stage.json")
        except (OSError, ValueError, Stop) as e:
            rec["captures_error"] = str(e)
        # the fresh read, a separate process: save, paused, hostiles
        R = Run(a.mod, a.game, wout)
        import game_lock
        R.letter = game_lock.check_game(a.game)
        try:
            rec["read"] = game_lock_run_read(R)
        except Stop as e:
            rec["read"] = {"error": str(e)}
    rec["verdict"] = verdict(rec, load_config(a.mod))
    path = os.path.join(REPO, "design", "concepts", a.mod, "version", ACCEPT)
    json.dump(rec, open(path, "w", encoding="utf-8"), indent=1, default=str)
    print("ACCEPT %s: %s (%s)" % (a.mod, rec["verdict"]["result"], path))
    for k, v in rec["verdict"]["rows"]:
        print("  %-28s %s" % (k, v))
    return 0 if rec["verdict"]["result"] == "PASS" else 1


def game_lock_run_read(R):
    """A fresh bridge read under the game's lock: {save, programState, paused, hostiles}."""
    import game_lock
    job = os.path.join(R.out, "job_read.json")
    rf = os.path.join(R.out, "result_read.json")
    json.dump({"do": "read", "result": _win(rf)}, open(job, "w"))
    if os.path.exists(rf):
        os.remove(rf)
    rc = game_lock.run(R.letter, "walk_stage accept: a fresh read", [shutil.which("python.exe"), _win(os.path.abspath(__file__)),
                                                                     "--bridge-phase", _win(job)])
    try:
        return dict(json.load(open(rf, encoding="utf-8")), exit=rc)
    except (OSError, ValueError):
        raise Stop("read", "the fresh read wrote nothing (exit %s)" % rc, EX_BLIND)


def verdict(rec, cfg):
    p, r, rd = rec.get("planted") or {}, rec.get("real") or {}, rec.get("read") or {}
    caps = rec.get("captures") or {}
    rows = [
        ("planted_exits_nonzero", p.get("exit") not in (None, 0)),
        ("planted_names_the_mod", bool(p.get("names_mod"))),
        ("real_exits_0_ready", r.get("exit") == 0 and str(r.get("last", "")).startswith("READY")),
        ("read_save_loaded", bool(rd.get("save")) and rd.get("programState") == "Playing"),
        ("read_paused", rd.get("paused") is True),
        ("read_zero_hostiles", rd.get("hostiles") == 0),
        ("capture_per_station", bool(caps) and len(caps) == len(cfg["stations"]) and all(caps.values())),
        ("no_model_process", not p.get("model_processes") and not r.get("model_processes")),
    ]
    return {"result": "PASS" if all(v for _, v in rows) else "FAIL", "rows": [(k, "PASS" if v else "FAIL") for k, v in rows]}


def verify_main(a):
    """The item's check: the committed acceptance record reads PASS, and its captures exist on this machine."""
    path = os.path.join(REPO, "design", "concepts", a.mod, "version", ACCEPT)
    try:
        rec = json.load(open(path, encoding="utf-8"))
    except FileNotFoundError:
        print("FAIL: no acceptance record %s (run: walk_stage.py accept %s --game <free game>)" % (path, a.mod))
        return 1
    except (OSError, ValueError) as e:
        print("COULD NOT LOOK: %s: %s" % (path, e))
        return 2
    v = verdict(rec, load_config(a.mod))
    import game_paths as GP
    gone = [n for n, c in (rec.get("captures") or {}).items() if not c or not os.path.exists(GP.win_to_wsl(c))]
    ok = v["result"] == "PASS" and not gone
    print("%s %s: acceptance of %s%s" % ("PASS" if ok else "FAIL", a.mod, rec.get("at"),
                                        "; captures missing on disk: %s" % gone[:5] if gone else ""))
    return 0 if ok else 1


def _read_phase(job, call, res):
    hs = call("jawa/companion_handshake").get("game") or {}
    a = call("rimworld/get_game_info").get("ticksGame")
    time.sleep(2)
    b = call("rimworld/get_game_info").get("ticksGame")
    ps = call("jawa/list_pawns", limit=2000).get("pawns")
    res.update(ok=True, save=hs.get("save"), programState=hs.get("programState"), paused=(a is not None and a == b),
               tick=b, hostiles=len([p for p in ps if p.get("hostile") and not p.get("dead")]) if isinstance(ps, list) else None)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["--bridge-phase"]:
        job = json.load(open(argv[1], encoding="utf-8"))
        if job["do"] == "read":
            import rimbridge_client as rbc
            res = {}
            try:
                host, port, token = rbc.resolve_endpoint()
                B = rbc.RimBridge(host=host, port=port, token=token, timeout=600.0).connect()
                _read_phase(job, lambda tool, **kw: B.call(tool, kw, check=False) or {}, res)
            except Exception as e:  # noqa: BLE001
                res.update(ok=False, why="%s: %s" % (type(e).__name__, e))
            json.dump(res, open(job["result"], "w"), default=str)
            return 0
        bridge_phase(argv[1])
        return 0
    if argv[:1] in (["accept"], ["verify"]):
        ap = argparse.ArgumentParser(prog="walk_stage.py " + argv[0])
        ap.add_argument("mod")
        ap.add_argument("--game", default="ArchSmall")
        ap.add_argument("--rebuild", action="store_true")
        a = ap.parse_args(argv[1:])
        return accept_main(a) if argv[0] == "accept" else verify_main(a)
    ap = argparse.ArgumentParser(prog="walk_stage.py", description=__doc__.split("\n")[0])
    ap.add_argument("mod")
    ap.add_argument("--game", required=True, help="ArchBig or ArchSmall (any letter case)")
    ap.add_argument("--rebuild", action="store_true", help="rebuild the walk map even when the save is on the list")
    ap.add_argument("--spec", default=None, help="a small_list.json to read instead of the mod's own (a test plants here)")
    ap.add_argument("--config", default=None, help="a walk_stage.json to read instead of the mod's own")
    ap.add_argument("--out", default=None, help="the capture folder (default: <data root>/showings/walk_stage_<Mod>_<time>)")
    return stage_main(ap.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
