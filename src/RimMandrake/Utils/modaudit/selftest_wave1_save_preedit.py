#!/usr/bin/env python3
"""Selftest for modaudit/wave1_save_preedit.py's fourth repair (relic precepts), on a synthetic mini-save.

Offline; writes only under a temp dir.
    python3 src/RimMandrake/Utils/modaudit/selftest_wave1_save_preedit.py
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SCRIPT = os.path.join(HERE, "wave1_save_preedit.py")

FAILS = []


def check(name, got, want):
    if got != want:
        FAILS.append("%s: got %r want %r" % (name, got, want))


def relic(pid, name, thing):
    return ('\t\t<li Class="Precept_Relic">\r\n\t\t\t<name>%s</name>\r\n\t\t\t<def>IdeoRelic</def>\r\n'
            '\t\t\t<ID>%s</ID>\r\n\t\t\t<thingDef>%s</thingDef>\r\n\t\t\t<generatedRelic>null</generatedRelic>\r\n'
            '\t\t</li>\r\n' % (name, pid, thing))


def fixture():
    body = "".join([
        relic(2402, "Hexlink", "VWE_Gun_ChargeLMG_Unique"),
        relic(2590, "Rifle of Self", "AM_M700A"),            # same name, other ID: a decoy
        relic(2591, "Loccorpus", "VWE_Gun_ChargeLMG_Unique"),
        relic(2701, "Strong Rifle", "VWE_Gun_MarksmanRifle"),
        relic(2810, "Rifle of Self", "VWE_Gun_MarksmanRifle"),
        relic(3605, "Animal Blaster", "VWE_Gun_ChargeLMG_Unique"),
        relic(9999, "Hexlink", "VWE_Gun_ChargeLMG_Unique"),  # unknown ID: never touched
    ])
    return ("<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n<savegame>\r\n<game>\r\n<ideos>\r\n" + body +
            "</ideos>\r\n<priceHistory><li>VWE_Gun_ChargeLMG_Unique</li></priceHistory>\r\n"
            "<things><thing Class=\"MinifiedThing\"><def>MinifiedThing</def><id>MinifiedThing1</id>"
            "<innerContainer><innerList><li><def>RM_Graffiti_Vandal</def><id>G1</id></li></innerList>"
            "</innerContainer></thing>\r\n"
            "</things>\r\n</game>\r\n</savegame>\r\n").encode()


def run(inp, out, *extra):
    p = subprocess.run([sys.executable, SCRIPT, inp, out, "--walls", "0", "--quests", "0", "--passions", "0"] +
                       list(extra), capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def t_spans():
    import wave1_save_preedit as w
    pend, done = w.relic_spans(fixture())
    check("pending", sorted(t for _, _, t, _ in pend),
          sorted("%s:%s->%s" % (n, o, r) for _, n, o, r in w.RELIC_MAP))
    check("done", done, [])
    check("five", len(w.RELIC_MAP), 5)


def t_apply_and_idempotent():
    import wave1_save_preedit as w
    td = tempfile.mkdtemp()
    inp, out, out2 = (os.path.join(td, n) for n in ("in.rws", "out.rws", "out2.rws"))
    with open(inp, "wb") as f:
        f.write(fixture())
    rc, log = run(inp, out, "--apply")
    check("apply rc (%s)" % log[-300:], rc, 0)
    d0, d1 = fixture(), open(out, "rb").read() if os.path.exists(out) else b""
    check("input untouched", open(inp, "rb").read(), d0)
    check("backup written", os.path.exists(out + ".input.bak") and open(out + ".input.bak", "rb").read() == d0, True)
    rel = w.relic_census(out) if os.path.exists(out) else []
    for pid, name, old, new in w.RELIC_MAP:
        check("%s now %s" % (name, new), (str(pid), name, new) in rel, True)
    check("unknown ID left alone", ("9999", "Hexlink", "VWE_Gun_ChargeLMG_Unique") in rel, True)
    check("decoy left alone", ("2590", "Rifle of Self", "AM_M700A") in rel, True)
    check("price row left alone", b"<li>VWE_Gun_ChargeLMG_Unique</li>" in d1, True)
    check("CRLF preserved", d1.count(b"\r\n"), d0.count(b"\r\n"))
    delta = sum(len(new) - len(old) for _, _, old, new in w.RELIC_MAP)
    check("size delta", len(d1) - len(d0), delta)
    rc, log = run(out, out2, "--apply")
    check("rerun rc (%s)" % log[-300:], rc, 0)
    check("rerun byte-identical", os.path.exists(out2) and open(out2, "rb").read() == d1, True)
    check("rerun says already", "already 5" in log, True)
    rc, log = run(inp, out, "--apply")
    check("refuses existing OUT", rc != 0 and "exists" in log, True)
    broken = d0.replace(b"<ID>2701</ID>\r\n\t\t\t<thingDef>VWE_Gun_MarksmanRifle", b"<ID>2701</ID>\r\n\t\t\t<thingDef>Gun_X")
    with open(inp + ".b", "wb") as f:
        f.write(broken)
    rc, log = run(inp + ".b", out + ".b", "--apply")
    check("refuses moved relic", rc != 0 and "REFUSED" in log and not os.path.exists(out + ".b"), True)


def main():
    for t in (t_spans, t_apply_and_idempotent):
        try:
            t()
        except Exception as e:  # a missing function is a FAIL, not a crash
            FAILS.append("%s raised %r" % (t.__name__, e))
    if FAILS:
        print("FAIL selftest_wave1_save_preedit: %d" % len(FAILS))
        for f in FAILS:
            print("  " + f)
        sys.exit(1)
    print("OK selftest_wave1_save_preedit")


if __name__ == "__main__":
    main()
