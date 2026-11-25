#!/usr/bin/env python3
# selftest-timeout: 3600   (about seventeen harness builds of ~3 min each through winbuild: the clean core and one per C# plant)
"""Selftest: the calm profile of BRIDGE v2.0 - named, versioned profiles, a control's status against its certificate line, the
record and its put-back, the lease, the scene's exceptions, the breach log and one driver (JawaBenchCalmProfileCore.cs; the Verse
half JawaBenchCalmProfile.cs and its two calls in JawaBenchCalm.cs; the certificate lines calm_profile.py).
Item RIMMANDRAKE_BUILD_CALM_PROFILE_BREACH_LOG_AND_LEASE. Page: design/specs/2026-11-23-bridge-v2/boundary.md §CALM PROFILE; one
test per promise there, 11 checks:

  1 a control reads HELD only with its certificate line      2 a scene's exception opens one gate for one named event
  3 a hold on needs is two entries                            4 the put-back runs in reverse order with read-back
  5 a lease that ran out puts back                            6 a value that could not be put back is named
  7 a destructive control is refused under CAMPAIGN only      8 attempts stopped and scheduling switched off are two numbers
  9 a second driver is an APPARATUS breach                   10 unknown profile keys are refused
 11 a NOT UNDONE control is listed as such

Each check is the C# unit of its promise (CalmProfileSelfTest, on the PRODUCTION core) and the wiring of the Verse half that makes the
rule reachable in the game. Each plant breaks one rule of a COPY of a core and must turn its named check red.
An offline test proves the rules, never that a hook is connected in the game: the tap certificate and prove_calm_profile.py do that.
No game, no bridge. Without dotnet.exe it FAILS as UNMEASURED.
Run: python3 src/RimMandrake/bridgetools/selftest_calm_profile.py [--no-plants]"""
import importlib.util
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
sys.path.insert(0, HERE)

CS = os.path.join(HERE, "JawaBench.BridgeTools")
CORE = "JawaBenchCalmProfileCore.cs"
VERSE = "JawaBenchCalmProfile.cs"
CALM = "JawaBenchCalm.cs"
PY = os.path.join(HERE, "calm_profile.py")
PROJ = os.path.join(HERE, "CalmProfileSelfTest", "CalmProfileSelfTest.csproj")
N_UNITS = 11                    # fewer printed = the harness did not run whole


class Unmeasured(Exception):
    pass


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def units(core_text):
    """Build the harness with this profile core, run it -> {unit: "ok" | "FAIL why"}."""
    import winbuild
    d = tempfile.mkdtemp(prefix="CalmProfileCore_", dir=winbuild.BUILD_ROOT)
    log = os.path.join(winbuild.BUILD_ROOT, "selftest_calm_profile.log")
    try:
        with open(os.path.join(d, CORE), "w", encoding="utf-8") as f:
            f.write(core_text)
        with open(log, "w") as lf:
            sys.stdout.flush()
            saved = os.dup(1)
            os.dup2(lf.fileno(), 1)
            try:
                rc, rec = winbuild.stage_build(PROJ, stage_name="CalmProfileSelfTest", extra=("-p:CoreDir=" + winbuild.win(d) + "\\",))
            finally:
                sys.stdout.flush()
                os.dup2(saved, 1)
                os.close(saved)
    except (OSError, SystemExit) as e:
        raise Unmeasured("the harness could not be built: %s" % e)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    if rc:
        raise Unmeasured("the harness build failed (rc %s), log %s" % (rc, log))
    dll = winbuild.staged_win(rec, os.path.dirname(PROJ)) + "\\bin\\Release\\net8.0\\CalmProfileSelfTest.dll"
    pr = winbuild.run_interop_captured([winbuild.dotnet_exe(), dll], capture_output=True, text=True, cwd="/mnt/d", timeout=180)
    out = {}
    for ln in pr.stdout.splitlines():
        if ln.startswith("U ") and not ln.startswith("U-count"):
            name, _, rest = ln[2:].strip().partition(" ")
            out[name] = rest
    if "U-count %d" % N_UNITS not in pr.stdout or len(out) != N_UNITS:
        raise Unmeasured("the harness printed %d units, want %d: %s %s" % (len(out), N_UNITS, pr.stdout[-300:], pr.stderr[-400:]))
    return out


