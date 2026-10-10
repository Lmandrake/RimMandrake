#!/usr/bin/env python3
"""MAP_SILENCE_SINGLE_OWNER_1 offline check: compiles CreatureBehaviors/Source/RM_SilenceReasons.cs (pure C#, no Verse) with the
Windows dotnet.exe and runs 12 assertions on the reason bookkeeping (hush starts on the first reason, restore only when the last
reason leaves, open-ended reasons never expire). Then plants a defect (Remove always says "restore") and requires the run to fail.
Also checks the wiring: FeverWood no longer ends sustainers itself and both sides go through the one service.

    python3 src/RimMandrake/Utils/selftest_silence_reasons.py
"""
import os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CB = os.path.join(ROOT, "src", "RimMandrake", "CreatureBehaviors", "Source")
FW = os.path.join(ROOT, "src", "RimMandrake", "FeverWood", "Source", "RM_MapComponent_TentacleWatch.cs")
STAGE = "/mnt/d/Luke/dev/_rmscratch/silencetest"
DOTNET = "/mnt/c/Users/Mandrake/.dotnet/dotnet.exe"
PROG = r'''using System; using System.Collections.Generic; using RimMandrake.CreatureBehaviors;
class P { static int bad; static void Eq(string n, object a, object b){ if(!Equals(a,b)){bad++;Console.WriteLine("FAIL "+n+": "+a+" != "+b);} else Console.WriteLine("ok   "+n);}
static int Main(){
 var r=new Dictionary<string,int>();
 Eq("first add starts hush", RM_SilenceReasons.Add(r,"hunt",100), true);
 Eq("second add does not", RM_SilenceReasons.Add(r,"sentinel",RM_SilenceReasons.Indefinite), false);
 Eq("same key shorter keeps later", RM_SilenceReasons.Add(r,"hunt",50), false); Eq("hunt end kept", r["hunt"], 100);
 Eq("expire at 100 leaves sentinel (not empty)", RM_SilenceReasons.Expire(r,100), false); Eq("count after expire", r.Count, 1);
 Eq("sentinel never expires", RM_SilenceReasons.Expire(r,int.MaxValue-1), false);
 Eq("remove unknown does not restore", RM_SilenceReasons.Remove(r,"nope"), false);
 Eq("remove last restores", RM_SilenceReasons.Remove(r,"sentinel"), true);
 RM_SilenceReasons.Add(r,"a",10); RM_SilenceReasons.Add(r,"b",20);
 Eq("remove one of two does not restore", RM_SilenceReasons.Remove(r,"a"), false);
 Eq("expire last restores", RM_SilenceReasons.Expire(r,20), true);
 Eq("expire empty is false", RM_SilenceReasons.Expire(r,999), false);
 Console.WriteLine(bad==0?"ALL OK":"FAILED "+bad); return bad; } }
'''
CSPROJ = '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework></PropertyGroup></Project>'


def run(kernel_text):
    os.makedirs(STAGE, exist_ok=True)
    open(os.path.join(STAGE, "RM_SilenceReasons.cs"), "w", encoding="utf-8").write(kernel_text)
    open(os.path.join(STAGE, "P.cs"), "w", encoding="utf-8").write(PROG)
    open(os.path.join(STAGE, "T.csproj"), "w", encoding="utf-8").write(CSPROJ)
    r = subprocess.run([DOTNET, "run"], cwd=STAGE, capture_output=True, text=True, timeout=300)
    return r.returncode, r.stdout + r.stderr


def main():
    if not os.path.exists(DOTNET):
        print("UNMEASURED: no Windows dotnet.exe on this machine")
        return 0
    kernel = open(os.path.join(CB, "RM_SilenceReasons.cs"), encoding="utf-8").read()
    bad = 0
    rc, out = run(kernel)
    ok = rc == 0 and "ALL OK" in out
    print(("ok   " if ok else "FAIL ") + "real kernel: 12/12 assertions" + ("" if ok else " | " + out[-300:]))
    bad += not ok
    planted = kernel.replace("return reasons.Remove(key) && reasons.Count == 0;", "return reasons.Remove(key);")
    assert planted != kernel
    rc, out = run(planted)
    hit = rc != 0 and "FAIL" in out
    print(("ok   " if hit else "FAIL ") + "planted defect (Remove restores while another reason is held) is caught")
    bad += not hit
    fw = open(FW, encoding="utf-8").read()
    cue = open(os.path.join(CB, "RM_MapComponent_SilenceCue.cs"), encoding="utf-8").read()
    checks = [
        ("FeverWood does not end sustainers itself", "sustainerManager" not in fw and "Notify_SwitchedMap" not in fw),
        ("FeverWood registers a reason", "AddReason(SilenceReasonSentinel" in fw and "RemoveReason(SilenceReasonSentinel" in fw),
        ("SilenceCue restores only via the reason set", cue.count("Notify_SwitchedMap") == 1 and "private void Restore()" in cue),
        ("kernel is in the csproj", "RM_SilenceReasons.cs" in open(os.path.join(CB, "RM_CreatureBehaviors.csproj"), encoding="utf-8").read()),
    ]
    for label, good in checks:
        print(("ok   " if good else "FAIL ") + label)
        bad += not good
    print(f"silence reasons selftest: {6 - bad}/6 ok")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
