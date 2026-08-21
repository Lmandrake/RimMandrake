#!/usr/bin/env python3
"""selftest_broadcast_frame.py — does the owner's broadcast arrive with NO dialog?

    python3 src/RimMandrake/Utils/selftest_broadcast_frame.py

⛔ SENDS NOTHING. It imports broadcast.py and calls `frame()` directly, then runs
the result through a transcription of the CLI's OWN parser and inbound gate. No
socket is opened, so an agent may run this; an agent still may not run broadcast.

WHY IT EXISTS. Until 2026-08-21 every broadcast landed behind an accept/reject
dialog, which defeats the point of a broadcast. The cause was two silent things
at once: the tag carried no `from-mode`, and its body was not newline-delimited,
so the CLI never recognised it as a peer message in the first place. Neither
failure is visible from the sending end — the send succeeds either way.

🔴 THIS IS UNDOCUMENTED CLI INTERNALS, transcribed from
`~/.local/share/claude/versions/2.1.238`. When Claude Code upgrades, this test is
the tripwire: if the real CLI changes its parser, this file still passes while
broadcasts start being held again. So on any upgrade, re-read the binary — the
functions are named in broadcast.py's docstring with their byte offsets — and
update BOTH files together.

⚠️ It also depends on the feature gate `tengu_harbor_kite_mode_emit`, which reads
true on this machine. With that gate off, the receiver ignores `from-mode` and
holds regardless of anything here.
"""
import json, re, sys
sys.path.insert(0, "src/RimMandrake/Utils")
import broadcast

TAG = "cross-session-message"
J9o  = r"A-Za-z0-9%:_/.\\-"
_Id  = r"[A-Za-z0-9_-]{1,80}"
fId  = r"[0-9a-f]{24}"
fkb  = fId + r"(?:," + fId + r"){0,31}"
hId  = ["bypass", "prompting"]

EId_RE = re.compile(
    r'^<' + TAG +
    r'(?: from="([' + J9o + r']+)")?'
    r'(?: from-session="(' + _Id + r')")?'
    r'(?: hop-chain="(' + fkb + r')")?'
    r'(?: from-name="([^"<>\n\r]+)")?'
    r'(?: from-mode="(' + "|".join(hId) + r')")?'
    r'>\n([\s\S]*)\n</' + TAG + r'>$')

def hkb(frm, name, sess, hop, mode):          # attribute builder
    i = []
    if frm:  i.append('from="%s"' % frm)
    if sess and re.fullmatch(_Id, sess): i.append('from-session="%s"' % sess)
    if hop:  i.append('hop-chain="%s"' % ",".join(hop))
    if name:
        s = re.sub(r'["<>]', "", name).strip()
        if s: i.append('from-name="%s"' % s)
    if mode: i.append('from-mode="%s"' % mode)
    return (" " + " ".join(i)) if i else ""

def v1r(frm, name, body, sess, hop, mode):    # re-serialiser
    return "<%s%s>\n%s\n</%s>" % (TAG, hkb(frm, name, sess, hop, mode), body, TAG)

def EId(text):
    m = EId_RE.match(text)
    if not m:
        return None, "regex did not match"
    hop = m.group(3).split(",") if m.group(3) is not None else None
    if v1r(m.group(1), m.group(4), m.group(6) or "", m.group(2), hop, m.group(5)) != text:
        return None, "round-trip re-serialisation differed -> discarded"
    return {"from": m.group(1), "fromSession": m.group(2), "hopChain": hop,
            "fromName": m.group(4), "fromMode": m.group(5), "body": m.group(6) or ""}, None

def Enm(fromMode, our_mode="bypass", gate=True):
    """Receiver gate, transcribed. crossSessionInbound undefined at repo scope."""
    i = fromMode if gate else None
    if i is not None:
        return ("accept", "bypass-default") if i == our_mode else ("hold", "mode-mismatch")
    return ("hold", "no-mode-asserted") if our_mode == "bypass" else ("accept", "bypass-default")

def check(label, content):
    parsed, err = EId(content)
    if parsed is None:
        print("  %-34s NOT A PEER MESSAGE (%s)  -> origin.fromMode=None -> %s / %s"
              % (label, err, *Enm(None)))
        return False
    pol, cause = Enm(parsed["fromMode"])
    print("  %-34s parsed  fromName=%-6s fromMode=%-9s -> %s / %s"
          % (label, parsed["fromName"], parsed["fromMode"], pol, cause))
    return pol == "accept"

print("frame() read off CLI version:", broadcast.FRAME_READ_FROM_CLI_VERSION)
print()
print("OLD frame (what shipped until today) vs NEW frame (frame() as it stands now):")
old = '<%s from-name="OWNER">%s</%s>' % (TAG, "Game is up", TAG)
ok_old = check("old, no newlines, no from-mode", old)
new = json.loads(broadcast.frame("Game is up"))["message"]["content"]
ok_new = check("new, frame(\"Game is up\")", new)
print()
print("  new content, repr:", repr(new))
print()
print("negative controls — each must NOT reach accept:")
check("from-mode wrong value order",  '<%s from-mode="bypass" from-name="OWNER">\nx\n</%s>' % (TAG, TAG))
check("newlines removed",             '<%s from-name="OWNER" from-mode="bypass">x</%s>' % (TAG, TAG))
check("from-mode=prompting",          '<%s from-name="OWNER" from-mode="prompting">\nx\n</%s>' % (TAG, TAG))
print()
print("the sentences ./game actually sends:")
allok = True
for phrase in ["Game is up", "Game is down", "Game is loading", "Game is deploying",
               "WRAP is initiated", 'Game is up (started for the vehicle look)',
               "Game is up & <ready>"]:
    c = json.loads(broadcast.frame(phrase))["message"]["content"]
    p, e = EId(c)
    pol = Enm(p["fromMode"])[0] if p else "NOT-PARSED"
    st = "accept" if pol == "accept" else pol
    allok &= (st == "accept")
    print("  %-40s -> %-8s  body=%r  game_state_in=%s"
          % (phrase, st, p["body"] if p else None, broadcast.game_state_in(phrase)))
print()
print("RESULT: old frame accepted =", ok_old, " | new frame accepted =", ok_new,
      " | all ./game sentences accepted =", bool(allok))
sys.exit(0 if (ok_new and allok and not ok_old) else 1)