_CLEAN = [None]


def unit(name):
    if _CLEAN[0] is None:
        _CLEAN[0] = units(read(os.path.join(CS, CORE)))
    return _CLEAN[0].get(name, "FAIL did not run")


def code(path):
    """The C# of a file with its comments and its strings blanked: what is wired, not what is described."""
    s = re.sub(r'@"(?:[^"]|"")*"|"(?:\\.|[^"\\\n])*"', '""', read(path))
    return re.sub(r"\s+", " ", re.sub(r"//[^\n]*", "", re.sub(r"/\*.*?\*/", "", s, flags=re.S)))


def wired(path, *needles):
    """None when the file holds each of these calls, else what is missing: a rule of the core that no hook calls proves nothing."""
    s = code(os.path.join(CS, path))
    for n in needles:
        if n not in s:
            return "FAIL %s does not hold: %s" % (path, n)
    return None


def both(*vals):
    bad = [v for v in vals if v != "ok" and v is not None]
    return "ok" if not bad else "; ".join(bad)


# ------------------------------------------------------------------------------------------------ the Python half of check 1
def load_py(text):
    d = tempfile.mkdtemp(prefix="calm_profile_")
    try:
        p = os.path.join(d, "calm_profile_under_test.py")
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        spec = importlib.util.spec_from_file_location("calm_profile_under_test", p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    finally:
        shutil.rmtree(d, ignore_errors=True)


def certificate_rules(m):
    """None when certificate_lines gives lines only from a valid certificate, and only for the held routes it shows."""
    import tap_certificate as T
    ident = {"companion": "mvid-A", "modlist": "fp-1", "inventory": {}, "settings": {}}
    shown = {"incident": ["fired", "held"], "gate.quest": ["allowed"], "gate.mental": ["allowed", "held"]}
    cert = T.make(ident, shown, {"tap": "job_start", "reported": "blind"})
    lines, _ = m.certificate_lines(cert, ident)
    if sorted(lines) != ["gate.mental.held", "incident.held"]:
        return "FAIL a valid certificate gave lines %s, want gate.mental.held and incident.held (gate.quest.held not shown)" % sorted(lines)
    other = dict(ident, companion="mvid-B")
    lines, why = m.certificate_lines(cert, other)
    if lines:
        return "FAIL a certificate for another companion gave lines %s" % lines
    lines, why = m.certificate_lines(None, ident)
    if lines or "could not look" not in why:
        return "FAIL no certificate gave lines %s (%s)" % (lines, why)
    args = m.arm_args(cert, ident, "drv", weather="Clear")
    if args.get("certified") != "incident.held,gate.mental.held" or args.get("driver") != "drv":
        return "FAIL arm_args: %s" % args
    try:
        m.arm_args(cert, ident, "drv", certified="incident.held,gate.quest.held")
        return "FAIL arm_args took certified lines from the caller"
    except ValueError:
        pass
    return None


_PY = [None]


def py_clean():
    if _PY[0] is None:
        _PY[0] = certificate_rules(load_py(read(PY)))
    return _PY[0]


# ------------------------------------------------------------------------------------------------ the 11 checks
def t_a_control_reads_held_only_with_its_certificate_line():
    return both(py_clean(),
                wired(VERSE, "var why = S.Arm(p, Current.Game, Campaign(), Now, (c, r) => Apply(c, r, map, p, minutes));"),
                unit("a_control_reads_held_only_with_its_certificate_line"))


def t_a_scene_exception_opens_one_gate_for_one_named_event():
    return both(wired(VERSE, 'var g = JawaBenchGates.G.Of(gate ?? "");', "return Done(S.Except(g, name));"),
                wired("JawaBenchGatesCore.cs", "public void AllowOne(string name)", "public int TakeBack(string name)"),
                unit("a_scene_exception_opens_one_gate_for_one_named_event"))


def t_a_hold_on_needs_is_two_entries():
    return both(wired(VERSE, 'r.AddNeedsHold(string.Join("", ids.ToArray()),', "foreach (var kv in _needs) if (kv.Key.CurLevel != kv.Value) kv.Key.CurLevel = kv.Value;"),
                unit("a_hold_on_needs_is_two_entries"))


def t_the_put_back_runs_in_reverse_order_with_read_back():
    return both(wired(VERSE, "S.Leave(", "JawaBenchGates.GiveBackQueue(back);"), wired(CORE, "lines?.AddRange(R.PutBackAll(", "lines.AddRange(R.PutBackAll(why, npb));"),
                unit("the_put_back_runs_in_reverse_order_with_read_back"))


def t_a_lease_that_ran_out_puts_back():
    return both(wired(CALM, "JawaBenchCalmProfile.Frame();"),
                wired(VERSE, "var left = S.Tick(Now, Current.Game, out rearm);", "if (rearm) { Rearm(); return; }",
                      "var hook = JawaBenchCalm.EnsurePatched();",
                      "var why = S.Rearm(Current.Game, Campaign(), Now, (c, r) => Apply(c, r, map, p, minutes), lines);"),
                unit("a_lease_that_ran_out_puts_back"))


def t_a_value_that_could_not_be_put_back_is_named():
    return both(wired(CORE, "LastNotPutBack = npb;"), wired(VERSE, '[""] = S.LastNotPutBack,'),
                unit("a_value_that_could_not_be_put_back_is_named"))


def t_a_destructive_control_is_refused_under_campaign_only():
    return both(wired(VERSE, "private static bool Campaign() => JawaBenchCompanionSafety.PolicyNow().DenyCampaignFamilies;",
                      "case P.ClearSite: return p.Clear ? ClearSite(r, map) :"),
                unit("a_destructive_control_is_refused_under_campaign_only"))


def t_attempts_stopped_and_scheduling_switched_off_are_two_numbers():
    return both(wired(VERSE, '[""] = S.AttemptsStopped(), [""] = S.SchedulingSwitchedOff(),', "() => g.Held - held0"),
                unit("attempts_stopped_and_scheduling_switched_off_are_two_numbers"))


def blank(text):
    """code() on a text instead of a file."""
    s = re.sub(r'@"(?:[^"]|"")*"|"(?:\\.|[^"\\\n])*"', '""', text)
    return re.sub(r"\s+", " ", re.sub(r"//[^\n]*", "", re.sub(r"/\*.*?\*/", "", s, flags=re.S)))


def call_order(text):
    """None when the tool answers a read before the driver check, and asks the driver check before the first write, else why not."""
    s = blank(text)
    i_read, i_call, i_arm = s.find('if (a == "") return Done(null);'), s.find("var no = S.Call(driver, a, t);"), s.find('if (a == "") { string bad;')
    if not 0 <= i_read < i_call:
        return "FAIL %s does not answer a read before the driver check (a read by anyone is no breach)" % VERSE
    if not i_call < i_arm:
        return "FAIL %s does not ask S.Call before the first write action" % VERSE
    return None


def t_a_second_driver_is_an_apparatus_breach():
    return both(call_order(read(os.path.join(CS, VERSE))), wired(VERSE, "S.B.Sink = () => JawaBenchWorld.LiveSink;"),
                unit("a_second_driver_is_an_apparatus_breach"))


def t_unknown_profile_keys_are_refused():
    return both(wired(VERSE, "var p = JawaBenchCalmProfileCore.Parse(keys, out bad);", "if (p == null) return Done(bad);",
                      "d = JawaBenchCondCore.ParseJson(spec) as Dictionary<string, object>;"),
                unit("unknown_profile_keys_are_refused"))


def t_a_not_undone_control_is_listed_as_such():
    return both(wired(VERSE, "r.Add(P.ClearSite, P.NotUndone, null, null, null, ", '[""] = S.R.NotUndoneLines(),'),
                unit("a_not_undone_control_is_listed_as_such"))


CHECKS = [t_a_control_reads_held_only_with_its_certificate_line, t_a_scene_exception_opens_one_gate_for_one_named_event,
          t_a_hold_on_needs_is_two_entries, t_the_put_back_runs_in_reverse_order_with_read_back, t_a_lease_that_ran_out_puts_back,
          t_a_value_that_could_not_be_put_back_is_named, t_a_destructive_control_is_refused_under_campaign_only,
          t_attempts_stopped_and_scheduling_switched_off_are_two_numbers, t_a_second_driver_is_an_apparatus_breach,
          t_unknown_profile_keys_are_refused, t_a_not_undone_control_is_listed_as_such]

# ------------------------------------------------------------------------------------------------ plants
PLANTS = [
    ("HELD without the certificate line", "a_control_reads_held_only_with_its_certificate_line",
     [("if (certified != null && certified.Contains(c.CertLine))", "if (true)")]),
    ("HELD for a control with no line, on a caller's word", "a_control_reads_held_only_with_its_certificate_line",
     [('if (c.CertLine == null) { why = "no certificate line exists for this kind of control yet"; return Unproven; }',
       'if (c.CertLine == null && certified != null && certified.Contains(c.Name)) { why = ""; return Held; }')]),
    ("an exception never closed at leave", "a_scene_exception_opens_one_gate_for_one_named_event",
     [("int left = x.Gate.TakeBack(x.Name);", "int left = 0;")]),
    ("a needs hold with no record of what did not happen", "a_hold_on_needs_is_two_entries",
     [('                Add(NeedsHold, NotUndone, null, null, null, "save", ', '                if (false) Add(NeedsHold, NotUndone, null, null, null, "save", ')]),
    ("a put-back in the order of the changes", "the_put_back_runs_in_reverse_order_with_read_back",
     [("for (int i = _live.Count - 1; i >= 0; i--)", "for (int i = 0; i < _live.Count; i++)")]),
    ("a put-back with no read-back", "the_put_back_runs_in_reverse_order_with_read_back",
     [("try { now = e.Read == null ? null : e.Read(); }", "try { now = e.Before; }")]),
    ("a lease that never ends", "a_lease_that_ran_out_puts_back",
     [('if (L.Expired(nowS)) return Leave("lease ended");', "")]),
    ("a lease end that switches off without putting back", "a_lease_that_ran_out_puts_back",
     [('if (L.Expired(nowS)) return Leave("lease ended");', 'if (L.Expired(nowS)) { Armed = false; L.End("lease ended"); return new List<string> { "lease ended" }; }')]),
    ("a re-arm after a load that renews the lease", "a_lease_that_ran_out_puts_back",
     [("if (!keepLease || !L.On) L.Arm(nowS, p.Minutes);", "L.Arm(nowS, p.Minutes);")]),
    ("exceptions dropped at a re-arm after a load", "a_scene_exception_opens_one_gate_for_one_named_event",
     [("if (x.Gate.TakeBack(x.Name) > 0) carry.Add(x);", "if (x.Gate.TakeBack(x.Name) > 0) { }")]),
    ("a value that reads otherwise counted as put back", "a_value_that_could_not_be_put_back_is_named",
     [("if (err == null && now != e.Before)", "if (false)")]),
    ("a failed put-back left unnamed", "a_value_that_could_not_be_put_back_is_named",
     [('if (err != null) { notPutBack?.Add(e.Control + " (" + e.Class + "): " + err);', "if (err != null) {")]),
    ("a destructive control that runs under CAMPAIGN", "a_destructive_control_is_refused_under_campaign_only",
     [("                    if (campaign)\n", "                    if (campaign && !c.Destructive)\n")]),
    ("a destructive control refused on every save", "a_destructive_control_is_refused_under_campaign_only",
     [("                    if (campaign)\n", "                    if (campaign || c.Destructive)\n")]),
    ("schedulers counted as attempts stopped", "attempts_stopped_and_scheduling_switched_off_are_two_numbers",
     [("                return n;\n            }\n\n            internal int SchedulingSwitchedOff()", "                return n + SchedulingSwitchedOff();\n            }\n\n            internal int SchedulingSwitchedOff()")]),
    ("a second driver let through", "a_second_driver_is_an_apparatus_breach",
     [("if (!Armed || P == null || string.Equals(driver ?? \"\", P.Driver, StringComparison.Ordinal)) return null;", "return null;")]),
    ("a second driver refused with no breach", "a_second_driver_is_an_apparatus_breach",
     [('                B.Add(Apparatus, "second_driver", tick, ', '                if (false) B.Add(Apparatus, "second_driver", tick, ')]),
    ("an unknown key ignored", "unknown_profile_keys_are_refused",
     [('if (!Keys.Contains(k)) { refusal = "REFUSED: unknown profile key', 'if (false) { refusal = "REFUSED: unknown profile key')]),
    ("a NOT UNDONE entry put back", "a_not_undone_control_is_listed_as_such",
     [("if (e.Class == NotUndone) { NotUndoneDone.Add(e); continue; }", "if (false) { NotUndoneDone.Add(e); continue; }")]),
]

# Plants on a copy of the Verse half's tool body, judged by call_order: the order of the read, the driver check and the writes.
_CALL = '                var no = S.Call(driver, a, t);\n                if (no != null) return Done(no);\n'
_READ = '                if (a == "read") return Done(null);\n'
_ARMED = '                if (!S.Armed) return Done("REFUSED: no calm profile is armed");\n'
VERSE_PLANTS = [
    ("a read that meets the driver check (another driver's read is a breach)", [(_READ, ""), (_CALL, _CALL + _READ)]),
    ("a write before the driver check", [(_CALL, ""), (_ARMED, _ARMED + _CALL)]),
]

PY_PLANTS = [
    ("lines from a refused certificate", [('if state != "valid":', 'if state == "could not look":')]),
    ("a line for a route the certificate did not show", [('if route in (cov.get(tap) or {}).get("covered", []):', "if True:")]),
    ("certified lines taken from the caller", [('    if "certified" in profile:\n        raise ValueError', '    if False:\n        raise ValueError'),
                                              ('return dict(profile, action="arm", driver=driver, certified=",".join(lines))',
                                               'return dict(dict(certified=",".join(lines)), **dict(profile, action="arm", driver=driver))')]),
]


def plant(text, subs, where):
    ok = True
    for old, new in subs:
        if text.count(old) != 1:
            print("FAIL plant: its text is in %s %d times, want 1: %r" % (where, text.count(old), old[:70]))
            ok = False
        text = text.replace(old, new)
    return text, ok


def plants():
    good = True
    src = read(os.path.join(CS, CORE))
    for name, must, subs in PLANTS:
        text, ok = plant(src, subs, CORE)
        red = sorted(u for u, v in units(text).items() if v != "ok")
        hit = ok and must in red
        good = good and hit
        print("%s plant %r turns red: %s" % ("ok  " if hit else "FAIL", name, red), flush=True)
    verse = read(os.path.join(CS, VERSE))
    for name, subs in VERSE_PLANTS:
        text, ok = plant(verse, subs, VERSE)
        v = call_order(text)
        hit = ok and v is not None
        good = good and hit
        print("%s plant %r turns a_second_driver_is_an_apparatus_breach red: %s" % ("ok  " if hit else "FAIL", name, v), flush=True)
    py = read(PY)
    for name, subs in PY_PLANTS:
        text, ok = plant(py, subs, "calm_profile.py")
        try:
            v = certificate_rules(load_py(text))
        except Exception as e:      # a plant that breaks the module is red too
            v = "FAIL %s" % e
        hit = ok and v is not None
        good = good and hit
        print("%s plant %r turns a_control_reads_held_only_with_its_certificate_line red: %s" % ("ok  " if hit else "FAIL", name, v), flush=True)
    return good


def main(argv):
    bad = 0
    try:
        for t in CHECKS:
            v = t()
            bad += v != "ok"
            print("%s %s%s" % ("ok  " if v == "ok" else "FAIL", t.__name__[2:], "" if v == "ok" else ": " + v), flush=True)
        good = True if "--no-plants" in argv else plants()
    except Unmeasured as e:
        print("FAIL calm profile UNMEASURED: %s" % e)
        return 1
    print("calm profile: %d of %d checks passed%s" % (len(CHECKS) - bad, len(CHECKS),
                                                    "" if "--no-plants" in argv else "; plants %s" % ("all red" if good else "NOT all red")))
    return 0 if bad == 0 and good else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
