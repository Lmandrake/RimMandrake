#!/usr/bin/env python3
"""PIT_CAPTURE_FIX_WARDEN_HURT_AT_LIP: capture down's pin must never swing at the warden.

Live round 5 (pit walk S7) the warden at the lip took Scratch and Crack while the held, unarmed pirate was pinned
4 m below, and the capture stopped. The attacker was our own pin: JobDriver_CaptureDown called
PawnUtility.ForceWait(Victim), i.e. vanilla JobDriver_Wait, whose CheckForAutoAttack (RimWorld 1.6,
Verse.AI/JobDriver_Wait.cs) TryMeleeAttacks any hostile in the 9 cells around the waiter every 4 ticks. The warden
stands in one of them.

The fix pins with RM_CaptureDownPinned (JobDriver_CaptureDownPinned): stand still, face the warden, nothing else.
This test reads the shipped source, def and DLL offline (no game, no git):
  1. JobDriver_CaptureDown pins only through JobDriver_CaptureDownPinned.Pin, in the reach AND the hold toil
     (re-pinning a pin something else ended), never PawnUtility.ForceWait.
  2. JobDriver_CaptureDownPinned derives JobDriver (not JobDriver_Wait) and contains no attack call.
  3. Its vanilla fallback (ForceWait) is reached only for a pawn that cannot swing (downed, asleep, bedded, shut down).
  4. The JobDef exists with that driver class, and the DefOf names it.
  5. The committed DLL is built from this source (.srchash per-file and dll hashes) and carries the type.
Each check also runs on the pre-fix shape to prove it can fail.
"""
import hashlib
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FW = ROOT / "src/RimMandrake/FlowWorks"
ROOMS = FW / "Source/Superdeep/RM_PitRooms.cs"
DEFOF = FW / "Source/RimMandrakeFlowWorks_DefOf.cs"
JOBDEFS = FW / "Defs/Canals/JobDefs/FlowWorks_JobDefs.xml"
DLL = FW / "Assemblies/RimMandrakeFlowWorks.dll"
STAMP = FW / "Assemblies/RimMandrakeFlowWorks.dll.srchash"

ATTACKS = ("TryMeleeAttack", "CheckForAutoAttack", "TryStartAttack", "AttackMelee", "JobDriver_Wait")


def class_body(src, name):
    """The text of `class <name>` up to the next top-level public class (or end of file)."""
    m = re.search(r"\bclass\s+" + re.escape(name) + r"\b[^{]*\{", src)
    if not m:
        return None
    nxt = re.search(r"\n\t(?:public|internal)\s+(?:static\s+)?class\s+", src[m.end():])
    return src[m.start(): m.end() + (nxt.start() if nxt else len(src))]


def check_capture(src):
    """Faults in JobDriver_CaptureDown's pinning; [] when sound."""
    body = class_body(src, "JobDriver_CaptureDown")
    if body is None:
        return ["JobDriver_CaptureDown not found"]
    faults = []
    if "ForceWait(" in body:
        faults.append("JobDriver_CaptureDown still pins with PawnUtility.ForceWait (vanilla Wait auto-melees the warden)")
    if body.count("JobDriver_CaptureDownPinned.Pin(") < 2:
        faults.append("JobDriver_CaptureDown must pin through JobDriver_CaptureDownPinned.Pin in reach and hold (found %d)"
                      % body.count("JobDriver_CaptureDownPinned.Pin("))
    return faults


def check_pin(src):
    """Faults in the pin driver; [] when sound."""
    body = class_body(src, "JobDriver_CaptureDownPinned")
    if body is None:
        return ["JobDriver_CaptureDownPinned not found"]
    faults = []
    if not re.search(r"class\s+JobDriver_CaptureDownPinned\s*:\s*JobDriver\s*\n", body):
        faults.append("JobDriver_CaptureDownPinned must derive JobDriver directly")
    for a in ATTACKS:
        if a in body:
            faults.append("pin driver mentions %s" % a)
    if "RM_CaptureDownPinned" not in body or "StartJob(" not in body:
        faults.append("Pin does not start an RM_CaptureDownPinned job")
    fw = body.find("ForceWait(")
    if fw >= 0:
        guard = body[:fw]
        gate = guard[guard.rfind("if (victim.Downed"):] if "if (victim.Downed" in guard else ""   # the enclosing gate
        for need in ("Downed", "Awake()", "InBed()", "IsDeactivated()", "IsSelfShutdown()"):
            if need not in gate:
                faults.append("vanilla ForceWait fallback not gated on %s" % need)
    return faults


def check_defs():
    faults = []
    hit = [jd for jd in ET.parse(JOBDEFS).getroot().iter("JobDef") if jd.findtext("defName") == "RM_CaptureDownPinned"]
    if len(hit) != 1:
        faults.append("RM_CaptureDownPinned JobDef count %d, want 1" % len(hit))
    elif hit[0].findtext("driverClass") != "RimMandrake.FlowWorks.JobDriver_CaptureDownPinned":
        faults.append("RM_CaptureDownPinned driverClass is %r" % hit[0].findtext("driverClass"))
    if not re.search(r"public static JobDef RM_CaptureDownPinned;", DEFOF.read_text(encoding="utf-8")):
        faults.append("DefOf lacks RM_CaptureDownPinned")
    return faults


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check_dll():
    faults = []
    lines = STAMP.read_text(encoding="utf-8").splitlines()
    dll_line = [ln for ln in lines if ln.startswith("# dll: ")]
    if not dll_line or dll_line[0].split(": ", 1)[1].strip() != sha(DLL):
        faults.append("committed DLL hash differs from its .srchash")
    files = {}
    for ln in lines:
        if ln and not ln.startswith("#"):
            h, rel = ln.split(" ", 1)
            files[rel.strip()] = h
    for rel, p in (("Superdeep/RM_PitRooms.cs", ROOMS), ("RimMandrakeFlowWorks_DefOf.cs", DEFOF)):
        if files.get(rel) != sha(p):
            faults.append(".srchash for %s is not this source: DLL not rebuilt" % rel)
    if b"JobDriver_CaptureDownPinned" not in DLL.read_bytes():   # a literal type name in the #Strings heap
        faults.append("DLL lacks the JobDriver_CaptureDownPinned type")
    return faults


OLD_SHAPE = """
\tpublic class JobDriver_CaptureDown : JobDriver
\t{
\t\t\t\t\tcase RM_PitRoomMath.CaptureStep.Hold:
\t\t\t\t\t\tPawnUtility.ForceWait(Victim, RM_PitRoomMath.CaptureDownTicks + 30, pawn);
\t\t\t\t\t\treturn;
\t}
"""

BAD_PIN = """
\tpublic class JobDriver_CaptureDownPinned : JobDriver_Wait
\t{
\t\tpublic static void Pin(Pawn victim, Pawn warden, int ticks)
\t\t{
\t\t\tPawnUtility.ForceWait(victim, ticks, warden);
\t\t}
\t}
"""


def main():
    src = ROOMS.read_text(encoding="utf-8")
    faults = check_capture(src) + check_pin(src) + check_defs() + check_dll()
    # the instrument can see: the pre-fix shape and a swinging pin are both refused
    if not check_capture(OLD_SHAPE):
        faults.append("SANITY: check_capture passed the pre-fix ForceWait pin")
    if not check_pin(BAD_PIN):
        faults.append("SANITY: check_pin passed a JobDriver_Wait pin with an ungated ForceWait")
    for f in faults:
        print("FAIL", f)
    if faults:
        return 1
    print("OK selftest_pit_capture_pin: capture down pins with RM_CaptureDownPinned (no auto-attack); DLL built from it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
